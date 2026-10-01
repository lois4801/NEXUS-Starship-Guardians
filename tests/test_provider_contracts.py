from __future__ import annotations

from types import SimpleNamespace

import pytest

from nexus_os.portable.command_cli import CommandCLIProvider
from nexus_os.portable.ollama_cli import OllamaCLIProvider


def test_command_cli_provider_contract(monkeypatch):
    monkeypatch.setattr("nexus_os.portable.command_cli.shutil.which", lambda _: "/usr/bin/fake")
    monkeypatch.setattr(
        "nexus_os.portable.command_cli.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="hello\n", stderr=""),
    )
    provider = CommandCLIProvider(command=["fake"], label="contract-model")
    result = provider.generate("prompt")

    assert result.text == "hello"
    assert result.provider == "cli"
    assert result.model == "contract-model"


def test_command_cli_provider_surfaces_nonzero_exit(monkeypatch):
    monkeypatch.setattr("nexus_os.portable.command_cli.shutil.which", lambda _: "/usr/bin/fake")
    monkeypatch.setattr(
        "nexus_os.portable.command_cli.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=2, stdout="", stderr="boom"),
    )
    provider = CommandCLIProvider(command=["fake"])

    with pytest.raises(RuntimeError, match="boom"):
        provider.generate("prompt")


def test_ollama_provider_contract(monkeypatch):
    monkeypatch.setattr("nexus_os.portable.ollama_cli.shutil.which", lambda _: "/usr/bin/ollama")
    monkeypatch.setattr(
        "nexus_os.portable.ollama_cli.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="answer\n", stderr=""),
    )
    provider = OllamaCLIProvider("llama3.2")
    result = provider.generate("prompt")

    assert result.text == "answer"
    assert result.provider == "ollama"
    assert result.model == "llama3.2"
