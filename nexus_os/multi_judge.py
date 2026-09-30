from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from statistics import mean


class JudgeKind(StrEnum):
    DETERMINISTIC = "deterministic"
    GUARDIAN = "guardian"
    ALTERNATE_MODEL = "alternate_model"
    EVIDENCE = "evidence"


@dataclass(frozen=True, slots=True)
class JudgeResult:
    judge_id: str
    kind: JudgeKind
    score: float
    passed: bool
    rationale: str = ""
    critical: bool = False

    def __post_init__(self) -> None:
        if not 0 <= self.score <= 10:
            raise ValueError("judge score must be between 0 and 10")


@dataclass(slots=True)
class MultiJudgeReport:
    results: list[JudgeResult] = field(default_factory=list)
    required_kinds: frozenset[JudgeKind] = frozenset(
        {JudgeKind.DETERMINISTIC, JudgeKind.EVIDENCE}
    )

    @property
    def average_score(self) -> float:
        return mean(item.score for item in self.results) if self.results else 0.0

    @property
    def critical_failures(self) -> int:
        return sum(1 for item in self.results if item.critical and not item.passed)

    @property
    def passed(self) -> bool:
        present = {item.kind for item in self.results}
        if not self.required_kinds.issubset(present):
            return False
        if any(item.critical and not item.passed for item in self.results):
            return False
        return all(item.passed for item in self.results if item.kind in self.required_kinds)

    def add(self, result: JudgeResult) -> None:
        self.results.append(result)
