from __future__ import annotations

import shutil
import subprocess

from .base import ProviderResult


class OllamaCLIProvider:
    name = "ollama"

    def __init__(self, model: str):
        self.model = model

    def generate(self, prompt: str) -> ProviderResult:
        exe = shutil.which("ollama")
        if not exe:
            raise RuntimeError("Ollama executable not found. Install Ollama and ensure it is on PATH.")
        proc = subprocess.run(
            [exe, "run", self.model],
            input=prompt,
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or f"Ollama exited with code {proc.returncode}")
        return ProviderResult(text=proc.stdout.strip(), provider=self.name, model=self.model)
