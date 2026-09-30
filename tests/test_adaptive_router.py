from nexus_os.adaptive_router import AdaptiveGuardianRouter, MissionRequirements
from nexus_os.guardian_registry import GuardianProfile, GuardianRegistry


def test_router_combines_guardians_for_capability_coverage():
    registry = GuardianRegistry()
    registry.register(
        GuardianProfile("frontend", "frontend", frozenset({"react", "ui"}))
    )
    registry.register(
        GuardianProfile("browser", "browser", frozenset({"browser-test"}))
    )
    router = AdaptiveGuardianRouter(registry)
    decision = router.route(
        MissionRequirements(
            capabilities=frozenset({"react", "browser-test"}),
            minimum_guardians=2,
            maximum_guardians=4,
        )
    )
    assert decision.sufficient
    assert {item.profile.guardian_id for item in decision.selected} == {"frontend", "browser"}


def test_router_reports_missing_capabilities():
    registry = GuardianRegistry()
    registry.register(GuardianProfile("api", "api", frozenset({"api"})))
    decision = AdaptiveGuardianRouter(registry).route(
        MissionRequirements(capabilities=frozenset({"database"}))
    )
    assert not decision.sufficient
    assert decision.missing_capabilities == frozenset({"database"})
