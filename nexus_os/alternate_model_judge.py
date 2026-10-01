from __future__ import annotations

import json
from dataclasses import dataclass

from .multi_judge import JudgeKind, JudgeResult
from .portable.base import PortableProvider


@dataclass(frozen=True, slots=True)
class AlternateJudgePrompt:
    task: str
    candidate: str
    evidence: str = ""


class AlternateModelJudge:
    """Use a provider independent from the builder to produce a structured semantic judgment."""

    def __init__(self, provider: PortableProvider, *, judge_id: str = "alternate-model"):
        self.provider = provider
        self.judge_id = judge_id

    def evaluate(self, prompt: AlternateJudgePrompt) -> JudgeResult:
        instruction = (
            "You are an independent evaluation Guardian. Judge the candidate against the task and evidence. "
            "Return ONLY JSON with keys score (0-10 number), passed (boolean), rationale (string), "
            "critical (boolean). Do not claim evidence that is not supplied.\n\n"
            f"TASK:\n{prompt.task}\n\nCANDIDATE:\n{prompt.candidate}\n\nEVIDENCE:\n{prompt.evidence}"
        )
        result = self.provider.generate(instruction)
        try:
            payload = json.loads(result.text)
        except json.JSONDecodeError as exc:
            raise ValueError("alternate-model judge returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise TypeError("alternate-model judge response must be a JSON object")
        score = payload.get("score")
        passed = payload.get("passed")
        rationale = payload.get("rationale", "")
        critical = payload.get("critical", False)
        if not isinstance(score, int | float) or isinstance(score, bool):
            raise TypeError("alternate-model judge score must be numeric")
        if not isinstance(passed, bool) or not isinstance(critical, bool):
            raise TypeError("alternate-model judge passed/critical must be booleans")
        if not isinstance(rationale, str):
            raise TypeError("alternate-model judge rationale must be a string")
        return JudgeResult(
            judge_id=self.judge_id,
            kind=JudgeKind.ALTERNATE_MODEL,
            score=float(score),
            passed=passed,
            rationale=rationale,
            critical=critical,
        )
