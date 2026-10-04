"""Tests for the Guardian Company Runtime.

Covers the four-wing pipeline (50 brainstorm / up to 200 execute / up to 200
test / 200 revise), the immediate fast path from execution failures into
testing, complexity-sized wings, concurrent multi-mission operation, and the
shared company leveling rules (500 starting levels, level-ups on success and
failure, company-wide shared experience).
"""

import asyncio

import pytest

from nexus_os.portable.company import (
    COMPANY_BRAINSTORM_GUARDIANS,
    COMPANY_FAST_PATH_TESTERS,
    COMPANY_MAX_REVISION_CYCLES,
    COMPANY_REVISE_GUARDIANS,
    COMPANY_SHARED_XP_PER_LEVEL_UP,
    COMPANY_STARTING_LEVEL,
    COMPANY_TOTAL_LOGICAL_GUARDIANS,
    COMPANY_XP_PER_LEVEL,
    DEFECT_MARKER,
    CompanyGuardian,
    GuardianCompany,
    build_company_team,
    wing_size_for_complexity,
)
from nexus_os.swarm import MAX_SWARM_GUARDIANS


class FakeProvider:
    """Routes company prompts to wing-specific deterministic responses."""

    name = "fake"

    def __init__(self, defect_in_qc: bool = False, fail_execute: bool = False):
        self.calls: list[str] = []
        self.defect_in_qc = defect_in_qc
        self.fail_execute = fail_execute

    def generate(self, prompt: str):
        from nexus_os.portable.base import ProviderResult

        self.calls.append(prompt)
        if "lead Guardian of the Nexus company brainstorm wing" in prompt:
            return ProviderResult(text="candidate plan", provider=self.name, model=None)
        if "lead Guardian revising" in prompt:
            return ProviderResult(text="refined plan", provider=self.name, model=None)
        if "red-team review" in prompt:
            return ProviderResult(text="critique", provider=self.name, model=None)
        if "fast-error path" in prompt:
            return ProviderResult(text=f"{DEFECT_MARKER}: execution failure", provider=self.name, model=None)
        if "test & QC wing" in prompt:
            text = f"{DEFECT_MARKER}: broken output" if self.defect_in_qc else "verified, pass"
            return ProviderResult(text=text, provider=self.name, model=None)
        if "revision wing" in prompt:
            return ProviderResult(text="improved work product", provider=self.name, model=None)
        if "execution wing" in prompt:
            if self.fail_execute:
                raise RuntimeError("execute boom")
            return ProviderResult(text="work product", provider=self.name, model=None)
        if "brainstorm wing" in prompt:
            return ProviderResult(text="idea", provider=self.name, model=None)
        raise AssertionError(f"unexpected prompt: {prompt[:80]}")


def run(coro):
    return asyncio.run(coro)


def test_company_constants_define_whole_business_scale():
    assert COMPANY_BRAINSTORM_GUARDIANS == 50
    assert COMPANY_REVISE_GUARDIANS == 200
    assert COMPANY_STARTING_LEVEL == 500
    assert COMPANY_TOTAL_LOGICAL_GUARDIANS == 50 + 3 * MAX_SWARM_GUARDIANS == 650


def test_build_company_team_is_deterministic_and_bounded():
    team = build_company_team("execute", 7)
    assert len(team) == 7
    assert len({spec.guardian_id for spec in team}) == 7
    assert all(spec.guardian_id.startswith("execute-") for spec in team)
    with pytest.raises(ValueError):
        build_company_team("unknown-wing", 5)
    with pytest.raises(ValueError):
        build_company_team("execute", MAX_SWARM_GUARDIANS + 1)


def test_wing_size_scales_with_complexity_up_to_200():
    assert wing_size_for_complexity(0) == 20
    assert wing_size_for_complexity(2) == 20
    assert wing_size_for_complexity(3) == 50
    assert wing_size_for_complexity(5) == 100
    assert wing_size_for_complexity(6) == 100
    assert wing_size_for_complexity(7) == 200
    assert wing_size_for_complexity(99) == 200


def test_guardian_starts_at_level_500_and_levels_on_success_and_failure():
    company = GuardianCompany(max_parallel=2)
    team = build_company_team("execute", 3)
    company._enroll(team, "execute")

    guardian = team[0].guardian_id
    peer = team[1].guardian_id
    assert company.level(guardian) == 500

    company.record_outcome(guardian, True)
    assert company.level(guardian) == 501
    company.record_outcome(guardian, False)
    assert company.level(guardian) == 502

    # Every level-up grants shared XP to the whole company.
    assert company.roster[peer].xp == 2 * COMPANY_SHARED_XP_PER_LEVEL_UP


