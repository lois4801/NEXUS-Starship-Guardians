from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, replace
from pathlib import Path

from nexus_os.evaluation_lab import EvaluationCase
from nexus_os.fixed_corpus import FixedEvaluationCorpus
from nexus_os.regression_corpus import RegressionCase


@dataclass(frozen=True, slots=True)
class BenchmarkCandidate:
    case_id: str
    task: str
    expected: str
    critical: bool
    provenance: str
    tags: tuple[str, ...]
    source_case_id: str
    category: str
    severity: int
    evidence_ref: str
    status: str = "candidate"
    reviewer: str = ""
    review_note: str = ""
    created_at: float = 0.0
    reviewed_at: float = 0.0
    replay_count: int = 0
    replay_passes: int = 0
    replay_failures: int = 0
    last_replayed_at: float = 0.0
    last_replay_strategy: str = ""
    last_replay_score: float = 0.0
    last_replay_failure_category: str = ""

    def __post_init__(self) -> None:
        if self.status not in {"candidate", "approved", "rejected"}:
            raise ValueError("benchmark candidate status must be candidate, approved, or rejected")
        if not self.case_id.strip() or not self.task.strip():
            raise ValueError("benchmark candidate requires non-empty case_id and task")
        if not self.evidence_ref.strip():
            raise ValueError("benchmark candidates require a verification evidence reference")
        if not 1 <= self.severity <= 5:
            raise ValueError("benchmark candidate severity must be between 1 and 5")
        if self.replay_count < 0 or self.replay_passes < 0 or self.replay_failures < 0:
            raise ValueError("benchmark replay counters cannot be negative")
        if self.replay_passes + self.replay_failures > self.replay_count:
            raise ValueError("benchmark replay pass/fail counters cannot exceed replay_count")

    @property
    def replayed(self) -> bool:
        return self.replay_count > 0

    @property
    def replay_pass_rate(self) -> float:
        return self.replay_passes / self.replay_count if self.replay_count else 0.0

    def to_evaluation_case(self) -> EvaluationCase:
        return EvaluationCase(
            case_id=self.case_id,
            task=self.task,
            expected=self.expected,
            critical=self.critical,
            provenance=self.provenance,
            tags=self.tags,
        )


class GuardianBenchmarkVault:
    """Governed store that turns verified regressions into reviewable benchmark candidates."""

    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.candidates_path = self.root / "candidates.json"
        self.snapshots_dir = self.root / "snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def candidates(self) -> list[BenchmarkCandidate]:
        if not self.candidates_path.exists():
            return []
        try:
            payload = json.loads(self.candidates_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        if not isinstance(payload, list):
            return []
        records: list[BenchmarkCandidate] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            try:
                item["tags"] = tuple(item.get("tags", ()))
                records.append(BenchmarkCandidate(**item))
            except (TypeError, ValueError):
                continue
        return records

    def _write_candidates(self, items: list[BenchmarkCandidate]) -> None:
        payload = []
        for item in items:
            record = asdict(item)
            record["tags"] = list(item.tags)
            payload.append(record)
        self.candidates_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def nominate(
        self,
        regression: RegressionCase,
        *,
        evidence_ref: str,
        extra_tags: tuple[str, ...] = (),
    ) -> BenchmarkCandidate:
        """Nominate a verified regression without silently approving it into a benchmark."""
        existing = {item.source_case_id: item for item in self.candidates()}
        if regression.case_id in existing:
            return existing[regression.case_id]
        tags = tuple(dict.fromkeys((*regression.tags, regression.category.value, *extra_tags)))
        candidate = BenchmarkCandidate(
            case_id=f"regression-{regression.case_id}",
            task=regression.task,
            expected=regression.expected,
            critical=regression.severity >= 5,
            provenance=regression.provenance,
            tags=tags,
            source_case_id=regression.case_id,
            category=regression.category.value,
            severity=regression.severity,
            evidence_ref=evidence_ref.strip(),
            created_at=time.time(),
        )
        records = self.candidates()
        records.append(candidate)
        self._write_candidates(records)
        return candidate

    def record_replay(
        self,
        case_id: str,
        *,
        strategy: str,
        passed: bool,
        score: float,
        failure_category: str = "",
    ) -> BenchmarkCandidate:
        if not strategy.strip():
            raise ValueError("benchmark replay requires a strategy")
        if not 0 <= score <= 10:
            raise ValueError("benchmark replay score must be between 0 and 10")
        records = self.candidates()
        for index, item in enumerate(records):
            if item.case_id != case_id:
                continue
            replayed = replace(
                item,
                replay_count=item.replay_count + 1,
                replay_passes=item.replay_passes + int(passed),
                replay_failures=item.replay_failures + int(not passed),
                last_replayed_at=time.time(),
                last_replay_strategy=strategy.strip(),
                last_replay_score=score,
                last_replay_failure_category=failure_category.strip(),
            )
            records[index] = replayed
            self._write_candidates(records)
            return replayed
        raise KeyError(f"unknown benchmark candidate: {case_id}")

    def review(
        self,
        case_id: str,
        *,
        approved: bool,
        reviewer: str,
        note: str = "",
        require_replay: bool = False,
    ) -> BenchmarkCandidate:
        if not reviewer.strip():
            raise ValueError("benchmark review requires a reviewer")
        records = self.candidates()
        for index, item in enumerate(records):
            if item.case_id != case_id:
                continue
            if approved and require_replay and not item.replayed:
                raise ValueError("benchmark approval requires replay evidence")
            reviewed = replace(
                item,
                status="approved" if approved else "rejected",
                reviewer=reviewer.strip(),
                review_note=note.strip(),
                reviewed_at=time.time(),
            )
            records[index] = reviewed
            self._write_candidates(records)
            return reviewed
        raise KeyError(f"unknown benchmark candidate: {case_id}")

    def approved(self) -> list[BenchmarkCandidate]:
        return [item for item in self.candidates() if item.status == "approved"]

    def build_snapshot(
        self,
        *,
        base: FixedEvaluationCorpus,
        version: str,
        description: str | None = None,
    ) -> FixedEvaluationCorpus:
        """Combine an immutable base corpus with reviewed/approved candidate cases."""
        cases = list(base.cases)
        known = {case.case_id for case in cases}
        for candidate in self.approved():
            if candidate.case_id in known:
                continue
            cases.append(candidate.to_evaluation_case())
            known.add(candidate.case_id)
        return FixedEvaluationCorpus(
            corpus_id=base.corpus_id,
            version=version.strip(),
            description=(
                description.strip()
                if description is not None
                else f"{base.description} Governed Guardian Benchmark Vault snapshot."
            ),
            cases=tuple(cases),
            schema_version=base.schema_version,
        )

    def freeze_snapshot(
        self,
        *,
        base: FixedEvaluationCorpus,
        version: str,
        description: str | None = None,
    ) -> tuple[FixedEvaluationCorpus, Path]:
        """Persist a reviewed benchmark snapshot without mutating the packaged core corpus."""
        snapshot = self.build_snapshot(base=base, version=version, description=description)
        safe_version = version.replace("/", "-").strip()
        if not safe_version:
            raise ValueError("snapshot version cannot be empty")
        destination = self.snapshots_dir / f"{snapshot.corpus_id}-{safe_version}.json"
        destination.write_text(
            json.dumps(snapshot.canonical_payload(), ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
        return snapshot, destination
