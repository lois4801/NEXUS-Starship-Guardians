from nexus_os.promotion_gate import (
    EvaluationSummary,
    PromotionPolicy,
    decide_promotion,
)


def test_promotion_accepts_better_candidate():
    baseline = EvaluationSummary("base", 9, 10, 8.0, cost=1.0, latency_seconds=10.0)
    candidate = EvaluationSummary("candidate", 10, 10, 8.7, cost=1.05, latency_seconds=10.5)
    decision = decide_promotion(
        baseline,
        candidate,
        PromotionPolicy(minimum_pass_rate=0.9, minimum_score_delta=0.2),
    )
    assert decision.promote
    assert decision.reasons == []


def test_promotion_blocks_critical_regression():
    baseline = EvaluationSummary("base", 10, 10, 9.0, critical_failures=0)
    candidate = EvaluationSummary("candidate", 10, 10, 9.5, critical_failures=1)
    decision = decide_promotion(baseline, candidate)
    assert not decision.promote
    assert "critical regression" in " ".join(decision.reasons)
