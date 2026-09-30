from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class ProviderResult:
    text: str
    provider: str
    model: str | None = None


class PortableProvider(Protocol):
    name: str

    def generate(self, prompt: str) -> ProviderResult:
        """Generate one response for a prompt."""
        ...
