from __future__ import annotations

from dataclasses import dataclass, field

from nexus_os.coding_worktrees import WorktreeLease
from nexus_os.execution import ExecutionTask
from nexus_os.workers.local_process import LocalProcessWorker


@dataclass(slots=True)
class VerificationCommand:
    name: str
    argv: list[str]


@dataclass(slots=True)
class VerificationStepResult:
    name: str
    ok: bool
    output: str = ""
    error: str | None = None


@dataclass(slots=True)
class VerificationReport:
    task_id: str
    passed: bool
    steps: list[VerificationStepResult] = field(default_factory=list)


class VerificationPipeline:
    """Run allowlisted quality gates inside one isolated coding worktree."""

    def __init__(self, worker: LocalProcessWorker):
        self.worker = worker

    async def run(
        self,
        lease: WorktreeLease,
        commands: list[VerificationCommand],
    ) -> VerificationReport:
        steps: list[VerificationStepResult] = []
        root = self.worker.policy.workspace_root.resolve()
        relative = str(lease.path.resolve().relative_to(root))
        for index, command in enumerate(commands, start=1):
            task = ExecutionTask(
                task_id=f"verify-{lease.task_id}-{index}",
                role="verification",
                instruction=f"Run verification gate: {command.name}",
                verification_required=False,
            )
            try:
                output = await self.worker.run_command(task, command.argv, cwd=relative)
                steps.append(VerificationStepResult(command.name, True, output=output))
            except (OSError, RuntimeError, TimeoutError, ValueError) as exc:
                steps.append(
                    VerificationStepResult(
                        command.name,
                        False,
                        error=f"{type(exc).__name__}: {exc}",
                    )
                )
                return VerificationReport(lease.task_id, False, steps)
        return VerificationReport(lease.task_id, True, steps)


def default_python_gates() -> list[VerificationCommand]:
    return [
        VerificationCommand("ruff", ["ruff", "check", "."]),
        VerificationCommand("pytest", ["pytest", "-q"]),
    ]


def default_node_gates() -> list[VerificationCommand]:
    return [
        VerificationCommand("lint", ["npm", "run", "lint", "--if-present"]),
        VerificationCommand("test", ["npm", "test", "--", "--runInBand"]),
    ]
