from __future__ import annotations

import pytest

from nexus_os.capability_map import CapabilityMap
from nexus_os.mission_classifier import MissionClassifier, MissionKind


def test_capability_map_extracts_explicit_capabilities_and_tools():
    match = CapabilityMap().resolve(
        "Build a React frontend with FastAPI backend, PostgreSQL schema, tests, and Docker deployment"
    )
    assert {"frontend", "backend", "database", "testing", "devops"}.issubset(match.capabilities)
    assert {"browser", "api", "database", "test", "terminal"}.issubset(match.tools)


def test_capability_map_falls_back_without_inventing_specific_domain():
    match = CapabilityMap().resolve("Improve this workflow")
    assert match.capabilities == frozenset({"general-engineering"})
    assert match.tools == frozenset()


def test_mission_classifier_builds_bounded_requirements():
    result = MissionClassifier().classify(
        "Build a production FastAPI API with PostgreSQL, security tests, Docker and telemetry"
    )
    assert result.kind == MissionKind.FEATURE
    assert result.requirements.maximum_guardians <= 200
    assert result.requirements.minimum_guardians >= 1
    assert "backend" in result.requirements.capabilities
    assert "database" in result.requirements.capabilities
    assert "security" in result.requirements.capabilities
    assert "observability" in result.requirements.capabilities
    assert result.confidence > 0.5


def test_mission_classifier_detects_bug_fix_before_feature_words():
    result = MissionClassifier().classify("Fix a broken React component and add a regression test")
    assert result.kind == MissionKind.BUG_FIX


def test_mission_classifier_rejects_empty_mission():
    with pytest.raises(ValueError, match="mission cannot be empty"):
        MissionClassifier().classify("   ")
