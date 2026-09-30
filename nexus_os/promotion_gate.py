from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class EvaluationSummary:
    name: str
    passed: int
    total: int
    average_score: float
    critical_failures: int = 0
    cost: float = 0.0
    latency_seconds: float = 0.0

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total else 0.0


@dataclass(frozen=True, slots=True)
class PromotionPolicy:
    minimum_pass_rate: float = 0.90
    minimum_score_delta: float = 0.0
    allow_critical_regression: bool = False
    maximum_cost_ratio: float | None = None
    maximum_latency_ratio: float | None = None


@dataclass(slots=True)
class PromotionDecision:
    promote: bool
    reasons: list[str] = field(default_factory=list)


def decide_promotion(
    baseline: EvaluationSummary,
    candidate: EvaluationSummary,
    policy: PromotionPolicy | None = None,
) -> PromotionDecision:
    policy = policy or PromotionPolicy()
    reasons: list[str] = []

    if candidate.total == 0:
        reasons.append("candidate has no evaluation cases")
    if candidate.pass_rate < policy.minimum_pass_rate:
        reasons.append("candidate pass rate is below the configured minimum")
    if candidate.pass_rate < baseline.pass_rate:
        reasons.append("candidate pass rate regressed versus baseline")
    if candidate.average_score < baseline.average_score + policy.minimum_score_delta:
        reasons.append("candidate score did not meet the required baseline delta")
    if not policy.allow_critical_regression and candidate.critical_failures > baseline.critical_failures:
        reasons.append("candidate introduced a critical regression")

    if (
        policy.maximum_cost_ratio is not None
        and baseline.cost > 0
        and candidate.cost / baseline.cost > policy.maximum_cost_ratio
    ):
        reasons.append("candidate cost exceeds the configured ratio")
    if (
        policy.maximum_latency_ratio is not None
        and baseline.latency_seconds > 0
        and candidate.latency_seconds / baseline.latency_seconds > policy.maximum_latency_ratio
    ):
        reasons.append("candidate latency exceeds the configured ratio")

    return PromotionDecision(promote=not reasons, reasons=reasons)
