# NEXUS Agentic OS · v0.1.0

**One reusable agent runtime; separate permissions and agent packs for Lucio AI Platform, Ember, and future applications.** This repository is independent of your application repositories. It is a **tested development starter**, not a claim of a production-ready autonomous app builder.

## Delivered in v0.1

- FastAPI REST API with Swagger UI (`/docs`), health endpoint and independently registered projects.
- Strong, randomly generated per-project API keys (only their SHA-256 hashes are stored), a separate admin token, and enforcement of tenant isolation on every protected endpoint.
- Project-specific enabled agents (`general`, `builder`, `research`), allowed tools, model provider and execution budgets.
- Bounded orchestration loop, durable SQLite run traces, explicit approval before writing project notes, denied-tool checks and recoverable pending approvals.
- Fully offline deterministic `demo` provider with a **real calculator** and UTC tool. This intentionally does **not** pretend to design apps, browse or write code.
- OpenAI-compatible `/v1/chat/completions` provider, configurable for local Ollama or a supported hosted endpoint. Requires a real model service and appropriate permissions.
- Python and server-side TypeScript SDKs, Docker, Docker Compose, examples and CI tests.

**Not yet implemented:** GitHub repository editing, terminal sandbox, full MCP client/server, external web research, app deployment, model-cost router, durable distributed queue, Postgres, or Kubernetes. Plan these as subsequent integrations; never expose arbitrary shell or tenant-wide credentials to models.

## Architecture

```text
Lucio AI ──┐
Ember ─────┼─> [NEXUS API / project key] -> [project permissions]
Future ───┘                                  |
                                             v
                 [selected agent profile] -> [bounded orchestrator]
                                              |     |
                                              |     +-> SQLite run history
                                              v
                                    [configured model provider]
                                              |
                                    [allowlisted action proposal]
                                              |
                          [approval for writes] -> [real tool call]
```

Each app gets its **own project key, enabled agents, tool allowlist and run history**. The central service never needs to merge the applications' existing Git histories.

## Quick start — local smoke test (no paid API required)

```bash
# Python 3.11+
git clone https://github.com/lois4801/NEXUS-Agentic-OS.git
cd NEXUS-Agentic-OS
python -m venv .venv
# PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -e '.[dev]'
# Set a secure admin token; PowerShell:
$env:NEXUS_ADMIN_TOKEN = python -c "import secrets; print(secrets.token_urlsafe(40))"
# macOS/Linux alternative: export NEXUS_ADMIN_TOKEN=$(python -c 'import secrets; print(secrets.token_urlsafe(40))')
uvicorn nexus_os.api:app --host 127.0.0.1 --port 8000 --workers 1
```

In another PowerShell window, set **the same admin token**, or set it in an ignored local `.env` file and load it securely. Then register a project:

```powershell
$headers = @{ Authorization = "Bearer $env:NEXUS_ADMIN_TOKEN" }
$project = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/v1/projects `
  -Headers $headers -ContentType 'application/json' `
  -Body '{"project_id":"lucio-dev","display_name":"Lucio development","agents":["general","builder"],"allowed_tools":["calculator","utc_now"],"provider":"demo"}'
# SAVE $project.api_key somewhere secure — it is displayed only once.
$keyHeaders = @{ Authorization = "Bearer $($project.api_key)" }
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/v1/projects/lucio-dev/runs `
  -Headers $keyHeaders -ContentType 'application/json' `
  -Body '{"goal":"calculate 12 * 7", "agent":"general"}'
```

The result should contain `status: completed`, a `tool_result` event with `84`, and a `final` event. Register `ember-dev` separately to give Ember a different API key and tool permissions. API documentation is at [localhost:8000/docs](http://127.0.0.1:8000/docs) when running locally.

### Python SDK

```python
from nexus_os.client import NexusClient
with NexusClient("http://127.0.0.1:8000", "YOUR_PROJECT_API_KEY") as nexus:
    result = nexus.create_run("lucio-dev", "calculate 12 * 7")
    print(result["answer"])
```

### TypeScript SDK (server-side ONLY)

```typescript
import { NexusClient } from './sdk/typescript/src/client';
const nexus = new NexusClient(process.env.NEXUS_URL!, process.env.NEXUS_PROJECT_KEY!);
const result = await nexus.createRun('ember-dev', 'calculate 12 * 7');
console.log(result.answer);
```

Use this SDK only from your own backend / server action; NEVER ship API keys to a browser/mobile client.

## Configure Ollama for real model-driven planning

Ollama exposes an OpenAI-compatible chat completions endpoint at `/v1/chat/completions`. Install Ollama, pull a suitable model (`ollama pull llama3.2`), and set:

```dotenv
NEXUS_MODEL_BASE_URL=http://localhost:11434/v1
NEXUS_MODEL_NAME=llama3.2
NEXUS_MODEL_API_KEY=
```

Register a new project with `"provider":"openai_compatible"`. The model can propose actions from that project's allowlisted tools; outputs are validated and tool use is recorded. This is a starter JSON-action protocol, not a guarantee that every local model will follow instructions reliably. If NEXUS itself runs in Docker and Ollama runs on your host, use `http://host.docker.internal:11434/v1` and enable Docker host mapping as needed on Linux.

## Approvals, security and operating limits

`project_note` is a **write** tool and will always return `pending_approval` when proposed; the owning project's API key (or admin token) calls `POST /v1/runs/{run_id}/approval` with `{"approved":true}` or `false`. No model can bypass the fixed server-side approval rule. New tools must explicitly declare their approval classification before release.

Before public deployment, add TLS, a reverse proxy, rate limiting, production-grade secret management, centralized audit logging, PostgreSQL, a durable queue and per-tenant execution quotas. SQLite and the in-process lock are intended for a single process only. Run only one Uvicorn worker. Do **not** expose `NEXUS_DEV_MODE=true` publicly. Avoid storing model/API keys in run events, user prompts or GitHub.

## Quality gates

```bash
pip install -e '.[dev]'
NEXUS_DEV_MODE=true pytest -q
ruff check nexus_os tests examples
```

CI runs both checks on push and pull request. Offline tests cover authentication, tenant isolation, real calculator execution, bogus tool rejection, approval and denial, and deliberate demo limitations. Integration tests against a **real** Ollama/hosted model and existing Lucio/Ember repositories remain a separate acceptance gate.

## Roadmap

1. **v0.1 (this release):** secure starter, offline demo, local LLM adapter, Python/TypeScript clients and CI.
2. **v0.2:** authenticated GitHub adapter, sandboxed coding worker, tests with evidence, job cancellation and resumable background queue.
3. **v0.3:** MCP tool gateway, PostgreSQL, event streaming, scoped skills/agent packs, model evaluation and budget router.
4. **v1.0:** verified Lucio and Ember integrations, tenancy security audit, observability, migrations, release and rollback playbooks.

See `docs/ARCHITECTURE.md` and `docs/INTEGRATION.md` for deeper design and phased app-specific integration instructions.
