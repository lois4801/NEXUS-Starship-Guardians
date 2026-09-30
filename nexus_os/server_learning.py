from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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


class ServerLearningRecorder:
    """Record terminal API/server runs into the shared Guardian learning system.

    Scores here represent execution reliability only, not semantic answer quality.
    Semantic quality should be measured by the Synthetic Evaluation Lab.
    """

    def __init__(self, engine: GuardianLearningEngine):
        self.engine = engine
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
        self._recorded_run_ids.add(run_id)
