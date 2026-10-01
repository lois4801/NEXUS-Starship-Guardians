from __future__ import annotations

import pytest

from nexus_os.alternate_model_judge import AlternateJudgePrompt, AlternateModelJudge
from nexus_os.multi_judge import JudgeKind
from nexus_os.portable.base import ProviderResult


class StubProvider:
    name = "stub"

    def __init__(self, text: str):
        self.text = text

    def generate(self, prompt: str) -> ProviderResult:
        assert "independent evaluation Guardian" in prompt
        return ProviderResult(text=self.text, provider=self.name, model="judge-model")


def test_alternate_model_judge_parses_structured_result():
    judge = AlternateModelJudge(
        StubProvider('{"score": 8.5, "passed": true, "rationale": "supported", "critical": false}')
    )
    result = judge.evaluate(AlternateJudgePrompt(task="Do x", candidate="Done", evidence="test passed"))
    assert result.kind == JudgeKind.ALTERNATE_MODEL
    assert result.score == 8.5
    assert result.passed is True
    assert result.critical is False


def test_alternate_model_judge_rejects_invalid_json():
    judge = AlternateModelJudge(StubProvider("not-json"))
    with pytest.raises(ValueError, match="invalid JSON"):
        judge.evaluate(AlternateJudgePrompt(task="x", candidate="y"))


def test_alternate_model_judge_rejects_wrong_types():
    judge = AlternateModelJudge(
        StubProvider('{"score": "high", "passed": true, "rationale": "x", "critical": false}')
    )
    with pytest.raises(ValueError, match="score must be numeric"):
        judge.evaluate(AlternateJudgePrompt(task="x", candidate="y"))
