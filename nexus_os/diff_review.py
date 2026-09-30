from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum


class ReviewSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(slots=True)
class DiffFinding:
    severity: ReviewSeverity
    code: str
    message: str
    line: str = ""


@dataclass(slots=True)
class DiffReviewReport:
    findings: list[DiffFinding] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0

    @property
    def blocking(self) -> bool:
        return any(item.severity == ReviewSeverity.HIGH for item in self.findings)

    @property
    def score(self) -> int:
        penalty = sum(
            3 if item.severity == ReviewSeverity.HIGH else 2 if item.severity == ReviewSeverity.MEDIUM else 1
            for item in self.findings
        )
        return max(0, 10 - penalty)


_SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


class AutomaticDiffReviewer:
    """Fast deterministic first-pass review before model/human review."""

    def __init__(self, *, max_changed_lines: int = 1500):
        self.max_changed_lines = max_changed_lines

    def review(self, diff: str) -> DiffReviewReport:
        report = DiffReviewReport()
        for raw in diff.splitlines():
            if raw.startswith("+++") or raw.startswith("---"):
                continue
            if raw.startswith("+"):
                report.additions += 1
                line = raw[1:]
                self._inspect_added_line(line, report)
            elif raw.startswith("-"):
                report.deletions += 1

        changed = report.additions + report.deletions
        if changed > self.max_changed_lines:
            report.findings.append(
                DiffFinding(
                    ReviewSeverity.MEDIUM,
                    "large-diff",
                    f"Diff changes {changed} lines; split or require focused review.",
                )
            )
        return report

    @staticmethod
    def _inspect_added_line(line: str, report: DiffReviewReport) -> None:
        stripped = line.strip()
        if any(marker in line for marker in ("<<<<<<<", "=======", ">>>>>>>")):
            report.findings.append(
                DiffFinding(ReviewSeverity.HIGH, "conflict-marker", "Unresolved merge conflict marker.", line)
            )
        if any(pattern.search(line) for pattern in _SECRET_PATTERNS):
            report.findings.append(
                DiffFinding(ReviewSeverity.HIGH, "possible-secret", "Possible credential or private key in diff.", line)
            )
        if "# noqa" in line and "BLE001" not in line:
            report.findings.append(
                DiffFinding(ReviewSeverity.LOW, "lint-suppression", "New lint suppression should be justified.", line)
            )
        if re.search(r"\b(TODO|FIXME|HACK)\b", stripped, re.IGNORECASE):
            report.findings.append(
                DiffFinding(ReviewSeverity.LOW, "unfinished-marker", "New TODO/FIXME/HACK marker added.", line)
            )
        if re.search(r"(?i)verify\s*=\s*False", line):
            report.findings.append(
                DiffFinding(ReviewSeverity.HIGH, "tls-disabled", "TLS verification appears disabled.", line)
            )
