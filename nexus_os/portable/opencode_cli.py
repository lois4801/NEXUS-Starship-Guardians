from __future__ import annotations

import shutil
import subprocess

from .base import ProviderResult

DEFAULT_TIMEOUT_SECONDS = 900


class OpenCodeCLIProvider:
    """Run the free, open-source OpenCode CLI (https://opencode.ai) headlessly.

    OpenCode is a terminal coding agent that supports 75+ model providers and
    works with provider free tiers (for example Google Gemini) or fully local
    models, so Guardian swarms can run on a desktop without a paid subscription.

    The external CLI remains responsible for its own login, subscription,
    licensing and provider terms. NEXUS never stores provider credentials;
    whichever model OpenCode is signed into is the model the Guardians get.

    Usage:
      nexus-guardians ask --provider opencode "question"
      nexus-guardians swarm --provider opencode --model google/gemini-3-flash \
          --guardians 30 "Build, review, test, and document this feature"

    When ``model`` is omitted, OpenCode uses its own configured default model.
    """

    name = "opencode"

    def __init__(self, model: str | None = None, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS):
        if timeout_seconds < 1:
            raise RuntimeError("timeout_seconds must be a positive integer")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def generate(self, prompt: str) -> ProviderResult:
        exe = shutil.which("opencode")
        if not exe:
            raise RuntimeError(
                "OpenCode executable not found on PATH. "
                "Install it from https://opencode.ai and ensure `opencode` is available."
            )
        command = [exe, "run", "--format", "text"]
        if self.model:
            command += ["--model", self.model]
        command.append(prompt)
        try:
            proc = subprocess.run(
                command,
                text=True,
                capture_output=True,
                check=False,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"OpenCode timed out after {self.timeout_seconds}s. "
                "Try a smaller swarm, a faster model, or a higher timeout."
            ) from exc
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or f"OpenCode exited with code {proc.returncode}")
        return ProviderResult(text=proc.stdout.strip(), provider=self.name, model=self.model)
