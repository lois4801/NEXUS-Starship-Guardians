from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path

from nexus_os.execution import ExecutionTask


@dataclass(slots=True)
class ProcessPolicy:
    workspace_root: Path
    allowed_executables: frozenset[str]
    timeout_seconds: float = 120.0
    max_output_chars: int = 20000

    def resolve_workspace(self, relative: str = ".") -> Path:
        root = self.workspace_root.resolve()
        target = (root / relative).resolve()
        if target != root and root not in target.parents:
            raise ValueError("workspace path escapes configured root")
        return target


class LocalProcessWorker:
    """Execute reviewed argv commands without a shell inside one workspace root."""

    def __init__(self, policy: ProcessPolicy):
        self.policy = policy

    async def run_command(
        self,
        task: ExecutionTask,
        argv: list[str],
        *,
        cwd: str = ".",
    ) -> str:
        if not argv:
            raise ValueError("command argv cannot be empty")
        executable = Path(argv[0]).name
        if executable not in self.policy.allowed_executables:
            raise ValueError(f"executable is not allowlisted: {executable}")
        workspace = self.policy.resolve_workspace(cwd)
        process = await asyncio.create_subprocess_exec(
            *argv,
            cwd=workspace,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        try:
            stdout, _ = await asyncio.wait_for(
                process.communicate(), timeout=self.policy.timeout_seconds
            )
        except TimeoutError:
            process.kill()
            await process.communicate()
            raise TimeoutError(f"task {task.task_id} exceeded process timeout") from None
        text = stdout.decode("utf-8", errors="replace")[: self.policy.max_output_chars]
        if process.returncode != 0:
            raise RuntimeError(
                f"task {task.task_id} command failed with exit code {process.returncode}: {text}"
            )
        return text
