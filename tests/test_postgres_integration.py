# ruff: noqa: I001
from __future__ import annotations

import os

import pytest

from nexus_os.distributed_queue import LeasePolicy, PostgresGuardianQueue


DSN = os.getenv("NEXUS_POSTGRES_DSN")
pytestmark = pytest.mark.skipif(not DSN, reason="NEXUS_POSTGRES_DSN is not configured")


def _factory():
    import psycopg

    return psycopg.connect(DSN)


def test_real_postgres_queue_claim_heartbeat_complete_cycle():
    queue = PostgresGuardianQueue(_factory, LeasePolicy(lease_seconds=30, retry_delay_seconds=0))
    queue.initialize()

    connection = _factory()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM guardian_jobs")
        connection.commit()
    finally:
        connection.close()

    job_id = queue.enqueue("mission-postgres-smoke", {"kind": "smoke"}, max_attempts=2)
    claimed = queue.claim("worker-a")
    assert claimed is not None
    assert claimed.job_id == job_id
    assert claimed.mission_id == "mission-postgres-smoke"
    assert claimed.payload == {"kind": "smoke"}
    assert claimed.attempts == 1

    # SKIP LOCKED / running-state ownership means a second worker cannot claim the same job.
    assert queue.claim("worker-b") is None

    queue.heartbeat(job_id, "worker-a")
    queue.complete(job_id, "worker-a", {"ok": True})

    connection = _factory()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT status, result, lease_owner, lease_expires_at FROM guardian_jobs WHERE job_id = %s",
                (job_id,),
            )
            row = cursor.fetchone()
    finally:
        connection.close()

    assert row is not None
    assert row[0] == "completed"
    assert row[1] == {"ok": True}
    assert row[2] is None
    assert row[3] is None


def test_real_postgres_queue_recovers_expired_lease():
    queue = PostgresGuardianQueue(_factory, LeasePolicy(lease_seconds=1, retry_delay_seconds=0))
    queue.initialize()

    connection = _factory()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM guardian_jobs")
        connection.commit()
    finally:
        connection.close()

    job_id = queue.enqueue("mission-expired-lease", {"kind": "recovery"}, max_attempts=2)
    claimed = queue.claim("worker-crashed", now=10.0)
    assert claimed is not None
    queue.recover_expired(now=12.0)

    reclaimed = queue.claim("worker-recovery", now=12.0)
    assert reclaimed is not None
    assert reclaimed.job_id == job_id
    assert reclaimed.attempts == 2
