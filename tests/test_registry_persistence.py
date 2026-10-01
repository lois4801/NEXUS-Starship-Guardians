from __future__ import annotations

from nexus_os.guardian_registry import GuardianProfile
from nexus_os.registry_persistence import SQLiteGuardianRegistry


def test_guardian_registry_persists_profiles_and_metrics(tmp_path):
    path = tmp_path / "guardian-registry.db"
    registry = SQLiteGuardianRegistry(path)
    registry.register(
        GuardianProfile(
            guardian_id="frontend-guardian",
            role="frontend",
            capabilities=frozenset({"react", "ui"}),
            allowed_tools=frozenset({"browser"}),
            preferred_models=("model-a",),
        )
    )
    registry.record_outcome(
        "frontend-guardian",
        success=True,
        score=9.0,
        cost=0.12,
        latency_seconds=2.5,
    )

    restarted = SQLiteGuardianRegistry(path)
    guardian = restarted.get("frontend-guardian")
    assert guardian.profile.capabilities == frozenset({"react", "ui"})
    assert guardian.profile.allowed_tools == frozenset({"browser"})
    assert guardian.metrics.attempts == 1
    assert guardian.metrics.successes == 1
    assert guardian.metrics.average_score == 9.0
    assert guardian.metrics.average_cost == 0.12
    assert guardian.metrics.average_latency_seconds == 2.5
