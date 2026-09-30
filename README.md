# Nexus Universe Agents · v0.1.0

> Formerly **NEXUS Agentic OS**. Existing repository, package, import, CLI, and environment-variable identifiers remain temporarily unchanged for backward compatibility. See `docs/BRANDING.md`.

**One reusable agent runtime; separate permissions and agent packs for Lucio AI Platform, Ember, and future applications.** This repository is independent of your application repositories. It is a **tested development starter**, not a claim of a production-ready autonomous app builder.

## Delivered in v0.1

- FastAPI REST API with Swagger UI (`/docs`), health endpoint and independently registered projects.
- Strong, randomly generated per-project API keys (only their SHA-256 hashes are stored), a separate admin token, and enforcement of tenant isolation on every protected endpoint.
- Project-specific enabled agents (`general`, `builder`, `research`), allowed tools, model provider and execution budgets.
- Bounded orchestration loop, durable SQLite run traces, explicit approval before writing project notes, denied-tool checks and recoverable pending approvals.
- Fully offline deterministic `demo` provider with a **real calculator** and UTC tool.
- OpenAI-compatible provider configurable for local Ollama or supported hosted endpoints.
- Portable local/CLI runtime for Ollama and user-authenticated coding/chat CLIs.
- Adaptive multi-agent swarm coordinator supporting **1-200 logical specialists per mission** with bounded physical concurrency, isolated failures, evidence compaction, and lead-agent synthesis.
- Dependency-aware Execution Swarm with approval gates, verification hooks, restricted process workers, and failure propagation.
- Isolated Git worktree manager and parallel coding coordinator for per-task branches/workspaces.
- Authenticated GitHub CLI adapter for draft PR creation and CI-check inspection.
- Python and server-side TypeScript SDKs, Docker, Docker Compose, examples, docs, and CI tests.

## Architecture

```text
Lucio AI / Ember / Future Apps
            |
            v
    Nexus Universe Agents
            |
     Mission Analyzer
            |
     Adaptive Swarm Planner
            |
  1..200 specialist agents
            |
    Lead synthesis/evidence
            |
    Dependency-aware DAG
            |
     Isolated Git worktrees
       /       |       \
 coding A   coding B   coding C
       \       |       /
       tests / review
            |
      verified commits
            |
       draft GitHub PRs
            |
       CI + approval gates
            |
        merge / release
```

## Quick start — local smoke test

```bash
git clone https://github.com/lois4801/NEXUS-Agentic-OS.git
cd NEXUS-Agentic-OS
python -m venv .venv
# PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -e '.[dev]'
```

Install/run the portable helper:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
.\.venv\Scripts\nexus-portable.exe doctor
```

Use an API-key-free local Ollama model:

```powershell
ollama pull llama3.2
.\.venv\Scripts\nexus-portable.exe ask --provider ollama --model llama3.2 "Design a feature plan"
```

Use swarm mode:

```powershell
.\.venv\Scripts\nexus-portable.exe swarm `
  --provider ollama `
  --model llama3.2 `
  --agents 24 `
  "Build, review, test, and document this feature"
```

For large decomposable work:

```powershell
.\.venv\Scripts\nexus-portable.exe swarm `
  --provider ollama `
  --model llama3.2 `
  --agents 200 `
  --max-parallel 8 `
  "Audit and prepare this application for production"
```

A 200-agent mission means up to 200 logical specialists, not 200 unrestricted simultaneous shell processes.

## Parallel coding

Nexus Universe Agents now includes the first parallel coding layer:

- one Git branch/worktree per writable task (`nua/task-<id>`)
- bounded parallel coding-agent runs
- workspace containment
- no shell evaluation of model output
- dependency-aware execution
- verification hooks
- authenticated `gh`-based draft PR publishing

See `docs/PARALLEL_CODING.md` and `docs/EXECUTION_SWARM.md`.

## Security boundaries

State-changing GitHub/filesystem/terminal/deployment/database workers remain permission-scoped and approval-gated. Local process execution uses argv calls, executable allowlists, working-directory containment, timeouts, and output caps. Model output is always treated as untrusted input.

Nexus Universe Agents does not bypass provider authentication. Local models can run without provider API keys; hosted model tools remain responsible for their own authentication, subscriptions, licensing, and terms.

## Quality gates

```bash
pip install -e '.[dev]'
NEXUS_DEV_MODE=true pytest -q
ruff check nexus_os tests examples
```

## Roadmap

1. **v0.1 foundation:** secure starter, offline/local model runtime, SDKs, CI.
2. **v0.2 Execution Swarm:** adaptive 200-agent coordination, isolated Git worktrees, bounded coding workers, verification, CI, and PR generation.
3. **v0.3:** MCP gateway, PostgreSQL, event streaming, resumable distributed queues, scoped skills/agent packs, model evaluation, and budget routing.
4. **v1.0:** verified Lucio and Ember integrations, tenancy/security audit, observability, migrations, release, and rollback playbooks.

See `docs/BRANDING.md`, `docs/ARCHITECTURE.md`, `docs/INTEGRATION.md`, `docs/PORTABLE_LLM_RUNTIME.md`, `docs/MULTI_AGENT_SWARM.md`, `docs/EXECUTION_SWARM.md`, and `docs/PARALLEL_CODING.md`.
