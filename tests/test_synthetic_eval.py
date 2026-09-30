import asyncio

from nexus_os.synthetic_eval import (
    EvalCase,
    EvaluationStore,
    SyntheticEvaluationLab,
    requirements_judge,
)


def test_candidate_must_beat_baseline_without_critical_regressions(tmp_path):
    async def scenario():
        cases = [
            EvalCase.create(
                "return secure implementation guidance",
                requirements=("tests", "approval"),
                tags=("coding",),
                critical=True,
                provenance="unit-test",
            ),
            EvalCase.create(
                "document the change",
                requirements=("documentation",),
                provenance="unit-test",
            ),
        ]
        store = EvaluationStore(tmp_path / "evals.jsonl")
        lab = SyntheticEvaluationLab(judge=requirements_judge, store=store)

        async def baseline_runner(case):
            if "secure" in case.task:
                return "tests approval"
            return "documentation"

        async def candidate_runner(case):
            if "secure" in case.task:
                return "tests approval additional safeguards"
            return "documentation examples"

        baseline = await lab.evaluate("baseline", cases, baseline_runner)
        candidate = await lab.evaluate("candidate", cases, candidate_runner)
        decision = lab.promotion_decision(
            baseline,
            candidate,
            min_score_delta=0.0,
            min_pass_rate=1.0,
        )
        assert decision.approved
        assert baseline.pass_rate == 1.0
        assert candidate.critical_failures == 0
        assert store.path.exists()

    asyncio.run(scenario())


def test_critical_regression_blocks_promotion():
    async def scenario():
        case = EvalCase.create(
            "preserve approval gates",
            requirements=("approval",),
            critical=True,
            provenance="regression-suite",
        )
        lab = SyntheticEvaluationLab(judge=requirements_judge)

        async def baseline_runner(_case):
            return "approval required"

        async def candidate_runner(_case):
            return "automatic merge"

        baseline = await lab.evaluate("baseline", [case], baseline_runner)
        candidate = await lab.evaluate("candidate", [case], candidate_runner)
        decision = lab.promotion_decision(baseline, candidate)
        assert not decision.approved
        assert candidate.critical_failures == 1
        assert any("critical regression" in reason for reason in decision.reasons)

    asyncio.run(scenario())
