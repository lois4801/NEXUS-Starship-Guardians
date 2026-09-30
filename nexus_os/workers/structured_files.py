from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class FileEdit:
    path: str
    content: str
    expected_sha256: str | None = None


@dataclass(slots=True)
class FileEditResult:
    path: str
    sha256: str
    bytes_written: int


class StructuredFileWorker:
    """Apply explicit file replacements inside one approved workspace root."""

    def __init__(self, workspace_root: Path, *, max_file_bytes: int = 2_000_000):
        self.workspace_root = workspace_root.resolve()
        self.max_file_bytes = max_file_bytes

    def _resolve(self, relative_path: str) -> Path:
        if not relative_path or Path(relative_path).is_absolute():
            raise ValueError("file path must be a non-empty relative path")
        target = (self.workspace_root / relative_path).resolve()
        if target != self.workspace_root and self.workspace_root not in target.parents:
            raise ValueError("file path escapes configured workspace root")
        return target

    @staticmethod
    def _sha(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def apply(self, edit: FileEdit) -> FileEditResult:
        target = self._resolve(edit.path)
        payload = edit.content.encode("utf-8")
        if len(payload) > self.max_file_bytes:
            raise ValueError("file edit exceeds configured size limit")
        if target.exists():
            if target.is_symlink():
                raise ValueError("refusing to replace a symlink")
            current = target.read_bytes()
            if edit.expected_sha256 is not None and self._sha(current) != edit.expected_sha256:
                raise ValueError("file changed since the edit was prepared")
        elif edit.expected_sha256 is not None:
            raise ValueError("expected existing file was not found")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        return FileEditResult(edit.path, self._sha(payload), len(payload))

    def read_sha256(self, relative_path: str) -> str:
        target = self._resolve(relative_path)
        if not target.is_file() or target.is_symlink():
            raise ValueError("file is not a regular readable file")
        return self._sha(target.read_bytes())
