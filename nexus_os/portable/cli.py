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

from .brainstorm import BRAINSTORM_GUARDIAN_COUNT, run_brainstorm
from .company import (
    COMPANY_BRAINSTORM_GUARDIANS,
    COMPANY_MAX_REVISION_CYCLES,
    COMPANY_REVISE_GUARDIANS,
    GuardianCompany,
)
from .registry import build_provider, list_providers


def _doctor() -> int:
    checks = {
        "python": sys.executable,
        "ollama": shutil.which("ollama"),
        "claude": shutil.which("claude"),
        "codex": shutil.which("codex"),
        "gemini": shutil.which("gemini"),
        "opencode": shutil.which("opencode"),
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
        reflection_prompt = _reflection_prompt(goal, report.synthesis, reliability_score)
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


def _reflection_prompt(goal: str, deliverable: str, score: float) -> str:
    return (
        "You are the Reflection Guardian for Nexus Starship Guardians. Distill exactly one "
        "reusable lesson from this mission for future similar work. Focus on process, architecture, "
        "verification, or failure prevention. Do not claim the model changed its own weights.\n\n"
        f"MISSION:\n{goal}\n\nFINAL SYNTHESIS:\n{deliverable}\n\n"
        f"GUARDIAN RELIABILITY SCORE: {score:.2f}/10\n"
    )


async def _run_brainstorm(
    provider_name: str,
    model: str | None,
    goal: str,
    guardians: int,
    max_parallel: int,
) -> int:
    provider = build_provider(provider_name, model)
    memory_path = Path(os.environ.get("NEXUS_LEARNING_PATH", ".nexus/guardian_learning.jsonl"))
    learning = GuardianLearningEngine(JsonlLearningStore(memory_path))

    report = await run_brainstorm(provider, goal, guardians, max_parallel=max_parallel)

    total_calls = report.active_guardians * 2
    reliability_score = 10.0 * (total_calls - report.total_failures) / total_calls

    print(
        json.dumps(
            {
                "mode": "brainstorm",
                "requested_guardians": report.requested_guardians,
                "active_guardians": report.active_guardians,
                "max_parallel": report.max_parallel,
                "divergent_failures": report.divergent_failures,
                "critique_failures": report.critique_failures,
                "learning_memory": str(memory_path),
                "reliability_score": round(reliability_score, 2),
            },
            indent=2,
        )
    )
    if report.candidate_plan:
        print("\n=== CANDIDATE PLAN (PRE-REVIEW) ===\n")
        print(report.candidate_plan)
    if report.final_plan:
        print("\n=== NEXUS STARSHIP GUARDIANS BRAINSTORM RESULT ===\n")
        print(report.final_plan)
        reflection_prompt = _reflection_prompt(goal, report.final_plan, reliability_score)
        reflected = await asyncio.to_thread(provider.generate, reflection_prompt)
        reflection = reflected.text.strip()
        learning.learn_from_run(
            task=goal,
            deliverable=report.final_plan,
            score=reliability_score,
            critique=(
                f"{report.total_failures} Guardian calls failed across two passes."
                if report.total_failures
                else "All Guardian calls completed successfully across two passes."
            ),
            rounds=2,
            distilled_lesson=reflection,
            metadata={
                "provider": provider_name,
                "model": model or "",
                "mode": "brainstorm",
                "requested_guardians": str(report.requested_guardians),
            },
        )
        print("\n=== LEARNED LESSON ===\n")
        print(reflection)
    return 0 if report.total_failures < total_calls else 1


async def _run_company(
    provider_name: str,
    model: str | None,
    goals: list[str],
    max_parallel: int,
    *,
    execute_size: int | None,
    test_size: int | None,
) -> int:
    provider = build_provider(provider_name, model)
    company = GuardianCompany(max_parallel=max_parallel)
    call = lambda prompt: asyncio.to_thread(provider.generate, prompt)
    report = await company.run_company(
        list(goals),
        lambda prompt: _result_text(call, prompt),
        execute_size=execute_size,
        test_size=test_size,
    )
    leveling = company.leveling_summary()
    missions = []
    for mission in report.missions:
        missions.append(
            {
                "goal": mission.goal,
                "complexity_score": mission.complexity_score,
                "execute_guardians": mission.execute_guardians,
                "test_guardians": mission.test_guardians,
                "revise_guardians": mission.revise_guardians,
                "revision_cycles": mission.revision_cycles,
                "confirmed_defects": mission.confirmed_defects,
                "fast_path_findings": len(mission.fast_path_findings),
                "has_final_output": mission.final_output is not None,
            }
        )
    print(
        json.dumps(
            {
                "mode": "company",
                "provider": provider_name,
                "model": model or "",
                "concurrent_missions": report.missions_run,
                "brainstorm_guardians_per_mission": COMPANY_BRAINSTORM_GUARDIANS,
                "revise_guardians_per_cycle": COMPANY_REVISE_GUARDIANS,
                "max_revision_cycles": COMPANY_MAX_REVISION_CYCLES,
                "missions": missions,
                "leveling": leveling,
            },
            indent=2,
        )
    )
    return 0


async def _result_text(call, prompt: str) -> str:
    result = await call(prompt)
    return result.text


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

    brain = sub.add_parser(
        "brainstorm",
        help="Divergent-convergent brainstorm: ideas, synthesis, red-team critique, refined plan",
    )
    brain.add_argument("--provider", required=True, choices=list_providers())
    brain.add_argument("--model")
    brain.add_argument(
        "--guardians",
        type=int,
        default=BRAINSTORM_GUARDIAN_COUNT,
        choices=range(1, MAX_SWARM_GUARDIANS + 1),
        help="Number of logical Guardians per phase (two phases run; company default 50)",
    )
    brain.add_argument("--max-parallel", type=int, default=DEFAULT_PARALLELISM)
    brain.add_argument("goal", nargs="+")

    company = sub.add_parser(
        "company",
        help=(
            "Run the Guardian Company Runtime: 50 brainstorm, up to 200 execute, "
            "up to 200 test/QC, 200 revise; each positional argument is a separate "
            "task run concurrently"
        ),
    )
    company.add_argument("--provider", required=True, choices=list_providers())
    company.add_argument("--model")
    company.add_argument(
        "--execute-size",
        type=int,
        default=None,
        choices=range(1, MAX_SWARM_GUARDIANS + 1),
        help="Override the complexity-sized execution wing (default: auto by complexity)",
    )
    company.add_argument(
        "--test-size",
        type=int,
        default=None,
        choices=range(1, MAX_SWARM_GUARDIANS + 1),
        help="Override the complexity-sized test/QC wing (default: auto by complexity)",
    )
    company.add_argument("--max-parallel", type=int, default=DEFAULT_PARALLELISM)
    company.add_argument("goals", nargs="+", help="One or more mission tasks to run concurrently")

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
    if args.command == "brainstorm":
        return asyncio.run(
            _run_brainstorm(
                args.provider,
                args.model,
                " ".join(args.goal),
                args.guardians,
                args.max_parallel,
            )
        )
    if args.command == "company":
        return asyncio.run(
            _run_company(
                args.provider,
                args.model,
                args.goals,
                args.max_parallel,
                execute_size=args.execute_size,
                test_size=args.test_size,
            )
        )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
