from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class RebaseResult:
    ok: bool
    conflicted_files: tuple[str, ...] = ()
    output: str = ""
    aborted: bool = False


class GitConflictManager:
    """Safe git rebase helper using argv execution only; never auto-resolves conflicts blindly."""

    def __init__(self, worktree: Path, *, timeout_seconds: float = 180.0):
        self.worktree = worktree.resolve()
        self.timeout_seconds = timeout_seconds
        if not (self.worktree / ".git").exists():
            raise ValueError(f"not a git worktree: {self.worktree}")

    def _run(self, args: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            ["git", *args],
            cwd=self.worktree,
            check=False,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
        )
        if check and completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
        return completed

    def conflicted_files(self) -> tuple[str, ...]:
        completed = self._run(["diff", "--name-only", "--diff-filter=U"], check=True)
        return tuple(line.strip() for line in completed.stdout.splitlines() if line.strip())

    def rebase(self, upstream: str, *, abort_on_conflict: bool = True) -> RebaseResult:
        if not upstream.strip() or upstream.startswith("-"):
            raise ValueError("invalid upstream ref")
        completed = self._run(["rebase", upstream])
        if completed.returncode == 0:
            return RebaseResult(ok=True, output=completed.stdout.strip())

        conflicts = self.conflicted_files()
        output = (completed.stdout + "\n" + completed.stderr).strip()
        aborted = False
        if conflicts and abort_on_conflict:
            abort = self._run(["rebase", "--abort"])
            aborted = abort.returncode == 0
        return RebaseResult(
            ok=False,
            conflicted_files=conflicts,
            output=output,
            aborted=aborted,
        )

    def is_clean(self) -> bool:
        completed = self._run(["status", "--porcelain"], check=True)
        return not completed.stdout.strip()
