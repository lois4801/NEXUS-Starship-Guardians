from nexus_os.adaptive_intelligence import AdaptiveGuardianIntelligence
from nexus_os.adaptive_router import AdaptiveGuardianRouter, MissionRequirements
from nexus_os.guardian_registry import GuardianProfile, GuardianRegistry
from nexus_os.guardian_teams import elite_specialist_team


def test_elite_specialist_team_covers_requested_roles():
    names = {guardian.name for guardian in elite_specialist_team()}
    assert len(names) == 10
    assert "AI Architect Guardian" in names
    assert "Software Platform Engineer Guardian" in names
    assert "AI Developer Guardian" in names
    assert "Coder Specialist Guardian" in names
    assert "AI Engineer Guardian" in names
    assert "Debugger Specialist Guardian" in names
    assert "AI Scientist Guardian" in names
    assert "AI Cloud Specialist Guardian" in names
    assert "API Specialist Guardian" in names
    assert "AI Programmer Guardian" in names


def test_adaptive_learning_requires_verified_outcomes(tmp_path):
    intelligence = AdaptiveGuardianIntelligence(tmp_path / "adaptive.json")

    try:
        intelligence.record_verified_outcome(
            "coder-specialist",
            skills=frozenset({"coding"}),
            success=True,
            score=9.0,
            verified=False,
        )
    except ValueError as exc:
        assert "verified" in str(exc)
    else:
        raise AssertionError("unverified outcomes must not update adaptive intelligence")


def test_adaptive_learning_persists_and_builds_skill_evidence(tmp_path):
    path = tmp_path / "adaptive.json"
    intelligence = AdaptiveGuardianIntelligence(path)
    for score in (8.0, 8.5, 9.0, 9.5):
        intelligence.record_verified_outcome(
            "coder-specialist",
            skills=frozenset({"coding", "testing"}),
            success=True,
            score=score,
            benchmark_passed=True,
            verified=True,
        )

    state = intelligence.state("coder-specialist")
    assert state.verified_runs == 4
    assert state.learning_cycles == 4
    assert state.skills["coding"].adaptive_score > 8.0
    assert state.skills["coding"].trend > 0

    reloaded = AdaptiveGuardianIntelligence(path)
    assert reloaded.state("coder-specialist").verified_runs == 4
    assert reloaded.state("coder-specialist").skills["coding"].benchmark_passes == 4


def test_critical_regressions_reduce_adaptive_score(tmp_path):
    intelligence = AdaptiveGuardianIntelligence(tmp_path / "adaptive.json")
    intelligence.record_verified_outcome(
        "debugger-specialist",
        skills=frozenset({"debugging"}),
        success=True,
        score=9.0,
        benchmark_passed=True,
        verified=True,
    )
    before = intelligence.state("debugger-specialist").skills["debugging"].adaptive_score

    intelligence.record_verified_outcome(
        "debugger-specialist",
        skills=frozenset({"debugging"}),
        success=False,
        score=4.0,
        benchmark_passed=False,
        critical_regression=True,
        verified=True,
    )
    after = intelligence.state("debugger-specialist").skills["debugging"].adaptive_score
    assert after < before


def test_training_priorities_surface_unknown_and_weak_skills(tmp_path):
    intelligence = AdaptiveGuardianIntelligence(tmp_path / "adaptive.json")
    intelligence.record_verified_outcome(
        "api-specialist",
        skills=frozenset({"api-design"}),
        success=False,
        score=3.5,
        benchmark_passed=False,
        verified=True,
    )

    priorities = intelligence.training_priorities("api-specialist")
    assert priorities
    assert any(item.skill == "api-design" for item in priorities)
    api_priority = next(item for item in priorities if item.skill == "api-design")
    assert api_priority.score < 7.5


def test_router_uses_bounded_adaptive_evidence_bonus(tmp_path):
    registry = GuardianRegistry()
    registry.register(
        GuardianProfile(
            guardian_id="coder-specialist",
            role="Coder Specialist Guardian",
            capabilities=frozenset({"coding"}),
        )
    )
    registry.register(
        GuardianProfile(
            guardian_id="ai-programmer",
            role="AI Programmer Guardian",
            capabilities=frozenset({"coding"}),
        )
    )
    intelligence = AdaptiveGuardianIntelligence(tmp_path / "adaptive.json")
    for _ in range(4):
        intelligence.record_verified_outcome(
            "coder-specialist",
            skills=frozenset({"coding"}),
            success=True,
            score=9.5,
            benchmark_passed=True,
            verified=True,
        )
        intelligence.record_verified_outcome(
            "ai-programmer",
            skills=frozenset({"coding"}),
            success=False,
            score=4.0,
            benchmark_passed=False,
            verified=True,
        )

    decision = AdaptiveGuardianRouter(registry, intelligence).route(
        MissionRequirements(capabilities=frozenset({"coding"}), maximum_guardians=1)
    )
    assert decision.sufficient
    assert decision.selected[0].profile.guardian_id == "coder-specialist"
