"""Guardian Company Runtime — a whole-business swarm operating model.

The company runs every mission through four wings that work together like a
company running the whole business:

1. **Brainstorm wing (50 Guardians)** — divergent-convergent planning: every
   Guardian proposes ideas with an exceed-expectations mandate, a lead
   Guardian synthesizes, the full wing red-teams the candidate, and the lead
   refines it into the execution plan.
2. **Execution wing (up to 200 Guardians)** — sized by mission complexity.
   Guardians implement the plan in parallel.
3. **Test & QC wing (up to 200 Guardians)** — sized by mission complexity.
   Guardians verify execution output. Any execution failure is routed to the
   testers **immediately** through a fast-path queue instead of waiting for
   the phase to finish.
4. **Revision wing (200 Guardians)** — when QC confirms defects, the whole
   wing re-implements a revised plan, which is re-tested in a bounded loop.

The company also runs **multiple missions concurrently** — each mission is an
independent pipeline, but every Guardian belongs to one company with a shared
experience pool.

**Leveling.** Every company Guardian starts at level 500: the accumulated
fleet-experience baseline imported at company founding (it grants no skill
evidence and no permissions — see governance notes below). After that,
Guardians level up only from verified outcomes: every recorded success grants
+1 level, every recorded failure also grants +1 level (failures teach), and
**whenever any Guardian levels up, every Guardian in the company receives
shared experience points**; 100 XP settles into one additional level. Leveling
never grants permissions: authorization stays in the Controlled Tool Gateway.

Governance notes:

- Level-ups and shared XP are bookkeeping over *verified* swarm outcomes
  (``GuardianResult.ok`` from real provider calls); they are not fabricated
  skill evidence and never modify ``AdaptiveGuardianIntelligence`` scores,
  which still require objective test/api/browser/security verification.
- The revise→re-test loop is bounded by ``COMPANY_MAX_REVISION_CYCLES`` so a
  mission can never spin unbounded.
- Physical concurrency stays bounded through a semaphore; 650 logical
  Guardians never means 650 simultaneous processes. NEXUS never stores
  provider credentials.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from functools import partial

from nexus_os.mission_classifier import MissionClassifier
from nexus_os.swarm import (
    DEFAULT_PARALLELISM,
    MAX_SWARM_GUARDIANS,
    ROLE_FAMILIES,
    GuardianResult,
    GuardianSpec,
    compact_evidence,
)

COMPANY_BRAINSTORM_GUARDIANS = 50
COMPANY_REVISE_GUARDIANS = 200
COMPANY_STARTING_LEVEL = 500
COMPANY_XP_PER_LEVEL = 100
COMPANY_SHARED_XP_PER_LEVEL_UP = 10
COMPANY_MAX_REVISION_CYCLES = 3
COMPANY_FAST_PATH_TESTERS = 5
COMPANY_TOTAL_LOGICAL_GUARDIANS = (
    COMPANY_BRAINSTORM_GUARDIANS + 3 * MAX_SWARM_GUARDIANS
)

WING_BRAINSTORM = "brainstorm"
WING_EXECUTE = "execute"
WING_TEST = "test"
WING_REVISE = "revise"

COMPANY_WINGS = (WING_BRAINSTORM, WING_EXECUTE, WING_TEST, WING_REVISE)

_COMPLEXITY_MARKERS = (
    "production",
    "multi",
    "migration",
    "security",
    "database",
    "distributed",
    "end-to-end",
)

DEFECT_MARKER = "DEFECT FOUND"


@dataclass(slots=True)
class CompanyGuardian:
    """A logical company Guardian with game-like progression bookkeeping."""

    guardian_id: str
    wing: str
    role: str
    level: int = COMPANY_STARTING_LEVEL
    xp: int = 0
    successes: int = 0
    failures: int = 0

    def add_xp(self, amount: int) -> int:
        """Add XP and return the number of levels settled from it."""
        if amount < 0:
            raise ValueError("xp amount must be non-negative")
        self.xp += amount
        levels, self.xp = divmod(self.xp, COMPANY_XP_PER_LEVEL)
        self.level += levels
        return levels


@dataclass(slots=True)
class CompanyMissionReport:
    goal: str
    plan: str | None
    complexity_score: int
    execute_guardians: int
    test_guardians: int
    revise_guardians: int
    revision_cycles: int = 0
    execute_results: list[GuardianResult] = field(default_factory=list)
    qc_results: list[GuardianResult] = field(default_factory=list)
    fast_path_findings: list[GuardianResult] = field(default_factory=list)
    final_output: str | None = None

    @property
    def confirmed_defects(self) -> int:
        fast_path = len(self.fast_path_findings)
        flagged = sum(1 for item in self.qc_results if DEFECT_MARKER in item.output)
        return fast_path + flagged


@dataclass(slots=True)
class CompanyReport:
    missions: list[CompanyMissionReport] = field(default_factory=list)
    total_level_ups: int = 0
    shared_xp_granted: int = 0

    @property
    def missions_run(self) -> int:
        return len(self.missions)


def build_company_team(wing: str, size: int) -> list[GuardianSpec]:
    """Build a deterministic wing roster with diverse role families."""
    if wing not in COMPANY_WINGS:
        raise ValueError(f"unknown company wing: {wing}")
    if not 1 <= size <= MAX_SWARM_GUARDIANS:
        raise ValueError(f"wing size must be between 1 and {MAX_SWARM_GUARDIANS}")
    team: list[GuardianSpec] = []
    for index in range(size):
        role = ROLE_FAMILIES[index % len(ROLE_FAMILIES)]
        replica = index // len(ROLE_FAMILIES) + 1
        team.append(
            GuardianSpec(
                guardian_id=f"{wing}-{role}-{replica:02d}",
                role=role,
                objective=_wing_objective(wing),
            )
        )
    return team


def _wing_objective(wing: str) -> str:
    return {
        WING_BRAINSTORM: (
            "Brainstorm the mission from your role's perspective; the stated goal is the "
            "floor, not the ceiling. Produce concrete, verifiable ideas."
        ),
        WING_EXECUTE: (
            "Implement your assigned part of the approved plan. Return the produced work "
            "product, not a description of it."
        ),
        WING_TEST: (
            "Independently verify the work product from your role's perspective. If you "
            f"find a real defect, start your reply with '{DEFECT_MARKER}:' and describe it."
        ),
        WING_REVISE: (
            "Re-implement and improve the work product against the confirmed QC findings. "
            "Return the improved work product."
        ),
    }[wing]


def mission_complexity(goal: str, capability_count: int) -> int:
    """Score mission complexity the same way the mission classifier does."""
    normalized = goal.strip().casefold()
    score = capability_count
    score += sum(marker in normalized for marker in _COMPLEXITY_MARKERS)
    return score


def wing_size_for_complexity(complexity: int) -> int:
    """Map a complexity score to an execution/test wing size (bounded by 200)."""
    if complexity <= 2:
        return 20
    if complexity <= 4:
        return 50
    if complexity <= 6:
        return 100
    return MAX_SWARM_GUARDIANS


ProviderCaller = Callable[[str], Awaitable[str]]


class GuardianCompany:
    """A company of up to 650 logical Guardians running whole-business missions.

    Wings brainstorm (50), execute (up to 200, complexity-sized), test and QC
    (up to 200, complexity-sized, with an immediate fast path for execution
    failures), and revise (200). Multiple missions run concurrently against
    the same shared company roster and shared experience pool.
    """

    def __init__(self, *, max_parallel: int = DEFAULT_PARALLELISM):
        if max_parallel < 1 or max_parallel > MAX_SWARM_GUARDIANS:
            raise ValueError(f"max_parallel must be between 1 and {MAX_SWARM_GUARDIANS}")
        self.max_parallel = max_parallel
        self.classifier = MissionClassifier()
        self.roster: dict[str, CompanyGuardian] = {}
        self.total_level_ups = 0
        self.shared_xp_granted = 0

    # ------------------------------------------------------------------ roster
    def _enroll(self, team: list[GuardianSpec], wing: str) -> None:
        for spec in team:
            if spec.guardian_id not in self.roster:
                self.roster[spec.guardian_id] = CompanyGuardian(
                    guardian_id=spec.guardian_id,
                    wing=wing,
                    role=spec.role,
                )

    def level(self, guardian_id: str) -> int:
        return self.roster[guardian_id].level

    def record_outcome(self, guardian_id: str, success: bool) -> None:
        """Record a verified swarm outcome: level up, then share XP company-wide.

        Both successes and failures grant +1 level — failures teach. Every
        level-up grants shared XP to the *entire* roster, so when one Guardian
        levels up, the whole company receives experience. XP settles into
        levels silently; settled levels do not re-trigger shared XP, keeping
        the cascade bounded.
        """
        guardian = self.roster[guardian_id]
        if success:
            guardian.successes += 1
        else:
            guardian.failures += 1
        guardian.level += 1
        self.total_level_ups += 1
        self._grant_shared_xp(source_id=guardian_id)

    def _grant_shared_xp(self, *, source_id: str) -> None:
        for guardian_id, guardian in self.roster.items():
            if guardian_id == source_id:
                continue
            guardian.add_xp(COMPANY_SHARED_XP_PER_LEVEL_UP)
            self.shared_xp_granted += COMPANY_SHARED_XP_PER_LEVEL_UP

    def leveling_summary(self) -> dict[str, object]:
        levels = [guardian.level for guardian in self.roster.values()]
        return {
            "guardians": len(levels),
            "starting_level": COMPANY_STARTING_LEVEL,
            "min_level": min(levels) if levels else COMPANY_STARTING_LEVEL,
            "max_level": max(levels) if levels else COMPANY_STARTING_LEVEL,
            "total_level_ups": self.total_level_ups,
            "shared_xp_granted": self.shared_xp_granted,
        }

    # -------------------------------------------------------------- wing sizing
    def wing_sizes(self, goal: str) -> tuple[int, int, int]:
        """Return (complexity_score, execute_size, test_size) for a mission."""
        classification = self.classifier.classify(goal)
        capability_count = len(classification.requirements.capabilities)
        complexity = mission_complexity(goal, capability_count)
        size = wing_size_for_complexity(complexity)
        return complexity, size, size

    # ---------------------------------------------------------------- pipeline
    async def _run_wing(
        self,
        team: list[GuardianSpec],
        wing: str,
        prompt_for: Callable[[GuardianSpec], str],
        call: ProviderCaller,
        on_failure: Callable[[GuardianResult], None] | None = None,
    ) -> list[GuardianResult]:
        self._enroll(team, wing)
        semaphore = asyncio.Semaphore(self.max_parallel)

        async def execute(spec: GuardianSpec) -> GuardianResult:
            async with semaphore:
                try:
                    output = await call(prompt_for(spec))
                    self.record_outcome(spec.guardian_id, True)
                    return GuardianResult(spec.guardian_id, spec.role, output)
                except Exception as exc:  # noqa: BLE001 - isolate one worker from the wing
                    self.record_outcome(spec.guardian_id, False)
                    result = GuardianResult(
                        spec.guardian_id,
                        spec.role,
                        "",
                        ok=False,
                        error=f"{type(exc).__name__}: {exc}",
                    )
                    if on_failure is not None:
                        on_failure(result)
                    return result

        return list(await asyncio.gather(*(execute(spec) for spec in team)))

    async def _synthesize(self, prompt: str, call: ProviderCaller) -> str:
        return (await call(prompt)).strip()

    async def run_mission(
        self,
        goal: str,
        call: ProviderCaller,
        *,
        execute_size: int | None = None,
        test_size: int | None = None,
    ) -> CompanyMissionReport:
        """Run one mission through the four-wing company pipeline."""
        complexity, default_execute, default_test = self.wing_sizes(goal)
        execute_size = execute_size or default_execute
        test_size = test_size or default_test

        report = CompanyMissionReport(
            goal=goal,
            plan=None,
            complexity_score=complexity,
            execute_guardians=execute_size,
            test_guardians=test_size,
            revise_guardians=COMPANY_REVISE_GUARDIANS,
        )

        # Phase 1 — brainstorm wing (fixed 50): diverge, synthesize, red-team, refine.
        brainstorm_team = build_company_team(WING_BRAINSTORM, COMPANY_BRAINSTORM_GUARDIANS)
        divergent = await self._run_wing(
            brainstorm_team,
            WING_BRAINSTORM,
            lambda spec: _diverge_prompt(spec, goal),
            call,
        )
        candidate = await self._synthesize(
            _plan_prompt(goal, compact_evidence([r for r in divergent if r.ok])),
            call,
        )
        critique_team = build_company_team(WING_BRAINSTORM, COMPANY_BRAINSTORM_GUARDIANS)
        critique = await self._run_wing(
            critique_team,
            WING_BRAINSTORM,
            lambda spec: _critique_prompt(spec, goal, candidate),
            call,
        )
        plan = await self._synthesize(
            _refine_prompt(goal, candidate, compact_evidence([r for r in critique if r.ok])),
            call,
        )
        report.plan = plan or None

        # Phase 2 — execution wing, with an immediate fast path into testing.
        fast_path: asyncio.Queue[GuardianResult | None] = asyncio.Queue()
        execute_team = build_company_team(WING_EXECUTE, execute_size)
        fast_path_findings: list[GuardianResult] = []

        async def fast_path_tester() -> None:
            testers = build_company_team(WING_TEST, COMPANY_FAST_PATH_TESTERS)
            self._enroll(testers, WING_TEST)
            while True:
                item = await fast_path.get()
                if item is None:
                    return
                tester = testers[len(fast_path_findings) % len(testers)]
                try:
                    output = await call(_fast_path_prompt(tester, goal, item))
                    self.record_outcome(tester.guardian_id, True)
                    finding = GuardianResult(tester.guardian_id, tester.role, output)
                except Exception as exc:  # noqa: BLE001 - the fast path must never kill the mission
                    self.record_outcome(tester.guardian_id, False)
                    finding = GuardianResult(
                        tester.guardian_id,
                        tester.role,
                        "",
                        ok=False,
                        error=f"{type(exc).__name__}: {exc}",
                    )
                fast_path_findings.append(finding)

        fast_path_task = asyncio.create_task(fast_path_tester())
        execute_results = await self._run_wing(
            execute_team,
            WING_EXECUTE,
            lambda spec: _execute_prompt(spec, goal, plan),
            call,
            on_failure=fast_path.put_nowait,
        )
        await fast_path.put(None)
        await fast_path_task
        report.execute_results = execute_results
        report.fast_path_findings = fast_path_findings

        # Phase 3 — test & QC wing over successful execution output.
        successful = [r for r in execute_results if r.ok]
        evidence = compact_evidence(successful)
        test_team = build_company_team(WING_TEST, test_size)
        qc_results = await self._run_wing(
            test_team,
            WING_TEST,
            lambda spec: _qc_prompt(spec, goal, plan, evidence),
            call,
        )
        report.qc_results = qc_results

        # Phase 4 — bounded revise / re-test loop driven by confirmed defects.
        # Fast-path findings count as confirmed defects for the first cycle only;
        # after that, whether to revise again is decided by the latest QC pass.
        # When every execution failed there is no evidence to revise, so the wing
        # re-implements from the approved plan plus the confirmed failure findings.
        current = evidence or plan
        cycles = 0
        pending_defects = report.confirmed_defects
        while (
            pending_defects > 0
            and cycles < COMPANY_MAX_REVISION_CYCLES
            and current.strip()
        ):
            revise_snapshot = current
            revise_team = build_company_team(WING_REVISE, COMPANY_REVISE_GUARDIANS)
            revisions = await self._run_wing(
                revise_team,
                WING_REVISE,
                partial(
                    _revise_prompt,
                    mission=goal,
                    current=revise_snapshot,
                    defect_count=pending_defects,
                ),
                call,
            )
            current = compact_evidence([r for r in revisions if r.ok]) or current
            retest_snapshot = current
            re_test_team = build_company_team(WING_TEST, test_size)
            qc_results = await self._run_wing(
                re_test_team,
                WING_TEST,
                partial(_qc_prompt, mission=goal, plan=plan, evidence=retest_snapshot),
                call,
            )
            report.qc_results = qc_results
            pending_defects = sum(
                1 for item in qc_results if DEFECT_MARKER in item.output
            )
            cycles += 1
        report.revision_cycles = cycles
        report.final_output = current.strip() or None
        return report

    async def run_company(
        self,
        goals: list[str],
        call: ProviderCaller,
    ) -> CompanyReport:
        """Run multiple missions concurrently against the shared company."""
        if not goals:
            raise ValueError("at least one mission goal is required")
        reports = await asyncio.gather(
            *(self.run_mission(goal, call) for goal in goals)
        )
        return CompanyReport(
            missions=list(reports),
            total_level_ups=self.total_level_ups,
            shared_xp_granted=self.shared_xp_granted,
        )


# ---------------------------------------------------------------------- prompts
def _diverge_prompt(spec: GuardianSpec, mission: str) -> str:
    return (
        "You are one Guardian in the Nexus Starship Guardians company brainstorm wing "
        f"({COMPANY_BRAINSTORM_GUARDIANS} Guardians).\n"
        f"Guardian ID: {spec.guardian_id}\nRole: {spec.role}\nMission: {mission}\n"
        "The requestor's stated goal is the floor, not the ceiling: include at least one "
        "concrete addition that would genuinely exceed their expectations. Be specific about "
        "mechanisms, artifacts, and verification steps. Return concise, actionable work product."
    )


def _plan_prompt(mission: str, evidence: str) -> str:
    return (
        "You are the lead Guardian of the Nexus company brainstorm wing. Synthesize the "
        "Guardian ideas below into ONE coherent candidate execution plan with verification "
        "gates. Preserve the strongest exceed-expectation additions.\n\n"
        f"MISSION:\n{mission}\n\nGUARDIAN IDEAS:\n{evidence}"
    )


def _critique_prompt(spec: GuardianSpec, mission: str, candidate: str) -> str:
    shown = candidate[:6000] if candidate else "(no synthesis produced — propose and attack your own plan)"
    return (
        "You are one Guardian in the Nexus company red-team review.\n"
        f"Guardian ID: {spec.guardian_id}\nRole: {spec.role}\nMission: {mission}\n"
        "Attack the candidate plan from your role's perspective: gaps, wrong assumptions, "
        "missing risks, cheaper or better alternatives. Do not praise; only critique.\n\n"
        f"CANDIDATE PLAN:\n{shown}"
    )


def _refine_prompt(mission: str, candidate: str, critique: str) -> str:
    return (
        "You are the lead Guardian revising the candidate plan after red-team review. Keep "
        "what the critique confirms, fix what it attacks, and finish with verification gates.\n\n"
        f"MISSION:\n{mission}\n\nCANDIDATE PLAN:\n{candidate[:6000]}\n\nCRITIQUE:\n{critique}"
    )


def _execute_prompt(spec: GuardianSpec, mission: str, plan: str) -> str:
    return (
        "You are one Guardian in the Nexus company execution wing.\n"
        f"Guardian ID: {spec.guardian_id}\nRole: {spec.role}\nMission: {mission}\n"
        f"Approved plan:\n{plan[:6000]}\n\n"
        "Implement your role's part of the plan now. Return the actual work product."
    )


def _fast_path_prompt(tester: GuardianSpec, mission: str, failure: GuardianResult) -> str:
    return (
        "You are a Nexus company test & QC Guardian on the fast-error path: an execution "
        "Guardian failed mid-flight and was routed to testers immediately.\n"
        f"Tester ID: {tester.guardian_id}\nRole: {tester.role}\nMission: {mission}\n"
        f"Failed Guardian: {failure.guardian_id} ({failure.role})\n"
        f"Error: {failure.error}\n\n"
        f"Classify the failure and state the bounded repair direction. Start with '{DEFECT_MARKER}:' "
        "if the failure blocks the mission."
    )


def _qc_prompt(spec: GuardianSpec, mission: str, plan: str, evidence: str) -> str:
    return (
        "You are one Guardian in the Nexus company test & QC wing.\n"
        f"Guardian ID: {spec.guardian_id}\nRole: {spec.role}\nMission: {mission}\n"
        f"Approved plan:\n{plan[:3000]}\n\nWORK PRODUCT UNDER TEST:\n{evidence}\n\n"
        f"Verify it independently from your role's perspective. If you find a real defect, "
        f"start your reply with '{DEFECT_MARKER}:' and describe it precisely; otherwise state "
        "what you verified and pass."
    )


def _revise_prompt(spec: GuardianSpec, mission: str, current: str, defect_count: int) -> str:
    return (
        "You are one Guardian in the Nexus company revision wing (200 Guardians re-implementing "
        "the revised plan together).\n"
        f"Guardian ID: {spec.guardian_id}\nRole: {spec.role}\nMission: {mission}\n"
        f"Confirmed defects so far: {defect_count}\n\nCURRENT WORK PRODUCT:\n{current[:6000]}\n\n"
        "Re-implement and improve the work product so the confirmed defects cannot survive. "
        "Return the improved work product itself."
    )
