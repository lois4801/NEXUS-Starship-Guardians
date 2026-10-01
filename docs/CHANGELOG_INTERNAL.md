# Nexus Starship Guardians — Internal Change Log

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
