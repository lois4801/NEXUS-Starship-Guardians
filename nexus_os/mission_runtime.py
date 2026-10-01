from __future__ import annotations

import re
from dataclasses import dataclass

from .adaptive_router import AdaptiveGuardianRouter
from .guardian_registry import GuardianProfile, GuardianRegistry
from .guardian_teams import artificial_architecture_team
from .mission_classifier import MissionClassifier
from .tool_gateway import ControlledToolGateway

_DIVISION_CAPABILITIES: dict[str, frozenset[str]] = {
    "command": frozenset({"architecture", "general-engineering"}),
    "learning": frozenset({"ai-engineering", "testing", "architecture"}),
    "code-quality": frozenset({"testing", "security", "frontend", "backend"}),
    "source-control": frozenset({"devops", "integration", "architecture"}),
    "verification": frozenset({"testing", "backend", "frontend"}),
    "execution": frozenset({"devops", "integration", "database"}),
    "repair": frozenset({"testing", "backend", "frontend"}),
    "operations": frozenset({"observability", "devops"}),
}

_DIVISION_TOOLS: dict[str, frozenset[str]] = {
    "command": frozenset(),
    "learning": frozenset({"model", "test"}),
    "code-quality": frozenset({"test", "security"}),
    "source-control": frozenset({"terminal", "integration"}),
    "verification": frozenset({"test", "api", "browser"}),
    "execution": frozenset({"terminal", "database", "integration"}),
    "repair": frozenset({"test", "api", "browser"}),
    "operations": frozenset({"observability", "terminal"}),
}


@dataclass(frozen=True, slots=True)
class LiveMissionPlan:
    kind: str
    confidence: float
    capabilities: frozenset[str]
    required_tools: frozenset[str]
    selected_guardians: tuple[str, ...]
    missing_capabilities: frozenset[str]
    missing_tools: frozenset[str]
    blocked_tools: frozenset[str]
    sufficient: bool
    reasons: tuple[str, ...]


class MissionRuntime:
    """Live, inspectable mission classification and permission-safe Guardian routing."""

    def __init__(
        self,
        classifier: MissionClassifier | None = None,
        registry: GuardianRegistry | None = None,
        gateway: ControlledToolGateway | None = None,
    ) -> None:
        self.classifier = classifier or MissionClassifier()
        self.registry = registry or build_default_guardian_registry()
        self.router = AdaptiveGuardianRouter(self.registry)
        self.gateway = gateway or ControlledToolGateway()

    def plan(self, goal: str, *, project_gateway_tools: frozenset[str]) -> LiveMissionPlan:
        classification = self.classifier.classify(goal)
        blocked_tools = self.gateway.blocked_tools(
            classification.requirements.tools,
            project_tools=project_gateway_tools,
        )
        routable_requirements = classification.requirements
        decision = self.router.route(routable_requirements)
        sufficient = decision.sufficient and not blocked_tools
        return LiveMissionPlan(
            kind=classification.kind.value,
            confidence=classification.confidence,
            capabilities=classification.requirements.capabilities,
            required_tools=classification.requirements.tools,
            selected_guardians=tuple(item.profile.guardian_id for item in decision.selected),
            missing_capabilities=decision.missing_capabilities,
            missing_tools=decision.missing_tools,
            blocked_tools=blocked_tools,
            sufficient=sufficient,
            reasons=classification.reasons,
        )


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def build_default_guardian_registry() -> GuardianRegistry:
    registry = GuardianRegistry()
    for role in artificial_architecture_team():
        capabilities = set(_DIVISION_CAPABILITIES.get(role.division, frozenset()))
        tools = set(_DIVISION_TOOLS.get(role.division, frozenset()))

        name = role.name.casefold()
        if "api" in name:
            capabilities.add("backend")
            tools.add("api")
        if "browser" in name:
            capabilities.add("frontend")
            tools.add("browser")
        if "security" in name:
            capabilities.add("security")
            tools.add("security")
        if "database" in name or "queue" in name:
            capabilities.add("database")
            tools.add("database")
        if "observability" in name:
            capabilities.add("observability")
            tools.add("observability")
        if "integration" in name:
            capabilities.add("integration")
            tools.add("integration")
        if "test" in name or "regression" in name or "evaluation" in name:
            capabilities.add("testing")
            tools.add("test")
        if "learning" in name or "fine-tuning" in name:
            capabilities.add("ai-engineering")
            tools.add("model")
        if "git" in name or "release" in name or "conflict" in name:
            capabilities.add("devops")
            tools.add("terminal")

        registry.register(
            GuardianProfile(
                guardian_id=_slug(role.name),
                role=role.name,
                capabilities=frozenset(capabilities or {"general-engineering"}),
                allowed_tools=frozenset(tools),
            )
        )
    return registry
