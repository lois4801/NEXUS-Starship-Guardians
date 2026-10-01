# Nexus Starship Guardians — Learnings and Retrospective

This file is part of the default repository update discipline. Meaningful changes should add a concise entry when they reveal reusable engineering lessons, regressions, CI failures, or architecture decisions.

## 2026-10-01 — Current State Graph and release/package discipline

### What changed

- made the Current State Graph a required repository artifact;
- embedded an animated current-state SVG in the README and Visual Gallery;
- promoted the runtime from `0.3.0.dev0` to formal `0.3.0` while keeping the plugin at the same version;
- added pre-merge wheel/sdist build verification;
- added post-merge GitHub Release automation;
- added GHCR Docker package publication with semantic version aliases.

### Reusable engineering lessons

1. **Architecture should have one obvious current-state view.** Deep subsystem docs are useful, but readers and maintainers also need a single graph that says what the system is *now*.
2. **A graph is a contract only if CI and process keep it present.** The repository now tests that the Current State document and visual exist; future architecture PRs are expected to update them when flow changes.
3. **A release should be reproducible from repository state.** Release assets are built from the merged commit, not uploaded from an unknown local machine.
4. **Packages and releases serve different jobs.** GitHub Releases hold human-facing notes and Python build artifacts; GHCR holds the deployable Docker package.
5. **Version drift is a compatibility risk.** Runtime and plugin versions are checked together before release so a plugin snapshot cannot silently claim compatibility with a different runtime version.
6. **Publishing should happen only after the normal verification gates.** The release workflow runs from merged `main`; the pull request must first pass Python, Ruff, pytest, live HTTP, Docker, PostgreSQL, plugin, and release-artifact checks.
7. **Release automation needs least privilege.** The workflow requests `contents: write` for tags/releases and `packages: write` for GHCR, rather than broad repository administration access.

### Remaining verification boundary

The release workflow itself still needs its first real execution from merged `main` to prove GitHub tag creation, Release asset upload, and GHCR publication under repository token permissions. Those outcomes must be verified after merge before calling the release channel operational.

## 2026-10-01 — Mission Intelligence and cross-project routing evidence

### What changed

- added deterministic mission classification with explicit mission kinds, confidence, reasons, and bounded Guardian team sizes;
- added a capability/tool map that converts mission language into inspectable routing requirements;
- added an independent alternate-model judge adapter with strict JSON validation;
- added correlated Guardian/mission/project telemetry context;
- added persistent cross-project Guardian performance aggregation;
- added unit coverage and an animated routing visual.

### Reusable engineering lessons

1. **Classification should produce inspectable requirements, not hidden intuition.** Routing decisions are easier to debug when mission type, capabilities, tools, team bounds, confidence, and rule matches are explicit data.
2. **Capability detection is not authorization.** A mission may require a browser, database, or integration tool, but only Guardians already granted that tool may be selected.
3. **Unknown missions should degrade conservatively.** The default capability is `general-engineering`; the classifier should not hallucinate a specialist domain just to appear confident.
4. **Model judges need a strict interface.** An alternate model must return typed JSON; malformed or loosely typed outputs fail closed instead of becoming evaluation evidence.
5. **Independent model judgment supplements tests rather than replacing them.** Deterministic and evidence judges remain mandatory in the multi-judge report.
6. **Correlation IDs should cross nested Guardian work.** API, queue, Guardian, verification, and evidence events need one mission lineage before a telemetry backend can be genuinely useful.
7. **Cross-project learning must preserve provenance.** Aggregate performance can improve routing across Lucio, Ember, Nexus Code, and future projects while still retaining project identity and respecting project permissions.

### Current verification boundary

This phase adds deterministic classification/routing primitives and local persistent cross-project metrics. It does not yet let an LLM silently rewrite mission requirements or grant permissions. Hosted alternate-model judges still require the provider's legitimate authentication when used outside deterministic tests.

### Next targets after this phase is green

- wire Mission Classifier output directly into the server/orchestration mission path;
- add model-assisted classification as a proposal checked by deterministic policy;
- add queue and verification span emission using the shared correlation ID;
- benchmark classifier/router strategies in the Guardian Intelligence Lab;
- add gated Railway/Supabase/MCP/Lucio/Ember/Nexus Code integration contracts.