def test_shared_xp_settles_into_levels_silently():
    guardian = CompanyGuardian(guardian_id="g", wing="execute", role="qa")
    levels = guardian.add_xp(COMPANY_XP_PER_LEVEL * 3 + 50)
    assert levels == 3
    assert guardian.level == COMPANY_STARTING_LEVEL + 3
    assert guardian.xp == 50


def test_company_runs_four_wing_pipeline_and_levels_company_wide():
    async def scenario():
        company = GuardianCompany(max_parallel=3)
        provider = FakeProvider()
        call = lambda prompt: asyncio.to_thread(
            lambda: provider.generate(prompt).text
        )
        report = await company.run_mission(
            "Build a secure API", call, execute_size=4, test_size=3
        )

        assert report.plan == "refined plan"
        assert report.execute_guardians == 4
        assert report.test_guardians == 3
        assert report.revise_guardians == 200
        assert report.revision_cycles == 0
        assert report.confirmed_defects == 0
        assert "work product" in (report.final_output or "")

        summary = company.leveling_summary()
        # Diverge and critique passes share the same 50 brainstorm Guardian IDs;
        # the fast-path squad enrolls 5 testers, superset of the 3-strong QC wing.
        assert summary["guardians"] == COMPANY_BRAINSTORM_GUARDIANS + 4 + COMPANY_FAST_PATH_TESTERS
        # Guardians that worked leveled up; idle fast-path testers correctly stay at 500.
        assert summary["max_level"] >= COMPANY_STARTING_LEVEL + 1
        assert summary["min_level"] == COMPANY_STARTING_LEVEL
        assert summary["total_level_ups"] > 0
        assert summary["shared_xp_granted"] > 0

    run(scenario())


def test_execution_failure_takes_immediate_fast_path_to_testers():
    async def scenario():
        company = GuardianCompany(max_parallel=2)
        provider = FakeProvider(fail_execute=True)
        call = lambda prompt: asyncio.to_thread(
            lambda: provider.generate(prompt).text
        )
        report = await company.run_mission(
            "Ship the feature", call, execute_size=3, test_size=2
        )

        assert len(report.fast_path_findings) == 3
        marked = [f.output.startswith(DEFECT_MARKER) for f in report.fast_path_findings]
        assert all(marked)
        fast_path_calls = [p for p in provider.calls if "fast-error path" in p]
        assert len(fast_path_calls) == 3
        # Confirmed failures forced at least one revision cycle (bounded).
        assert 1 <= report.revision_cycles <= COMPANY_MAX_REVISION_CYCLES

    run(scenario())


def test_confirmed_defect_triggers_bounded_revise_and_retest():
    async def scenario():
        company = GuardianCompany(max_parallel=2)
        provider = FakeProvider(defect_in_qc=True)
        call = lambda prompt: asyncio.to_thread(
            lambda: provider.generate(prompt).text
        )
        report = await company.run_mission(
            "Fix the broken checkout flow", call, execute_size=2, test_size=2
        )

        assert report.confirmed_defects == 2
        assert report.revision_cycles == COMPANY_MAX_REVISION_CYCLES
        revise_calls = [p for p in provider.calls if "revision wing" in p]
        assert len(revise_calls) == COMPANY_REVISE_GUARDIANS * COMPANY_MAX_REVISION_CYCLES
        assert "improved work product" in (report.final_output or "")

    run(scenario())


def test_company_runs_multiple_missions_concurrently_with_shared_roster():
    async def scenario():
        company = GuardianCompany(max_parallel=2)
        provider = FakeProvider()
        call = lambda prompt: asyncio.to_thread(
            lambda: provider.generate(prompt).text
        )
        report = await company.run_company(
            ["Build an API", "Write the docs"], call
        )

        assert report.missions_run == 2
        assert [m.goal for m in report.missions] == ["Build an API", "Write the docs"]
        # Both missions drew from one shared company roster and XP pool.
        assert company.total_level_ups == report.total_level_ups
        assert len(company.roster) > max(
            COMPANY_BRAINSTORM_GUARDIANS, report.missions[0].execute_guardians
        )

    run(scenario())


def test_run_company_rejects_empty_goal_list():
    company = GuardianCompany(max_parallel=1)
    with pytest.raises(ValueError):
        run(company.run_company([], lambda prompt: asyncio.sleep(0, result="x")))
