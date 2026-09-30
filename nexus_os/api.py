"""Nexus Starship Guardians REST API with project-scoped keys and bounded execution."""

import secrets
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException

from .config import Settings
from .learning_memory import GuardianLearningEngine, JsonlLearningStore
from .models import Approval, ProjectCreate, ProjectCreated, ProjectInfo, RunCreate, RunView
from .orchestrator import Orchestrator
from .server_learning import ServerLearningRecorder
from .storage import Store


def create_app(settings: Settings | None = None, store: Store | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    store = store or Store(settings.db_path)
    learning = GuardianLearningEngine(JsonlLearningStore(Path(settings.learning_path)))
    learning_recorder = ServerLearningRecorder(learning)
    orchestrator = Orchestrator(store, settings, learning_recorder=learning_recorder)
    app = FastAPI(title="Nexus Starship Guardians", version="0.3.0-dev", docs_url="/docs")

    def authenticate(authorization: str | None = Header(default=None)) -> str:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Bearer authentication required")
        token = authorization[7:]
        if not token:
            raise HTTPException(status_code=401, detail="Invalid bearer token")
        if secrets.compare_digest(token, settings.admin_token):
            return "__admin__"
        project_id = store.key_project(token)
        if not project_id:
            raise HTTPException(status_code=401, detail="Invalid bearer token")
        return project_id

    def require_scope(principal: str, project_id: str) -> None:
        if principal not in ("__admin__", project_id):
            raise HTTPException(status_code=403, detail="Project access denied")

    def scoped_run(run_id: str, principal: str) -> dict[str, Any]:
        run = store.get_run(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        require_scope(principal, run["project_id"])
        return run

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "version": "0.3.0-dev",
            "mode": "dev" if settings.dev_mode else "configured",
            "learning": "enabled",
        }

    @app.post("/v1/projects", response_model=ProjectCreated, status_code=201)
    def create_project(spec: ProjectCreate, principal: str = Depends(authenticate)):
        if principal != "__admin__":
            raise HTTPException(status_code=403, detail="Admin key required")
        if not spec.agents or len(spec.agents) != len(set(spec.agents)):
            raise HTTPException(status_code=422, detail="Guardians must be nonempty and unique")
        if len(spec.allowed_tools) != len(set(spec.allowed_tools)):
            raise HTTPException(status_code=422, detail="Tools must be unique")
        key = "nxs_" + secrets.token_urlsafe(32)
        try:
            store.add_project(spec, key)
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=409, detail="Project already exists") from exc
        return ProjectCreated(project=ProjectInfo.model_validate(spec.model_dump()), api_key=key)

    @app.get("/v1/projects/{project_id}", response_model=ProjectInfo)
    def get_project(project_id: str, principal: str = Depends(authenticate)):
        require_scope(principal, project_id)
        project = store.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    @app.post("/v1/projects/{project_id}/runs", response_model=RunView, status_code=201)
    def start_run(project_id: str, payload: RunCreate, principal: str = Depends(authenticate)):
        require_scope(principal, project_id)
        project = store.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if payload.agent not in project.agents:
            raise HTTPException(status_code=403, detail="Guardian not enabled for this project")
        run_id = store.add_run(project_id, payload.agent, payload.goal)
        return orchestrator.advance(run_id)

    @app.get("/v1/runs/{run_id}", response_model=RunView)
    def get_run(run_id: str, principal: str = Depends(authenticate)):
        return scoped_run(run_id, principal)

    @app.post("/v1/runs/{run_id}/approval", response_model=RunView)
    def approve_run(run_id: str, payload: Approval, principal: str = Depends(authenticate)):
        scoped_run(run_id, principal)
        try:
            return orchestrator.advance(run_id, approved=payload.approved)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.get("/v1/projects/{project_id}/notes")
    def get_notes(project_id: str, principal: str = Depends(authenticate)):
        require_scope(principal, project_id)
        if not store.get_project(project_id):
            raise HTTPException(status_code=404, detail="Project not found")
        return {"notes": store.list_notes(project_id)}

    return app


def get_app() -> FastAPI:
    return create_app()


app = get_app()  # production requires NEXUS_ADMIN_TOKEN; use NEXUS_DEV_MODE=true only on localhost
