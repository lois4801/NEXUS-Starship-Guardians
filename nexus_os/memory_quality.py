from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MemoryQuality:
    memory_id: str
    successful_reuses: int = 0
    harmful_reuses: int = 0
    neutral_reuses: int = 0
    confidence: float = 0.5
    quarantined: bool = False

    @property
    def usefulness(self) -> float:
        total = self.successful_reuses + self.harmful_reuses + self.neutral_reuses
        if not total:
            return self.confidence
        observed = (self.successful_reuses - self.harmful_reuses) / total
        normalized = (observed + 1) / 2
        return max(0.0, min(1.0, (normalized * 0.8) + (self.confidence * 0.2)))


class MemoryQualityRegistry:
    """Track whether retrieved lessons improve verified outcomes."""

    def __init__(self, *, quarantine_threshold: float = 0.3, minimum_observations: int = 3) -> None:
        self.quarantine_threshold = quarantine_threshold
        self.minimum_observations = minimum_observations
        self._items: dict[str, MemoryQuality] = {}

    def register(self, memory_id: str, *, confidence: float = 0.5) -> MemoryQuality:
        if not memory_id.strip():
            raise ValueError("memory_id cannot be empty")
        if not 0 <= confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        item = MemoryQuality(memory_id=memory_id, confidence=confidence)
        self._items[memory_id] = item
        return item

    def record_reuse(self, memory_id: str, outcome: str) -> MemoryQuality:
        item = self._items[memory_id]
        if outcome == "helpful":
            item.successful_reuses += 1
        elif outcome == "harmful":
            item.harmful_reuses += 1
        elif outcome == "neutral":
            item.neutral_reuses += 1
        else:
            raise ValueError("outcome must be helpful, harmful, or neutral")
        observations = item.successful_reuses + item.harmful_reuses + item.neutral_reuses
        if observations >= self.minimum_observations and item.usefulness < self.quarantine_threshold:
            item.quarantined = True
        return item

    def eligible(self, memory_id: str) -> bool:
        return not self._items[memory_id].quarantined
