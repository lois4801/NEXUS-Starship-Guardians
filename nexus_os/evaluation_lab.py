from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .failure_taxonomy import FailureSignal, classify_failure
from .promotion_gate import EvaluationSummary, PromotionDecision, PromotionPolicy, decide_promotion

if TYPE_CHECKING:
    from .fixed_corpus import FixedEvaluationCorpus


@dataclass(frozen=True, slots=True)
class EvaluationCase:
    case_id: str
    task: str
    expected: str = ""
    critical: bool = False
    provenance: str = "manual"
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EvaluationOutcome:
    case_id: str
    passed: bool
    score: float
    output: str = ""
    critique: str = ""
    cost: float = 0.0
    latency_seconds: float = 0.0
    failure: FailureSignal | None = None

    def __post_init__(self) -> None:
        if not 0 <= self.score <= 10:
            raise ValueError("evaluation score must be between 0 and 10")


@dataclass(slots=True)
class EvaluationRun:
    strategy: str
    outcomes: list[EvaluationOutcome] = field(default_factory=list)
    corpus_id: str = ""
    corpus_version: str = ""
    corpus_fingerprint: str = ""

    def summary(self, cases: Sequence[EvaluationCase]) -> EvaluationSummary:
        critical_ids = {case.case_id for case in cases if case.critical}
        return EvaluationSummary(
            name=self.strategy,
            passed=sum(1 for item in self.outcomes if item.passed),
            total=len(self.outcomes),
            average_score=(
                sum(item.score for item in self.outcomes) / len(self.outcomes)
                if self.outcomes
                else 0.0
            ),
            critical_failures=sum(
                1 for item in self.outcomes if item.case_id in critical_ids and not item.passed
            ),
            cost=sum(item.cost for item in self.outcomes),
            latency_seconds=sum(item.latency_seconds for item in self.outcomes),
        )


Executor = Callable[[str, EvaluationCase], EvaluationOutcome]


class GuardianIntelligenceLab:
    """Run reproducible strategy evaluations and evidence-based promotion decisions."""

    def run(
        self,
        strategy: str,
        cases: Sequence[EvaluationCase],
        executor: Executor,
    ) -> EvaluationRun:
        run = EvaluationRun(strategy=strategy)
        for case in cases:
            started = time.perf_counter()
            outcome = executor(strategy, case)
            elapsed = time.perf_counter() - started
            if outcome.case_id != case.case_id:
                raise ValueError("executor returned an outcome for the wrong evaluation case")
            if outcome.latency_seconds <= 0:
                outcome = EvaluationOutcome(
                    case_id=outcome.case_id,
                    passed=outcome.passed,
                    score=outcome.score,
                    output=outcome.output,
                    critique=outcome.critique,
                    cost=outcome.cost,
                    latency_seconds=elapsed,
                    failure=outcome.failure,
                )
            if not outcome.passed and outcome.failure is None:
                outcome = EvaluationOutcome(
                    case_id=outcome.case_id,
                    passed=False,
                    score=outcome.score,
                    output=outcome.output,
                    critique=outcome.critique,
                    cost=outcome.cost,
                    latency_seconds=outcome.latency_seconds,
                    failure=classify_failure(critique=outcome.critique or outcome.output),
                )
            run.outcomes.append(outcome)
        return run

    def run_fixed(
        self,
        strategy: str,
        corpus: FixedEvaluationCorpus,
        executor: Executor,
    ) -> EvaluationRun:
        """Run a strategy against a versioned corpus and bind the run to its fingerprint."""
        run = self.run(strategy, corpus.cases, executor)
        run.corpus_id = corpus.corpus_id
        run.corpus_version = corpus.version
        run.corpus_fingerprint = corpus.sha256
        return run

    def compare(
        self,
        *,
        baseline: EvaluationRun,
        candidate: EvaluationRun,
        cases: Sequence[EvaluationCase],
        policy: PromotionPolicy | None = None,
    ) -> PromotionDecision:
        return decide_promotion(
            baseline.summary(cases),
            candidate.summary(cases),
            policy,
        )

    def compare_fixed(
        self,
        *,
        baseline: EvaluationRun,
        candidate: EvaluationRun,
        corpus: FixedEvaluationCorpus,
        policy: PromotionPolicy | None = None,
    ) -> PromotionDecision:
        """Compare runs only when both are bound to the exact supplied corpus snapshot."""
        expected = corpus.sha256
        reasons: list[str] = []
        if baseline.corpus_fingerprint != expected:
            reasons.append("baseline run does not match the supplied fixed corpus fingerprint")
        if candidate.corpus_fingerprint != expected:
            reasons.append("candidate run does not match the supplied fixed corpus fingerprint")
        if baseline.corpus_id != corpus.corpus_id or candidate.corpus_id != corpus.corpus_id:
            reasons.append("baseline and candidate must use the same fixed corpus ID")
        if baseline.corpus_version != corpus.version or candidate.corpus_version != corpus.version:
            reasons.append("baseline and candidate must use the same fixed corpus version")
        if reasons:
            return PromotionDecision(promote=False, reasons=reasons)
        return self.compare(
            baseline=baseline,
            candidate=candidate,
            cases=corpus.cases,
            policy=policy,
        )
