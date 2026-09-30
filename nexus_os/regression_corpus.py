from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .failure_taxonomy import FailureCategory, FailureSignal


@dataclass(frozen=True, slots=True)
class RegressionCase:
    case_id: str
    title: str
    task: str
    expected: str
    category: FailureCategory
    severity: int
    provenance: str
    tags: tuple[str, ...] = ()
    created_at: float = field(default_factory=time.time)


class RegressionCorpus:
    """Append-only regression cases derived from verified failures and repairs."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def fingerprint(task: str, expected: str, category: FailureCategory) -> str:
        raw = f"{category.value}\n{task.strip()}\n{expected.strip()}".encode()
        return hashlib.sha256(raw).hexdigest()[:20]

    def records(self) -> list[RegressionCase]:
        if not self.path.exists():
            return []
        items: list[RegressionCase] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            try:
                data = json.loads(line)
                data["category"] = FailureCategory(data["category"])
                data["tags"] = tuple(data.get("tags", ()))
                items.append(RegressionCase(**data))
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                continue
        return items

    def add(
        self,
        *,
        title: str,
        task: str,
        expected: str,
        failure: FailureSignal,
        provenance: str,
        tags: tuple[str, ...] = (),
    ) -> RegressionCase:
        case_id = self.fingerprint(task, expected, failure.category)
        existing = {item.case_id: item for item in self.records()}
        if case_id in existing:
            return existing[case_id]
        case = RegressionCase(
            case_id=case_id,
            title=title.strip(),
            task=task.strip(),
            expected=expected.strip(),
            category=failure.category,
            severity=failure.severity,
            provenance=provenance.strip(),
            tags=tags,
        )
        payload = asdict(case)
        payload["category"] = case.category.value
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        return case

    def critical(self) -> list[RegressionCase]:
        return [item for item in self.records() if item.severity >= 5]
