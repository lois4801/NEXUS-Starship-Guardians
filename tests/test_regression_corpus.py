from nexus_os.failure_taxonomy import FailureCategory, FailureSignal
from nexus_os.regression_corpus import RegressionCorpus


def test_regression_corpus_deduplicates_cases(tmp_path):
    corpus = RegressionCorpus(tmp_path / "regressions.jsonl")
    failure = FailureSignal(FailureCategory.CORRECTNESS, "wrong output", 4)
    first = corpus.add(
        title="Login regression",
        task="login with valid credentials",
        expected="login succeeds",
        failure=failure,
        provenance="run-1",
    )
    second = corpus.add(
        title="Same regression",
        task="login with valid credentials",
        expected="login succeeds",
        failure=failure,
        provenance="run-2",
    )
    assert first.case_id == second.case_id
    assert len(corpus.records()) == 1


def test_critical_regressions_are_queryable(tmp_path):
    corpus = RegressionCorpus(tmp_path / "regressions.jsonl")
    corpus.add(
        title="Secret leak",
        task="render config",
        expected="no credentials",
        failure=FailureSignal(FailureCategory.SAFETY, "secret exposed", 5),
        provenance="security-run",
    )
    assert len(corpus.critical()) == 1
