# Nexus Starship Guardians · v0.2-dev

**One reusable Guardian runtime; separate permissions and Guardian packs for Lucio AI Platform, Ember, and future applications.** This repository is independent of your application repositories. It is a tested development starter, not a claim of a production-ready autonomous app builder.

## Current capabilities

- FastAPI REST API with Swagger UI (`/docs`), health endpoint and independently registered projects.
- Strong, randomly generated per-project API keys, a separate admin token, and tenant-isolation enforcement.
- Project-specific enabled Guardians, allowed tools, model provider, and execution budgets.
- Portable local/CLI runtime for Ollama and user-authenticated coding/chat CLIs.
- Adaptive Guardian swarm coordinator supporting **1–200 logical Guardians per mission** with bounded physical concurrency, isolated failures, evidence compaction, and lead-Guardian synthesis.
- Canonical **30-Guardian Artificial Architecture team** spanning command, learning, code quality, source control, verification, execution, repair, and operations.
- Automatic cross-run Guardian learning through episodic memory, reflection, evaluation evidence, and relevant-lesson retrieval.
- Server-wide learning recorder so terminal API runs feed the same Guardian learning system, explicitly scored as execution reliability rather than semantic answer quality.
- **Synthetic Evaluation Lab** with provenance-tracked evaluation cases, deterministic acceptance judging, failure taxonomy, baseline-vs-candidate comparison, and promotion gates that block critical regressions.
- Dependency-aware Execution Swarm with approval gates, verification hooks, restricted process workers, and failure propagation.
- Isolated Git worktree manager and parallel coding coordinator for per-task branches/workspaces.
- Automatic deterministic diff review for merge markers, possible secrets, TLS bypass, unfinished markers, and oversized diffs.
- Safe Git rebase/conflict detection with conflict enumeration and abort support; no blind auto-resolution.
- Browser and API verification workers.
- Durable SQLite job queue with bounded retries and interrupted-job recovery.
- Provenance-tracked SHA-256 evidence bundles.
- Verified bounded auto-repair loop that records verification evidence and automatically learns from every configured run.
- Authenticated GitHub CLI adapter for draft PR creation and CI-check inspection.
- Structured file-edit worker with workspace containment and stale-file protection.
- Python and server-side TypeScript SDKs, Docker, Docker Compose, examples, docs, and CI tests.

## Architecture

```text
Lucio AI / Ember / Future Apps
            |
            v
   Nexus Starship Guardians
            |
      Mission Analyzer
            |
   30-Guardian Architecture Team
            |
     Guardian Swarm Planner
            |
    1..200 Guardians
            |
  prior lessons + evidence
            |
   Lead synthesis / critique
            |
   Dependency-aware DAG
            |
    Isolated Git worktrees
       /       |       \
 coding A   coding B   coding C
       \       |       /
   diff review / rebase safety
            |
 browser + API + unit tests
            |
     verified auto-repair
            |
      evidence bundle
            |
     reflection + memory
            |
   Synthetic Evaluation Lab
       /              \
 baseline           candidate
       \              /
       promotion gates
            |
       draft GitHub PRs
            |
       CI + approval gates
            |
        merge / release
```

## Quick start

```bash
git clone https://github.com/lois4801/NEXUS-Agentic-OS.git
cd NEXUS-Agentic-OS
python -m venv .venv
# PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -e '.[dev]'
```

> The GitHub repository URL is still the existing repository address. The canonical product and package name is **Nexus Starship Guardians**.

Install/run the portable helper:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
.\.venv\Scripts\nexus-guardians.exe doctor
```

Use an API-key-free local Ollama model:

```powershell
ollama pull llama3.2
.\.venv\Scripts\nexus-guardians.exe ask --provider ollama --model llama3.2 "Design a feature plan"
```

Use Guardian swarm mode:

```powershell
.\.venv\Scripts\nexus-guardians.exe swarm `
  --provider ollama `
  --model llama3.2 `
  --guardians 30 `
  "Build, review, test, repair, and document this feature"
