from __future__ import annotations

import asyncio
import os
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

MAX_SWARM_AGENTS = 200
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
class AgentSpec:
    agent_id: str
    role: str
    objective: str


@dataclass(slots=True)
class AgentResult:
    agent_id: str
    role: str
    output: str
    ok: bool = True
    error: str | None = None


@dataclass(slots=True)
class SwarmReport:
    goal: str
    requested_agents: int
    active_agents: int
    max_parallel: int
    results: list[AgentResult] = field(default_factory=list)
    synthesis: str | None = None


Worker = Callable[[AgentSpec, str], Awaitable[str]]
Synthesizer = Callable[[str, list[AgentResult]], Awaitable[str]]


def build_team(goal: str, requested_agents: int) -> list[AgentSpec]:
    """Build up to 200 logical specialists with deterministic, diverse roles."""
    if not 1 <= requested_agents <= MAX_SWARM_AGENTS:
        raise ValueError(f"requested_agents must be between 1 and {MAX_SWARM_AGENTS}")
    team: list[AgentSpec] = []
    for index in range(requested_agents):
        role = ROLE_FAMILIES[index % len(ROLE_FAMILIES)]
        replica = index // len(ROLE_FAMILIES) + 1
        team.append(
            AgentSpec(
                agent_id=f"{role}-{replica:02d}",
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
    """Run a large logical team with bounded physical concurrency.

    A swarm may contain up to 200 agents, while max_parallel limits simultaneous
    model/process calls so a laptop or local model server is not overwhelmed.
    """

    def __init__(self, *, max_parallel: int = DEFAULT_PARALLELISM):
        if max_parallel < 1 or max_parallel > MAX_SWARM_AGENTS:
            raise ValueError(f"max_parallel must be between 1 and {MAX_SWARM_AGENTS}")
        self.max_parallel = max_parallel

    async def run(
        self,
        goal: str,
        requested_agents: int,
        worker: Worker,
        synthesizer: Synthesizer | None = None,
    ) -> SwarmReport:
        team = build_team(goal, requested_agents)
        semaphore = asyncio.Semaphore(self.max_parallel)

        async def execute(spec: AgentSpec) -> AgentResult:
            async with semaphore:
                try:
                    output = await worker(spec, goal)
                    return AgentResult(spec.agent_id, spec.role, output)
                except Exception as exc:  # noqa: BLE001 - isolate one worker from the swarm
                    return AgentResult(
                        spec.agent_id,
                        spec.role,
                        "",
                        ok=False,
                        error=f"{type(exc).__name__}: {exc}",
                    )

        results = await asyncio.gather(*(execute(spec) for spec in team))
        report = SwarmReport(
            goal=goal,
            requested_agents=requested_agents,
            active_agents=len(team),
            max_parallel=self.max_parallel,
            results=list(results),
        )
        if synthesizer:
            successful = [result for result in report.results if result.ok]
            report.synthesis = await synthesizer(goal, successful)
        return report


def compact_evidence(results: list[AgentResult], *, max_chars: int = 48000) -> str:
    """Create a bounded synthesis payload from successful specialist outputs."""
    chunks: list[str] = []
    used = 0
    for result in results:
        if not result.ok or not result.output.strip():
            continue
        chunk = f"[{result.agent_id} | {result.role}]\n{result.output.strip()}\n"
        if used + len(chunk) > max_chars:
            break
        chunks.append(chunk)
        used += len(chunk)
    return "\n".join(chunks)
