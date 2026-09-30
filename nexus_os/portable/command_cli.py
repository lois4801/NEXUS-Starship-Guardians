from __future__ import annotations

import json
import os
import shutil
import subprocess

from .base import ProviderResult


class CommandCLIProvider:
    """Run a user-configured LLM/coding CLI without invoking a shell.

    Configure NEXUS_LLM_COMMAND as a JSON array, for example:
      ["claude", "-p"]
    or
      ["codex", "exec", "-"]

    The external CLI remains responsible for its own login, subscription,
    licensing and provider terms. NEXUS never stores provider credentials.
    """

    name = "cli"

    def __init__(self, command: list[str] | None = None, label: str = "external-cli"):
        if command is None:
            raw = os.getenv("NEXUS_LLM_COMMAND", "")
            if not raw:
                raise RuntimeError("Set NEXUS_LLM_COMMAND to a JSON command array.")
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise RuntimeError("NEXUS_LLM_COMMAND must be valid JSON.") from exc
            if not isinstance(parsed, list) or not parsed or not all(isinstance(x, str) for x in parsed):
                raise RuntimeError("NEXUS_LLM_COMMAND must be a non-empty JSON array of strings.")
            command = parsed
        if shutil.which(command[0]) is None:
            raise RuntimeError(f"Executable not found on PATH: {command[0]}")
        self.command = command
        self.label = label

    def generate(self, prompt: str) -> ProviderResult:
        proc = subprocess.run(
            self.command,
            input=prompt,
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or f"CLI exited with code {proc.returncode}")
        return ProviderResult(text=proc.stdout.strip(), provider=self.name, model=self.label)
