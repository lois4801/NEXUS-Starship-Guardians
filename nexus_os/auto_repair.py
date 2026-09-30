from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from nexus_os.evidence_bundle import EvidenceBundle
from nexus_os.learning_memory import GuardianLearningEngine

Build = Callable[[], Awaitable[str]]
Verify = Callable[[str], Awaitable[tuple[bool, str]]]
Repair = Callable[[str, str, int], Awaitable[str]]
Reflect = Callable[[str, str, str], Awaitable[str]]


@dataclass(slots=True)
class RepairRound:
    round_number: int
    candidate: str
    verification: str
    passed: bool


@dataclass(slots=True)
class AutoRepairReport:
    task: str
    passed: bool
    final_candidate: str
    rounds: list[RepairRound] = field(default_factory=list)
    evidence: EvidenceBundle | None = None


class VerifiedAutoRepairLoop:
    """Bounded build -> verify -> repair loop with evidence and cross-run learning."""

    def __init__(
        self,
        *,
        max_rounds: int = 3,
        learning: GuardianLearningEngine | None = None,
    ):
        if max_rounds < 1 or max_rounds > 10:
            raise ValueError("max_rounds must be between 1 and 10")
        self.max_rounds = max_rounds
        self.learning = learning

    async def run(
        self,
        task: str,
        build: Build,
        verify: Verify,
        repair: Repair,
        *,
        reflect: Reflect | None = None,
    ) -> AutoRepairReport:
        candidate = await build()
        rounds: list[RepairRound] = []
        evidence = EvidenceBundle(mission=task)
        final_verification = ""
        passed = False

        for round_number in range(1, self.max_rounds + 1):
            passed, final_verification = await verify(candidate)
            rounds.append(
                RepairRound(
                    round_number=round_number,
                    candidate=candidate,
                    verification=final_verification,
                    passed=passed,
                )
            )
            evidence.add_text(
                "verification",
                f"repair-round-{round_number}",
                final_verification,
                metadata={"passed": str(passed).lower()},
            )
            if passed:
                break
            if round_number < self.max_rounds:
                candidate = await repair(candidate, final_verification, round_number)

        lesson = ""
        if reflect is not None:
            lesson = await reflect(task, candidate, final_verification)
            if lesson.strip():
                evidence.add_text("reflection", "Guardian reflection", lesson)

        if self.learning is not None:
            self.learning.learn_from_run(
                task=task,
                deliverable=candidate,
                score=10.0 if passed else 0.0,
                critique=final_verification,
                rounds=len(rounds),
                distilled_lesson=lesson or final_verification,
                evidence_refs=tuple(item.sha256 for item in evidence.items),
                metadata={"verified": str(passed).lower()},
            )

        return AutoRepairReport(
            task=task,
            passed=passed,
            final_candidate=candidate,
            rounds=rounds,
            evidence=evidence,
        )
