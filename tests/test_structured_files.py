from pathlib import Path

import pytest

from nexus_os.workers.structured_files import FileEdit, StructuredFileWorker


def test_applies_scoped_text_edit(tmp_path: Path):
    worker = StructuredFileWorker(tmp_path)
    result = worker.apply(FileEdit("src/example.txt", "hello"))
    assert (tmp_path / "src" / "example.txt").read_text() == "hello"
    assert result.bytes_written == 5


def test_rejects_workspace_escape(tmp_path: Path):
    worker = StructuredFileWorker(tmp_path)
    with pytest.raises(ValueError):
        worker.apply(FileEdit("../escape.txt", "no"))


def test_expected_hash_prevents_stale_overwrite(tmp_path: Path):
    target = tmp_path / "file.txt"
    target.write_text("first")
    worker = StructuredFileWorker(tmp_path)
    stale = "0" * 64
    with pytest.raises(ValueError):
        worker.apply(FileEdit("file.txt", "second", expected_sha256=stale))
