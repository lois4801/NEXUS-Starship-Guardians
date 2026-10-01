from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ModelProfile:
    model_id: str
    provider: str
    task_categories: frozenset[str]


@dataclass(slots=True)
class ModelMetrics:
    attempts: int = 0
    successes: int = 0
    total_score: float = 0.0
    total_cost: float = 0.0
    total_latency_seconds: float = 0.0

    @property
    def success_rate(self) -> float:
        return self.successes / self.attempts if self.attempts else 0.0

    @property
    def average_score(self) -> float:
        return self.total_score / self.attempts if self.attempts else 0.0

    @property
    def average_cost(self) -> float:
        return self.total_cost / self.attempts if self.attempts else 0.0

    @property
    def average_latency(self) -> float:
        return self.total_latency_seconds / self.attempts if self.attempts else 0.0


@dataclass(slots=True)
class RegisteredModel:
    profile: ModelProfile
    metrics_by_task: dict[str, ModelMetrics] = field(default_factory=dict)


class ModelRegistry:
    """Track verified model performance by task category instead of hard-coded model rankings."""

    def __init__(self) -> None:
        self._models: dict[str, RegisteredModel] = {}

    def register(self, profile: ModelProfile) -> None:
        if not profile.model_id.strip():
            raise ValueError("model_id cannot be empty")
        if profile.model_id in self._models:
            raise ValueError(f"model already registered: {profile.model_id}")
        self._models[profile.model_id] = RegisteredModel(profile)

    def record_outcome(
        self,
        model_id: str,
        *,
        task_category: str,
        success: bool,
        score: float,
        cost: float = 0.0,
        latency_seconds: float = 0.0,
    ) -> None:
        if not 0 <= score <= 10:
            raise ValueError("score must be between 0 and 10")
        item = self._models[model_id]
        metrics = item.metrics_by_task.setdefault(task_category, ModelMetrics())
        metrics.attempts += 1
        metrics.successes += int(success)
        metrics.total_score += score
        metrics.total_cost += max(0.0, cost)
        metrics.total_latency_seconds += max(0.0, latency_seconds)

    @staticmethod
    def _utility(metrics: ModelMetrics) -> float:
        if not metrics.attempts:
            return 5.0
        quality = metrics.average_score
        reliability = metrics.success_rate * 10
        cost_penalty = min(metrics.average_cost, 10.0) * 0.10
        latency_penalty = min(metrics.average_latency / 60.0, 10.0) * 0.10
        return (quality * 0.55) + (reliability * 0.45) - cost_penalty - latency_penalty

    def rank(self, task_category: str) -> tuple[RegisteredModel, ...]:
        candidates = [
            item
            for item in self._models.values()
            if task_category in item.profile.task_categories or "general" in item.profile.task_categories
        ]
        return tuple(
            sorted(
                candidates,
                key=lambda item: self._utility(item.metrics_by_task.get(task_category, ModelMetrics())),
                reverse=True,
            )
        )
