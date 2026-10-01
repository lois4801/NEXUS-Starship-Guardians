from __future__ import annotations

from dataclasses import dataclass

from .failure_taxonomy import FailureSignal, classify_failure
from .regression_corpus import RegressionCase, RegressionCorpus


@dataclass(frozen=True, slots=True)
class RegressionCapture:
    failure: FailureSignal
    case: RegressionCase


class RegressionLearningBridge:
    """Promote verified execution failures into reusable regression cases."""

    def __init__(self, corpus: RegressionCorpus):
        self.corpus = corpus

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
    ) -> RegressionCapture | None:
        if not verified:
            return None
        failure = classify_failure(error=error, critique=critique, regression=regression)
        case = self.corpus.add(
            title=title,
            task=task,
            expected=expected,
            failure=failure,
            provenance=provenance,
            tags=tags,
        )
        return RegressionCapture(failure=failure, case=case)
