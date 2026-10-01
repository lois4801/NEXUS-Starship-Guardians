from __future__ import annotations

from nexus_os.benchmark_vault import GuardianBenchmarkVault
from nexus_os.failure_taxonomy import FailureCategory
from nexus_os.regression_bridge import RegressionLearningBridge
from nexus_os.regression_corpus import RegressionCorpus


def test_verified_failure_becomes_regression_case(tmp_path):
    corpus = RegressionCorpus(tmp_path / "regressions.jsonl")
    bridge = RegressionLearningBridge(corpus)

    capture = bridge.capture(
        title="Login regression",
        task="Authenticate a valid user",
        expected="Valid credentials return success",
        error="assert expected 200 but got 500",
        verified=True,
        provenance="pytest:test_login",
        tags=("auth",),
    )

    assert capture is not None
    assert capture.failure.category == FailureCategory.CORRECTNESS
    assert capture.benchmark_candidate is None
    records = corpus.records()
    assert len(records) == 1
    assert records[0].provenance == "pytest:test_login"


def test_verified_failure_is_automatically_nominated_when_vault_is_enabled(tmp_path):
    corpus = RegressionCorpus(tmp_path / "regressions.jsonl")
    vault = GuardianBenchmarkVault(tmp_path / "benchmark-vault")
    bridge = RegressionLearningBridge(corpus, benchmark_vault=vault)

    capture = bridge.capture(
        title="Deployment evidence regression",
        task="Verify a deployment before claiming completion",
        expected="Authenticated deployment evidence must exist",
        error="assert expected deployment evidence but evidence was missing",
        verified=True,
        provenance="ci:deployment-verification",
        tags=("deployment",),
        evidence_ref="sha256:deployment-evidence-001",
    )

    assert capture is not None
    assert capture.benchmark_candidate is not None
    assert capture.benchmark_candidate.status == "candidate"
    assert capture.benchmark_candidate.evidence_ref == "sha256:deployment-evidence-001"
    assert "verified-regression" in capture.benchmark_candidate.tags
    assert len(vault.candidates()) == 1


def test_vault_enabled_capture_requires_evidence_reference(tmp_path):
    corpus = RegressionCorpus(tmp_path / "regressions.jsonl")
    vault = GuardianBenchmarkVault(tmp_path / "benchmark-vault")
    bridge = RegressionLearningBridge(corpus, benchmark_vault=vault)

    try:
        bridge.capture(
            title="Missing evidence reference",
            task="Do verified work",
            expected="Evidence is linked",
            error="failed assertion",
            verified=True,
            provenance="ci",
        )
    except ValueError as exc:
        assert "evidence_ref" in str(exc)
    else:
        raise AssertionError("vault-enabled capture should require evidence_ref")


def test_unverified_failure_is_not_promoted_to_regression(tmp_path):
    corpus = RegressionCorpus(tmp_path / "regressions.jsonl")
    bridge = RegressionLearningBridge(corpus)

    capture = bridge.capture(
        title="Unverified suspicion",
        task="Do work",
        expected="Work succeeds",
        error="maybe failed",
        verified=False,
        provenance="guardian-guess",
    )

    assert capture is None
    assert corpus.records() == []


def test_duplicate_verified_failure_is_deduplicated(tmp_path):
    corpus = RegressionCorpus(tmp_path / "regressions.jsonl")
    bridge = RegressionLearningBridge(corpus)
    kwargs = {
        "title": "Same failure",
        "task": "Build project",
        "expected": "Build passes",
        "error": "failed assertion",
        "verified": True,
        "provenance": "ci",
    }
    first = bridge.capture(**kwargs)
    second = bridge.capture(**kwargs)

    assert first is not None and second is not None
    assert first.case.case_id == second.case.case_id
    assert len(corpus.records()) == 1
