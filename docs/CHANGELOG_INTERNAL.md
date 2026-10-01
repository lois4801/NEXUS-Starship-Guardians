# Nexus Starship Guardians — Internal Change Log

## 2026-10-01 — v0.4.0 Live Mission Runtime and controlled integration policy

### Added

- `MissionRuntime` that moves deterministic Mission Intelligence into the live REST execution path;
- one durable `mission_intelligence` event per run before provider execution;
- project-scoped `POST /v1/projects/{project_id}/mission-plan` endpoint;
- `gateway_tools` project configuration kept separate from local REST v1 `allowed_tools`;
- `ControlledToolGateway` permission policy for browser/API/database/test/security/terminal/observability/model/integration capabilities;
- collective adaptive routing so multiple Guardians can jointly cover a mission's capabilities and explicit tool requirements;
- integration-readiness contracts and API for Lucio AI Platform, Ember, Nexus Code, Railway, and Supabase;
- explicit `connected=false` semantics for readiness-only external contracts;
- v0.4 plugin manifests and plugin documentation;
- dedicated live mission runtime/gateway/integration regression tests;
- `docs/LIVE_MISSION_RUNTIME.md`;
- updated canonical Current State Graph and animated SVG.

### Compatibility policy

REST v1 `agent` / `agents`, the `nexus_os` namespace, `NEXUS_*` environment variables, and the `nexus-portable` CLI alias remain supported. Mission Intelligence is advisory for existing v1 run execution in v0.4; insufficient planning evidence is recorded but does not silently break an existing client.

### Permission policy

Capability detection never grants access. High-level external tools require explicit project enablement plus Guardian permission, and the gateway remains a policy layer until a real authenticated adapter exists.

### Release target

- runtime: `0.4.0`;
- portable plugin manifest: `0.4.0`;
- Codex compatibility manifest: `0.4.0`;
- expected post-merge outputs: GitHub Release `v0.4.0` plus GHCR `0.4.0`, `0.4`, and `latest` images after the complete CI/release workflow succeeds.

## 2026-10-01 — Formal v0.3.0 release, Current State Graph, and package automation

### Added

- canonical `docs/CURRENT_STATE.md` architecture snapshot;
- animated `docs/assets/current-state-graph.svg` embedded in the README and Visual Gallery;
- permanent rule that meaningful architecture changes must update the Current State Graph in the same pull request;
- `docs/RELEASES_AND_PACKAGES.md` with semantic versioning and release/package policy;
- automated GitHub Release workflow producing Python wheel and source distribution assets;
- automated GitHub Packages publication through GHCR with version, minor, and `latest` Docker tags;
- CI release-artifact smoke job that builds wheel/sdist before merge and verifies runtime/plugin version alignment;
- release metadata regression tests.

### Release target

- runtime package version promoted from `0.3.0.dev0` to `0.3.0`;
- plugin manifest remains aligned at `0.3.0`;
- first formal release target is `v0.3.0`.

### Repository policy

Every meaningful update should keep code, tests, docs, Current State Graph, relevant visuals, learnings, changelog, and release/package metadata synchronized. GitHub Releases and GHCR packages are outputs of the verified release path, not manual side artifacts.

## 2026-10-01 — Mission Intelligence and cross-project routing evidence

### Added

- deterministic `MissionClassifier` with mission kind, confidence, reasons, and bounded Guardian team sizing;
- `CapabilityMap` for explicit capability/tool requirements;
- `AlternateModelJudge` with strict structured JSON validation;
- correlated Guardian execution telemetry with reusable correlation IDs;
- persistent cross-project Guardian performance aggregation;
- dedicated tests for classifier, capability mapping, alternate-model judging, telemetry correlation, and cross-project metrics;
- animated Mission Intelligence + Adaptive Routing visual;
- `MISSION_INTELLIGENCE.md` and Visual Gallery updates.

### Architecture policy

Mission interpretation may propose capabilities, but it never grants tool permissions. Adaptive routing must continue to enforce each Guardian's explicit allowlist. Alternate-model judgments are additional semantic evidence and never replace deterministic/evidence judges.

