from pathlib import Path

import pytest

from nexus_os.execution.worktrees import WorktreeError, WorktreeManager


def test_rejects_unsafe_task_id(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    manager = WorktreeManager(repo, tmp_path / "worktrees")
    with pytest.raises(WorktreeError):
        manager.create("../../escape")


def test_requires_git_repository(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    with pytest.raises(WorktreeError):
        WorktreeManager(repo, tmp_path / "worktrees")
