from __future__ import annotations

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
    records = corpus.records()
    assert len(records) == 1
    assert records[0].provenance == "pytest:test_login"


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
