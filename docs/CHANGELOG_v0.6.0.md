# Nexus Starship Guardians — v0.6.0 Change Log

## Guardian Benchmark Vault

### Added

- `nexus_os.benchmark_vault.BenchmarkCandidate` with stable case identity, provenance, tags, severity, criticality, evidence reference, review status, reviewer, review note, and timestamps.
- `nexus_os.benchmark_vault.GuardianBenchmarkVault` with persistent candidate storage, source-regression deduplication, governed approve/reject review, approved-candidate filtering, snapshot construction, and frozen snapshot export.
- automatic verified-regression nomination through `RegressionLearningBridge` when a Benchmark Vault is configured.
- mandatory `evidence_ref` for vault-enabled automatic nomination.
- pre-write validation so a missing evidence reference cannot leave a partial regression record.
- versioned `FixedEvaluationCorpus` snapshots composed from the immutable packaged core plus approved Benchmark Vault candidates.
- SHA-256-compatible snapshots for `GuardianIntelligenceLab.run_fixed(...)` and `compare_fixed(...)`.

### Tests

- benchmark nomination deduplication;
- unreviewed-candidate exclusion;
- approved-candidate snapshot inclusion;
- rejected-candidate exclusion;
- severity-to-criticality behavior;
- automatic RegressionLearningBridge nomination;
- evidence-reference enforcement with no partial state;
- repository visibility of Benchmark Vault docs and animated SVG.

### Documentation and visuals

- `docs/GUARDIAN_BENCHMARK_VAULT.md`;
- animated `docs/assets/guardian-benchmark-vault.svg`;
- updated animated `docs/assets/current-state-graph.svg`;
- updated `docs/CURRENT_STATE.md`;
- updated `docs/VISUAL_GALLERY.md`;
- updated `docs/PROCESS_WORKFLOWS.md`;
- updated `docs/RELEASES_AND_PACKAGES.md`;
- `docs/LEARNINGS_V0.6.0.md`;
- README v0.6.0 architecture, learning, release, visual, and roadmap refresh.

### Release metadata

- runtime package: `0.6.0`;
- ChatGPT/plugin manifest: `0.6.0`;
- Codex compatibility manifest: `0.6.0`;
- expected release tag: `v0.6.0`;
- expected GHCR tags: `0.6.0`, `0.6`, and `latest`.

## Governance invariant

Automatic learning may nominate benchmark knowledge. It may not silently approve or rewrite permanent benchmark truth. Only reviewed/approved candidates can enter a new frozen snapshot, and the packaged core corpus remains immutable.
