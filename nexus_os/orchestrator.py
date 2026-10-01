"""Bounded Guardian loop with durable event trace and explicit approval for write tools."""

import threading
from datetime import UTC, datetime
from typing import Any

from .config import Settings
from .intelligence_fabric import IntelligenceFabric
from .mission_runtime import MissionRuntime
from .models import Action
from .providers import ProviderError, get_provider
from .server_learning import ServerLearningRecorder
from .storage import Store
from .tools import APPROVAL_REQUIRED, TOOL_DESCRIPTIONS, ToolError, run_tool


class Orchestrator:
    def __init__(
        self,
        store: Store,
        settings: Settings,
        learning_recorder: ServerLearningRecorder | None = None,
        mission_runtime: MissionRuntime | None = None,
        intelligence_fabric: IntelligenceFabric | None = None,
    ):
        self.store = store
        self.settings = settings
        self.learning_recorder = learning_recorder
        self.mission_runtime = mission_runtime or MissionRuntime()
        self.intelligence_fabric = intelligence_fabric or IntelligenceFabric(
            classifier=self.mission_runtime.classifier
        )
        self.lock = threading.RLock()  # single-process starter; use distributed locks when scaling

    @staticmethod
    def event(run: dict[str, Any], typ: str, **details: Any) -> None:
        run["events"].append({"type": typ, "at": datetime.now(UTC).isoformat(), **details})

    def _persist(self, run: dict[str, Any]) -> dict[str, Any]:
        self.store.update_run(run)
        if self.learning_recorder is not None:
            self.learning_recorder.record_if_terminal(run)
        return run

    def _record_mission_intelligence(self, run: dict[str, Any], project) -> None:
        if any(event.get("type") == "mission_intelligence" for event in run["events"]):
            return
        plan = self.mission_runtime.plan(
            run["goal"],
            project_gateway_tools=frozenset(project.gateway_tools),
        )
        self.event(
            run,
            "mission_intelligence",
            kind=plan.kind,
            confidence=plan.confidence,
            capabilities=sorted(plan.capabilities),
            required_tools=sorted(plan.required_tools),
            selected_guardians=list(plan.selected_guardians),
            missing_capabilities=sorted(plan.missing_capabilities),
            missing_tools=sorted(plan.missing_tools),
            blocked_tools=sorted(plan.blocked_tools),
            sufficient=plan.sufficient,
            reasons=list(plan.reasons),
        )

    def _record_strategy_intelligence(self, run: dict[str, Any]) -> None:
        if any(event.get("type") == "strategy_intelligence" for event in run["events"]):
            return
        plan = self.intelligence_fabric.plan(run["goal"])
        self.event(
            run,
            "strategy_intelligence",
            strategy=plan.strategy.mode.value,
            rationale=list(plan.strategy.rationale),
            required_evidence=list(plan.strategy.required_evidence),
            uncertainty=plan.uncertainty,
            adversarial_cases=[case.case_id for case in plan.adversarial_cases],
            assumptions=list(plan.assumptions),
        )

    def advance(self, run_id: str, approved: bool | None = None) -> dict[str, Any]:
        with self.lock:
            run = self.store.get_run(run_id)
            if not run:
                raise LookupError("Run not found")
            project = self.store.get_project(run["project_id"])
            assert project is not None
            self._record_mission_intelligence(run, project)
            self._record_strategy_intelligence(run)
            if approved is not None:
                if run["status"] != "pending_approval" or not run["pending_approval"]:
                    raise ValueError("No approval is pending")
                pending = run["pending_approval"]
                run["pending_approval"] = None
                if not approved:
                    self.event(run, "approval_denied", tool=pending["tool"])
                    run["status"] = "completed"
                    run["answer"] = "The requested tool operation was denied."
                    return self._persist(run)
                self.event(run, "approval_granted", tool=pending["tool"])
                self._perform(run, pending["tool"], pending["arguments"])
                run["steps_used"] += 1
            while run["steps_used"] < project.max_steps and run["status"] not in (
                "failed",
                "completed",
            ):
                provider = get_provider(project, self.settings)
                try:
                    action: Action = provider.next_action(
                        run["goal"],
                        run["agent"],
                        run["events"],
                        project.allowed_tools,
                        project.model or self.settings.model_name,
                    )
                except ProviderError as exc:
                    run["status"] = "failed"
                    self.event(run, "provider_error", error=str(exc))
                    break
                if action.type == "final":
                    run["answer"] = action.answer or "No answer returned"
                    run["status"] = "completed"
                    self.event(run, "final", answer=run["answer"])
                    break
                if (
                    not action.tool
                    or action.tool not in TOOL_DESCRIPTIONS
                    or action.tool not in project.allowed_tools
                ):
                    run["status"] = "failed"
                    self.event(run, "policy_denied", tool=action.tool or "missing")
                    break
                if action.tool in APPROVAL_REQUIRED:
                    run["pending_approval"] = {
                        "tool": action.tool,
                        "arguments": action.arguments,
                    }
                    run["status"] = "pending_approval"
                    self.event(
                        run,
                        "approval_requested",
                        tool=action.tool,
                        arguments=action.arguments,
                    )
                    break
                self._perform(run, action.tool, action.arguments)
                run["steps_used"] += 1
            if run["steps_used"] >= project.max_steps and run["status"] not in (
                "failed",
                "completed",
            ):
                run["status"] = "max_steps"
                self.event(run, "max_steps_reached", limit=project.max_steps)
            return self._persist(run)

    def _perform(self, run: dict[str, Any], tool: str, arguments: dict) -> None:
        try:
            result = run_tool(tool, arguments, run["project_id"], self.store)
            self.event(run, "tool_result", tool=tool, arguments=arguments, result=result)
        except (ToolError, ValueError) as exc:
            self.event(run, "tool_error", tool=tool, error=str(exc))
