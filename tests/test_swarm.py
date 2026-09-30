import asyncio

import pytest

from nexus_os.swarm import (
    MAX_SWARM_GUARDIANS,
    GuardianResult,
    SwarmCoordinator,
    build_team,
    compact_evidence,
)


def test_build_team_supports_200_guardians():
    team = build_team("build the app", MAX_SWARM_GUARDIANS)
    assert len(team) == 200
    assert len({guardian.guardian_id for guardian in team}) == 200


def test_build_team_rejects_invalid_size():
    with pytest.raises(ValueError):
        build_team("x", 0)
    with pytest.raises(ValueError):
        build_team("x", 201)


def test_swarm_runs_all_guardians_and_synthesizes():
    async def scenario():
        coordinator = SwarmCoordinator(max_parallel=4)

        async def worker(spec, goal):
            await asyncio.sleep(0)
            return f"{spec.role}:{goal}"

        async def synth(goal, results):
            return f"{goal}:{len(results)}"

        report = await coordinator.run("ship", 25, worker, synth)
        assert report.active_guardians == 25
        assert len(report.results) == 25
        assert report.synthesis == "ship:25"
        assert all(item.ok for item in report.results)

    asyncio.run(scenario())


def test_swarm_isolates_guardian_failure():
    async def scenario():
        coordinator = SwarmCoordinator(max_parallel=3)

        async def worker(spec, goal):
            if spec.guardian_id.endswith("-01") and spec.role == "backend":
                raise RuntimeError("boom")
            return goal

        report = await coordinator.run("verify", 8, worker)
        assert len(report.results) == 8
        assert sum(1 for item in report.results if not item.ok) == 1

    asyncio.run(scenario())


def test_compact_evidence_omits_failures_and_bounds_payload():
    results = [
        GuardianResult("a", "qa", "useful"),
        GuardianResult("b", "debug", "", ok=False, error="failed"),
        GuardianResult("c", "security", "important"),
    ]
    text = compact_evidence(results, max_chars=1000)
    assert "useful" in text
    assert "important" in text
    assert "failed" not in text
