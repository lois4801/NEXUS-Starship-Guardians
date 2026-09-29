"""Bounded agent loop with durable event trace and explicit approval for write tools."""

import threading
from datetime import datetime, timezone
from typing import Any

from .config import Settings
from .models import Action
from .providers import ProviderError, get_provider
from .storage import Store
from .tools import APPROVAL_REQUIRED, TOOL_DESCRIPTIONS, ToolError, run_tool


class Orchestrator:
    def __init__(self, store: Store, settings: Settings):
        self.store = store
        self.settings = settings
        self.lock = threading.RLock()  # single-process starter; use distributed locks when scaling

    @staticmethod
    def event(run: dict[str, Any], typ: str, **details: Any) -> None:
        run["events"].append({"type": typ, "at": datetime.now(timezone.utc).isoformat(), **details})

    def advance(self, run_id: str, approved: bool | None = None) -> dict[str, Any]:
        with self.lock:
            run = self.store.get_run(run_id)
            if not run:
                raise LookupError("Run not found")
            project = self.store.get_project(run["project_id"])
            assert project is not None
            if approved is not None:
                if run["status"] != "pending_approval" or not run["pending_approval"]:
                    raise ValueError("No approval is pending")
                pending = run["pending_approval"]
                run["pending_approval"] = None
                if not approved:
                    self.event(run, "approval_denied", tool=pending["tool"])
                    run["status"] = "completed"
                    run["answer"] = "The requested tool operation was denied."
                    self.store.update_run(run)
                    return run
                self.event(run, "approval_granted", tool=pending["tool"])
                self._perform(run, pending["tool"], pending["arguments"])
                run["steps_used"] += 1
            while run["steps_used"] < project.max_steps and run["status"] not in ("failed", "completed"):
                provider = get_provider(project, self.settings)
                try:
                    action: Action = provider.next_action(
                        run["goal"], run["agent"], run["events"],
                        project.allowed_tools, project.model or self.settings.model_name,
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
                if not action.tool or action.tool not in TOOL_DESCRIPTIONS or action.tool not in project.allowed_tools:
                    run["status"] = "failed"
                    self.event(run, "policy_denied", tool=action.tool or "missing")
                    break
                if action.tool in APPROVAL_REQUIRED:
                    run["pending_approval"] = {"tool": action.tool, "arguments": action.arguments}
                    run["status"] = "pending_approval"
                    self.event(run, "approval_requested", tool=action.tool, arguments=action.arguments)
                    break
                self._perform(run, action.tool, action.arguments)
                run["steps_used"] += 1
            if run["steps_used"] >= project.max_steps and run["status"] not in ("failed", "completed"):
                run["status"] = "max_steps"
                self.event(run, "max_steps_reached", limit=project.max_steps)
            self.store.update_run(run)
            return run

    def _perform(self, run: dict[str, Any], tool: str, arguments: dict) -> None:
        try:
            result = run_tool(tool, arguments, run["project_id"], self.store)
            self.event(run, "tool_result", tool=tool, arguments=arguments, result=result)
        except (ToolError, ValueError) as exc:
            self.event(run, "tool_error", tool=tool, error=str(exc))
