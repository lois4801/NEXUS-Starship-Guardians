from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field
from enum import StrEnum


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(slots=True)
class ExecutionTask:
    task_id: str
    role: str
    instruction: str
    dependencies: tuple[str, ...] = ()
    requires_approval: bool = False
    verification_required: bool = True


@dataclass(slots=True)
class TaskResult:
    task_id: str
    status: TaskStatus
    output: str = ""
    error: str | None = None
    verification: str | None = None


@dataclass(slots=True)
class ExecutionReport:
    results: dict[str, TaskResult] = field(default_factory=dict)

    @property
    def completed(self) -> list[TaskResult]:
        return [item for item in self.results.values() if item.status == TaskStatus.COMPLETED]

    @property
    def failed(self) -> list[TaskResult]:
        return [item for item in self.results.values() if item.status == TaskStatus.FAILED]


Worker = Callable[[ExecutionTask], Awaitable[str]]
Verifier = Callable[[ExecutionTask, str], Awaitable[str]]
ApprovalCheck = Callable[[ExecutionTask], Awaitable[bool]]


def validate_tasks(tasks: Sequence[ExecutionTask]) -> None:
    ids = [task.task_id for task in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("task_id values must be unique")
    known = set(ids)
    for task in tasks:
        unknown = set(task.dependencies) - known
        if unknown:
            raise ValueError(f"{task.task_id} has unknown dependencies: {sorted(unknown)}")
        if task.task_id in task.dependencies:
            raise ValueError(f"{task.task_id} cannot depend on itself")

    visiting: set[str] = set()
    visited: set[str] = set()
    by_id = {task.task_id: task for task in tasks}

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise ValueError("task dependency graph contains a cycle")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in by_id[task_id].dependencies:
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in ids:
        visit(task_id)


class ExecutionCoordinator:
    """Execute a dependency graph with bounded parallelism and verification gates."""

    def __init__(self, *, max_parallel: int = 8):
        if not 1 <= max_parallel <= 200:
            raise ValueError("max_parallel must be between 1 and 200")
        self.max_parallel = max_parallel

    async def run(
        self,
        tasks: Sequence[ExecutionTask],
        worker: Worker,
        *,
        verifier: Verifier | None = None,
        approval_check: ApprovalCheck | None = None,
    ) -> ExecutionReport:
        validate_tasks(tasks)
        by_id = {task.task_id: task for task in tasks}
        report = ExecutionReport(
            results={task.task_id: TaskResult(task.task_id, TaskStatus.PENDING) for task in tasks}
        )
        semaphore = asyncio.Semaphore(self.max_parallel)

        async def execute(task: ExecutionTask) -> None:
            async with semaphore:
                result = report.results[task.task_id]
                if task.requires_approval:
                    if approval_check is None or not await approval_check(task):
                        result.status = TaskStatus.BLOCKED
                        result.error = "approval required"
                        return
                result.status = TaskStatus.RUNNING
                try:
                    output = await worker(task)
                    result.output = output
                    if task.verification_required and verifier is not None:
                        result.verification = await verifier(task, output)
                    result.status = TaskStatus.COMPLETED
                except (RuntimeError, ValueError, TimeoutError, OSError) as exc:
                    result.status = TaskStatus.FAILED
                    result.error = f"{type(exc).__name__}: {exc}"

        pending = set(by_id)
        while pending:
            ready: list[ExecutionTask] = []
            progressed = False
            for task_id in sorted(pending):
                task = by_id[task_id]
                dependency_states = [report.results[item].status for item in task.dependencies]
                if any(state in {TaskStatus.FAILED, TaskStatus.BLOCKED, TaskStatus.SKIPPED} for state in dependency_states):
                    report.results[task_id].status = TaskStatus.SKIPPED
                    report.results[task_id].error = "dependency did not complete successfully"
                    pending.remove(task_id)
                    progressed = True
                elif all(state == TaskStatus.COMPLETED for state in dependency_states):
                    ready.append(task)

            if ready:
                await asyncio.gather(*(execute(task) for task in ready))
                for task in ready:
                    pending.remove(task.task_id)
                progressed = True

            if not progressed and pending:
                raise RuntimeError("execution graph made no progress")

        return report
