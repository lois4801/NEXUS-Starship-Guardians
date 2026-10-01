from __future__ import annotations

from dataclasses import dataclass

from .adversarial_eval import AdversarialCase, AdversarialCaseGenerator
from .mission_classifier import MissionClassification, MissionClassifier
from .strategy_engine import StrategyEngine, StrategyPlan


@dataclass(frozen=True, slots=True)
class IntelligencePlan:
    mission: str
    classification: MissionClassification
    strategy: StrategyPlan
    adversarial_cases: tuple[AdversarialCase, ...]
    assumptions: tuple[str, ...]
    uncertainty: float


class IntelligenceFabric:
    """Compose mission classification, strategy selection, adversarial checks, and uncertainty."""

    def __init__(
        self,
        classifier: MissionClassifier | None = None,
        strategy_engine: StrategyEngine | None = None,
        adversarial_generator: AdversarialCaseGenerator | None = None,
    ) -> None:
        self.classifier = classifier or MissionClassifier()
        self.strategy_engine = strategy_engine or StrategyEngine()
        self.adversarial_generator = adversarial_generator or AdversarialCaseGenerator()

    def plan(self, mission: str) -> IntelligencePlan:
        classification = self.classifier.classify(mission)
        strategy = self.strategy_engine.choose(classification)
        adversarial = self.adversarial_generator.generate(mission)
        assumptions: list[str] = []
        if classification.confidence < 0.75:
            assumptions.append("mission interpretation should be confirmed before consequential execution")
        if not classification.requirements.tools:
            assumptions.append("no high-level external tool requirement was inferred")
        uncertainty = round(max(0.0, min(1.0, 1.0 - classification.confidence)), 2)
        return IntelligencePlan(
            mission=mission,
            classification=classification,
            strategy=strategy,
            adversarial_cases=adversarial,
            assumptions=tuple(assumptions),
            uncertainty=uncertainty,
        )
