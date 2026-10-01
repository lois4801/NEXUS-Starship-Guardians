from __future__ import annotations

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _runtime_version() -> str:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return data["project"]["version"]


def _plugin_version() -> str:
    data = json.loads((ROOT / "plugin" / "plugin.json").read_text(encoding="utf-8"))
    return data["version"]


def test_runtime_and_plugin_release_versions_match() -> None:
    assert _runtime_version() == _plugin_version()


def test_current_state_graph_is_repo_visible() -> None:
    doc = ROOT / "docs" / "CURRENT_STATE.md"
    visual = ROOT / "docs" / "assets" / "current-state-graph.svg"
    assert doc.is_file()
    assert visual.is_file()
    text = doc.read_text(encoding="utf-8")
    assert "NEXUS STARSHIP GUARDIANS" in text
    assert "Guardian Benchmark Vault" in text
    assert "GitHub Release" in text
    assert "GHCR Package" in text


def test_benchmark_vault_docs_and_animation_are_repo_visible() -> None:
    doc = ROOT / "docs" / "GUARDIAN_BENCHMARK_VAULT.md"
    visual = ROOT / "docs" / "assets" / "guardian-benchmark-vault.svg"
    assert doc.is_file()
    assert visual.is_file()
    assert "Benchmark Vault" in doc.read_text(encoding="utf-8")
    svg = visual.read_text(encoding="utf-8")
    assert "GUARDIAN BENCHMARK VAULT" in svg
    assert "<animate" in svg


def test_release_workflow_has_required_publish_permissions_and_outputs() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yaml").read_text(encoding="utf-8")
    assert "contents: write" in workflow
    assert "packages: write" in workflow
    assert "gh release create" in workflow
    assert "docker push" in workflow
    assert "python -m build" in workflow