## 2026-10-01 — Production verification, persistence, and observability

### What changed

- added live Uvicorn startup plus `/health` verification over real HTTP;
- added Docker image build, container healthcheck, and host-side health verification;
- added Compose configuration validation;
- added SQLite-backed Guardian Registry persistence;
- added verified failure → Regression Corpus wiring;
- added deterministic provider contract tests;
- added OpenTelemetry HTTP span instrumentation;
- added animated README and production-verification SVG visuals.

### Reusable engineering lessons

1. **Import success is weaker evidence than process success.** A FastAPI module can import while Uvicorn startup, networking, middleware, filesystem permissions, or environment loading still fail. CI should exercise the live process.
2. **Container health belongs inside the image.** A deployment should expose a machine-readable health contract that Docker/Compose can use without external knowledge of the application internals.
3. **Routing intelligence needs durable evidence.** Guardian success, quality, cost, and latency metrics lose value if they disappear at every restart; persistence is part of adaptive routing, not an optional dashboard feature.
4. **Learning memory needs an evidence gate.** A system that stores every suspected failure will contaminate itself. Only verified failures are eligible for automatic regression promotion.
5. **Provider adapters need contract tests without hosted credentials.** Deterministic mocks can prove output shape, model/provider identity, and error propagation while keeping CI independent of external subscriptions.
6. **Observability should be instrumented centrally but exported per deployment.** The runtime can emit OpenTelemetry spans without hard-coding a vendor or backend.
7. **Visuals are part of the engineering contract.** Animated/architecture graphics should evolve in the same pull request as the flow they explain.

### Verification boundary

This phase is designed to prove local/runtime production surfaces in GitHub Actions: Python compatibility, live HTTP, Docker, PostgreSQL, provider contracts, persistence behavior, and regression-learning rules. Hosted integrations still require their own credentialed/gated tests.

### Next targets after this phase is green

- Mission Classifier that emits explicit capability requirements;
- alternate-model judge adapters;
- Guardian/queue trace correlation and structured metrics;
- persistent cross-project performance aggregation;
- gated Railway/Supabase/MCP/Lucio/Ember/Nexus Code integration suites;
- release/rollback evidence automation.

## 2026-10-01 — Compatibility and production hardening

### What changed

- expanded CI to Python 3.11, 3.12, and 3.13;
- added canonical and legacy CLI smoke tests;
- added REST API import/title smoke testing;
- added real PostgreSQL 16 service integration testing;
- documented compatibility guarantees for retained technical identifiers;
- expanded environment configuration examples;
- added a production-verification workflow visual.

### What the hardening run found

1. **Brand renaming and interface renaming are not the same thing.** Product-facing naming can move to Nexus Starship Guardians while technical interfaces such as `nexus_os`, `nexus-portable`, REST v1 `agent`/`agents`, and `NEXUS_*` remain compatibility surfaces. Mechanical renaming would create avoidable breakage.
2. **A single Python version was not enough evidence.** The package, tests, CLI, and REST import now pass on Python 3.11, 3.12, and 3.13.
3. **Real database tests reveal assumptions unit tests cannot.** The first live PostgreSQL recovery test failed because it mixed real enqueue time with a synthetic claim clock. PostgreSQL behaved correctly; the test assumption was wrong.
4. **Synthetic time must be internally consistent.** Time-sensitive queue tests now set `available_at`, claim time, expiry time, and recovery time from one synthetic timeline.
5. **Compatibility deserves tests, not comments.** Both `nexus-guardians` and the legacy `nexus-portable` CLI are exercised in CI, and the retained `nexus_os` namespace is imported explicitly.
6. **Production claims should match tested scope.** The hardening matrix proves install/import/CLI/API-health/unit/PostgreSQL queue compatibility, but does not prove every hosted model, browser provider, Railway deployment, Supabase project, or MCP service without those environments and credentials.

### Verification result

The final hardening code-bearing CI run passed all four jobs:

- Python 3.11 — passed;
- Python 3.12 — passed;
- Python 3.13 — passed;
- PostgreSQL 16 integration — passed.

