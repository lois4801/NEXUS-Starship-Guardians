from __future__ import annotations

from dataclasses import dataclass

from nexus_os.evaluation_lab import EvaluationCase
from nexus_os.fixed_corpus import FixedEvaluationCorpus


DEFAULT_COVERAGE_CATEGORIES: tuple[str, ...] = (
    "architecture",
    "platform",
    "coding",
    "debugging",
    "ai-ml",
    "evaluation",
    "cloud",
    "api",
    "security",
    "database",
    "ui",
    "deployment",
    "tool-use",
    "reliability",
)

_CATEGORY_ALIASES: dict[str, frozenset[str]] = {
    "architecture": frozenset({"architecture", "systems-design", "design"}),
    "platform": frozenset({"platform", "platform-engineering", "distributed-systems", "queue"}),
    "coding": frozenset({"coding", "code", "engineering", "programming", "implementation"}),
    "debugging": frozenset({"debugging", "failure", "repair", "root-cause", "regression"}),
    "ai-ml": frozenset({"ai", "ai-ml", "model", "rag", "inference", "agents"}),
    "evaluation": frozenset({"evaluation", "benchmark", "judge", "promotion"}),
    "cloud": frozenset({"cloud", "container", "containers", "infrastructure", "scaling"}),
    "api": frozenset({"api", "contracts", "rest", "http"}),
    "security": frozenset({"security", "permissions", "credentials", "auth", "authentication"}),
    "database": frozenset({"database", "schema", "migration", "postgres", "supabase"}),
    "ui": frozenset({"ui", "ux", "browser", "frontend", "visual"}),
    "deployment": frozenset({"deployment", "release", "rollback", "hosting"}),
    "tool-use": frozenset({"tool-use", "tools", "integration", "connector"}),
    "reliability": frozenset({"reliability", "verification", "completion-claims", "evidence"}),
}


@dataclass(frozen=True, slots=True)
class CoverageGap:
    category: str
    current_cases: int
    target_cases: int

    @property
    def missing_cases(self) -> int:
        return max(0, self.target_cases - self.current_cases)


@dataclass(frozen=True, slots=True)
class CoverageSnapshot:
    name: str
    corpus_id: str
    corpus_version: str
    corpus_fingerprint: str
    total_cases: int
    category_counts: dict[str, int]
    critical_counts: dict[str, int]
    uncategorized_cases: tuple[str, ...]

    def coverage_ratio(self, category: str, *, target_cases: int = 3) -> float:
        if target_cases < 1:
            raise ValueError("target_cases must be at least 1")
        return min(1.0, self.category_counts.get(category, 0) / target_cases)

    def gaps(self, *, target_cases: int = 3) -> list[CoverageGap]:
        if target_cases < 1:
            raise ValueError("target_cases must be at least 1")
        gaps = [
            CoverageGap(category, self.category_counts.get(category, 0), target_cases)
            for category in DEFAULT_COVERAGE_CATEGORIES
            if self.category_counts.get(category, 0) < target_cases
        ]
        gaps.sort(key=lambda item: (item.missing_cases, item.category), reverse=True)
        return gaps


@dataclass(frozen=True, slots=True)
class CoverageDelta:
    category: str
    previous: int
    current: int

    @property
    def change(self) -> int:
        return self.current - self.previous


class CoverageIntelligence:
    """Measure benchmark breadth so Guardian learning is not optimized to a narrow corpus."""

    def classify(self, case: EvaluationCase) -> frozenset[str]:
        terms = {tag.lower().strip() for tag in case.tags if tag.strip()}
        task = case.task.lower()
        expected = case.expected.lower()
        categories: set[str] = set()
        for category, aliases in _CATEGORY_ALIASES.items():
            if terms & aliases:
                categories.add(category)
                continue
            if any(alias in task or alias in expected for alias in aliases):
                categories.add(category)
        return frozenset(categories)

    def analyze(
        self,
        corpus: FixedEvaluationCorpus,
        *,
        name: str | None = None,
    ) -> CoverageSnapshot:
        counts = {category: 0 for category in DEFAULT_COVERAGE_CATEGORIES}
        critical = {category: 0 for category in DEFAULT_COVERAGE_CATEGORIES}
        uncategorized: list[str] = []
        for case in corpus.cases:
            categories = self.classify(case)
            if not categories:
                uncategorized.append(case.case_id)
                continue
            for category in categories:
                counts[category] = counts.get(category, 0) + 1
                if case.critical:
                    critical[category] = critical.get(category, 0) + 1
        return CoverageSnapshot(
            name=name or f"{corpus.corpus_id}@{corpus.version}",
            corpus_id=corpus.corpus_id,
            corpus_version=corpus.version,
            corpus_fingerprint=corpus.sha256,
            total_cases=len(corpus.cases),
            category_counts=counts,
            critical_counts=critical,
            uncategorized_cases=tuple(uncategorized),
        )

    def compare(
        self,
        previous: CoverageSnapshot,
        current: CoverageSnapshot,
    ) -> list[CoverageDelta]:
        categories = sorted(set(previous.category_counts) | set(current.category_counts))
        return [
            CoverageDelta(
                category=category,
                previous=previous.category_counts.get(category, 0),
                current=current.category_counts.get(category, 0),
            )
            for category in categories
        ]
