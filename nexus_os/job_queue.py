from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class JobState(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True)
class DurableJob:
    job_id: str
    payload: dict
    state: JobState
    attempts: int
    max_attempts: int
    last_error: str | None = None


class SqliteJobQueue:
    """Small durable queue with crash recovery and bounded retries."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS guardian_jobs (
                    job_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    state TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    max_attempts INTEGER NOT NULL DEFAULT 3,
                    last_error TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
                """
            )

    def enqueue(self, payload: dict, *, max_attempts: int = 3, job_id: str | None = None) -> str:
        if max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        now = time.time()
        identifier = job_id or uuid.uuid4().hex
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO guardian_jobs VALUES (?, ?, ?, 0, ?, NULL, ?, ?)",
                (identifier, json.dumps(payload), JobState.PENDING.value, max_attempts, now, now),
            )
        return identifier

    def claim_next(self) -> DurableJob | None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                """
                SELECT * FROM guardian_jobs
                WHERE state = ? AND attempts < max_attempts
                ORDER BY created_at ASC
                LIMIT 1
                """,
                (JobState.PENDING.value,),
            ).fetchone()
            if row is None:
                connection.commit()
                return None
            attempts = int(row["attempts"]) + 1
            connection.execute(
                "UPDATE guardian_jobs SET state = ?, attempts = ?, updated_at = ? WHERE job_id = ?",
                (JobState.RUNNING.value, attempts, time.time(), row["job_id"]),
            )
            connection.commit()
            return DurableJob(
                job_id=row["job_id"],
                payload=json.loads(row["payload"]),
                state=JobState.RUNNING,
                attempts=attempts,
                max_attempts=int(row["max_attempts"]),
                last_error=row["last_error"],
            )

    def complete(self, job_id: str) -> None:
        self._set_state(job_id, JobState.COMPLETED)

    def fail(self, job_id: str, error: str) -> None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT attempts, max_attempts FROM guardian_jobs WHERE job_id = ?", (job_id,)
            ).fetchone()
            if row is None:
                raise KeyError(job_id)
            next_state = (
                JobState.FAILED
                if int(row["attempts"]) >= int(row["max_attempts"])
                else JobState.PENDING
            )
            connection.execute(
                "UPDATE guardian_jobs SET state = ?, last_error = ?, updated_at = ? WHERE job_id = ?",
                (next_state.value, error[:4000], time.time(), job_id),
            )

    def recover_interrupted(self) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE guardian_jobs SET state = ?, updated_at = ? WHERE state = ?",
                (JobState.PENDING.value, time.time(), JobState.RUNNING.value),
            )
            return cursor.rowcount

    def get(self, job_id: str) -> DurableJob:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM guardian_jobs WHERE job_id = ?", (job_id,)
            ).fetchone()
        if row is None:
            raise KeyError(job_id)
        return DurableJob(
            job_id=row["job_id"],
            payload=json.loads(row["payload"]),
            state=JobState(row["state"]),
            attempts=int(row["attempts"]),
            max_attempts=int(row["max_attempts"]),
            last_error=row["last_error"],
        )

    def _set_state(self, job_id: str, state: JobState) -> None:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE guardian_jobs SET state = ?, updated_at = ? WHERE job_id = ?",
                (state.value, time.time(), job_id),
            )
            if cursor.rowcount != 1:
                raise KeyError(job_id)
