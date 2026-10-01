# Nexus Starship Guardians v0.6.0 — Benchmark Vault Learnings

## What changed

v0.6.0 adds a governed bridge between verified regressions and future fixed evaluation corpora. `RegressionLearningBridge` can automatically nominate a verified regression into `GuardianBenchmarkVault` when the deployment supplies an evidence reference. The nomination is not benchmark truth until an explicit review approves it. Approved candidates can be combined with the immutable core corpus and frozen as a new versioned `FixedEvaluationCorpus` snapshot.

## Reusable engineering lessons

1. **Automatic learning should propose truth, not silently define it.** A verified failure is strong enough to create a candidate, but permanent benchmark truth deserves a separate review decision.
2. **Evidence lineage must survive learning.** A benchmark candidate without the evidence that justified it is difficult to audit. Vault-enabled automatic nomination therefore requires `evidence_ref`.
3. **Regression memory and benchmark truth are different layers.** The Regression Corpus can be append-only operational memory, while the fixed evaluation corpus should be deliberately versioned and fingerprinted.
4. **The immutable base matters.** The packaged core corpus remains unchanged. New reviewed cases produce a new snapshot rather than editing the baseline in place.
5. **Rejected knowledge is still useful history.** Rejected candidates remain review history so repeated proposals can be understood without contaminating evaluation truth.
6. **Benchmark version and runtime version are separate identities.** Nexus runtime `v0.6.0` can generate multiple future benchmark snapshot versions without pretending that model-evaluation data and software releases are the same artifact.
7. **Deduplication prevents incident volume from becoming benchmark bias.** Repeated captures of the same underlying regression should not create repeated benchmark weight.
8. **Criticality should be evidence-derived and inspectable.** The initial vault maps verified severity 5 to critical benchmark cases; lower severity cases remain non-critical unless a later reviewed policy changes that mapping.
9. **Visual architecture is part of the contract.** The Current State Graph and dedicated animated Benchmark Vault visual were updated in the same change because the learning loop materially changed.
10. **Promotion still depends on identical evaluation material.** Benchmark growth does not weaken the v0.5.1 invariant: baseline and candidate must use the exact same corpus ID, version, and SHA-256 fingerprint.

## Safety boundary

The Benchmark Vault is intentionally not a self-training weight updater and not an authorization layer. It does not grant credentials, tools, deployment permissions, or model access. It stores reviewed evaluation knowledge. External actions remain governed by the existing project/tool/Guardian authorization model.

## Next targets

- add project-scoped benchmark-vault persistence adapters for shared deployments;
- add an authenticated review API/UI above the local vault primitives;
- add replay evidence that proves a candidate reliably reproduces before review approval;
- add benchmark coverage analytics by subsystem, failure category, severity, and project;
- add snapshot-diff reports showing exactly which cases changed between benchmark versions;
- add CI hooks that can run approved frozen snapshots against candidate routing/model strategies;
- add causal failure links so one incident can be connected to underlying dependency or architecture causes without duplicating benchmark cases;
- later add curated offline training/export pipelines that remain separate from production runtime mutation.
