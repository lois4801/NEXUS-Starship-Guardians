from __future__ import annotations

from dataclasses import dataclass

from .guardian_registry import GuardianRegistry, RegisteredGuardian


@dataclass(frozen=True, slots=True)
class MissionRequirements:
    capabilities: frozenset[str]
    tools: frozenset[str] = frozenset()
    minimum_guardians: int = 1
    maximum_guardians: int = 8

    def __post_init__(self) -> None:
        if self.minimum_guardians < 1:
            raise ValueError("minimum_guardians must be at least 1")
        if self.maximum_guardians < self.minimum_guardians:
            raise ValueError("maximum_guardians must be >= minimum_guardians")
        if self.maximum_guardians > 200:
            raise ValueError("maximum_guardians cannot exceed 200")


@dataclass(slots=True)
class RoutingDecision:
    selected: list[RegisteredGuardian]
    missing_capabilities: frozenset[str]
    sufficient: bool


class AdaptiveGuardianRouter:
    def __init__(self, registry: GuardianRegistry):
        self.registry = registry

    def route(self, requirements: MissionRequirements) -> RoutingDecision:
        candidates = self.registry.select(
            required_capabilities=requirements.capabilities,
            required_tools=requirements.tools,
            limit=requirements.maximum_guardians,
        )
        if len(candidates) >= requirements.minimum_guardians:
            return RoutingDecision(candidates, frozenset(), True)

        covered: set[str] = set()
        broad = self.registry.select(required_tools=requirements.tools, limit=requirements.maximum_guardians)
        selected: list[RegisteredGuardian] = []
        for guardian in broad:
            contribution = guardian.profile.capabilities & requirements.capabilities
            if contribution - covered:
                selected.append(guardian)
                covered.update(contribution)
            if requirements.capabilities.issubset(covered):
                break
        missing = requirements.capabilities - covered
        sufficient = not missing and len(selected) >= requirements.minimum_guardians
        return RoutingDecision(selected, frozenset(missing), sufficient)
