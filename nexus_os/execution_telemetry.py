# ruff: noqa: I001
from __future__ import annotations

import contextvars
import secrets
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from time import perf_counter

from opentelemetry import trace


_correlation_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "nexus_correlation_id", default=None
)


@dataclass(slots=True)
class ExecutionTrace:
    correlation_id: str
    operation: str
    duration_seconds: float = 0.0
    guardian_id: str | None = None
    project_id: str | None = None
    mission_id: str | None = None
    success: bool = True


def current_correlation_id() -> str | None:
    return _correlation_id.get()


def new_correlation_id() -> str:
    return "nsg_" + secrets.token_hex(12)


@contextmanager
def guardian_span(
    operation: str,
    *,
    guardian_id: str | None = None,
    project_id: str | None = None,
    mission_id: str | None = None,
    correlation_id: str | None = None,
) -> Iterator[ExecutionTrace]:
    """Create a correlated OpenTelemetry span for Guardian/queue work."""
    correlation_id = correlation_id or current_correlation_id() or new_correlation_id()
    token = _correlation_id.set(correlation_id)
    tracer = trace.get_tracer("nexus-starship-guardians.execution")
    started = perf_counter()
    execution = ExecutionTrace(
        correlation_id=correlation_id,
        operation=operation,
        guardian_id=guardian_id,
        project_id=project_id,
        mission_id=mission_id,
    )
    try:
        with tracer.start_as_current_span(operation) as span:
            span.set_attribute("nexus.correlation_id", correlation_id)
            if guardian_id:
                span.set_attribute("nexus.guardian_id", guardian_id)
            if project_id:
                span.set_attribute("nexus.project_id", project_id)
            if mission_id:
                span.set_attribute("nexus.mission_id", mission_id)
            try:
                yield execution
            except Exception as exc:
                execution.success = False
                span.record_exception(exc)
                span.set_attribute("nexus.success", False)
                raise
            else:
                span.set_attribute("nexus.success", True)
    finally:
        execution.duration_seconds = max(0.0, perf_counter() - started)
        _correlation_id.reset(token)
