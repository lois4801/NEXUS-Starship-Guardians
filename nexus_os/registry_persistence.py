from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .guardian_registry import GuardianMetrics, GuardianProfile, GuardianRegistry


class SQLiteGuardianRegistry(GuardianRegistry):
    """Guardian registry with SQLite-backed profiles and performance metrics."""

    def __init__(self, path: str | Path):
        super().__init__()
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()
        self._load()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS guardian_registry (
                    guardian_id TEXT PRIMARY KEY,
                    role TEXT NOT NULL,
                    capabilities TEXT NOT NULL,
                    allowed_tools TEXT NOT NULL,
                    preferred_models TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    successes INTEGER NOT NULL DEFAULT 0,
                    total_score REAL NOT NULL DEFAULT 0,
                    total_cost REAL NOT NULL DEFAULT 0,
                    total_latency_seconds REAL NOT NULL DEFAULT 0
                )
                """
            )

    def _load(self) -> None:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT guardian_id, role, capabilities, allowed_tools, preferred_models,
                       attempts, successes, total_score, total_cost, total_latency_seconds
                FROM guardian_registry
                ORDER BY guardian_id
                """
            ).fetchall()
        for row in rows:
            profile = GuardianProfile(
                guardian_id=row[0],
                role=row[1],
                capabilities=frozenset(json.loads(row[2])),
                allowed_tools=frozenset(json.loads(row[3])),
                preferred_models=tuple(json.loads(row[4])),
            )
            super().register(profile)
            self.get(profile.guardian_id).metrics = GuardianMetrics(
                attempts=int(row[5]),
                successes=int(row[6]),
                total_score=float(row[7]),
                total_cost=float(row[8]),
                total_latency_seconds=float(row[9]),
            )

    def register(self, profile: GuardianProfile) -> None:
        super().register(profile)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO guardian_registry (
                    guardian_id, role, capabilities, allowed_tools, preferred_models
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    profile.guardian_id,
                    profile.role,
                    json.dumps(sorted(profile.capabilities)),
                    json.dumps(sorted(profile.allowed_tools)),
                    json.dumps(list(profile.preferred_models)),
                ),
            )

    def record_outcome(
        self,
        guardian_id: str,
        *,
        success: bool,
        score: float,
        cost: float = 0.0,
        latency_seconds: float = 0.0,
    ) -> None:
        super().record_outcome(
            guardian_id,
            success=success,
            score=score,
            cost=cost,
            latency_seconds=latency_seconds,
        )
        metrics = self.get(guardian_id).metrics
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE guardian_registry
                SET attempts = ?, successes = ?, total_score = ?, total_cost = ?,
                    total_latency_seconds = ?
                WHERE guardian_id = ?
                """,
                (
                    metrics.attempts,
                    metrics.successes,
                    metrics.total_score,
                    metrics.total_cost,
                    metrics.total_latency_seconds,
                    guardian_id,
                ),
            )
