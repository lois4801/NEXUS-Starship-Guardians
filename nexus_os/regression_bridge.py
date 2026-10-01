from __future__ import annotations

from dataclasses import dataclass

from .benchmark_vault import BenchmarkCandidate, GuardianBenchmarkVault
from .failure_taxonomy import FailureSignal, classify_failure
from .regression_corpus import RegressionCase, RegressionCorpus


@dataclass(frozen=True, slots=True)
class RegressionCapture:
    failure: FailureSignal
    case: RegressionCase
    benchmark_candidate: BenchmarkCandidate | None = None


class RegressionLearningBridge:
    """Promote verified execution failures into reusable regression cases and vault candidates."""

    def __init__(
        self,
        corpus: RegressionCorpus,
        benchmark_vault: GuardianBenchmarkVault | None = None,
    ):
        self.corpus = corpus
        self.benchmark_vault = benchmark_vault

    def capture(
        self,
        *,
        title: str,
        task: str,
        expected: str,
        error: str = "",
        critique: str = "",
        regression: bool = False,
        verified: bool,
        provenance: str,
        tags: tuple[str, ...] = (),
        evidence_ref: str = "",
    ) -> RegressionCapture | None:
        if not verified:
            return None
        if self.benchmark_vault is not None and not evidence_ref.strip():
            raise ValueError("Benchmark Vault nomination requires evidence_ref")

        failure = classify_failure(error=error, critique=critique, regression=regression)
        case = self.corpus.add(
            title=title,
            task=task,
            expected=expected,
            failure=failure,
            provenance=provenance,
            tags=tags,
        )
        benchmark_candidate = None
        if self.benchmark_vault is not None:
            benchmark_candidate = self.benchmark_vault.nominate(
                case,
                evidence_ref=evidence_ref,
                extra_tags=("verified-regression",),
            )
        return RegressionCapture(
            failure=failure,
            case=case,
            benchmark_candidate=benchmark_candidate,
        )
