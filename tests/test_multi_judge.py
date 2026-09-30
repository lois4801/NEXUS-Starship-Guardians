from nexus_os.multi_judge import JudgeKind, JudgeResult, MultiJudgeReport


def test_multi_judge_requires_deterministic_and_evidence_judges():
    report = MultiJudgeReport()
    report.add(JudgeResult("tests", JudgeKind.DETERMINISTIC, 10, True))
    assert not report.passed
    report.add(JudgeResult("evidence", JudgeKind.EVIDENCE, 9, True))
    assert report.passed


def test_critical_failure_blocks_report():
    report = MultiJudgeReport()
    report.add(JudgeResult("tests", JudgeKind.DETERMINISTIC, 10, True))
    report.add(JudgeResult("evidence", JudgeKind.EVIDENCE, 10, True))
    report.add(JudgeResult("security", JudgeKind.GUARDIAN, 2, False, critical=True))
    assert not report.passed
    assert report.critical_failures == 1