## 2026-10-01 — Production verification, persistence, and observability

### Added

- live Uvicorn HTTP startup and `/health` CI verification;
- Docker image build, container startup, Docker `HEALTHCHECK`, and host-side HTTP verification;
- Docker Compose configuration validation;
- `SQLiteGuardianRegistry` for persisted Guardian profiles and performance metrics;
- `RegressionLearningBridge` to promote only verified failures into the Regression Corpus;
- deterministic provider contract tests for command-CLI and Ollama adapters;
- OpenTelemetry HTTP request span instrumentation foundation;
- animated Nexus Starship Guardians hero SVG;
- animated production-verification motion graph;
- production-verification and visual-gallery documentation.

### Verification targets

The phase is expected to pass the existing Python 3.11/3.12/3.13 matrix and PostgreSQL 16 integration job plus the new live-Uvicorn and Docker jobs before merge.

### Architecture policy

Production readiness claims must be backed by an environment that reproduces the claimed behavior. A successful Python import is not equivalent to a live HTTP service, and unit SQL tests are not equivalent to a real PostgreSQL transaction. Verified failures may become regression knowledge; unsupported suspicions may not.

## 2026-10-01 — Compatibility and production hardening

### Added

- Python CI matrix for 3.11, 3.12, and 3.13;
- canonical `nexus-guardians` CLI smoke test;
- legacy `nexus-portable` compatibility smoke test;
- clean-process REST API import/title smoke test;
- explicit compatibility contract for the retained `nexus_os` namespace and REST v1 wire fields;
- live PostgreSQL 16 GitHub Actions service testing;
- PostgreSQL claim/heartbeat/complete and expired-lease recovery integration tests;
- expanded environment template for learning, evaluation, and PostgreSQL settings;
- compatibility and production-verification workflow documentation.

### Compatibility policy

Nexus Starship Guardians is the canonical product name. Existing technical interfaces such as `nexus_os`, `nexus-portable`, REST v1 `agent`/`agents` fields, and `NEXUS_*` environment variables remain supported intentionally until a versioned migration can remove them without breaking Lucio AI Platform, Ember, Nexus Code, scripts, SDKs, or deployed clients.

### Verification result

Latest hardening CI passed:

- Python 3.11: install, Ruff, pytest, canonical CLI, legacy CLI, REST import — passed;
- Python 3.12: install, Ruff, pytest, canonical CLI, legacy CLI, REST import — passed;
- Python 3.13: install, Ruff, pytest, canonical CLI, legacy CLI, REST import — passed;
- PostgreSQL 16: service health, queue initialization, claim/ownership, heartbeat, completion, and expired-lease recovery — passed.

A failed first PostgreSQL recovery test exposed a synthetic-clock mismatch in the test itself. The test now uses one consistent synthetic clock and passes against the real database service.

## 2026-09-30 — Intelligence, routing, and distributed execution expansion

### Added

- Guardian Intelligence Lab (`evaluation_lab.py`)
- Multi-Judge Evaluation (`multi_judge.py`)
- Promotion Gate (`promotion_gate.py`)
- Failure Taxonomy (`failure_taxonomy.py`)
- Automatic Regression Corpus (`regression_corpus.py`)
- Strategy Tournament (`strategy_tournament.py`)
- Guardian Capability Registry (`guardian_registry.py`)
- Adaptive Guardian Router (`adaptive_router.py`)
- PostgreSQL lease queue foundation (`distributed_queue.py`)
- dedicated tests for all modules above
- architecture and process workflow Mermaid diagrams
- subsystem documentation
- permanent learnings/retrospective log

### Default repository update rule

For every meaningful Nexus Starship Guardians change, update GitHub with the applicable combination of:

1. code;
2. tests;
3. documentation;
4. architecture/process visuals;
5. learnings/retrospective;
6. change log and verification status.

### Verification target

Run package installation, Ruff, and pytest in GitHub Actions. PostgreSQL concurrency remains an explicit integration-test target.
