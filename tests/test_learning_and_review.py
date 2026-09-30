from pathlib import Path

from nexus_os.diff_review import AutomaticDiffReviewer
from nexus_os.learning_memory import GuardianLearningEngine, JsonlLearningStore


def test_learning_store_retrieves_lessons_and_exports_sft(tmp_path: Path):
    store = JsonlLearningStore(tmp_path / "memory.jsonl")
    engine = GuardianLearningEngine(store)
    engine.learn_from_run(
        task="fix API authentication regression",
        deliverable="patched auth",
        score=9,
        critique="Always run authentication regression tests after middleware changes.",
        rounds=2,
    )

    context = engine.context_for("authentication API")
    assert "authentication regression" in context

    target = tmp_path / "sft.jsonl"
    assert store.export_sft_pairs(target, min_score=8) == 1
    assert "patched auth" in target.read_text(encoding="utf-8")


def test_diff_review_blocks_conflicts_and_possible_secrets():
    report = AutomaticDiffReviewer().review(
        "+<<<<<<< HEAD\n"
        "+api_key = \"super-secret-value-123\"\n"
        "+requests.get(url, verify=False)\n"
    )
    assert report.blocking
    codes = {item.code for item in report.findings}
    assert {"conflict-marker", "possible-secret", "tls-disabled"} <= codes
