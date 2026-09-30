from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import sys
from pathlib import Path

from nexus_os.learning_memory import GuardianLearningEngine, JsonlLearningStore
from nexus_os.swarm import (
    DEFAULT_PARALLELISM,
    MAX_SWARM_GUARDIANS,
    SwarmCoordinator,
    compact_evidence,
)

from .registry import build_provider, list_providers


def _doctor() -> int:
    checks = {
        "python": sys.executable,
        "ollama": shutil.which("ollama"),
        "claude": shutil.which("claude"),
        "codex": shutil.which("codex"),
        "gemini": shutil.which("gemini"),
    }
    print(json.dumps(checks, indent=2))
    return 0


async def _run_swarm(
    provider_name: str,
    model: str | None,
    goal: str,
    guardians: int,
    max_parallel: int,
) -> int:
    provider = build_provider(provider_name, model)
    coordinator = SwarmCoordinator(max_parallel=max_parallel)
    memory_path = Path(os.environ.get("NEXUS_LEARNING_PATH", ".nexus/guardian_learning.jsonl"))
    learning = GuardianLearningEngine(JsonlLearningStore(memory_path))
    prior_lessons = learning.context_for(goal)

    async def worker(spec, mission: str) -> str:
        prompt = (
            "You are one Guardian in a coordinated Nexus Starship Guardians team.\n"
            f"Guardian ID: {spec.guardian_id}\nRole: {spec.role}\n"
            f"Mission: {mission}\nAssignment: {spec.objective}\n\n"
            "Relevant lessons learned from prior missions:\n"
            f"{prior_lessons}\n\n"
            "Return concise, actionable work product for the lead Guardian."
        )
        result = await asyncio.to_thread(provider.generate, prompt)
        return result.text

    async def synthesize(mission: str, results) -> str:
        evidence = compact_evidence(results)
        prompt = (
            "You are the lead Guardian for Nexus Starship Guardians. Synthesize the Guardian work "
            "below into one coherent execution plan. Resolve conflicts, remove duplicates, preserve "
            "important risks, identify dependencies, and finish with verification gates. Do not claim "
            "unverified work is complete.\n\n"
            f"MISSION:\n{mission}\n\nGUARDIAN EVIDENCE:\n{evidence}"
        )
        result = await asyncio.to_thread(provider.generate, prompt)
        return result.text

    report = await coordinator.run(goal, guardians, worker, synthesize)
    failures = sum(1 for result in report.results if not result.ok)
    successes = report.active_guardians - failures
    reliability_score = 10.0 * successes / report.active_guardians

    reflection = ""
    if report.synthesis:
        reflection_prompt = (
            "You are the Reflection Guardian for Nexus Starship Guardians. Distill exactly one "
            "reusable lesson from this mission for future similar work. Focus on process, architecture, "
            "verification, or failure prevention. Do not claim the model changed its own weights.\n\n"
            f"MISSION:\n{goal}\n\nFINAL SYNTHESIS:\n{report.synthesis}\n\n"
            f"GUARDIAN RELIABILITY SCORE: {reliability_score:.2f}/10\n"
        )
        reflected = await asyncio.to_thread(provider.generate, reflection_prompt)
        reflection = reflected.text.strip()
        learning.learn_from_run(
            task=goal,
            deliverable=report.synthesis,
            score=reliability_score,
            critique=(
                f"{failures} Guardian calls failed; {successes} completed successfully."
                if failures
                else "All Guardian calls completed successfully."
            ),
            rounds=1,
            distilled_lesson=reflection,
            metadata={
                "provider": provider_name,
                "model": model or "",
                "requested_guardians": str(report.requested_guardians),
            },
        )

    print(
        json.dumps(
            {
                "requested_guardians": report.requested_guardians,
                "active_guardians": report.active_guardians,
                "max_parallel": report.max_parallel,
                "successful_guardians": successes,
                "failed_guardians": failures,
                "learning_memory": str(memory_path),
                "reliability_score": round(reliability_score, 2),
            },
            indent=2,
        )
    )
    if report.synthesis:
        print("\n=== NEXUS STARSHIP GUARDIANS SWARM SYNTHESIS ===\n")
        print(report.synthesis)
    if reflection:
        print("\n=== LEARNED LESSON ===\n")
        print(reflection)
    return 0 if failures < report.active_guardians else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="nexus-guardians",
        description="Nexus Starship Guardians portable runtime",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("providers", help="List built-in portable providers")
    sub.add_parser("doctor", help="Detect local model/coding CLIs")

    ask = sub.add_parser("ask", help="Send one prompt through a portable provider")
    ask.add_argument("--provider", required=True, choices=list_providers())
    ask.add_argument("--model")
    ask.add_argument("prompt", nargs="+")

    swarm = sub.add_parser("swarm", help="Run a coordinated team of up to 200 logical Guardians")
    swarm.add_argument("--provider", required=True, choices=list_providers())
    swarm.add_argument("--model")
    swarm.add_argument(
        "--guardians",
        type=int,
        default=24,
        choices=range(1, MAX_SWARM_GUARDIANS + 1),
        help="Number of logical Guardians to coordinate",
    )
    swarm.add_argument("--max-parallel", type=int, default=DEFAULT_PARALLELISM)
    swarm.add_argument("goal", nargs="+")

    args = parser.parse_args()
    if args.command == "providers":
        print("\n".join(list_providers()))
        return 0
    if args.command == "doctor":
        return _doctor()
    if args.command == "ask":
        provider = build_provider(args.provider, args.model)
        result = provider.generate(" ".join(args.prompt))
        print(result.text)
        return 0
    if args.command == "swarm":
        return asyncio.run(
            _run_swarm(
                args.provider,
                args.model,
                " ".join(args.goal),
                args.guardians,
                args.max_parallel,
            )
        )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
