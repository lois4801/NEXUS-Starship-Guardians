from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .adaptive_router import MissionRequirements
from .capability_map import CapabilityMap


class MissionKind(StrEnum):
    BUG_FIX = "bug_fix"
    FEATURE = "feature"
    REFACTOR = "refactor"
    TEST = "test"
    DEPLOY = "deploy"
    RESEARCH = "research"
    GENERAL = "general"


@dataclass(frozen=True, slots=True)
class MissionClassification:
    kind: MissionKind
    requirements: MissionRequirements
    confidence: float
    reasons: tuple[str, ...]


class MissionClassifier:
    """Deterministically translate a user mission into explicit routing requirements."""

    def __init__(self, capability_map: CapabilityMap | None = None):
        self.capability_map = capability_map or CapabilityMap()

    def classify(self, mission: str) -> MissionClassification:
        text = mission.strip()
        if not text:
            raise ValueError("mission cannot be empty")
        normalized = text.casefold()
        kind, kind_reason = self._kind(normalized)
        match = self.capability_map.resolve(text)
        complexity = self._complexity(normalized, len(match.capabilities))
        minimum, maximum = self._team_bounds(kind, complexity)
        reasons = (kind_reason, *tuple(f"capability:{item}" for item in match.matched_rules))
        confidence = min(
            0.98,
            0.55
            + (0.08 * len(match.matched_rules))
            + (0.08 if kind is not MissionKind.GENERAL else 0.0),
        )
        return MissionClassification(
            kind=kind,
            requirements=MissionRequirements(
                capabilities=match.capabilities,
                tools=match.tools,
                minimum_guardians=minimum,
                maximum_guardians=maximum,
            ),
            confidence=round(confidence, 2),
            reasons=reasons,
        )

    @staticmethod
    def _kind(normalized: str) -> tuple[MissionKind, str]:
        # Delivery intent has precedence over supporting work mentioned in the same mission.
        # Example: "Build an API with tests" is a feature mission with a testing capability,
        # not a test-only mission. Bug/fix intent remains the strongest signal.
        rules = (
            (MissionKind.BUG_FIX, ("bug", "fix", "broken", "error", "debug")),
            (MissionKind.REFACTOR, ("refactor", "cleanup", "restructure", "modernize")),
            (MissionKind.FEATURE, ("feature", "build", "create", "implement", "add")),
            (MissionKind.DEPLOY, ("deploy", "release", "railway", "production")),
            (MissionKind.RESEARCH, ("research", "compare", "investigate", "analyze")),
            (MissionKind.TEST, ("test", "verify", "qa", "regression")),
        )
        for kind, keywords in rules:
            for keyword in keywords:
                if keyword in normalized:
                    return kind, f"kind:{keyword}"
        return MissionKind.GENERAL, "kind:general"

    @staticmethod
    def _complexity(normalized: str, capability_count: int) -> int:
        score = capability_count
        score += sum(
            marker in normalized
            for marker in (
                "production",
                "multi",
                "migration",
                "security",
                "database",
                "distributed",
                "end-to-end",
            )
        )
        return score

    @staticmethod
    def _team_bounds(kind: MissionKind, complexity: int) -> tuple[int, int]:
        if kind is MissionKind.RESEARCH:
            return 2, min(12, max(4, complexity * 2))
        if kind in {MissionKind.DEPLOY, MissionKind.REFACTOR}:
            return 3, min(24, max(8, complexity * 3))
        if complexity >= 6:
            return 4, min(40, max(12, complexity * 4))
        if complexity >= 3:
            return 2, min(16, max(6, complexity * 3))
        return 1, 6
