"""Tests for the v0.9.0 specialist expansions.

The Autonomous Operations Wing (ten specialists) was acquired from the
Guardian fleet owner's other repositories (LucioDigital-Platform Dev Agent
phases, Lucio-AI-Platform assistant squad, Multi-Agent AI System patterns).

The Agency Services Wing (twelve specialists) was selected by gap analysis
against the agency-agents open catalog (msitarzewski/agency-agents, MIT
License); only skill concepts were taken and all profiles are original NEXUS
definitions. Both wings must be deployable autonomously through the same
surfaces as the original ten specialists.
"""

from nexus_os.adaptive_intelligence import SPECIALIST_INTELLIGENCE_PROFILES
from nexus_os.guardian_teams import (
    agency_services_team,
    autonomous_operations_team,
    elite_specialist_team,
)
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

AGENCY_WING_IDS = frozenset(
    {
        "gis-spatial-analyst",
        "sales-pipeline-strategist",
        "game-design-specialist",
        "xr-spatial-engineer",
        "paid-media-strategist",
        "financial-analysis-specialist",
        "healthcare-evidence-specialist",
        "blockchain-engineer",
        "embedded-iot-engineer",
        "knowledge-search-engineer",
        "legal-compliance-specialist",
        "pmo-operations-specialist",
    }
)


def test_specialist_roster_grows_to_thirty_two_with_unique_ids():
    ids = [profile.guardian_id for profile in SPECIALIST_INTELLIGENCE_PROFILES]
    assert len(ids) == 32
    assert len(set(ids)) == 32
    assert AUTONOMOUS_WING_IDS <= set(ids)
    assert AGENCY_WING_IDS <= set(ids)


def test_autonomous_operations_team_lists_all_new_specialists():
    team = autonomous_operations_team()
    names = {guardian.name for guardian in team}
    assert len(team) == 10
    assert len(names) == 10
    assert all(guardian.division == "autonomous-operations" for guardian in team)
    expected_names = {profile.role for profile in SPECIALIST_INTELLIGENCE_PROFILES} - {
        guardian.name for guardian in elite_specialist_team()
    } - {guardian.name for guardian in agency_services_team()}
    assert names == expected_names


def test_new_specialists_do_not_duplicate_elite_wing_roles():
    elite_names = {guardian.name for guardian in elite_specialist_team()}
    wing_names = {guardian.name for guardian in autonomous_operations_team()}
    assert not elite_names & wing_names


def test_agency_services_team_lists_all_new_specialists():
    team = agency_services_team()
    names = {guardian.name for guardian in team}
    assert len(team) == 12
    assert len(names) == 12
    assert all(guardian.division == "agency-services" for guardian in team)
    covered = {guardian.name for guardian in elite_specialist_team()} | {
        guardian.name for guardian in autonomous_operations_team()
    }
    expected_names = {profile.role for profile in SPECIALIST_INTELLIGENCE_PROFILES} - covered
    assert names == expected_names


def test_agency_specialists_do_not_duplicate_existing_wing_roles():
    existing_names = {guardian.name for guardian in elite_specialist_team()} | {
        guardian.name for guardian in autonomous_operations_team()
    }
    agency_names = {guardian.name for guardian in agency_services_team()}
    assert not existing_names & agency_names


def test_agency_specialists_receive_only_capabilities_honest_tool_grants():
    registry = build_default_guardian_registry()
    registered = {item.profile.guardian_id: item.profile for item in registry.all()}
    for guardian_id in AGENCY_WING_IDS:
        assert guardian_id in registered
    # Database work is honestly granted to spatial and financial analysts.
    assert "database" in registered["gis-spatial-analyst"].allowed_tools
    assert "database" in registered["financial-analysis-specialist"].allowed_tools
    # RAG and retrieval work reaches the model and database gateways.
    assert "model" in registered["knowledge-search-engineer"].allowed_tools
    assert "database" in registered["knowledge-search-engineer"].allowed_tools
    # Embedded/IoT spans integration, API, and terminal surfaces.
    assert "terminal" in registered["embedded-iot-engineer"].allowed_tools
    assert "integration" in registered["embedded-iot-engineer"].allowed_tools
    # Blockchain engineering gets API and security surfaces.
    assert "api" in registered["blockchain-engineer"].allowed_tools
    assert "security" in registered["blockchain-engineer"].allowed_tools
    # Healthcare evidence review is research-only: no tool grants beyond reads.
    assert not registered["healthcare-evidence-specialist"].allowed_tools
    # Legal review holds security but never execution surfaces.
    legal_tools = registered["legal-compliance-specialist"].allowed_tools
    assert "terminal" not in legal_tools
    assert "api" not in legal_tools


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
