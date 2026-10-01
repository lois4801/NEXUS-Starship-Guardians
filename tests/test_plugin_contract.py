from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugin"
CLI_PATH = PLUGIN / "skills" / "nexus-run-operations" / "scripts" / "nexus_cli.py"


def _load_cli():
    spec = importlib.util.spec_from_file_location("nexus_plugin_cli", CLI_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_plugin_manifests_are_reconciled():
    portable = json.loads((PLUGIN / "plugin.json").read_text(encoding="utf-8"))
    codex = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))

    assert portable["name"] == "nexus-starship-guardians"
    assert codex["name"] == "nexus-starship-guardians"
    assert portable["version"] == codex["version"] == "0.3.0"
    assert portable["repository"] == codex["repository"]
    assert portable["repository"].endswith("/NEXUS-Starship-Guardians")
    assert portable["extensions"]["com.openai"]["interface"]["displayName"] == "Nexus Starship Guardians"
    assert codex["interface"]["displayName"] == "Nexus Starship Guardians"

    manifest_text = (PLUGIN / "plugin.json").read_text(encoding="utf-8")
    codex_text = (PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    assert "Agentic OS" not in manifest_text
    assert "Agentic OS" not in codex_text


def test_plugin_contains_six_skills():
    skill_files = sorted((PLUGIN / "skills").glob("*/SKILL.md"))
    assert len(skill_files) == 6
    assert {path.parent.name for path in skill_files} == {
        "host-workspace-operator",
        "nexus-app-integration",
        "nexus-project-setup",
        "nexus-readiness-review",
        "nexus-run-operations",
        "sandbox-python-executor",
    }


def test_plugin_docs_do_not_use_retired_product_name():
    checked = [PLUGIN / "README.md", PLUGIN / "REVIEWER_TESTS.md"]
    checked.extend((PLUGIN / "skills").glob("*/SKILL.md"))
    for path in checked:
        assert "Agentic OS" not in path.read_text(encoding="utf-8"), path


def test_cli_safe_view_translates_legacy_agent_to_guardian():
    cli = _load_cli()
    view = cli.safe_view(
        {
            "status": "completed",
            "run_id": "abcdefgh",
            "project_id": "lucio-dev",
            "agent": "builder",
            "answer": "done",
            "steps_used": 2,
        }
    )
    assert view["guardian"] == "builder"
    assert "agent" not in view


def test_cli_rejects_non_loopback_http(monkeypatch):
    cli = _load_cli()
    monkeypatch.setenv("NEXUS_URL", "http://example.com")
    with pytest.raises(ValueError, match="HTTPS"):
        cli._base_url()


def test_cli_guardian_flag_uses_rest_v1_agent_wire_field(monkeypatch, capsys):
    cli = _load_cli()
    captured = {}

    def fake_request(method, path, payload=None, auth=True):
        captured.update(method=method, path=path, payload=payload, auth=auth)
        return {
            "status": "completed",
            "run_id": "abcdefgh",
            "project_id": "lucio-dev",
            "agent": payload["agent"],
            "answer": "ok",
            "steps_used": 1,
        }

    monkeypatch.setattr(cli, "request", fake_request)
    exit_code = cli.main(
        [
            "run",
            "--project",
            "lucio-dev",
            "--guardian",
            "builder",
            "--goal",
            "check the build",
        ]
    )
    assert exit_code == 0
    assert captured["payload"] == {"goal": "check the build", "agent": "builder"}
    output = json.loads(capsys.readouterr().out)
    assert output["guardian"] == "builder"


def test_cli_legacy_agent_flag_remains_supported(monkeypatch):
    cli = _load_cli()
    captured = {}

    def fake_request(method, path, payload=None, auth=True):
        captured["payload"] = payload
        return {
            "status": "completed",
            "run_id": "abcdefgh",
            "project_id": "lucio-dev",
            "agent": payload["agent"],
            "answer": "ok",
            "steps_used": 1,
        }

    monkeypatch.setattr(cli, "request", fake_request)
    assert cli.main(["run", "--project", "lucio-dev", "--agent", "general", "--goal", "test"]) == 0
    assert captured["payload"]["agent"] == "general"
