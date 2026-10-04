"""Tests for the v0.9.0 Autonomous Operations Wing specialist expansion.

The ten new specialists were acquired from the Guardian fleet owner's other
repositories (LucioDigital-Platform Dev Agent phases, Lucio-AI-Platform
assistant squad, Multi-Agent AI System patterns) and must be deployable
autonomously through the same surfaces as the original ten specialists.
"""

from nexus_os.adaptive_intelligence import SPECIALIST_INTELLIGENCE_PROFILES
from nexus_os.guardian_teams import autonomous_operations_team, elite_specialist_team
from nexus_os.mission_runtime import build_default_guardian_registry

AUTONOMOUS_WING_IDS = frozenset(
    {
        "planner-strategist",
        "verification-qa-specialist",
        "reviewer-specialist",
        "deployment-release-specialist",
        "evidence-research-specialist",
        "content-seo-strategist",
        "design-experience-specialist",
        "budget-cost-controller",
        "data-analyst-specialist",
        "evaluation-judge-specialist",
    }
)


def test_specialist_roster_doubles_to_twenty_with_unique_ids():
    ids = [profile.guardian_id for profile in SPECIALIST_INTELLIGENCE_PROFILES]
    assert len(ids) == 20
    assert len(set(ids)) == 20
    assert AUTONOMOUS_WING_IDS <= set(ids)


def test_autonomous_operations_team_lists_all_new_specialists():
    team = autonomous_operations_team()
    names = {guardian.name for guardian in team}
    assert len(team) == 10
    assert len(names) == 10
    assert all(guardian.division == "autonomous-operations" for guardian in team)
    expected_names = {
        profile.role for profile in SPECIALIST_INTELLIGENCE_PROFILES
    } - {guardian.name for guardian in elite_specialist_team()}
    assert names == expected_names


def test_new_specialists_do_not_duplicate_elite_wing_roles():
    elite_names = {guardian.name for guardian in elite_specialist_team()}
    wing_names = {guardian.name for guardian in autonomous_operations_team()}
    assert not elite_names & wing_names


def test_default_registry_registers_every_specialist_with_bounded_tools():
    registry = build_default_guardian_registry()
    registered = {item.profile.guardian_id: item.profile for item in registry.all()}
    for profile in SPECIALIST_INTELLIGENCE_PROFILES:
        assert profile.guardian_id in registered
    # The original specialists keep their historical tool grants.
    assert "model" in registered["ai-architect"].allowed_tools
    assert "test" in registered["debugger-specialist"].allowed_tools
    # New specialists receive only capabilities-honest tool grants.
    assert "database" in registered["data-analyst-specialist"].allowed_tools
    assert "browser" in registered["verification-qa-specialist"].allowed_tools
    assert "test" in registered["verification-qa-specialist"].allowed_tools
    assert "terminal" in registered["deployment-release-specialist"].allowed_tools
    assert "test" in registered["evaluation-judge-specialist"].allowed_tools
    # Review and planning authority stays approval-shaped, not execution-shaped:
    # the reviewer must not hold deployment or database tools.
    reviewer_tools = registered["reviewer-specialist"].allowed_tools
    assert "terminal" not in reviewer_tools
    assert "database" not in reviewer_tools
