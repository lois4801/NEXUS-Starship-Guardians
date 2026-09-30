from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass


@dataclass(slots=True)
class PullRequestResult:
    url: str
    number: int | None = None


class PullRequestPublisher:
    """Publish a reviewed branch with the authenticated GitHub CLI.

    This adapter relies on the user's existing `gh` authentication and does not
    accept tokens from model output. It never invokes a shell.
    """

    def __init__(self, *, repo: str):
        self.repo = repo
        if shutil.which("gh") is None:
            raise RuntimeError("GitHub CLI (gh) is not installed")

    def create(
        self,
        *,
        head: str,
        base: str,
        title: str,
        body: str,
        draft: bool = True,
    ) -> PullRequestResult:
        if not head or not base or not title:
            raise ValueError("head, base, and title are required")
        args = [
            "gh",
            "pr",
            "create",
            "--repo",
            self.repo,
            "--head",
            head,
            "--base",
            base,
            "--title",
            title,
            "--body",
            body,
        ]
        if draft:
            args.append("--draft")
        completed = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
        url = completed.stdout.strip().splitlines()[-1]
        return PullRequestResult(url=url)

    def checks(self, pr: str) -> dict:
        completed = subprocess.run(
            ["gh", "pr", "checks", pr, "--repo", self.repo, "--json", "name,state,link"],
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if completed.returncode not in (0, 8):
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
        return {"checks": json.loads(completed.stdout or "[]"), "exit_code": completed.returncode}
