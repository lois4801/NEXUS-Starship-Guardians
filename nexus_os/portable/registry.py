from __future__ import annotations

from .command_cli import CommandCLIProvider
from .ollama_cli import OllamaCLIProvider
from .opencode_cli import OpenCodeCLIProvider


def list_providers() -> list[str]:
    return ["ollama", "opencode", "cli"]


def build_provider(name: str, model: str | None = None):
    normalized = name.strip().lower()
    if normalized == "ollama":
        if not model:
            raise RuntimeError("--model is required for the Ollama provider.")
        return OllamaCLIProvider(model)
    if normalized == "opencode":
        return OpenCodeCLIProvider(model)
    if normalized == "cli":
        return CommandCLIProvider(label=model or "external-cli")
    raise RuntimeError(f"Unknown portable provider: {name}. Available: {', '.join(list_providers())}")
