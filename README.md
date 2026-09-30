# NEXUS Agentic OS · v0.1.0

**One reusable agent runtime; separate permissions and agent packs for Lucio AI Platform, Ember, and future applications.** This repository is independent of your application repositories. It is a **tested development starter**, not a claim of a production-ready autonomous app builder.

## Delivered in v0.1

- FastAPI REST API with Swagger UI (`/docs`), health endpoint and independently registered projects.
- Strong, randomly generated per-project API keys (only their SHA-256 hashes are stored), a separate admin token, and enforcement of tenant isolation on every protected endpoint.
- Project-specific enabled agents (`general`, `builder`, `research`), allowed tools, model provider and execution budgets.
- Bounded orchestration loop, durable SQLite run traces, explicit approval before writing project notes, denied-tool checks and recoverable pending approvals.
- Fully offline deterministic `demo` provider with a **real calculator** and UTC tool. This intentionally does **not** pretend to design apps, browse or write code.
- OpenAI-compatible `/v1/chat/completions` provider, configurable for local Ollama or a supported hosted endpoint. Requires a real model service and appropriate permissions.
- Portable local/CLI runtime for using Ollama and user-authenticated coding/chat CLIs without requiring a paid API in the NEXUS core.
- Adaptive multi-agent swarm coordinator supporting **1-200 logical specialists per mission** with bounded physical concurrency, isolated failures, evidence compaction, and lead-agent synthesis.
- Python and server-side TypeScript SDKs, Docker, Docker Compose, examples and CI tests.

**Not yet implemented:** GitHub repository editing, terminal sandbox, full MCP client/server, external web research, app deployment, model-cost router, durable distributed queue, Postgres, or Kubernetes. Plan these as subsequent integrations; never expose arbitrary shell or tenant-wide credentials to models.

## Architecture

```text
Lucio AI ──┐
Ember ─────┼─> [NEXUS API / project key] -> [project permissions]
Future ───┘                                  |
                                             v
                         [mission / goal router]
                                  |
                         [adaptive swarm planner]
                                  |
                  1..200 logical specialist agents
                                  |
                     bounded parallel model calls
                                  |
                     [lead synthesis + evidence]
                                  |
                 [safe bounded execution orchestrator]
                           |               |
                     approvals         run history
                           |
                    allowlisted tools
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
$project = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/v1/projects/lucio-dev `
  -Headers $headers -ContentType 'application/json'
```

Use the existing API and SDK examples in this repository for scoped project runs and approvals.

## Portable LLM runtime

Install the repo and detect which local/coding assistants are available:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
.\.venv\Scripts\nexus-portable.exe doctor
```

Use an API-key-free local Ollama model:

```powershell
ollama pull llama3.2
.\.venv\Scripts\nexus-portable.exe ask --provider ollama --model llama3.2 "Design a feature plan"
```

Or bridge a coding/chat CLI that is already installed and authenticated on the laptop:

```powershell
$env:NEXUS_LLM_COMMAND='["codex","exec","-"]'
.\.venv\Scripts\nexus-portable.exe ask --provider cli --model codex "Review this repository"
```

NEXUS does not bypass provider authentication. Local models can run without provider API keys; hosted model tools remain responsible for their own login, subscription, license, and terms. See `docs/PORTABLE_LLM_RUNTIME.md`.

## 200-agent swarm mode

Normal development work usually benefits from a focused team of 12-32 specialists:

```powershell
.\.venv\Scripts\nexus-portable.exe swarm `
  --provider ollama `
  --model llama3.2 `
  --agents 24 `
  "Build, review, test, and document this feature"
```

For a broad decomposable mission, NEXUS can coordinate the full 200-agent logical team while limiting simultaneous local model calls:

```powershell
.\.venv\Scripts\nexus-portable.exe swarm `
  --provider ollama `
  --model llama3.2 `
  --agents 200 `
  --max-parallel 8 `
  "Audit and prepare this application for production"
```

A 200-agent mission does **not** mean 200 unrestricted simultaneous processes. The scheduler separates logical team size from physical concurrency to avoid exhausting RAM/VRAM or making a workstation slower. Specialists cover architecture, frontend, backend, APIs, database, security, DevOps, QA, testing, debugging, performance, UX, accessibility, research, evidence, product, integration, release, observability, data, AI engineering, code review, migrations, CI/CD, compliance, and related roles. A lead orchestrator synthesizes their work into one dependency-aware result. See `docs/MULTI_AGENT_SWARM.md`.

## Configure Ollama for real model-driven planning

Ollama exposes an OpenAI-compatible chat completions endpoint at `/v1/chat/completions`. Install Ollama, pull a suitable model (`ollama pull llama3.2`), and set:

```dotenv
NEXUS_MODEL_BASE_URL=http://localhost:11434/v1
NEXUS_MODEL_NAME=llama3.2
NEXUS_MODEL_API_KEY=
```

Register a new project with `"provider":"openai_compatible"`. The model can propose actions from that project's allowlisted tools; outputs are validated and tool use is recorded. This is a starter JSON-action protocol, not a guarantee that every local model will follow instructions reliably. If NEXUS itself runs in Docker and Ollama runs on your host, use `http://host.docker.internal:11434/v1` and enable Docker host mapping as needed on Linux.

## Approvals, security and operating limits

`project_note` is a **write** tool and will always return `pending_approval` when proposed. No model can bypass the fixed server-side approval rule. New tools must explicitly declare their approval classification before release.

Before public deployment, add TLS, a reverse proxy, rate limiting, production-grade secret management, centralized audit logging, PostgreSQL, a durable queue and per-tenant execution quotas. SQLite and the in-process lock are intended for a single process only. Run only one Uvicorn worker. Do **not** expose `NEXUS_DEV_MODE=true` publicly. Avoid storing model/API keys in run events, user prompts or GitHub.

## Quality gates

```bash
pip install -e '.[dev]'
NEXUS_DEV_MODE=true pytest -q
ruff check nexus_os tests examples
```

CI runs both checks on push and pull request. Offline tests cover authentication, tenant isolation, real calculator execution, bogus tool rejection, approval and denial, deliberate demo limitations, portable-provider registry checks, and 200-agent swarm construction/execution behavior. Integration tests against a **real** Ollama/hosted model and existing Lucio/Ember repositories remain a separate acceptance gate.

## Roadmap

1. **v0.1 (current foundation):** secure starter, offline demo, local LLM adapter, Python/TypeScript clients and CI.
2. **v0.2:** adaptive multi-agent execution, authenticated GitHub adapter, sandboxed coding worker, tests with evidence, cancellation and resumable background queue.
3. **v0.3:** MCP tool gateway, PostgreSQL, event streaming, scoped skills/agent packs, model evaluation and budget router.
4. **v1.0:** verified Lucio and Ember integrations, tenancy security audit, observability, migrations, release and rollback playbooks.

See `docs/ARCHITECTURE.md`, `docs/INTEGRATION.md`, `docs/PORTABLE_LLM_RUNTIME.md`, and `docs/MULTI_AGENT_SWARM.md` for deeper design and phased integration instructions.
