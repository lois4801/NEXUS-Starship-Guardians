# Nexus Starship Guardians · v0.4.0

![Nexus Starship Guardians](docs/assets/nexus-starship-guardians-hero.svg)

**A reusable Guardian engineering runtime for Lucio AI Platform, Ember, Nexus Code, and future applications.** Nexus Starship Guardians coordinates bounded Guardian teams, live mission intelligence, permission-safe routing, verified execution, learning memory, evaluation, regression protection, and increasingly distributed work.

## Current State Graph

![Nexus Starship Guardians Current State](docs/assets/current-state-graph.svg)

The Current State Graph is maintained as architecture documentation and must change whenever the runtime flow materially changes. See [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md).

## Current capabilities

- FastAPI REST API with project-scoped authentication and approval gates.
- **Live Mission Runtime** that classifies each mission, maps capabilities/tools, selects a bounded Guardian team, and records a `mission_intelligence` event before normal REST v1 execution.
- **Controlled Tool Gateway policy** that separates high-level external-tool permissions from local runtime tools. Requirements never grant permissions by themselves.
- **Integration Readiness Contracts** for Lucio AI Platform, Ember, Nexus Code, Railway, and Supabase. Readiness does not claim a live external connection.
- Portable local/CLI runtime for Ollama and authenticated coding/chat CLIs.
- Adaptive swarm coordination for **1–200 logical Guardians** with bounded physical concurrency.
- Canonical **30-Guardian Artificial Architecture team**.
- Cross-run learning through episodic memory, reflection, evidence, and relevant-lesson retrieval.
- Isolated Git worktrees, parallel coding coordination, structured file editing, and automatic diff review.
- Browser/API/unit verification, bounded auto-repair, SHA-256 evidence bundles, and safe rebase/conflict handling.
- **Guardian Intelligence Lab** for fixed-corpus baseline/candidate evaluation.
- **Multi-Judge Evaluation** with deterministic, Guardian, alternate-model, and evidence judge types.
- **Promotion Gate** that blocks pass-rate regressions, insufficient score gains, critical regressions, and optional cost/latency overruns.
- **Failure Taxonomy + Automatic Regression Corpus** with verified-failure capture and deduplication.
- **Guardian Capability Registry + Adaptive Team Router** using capability/tool requirements and historical quality/reliability/cost/latency evidence; teams can collectively cover a mission.
- **Persistent Guardian Registry metrics** through SQLite so routing history survives process restarts.
- **Strategy Tournament** for comparing models, prompts, team structures, routing strategies, and repair policies on the same corpus.
- Durable SQLite queue for local development plus a **PostgreSQL distributed lease queue** using `FOR UPDATE SKIP LOCKED`, worker leases, heartbeats, retries, and expired-lease recovery.
- **OpenTelemetry HTTP instrumentation foundation** for live API request spans.
- CI compatibility matrix for **Python 3.11, 3.12, and 3.13**, canonical/legacy CLI smoke tests, live Uvicorn HTTP verification, Docker build/start/health verification, REST checks, release-artifact builds, and a real **PostgreSQL 16** service integration test.
- Reconciled **ChatGPT/Codex plugin v0.4** using current Guardian terminology, mission-planning guidance, integration-readiness guidance, and REST v1 compatibility fields.
- GitHub-rendered Mermaid diagrams plus animated SVG architecture/process visuals and a permanent engineering learnings/retrospective log.

## Releases and Packages

Nexus Starship Guardians publishes two complementary release outputs:

- **GitHub Releases** — semantic version, generated release notes, source, Python wheel, and Python source distribution.
- **GitHub Packages / GHCR** — versioned Docker images such as `ghcr.io/lois4801/nexus-starship-guardians:0.4.0` plus `0.4` and `latest` aliases.

Release/package automation is defined in [`.github/workflows/release.yaml`](.github/workflows/release.yaml). The versioning and release history is in [`docs/RELEASES_AND_PACKAGES.md`](docs/RELEASES_AND_PACKAGES.md).

## Production verification

![Production verification pipeline](docs/assets/production-verification-pipeline.svg)

Every meaningful change is expected to earn evidence from the applicable compatibility, live HTTP, Docker, PostgreSQL, provider-contract, persistence, mission-runtime, plugin, release-artifact, and learning gates before promotion. See [`docs/PRODUCTION_VERIFICATION.md`](docs/PRODUCTION_VERIFICATION.md).

## Architecture

