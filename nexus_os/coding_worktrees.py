from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

_SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")


@dataclass(slots=True)
class WorktreeLease:
    task_id: str
    branch: str
    path: Path


class WorktreeError(RuntimeError):
    pass


class WorktreeManager:
    """Create isolated task worktrees using git argv execution only."""

    def __init__(self, repo_root: Path, workspace_root: Path):
        self.repo_root = repo_root.resolve()
        self.workspace_root = workspace_root.resolve()
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        if not (self.repo_root / ".git").exists():
            raise WorktreeError(f"Not a git repository: {self.repo_root}")

    @staticmethod
    def _safe(value: str) -> str:
        if not _SAFE_NAME.fullmatch(value):
            raise WorktreeError(f"Unsafe identifier: {value!r}")
        return value

    def _run(self, args: list[str], cwd: Path | None = None) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(cwd or self.repo_root),
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if completed.returncode != 0:
            raise WorktreeError(completed.stderr.strip() or completed.stdout.strip())
        return completed.stdout.strip()

    def create(self, task_id: str, *, base_ref: str = "HEAD") -> WorktreeLease:
        task_id = self._safe(task_id)
        branch = f"nua/task-{task_id}"
        target = (self.workspace_root / task_id).resolve()
        if self.workspace_root not in target.parents:
            raise WorktreeError("Worktree target escaped workspace root")
        if target.exists():
            raise WorktreeError(f"Worktree already exists: {target}")
        self._run(["worktree", "add", "-b", branch, str(target), base_ref])
        return WorktreeLease(task_id=task_id, branch=branch, path=target)

    def remove(self, lease: WorktreeLease, *, force: bool = False) -> None:
        target = lease.path.resolve()
        if self.workspace_root not in target.parents:
            raise WorktreeError("Refusing to remove worktree outside workspace root")
        args = ["worktree", "remove"]
        if force:
            args.append("--force")
        args.append(str(target))
        self._run(args)

    def status(self, lease: WorktreeLease) -> str:
        return self._run(["status", "--short"], cwd=lease.path)

    def commit(self, lease: WorktreeLease, message: str) -> str:
        if not message.strip():
            raise WorktreeError("Commit message cannot be empty")
        self._run(["add", "--all"], cwd=lease.path)
        self._run(["commit", "-m", message], cwd=lease.path)
        return self._run(["rev-parse", "HEAD"], cwd=lease.path)
