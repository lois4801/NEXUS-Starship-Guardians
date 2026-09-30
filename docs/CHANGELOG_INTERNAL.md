# Nexus Starship Guardians — Internal Change Log

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
