"""Nexus Starship Guardians REST API with project-scoped keys and bounded execution."""

import secrets
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException

from . import __version__
from .adaptive_intelligence import AdaptiveGuardianIntelligence
from .config import Settings
from .integration_contracts import IntegrationContractRegistry
from .intelligence_fabric import IntelligenceFabric
from .learning_memory import GuardianLearningEngine, JsonlLearningStore
from .mission_runtime import MissionRuntime
from .models import (
    Approval,
    IntegrationReadinessView,
    IntelligencePlanView,
    MissionPlanRequest,
    MissionPlanView,
    ProjectCreate,
    ProjectCreated,
    ProjectInfo,
    RunCreate,
    RunView,
)
from .observability import install_http_tracing
from .orchestrator import Orchestrator
from .server_learning import ServerLearningRecorder
from .storage import Store


def create_app(settings: Settings | None = None, store: Store | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    store = store or Store(settings.db_path)
    learning = GuardianLearningEngine(JsonlLearningStore(Path(settings.learning_path)))
    adaptive_intelligence = AdaptiveGuardianIntelligence(Path(settings.adaptive_intelligence_path))
    learning_recorder = ServerLearningRecorder(learning, adaptive_intelligence)
    mission_runtime = MissionRuntime(adaptive_intelligence=adaptive_intelligence)
    intelligence_fabric = IntelligenceFabric(classifier=mission_runtime.classifier)
    integrations = IntegrationContractRegistry()
    orchestrator = Orchestrator(
        store,
        settings,
        learning_recorder=learning_recorder,
        mission_runtime=mission_runtime,
        intelligence_fabric=intelligence_fabric,
    )
    app = FastAPI(title="Nexus Starship Guardians", version=__version__, docs_url="/docs")
    install_http_tracing(app)

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

    def scoped_project(project_id: str, principal: str) -> ProjectCreate:
        require_scope(principal, project_id)
        project = store.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    def scoped_run(run_id: str, principal: str) -> dict[str, Any]:
        run = store.get_run(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        require_scope(principal, run["project_id"])
        return run

    def mission_view(goal: str, project: ProjectCreate) -> MissionPlanView:
        plan = mission_runtime.plan(goal, project_gateway_tools=frozenset(project.gateway_tools))
        return MissionPlanView(
            kind=plan.kind,
            confidence=plan.confidence,
            capabilities=sorted(plan.capabilities),
            required_tools=sorted(plan.required_tools),
            selected_guardians=list(plan.selected_guardians),
            missing_capabilities=sorted(plan.missing_capabilities),
            missing_tools=sorted(plan.missing_tools),
            blocked_tools=sorted(plan.blocked_tools),
            sufficient=plan.sufficient,
            reasons=list(plan.reasons),
        )

    def intelligence_view(goal: str) -> IntelligencePlanView:
        plan = intelligence_fabric.plan(goal)
        return IntelligencePlanView(
            kind=plan.classification.kind.value,
            confidence=plan.classification.confidence,
            uncertainty=plan.uncertainty,
            capabilities=sorted(plan.classification.requirements.capabilities),
            required_tools=sorted(plan.classification.requirements.tools),
            strategy=plan.strategy.mode.value,
            strategy_rationale=list(plan.strategy.rationale),
            required_evidence=list(plan.strategy.required_evidence),
            adversarial_cases=[
                {
                    "case_id": case.case_id,
                    "title": case.title,
                    "expected_guardrail": case.expected_guardrail,
                    "category": case.category,
                }
                for case in plan.adversarial_cases
            ],
            assumptions=list(plan.assumptions),
        )

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "version": __version__,
            "mode": "dev" if settings.dev_mode else "configured",
            "learning": "enabled",
            "adaptive_guardian_intelligence": "live",
            "adaptive_specialists": len(adaptive_intelligence.profiles()),
            "mission_intelligence": "live",
            "intelligence_fabric": "live",
        }

    @app.post("/v1/projects", response_model=ProjectCreated, status_code=201)
    def create_project(spec: ProjectCreate, principal: str = Depends(authenticate)):
        if principal != "__admin__":
            raise HTTPException(status_code=403, detail="Admin key required")
        if not spec.agents or len(spec.agents) != len(set(spec.agents)):
            raise HTTPException(status_code=422, detail="Guardians must be nonempty and unique")
        if len(spec.allowed_tools) != len(set(spec.allowed_tools)):
            raise HTTPException(status_code=422, detail="Tools must be unique")
        if len(spec.gateway_tools) != len(set(spec.gateway_tools)):
            raise HTTPException(status_code=422, detail="Gateway tools must be unique")
        key = "nxs_" + secrets.token_urlsafe(32)
        try:
            store.add_project(spec, key)
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=409, detail="Project already exists") from exc
        return ProjectCreated(project=ProjectInfo.model_validate(spec.model_dump()), api_key=key)

    @app.get("/v1/projects/{project_id}", response_model=ProjectInfo)
    def get_project(project_id: str, principal: str = Depends(authenticate)):
        return scoped_project(project_id, principal)

    @app.post("/v1/projects/{project_id}/mission-plan", response_model=MissionPlanView)
    def plan_mission(
        project_id: str,
        payload: MissionPlanRequest,
        principal: str = Depends(authenticate),
    ):
        project = scoped_project(project_id, principal)
        return mission_view(payload.goal, project)

    @app.post("/v1/projects/{project_id}/intelligence-plan", response_model=IntelligencePlanView)
    def plan_intelligence(
        project_id: str,
        payload: MissionPlanRequest,
        principal: str = Depends(authenticate),
    ):
        scoped_project(project_id, principal)
        return intelligence_view(payload.goal)

    @app.get(
        "/v1/projects/{project_id}/integrations/{integration_name}/readiness",
        response_model=IntegrationReadinessView,
    )
    def integration_readiness(
        project_id: str,
        integration_name: str,
        principal: str = Depends(authenticate),
    ):
        project = scoped_project(project_id, principal)
        available_capabilities = frozenset(
            capability
            for guardian in mission_runtime.registry.all()
            for capability in guardian.profile.capabilities
        )
        try:
            readiness = integrations.assess(
                integration_name,
                available_capabilities=available_capabilities,
                enabled_tools=frozenset(project.gateway_tools),
                connected=False,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return IntegrationReadinessView(
            integration=readiness.integration,
            description=readiness.description,
            connected=readiness.connected,
            required_capabilities=sorted(readiness.required_capabilities),
            required_tools=sorted(readiness.required_tools),
            missing_capabilities=sorted(readiness.missing_capabilities),
            missing_tools=sorted(readiness.missing_tools),
            ready=readiness.ready,
        )

    @app.post("/v1/projects/{project_id}/runs", response_model=RunView, status_code=201)
    def start_run(project_id: str, payload: RunCreate, principal: str = Depends(authenticate)):
        project = scoped_project(project_id, principal)
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
        scoped_project(project_id, principal)
        return {"notes": store.list_notes(project_id)}

    return app


def get_app() -> FastAPI:
    return create_app()


app = get_app()  # production requires NEXUS_ADMIN_TOKEN; use NEXUS_DEV_MODE=true only on localhost