```

For large decomposable work:

```powershell
.\.venv\Scripts\nexus-guardians.exe swarm `
  --provider ollama `
  --model llama3.2 `
  --guardians 200 `
  --max-parallel 8 `
  "Audit and prepare this application for production"
```

A 200-Guardian mission means up to 200 collaborating logical specialists, not 200 unrestricted simultaneous shell processes.

## Automatic Guardian learning

Every portable swarm run now:

1. retrieves relevant lessons from prior missions;
2. injects those lessons into Guardian context;
3. runs the Guardian swarm and lead synthesis;
4. records reliability/evidence for the run;
5. asks a Reflection Guardian for one reusable lesson;
6. stores the episode + lesson for future missions.

The REST/server execution path also records terminal run outcomes into the shared learning store. Those server scores are labeled `execution-reliability`; they are not treated as proof that an answer is semantically correct.

Default memory path: `.nexus/guardian_learning.jsonl` for the portable CLI and `./data/guardian_learning.jsonl` for the server. Override with `NEXUS_LEARNING_PATH`.

This is **memory + reflection + evaluation**, not live self-modification of model weights. `JsonlLearningStore.export_sft_pairs()` can prepare high-scoring episodes for a separate curated offline SFT/LoRA pipeline.

## Synthetic Evaluation Lab

The lab compares baseline and candidate Guardian/model/configuration runs on provenance-tracked synthetic and regression cases. A candidate is promoted only when configured gates pass, including no critical regressions, minimum pass rate, no pass-rate regression versus baseline, and the required score delta.

Evaluation reports are stored as append-only JSONL. Set `NEXUS_EVALUATION_PATH` to choose the server-side evaluation store. See `docs/SYNTHETIC_EVALUATION_LAB.md`.

## Parallel coding and verified repair

Nexus Starship Guardians includes:

- one Git branch/worktree per writable task (`nsg/task-<id>`)
- bounded parallel coding-Guardian runs
- structured file editing with stale-file protection
- deterministic diff review before promotion
- safe rebase/conflict detection
- browser/API/test verification workers
- bounded verified repair loops
- durable resumable jobs
- SHA-256 evidence bundles
- authenticated `gh`-based draft PR publishing

See `docs/PARALLEL_CODING.md`, `docs/EXECUTION_SWARM.md`, and `docs/SELF_LEARNING_GUARDIANS.md`.

## Security boundaries

State-changing GitHub/filesystem/terminal/deployment/database workers remain permission-scoped and approval-gated. Local process execution uses argv calls, executable allowlists, working-directory containment, timeouts, and output caps. Model output is always treated as untrusted input.

Nexus Starship Guardians does not bypass provider authentication. Local models can run without provider API keys; hosted model tools remain responsible for their own authentication, subscriptions, licensing, and terms.

## Quality gates

```bash
pip install -e '.[dev]'
NEXUS_DEV_MODE=true pytest -q
ruff check nexus_os tests examples
```

## Roadmap

1. **v0.1 foundation:** secure starter, offline/local model runtime, SDKs, CI.
2. **v0.2 Execution + Learning Swarm:** adaptive 200-Guardian coordination, 30-Guardian architecture team, isolated Git worktrees, automatic diff review, safe rebase handling, browser/API verification, resumable jobs, evidence bundles, verified auto-repair, automatic cross-run learning, server-wide learning, and baseline-gated synthetic evaluation.
3. **v0.3:** PostgreSQL/distributed queue backend, MCP gateway, multi-judge evaluation, failure-taxonomy dashboard, automatic regression-case curation, cost routing, and production observability.
4. **v1.0:** verified Lucio and Ember integrations, tenancy/security audit, release automation, rollback playbooks, and governed offline model-improvement pipeline.

See `docs/BRANDING.md`, `docs/ARCHITECTURE.md`, `docs/INTEGRATION.md`, `docs/PORTABLE_LLM_RUNTIME.md`, `docs/MULTI_GUARDIAN_SWARM.md`, `docs/EXECUTION_SWARM.md`, `docs/PARALLEL_CODING.md`, `docs/SELF_LEARNING_GUARDIANS.md`, and `docs/SYNTHETIC_EVALUATION_LAB.md`.
