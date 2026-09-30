from __future__ import annotations

import asyncio
import os
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

MAX_SWARM_GUARDIANS = 200
MAX_SWARM_AGENTS = MAX_SWARM_GUARDIANS  # compatibility alias
DEFAULT_PARALLELISM = max(2, min(16, (os.cpu_count() or 4) * 2))

ROLE_FAMILIES = (
    "orchestrator", "architect", "frontend", "backend", "api", "database",
    "security", "devops", "qa", "test", "debug", "performance", "ux",
    "ui", "accessibility", "research", "evidence", "reality-check", "docs",
    "product", "requirements", "integration", "release", "observability",
    "risk", "data", "ai-engineering", "prompt", "code-review", "refactor",
    "dependency", "migration", "infra", "network", "container", "ci-cd",
    "automation", "support", "analytics", "compliance",
)


@dataclass(slots=True)
class GuardianSpec:
    guardian_id: str
    role: str
    objective: str

    @property
    def agent_id(self) -> str:
        """Compatibility alias for integrations written before Guardian terminology."""
        return self.guardian_id


@dataclass(slots=True)
class GuardianResult:
    guardian_id: str
    role: str
    output: str
    ok: bool = True
    error: str | None = None

    @property
    def agent_id(self) -> str:
        """Compatibility alias for integrations written before Guardian terminology."""
        return self.guardian_id


# Backward-compatible Python aliases. New code should use GuardianSpec/GuardianResult.
AgentSpec = GuardianSpec
AgentResult = GuardianResult


@dataclass(slots=True)
class SwarmReport:
    goal: str
    requested_guardians: int
    active_guardians: int
    max_parallel: int
    results: list[GuardianResult] = field(default_factory=list)
    synthesis: str | None = None

    @property
    def requested_agents(self) -> int:
        return self.requested_guardians

    @property
    def active_agents(self) -> int:
        return self.active_guardians


Worker = Callable[[GuardianSpec, str], Awaitable[str]]
Synthesizer = Callable[[str, list[GuardianResult]], Awaitable[str]]


def build_team(goal: str, requested_guardians: int) -> list[GuardianSpec]:
    """Build up to 200 logical Guardians with deterministic, diverse roles."""
    if not 1 <= requested_guardians <= MAX_SWARM_GUARDIANS:
        raise ValueError(
            f"requested_guardians must be between 1 and {MAX_SWARM_GUARDIANS}"
        )
    team: list[GuardianSpec] = []
    for index in range(requested_guardians):
        role = ROLE_FAMILIES[index % len(ROLE_FAMILIES)]
        replica = index // len(ROLE_FAMILIES) + 1
        team.append(
            GuardianSpec(
                guardian_id=f"{role}-{replica:02d}",
                role=role,
                objective=(
                    f"Analyze the goal from the {role} perspective. Produce concrete findings, "
                    "risks, dependencies, implementation steps, and verification evidence. "
                    "Do not duplicate generic advice from other roles."
                ),
            )
        )
    return team


class SwarmCoordinator:
    """Run a large Guardian team with bounded physical concurrency.

    A swarm may contain up to 200 Guardians, while max_parallel limits simultaneous
    model/process calls so a laptop or local model server is not overwhelmed.
    """

    def __init__(self, *, max_parallel: int = DEFAULT_PARALLELISM):
        if max_parallel < 1 or max_parallel > MAX_SWARM_GUARDIANS:
            raise ValueError(f"max_parallel must be between 1 and {MAX_SWARM_GUARDIANS}")
        self.max_parallel = max_parallel

    async def run(
        self,
        goal: str,
        requested_guardians: int,
        worker: Worker,
        synthesizer: Synthesizer | None = None,
    ) -> SwarmReport:
        team = build_team(goal, requested_guardians)
        semaphore = asyncio.Semaphore(self.max_parallel)

        async def execute(spec: GuardianSpec) -> GuardianResult:
            async with semaphore:
                try:
                    output = await worker(spec, goal)
                    return GuardianResult(spec.guardian_id, spec.role, output)
                except Exception as exc:  # noqa: BLE001 - isolate one worker from the swarm
                    return GuardianResult(
                        spec.guardian_id,
                        spec.role,
                        "",
                        ok=False,
                        error=f"{type(exc).__name__}: {exc}",
                    )

        results = await asyncio.gather(*(execute(spec) for spec in team))
        report = SwarmReport(
            goal=goal,
            requested_guardians=requested_guardians,
            active_guardians=len(team),
            max_parallel=self.max_parallel,
            results=list(results),
        )
        if synthesizer:
            successful = [result for result in report.results if result.ok]
            report.synthesis = await synthesizer(goal, successful)
        return report


def compact_evidence(results: list[GuardianResult], *, max_chars: int = 48000) -> str:
    """Create a bounded synthesis payload from successful Guardian outputs."""
    chunks: list[str] = []
    used = 0
    for result in results:
        if not result.ok or not result.output.strip():
            continue
        chunk = f"[{result.guardian_id} | {result.role}]\n{result.output.strip()}\n"
        if used + len(chunk) > max_chars:
            break
        chunks.append(chunk)
        used += len(chunk)
    return "\n".join(chunks)
