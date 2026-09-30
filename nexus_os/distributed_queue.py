# ruff: noqa: I001
from __future__ import annotations

import json
import time
import typing
import uuid
from collections.abc import Callable
from dataclasses import dataclass


POSTGRES_QUEUE_DDL = """
CREATE TABLE IF NOT EXISTS guardian_jobs (
    job_id TEXT PRIMARY KEY,
    mission_id TEXT NOT NULL,
    payload JSONB NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending','running','completed','failed')),
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    lease_owner TEXT,
    lease_expires_at DOUBLE PRECISION,
    heartbeat_at DOUBLE PRECISION,
    available_at DOUBLE PRECISION NOT NULL,
    created_at DOUBLE PRECISION NOT NULL,
    updated_at DOUBLE PRECISION NOT NULL,
    result JSONB,
    error TEXT
);
CREATE INDEX IF NOT EXISTS guardian_jobs_claim_idx
ON guardian_jobs (status, available_at, created_at);
""".strip()


CLAIM_SQL = """
WITH candidate AS (
    SELECT job_id
    FROM guardian_jobs
    WHERE status = 'pending'
      AND available_at <= %s
      AND attempts < max_attempts
    ORDER BY available_at, created_at
    FOR UPDATE SKIP LOCKED
    LIMIT 1
)
UPDATE guardian_jobs AS jobs
SET status = 'running',
    attempts = attempts + 1,
    lease_owner = %s,
    lease_expires_at = %s,
    heartbeat_at = %s,
    updated_at = %s
FROM candidate
WHERE jobs.job_id = candidate.job_id
RETURNING jobs.job_id, jobs.mission_id, jobs.payload, jobs.attempts,
          jobs.max_attempts, jobs.lease_expires_at;
""".strip()


@dataclass(frozen=True, slots=True)
class DistributedJob:
    job_id: str
    mission_id: str
    payload: dict[str, typing.Any]
    attempts: int
    max_attempts: int
    lease_expires_at: float | None = None


@dataclass(frozen=True, slots=True)
class LeasePolicy:
    lease_seconds: float = 120.0
    retry_delay_seconds: float = 10.0

    def __post_init__(self) -> None:
        if self.lease_seconds <= 0 or self.retry_delay_seconds < 0:
            raise ValueError("invalid lease policy")


class Cursor(typing.Protocol):
    def execute(
        self,
        query: str,
        params: tuple[typing.Any, ...] = (),
    ) -> typing.Any: ...

    def fetchone(self) -> typing.Any: ...


class Connection(typing.Protocol):
    def cursor(self) -> Cursor: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def close(self) -> None: ...


ConnectionFactory = Callable[[], Connection]


class PostgresGuardianQueue:
    """DB-API style PostgreSQL queue using leases and SKIP LOCKED for distributed workers."""

    def __init__(self, connection_factory: ConnectionFactory, policy: LeasePolicy | None = None):
        self.connection_factory = connection_factory
        self.policy = policy or LeasePolicy()

    def initialize(self) -> None:
        connection = self.connection_factory()
        try:
            cursor = connection.cursor()
            cursor.execute(POSTGRES_QUEUE_DDL)
            connection.commit()
        finally:
            connection.close()

    def enqueue(
        self,
        mission_id: str,
        payload: dict[str, typing.Any],
        *,
        max_attempts: int = 3,
        available_at: float | None = None,
    ) -> str:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        now = time.time()
        job_id = uuid.uuid4().hex
        connection = self.connection_factory()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO guardian_jobs (
                    job_id, mission_id, payload, status, attempts, max_attempts,
                    available_at, created_at, updated_at
                ) VALUES (%s, %s, %s::jsonb, 'pending', 0, %s, %s, %s, %s)
                """,
                (
                    job_id,
                    mission_id,
                    json.dumps(payload),
                    max_attempts,
                    available_at if available_at is not None else now,
                    now,
                    now,
                ),
            )
            connection.commit()
            return job_id
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def claim(self, worker_id: str, *, now: float | None = None) -> DistributedJob | None:
        if not worker_id.strip():
            raise ValueError("worker_id cannot be empty")
        now = time.time() if now is None else now
        expires = now + self.policy.lease_seconds
        connection = self.connection_factory()
        try:
            cursor = connection.cursor()
            cursor.execute(CLAIM_SQL, (now, worker_id, expires, now, now))
            row = cursor.fetchone()
            connection.commit()
            if not row:
                return None
            payload = row[2]
            if isinstance(payload, str):
                payload = json.loads(payload)
            return DistributedJob(
                job_id=row[0],
                mission_id=row[1],
                payload=dict(payload),
                attempts=int(row[3]),
                max_attempts=int(row[4]),
                lease_expires_at=float(row[5]),
            )
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def heartbeat(self, job_id: str, worker_id: str, *, now: float | None = None) -> None:
        now = time.time() if now is None else now
        expires = now + self.policy.lease_seconds
        self._mutate(
            """
            UPDATE guardian_jobs
            SET heartbeat_at = %s, lease_expires_at = %s, updated_at = %s
            WHERE job_id = %s AND status = 'running' AND lease_owner = %s
            """,
            (now, expires, now, job_id, worker_id),
        )

    def complete(self, job_id: str, worker_id: str, result: dict[str, typing.Any]) -> None:
        now = time.time()
        self._mutate(
            """
            UPDATE guardian_jobs
            SET status = 'completed', result = %s::jsonb, lease_owner = NULL,
                lease_expires_at = NULL, updated_at = %s
            WHERE job_id = %s AND status = 'running' AND lease_owner = %s
            """,
            (json.dumps(result), now, job_id, worker_id),
        )

    def fail(self, job_id: str, worker_id: str, error: str, *, retry: bool = True) -> None:
        now = time.time()
        if retry:
            query = """
                UPDATE guardian_jobs
                SET status = CASE WHEN attempts >= max_attempts THEN 'failed' ELSE 'pending' END,
                    error = %s, lease_owner = NULL, lease_expires_at = NULL,
                    available_at = %s, updated_at = %s
                WHERE job_id = %s AND status = 'running' AND lease_owner = %s
            """
            params = (
                error,
                now + self.policy.retry_delay_seconds,
                now,
                job_id,
                worker_id,
            )
        else:
            query = """
                UPDATE guardian_jobs
                SET status = 'failed', error = %s, lease_owner = NULL,
                    lease_expires_at = NULL, updated_at = %s
                WHERE job_id = %s AND status = 'running' AND lease_owner = %s
            """
            params = (error, now, job_id, worker_id)
        self._mutate(query, params)

    def recover_expired(self, *, now: float | None = None) -> None:
        now = time.time() if now is None else now
        self._mutate(
            """
            UPDATE guardian_jobs
            SET status = CASE WHEN attempts >= max_attempts THEN 'failed' ELSE 'pending' END,
                lease_owner = NULL, lease_expires_at = NULL, available_at = %s, updated_at = %s,
                error = COALESCE(error, 'worker lease expired')
            WHERE status = 'running' AND lease_expires_at IS NOT NULL AND lease_expires_at < %s
            """,
            (now, now, now),
        )

    def _mutate(self, query: str, params: tuple[typing.Any, ...]) -> None:
        connection = self.connection_factory()
        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
