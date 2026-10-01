from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PerformanceSummary:
    guardian_id: str
    attempts: int
    successes: int
    average_score: float
    average_cost: float
    average_latency_seconds: float
    projects: int


class CrossProjectPerformanceStore:
    """Persist project-scoped Guardian outcomes and aggregate them across projects."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS guardian_outcomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    guardian_id TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    score REAL NOT NULL,
                    cost REAL NOT NULL,
                    latency_seconds REAL NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS ix_guardian_outcomes_guardian ON guardian_outcomes(guardian_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS ix_guardian_outcomes_project ON guardian_outcomes(project_id)"
            )

    def record(
        self,
        *,
        project_id: str,
        guardian_id: str,
        success: bool,
        score: float,
        cost: float = 0.0,
        latency_seconds: float = 0.0,
    ) -> None:
        if not project_id.strip() or not guardian_id.strip():
            raise ValueError("project_id and guardian_id are required")
        if not 0 <= score <= 10:
            raise ValueError("score must be between 0 and 10")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO guardian_outcomes (
                    project_id, guardian_id, success, score, cost, latency_seconds
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    guardian_id,
                    int(success),
                    score,
                    max(0.0, cost),
                    max(0.0, latency_seconds),
                ),
            )

    def summary(self, guardian_id: str) -> PerformanceSummary:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT guardian_id, COUNT(*), SUM(success), AVG(score), AVG(cost),
                       AVG(latency_seconds), COUNT(DISTINCT project_id)
                FROM guardian_outcomes
                WHERE guardian_id = ?
                GROUP BY guardian_id
                """,
                (guardian_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"no performance history for Guardian: {guardian_id}")
        return PerformanceSummary(
            guardian_id=row[0],
            attempts=int(row[1]),
            successes=int(row[2]),
            average_score=float(row[3]),
            average_cost=float(row[4]),
            average_latency_seconds=float(row[5]),
            projects=int(row[6]),
        )

    def leaderboard(self, *, minimum_attempts: int = 1, limit: int = 20) -> list[PerformanceSummary]:
        if minimum_attempts < 1 or limit < 1:
            raise ValueError("minimum_attempts and limit must be at least 1")
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT guardian_id, COUNT(*) AS attempts, SUM(success), AVG(score), AVG(cost),
                       AVG(latency_seconds), COUNT(DISTINCT project_id)
                FROM guardian_outcomes
                GROUP BY guardian_id
                HAVING COUNT(*) >= ?
                ORDER BY ((AVG(score) * 0.55) + ((SUM(success) * 1.0 / COUNT(*)) * 10 * 0.45)) DESC,
                         AVG(cost) ASC, AVG(latency_seconds) ASC
                LIMIT ?
                """,
                (minimum_attempts, limit),
            ).fetchall()
        return [
            PerformanceSummary(
                guardian_id=row[0],
                attempts=int(row[1]),
                successes=int(row[2]),
                average_score=float(row[3]),
                average_cost=float(row[4]),
                average_latency_seconds=float(row[5]),
                projects=int(row[6]),
            )
            for row in rows
        ]
