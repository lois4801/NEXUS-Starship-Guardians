from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from nexus_os.execution import ExecutionTask
from nexus_os.workers.local_process import LocalProcessWorker


@dataclass(slots=True)
class APICheck:
    method: str
    path: str
    expected_status: int = 200
    json_body: dict | None = None


@dataclass(slots=True)
class APICheckResult:
    ok: bool
    status_code: int
    body_excerpt: str


class APITestWorker:
    """Run bounded HTTP checks against one configured origin."""

    def __init__(self, base_url: str, *, timeout_seconds: float = 15.0, max_body_chars: int = 4000):
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("base_url must be an absolute http(s) URL")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_body_chars = max_body_chars

    async def run(self, check: APICheck) -> APICheckResult:
        if not check.path.startswith("/") or check.path.startswith("//"):
            raise ValueError("API check path must be origin-relative")
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_seconds) as client:
            response = await client.request(
                check.method.upper(),
                check.path,
                json=check.json_body,
            )
        return APICheckResult(
            ok=response.status_code == check.expected_status,
            status_code=response.status_code,
            body_excerpt=response.text[: self.max_body_chars],
        )


class BrowserTestWorker:
    """Run an operator-configured browser test command through the restricted process worker."""

    def __init__(self, process_worker: LocalProcessWorker, command: tuple[str, ...]):
        if not command:
            raise ValueError("browser test command cannot be empty")
        self.process_worker = process_worker
        self.command = command

    async def run(self, *, task_id: str = "browser-tests", cwd: str = ".") -> str:
        task = ExecutionTask(
            task_id=task_id,
            role="browser-verification-guardian",
            instruction="Run configured browser verification suite",
            verification_required=False,
        )
        return await self.process_worker.run_command(task, list(self.command), cwd=cwd)
