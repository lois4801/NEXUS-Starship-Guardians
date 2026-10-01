from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .adaptive_intelligence import AdaptiveGuardianIntelligence
from .learning_memory import GuardianLearningEngine


@dataclass(slots=True, frozen=True)
class ServerLearningOutcome:
    score: float
    critique: str
    distilled_lesson: str | None


def _terminal_outcome(run: dict[str, Any]) -> ServerLearningOutcome | None:
    status = str(run.get("status", ""))
    events = list(run.get("events", []))
    if status not in {"completed", "failed", "max_steps"}:
        return None

    failure_events = [
        event
        for event in events
        if event.get("type") in {"provider_error", "policy_denied", "tool_error", "max_steps_reached"}
    ]
    if status == "completed" and not failure_events:
        return ServerLearningOutcome(
            score=10.0,
            critique="Operational execution completed without recorded policy, provider, or tool failures.",
            distilled_lesson=None,
        )

    if failure_events:
        last = failure_events[-1]
        event_type = str(last.get("type", "failure"))
        detail = str(last.get("error") or last.get("tool") or last.get("limit") or "unknown")
        lesson = (
            f"When a Guardian run hits {event_type}, inspect the underlying condition before retrying; "
            f"the latest recorded detail was: {detail}."
        )
        return ServerLearningOutcome(
            score=2.0 if status == "failed" else 4.0,
            critique=f"Server run ended with {event_type}: {detail}",
            distilled_lesson=lesson,
        )

    return ServerLearningOutcome(
        score=6.0,
        critique=f"Server run ended in terminal status {status} without a classified failure event.",
        distilled_lesson=None,
    )


def _mission_capabilities(run: dict[str, Any]) -> frozenset[str]:
    for event in reversed(list(run.get("events", []))):
        if event.get("type") != "mission_intelligence":
            continue
        capabilities = event.get("capabilities", [])
        if isinstance(capabilities, list):
            return frozenset(
                str(item).strip() for item in capabilities if str(item).strip()
            )
    return frozenset()


def _has_verification_evidence(run: dict[str, Any]) -> bool:
    """Successful adaptive learning requires objective verification evidence.

    Concrete terminal failures are already evidence of failure. Successful runs need a verification
    tool result so a mere final answer cannot reinforce itself as specialist expertise.
    """
    events = list(run.get("events", []))
    if any(
        event.get("type") in {"provider_error", "policy_denied", "tool_error", "max_steps_reached"}
        for event in events
    ):
        return True
    verification_tools = {"test", "api", "browser", "security"}
    return any(
        event.get("type") == "tool_result" and str(event.get("tool", "")) in verification_tools
        for event in events
    )


class ServerLearningRecorder:
    """Record terminal API/server runs into shared and specialist learning systems.

    General memory records execution reliability. Adaptive specialist intelligence is stricter:
    failed runs may learn from concrete failure events, while successful runs require objective
    verification tool evidence before per-skill evidence changes.
    """

    def __init__(
        self,
        engine: GuardianLearningEngine,
        adaptive_intelligence: AdaptiveGuardianIntelligence | None = None,
    ):
        self.engine = engine
        self.adaptive_intelligence = adaptive_intelligence
        self._recorded_run_ids: set[str] = set()

    def record_if_terminal(self, run: dict[str, Any]) -> None:
        run_id = str(run.get("run_id", ""))
        if not run_id or run_id in self._recorded_run_ids:
            return
        outcome = _terminal_outcome(run)
        if outcome is None:
            return
        project_id = str(run.get("project_id", ""))
        guardian = str(run.get("agent", run.get("guardian", "unknown")))
        answer = str(run.get("answer") or "")
        self.engine.learn_from_run(
            task=str(run.get("goal", "")),
            deliverable=answer,
            score=outcome.score,
            critique=outcome.critique,
            rounds=int(run.get("steps_used", 0)),
            distilled_lesson=outcome.distilled_lesson,
            metadata={
                "source": "server",
                "project_id": project_id,
                "guardian": guardian,
                "status": str(run.get("status", "")),
                "score_kind": "execution-reliability",
            },
        )

        if self.adaptive_intelligence is not None and _has_verification_evidence(run):
            try:
                profile = self.adaptive_intelligence.profile(guardian)
            except KeyError:
                profile = None
            if profile is not None:
                skills = _mission_capabilities(run)
                if not skills:
                    skills = profile.capabilities
                status = str(run.get("status", ""))
                success = status == "completed" and outcome.score >= 8.0
                self.adaptive_intelligence.record_verified_outcome(
                    guardian,
                    skills=skills,
                    success=success,
                    score=outcome.score,
                    benchmark_passed=None,
                    critical_regression=False,
                    verified=True,
                )

        self._recorded_run_ids.add(run_id)
