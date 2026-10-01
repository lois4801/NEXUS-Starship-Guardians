from nexus_os.adaptive_intelligence import AdaptiveGuardianIntelligence
from nexus_os.cognitive_evolution import CognitiveEvolutionEngine
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


def test_verified_specialist_success_learns_automatically(tmp_path):
    store = JsonlLearningStore(tmp_path / "learning.jsonl")
    adaptive = AdaptiveGuardianIntelligence(tmp_path / "adaptive.json")
    recorder = ServerLearningRecorder(GuardianLearningEngine(store), adaptive)
    run = {
        "run_id": "run-specialist-success",
        "project_id": "project-a",
        "agent": "coder-specialist",
        "goal": "Build and test the backend feature",
        "answer": "done",
        "status": "completed",
        "steps_used": 3,
        "events": [
            {
                "type": "mission_intelligence",
                "capabilities": ["backend", "testing"],
            },
            {"type": "tool_result", "tool": "test", "result": "passed"},
            {"type": "final", "answer": "done"},
        ],
    }

    recorder.record_if_terminal(run)
    state = adaptive.state("coder-specialist")
    assert state.verified_runs == 1
    assert state.learning_cycles == 1
    assert state.skills["backend"].attempts == 1
    assert state.skills["backend"].successes == 1
    assert state.skills["testing"].adaptive_score > 5.0


def test_unverified_specialist_success_does_not_reinforce_itself(tmp_path):
    store = JsonlLearningStore(tmp_path / "learning.jsonl")
    adaptive = AdaptiveGuardianIntelligence(tmp_path / "adaptive.json")
    recorder = ServerLearningRecorder(GuardianLearningEngine(store), adaptive)
    recorder.record_if_terminal(
        {
            "run_id": "run-specialist-unverified",
            "project_id": "project-a",
            "agent": "coder-specialist",
            "goal": "Build the backend feature",
            "answer": "done",
            "status": "completed",
            "steps_used": 1,
            "events": [
                {"type": "mission_intelligence", "capabilities": ["backend"]},
                {"type": "final", "answer": "done"},
            ],
        }
    )
    state = adaptive.state("coder-specialist")
    assert state.verified_runs == 0
    assert "backend" not in state.skills


def test_verified_specialist_failure_learns_from_concrete_failure_event(tmp_path):
    store = JsonlLearningStore(tmp_path / "learning.jsonl")
    adaptive = AdaptiveGuardianIntelligence(tmp_path / "adaptive.json")
    recorder = ServerLearningRecorder(GuardianLearningEngine(store), adaptive)
    recorder.record_if_terminal(
        {
            "run_id": "run-specialist-failure",
            "project_id": "project-a",
            "agent": "api-specialist",
            "goal": "Repair the API",
            "answer": "",
            "status": "failed",
            "steps_used": 2,
            "events": [
                {"type": "mission_intelligence", "capabilities": ["backend"]},
                {"type": "tool_error", "tool": "api", "error": "contract mismatch"},
            ],
        }
    )
    evidence = adaptive.state("api-specialist").skills["backend"]
    assert evidence.attempts == 1
    assert evidence.successes == 0
    assert evidence.average_score == 2.0


def test_verified_live_run_feeds_cognitive_evolution_and_counterfactual_cycle(tmp_path):
    store = JsonlLearningStore(tmp_path / "learning.jsonl")
    adaptive = AdaptiveGuardianIntelligence(tmp_path / "adaptive.json")
    cognitive = CognitiveEvolutionEngine(tmp_path / "cognitive.json", adaptive)
    recorder = ServerLearningRecorder(
        GuardianLearningEngine(store),
        adaptive,
        cognitive,
    )
    recorder.record_if_terminal(
        {
            "run_id": "run-cognitive-failure",
            "project_id": "project-a",
            "agent": "debugger-specialist",
            "goal": "Debug the API regression",
            "answer": "",
            "status": "failed",
            "steps_used": 2,
            "events": [
                {
                    "type": "mission_intelligence",
                    "capabilities": ["debugging", "testing"],
                    "confidence": 0.95,
                },
                {"type": "strategy_intelligence", "strategy": "direct-repair"},
                {"type": "tool_error", "tool": "test", "error": "regression persists"},
            ],
        }
    )

    state = cognitive.state("debugger-specialist")
    assert state.verified_episodes == 1
    assert state.counterfactual_cycles == 1
    assert state.calibration.predictions == 1
    assert cognitive.lessons()
    assert cognitive.failure_clusters()[0].signature == "tool_error:test"
