from __future__ import annotations

import pytest

from nexus_os.cross_project_metrics import CrossProjectPerformanceStore


def test_cross_project_store_aggregates_guardian_history(tmp_path):
    store = CrossProjectPerformanceStore(tmp_path / "performance.db")
    store.record(project_id="lucio", guardian_id="backend-01", success=True, score=9, cost=0.1, latency_seconds=2)
    store.record(project_id="ember", guardian_id="backend-01", success=False, score=5, cost=0.2, latency_seconds=4)

    summary = store.summary("backend-01")
    assert summary.attempts == 2
    assert summary.successes == 1
    assert summary.projects == 2
    assert summary.average_score == 7.0
    assert summary.average_cost == pytest.approx(0.15)
    assert summary.average_latency_seconds == 3.0


def test_cross_project_leaderboard_prefers_higher_quality_and_reliability(tmp_path):
    store = CrossProjectPerformanceStore(tmp_path / "performance.db")
    store.record(project_id="a", guardian_id="strong", success=True, score=9)
    store.record(project_id="b", guardian_id="strong", success=True, score=9)
    store.record(project_id="a", guardian_id="weak", success=False, score=5)
    store.record(project_id="b", guardian_id="weak", success=True, score=6)

    board = store.leaderboard(minimum_attempts=2)
    assert [item.guardian_id for item in board] == ["strong", "weak"]


def test_cross_project_store_validates_inputs(tmp_path):
    store = CrossProjectPerformanceStore(tmp_path / "performance.db")
    with pytest.raises(ValueError, match="project_id and guardian_id"):
        store.record(project_id="", guardian_id="g", success=True, score=8)
