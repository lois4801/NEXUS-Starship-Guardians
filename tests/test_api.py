"""Real API tests with deterministic provider; no paid model or network dependency."""

import pytest
from fastapi.testclient import TestClient

from nexus_os.api import create_app
from nexus_os.config import Settings
from nexus_os.storage import Store


@pytest.fixture
def api(tmp_path):
    settings = Settings("test-admin-secret", str(tmp_path / "nexus.db"), "http://localhost:11434/v1", "", "llama3.2", True)
    app = create_app(settings, Store(settings.db_path))
    return TestClient(app)


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def add_project(api, name="lucio", tools=None, agents=None, gateway_tools=None):
    result = api.post("/v1/projects", headers=headers("test-admin-secret"), json={
        "project_id": name,
        "display_name": name,
        "agents": agents or ["general"],
        "allowed_tools": tools if tools is not None else ["calculator", "utc_now"],
        "gateway_tools": gateway_tools or [],
    })
    assert result.status_code == 201, result.text
    return result.json()["api_key"]


def test_requires_auth_and_admin(api):
    assert api.get("/v1/projects/lucio").status_code == 401
    key = add_project(api)
    assert api.post("/v1/projects", headers=headers(key), json={"project_id": "ember", "display_name": "Ember"}).status_code == 403
    health = api.get("/health").json()
    assert health["status"] == "ok"
    assert health["mission_intelligence"] == "live"
    assert health["intelligence_fabric"] == "live"
    assert api.get("/v1/projects/lucio", headers=headers(key)).status_code == 200


def test_real_tool_execution_and_trace(api):
    key = add_project(api)
    r = api.post("/v1/projects/lucio/runs", headers=headers(key), json={"goal": "calculate 12 * 7"})
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "completed"
    assert "84" in data["answer"]
    assert [e["type"] for e in data["events"]] == [
        "mission_intelligence",
        "strategy_intelligence",
        "tool_result",
        "final",
    ]
    assert "selected_guardians" in data["events"][0]
    strategy = data["events"][1]
    assert strategy["strategy"]
    assert strategy["required_evidence"]
    assert api.get("/v1/runs/" + data["run_id"], headers=headers(key)).status_code == 200


def test_intelligence_plan_is_project_scoped_and_inspectable(api):
    key = add_project(api)
    response = api.post(
        "/v1/projects/lucio/intelligence-plan",
        headers=headers(key),
        json={"goal": "Deploy a secure FastAPI service with PostgreSQL migration and tests"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["strategy"] == "security_first"
    assert "security review" in data["required_evidence"]
    assert "database" in data["capabilities"]
    assert data["adversarial_cases"]
    assert 0 <= data["uncertainty"] <= 1


def test_cross_project_isolation(api):
    lucio = add_project(api, "lucio")
    ember = add_project(api, "ember")
    run = api.post("/v1/projects/lucio/runs", headers=headers(lucio), json={"goal": "utc now"}).json()
    assert api.get("/v1/projects/lucio", headers=headers(ember)).status_code == 403
    assert api.post("/v1/projects/lucio/runs", headers=headers(ember), json={"goal": "utc now"}).status_code == 403
    assert api.post("/v1/projects/lucio/intelligence-plan", headers=headers(ember), json={"goal": "test"}).status_code == 403
    assert api.get("/v1/runs/" + run["run_id"], headers=headers(ember)).status_code == 403
    assert api.post("/v1/runs/" + run["run_id"] + "/approval", headers=headers(ember), json={"approved": True}).status_code == 403


def test_agent_allowlist(api):
    key = add_project(api, agents=["general"])
    assert api.post("/v1/projects/lucio/runs", headers=headers(key), json={"goal": "test", "agent": "builder"}).status_code == 403


def test_demo_provider_does_not_fabricate_app_building(api):
    key = add_project(api)
    data = api.post("/v1/projects/lucio/runs", headers=headers(key), json={"goal": "build a live SaaS"}).json()
    assert data["status"] == "completed"
    assert "Demo provider only supports" in data["answer"]


def test_duplicate_project_rejected(api):
    add_project(api)
    assert api.post("/v1/projects", headers=headers("test-admin-secret"), json={"project_id": "lucio", "display_name": "Second"}).status_code == 409


def test_notes_are_project_scoped(api):
    lucio = add_project(api, "lucio", tools=["project_note"])
    ember = add_project(api, "ember", tools=["project_note"])
    from nexus_os import orchestrator as orch
    from nexus_os.models import Action
    original = orch.get_provider

    class FakeProvider:
        def next_action(self, goal, agent, history, available, model):
            if any(e["type"] == "tool_result" for e in history):
                return Action(type="final", answer="saved")
            return Action(type="tool", tool="project_note", arguments={"content": goal})

    orch.get_provider = lambda project, settings: FakeProvider()
    try:
        run = api.post("/v1/projects/lucio/runs", headers=headers(lucio), json={"goal": "Scoped example"}).json()
        assert run["status"] == "pending_approval"
        assert api.get("/v1/projects/lucio/notes", headers=headers(lucio)).json()["notes"] == []
        assert api.post(f"/v1/runs/{run['run_id']}/approval", headers=headers(ember), json={"approved": True}).status_code == 403
        done = api.post(f"/v1/runs/{run['run_id']}/approval", headers=headers(lucio), json={"approved": True}).json()
        assert done["status"] == "completed"
        assert api.get("/v1/projects/lucio/notes", headers=headers(lucio)).json()["notes"][0]["content"] == "Scoped example"
        assert api.get("/v1/projects/ember/notes", headers=headers(ember)).json()["notes"] == []
    finally:
        orch.get_provider = original


def test_denial_prevents_write(api):
    key = add_project(api, tools=["project_note"])
    from nexus_os import orchestrator as orch
    from nexus_os.models import Action
    original = orch.get_provider

    class FakeProvider:
        def next_action(self, goal, agent, history, available, model):
            return Action(type="tool", tool="project_note", arguments={"content": "Secret"})

    orch.get_provider = lambda project, settings: FakeProvider()
    try:
        run = api.post("/v1/projects/lucio/runs", headers=headers(key), json={"goal": "Write"}).json()
        done = api.post(f"/v1/runs/{run['run_id']}/approval", headers=headers(key), json={"approved": False}).json()
        assert done["status"] == "completed"
        assert api.get("/v1/projects/lucio/notes", headers=headers(key)).json()["notes"] == []
    finally:
        orch.get_provider = original
