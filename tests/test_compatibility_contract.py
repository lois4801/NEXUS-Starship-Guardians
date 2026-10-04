from __future__ import annotations

import os
import subprocess
import sys
from importlib import metadata

from fastapi.testclient import TestClient

from nexus_os import __version__
from nexus_os.api import create_app
from nexus_os.config import Settings
from nexus_os.storage import Store


def test_distribution_identity_is_nexus_starship_guardians():
    assert metadata.version("nexus-starship-guardians")


def test_legacy_python_namespace_remains_importable():
    import nexus_os  # noqa: F401


def test_canonical_and_legacy_cli_entrypoints_both_work():
    for command in ("nexus-guardians", "nexus-portable"):
        completed = subprocess.run(
            [command, "doctor"],
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert completed.returncode == 0, completed.stderr
        assert '"python"' in completed.stdout


def test_api_health_reports_current_product_version(tmp_path):
    settings = Settings(
        admin_token="test-admin-token",
        db_path=str(tmp_path / "compat.db"),
        dev_mode=True,
        model_base_url="http://localhost:11434/v1",
        model_name="llama3.2",
        model_api_key="",
        learning_path=str(tmp_path / "learning.jsonl"),
        evaluation_path=str(tmp_path / "evaluation.jsonl"),
        adaptive_intelligence_path=str(tmp_path / "adaptive.json"),
        cognitive_evolution_path=str(tmp_path / "cognitive.json"),
    )
    app = create_app(settings=settings, store=Store(settings.db_path))
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["version"] == __version__
    assert payload["learning"] == "enabled"
    assert payload["adaptive_guardian_intelligence"] == "live"
    assert payload["cognitive_evolution"] == "live"
    assert payload["adaptive_specialists"] == 20
    assert payload["mission_intelligence"] == "live"
    assert payload["intelligence_fabric"] == "live"


def test_module_entrypoint_is_importable_in_clean_python_process():
    env = os.environ.copy()
    env["NEXUS_DEV_MODE"] = "true"
    completed = subprocess.run(
        [sys.executable, "-c", "import nexus_os.api; print(nexus_os.api.app.title)"],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
        env=env,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Nexus Starship Guardians" in completed.stdout
