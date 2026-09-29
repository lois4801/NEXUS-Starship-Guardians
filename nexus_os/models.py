"""Versioned API data contracts."""

from typing import Any, Literal
from pydantic import BaseModel, Field

AgentId = Literal["general", "builder", "research"]
ProviderId = Literal["demo", "openai_compatible"]
ToolId = Literal["calculator", "utc_now", "project_note"]
RunStatus = Literal["completed", "pending_approval", "failed", "max_steps"]

AGENT_PROFILES = {
    "general": "You are a general-purpose assistant. Use only the supplied tools.",
    "builder": "You are a software delivery planner. Never claim code was written or tested unless tool results prove it.",
    "research": "You are a research assistant. Never claim live web access or verified external facts without an actual source tool.",
}


class ProjectCreate(BaseModel):
    project_id: str = Field(pattern=r"^[a-z][a-z0-9-]{2,47}$")
    display_name: str = Field(min_length=1, max_length=120)
    provider: ProviderId = "demo"
    model: str | None = Field(default=None, max_length=120)
    agents: list[AgentId] = Field(default_factory=lambda: ["general"])
    allowed_tools: list[ToolId] = Field(default_factory=lambda: ["calculator", "utc_now"])
    max_steps: int = Field(default=5, ge=1, le=12)


class ProjectInfo(ProjectCreate):
    pass


class ProjectCreated(BaseModel):
    project: ProjectInfo
    api_key: str = Field(description="Only returned once. Store securely.")


class RunCreate(BaseModel):
    goal: str = Field(min_length=1, max_length=4000)
    agent: AgentId = "general"


class Action(BaseModel):
    type: Literal["tool", "final"]
    tool: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    answer: str | None = None


class RunView(BaseModel):
    run_id: str
    project_id: str
    agent: AgentId
    goal: str
    status: RunStatus
    answer: str | None
    steps_used: int
    events: list[dict[str, Any]]
    pending_approval: dict[str, Any] | None = None


class Approval(BaseModel):
    approved: bool
