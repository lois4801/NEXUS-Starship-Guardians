# Guardian Benchmark Vault

The Guardian Benchmark Vault is the governed benchmark-growth layer for Nexus Starship Guardians. It connects verified production or CI failures to the Guardian Intelligence Lab without allowing the runtime to silently rewrite its own benchmark truth.

![Guardian Benchmark Vault](assets/guardian-benchmark-vault.svg)

## Why it exists

The Intelligence Lab already compares a baseline and candidate against a fingerprinted fixed corpus. The Benchmark Vault adds a controlled path for that corpus to improve over time:

```text
verified failure
      ↓
RegressionLearningBridge
      ↓
RegressionCorpus
      ↓
Benchmark Vault candidate
      ↓
review / replay / evidence check
   ↙               ↘
reject             approve
                      ↓
              versioned snapshot
                      ↓
              Intelligence Lab
                      ↓
               Promotion Gate
```

A verified failure may become a benchmark **candidate automatically** when a `GuardianBenchmarkVault` is attached to the regression bridge and an evidence reference is supplied. Automatic nomination is not automatic approval.

## Core modules

- `nexus_os.benchmark_vault.BenchmarkCandidate`
- `nexus_os.benchmark_vault.GuardianBenchmarkVault`
- `nexus_os.regression_bridge.RegressionLearningBridge`
- `nexus_os.regression_corpus.RegressionCorpus`
- `nexus_os.fixed_corpus.FixedEvaluationCorpus`
- `nexus_os.evaluation_lab.GuardianIntelligenceLab`
- `nexus_os.promotion_gate.decide_promotion`

## Candidate lifecycle

Each candidate records:

- a stable benchmark case ID;
- task and expected behavior;
- critical/non-critical status derived from verified severity;
- original regression case ID;
- failure category and severity;
- provenance and tags;
- verification evidence reference;
- review status;
- reviewer and review note;
- nomination and review timestamps.

Supported states are:

- `candidate` — verified failure nominated, not yet trusted as fixed benchmark truth;
- `approved` — reviewed and eligible for the next frozen benchmark snapshot;
- `rejected` — retained as review history but excluded from benchmark snapshots.

## Automatic nomination

```python
from pathlib import Path

from nexus_os.benchmark_vault import GuardianBenchmarkVault
from nexus_os.regression_bridge import RegressionLearningBridge
from nexus_os.regression_corpus import RegressionCorpus

corpus = RegressionCorpus(Path("data/regressions.jsonl"))
vault = GuardianBenchmarkVault(Path("data/benchmark-vault"))
bridge = RegressionLearningBridge(corpus, benchmark_vault=vault)

capture = bridge.capture(
    title="Deployment evidence regression",
    task="Verify a deployment before claiming completion",
    expected="Authenticated deployment evidence must exist",
    error="expected deployment evidence but evidence was missing",
    verified=True,
    provenance="ci:deployment-verification",
    evidence_ref="sha256:<evidence-bundle-digest>",
)
```

When the vault is enabled, a verified capture requires `evidence_ref`. This prevents an automatically nominated benchmark from losing the evidence that justified its existence.

## Review and approval

```python
candidate = capture.benchmark_candidate

vault.review(
    candidate.case_id,
    approved=True,
    reviewer="guardian-reviewer",
    note="Failure replayed and evidence bundle verified.",
)
```

The reviewer identity is an audit label, not an authorization system. Deployments can wrap this API in their own approval, identity, or change-management policy.

## Frozen snapshots

The packaged core benchmark remains immutable. The vault creates a new versioned snapshot by combining that base with approved candidates:

```python
from nexus_os.fixed_corpus import FixedEvaluationCorpus

base = FixedEvaluationCorpus.load_core()
snapshot, path = vault.freeze_snapshot(
    base=base,
    version="1.1.0",
    description="Core benchmark plus reviewed production regressions.",
)

print(snapshot.sha256)
print(path)
```

The snapshot is a normal `FixedEvaluationCorpus`, so it can be fingerprinted and supplied to `GuardianIntelligenceLab.run_fixed(...)` and `compare_fixed(...)`.

## Governance rules

1. Unverified suspicions do not enter the Regression Corpus.
2. Verified failures may be nominated automatically only with an evidence reference.
3. Nominations start in `candidate` state.
4. Candidates do not enter snapshots until explicitly reviewed and approved.
5. Rejected candidates remain excluded from frozen benchmark truth.
6. The packaged core corpus is never silently mutated.
7. Frozen snapshots receive their own semantic version and SHA-256 fingerprint.
8. Baseline and candidate evaluation must still use the exact same snapshot.

## Intended growth path

The first packaged corpus contains eight seed cases. The Benchmark Vault is the mechanism for safely growing future corpora from real evidence across coding, debugging, testing, security, database migrations, UI behavior, API contracts, deployments, integrations, routing, tool policy, and production reliability.

The target is not “more tests at any cost.” The target is a high-signal benchmark history where every permanent case has provenance, evidence, review history, and a reproducible failure mode.
