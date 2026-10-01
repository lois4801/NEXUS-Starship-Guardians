from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class GuardianProfile:
    guardian_id: str
    role: str
    capabilities: frozenset[str]
    allowed_tools: frozenset[str] = frozenset()
    preferred_models: tuple[str, ...] = ()


@dataclass(slots=True)
class GuardianMetrics:
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
    def average_latency_seconds(self) -> float:
        return self.total_latency_seconds / self.attempts if self.attempts else 0.0


@dataclass(slots=True)
class RegisteredGuardian:
    profile: GuardianProfile
    metrics: GuardianMetrics = field(default_factory=GuardianMetrics)


class GuardianRegistry:
    def __init__(self) -> None:
        self._items: dict[str, RegisteredGuardian] = {}

    def register(self, profile: GuardianProfile) -> None:
        if not profile.guardian_id.strip():
            raise ValueError("guardian_id cannot be empty")
        if profile.guardian_id in self._items:
            raise ValueError(f"guardian already registered: {profile.guardian_id}")
        self._items[profile.guardian_id] = RegisteredGuardian(profile)

    def get(self, guardian_id: str) -> RegisteredGuardian:
        try:
            return self._items[guardian_id]
        except KeyError as exc:
            raise KeyError(f"unknown Guardian: {guardian_id}") from exc

    def all(self) -> list[RegisteredGuardian]:
        """Return a snapshot of all registered Guardians."""
        return list(self._items.values())

    def record_outcome(
        self,
        guardian_id: str,
        *,
        success: bool,
        score: float,
        cost: float = 0.0,
        latency_seconds: float = 0.0,
    ) -> None:
        if not 0 <= score <= 10:
            raise ValueError("score must be between 0 and 10")
        item = self.get(guardian_id)
        metrics = item.metrics
        metrics.attempts += 1
        metrics.successes += int(success)
        metrics.total_score += score
        metrics.total_cost += max(0.0, cost)
        metrics.total_latency_seconds += max(0.0, latency_seconds)

    def eligible(
        self,
        *,
        required_capabilities: frozenset[str] = frozenset(),
        required_tools: frozenset[str] = frozenset(),
    ) -> list[RegisteredGuardian]:
        return [
            item
            for item in self._items.values()
            if required_capabilities.issubset(item.profile.capabilities)
            and required_tools.issubset(item.profile.allowed_tools)
        ]

    @staticmethod
    def utility(item: RegisteredGuardian) -> float:
        metrics = item.metrics
        if not metrics.attempts:
            return 5.0
        quality = metrics.average_score
        reliability = metrics.success_rate * 10
        cost_penalty = min(metrics.average_cost, 10.0) * 0.10
        latency_penalty = min(metrics.average_latency_seconds / 60.0, 10.0) * 0.10
        return (quality * 0.55) + (reliability * 0.45) - cost_penalty - latency_penalty

    def select(
        self,
        *,
        required_capabilities: frozenset[str] = frozenset(),
        required_tools: frozenset[str] = frozenset(),
        limit: int = 8,
    ) -> list[RegisteredGuardian]:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        candidates = self.eligible(
            required_capabilities=required_capabilities,
            required_tools=required_tools,
        )
        return sorted(candidates, key=self.utility, reverse=True)[:limit]