```mermaid
flowchart TD
    A[Nexus Starship Guardians] --> B[Mission Intelligence]
    B --> C[Live Mission Runtime]
    C --> D[Capability Map]
    D --> E[Guardian Registry]
    E --> F[Adaptive Team Router]
    F --> G[Models]
    F --> H[Guardians]
    F --> I[Controlled Tool Gateway]

    X[Integration Readiness Contracts] --> I
    X --> X1[Lucio]
    X --> X2[Ember]
    X --> X3[Nexus Code]
    X --> X4[Railway]
    X --> X5[Supabase]

    G --> J[Execution DAG]
    H --> J
    I --> J
    J --> K[Verification Grid]
    K --> L[Auto Repair]
    L --> M[Evidence Bundle]
    M --> N[Multi-Judge Evaluation]
    N --> O[Regression Corpus]
    O --> P[Learning Memory]
    P --> Q[Promotion Gate]
    Q --> R[Release]

    S[ChatGPT / Codex Plugin] --> T[Nexus REST v1 Adapter]
    T --> C
    R --> U[GitHub Release]
    R --> V[GHCR Package]
```

Full visuals: [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md), [`docs/ARCHITECTURE_VISUALS.md`](docs/ARCHITECTURE_VISUALS.md), [`docs/PROCESS_WORKFLOWS.md`](docs/PROCESS_WORKFLOWS.md), and [`docs/VISUAL_GALLERY.md`](docs/VISUAL_GALLERY.md).

## Live mission planning

A project can opt into high-level gateway-tool capabilities independently from the existing local `allowed_tools` contract. For example, a project can enable `browser`, `api`, and `test` for mission planning without granting shell/database/integration permissions.

REST v1 now includes:

```text
POST /v1/projects/{project_id}/mission-plan
GET  /v1/projects/{project_id}/integrations/{integration_name}/readiness
```

A mission plan returns the mission kind, classifier confidence, capabilities, required tools, selected Guardians, missing capabilities/tools, project-disabled tools, and whether the plan is sufficient. Existing run creation remains compatible: `POST /v1/projects/{project_id}/runs` still accepts the v1 `agent` compatibility field, and every run records mission intelligence as trace evidence before provider execution.

See [`docs/LIVE_MISSION_RUNTIME.md`](docs/LIVE_MISSION_RUNTIME.md).

## Quick start

```bash
git clone https://github.com/lois4801/NEXUS-Starship-Guardians.git
cd NEXUS-Starship-Guardians
python -m venv .venv
# PowerShell: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -e '.[dev]'
```

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
.\.venv\Scripts\nexus-guardians.exe doctor
```

Example Guardian swarm:

```powershell
.\.venv\Scripts\nexus-guardians.exe swarm `
  --provider ollama `
  --model llama3.2 `
  --guardians 30 `
  "Build, review, test, repair, evaluate, and document this feature"
```

A 200-Guardian mission means up to 200 collaborating logical specialists, not 200 unrestricted shell processes.

## Compatibility contract

**Nexus Starship Guardians** is the canonical product name and `nexus-guardians` is the canonical CLI.

To avoid breaking existing integrations, these technical compatibility surfaces remain supported and tested:

- Python namespace: `nexus_os`
- Legacy CLI alias: `nexus-portable`
- Existing REST v1 wire fields such as `agent` / `agents`
- Existing `NEXUS_*` environment-variable prefix

These are compatibility interfaces, not the current product name. Removing them requires a versioned migration and regression coverage. See [`docs/COMPATIBILITY_AND_PRODUCTION_VERIFICATION.md`](docs/COMPATIBILITY_AND_PRODUCTION_VERIFICATION.md).

## Permission model

Mission classification and capability detection are **not authorization**. `ControlledToolGateway` keeps high-level tool policy explicit:

```text
mission requires a tool
        +
project enabled that tool
        +
selected Guardian is allowed that tool
        =
