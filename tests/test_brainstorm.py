import asyncio

from nexus_os.portable.base import ProviderResult
from nexus_os.portable.brainstorm import run_brainstorm
from nexus_os.swarm import MAX_SWARM_GUARDIANS


class FakeProvider:
    """Routes prompts to phase-specific responses and records call order."""

    name = "fake"

    def __init__(self, fail_on_diverge: bool = False):
        self.calls: list[str] = []
        self.fail_on_diverge = fail_on_diverge

    def generate(self, prompt: str) -> ProviderResult:
        self.calls.append(prompt)
        if "Brainstorm rules" in prompt:
            if self.fail_on_diverge:
                raise RuntimeError("diverge boom")
            return ProviderResult(text="idea", provider=self.name, model=None)
        if "lead Guardian revising" in prompt:
            return ProviderResult(text="final plan", provider=self.name, model=None)
        if "Attack it from your role" in prompt:
            return ProviderResult(text="critique", provider=self.name, model=None)
        if "Synthesize their work" in prompt:
            return ProviderResult(text="candidate plan", provider=self.name, model=None)
        raise AssertionError(f"unexpected prompt: {prompt[:80]}")


def test_brainstorm_runs_four_phases():
    async def scenario():
        provider = FakeProvider()
        report = await run_brainstorm(provider, "ship it", 8, max_parallel=3)

        assert report.requested_guardians == 8
        assert report.active_guardians == 8
        assert len(report.divergent_results) == 8
        assert len(report.critique_results) == 8
        assert report.candidate_plan == "candidate plan"
        assert report.final_plan == "final plan"
        assert report.divergent_failures == 0
        assert report.critique_failures == 0
        assert report.total_failures == 0

    asyncio.run(scenario())


def test_brainstorm_default_is_200_guardians():
    async def scenario():
        provider = FakeProvider()
        report = await run_brainstorm(provider, "big mission", max_parallel=4)

        assert report.requested_guardians == MAX_SWARM_GUARDIANS
        assert report.active_guardians == MAX_SWARM_GUARDIANS
        assert len(report.divergent_results) == MAX_SWARM_GUARDIANS
        assert len(report.critique_results) == MAX_SWARM_GUARDIANS

    asyncio.run(scenario())


def test_brainstorm_mandate_and_phase_order():
    async def scenario():
        provider = FakeProvider()
        await run_brainstorm(provider, "mission", 6, max_parallel=2)

        divergent = [i for i, p in enumerate(provider.calls) if "Brainstorm rules" in p]
        synthesis = [i for i, p in enumerate(provider.calls) if "Synthesize their work" in p]
        critique = [i for i, p in enumerate(provider.calls) if "Attack it from your role" in p]
        refinement = [i for i, p in enumerate(provider.calls) if "lead Guardian revising" in p]

        assert len(divergent) == 6
        assert len(critique) == 6
        assert synthesis and refinement
        assert max(divergent) < min(synthesis)
        assert max(synthesis) < min(critique)
        assert max(critique) < min(refinement)
        assert all("floor, not the ceiling" in provider.calls[i] for i in divergent)
        assert all("candidate plan" in provider.calls[i].lower() for i in critique)
        assert "candidate" in provider.calls[refinement[0]].lower()

    asyncio.run(scenario())


def test_brainstorm_isolates_divergent_failures():
    async def scenario():
        provider = FakeProvider(fail_on_diverge=True)
        report = await run_brainstorm(provider, "mission", 5, max_parallel=2)

        assert report.divergent_failures == 5
        assert report.critique_failures == 0
        # The lead still attempts a synthesis from empty evidence.
        assert report.candidate_plan == "candidate plan"
        # The red team still runs and can overrule it.
        assert report.final_plan == "final plan"
        assert len(report.critique_results) == 5

    asyncio.run(scenario())
