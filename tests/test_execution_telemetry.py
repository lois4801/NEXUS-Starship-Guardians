from __future__ import annotations

from nexus_os.execution_telemetry import current_correlation_id, guardian_span


def test_guardian_span_sets_and_resets_correlation_id():
    assert current_correlation_id() is None
    with guardian_span("build", guardian_id="builder-01") as trace:
        assert trace.correlation_id.startswith("nsg_")
        assert current_correlation_id() == trace.correlation_id
    assert current_correlation_id() is None


def test_nested_guardian_span_reuses_correlation_id():
    with guardian_span("mission", mission_id="m1") as outer:
        with guardian_span("test", guardian_id="qa-01") as inner:
            assert inner.correlation_id == outer.correlation_id