policy permits the adapter to be considered
```

Even then, a real external adapter must separately authenticate and execute the action. Nexus v0.4 does not pretend an MCP server, Railway account, Supabase project, browser session, database, or shell is connected merely because the mission requires one.

## Learning and evaluation

Automatic Guardian learning means **memory + reflection + evaluation**, not live production weight mutation. High-quality verified episodes can later be curated for offline SFT/LoRA; a candidate model or strategy should then beat the fixed evaluation baseline before promotion.

The Guardian Intelligence Lab compares candidates on pass rate, score, critical regressions, cost, and latency. Deterministic/evidence failures cannot be hidden by a high semantic score.

`RegressionLearningBridge` only turns verified failure evidence into persistent regression cases. Unsupported suspicions are not promoted into long-term learning truth.

## Adaptive routing

`GuardianRegistry` records capabilities, tool access, success rate, quality, cost, and latency. `AdaptiveGuardianRouter` chooses a bounded team from explicit `MissionRequirements` and can combine multiple Guardians whose capabilities/tool allowlists collectively satisfy the mission.

`SQLiteGuardianRegistry` persists profiles and performance metrics across process restarts. Historical performance never grants new tool permissions.

## Distributed execution

`PostgresGuardianQueue` implements the PostgreSQL multi-worker contract: queued jobs, `SKIP LOCKED` claims, leases, heartbeats, bounded retries, completion/failure transitions, and expired-lease recovery. The adapter uses an injected DB-API compatible connection factory.

The CI workflow launches a real PostgreSQL 16 service and verifies queue initialization, claim/ownership behavior, heartbeat, completion, and expired-lease recovery.

## Observability

Incoming FastAPI requests create OpenTelemetry spans with service name, request method, path, and response status. Run traces additionally preserve the mission-intelligence decision that preceded execution. Exporters remain deployment-specific rather than hard-coded into the runtime.

## Default repository update standard

Every meaningful Nexus Starship Guardians change should update the applicable repository evidence:

1. code;
2. automated tests;
3. documentation;
4. **Current State Graph plus relevant architecture/process visuals**;
5. learnings/retrospective;
6. change log and CI/verification status;
7. release/package metadata when the change is part of a versioned release.

## Quality gates

```bash
pip install -e '.[dev]'
ruff check nexus_os tests examples
NEXUS_DEV_MODE=true pytest -q
nexus-guardians doctor
nexus-portable doctor
```

GitHub Actions additionally validates:

- Python 3.11 / 3.12 / 3.13 compatibility;
- live Mission Runtime/API behavior;
- live Uvicorn startup and `/health` over HTTP;
- Docker Compose configuration;
- Docker image build, start and container health;
- PostgreSQL 16 queue behavior;
- deterministic provider contracts;
- plugin/runtime version alignment;
- wheel/source-distribution builds;
- release metadata and Current State Graph presence.

## Key documentation

- [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md)
- [`docs/LIVE_MISSION_RUNTIME.md`](docs/LIVE_MISSION_RUNTIME.md)
- [`docs/RELEASES_AND_PACKAGES.md`](docs/RELEASES_AND_PACKAGES.md)
- [`docs/VISUAL_GALLERY.md`](docs/VISUAL_GALLERY.md)
- [`docs/ARCHITECTURE_VISUALS.md`](docs/ARCHITECTURE_VISUALS.md)
- [`docs/PROCESS_WORKFLOWS.md`](docs/PROCESS_WORKFLOWS.md)
- [`docs/PRODUCTION_VERIFICATION.md`](docs/PRODUCTION_VERIFICATION.md)
- [`docs/COMPATIBILITY_AND_PRODUCTION_VERIFICATION.md`](docs/COMPATIBILITY_AND_PRODUCTION_VERIFICATION.md)
- [`docs/GUARDIAN_INTELLIGENCE_LAB.md`](docs/GUARDIAN_INTELLIGENCE_LAB.md)
- [`docs/MULTI_JUDGE_EVALUATION.md`](docs/MULTI_JUDGE_EVALUATION.md)
- [`docs/REGRESSION_CORPUS.md`](docs/REGRESSION_CORPUS.md)
- [`docs/GUARDIAN_REGISTRY.md`](docs/GUARDIAN_REGISTRY.md)
- [`docs/ADAPTIVE_ROUTING.md`](docs/ADAPTIVE_ROUTING.md)
- [`docs/DISTRIBUTED_EXECUTION.md`](docs/DISTRIBUTED_EXECUTION.md)
- [`docs/SELF_LEARNING_GUARDIANS.md`](docs/SELF_LEARNING_GUARDIANS.md)
- [`docs/LEARNINGS_AND_RETROSPECTIVE.md`](docs/LEARNINGS_AND_RETROSPECTIVE.md)
- [`docs/CHANGELOG_INTERNAL.md`](docs/CHANGELOG_INTERNAL.md)

## Roadmap

1. **Foundation:** secure project runtime, provider adapters, SDKs, CI.
2. **Execution + Learning:** 30/200-Guardian coordination, worktrees, verification, repair, evidence, cross-run learning.
3. **Intelligence + Routing:** multi-judge evaluation, regression corpus, promotion gates, strategy tournament, Guardian registry, adaptive routing, PostgreSQL distributed queue.
4. **Production verification:** multi-version compatibility, live HTTP, Docker health, PostgreSQL integration, persisted Guardian metrics, verified failure-to-regression wiring, provider contracts, release/package automation, and HTTP tracing.
5. **Live integration wave:** Mission Intelligence is now in the live REST path; next are authenticated adapter implementations for selected external systems plus queue/mission telemetry and governed MCP/tool execution.
6. **v1.0:** security/tenancy audit, governed release/rollback automation, and curated offline model-improvement pipeline.
