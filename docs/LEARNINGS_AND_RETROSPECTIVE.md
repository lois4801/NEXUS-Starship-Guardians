# Nexus Starship Guardians — Learnings and Retrospective

This file is part of the default repository update discipline. Meaningful changes should add a concise entry when they reveal reusable engineering lessons, regressions, CI failures, or architecture decisions.

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
