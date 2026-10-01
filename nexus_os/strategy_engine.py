from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .mission_classifier import MissionClassification, MissionKind


class StrategyMode(StrEnum):
    RESEARCH_FIRST = "research_first"
    PROTOTYPE_FIRST = "prototype_first"
    TEST_FIRST = "test_first"
    SECURITY_FIRST = "security_first"
    MIGRATION_SAFE = "migration_safe"
    COST_OPTIMIZED = "cost_optimized"
    BALANCED = "balanced"


@dataclass(frozen=True, slots=True)
class StrategyPlan:
    mode: StrategyMode
    rationale: tuple[str, ...]
    required_evidence: tuple[str, ...]
    max_repair_rounds: int
    escalation_threshold: float


class StrategyEngine:
    """Choose an inspectable execution strategy from deterministic mission evidence."""

    def choose(self, classification: MissionClassification) -> StrategyPlan:
        caps = classification.requirements.capabilities
        kind = classification.kind
        rationale: list[str] = []

        if "security" in caps:
            mode = StrategyMode.SECURITY_FIRST
            rationale.append("security capability detected")
        elif "database" in caps and kind in {MissionKind.DEPLOY, MissionKind.REFACTOR}:
            mode = StrategyMode.MIGRATION_SAFE
            rationale.append("database change with deploy/refactor intent")
        elif kind is MissionKind.TEST:
            mode = StrategyMode.TEST_FIRST
            rationale.append("test-only mission")
        elif kind is MissionKind.RESEARCH:
            mode = StrategyMode.RESEARCH_FIRST
            rationale.append("research mission")
        elif kind is MissionKind.FEATURE and classification.confidence >= 0.75:
            mode = StrategyMode.PROTOTYPE_FIRST
            rationale.append("high-confidence feature mission")
        elif classification.confidence < 0.7:
            mode = StrategyMode.RESEARCH_FIRST
            rationale.append("low classification confidence")
        else:
            mode = StrategyMode.BALANCED
            rationale.append("balanced default")

        required_evidence = ["acceptance criteria", "verification results", "evidence bundle"]
        if "security" in caps:
            required_evidence.append("security review")
        if "database" in caps:
            required_evidence.append("migration/rollback evidence")
        if "frontend" in caps:
            required_evidence.append("browser verification")
        if "backend" in caps:
            required_evidence.append("API contract verification")

        return StrategyPlan(
            mode=mode,
            rationale=tuple(rationale),
            required_evidence=tuple(required_evidence),
            max_repair_rounds=3,
            escalation_threshold=0.72,
        )
