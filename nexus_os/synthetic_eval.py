from __future__ import annotations

import hashlib
import json
import time
import uuid
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path


class FailureCategory(StrEnum):
    CORRECTNESS = "correctness"
    COMPLETENESS = "completeness"
    SAFETY = "safety"
    TOOL_USE = "tool-use"
    REGRESSION = "regression"
    RELIABILITY = "reliability"
    UNKNOWN = "unknown"


@dataclass(slots=True, frozen=True)
class EvalCase:
    case_id: str
    task: str
    requirements: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    source: str = "synthetic"
    critical: bool = False
    provenance: str = ""

    @classmethod
    def create(
        cls,
        task: str,
        *,
        requirements: tuple[str, ...] = (),
        tags: tuple[str, ...] = (),
        source: str = "synthetic",
        critical: bool = False,
        provenance: str = "",
    ) -> EvalCase:
        digest = hashlib.sha256(
            json.dumps(
                {
                    "task": task,
                    "requirements": requirements,
                    "tags": tags,
                    "source": source,
                    "critical": critical,
                    "provenance": provenance,
                },
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()[:16]
        return cls(
            case_id=f"eval-{digest}",
            task=task,
            requirements=requirements,
            tags=tags,
            source=source,
            critical=critical,
            provenance=provenance,
        )


@dataclass(slots=True, frozen=True)
class EvalJudgement:
    score: float
    passed: bool
    critique: str = ""
    failure_category: FailureCategory | None = None


@dataclass(slots=True)
class EvalResult:
    case: EvalCase
    output: str
    judgement: EvalJudgement
    duration_seconds: float
    error: str | None = None


@dataclass(slots=True)
class CandidateReport:
    candidate: str
    results: list[EvalResult] = field(default_factory=list)

    @property
    def average_score(self) -> float:
        if not self.results:
            return 0.0
        return sum(item.judgement.score for item in self.results) / len(self.results)

    @property
    def pass_rate(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for item in self.results if item.judgement.passed) / len(self.results)

    @property
    def critical_failures(self) -> int:
        return sum(
            1
            for item in self.results
            if item.case.critical and not item.judgement.passed
        )

    @property
    def failure_taxonomy(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self.results:
            category = item.judgement.failure_category
            if item.judgement.passed or category is None:
                continue
            counts[category.value] = counts.get(category.value, 0) + 1
        return counts


@dataclass(slots=True, frozen=True)
class PromotionDecision:
    approved: bool
    reasons: tuple[str, ...]
    candidate_score: float
    baseline_score: float
    candidate_pass_rate: float
    baseline_pass_rate: float


Runner = Callable[[EvalCase], Awaitable[str]]
Judge = Callable[[EvalCase, str], Awaitable[EvalJudgement]]


class EvaluationStore:
    """Append-only provenance store for synthetic and regression evaluation reports."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append_report(self, report: CandidateReport) -> str:
        report_id = uuid.uuid4().hex
        payload = {
            "type": "evaluation-report",
            "report_id": report_id,
            "candidate": report.candidate,
            "created_at": time.time(),
            "average_score": report.average_score,
            "pass_rate": report.pass_rate,
            "critical_failures": report.critical_failures,
            "failure_taxonomy": report.failure_taxonomy,
            "results": [
                {
                    "case": asdict(item.case),
                    "output": item.output,
                    "judgement": {
                        "score": item.judgement.score,
                        "passed": item.judgement.passed,
                        "critique": item.judgement.critique,
                        "failure_category": (
                            item.judgement.failure_category.value
                            if item.judgement.failure_category
                            else None
                        ),
                    },
                    "duration_seconds": item.duration_seconds,
                    "error": item.error,
                }
                for item in report.results
            ],
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        return report_id


class SyntheticEvaluationLab:
    """Run repeatable Guardian evaluations and make evidence-based promotion decisions."""

    def __init__(self, *, judge: Judge, store: EvaluationStore | None = None):
        self.judge = judge
        self.store = store

    async def evaluate(
        self,
        candidate_name: str,
        cases: Sequence[EvalCase],
        runner: Runner,
    ) -> CandidateReport:
        report = CandidateReport(candidate=candidate_name)
        for case in cases:
            started = time.monotonic()
            try:
                output = await runner(case)
                judgement = await self.judge(case, output)
                error = None
            except (RuntimeError, ValueError, TimeoutError, OSError) as exc:
                output = ""
                error = f"{type(exc).__name__}: {exc}"
                judgement = EvalJudgement(
                    score=0.0,
                    passed=False,
                    critique=error,
                    failure_category=FailureCategory.RELIABILITY,
                )
            report.results.append(
                EvalResult(
                    case=case,
                    output=output,
                    judgement=judgement,
                    duration_seconds=time.monotonic() - started,
                    error=error,
                )
            )
        if self.store is not None:
            self.store.append_report(report)
        return report

    @staticmethod
    def promotion_decision(
        baseline: CandidateReport,
        candidate: CandidateReport,
        *,
        min_score_delta: float = 0.0,
        min_pass_rate: float = 0.8,
    ) -> PromotionDecision:
        reasons: list[str] = []
        if candidate.critical_failures:
            reasons.append(f"candidate has {candidate.critical_failures} critical regression(s)")
        if candidate.pass_rate < min_pass_rate:
            reasons.append(
                f"candidate pass rate {candidate.pass_rate:.3f} is below required {min_pass_rate:.3f}"
            )
        if candidate.pass_rate < baseline.pass_rate:
            reasons.append("candidate pass rate regressed versus baseline")
        required_score = baseline.average_score + min_score_delta
        if candidate.average_score < required_score:
            reasons.append(
                f"candidate score {candidate.average_score:.3f} is below required {required_score:.3f}"
            )
        return PromotionDecision(
            approved=not reasons,
            reasons=tuple(reasons),
            candidate_score=candidate.average_score,
            baseline_score=baseline.average_score,
            candidate_pass_rate=candidate.pass_rate,
            baseline_pass_rate=baseline.pass_rate,
        )


async def requirements_judge(case: EvalCase, output: str) -> EvalJudgement:
    """Deterministic offline judge useful for regression smoke tests.

    Model-based judges can be supplied for semantic scoring, but promotion should retain
    deterministic acceptance tests so one judge model cannot redefine success by itself.
    """
    lowered = output.lower()
    missing = [requirement for requirement in case.requirements if requirement.lower() not in lowered]
    if missing:
        score = max(0.0, 10.0 - 2.0 * len(missing))
        return EvalJudgement(
            score=score,
            passed=False,
            critique=f"Missing required evidence: {', '.join(missing)}",
            failure_category=FailureCategory.COMPLETENESS,
        )
    return EvalJudgement(score=10.0, passed=True, critique="All deterministic requirements present.")
