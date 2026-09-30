from nexus_os.guardian_registry import GuardianProfile, GuardianRegistry


def test_registry_selects_capable_guardian_and_learns_metrics():
    registry = GuardianRegistry()
    registry.register(
        GuardianProfile(
            guardian_id="frontend-01",
            role="frontend",
            capabilities=frozenset({"react", "ui"}),
            allowed_tools=frozenset({"browser"}),
        )
    )
    registry.register(
        GuardianProfile(
            guardian_id="backend-01",
            role="backend",
            capabilities=frozenset({"api"}),
        )
    )
    registry.record_outcome("frontend-01", success=True, score=9.5, cost=0.1, latency_seconds=2)
    selected = registry.select(
        required_capabilities=frozenset({"react"}),
        required_tools=frozenset({"browser"}),
    )
    assert [item.profile.guardian_id for item in selected] == ["frontend-01"]
    assert selected[0].metrics.success_rate == 1.0
