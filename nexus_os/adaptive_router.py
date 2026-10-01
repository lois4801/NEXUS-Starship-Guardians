from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .guardian_registry import GuardianRegistry, RegisteredGuardian

if TYPE_CHECKING:
    from .adaptive_intelligence import AdaptiveGuardianIntelligence
    from .cognitive_evolution import CognitiveEvolutionEngine


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
    missing_tools: frozenset[str]
    sufficient: bool


class AdaptiveGuardianRouter:
    def __init__(
        self,
        registry: GuardianRegistry,
        intelligence: AdaptiveGuardianIntelligence | None = None,
        cognitive_evolution: CognitiveEvolutionEngine | None = None,
    ):
        self.registry = registry
        self.intelligence = intelligence
        self.cognitive_evolution = cognitive_evolution

    def _utility(
        self,
        guardian: RegisteredGuardian,
        required_capabilities: frozenset[str],
    ) -> float:
        utility = self.registry.utility(guardian)
        guardian_id = guardian.profile.guardian_id
        if self.intelligence is not None:
            utility += self.intelligence.routing_bonus(guardian_id, required_capabilities)
        if self.cognitive_evolution is not None:
            utility += self.cognitive_evolution.routing_bonus(guardian_id, required_capabilities)
        return utility

    def route(self, requirements: MissionRequirements) -> RoutingDecision:
        """Select a bounded team that collectively covers capabilities and tools.

        Historical utility ranks eligible contributors. Adaptive skill evidence and v0.8 cognitive
        calibration may add small bounded bonuses for repeatedly verified strengths. Permissions are
        never inferred from performance: a required tool counts as covered only when at least one
        selected Guardian explicitly has that tool in its allowlist.
        """
        broad = self.registry.all()
        broad.sort(
            key=lambda guardian: self._utility(guardian, requirements.capabilities),
            reverse=True,
        )

        selected: list[RegisteredGuardian] = []
        covered_capabilities: set[str] = set()
        covered_tools: set[str] = set()

        while len(selected) < requirements.maximum_guardians:
            remaining_capabilities = requirements.capabilities - covered_capabilities
            remaining_tools = requirements.tools - covered_tools
            if not remaining_capabilities and not remaining_tools:
                break

            best: RegisteredGuardian | None = None
            best_gain = 0
            best_utility = float("-inf")
            for guardian in broad:
                if guardian in selected:
                    continue
                capability_gain = len(guardian.profile.capabilities & remaining_capabilities)
                tool_gain = len(guardian.profile.allowed_tools & remaining_tools)
                gain = capability_gain + tool_gain
                utility = self._utility(guardian, remaining_capabilities)
                if gain > best_gain or (gain == best_gain and gain > 0 and utility > best_utility):
                    best = guardian
                    best_gain = gain
                    best_utility = utility
            if best is None or best_gain == 0:
                break
            selected.append(best)
            covered_capabilities.update(best.profile.capabilities)
            covered_tools.update(best.profile.allowed_tools)

        if not (requirements.capabilities - covered_capabilities) and not (
            requirements.tools - covered_tools
        ):
            for guardian in broad:
                if len(selected) >= requirements.minimum_guardians:
                    break
                if guardian not in selected:
                    selected.append(guardian)

        missing_capabilities = requirements.capabilities - covered_capabilities
        missing_tools = requirements.tools - covered_tools
        sufficient = (
            not missing_capabilities
            and not missing_tools
            and len(selected) >= requirements.minimum_guardians
        )
        return RoutingDecision(
            selected=selected,
            missing_capabilities=frozenset(missing_capabilities),
            missing_tools=frozenset(missing_tools),
            sufficient=sufficient,
        )
