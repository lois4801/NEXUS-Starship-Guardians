from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .evaluation_lab import EvaluationCase, EvaluationRun, GuardianIntelligenceLab
from .promotion_gate import EvaluationSummary


@dataclass(frozen=True, slots=True)
class TournamentEntry:
    strategy: str
    summary: EvaluationSummary


class StrategyTournament:
    """Compare multiple strategies on the same fixed evaluation corpus."""

    def __init__(self, lab: GuardianIntelligenceLab):
        self.lab = lab

    def summarize(
        self,
        runs: Sequence[EvaluationRun],
        cases: Sequence[EvaluationCase],
    ) -> list[TournamentEntry]:
        entries = [TournamentEntry(run.strategy, run.summary(cases)) for run in runs]
        return sorted(
            entries,
            key=lambda item: (
                item.summary.critical_failures == 0,
                item.summary.pass_rate,
                item.summary.average_score,
                -item.summary.cost,
                -item.summary.latency_seconds,
            ),
            reverse=True,
        )
