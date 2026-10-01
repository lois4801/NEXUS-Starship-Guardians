"""Minimal Python SDK for Lucio, Ember, and future Python applications."""

import httpx


class NexusClient:
    def __init__(self, base_url: str, api_key: str):
        self.client = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=65,
        )

    def create_run(self, project_id: str, goal: str, agent: str = "general") -> dict:
        """Create a REST v1 run; `agent` remains the compatibility wire field for Guardian."""
        response = self.client.post(
            f"/v1/projects/{project_id}/runs",
            json={"goal": goal, "agent": agent},
        )
        response.raise_for_status()
        return response.json()

    def plan_mission(self, project_id: str, goal: str) -> dict:
        response = self.client.post(
            f"/v1/projects/{project_id}/mission-plan",
            json={"goal": goal},
        )
        response.raise_for_status()
        return response.json()

    def integration_readiness(self, project_id: str, integration_name: str) -> dict:
        response = self.client.get(
            f"/v1/projects/{project_id}/integrations/{integration_name}/readiness"
        )
        response.raise_for_status()
        return response.json()

    def get_run(self, run_id: str) -> dict:
        response = self.client.get(f"/v1/runs/{run_id}")
        response.raise_for_status()
        return response.json()

    def approve(self, run_id: str, approved: bool) -> dict:
        response = self.client.post(
            f"/v1/runs/{run_id}/approval",
            json={"approved": approved},
        )
        response.raise_for_status()
        return response.json()

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
