"""Deterministic demo and OpenAI-compatible model providers (including local Ollama)."""

import json
import re
import httpx
from .config import Settings
from .models import Action, AGENT_PROFILES, ProjectCreate
from .tools import TOOL_DESCRIPTIONS


class ProviderError(RuntimeError):
    pass


class DemoProvider:
    """Honest deterministic smoke-test agent; not a substitute for an LLM."""

    def next_action(self, goal: str, agent: str, history: list[dict], available: list[str], model: str) -> Action:
        if history:
            last = history[-1]
            if last.get("type") == "tool_result":
                return Action(type="final", answer=f"Tool result: {json.dumps(last['result'], ensure_ascii=False)}")
            if last.get("type") == "tool_error":
                return Action(type="final", answer=f"Tool failed: {last['error']}")
        expr = re.fullmatch(r"\s*(?:calculate|compute)\s+(.+?)\s*\??\s*", goal, re.I)
        if expr and "calculator" in available:
            return Action(type="tool", tool="calculator", arguments={"expression": expr.group(1)})
        if goal.strip().lower() in ("what time is it?", "utc now") and "utc_now" in available:
            return Action(type="tool", tool="utc_now")
        return Action(type="final", answer="Demo provider only supports 'calculate EXPRESSION' and 'utc now'. Configure an OpenAI-compatible model for general tasks.")


class OpenAICompatibleProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    def next_action(self, goal: str, agent: str, history: list[dict], available: list[str], model: str) -> Action:
        tool_list = {name: TOOL_DESCRIPTIONS[name] for name in available}
        system = (
            AGENT_PROFILES[agent] + "\nYou have no tools beyond the provided allowlist. "
            "Return ONLY a JSON object with schema: "
            '{"type":"tool","tool":"tool_name","arguments":{}} OR '
            '{"type":"final","answer":"your actual answer"}. '
            "Do not report that a tool ran until a tool_result appears in the history. "
            f"Available tools: {json.dumps(tool_list)}"
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps({"goal": goal, "history": history}, ensure_ascii=False)},
        ]
        headers = {"Authorization": f"Bearer {self.settings.model_api_key or 'ollama'}"}
        try:
            with httpx.Client(timeout=45, follow_redirects=False) as client:
                r = client.post(
                    self.settings.model_base_url + "/chat/completions",
                    headers=headers,
                    json={"model": model, "messages": messages, "temperature": 0},
                )
                r.raise_for_status()
                content = r.json()["choices"][0]["message"]["content"]
                if not isinstance(content, str):
                    raise ProviderError("Model response did not contain text")
                content = content.strip()
                if content.startswith("```"):
                    content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content)
                action = Action.model_validate_json(content)
                if action.type == "tool" and action.tool not in available:
                    raise ProviderError("Model requested a tool not permitted for this project")
                return action
        except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError, ValueError) as exc:
            raise ProviderError(f"Model call or action validation failed: {type(exc).__name__}") from exc


def get_provider(project: ProjectCreate, settings: Settings):
    return DemoProvider() if project.provider == "demo" else OpenAICompatibleProvider(settings)
