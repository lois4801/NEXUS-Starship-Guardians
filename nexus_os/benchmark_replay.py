from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from nexus_os.benchmark_vault import BenchmarkCandidate, GuardianBenchmarkVault
from nexus_os.evaluation_lab import EvaluationOutcome, Executor, GuardianIntelligenceLab


@dataclass(frozen=True, slots=True)
class ReplayOutcome:
    strategy: str
    passed: bool
    score: float
    failure_category: str = ""


@dataclass(frozen=True, slots=True)
class CandidateReplayReport:
    candidate_case_id: str
    outcomes: tuple[ReplayOutcome, ...]

    @property
    def replay_count(self) -> int:
        return len(self.outcomes)

    @property
    def pass_rate(self) -> float:
        return (
            sum(1 for outcome in self.outcomes if outcome.passed) / len(self.outcomes)
            if self.outcomes
            else 0.0
        )

    @property
    def reproduced_failure(self) -> bool:
        return any(not outcome.passed for outcome in self.outcomes)

    @property
    def review_ready(self) -> bool:
        return bool(self.outcomes)


class BenchmarkReplayEngine:
    """Replay Benchmark Vault candidates before human/governed review.

    Replay evidence is diagnostic. It can increase confidence in a candidate but cannot approve
    the candidate or rewrite a frozen benchmark snapshot on its own.
    """

    def __init__(self, lab: GuardianIntelligenceLab | None = None):
        self.lab = lab or GuardianIntelligenceLab()

    def replay_candidate(
        self,
        candidate: BenchmarkCandidate,
        *,
        strategies: Iterable[str],
        executor: Executor,
        vault: GuardianBenchmarkVault | None = None,
    ) -> CandidateReplayReport:
        case = candidate.to_evaluation_case()
        outcomes: list[ReplayOutcome] = []
        for strategy in strategies:
            if not strategy.strip():
                continue
            run = self.lab.run(strategy, (case,), executor)
            if not run.outcomes:
                continue
            outcome: EvaluationOutcome = run.outcomes[0]
            failure_category = outcome.failure.category.value if outcome.failure is not None else ""
            replay = ReplayOutcome(
                strategy=strategy,
                passed=outcome.passed,
                score=outcome.score,
                failure_category=failure_category,
            )
            outcomes.append(replay)
            if vault is not None:
                vault.record_replay(
                    candidate.case_id,
                    strategy=strategy,
                    passed=outcome.passed,
                    score=outcome.score,
                    failure_category=failure_category,
                )
        return CandidateReplayReport(candidate.case_id, tuple(outcomes))

    def replay_pending(
        self,
        vault: GuardianBenchmarkVault,
        *,
        strategies: Iterable[str],
        executor: Executor,
    ) -> list[CandidateReplayReport]:
        reports: list[CandidateReplayReport] = []
        for candidate in vault.candidates():
            if candidate.status != "candidate":
                continue
            reports.append(
                self.replay_candidate(
                    candidate,
                    strategies=strategies,
                    executor=executor,
                    vault=vault,
                )
            )
        return reports
