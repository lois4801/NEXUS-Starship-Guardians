"""Project-scoped SQLite persistence (single-instance starter backend)."""

import hashlib
import json
import sqlite3
import threading
from pathlib import Path
from typing import Any
from uuid import uuid4

from .models import ProjectCreate


def _hash(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


class Store:
    def __init__(self, path: str):
        self._lock = threading.RLock()
        if path != ":memory:":
            Path(path).expanduser().parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
              project_id TEXT PRIMARY KEY,
              spec_json TEXT NOT NULL,
              key_hash TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS runs (
              run_id TEXT PRIMARY KEY,
              project_id TEXT NOT NULL REFERENCES projects(project_id),
              agent TEXT NOT NULL,
              goal TEXT NOT NULL,
              status TEXT NOT NULL,
              answer TEXT,
              steps_used INTEGER NOT NULL DEFAULT 0,
              events_json TEXT NOT NULL DEFAULT '[]',
              pending_json TEXT
            );
            CREATE TABLE IF NOT EXISTS notes (
              note_id TEXT PRIMARY KEY,
              project_id TEXT NOT NULL REFERENCES projects(project_id),
              content TEXT NOT NULL
            );
        """)
        self.db.commit()

    def add_project(self, spec: ProjectCreate, key: str) -> None:
        with self._lock:
            self.db.execute(
                "INSERT INTO projects(project_id,spec_json,key_hash) VALUES (?,?,?)",
                (spec.project_id, spec.model_dump_json(), _hash(key)),
            )
            self.db.commit()

    def get_project(self, project_id: str) -> ProjectCreate | None:
        with self._lock:
            row = self.db.execute("SELECT spec_json FROM projects WHERE project_id=?", (project_id,)).fetchone()
            return ProjectCreate.model_validate_json(row[0]) if row else None

    def key_project(self, key: str) -> str | None:
        with self._lock:
            row = self.db.execute("SELECT project_id FROM projects WHERE key_hash=?", (_hash(key),)).fetchone()
            return row[0] if row else None

    def add_run(self, project_id: str, agent: str, goal: str) -> str:
        run_id = str(uuid4())
        with self._lock:
            self.db.execute(
                "INSERT INTO runs(run_id,project_id,agent,goal,status) VALUES (?,?,?,?,?)",
                (run_id, project_id, agent, goal, "pending_approval"),
            )
            self.db.commit()
        return run_id

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self._lock:
            row = self.db.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if not row:
                return None
            data = dict(row)
            data["events"] = json.loads(data.pop("events_json"))
            data["pending_approval"] = json.loads(data.pop("pending_json")) if data["pending_json"] else None
            return data

    def update_run(self, run: dict[str, Any]) -> None:
        with self._lock:
            self.db.execute(
                """UPDATE runs SET status=?,answer=?,steps_used=?,events_json=?,pending_json=?
                   WHERE run_id=?""",
                (run["status"], run["answer"], run["steps_used"], json.dumps(run["events"]),
                 json.dumps(run["pending_approval"]) if run["pending_approval"] else None, run["run_id"]),
            )
            self.db.commit()

    def add_note(self, project_id: str, content: str) -> str:
        note_id = str(uuid4())
        with self._lock:
            self.db.execute(
                "INSERT INTO notes(note_id,project_id,content) VALUES (?,?,?)", (note_id, project_id, content)
            )
            self.db.commit()
        return note_id

    def list_notes(self, project_id: str) -> list[dict[str, str]]:
        with self._lock:
            rows = self.db.execute(
                "SELECT note_id,content FROM notes WHERE project_id=? ORDER BY rowid", (project_id,)
            ).fetchall()
            return [dict(row) for row in rows]
