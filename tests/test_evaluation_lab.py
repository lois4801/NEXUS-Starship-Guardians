from nexus_os.evaluation_lab import EvaluationCase, EvaluationOutcome, GuardianIntelligenceLab
from nexus_os.promotion_gate import PromotionPolicy


def test_evaluation_lab_compares_baseline_and_candidate():
    lab = GuardianIntelligenceLab()
    cases = [
        EvaluationCase("a", "task a", critical=True),
        EvaluationCase("b", "task b"),
    ]

    def executor(strategy, case):
        if strategy == "candidate":
            return EvaluationOutcome(case.case_id, True, 9.0)
        passed = case.case_id != "b"
        return EvaluationOutcome(case.case_id, passed, 8.0 if passed else 6.0)

    baseline = lab.run("baseline", cases, executor)
    candidate = lab.run("candidate", cases, executor)
    decision = lab.compare(
        baseline=baseline,
        candidate=candidate,
        cases=cases,
        policy=PromotionPolicy(minimum_pass_rate=0.5),
    )
    assert decision.promote
    assert candidate.summary(cases).pass_rate == 1.0


def test_evaluation_lab_adds_failure_signal():
    lab = GuardianIntelligenceLab()
    case = EvaluationCase("x", "must be correct")

    def executor(strategy, item):
        return EvaluationOutcome(item.case_id, False, 2.0, critique="incorrect result")

    run = lab.run("candidate", [case], executor)
    assert run.outcomes[0].failure is not None
