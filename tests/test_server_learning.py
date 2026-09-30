from nexus_os.learning_memory import GuardianLearningEngine, JsonlLearningStore
from nexus_os.server_learning import ServerLearningRecorder


def test_server_learning_records_terminal_failure_once(tmp_path):
    store = JsonlLearningStore(tmp_path / "learning.jsonl")
    recorder = ServerLearningRecorder(GuardianLearningEngine(store))
    run = {
        "run_id": "run-1",
        "project_id": "project-a",
        "agent": "builder",
        "goal": "build feature",
        "answer": "",
        "status": "failed",
        "steps_used": 2,
        "events": [
            {"type": "provider_error", "error": "provider unavailable"},
        ],
    }

    recorder.record_if_terminal(run)
    recorder.record_if_terminal(run)
    records = store.records()
    episodes = [item for item in records if item.get("type") == "episode"]
    lessons = [item for item in records if item.get("type") == "lesson"]
    assert len(episodes) == 1
    assert len(lessons) == 1
    assert episodes[0]["metadata"]["score_kind"] == "execution-reliability"
    assert "provider_error" in lessons[0]["text"]


def test_server_learning_does_not_record_pending_runs(tmp_path):
    store = JsonlLearningStore(tmp_path / "learning.jsonl")
    recorder = ServerLearningRecorder(GuardianLearningEngine(store))
    recorder.record_if_terminal(
        {
            "run_id": "run-2",
            "project_id": "project-a",
            "agent": "builder",
            "goal": "build feature",
            "status": "pending_approval",
            "events": [],
        }
    )
    assert store.records() == []