Within the Python matrix, package installation, Ruff, pytest, canonical CLI, legacy CLI, and REST API import/title all passed. The PostgreSQL job passed queue initialization, ownership/claim behavior, heartbeat, completion, and expired-lease recovery against a real database container.

### Reusable lesson

**Preserve compatibility first, rename safely second, and verify behavior on the real dependency whenever practical.** A branding migration should not force a breaking runtime migration unless there is a deliberate versioned deprecation plan.

### Next hardening targets

- add Docker image build/start/health CI;
- add FastAPI HTTP smoke testing through a live uvicorn process;
- add persisted Guardian Registry integration tests;
- add provider-contract tests with deterministic fake providers;
- add optional gated tests for Railway/Supabase/MCP integrations when credentials are available;
- define a v1 compatibility/deprecation policy for legacy REST v1 field names.

## 2026-09-30 — Guardian Intelligence + Adaptive Execution phase

### What changed

- added failure taxonomy and promotion policy;
- added multi-judge evaluation aggregation;
- added automatic append-only regression corpus;
- added Guardian Intelligence Lab and strategy tournament;
- added Guardian capability/performance registry;
- added adaptive Guardian routing;
- added PostgreSQL distributed lease-queue foundation;
- added GitHub-rendered architecture/process diagrams and subsystem documentation;
- added dedicated unit tests for each new layer.

### Learnings applied from earlier work

1. **Verification must precede completion claims.** Earlier CI runs caught Ruff errors that implementation summaries alone would have missed. New promotion/evaluation logic therefore treats deterministic evidence as a required judge.
2. **Stale writes must fail safely.** GitHub rejected stale blob-SHA updates during prior documentation changes. This reinforced the existing stale-file/hash protections and the general rule to refresh state before replacement writes.
3. **Logical Guardians and physical workers are different resources.** Up to 200 specialist roles can collaborate, while process/model concurrency remains bounded to protect local and hosted systems.
4. **Self-learning is memory + reflection + evaluation, not live weight mutation.** Production traces can become curated offline training/evaluation material, but model promotion requires a fixed baseline and regression gate.
5. **One judge is insufficient.** Deterministic tests and evidence checks should not be overridden by a model giving itself a high semantic score.
6. **Failures should compound into defenses.** Verified failure/repair episodes should create deduplicated regression cases so future strategies face the same failure again during evaluation.
7. **Routing should be evidence-driven.** Guardian selection now has a registry foundation for capabilities, success rate, quality, cost, and latency rather than relying only on role labels.
8. **Distributed execution needs leases, not optimistic ownership.** PostgreSQL `FOR UPDATE SKIP LOCKED`, heartbeats, retry limits, and lease recovery form the initial multi-worker contract.

### CI learning from this phase

The first combined v0.3 development runs did not pass immediately. GitHub Actions found five Ruff issues before pytest could run. Four were ordinary style findings and were corrected directly. A final `I001` import-order finding in `distributed_queue.py` persisted across multiple import arrangements, including the ordering suggested by Ruff itself. Rather than disable import-order checking globally, the final implementation scopes the `I001` exemption to that one PostgreSQL queue file while leaving every other Ruff rule and the repository-wide Ruff gate active.

**Reusable lesson:** quality gates should fail narrowly, fixes should follow exact evidence, and an exceptional lint suppression should be local, documented, and never used to hide behavioral failures.

After that containment, the latest code-bearing CI run completed all three gates successfully:

- editable package installation: passed;
- Ruff: passed;
- pytest: passed.

### Current verification boundary

Python unit tests and Ruff are green for the implemented intelligence/routing/distributed foundations. The PostgreSQL adapter has deterministic/unit coverage, but a live PostgreSQL service is still required to verify concurrent worker claims and transaction behavior under real database conditions.

### Next regression/evaluation targets

- add a real PostgreSQL GitHub Actions service test;
- persist Guardian Registry metrics beyond process memory;
- connect regression cases automatically to verification failures;
- add alternate-model judge adapters;
- add a Mission Classifier that proposes explicit capability requirements;
- benchmark router strategies on quality, cost, and latency before promotion.

## Entry template

```text
Date:
Feature / mission:
What changed:
Tests/evidence:
What failed:
How it was fixed:
Reusable lesson:
Regression case added:
Architecture/visual docs updated:
Remaining verification boundary:
```
