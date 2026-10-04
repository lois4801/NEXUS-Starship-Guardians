from __future__ import annotations

import subprocess
from types import SimpleNamespace

import pytest

from nexus_os.portable.opencode_cli import DEFAULT_TIMEOUT_SECONDS, OpenCodeCLIProvider
from nexus_os.portable.registry import build_provider, list_providers


def _patch_run(monkeypatch, completed):
    calls = []

    def fake_run(*args, **kwargs):
        calls.append((args, kwargs))
        return completed

    monkeypatch.setattr("nexus_os.portable.opencode_cli.shutil.which", lambda _: "/usr/bin/fake")
    monkeypatch.setattr("nexus_os.portable.opencode_cli.subprocess.run", fake_run)
    return calls


def test_opencode_provider_contract(monkeypatch):
    calls = _patch_run(monkeypatch, SimpleNamespace(returncode=0, stdout="hello\n", stderr=""))
    provider = OpenCodeCLIProvider("google/gemini-3-flash")
    result = provider.generate("prompt")

    assert result.text == "hello"
    assert result.provider == "opencode"
    assert result.model == "google/gemini-3-flash"
    command = calls[0][0][0]
    assert command[:3] == ["/usr/bin/fake", "run", "--format"]
    assert "text" in command
    model_index = command.index("--model")
    assert command[model_index + 1] == "google/gemini-3-flash"
    assert command[-1] == "prompt"
    assert calls[0][1]["timeout"] == DEFAULT_TIMEOUT_SECONDS


def test_opencode_provider_omits_model_flag_without_model(monkeypatch):
    calls = _patch_run(monkeypatch, SimpleNamespace(returncode=0, stdout="ok", stderr=""))
    provider = OpenCodeCLIProvider()
    result = provider.generate("prompt")

    assert result.model is None
    assert "--model" not in calls[0][0][0]


def test_opencode_provider_surfaces_nonzero_exit(monkeypatch):
    _patch_run(monkeypatch, SimpleNamespace(returncode=2, stdout="", stderr="boom"))
    provider = OpenCodeCLIProvider()

    with pytest.raises(RuntimeError, match="boom"):
        provider.generate("prompt")


def test_opencode_provider_requires_executable(monkeypatch):
    monkeypatch.setattr("nexus_os.portable.opencode_cli.shutil.which", lambda _: None)
    provider = OpenCodeCLIProvider()

    with pytest.raises(RuntimeError, match="not found"):
        provider.generate("prompt")


def test_opencode_provider_surfaces_timeout(monkeypatch):
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="opencode", timeout=kwargs["timeout"])

    monkeypatch.setattr("nexus_os.portable.opencode_cli.shutil.which", lambda _: "/usr/bin/fake")
    monkeypatch.setattr("nexus_os.portable.opencode_cli.subprocess.run", fake_run)
    provider = OpenCodeCLIProvider(timeout_seconds=5)

    with pytest.raises(RuntimeError, match="timed out after 5s"):
        provider.generate("prompt")


def test_opencode_provider_rejects_bad_timeout():
    with pytest.raises(RuntimeError, match="positive integer"):
        OpenCodeCLIProvider(timeout_seconds=0)


def test_registry_exposes_opencode():
    assert "opencode" in list_providers()
    provider = build_provider("opencode", "google/gemini-3-flash")
    assert isinstance(provider, OpenCodeCLIProvider)
    assert provider.model == "google/gemini-3-flash"


def test_registry_builds_opencode_without_model():
    provider = build_provider("OpenCode")
    assert isinstance(provider, OpenCodeCLIProvider)
    assert provider.model is None
