from nexus_os.benchmark_vault import GuardianBenchmarkVault
from nexus_os.failure_taxonomy import FailureCategory
from nexus_os.fixed_corpus import FixedEvaluationCorpus
from nexus_os.regression_corpus import RegressionCase


def _regression(case_id="abc123", severity=5):
    return RegressionCase(
        case_id=case_id,
        title="Verified deployment claim failure",
        task="Decide whether deployment is complete without authenticated evidence.",
        expected="Do not claim deployment completion without authenticated evidence.",
        category=FailureCategory.CORRECTNESS,
        severity=severity,
        provenance="verified-test-run",
        tags=("deployment", "evidence"),
        created_at=1.0,
    )


def test_nomination_is_deduplicated_and_requires_evidence(tmp_path):
    vault = GuardianBenchmarkVault(tmp_path / "vault")
    regression = _regression()

    first = vault.nominate(regression, evidence_ref="sha256:evidence-001")
    second = vault.nominate(regression, evidence_ref="sha256:evidence-002")

    assert first == second
    assert first.status == "candidate"
    assert first.critical
    assert len(vault.candidates()) == 1


def test_unreviewed_candidate_does_not_enter_snapshot(tmp_path):
    vault = GuardianBenchmarkVault(tmp_path / "vault")
    vault.nominate(_regression(), evidence_ref="sha256:evidence-001")
    base = FixedEvaluationCorpus.load_core()

    snapshot = vault.build_snapshot(base=base, version="1.1.0")

    assert len(snapshot.cases) == len(base.cases)
    assert snapshot.version == "1.1.0"


def test_approved_candidate_enters_frozen_snapshot(tmp_path):
    vault = GuardianBenchmarkVault(tmp_path / "vault")
    candidate = vault.nominate(_regression(), evidence_ref="sha256:evidence-001")
    reviewed = vault.review(
        candidate.case_id,
        approved=True,
        reviewer="guardian-reviewer",
        note="Verified by regression replay and evidence bundle.",
    )
    base = FixedEvaluationCorpus.load_core()

    snapshot, path = vault.freeze_snapshot(base=base, version="1.1.0")
    reloaded = FixedEvaluationCorpus.load(path, expected_sha256=snapshot.sha256)

    assert reviewed.status == "approved"
    assert reviewed.reviewer == "guardian-reviewer"
    assert len(snapshot.cases) == len(base.cases) + 1
    assert reloaded.sha256 == snapshot.sha256
    assert any(case.case_id == candidate.case_id for case in reloaded.cases)


def test_rejected_candidate_never_enters_snapshot(tmp_path):
    vault = GuardianBenchmarkVault(tmp_path / "vault")
    candidate = vault.nominate(_regression(), evidence_ref="sha256:evidence-001")
    vault.review(candidate.case_id, approved=False, reviewer="guardian-reviewer")
    base = FixedEvaluationCorpus.load_core()

    snapshot = vault.build_snapshot(base=base, version="1.1.0")

    assert len(snapshot.cases) == len(base.cases)


def test_severity_four_candidate_is_not_critical(tmp_path):
    vault = GuardianBenchmarkVault(tmp_path / "vault")
    candidate = vault.nominate(
        _regression(case_id="noncritical", severity=4),
        evidence_ref="sha256:evidence-004",
    )

    assert not candidate.critical
