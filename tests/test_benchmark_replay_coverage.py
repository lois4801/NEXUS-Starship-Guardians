from nexus_os.benchmark_replay import BenchmarkReplayEngine
from nexus_os.benchmark_vault import GuardianBenchmarkVault
from nexus_os.coverage_intelligence import CoverageIntelligence
from nexus_os.evaluation_lab import EvaluationOutcome
from nexus_os.failure_taxonomy import FailureCategory
from nexus_os.fixed_corpus import FixedEvaluationCorpus
from nexus_os.regression_corpus import RegressionCase


def test_benchmark_replay_updates_vault_evidence(tmp_path):
    vault = GuardianBenchmarkVault(tmp_path / "vault")
    regression = RegressionCase(
        case_id="reg-1",
        title="API regression",
        task="Verify the API does not claim success without evidence.",
        expected="Require verification evidence.",
        category=FailureCategory.REGRESSION,
        severity=5,
        provenance="test",
        tags=("api", "verification"),
    )
    candidate = vault.nominate(regression, evidence_ref="evidence://run/1")

    def executor(strategy, case):
        passed = strategy == "candidate"
        return EvaluationOutcome(
            case_id=case.case_id,
            passed=passed,
            score=9.0 if passed else 4.0,
            critique="failed expected verification" if not passed else "",
            latency_seconds=0.01,
        )

    report = BenchmarkReplayEngine().replay_candidate(
        candidate,
        strategies=("baseline", "candidate"),
        executor=executor,
        vault=vault,
    )
    assert report.replay_count == 2
    assert report.reproduced_failure
    assert report.pass_rate == 0.5

    stored = vault.candidates()[0]
    assert stored.replay_count == 2
    assert stored.replay_passes == 1
    assert stored.replay_failures == 1
    assert stored.replayed


def test_review_can_require_replay_before_approval(tmp_path):
    vault = GuardianBenchmarkVault(tmp_path / "vault")
    regression = RegressionCase(
        case_id="reg-2",
        title="Cloud rollback regression",
        task="Require rollback evidence before production schema promotion.",
        expected="Block promotion without rollback evidence.",
        category=FailureCategory.RELIABILITY,
        severity=5,
        provenance="test",
        tags=("cloud", "deployment", "database"),
    )
    candidate = vault.nominate(regression, evidence_ref="evidence://run/2")

    try:
        vault.review(
            candidate.case_id,
            approved=True,
            reviewer="guardian-review",
            require_replay=True,
        )
    except ValueError as exc:
        assert "replay" in str(exc)
    else:
        raise AssertionError("approval should be blocked when replay is required but absent")


def test_coverage_intelligence_measures_specialist_domains():
    corpus = FixedEvaluationCorpus.from_mapping(
        {
            "schema_version": 1,
            "corpus_id": "coverage-test",
            "version": "1.0.0",
            "description": "coverage test",
            "cases": [
                {
                    "case_id": "api-1",
                    "task": "Verify API authentication and contract behavior.",
                    "expected": "Secure API contract.",
                    "critical": True,
                    "provenance": "test",
                    "tags": ["api", "security"],
                },
                {
                    "case_id": "code-1",
                    "task": "Debug a coding regression with tests.",
                    "expected": "Repair the regression and verify tests.",
                    "critical": False,
                    "provenance": "test",
                    "tags": ["coding", "debugging", "regression"],
                },
                {
                    "case_id": "cloud-1",
                    "task": "Deploy a container with rollback evidence.",
                    "expected": "Verified cloud deployment.",
                    "critical": True,
                    "provenance": "test",
                    "tags": ["cloud", "deployment"],
                },
            ],
        }
    )

    snapshot = CoverageIntelligence().analyze(corpus)
    assert snapshot.total_cases == 3
    assert snapshot.category_counts["api"] >= 1
    assert snapshot.category_counts["security"] >= 1
    assert snapshot.category_counts["coding"] >= 1
    assert snapshot.category_counts["debugging"] >= 1
    assert snapshot.category_counts["cloud"] >= 1
    assert snapshot.category_counts["deployment"] >= 1
    assert snapshot.critical_counts["api"] == 1


def test_coverage_comparison_shows_snapshot_growth():
    intelligence = CoverageIntelligence()
    previous = FixedEvaluationCorpus.from_mapping(
        {
            "schema_version": 1,
            "corpus_id": "coverage-growth",
            "version": "1.0.0",
            "description": "previous",
            "cases": [
                {
                    "case_id": "code-1",
                    "task": "Coding test.",
                    "expected": "Pass.",
                    "critical": False,
                    "provenance": "test",
                    "tags": ["coding"],
                }
            ],
        }
    )
    current = FixedEvaluationCorpus.from_mapping(
        {
            "schema_version": 1,
            "corpus_id": "coverage-growth",
            "version": "1.1.0",
            "description": "current",
            "cases": [
                {
                    "case_id": "code-1",
                    "task": "Coding test.",
                    "expected": "Pass.",
                    "critical": False,
                    "provenance": "test",
                    "tags": ["coding"],
                },
                {
                    "case_id": "api-1",
                    "task": "API test.",
                    "expected": "Pass.",
                    "critical": False,
                    "provenance": "test",
                    "tags": ["api"],
                },
            ],
        }
    )

    deltas = {item.category: item for item in intelligence.compare(
        intelligence.analyze(previous), intelligence.analyze(current)
    )}
    assert deltas["api"].change == 1
    assert deltas["coding"].change == 0
