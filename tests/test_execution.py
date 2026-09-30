import asyncio

import pytest

from nexus_os.execution import ExecutionCoordinator, ExecutionTask, TaskStatus, validate_tasks


def test_validate_tasks_rejects_cycle():
    tasks = [
        ExecutionTask("a", "builder", "A", dependencies=("b",)),
        ExecutionTask("b", "tester", "B", dependencies=("a",)),
    ]
    with pytest.raises(ValueError, match="cycle"):
        validate_tasks(tasks)


def test_execution_respects_dependencies_and_verifies():
    events: list[str] = []

    async def worker(task: ExecutionTask) -> str:
        events.append(task.task_id)
        await asyncio.sleep(0)
        return f"done:{task.task_id}"

    async def verifier(task: ExecutionTask, output: str) -> str:
        return f"verified:{task.task_id}:{output}"

    tasks = [
        ExecutionTask("build", "builder", "build"),
        ExecutionTask("test", "tester", "test", dependencies=("build",)),
    ]
    report = asyncio.run(
        ExecutionCoordinator(max_parallel=2).run(tasks, worker, verifier=verifier)
    )
    assert events == ["build", "test"]
    assert report.results["build"].status == TaskStatus.COMPLETED
    assert report.results["test"].status == TaskStatus.COMPLETED
    assert report.results["test"].verification == "verified:test:done:test"


def test_unapproved_write_blocks_dependents():
    async def worker(task: ExecutionTask) -> str:
        return task.task_id

    async def approval_check(task: ExecutionTask) -> bool:
        return False

    tasks = [
        ExecutionTask("write", "builder", "change file", requires_approval=True),
        ExecutionTask("verify", "tester", "verify", dependencies=("write",)),
    ]
    report = asyncio.run(
        ExecutionCoordinator().run(tasks, worker, approval_check=approval_check)
    )
    assert report.results["write"].status == TaskStatus.BLOCKED
    assert report.results["verify"].status == TaskStatus.SKIPPED


def test_worker_failure_isolated_and_blocks_only_dependents():
    async def worker(task: ExecutionTask) -> str:
        if task.task_id == "broken":
            raise RuntimeError("boom")
        return task.task_id

    tasks = [
        ExecutionTask("broken", "builder", "broken"),
        ExecutionTask("independent", "docs", "docs"),
        ExecutionTask("dependent", "tester", "test", dependencies=("broken",)),
    ]
    report = asyncio.run(ExecutionCoordinator(max_parallel=2).run(tasks, worker))
    assert report.results["broken"].status == TaskStatus.FAILED
    assert report.results["independent"].status == TaskStatus.COMPLETED
    assert report.results["dependent"].status == TaskStatus.SKIPPED
