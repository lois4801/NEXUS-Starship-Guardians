from nexus_os.evaluation_lab import EvaluationCase, EvaluationOutcome, EvaluationRun, GuardianIntelligenceLab
from nexus_os.strategy_tournament import StrategyTournament


def test_tournament_orders_safer_higher_quality_strategy_first():
    cases = [EvaluationCase("critical", "security task", critical=True)]
    weaker = EvaluationRun("weaker", [EvaluationOutcome("critical", False, 9.5)])
    stronger = EvaluationRun("stronger", [EvaluationOutcome("critical", True, 9.0)])
    entries = StrategyTournament(GuardianIntelligenceLab()).summarize(
        [weaker, stronger], cases
    )
    assert entries[0].strategy == "stronger"
