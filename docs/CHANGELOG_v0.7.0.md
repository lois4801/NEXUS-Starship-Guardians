# Changelog — v0.7.0

## Adaptive Guardian Intelligence

- Added persistent `AdaptiveGuardianIntelligence` specialist-learning engine.
- Added ten specialist profiles: AI Architect, Software Platform Engineer, AI Developer, Coder Specialist, AI Engineer, Debugger Specialist, AI Scientist, AI Cloud Specialist, API Specialist, and AI Programmer Guardians.
- Added per-skill verified evidence: attempts, success rate, quality, benchmark pass/fail, critical regressions, confidence, recent trend, and adaptive score.
- Added automatic specialist training priorities for weak, uncertain, declining, or regression-prone capabilities.
- Added bounded adaptive routing evidence through `AdaptiveGuardianRouter` while preserving explicit tool authorization.
- Added `elite_specialist_team()` without breaking the canonical 30-Guardian Artificial Architecture team.

## Benchmark Replay

- Added `BenchmarkReplayEngine`.
- Added pending-candidate replay across selected strategies.
- Added replay pass/fail, score, failure category, replay count, and replay pass-rate evidence to Benchmark Vault candidates.
- Added optional `require_replay=True` guard for benchmark approval.
- Replay remains diagnostic evidence and cannot auto-approve permanent benchmark truth.

## Coverage Intelligence

- Added `CoverageIntelligence` and coverage snapshots.
- Added category coverage for architecture, platform, coding, debugging, AI/ML, evaluation, cloud, API, security, database, UI, deployment, tool-use, and reliability.
- Added critical-case counts, uncategorized case reporting, target-gap analysis, and snapshot-to-snapshot coverage deltas.

## Tests

- Added adaptive specialist team coverage tests.
- Added verified-learning enforcement tests.
- Added persistence, trend, regression-penalty, training-priority, and adaptive-routing tests.
- Added Benchmark Replay evidence tests.
- Added replay-required approval test.
- Added Coverage Intelligence classification and snapshot-growth tests.

## GitHub documentation and visuals

- Updated `README.md` to v0.7.0.
- Updated `docs/CURRENT_STATE.md`.
- Rebuilt the animated `docs/assets/current-state-graph.svg` for v0.7.0.
- Added animated `docs/assets/adaptive-guardian-intelligence.svg`.
- Added `docs/ADAPTIVE_GUARDIAN_INTELLIGENCE.md`.
- Updated `docs/VISUAL_GALLERY.md`.
- Added this v0.7.0 changelog and engineering learnings.

## Release metadata

- Python runtime version: `0.7.0`.
- ChatGPT plugin version: `0.7.0`.
- Codex plugin version: `0.7.0`.
- Expected stable release tag after merge: `v0.7.0`.
- Expected GHCR tags: `0.7.0`, `0.7`, `latest`.

## Safety and governance invariant

Automatic learning may update evidence, confidence, memory quality, replay evidence, training priorities, and bounded routing preference from verified outcomes. It may not silently mutate production model weights, grant credentials or permissions, approve benchmark truth, overwrite the fixed core corpus, or bypass promotion/release gates.
