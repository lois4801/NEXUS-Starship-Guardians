import json

import pytest

from nexus_os.evaluation_lab import EvaluationOutcome, GuardianIntelligenceLab
from nexus_os.fixed_corpus import CORE_CORPUS_SHA256, FixedEvaluationCorpus
from nexus_os.promotion_gate import PromotionPolicy


def test_core_corpus_is_locked_versioned_and_packaged():
    corpus = FixedEvaluationCorpus.load_core()
    assert corpus.corpus_id == "guardian-intelligence-lab-core"
    assert corpus.version == "1.0.0"
    assert corpus.sha256 == CORE_CORPUS_SHA256
    assert len(corpus.cases) == 8
    assert sum(case.critical for case in corpus.cases) == 7


def test_fixed_corpus_detects_tampering(tmp_path):
    payload = FixedEvaluationCorpus.load_core().canonical_payload()
    payload["cases"][0]["expected"] = "Silently claim deployment succeeded."
    tampered = tmp_path / "tampered.json"
    tampered.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="fingerprint mismatch"):
        FixedEvaluationCorpus.load(tampered, expected_sha256=CORE_CORPUS_SHA256)


def test_fixed_corpus_rejects_duplicate_case_ids():
    payload = FixedEvaluationCorpus.load_core().canonical_payload()
    payload["cases"][1]["case_id"] = payload["cases"][0]["case_id"]

    with pytest.raises(ValueError, match="duplicate case IDs"):
        FixedEvaluationCorpus.from_mapping(payload)


def test_lab_binds_baseline_and_candidate_to_same_corpus():
    corpus = FixedEvaluationCorpus.load_core()
    lab = GuardianIntelligenceLab()

    def executor(strategy, case):
        score = 9.5 if strategy == "candidate" else 9.0
        return EvaluationOutcome(case.case_id, True, score, latency_seconds=0.01)

    baseline = lab.run_fixed("baseline", corpus, executor)
    candidate = lab.run_fixed("candidate", corpus, executor)
    decision = lab.compare_fixed(
        baseline=baseline,
        candidate=candidate,
        corpus=corpus,
        policy=PromotionPolicy(minimum_pass_rate=1.0, minimum_score_delta=0.1),
    )

    assert decision.promote
    assert baseline.corpus_fingerprint == CORE_CORPUS_SHA256
    assert candidate.corpus_fingerprint == CORE_CORPUS_SHA256


def test_lab_blocks_unbound_or_mismatched_runs():
    corpus = FixedEvaluationCorpus.load_core()
    lab = GuardianIntelligenceLab()

    def executor(strategy, case):
        return EvaluationOutcome(case.case_id, True, 9.0, latency_seconds=0.01)

    baseline = lab.run_fixed("baseline", corpus, executor)
    candidate = lab.run("candidate", corpus.cases, executor)
    decision = lab.compare_fixed(baseline=baseline, candidate=candidate, corpus=corpus)

    assert not decision.promote
    assert any("candidate run" in reason for reason in decision.reasons)
