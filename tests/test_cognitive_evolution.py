import pytest

from nexus_os.adaptive_intelligence import AdaptiveGuardianIntelligence
from nexus_os.cognitive_evolution import CognitiveEvolutionEngine


def _engines(tmp_path):
    adaptive = AdaptiveGuardianIntelligence(tmp_path / "adaptive.json")
    cognitive = CognitiveEvolutionEngine(tmp_path / "cognitive.json", adaptive)
    return adaptive, cognitive


def test_cognitive_evolution_requires_verified_evidence(tmp_path):
    _, cognitive = _engines(tmp_path)
    with pytest.raises(ValueError, match="verified evidence"):
        cognitive.record_verified_episode(
            "api-specialist",
            skills=frozenset({"integration"}),
            success=True,
            score=9.0,
            summary="Worked",
            verified=False,
        )


def test_verified_lesson_transfers_without_transferring_skill_score(tmp_path):
    adaptive, cognitive = _engines(tmp_path)
    cognitive.record_verified_episode(
        "api-specialist",
        skills=frozenset({"integration", "testing"}),
        success=True,
        score=9.5,
        summary="Contract-first validation prevented an integration regression.",
        strategy="contract-first",
        predicted_confidence=0.85,
        verified=True,
    )

    lessons = cognitive.shared_lessons(
        "ai-developer",
        skills=frozenset({"integration"}),
    )
    assert lessons
    assert lessons[0].source_guardian == "api-specialist"
    assert adaptive.state("ai-developer").verified_runs == 0
    assert "integration" not in adaptive.state("ai-developer").skills


def test_failure_cluster_and_counterfactual_plan(tmp_path):
    _, cognitive = _engines(tmp_path)
    cognitive.record_verified_episode(
        "debugger-specialist",
        skills=frozenset({"debugging", "testing"}),
        success=False,
        score=2.0,
        summary="Regression reproduced after the original repair.",
        strategy="direct-repair",
        failure_signature="test-regression",
        predicted_confidence=0.9,
        verified=True,
    )
    cluster = cognitive.failure_clusters()[0]
    assert cluster.signature == "test-regression"
    assert cluster.count == 1

    plan = cognitive.counterfactual_plan(
        "debugger-specialist",
        skills=frozenset({"debugging", "testing"}),
        failure_signature="test-regression",
        original_strategy="direct-repair",
    )
    assert "minimal-reproduction" in plan.alternative_strategies
    assert "hypothesis-first-debugging" in plan.alternative_strategies


def test_curriculum_combines_personal_gaps_and_transferable_lessons(tmp_path):
    adaptive, cognitive = _engines(tmp_path)
    cognitive.record_verified_episode(
        "api-specialist",
        skills=frozenset({"testing"}),
        success=True,
        score=9.0,
        summary="Replay contract tests before accepting an API repair.",
        verified=True,
    )
    adaptive.record_verified_outcome(
        "coder-specialist",
        skills=frozenset({"testing"}),
        success=False,
        score=3.0,
        benchmark_passed=False,
        verified=True,
    )
    curriculum = cognitive.curriculum("coder-specialist", limit=10)
    testing = next(item for item in curriculum if item.skill == "testing")
    assert testing.transferable_lessons
    assert any("Replay" in exercise for exercise in testing.exercises)


def test_confidence_calibration_penalizes_overconfident_failure(tmp_path):
    _, cognitive = _engines(tmp_path)
    before = cognitive.state("ai-architect").calibration.reliability
    cognitive.record_verified_episode(
        "ai-architect",
        skills=frozenset({"architecture"}),
        success=False,
        score=2.0,
        summary="Architecture failed the migration rehearsal.",
        failure_signature="architecture-migration-failure",
        predicted_confidence=0.98,
        verified=True,
    )
    after = cognitive.state("ai-architect").calibration.reliability
    assert after < before
    assert -0.25 <= cognitive.routing_bonus("ai-architect", frozenset({"architecture"})) <= 0.35


def test_cognitive_state_persists(tmp_path):
    adaptive = AdaptiveGuardianIntelligence(tmp_path / "adaptive.json")
    path = tmp_path / "cognitive.json"
    cognitive = CognitiveEvolutionEngine(path, adaptive)
    cognitive.record_verified_episode(
        "ai-scientist",
        skills=frozenset({"evaluation"}),
        success=True,
        score=9.0,
        summary="Controlled evaluation isolated the causal variable.",
        verified=True,
    )

    reloaded = CognitiveEvolutionEngine(path, adaptive)
    assert reloaded.state("ai-scientist").verified_episodes == 1
    assert reloaded.lessons()[0].summary.startswith("Controlled evaluation")
