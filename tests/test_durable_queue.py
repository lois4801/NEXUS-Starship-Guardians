from pathlib import Path

from nexus_os.job_queue import JobState, SqliteJobQueue


def test_queue_claim_complete_and_recover(tmp_path: Path):
    queue = SqliteJobQueue(tmp_path / "jobs.db")
    first = queue.enqueue({"task": "build"})
    claimed = queue.claim_next()
    assert claimed is not None
    assert claimed.job_id == first
    assert claimed.state == JobState.RUNNING

    assert queue.recover_interrupted() == 1
    assert queue.get(first).state == JobState.PENDING

    claimed_again = queue.claim_next()
    assert claimed_again is not None
    queue.complete(first)
    assert queue.get(first).state == JobState.COMPLETED


def test_queue_retries_then_fails(tmp_path: Path):
    queue = SqliteJobQueue(tmp_path / "jobs.db")
    job_id = queue.enqueue({"task": "verify"}, max_attempts=2)

    assert queue.claim_next() is not None
    queue.fail(job_id, "first failure")
    assert queue.get(job_id).state == JobState.PENDING

    assert queue.claim_next() is not None
    queue.fail(job_id, "second failure")
    job = queue.get(job_id)
    assert job.state == JobState.FAILED
    assert job.attempts == 2
