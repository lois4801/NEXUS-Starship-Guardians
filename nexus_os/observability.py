from __future__ import annotations

from fastapi import FastAPI, Request
from opentelemetry import trace


def install_http_tracing(app: FastAPI, *, service_name: str = "nexus-starship-guardians") -> None:
    """Instrument HTTP requests with OpenTelemetry spans without requiring an exporter."""
    tracer = trace.get_tracer(service_name)

    @app.middleware("http")
    async def guardian_http_trace(request: Request, call_next):
        span_name = f"{request.method} {request.url.path}"
        with tracer.start_as_current_span(span_name) as span:
            span.set_attribute("service.name", service_name)
            span.set_attribute("http.request.method", request.method)
            span.set_attribute("url.path", request.url.path)
            response = await call_next(request)
            span.set_attribute("http.response.status_code", response.status_code)
            return response
