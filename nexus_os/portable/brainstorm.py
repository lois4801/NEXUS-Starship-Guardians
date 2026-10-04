"""Divergent-convergent Guardian brainstorming pipeline.

Runs the company brainstorm wing of 50 logical Guardians through four phases:

1. **Diverge** — every Guardian independently generates ideas for the mission
   with an explicit mandate to exceed the requestor's stated expectations.
2. **Synthesize** — the lead Guardian merges the ideas into one candidate plan.
3. **Critique** — every Guardian red-teams the candidate plan in a second
   parallel pass (gaps, wrong assumptions, better alternatives).
4. **Refine** — the lead Guardian revises the plan against the critique.

Physical concurrency stays bounded through :class:`~nexus_os.swarm.SwarmCoordinator`,
so 50 logical Guardians never means 50 simultaneous processes. The external
provider CLI (for example OpenCode) remains responsible for its own login,
subscription, licensing, and provider terms; NEXUS never stores credentials.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from nexus_os.swarm import (
    DEFAULT_PARALLELISM,
    GuardianResult,
    SwarmCoordinator,
    compact_evidence,
)

BRAINSTORM_GUARDIAN_COUNT = 50
MAX_PLAN_CHARS = 12000


@dataclass(slots=True)
class BrainstormReport:
    goal: str
    requested_guardians: int
    active_guardians: int
    max_parallel: int
    divergent_results: list[GuardianResult] = field(default_factory=list)
    candidate_plan: str | None = None
    critique_results: list[GuardianResult] = field(default_factory=list)
    final_plan: str | None = None
    divergent_failures: int = 0
    critique_failures: int = 0

    @property
    def total_failures(self) -> int:
        return self.divergent_failures + self.critique_failures


def _divergent_prompt(spec, mission: str) -> str:
    return (
        "You are one Guardian in a Nexus Starship Guardians brainstorming swarm of "
        f"{BRAINSTORM_GUARDIAN_COUNT} logical Guardians.\n"
        f"Guardian ID: {spec.guardian_id}\nRole: {spec.role}\n"
        f"Mission: {mission}\n"
        "Assignment: from your role's perspective, generate the strongest concrete ideas and "
        "approaches for this mission.\n\n"
        "Brainstorm rules:\n"
        "- The requestor's stated goal is the floor, not the ceiling. Include at least one "
        "concrete addition that would genuinely exceed their expectations.\n"
        "- Be specific: name mechanisms, artifacts, and verification steps, not generic advice.\n"
        "- Stay inside your specialty; do not duplicate what other roles would contribute.\n"
        "- Flag risks, dependencies, and assumptions explicitly.\n\n"
        "Return concise, actionable work product for the lead Guardian."
    )


def _synthesis_prompt(mission: str, evidence: str) -> str:
    return (
        "You are the lead Guardian of a Nexus Starship Guardians brainstorming swarm. The "
        "Guardians below independently brainstormed the mission. Synthesize their work into ONE "
        "coherent candidate plan.\n\n"
        "Synthesis rules:\n"
        "- Merge complementary ideas; resolve conflicts explicitly; remove duplicates.\n"
        "- Preserve concrete details over vague statements.\n"
        "- The requestor's stated goal is the floor: keep the strongest exceed-expectation "
        "additions the Guardians proposed.\n"
        "- Finish with verification gates: what evidence would prove this plan works.\n\n"
        f"MISSION:\n{mission}\n\nGUARDIAN IDEAS:\n{evidence}"
    )


def _critique_prompt(spec, mission: str, candidate: str) -> str:
    if candidate:
        candidate_block = f"CANDIDATE PLAN:\n{candidate[:MAX_PLAN_CHARS]}"
    else:
        candidate_block = (
            "CANDIDATE PLAN:\n(no synthesis was produced — propose the strongest plan yourself "
            "from the mission, then critique your own proposal)"
        )
    return (
        "You are one Guardian in a Nexus Starship Guardians red-team review.\n"
        f"Guardian ID: {spec.guardian_id}\nRole: {spec.role}\n"
        f"Mission: {mission}\n\n"
        "A brainstorming swarm produced the candidate plan below. Attack it from your role's "
        "perspective:\n"
        "- Find gaps, wrong assumptions, missing risks, and missing steps.\n"
        "- Propose a cheaper or better alternative wherever one exists.\n"
        "- Name anything that would disappoint the requestor or violate their constraints.\n"
        "Do not praise the plan; only critique. Be specific and concise.\n\n"
        f"{candidate_block}"
    )


def _refinement_prompt(mission: str, candidate: str, critique: str) -> str:
    return (
        "You are the lead Guardian revising a candidate plan after red-team review.\n\n"
        "Revision rules:\n"
        "- Keep what the critique confirms; fix what it attacks; add what it finds missing.\n"
        "- Explicitly list the top changes and why.\n"
        "- Preserve the strongest exceed-expectation ideas.\n"
        "- Finish with verification gates.\n\n"
        f"MISSION:\n{mission}\n\n"
        f"CANDIDATE PLAN:\n{candidate[:MAX_PLAN_CHARS]}\n\n"
        f"RED-TEAM CRITIQUE:\n{critique}"
    )


async def run_brainstorm(
    provider,
    goal: str,
    requested_guardians: int = BRAINSTORM_GUARDIAN_COUNT,
    *,
    max_parallel: int = DEFAULT_PARALLELISM,
) -> BrainstormReport:
    """Run the four-phase brainstorm through a portable provider.

    ``provider`` is any object with ``generate(prompt) -> ProviderResult``
    (see :mod:`nexus_os.portable.base`), for example the Ollama, OpenCode, or
    command CLI providers.
    """
    coordinator = SwarmCoordinator(max_parallel=max_parallel)
    call = lambda prompt: asyncio.to_thread(provider.generate, prompt)

    async def diverge(spec, mission: str) -> str:
        result = await call(_divergent_prompt(spec, mission))
        return result.text

    async def synthesize(mission: str, results) -> str:
        evidence = compact_evidence(results)
        result = await call(_synthesis_prompt(mission, evidence))
        return result.text

    divergent = await coordinator.run(goal, requested_guardians, diverge, synthesize)
    candidate = (divergent.synthesis or "").strip()

    async def critique(spec, mission: str) -> str:
        result = await call(_critique_prompt(spec, mission, candidate))
        return result.text

    async def refine(mission: str, results) -> str:
        review = compact_evidence(results)
        result = await call(_refinement_prompt(mission, candidate, review))
        return result.text

    reviewed = await coordinator.run(goal, requested_guardians, critique, refine)

    return BrainstormReport(
        goal=goal,
        requested_guardians=divergent.requested_guardians,
        active_guardians=divergent.active_guardians,
        max_parallel=max_parallel,
        divergent_results=list(divergent.results),
        candidate_plan=candidate or None,
        critique_results=list(reviewed.results),
        final_plan=reviewed.synthesis or None,
        divergent_failures=sum(1 for item in divergent.results if not item.ok),
        critique_failures=sum(1 for item in reviewed.results if not item.ok),
    )
