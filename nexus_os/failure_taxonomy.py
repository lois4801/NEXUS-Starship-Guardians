from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class FailureCategory(StrEnum):
    CORRECTNESS = "correctness"
    COMPLETENESS = "completeness"
    SAFETY = "safety"
    TOOL_USE = "tool_use"
    REGRESSION = "regression"
    RELIABILITY = "reliability"
    COST = "cost"
    LATENCY = "latency"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class FailureSignal:
    category: FailureCategory
    reason: str
    severity: int = 1

    def __post_init__(self) -> None:
        if not 1 <= self.severity <= 5:
            raise ValueError("severity must be between 1 and 5")


def classify_failure(*, error: str = "", critique: str = "", regression: bool = False) -> FailureSignal:
    """Deterministically classify common failure evidence before model-based analysis."""
    text = f"{error} {critique}".lower()
    if regression:
        return FailureSignal(FailureCategory.REGRESSION, "previously passing behavior regressed", 5)
    if any(term in text for term in ("credential", "secret", "unsafe", "security", "tls")):
        return FailureSignal(FailureCategory.SAFETY, "safety/security evidence detected", 5)
    if any(term in text for term in ("timeout", "crash", "unavailable", "connection", "retry")):
        return FailureSignal(FailureCategory.RELIABILITY, "runtime reliability failure detected", 4)
    if any(term in text for term in ("tool denied", "permission", "not allowlisted", "approval")):
        return FailureSignal(FailureCategory.TOOL_USE, "tool policy or permission failure detected", 3)
    if any(term in text for term in ("missing", "incomplete", "omitted", "not implemented")):
        return FailureSignal(FailureCategory.COMPLETENESS, "required behavior appears incomplete", 3)
    if any(term in text for term in ("wrong", "incorrect", "assert", "expected", "failed")):
        return FailureSignal(FailureCategory.CORRECTNESS, "correctness evidence detected", 4)
    return FailureSignal(FailureCategory.UNKNOWN, "failure requires Guardian review", 2)
