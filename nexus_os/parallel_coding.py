from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path

from nexus_os.coding_worktrees import WorktreeLease, WorktreeManager
from nexus_os.portable.base import PortableProvider


@dataclass(slots=True)
class CodingTask:
    task_id: str
    instruction: str
    base_ref: str = "HEAD"


@dataclass(slots=True)
class CodingResult:
    task_id: str
    branch: str
    worktree: str
    proposal: str
    status: str
    commit_sha: str | None = None
    error: str | None = None


class ParallelCodingCoordinator:
    """Run coding agents in separate git worktrees with bounded concurrency."""

    def __init__(
        self,
        manager: WorktreeManager,
        provider: PortableProvider,
        *,
        max_parallel: int = 4,
    ):
        if max_parallel < 1:
            raise ValueError("max_parallel must be positive")
        self.manager = manager
        self.provider = provider
        self.max_parallel = max_parallel

    async def run(self, tasks: list[CodingTask]) -> list[CodingResult]:
        semaphore = asyncio.Semaphore(self.max_parallel)

        async def execute(task: CodingTask) -> CodingResult:
            async with semaphore:
                lease: WorktreeLease | None = None
                try:
                    lease = await asyncio.to_thread(
                        self.manager.create, task.task_id, base_ref=task.base_ref
                    )
                    prompt = self._prompt(task, lease.path)
                    generated = await asyncio.to_thread(self.provider.generate, prompt)
                    return CodingResult(
                        task_id=task.task_id,
                        branch=lease.branch,
                        worktree=str(lease.path),
                        proposal=generated.text,
                        status="proposal_ready",
                    )
                except (OSError, RuntimeError, ValueError) as exc:
                    return CodingResult(
                        task_id=task.task_id,
                        branch=lease.branch if lease else "",
                        worktree=str(lease.path) if lease else "",
                        proposal="",
                        status="failed",
                        error=f"{type(exc).__name__}: {exc}",
                    )

        return list(await asyncio.gather(*(execute(task) for task in tasks)))

    @staticmethod
    def _prompt(task: CodingTask, worktree: Path) -> str:
        return (
            "You are a coding specialist in Nexus Universe Agents. "
            f"Your isolated git worktree is {worktree}. "
            "Work only on the assigned task. Return a concrete implementation plan or patch-oriented "
            "instructions, tests to run, risks, and acceptance criteria. Never claim edits or tests happened "
            "unless an execution worker provides evidence.\n\n"
            f"TASK {task.task_id}: {task.instruction}"
        )
