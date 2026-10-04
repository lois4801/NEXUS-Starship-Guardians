from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from nexus_os.adaptive_intelligence import SPECIALIST_INTELLIGENCE_PROFILES
from nexus_os.adaptive_router import AdaptiveGuardianRouter, MissionRequirements
from nexus_os.api import create_app
from nexus_os.config import Settings
from nexus_os.guardian_registry import GuardianProfile, GuardianRegistry
from nexus_os.mission_runtime import MissionRuntime
from nexus_os.storage import Store
from nexus_os.tool_gateway import ControlledToolGateway


def test_router_can_cover_capabilities_and_tools_across_multiple_guardians():
    registry = GuardianRegistry()
    registry.register(GuardianProfile("frontend-guardian", "Frontend Guardian", frozenset({"frontend"}), frozenset({"browser"})))
    registry.register(GuardianProfile("backend-guardian", "Backend Guardian", frozenset({"backend"}), frozenset({"api"})))
    decision = AdaptiveGuardianRouter(registry).route(
        MissionRequirements(frozenset({"frontend", "backend"}), frozenset({"browser", "api"}), minimum_guardians=2, maximum_guardians=4)
    )
    assert decision.sufficient
    assert {item.profile.guardian_id for item in decision.selected} == {"frontend-guardian", "backend-guardian"}


def test_gateway_never_grants_permission_from_requirement_alone():
    decision = ControlledToolGateway().authorize("database", project_tools=frozenset({"database"}), guardian_tools=frozenset())
    assert not decision.allowed


def test_mission_runtime_marks_project_disabled_tools_as_blocked():
    plan = MissionRuntime().plan("Build a React API with Postgres tests", project_gateway_tools=frozenset({"browser", "api", "test"}))
    assert "database" in plan.blocked_tools
    assert not plan.sufficient


def test_default_live_registry_includes_all_adaptive_specialists():
    registered = {item.profile.guardian_id for item in MissionRuntime().registry.all()}
    expected = {profile.guardian_id for profile in SPECIALIST_INTELLIGENCE_PROFILES}
    assert expected <= registered
    assert len(expected) == 32


@pytest.fixture
def api(tmp_path):
    settings = Settings(
        admin_token="test-admin-secret",
        db_path=str(tmp_path / "runtime.db"),
        model_base_url="http://localhost:11434/v1",
        model_api_key="",
        model_name="llama3.2",
        dev_mode=True,
        learning_path=str(tmp_path / "learning.jsonl"),
        evaluation_path=str(tmp_path / "evaluation.jsonl"),
        adaptive_intelligence_path=str(tmp_path / "adaptive.json"),
        cognitive_evolution_path=str(tmp_path / "cognitive.json"),
    )
    return TestClient(create_app(settings, Store(settings.db_path)))


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _project(api: TestClient, *, gateway_tools: list[str]) -> str:
    response = api.post(
        "/v1/projects",
        headers=_headers("test-admin-secret"),
        json={"project_id": "lucio", "display_name": "Lucio", "agents": ["general"], "gateway_tools": gateway_tools},
    )
    assert response.status_code == 201, response.text
    return response.json()["api_key"]


def test_mission_plan_endpoint_is_project_scoped_and_permission_aware(api):
    key = _project(api, gateway_tools=["browser", "api", "test"])
    response = api.post("/v1/projects/lucio/mission-plan", headers=_headers(key), json={"goal": "Build a React API with tests"})
    assert response.status_code == 200
    assert response.json()["selected_guardians"]


def test_cognitive_summary_endpoint_is_project_scoped(api):
    key = _project(api, gateway_tools=[])
    response = api.get("/v1/projects/lucio/guardians/api-specialist/cognitive-summary", headers=_headers(key))
    assert response.status_code == 200
    payload = response.json()
    assert payload["adaptive"]["guardian_id"] == "api-specialist"
    assert payload["cognitive"]["guardian_id"] == "api-specialist"
    assert "curriculum" in payload["cognitive"]


def test_integration_readiness_is_not_a_connection_claim(api):
    key = _project(api, gateway_tools=["integration", "api"])
    response = api.get("/v1/projects/lucio/integrations/lucio/readiness", headers=_headers(key))
    assert response.status_code == 200
    assert response.json()["connected"] is False


def test_unknown_integration_contract_returns_404(api):
    key = _project(api, gateway_tools=[])
    response = api.get("/v1/projects/lucio/integrations/not-real/readiness", headers=_headers(key))
    assert response.status_code == 404
