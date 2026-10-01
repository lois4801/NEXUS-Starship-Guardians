from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Mapping

from .evaluation_lab import EvaluationCase


CORE_CORPUS_SHA256 = "58e81cf285623497af9c4ee96cacfa9ddce2270636f697b51dbdc77c7cb4387e"


@dataclass(frozen=True, slots=True)
class FixedEvaluationCorpus:
    """Immutable, fingerprinted evaluation corpus for reproducible comparisons."""

    corpus_id: str
    version: str
    description: str
    cases: tuple[EvaluationCase, ...]
    schema_version: int = 1

    def __post_init__(self) -> None:
        if self.schema_version != 1:
            raise ValueError("unsupported fixed-corpus schema version")
        if not self.corpus_id.strip():
            raise ValueError("corpus_id cannot be empty")
        if not self.version.strip():
            raise ValueError("corpus version cannot be empty")
        if not self.cases:
            raise ValueError("fixed evaluation corpus must contain at least one case")
        case_ids = [case.case_id for case in self.cases]
        if len(case_ids) != len(set(case_ids)):
            raise ValueError("fixed evaluation corpus contains duplicate case IDs")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "corpus_id": self.corpus_id,
            "version": self.version,
            "description": self.description,
            "cases": [
                {
                    "case_id": case.case_id,
                    "task": case.task,
                    "expected": case.expected,
                    "critical": case.critical,
                    "provenance": case.provenance,
                    "tags": list(case.tags),
                }
                for case in self.cases
            ],
        }

    @property
    def sha256(self) -> str:
        payload = json.dumps(
            self.canonical_payload(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "FixedEvaluationCorpus":
        try:
            raw_cases = payload["cases"]
        except KeyError as exc:
            raise ValueError("fixed corpus is missing cases") from exc
        if not isinstance(raw_cases, list):
            raise ValueError("fixed corpus cases must be a list")

        cases: list[EvaluationCase] = []
        for index, item in enumerate(raw_cases):
            if not isinstance(item, Mapping):
                raise ValueError(f"fixed corpus case {index} must be an object")
            try:
                case_id = str(item["case_id"]).strip()
                task = str(item["task"]).strip()
            except KeyError as exc:
                raise ValueError(f"fixed corpus case {index} is missing {exc.args[0]}") from exc
            if not case_id or not task:
                raise ValueError(f"fixed corpus case {index} requires non-empty case_id and task")
            raw_tags = item.get("tags", [])
            if not isinstance(raw_tags, list) or not all(isinstance(tag, str) for tag in raw_tags):
                raise ValueError(f"fixed corpus case {case_id} tags must be a list of strings")
            critical = item.get("critical", False)
            if not isinstance(critical, bool):
                raise ValueError(f"fixed corpus case {case_id} critical must be a boolean")
            cases.append(
                EvaluationCase(
                    case_id=case_id,
                    task=task,
                    expected=str(item.get("expected", "")).strip(),
                    critical=critical,
                    provenance=str(item.get("provenance", "manual")).strip() or "manual",
                    tags=tuple(tag.strip() for tag in raw_tags if tag.strip()),
                )
            )

        schema_version = payload.get("schema_version", 1)
        if not isinstance(schema_version, int):
            raise ValueError("fixed-corpus schema_version must be an integer")
        return cls(
            corpus_id=str(payload.get("corpus_id", "")).strip(),
            version=str(payload.get("version", "")).strip(),
            description=str(payload.get("description", "")).strip(),
            cases=tuple(cases),
            schema_version=schema_version,
        )

    @classmethod
    def from_json_text(
        cls,
        text: str,
        *,
        expected_sha256: str | None = None,
        source: str = "<memory>",
    ) -> "FixedEvaluationCorpus":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"fixed corpus is not valid JSON: {source}") from exc
        if not isinstance(payload, Mapping):
            raise ValueError("fixed corpus root must be a JSON object")
        corpus = cls.from_mapping(payload)
        if expected_sha256 is not None and corpus.sha256 != expected_sha256:
            raise ValueError(
                "fixed corpus fingerprint mismatch: "
                f"expected {expected_sha256}, got {corpus.sha256}"
            )
        return corpus

    @classmethod
    def load(
        cls,
        path: Path,
        *,
        expected_sha256: str | None = None,
    ) -> "FixedEvaluationCorpus":
        return cls.from_json_text(
            path.read_text(encoding="utf-8"),
            expected_sha256=expected_sha256,
            source=str(path),
        )

    @classmethod
    def load_core(cls) -> "FixedEvaluationCorpus":
        """Load the locked core corpus shipped inside the Python package."""
        text = resources.files("nexus_os").joinpath("benchmarks/core_v1.json").read_text(
            encoding="utf-8"
        )
        return cls.from_json_text(
            text,
            expected_sha256=CORE_CORPUS_SHA256,
            source="nexus_os/benchmarks/core_v1.json",
        )
