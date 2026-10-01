# Engineering Learnings — v0.7.0

## 1. “Self-learning” needs evidence boundaries

The most important design decision in v0.7.0 is that Guardians do not learn from their own unsupported claims. Adaptive updates require a verified outcome. This prevents confident but wrong completions from being reinforced as expertise.

## 2. One aggregate Guardian score hides dangerous weaknesses

A specialist can be excellent overall while still being weak in one mission-critical capability. Per-skill evidence makes weaknesses visible. Routing can then prefer a Guardian whose proven strength matches the exact requirement instead of relying on a generic reputation score.

## 3. Confidence and performance are different

A new skill with no failures is not automatically strong; it is uncertain. v0.7.0 therefore tracks observation confidence separately from adaptive score and prioritizes low-evidence capabilities for replay or evaluation.

## 4. Critical regressions need disproportionate weight

A specialist that usually scores well but repeatedly causes critical regressions should not remain highly ranked. Critical-regression penalties deliberately outweigh small semantic-score improvements.

## 5. Learning should influence routing, not authorization

Performance evidence can help Nexus decide **who should try the work**. It cannot decide **what the Guardian is allowed to access**. Tool permissions, credentials, external adapters, and project policy remain separate control planes.

## 6. Replay before benchmark approval improves review quality

A verified production failure can still be noisy or environment-specific. Benchmark Replay adds a reproducibility layer before governed review. A reviewer can see whether the failure reproduces under the baseline, candidate strategy, or alternate strategies.

## 7. Benchmark breadth matters as much as benchmark size

Adding hundreds of cases from the same category can create misleading confidence. Coverage Intelligence therefore measures domain breadth and exposes under-tested areas such as cloud, API, UI, security, database, deployment, or debugging.

## 8. Automatic improvement should target the weakest link

The strongest compounding loop is not “make every Guardian more verbose or complex.” It is:

```text
verified outcome
  ↓
identify weak / uncertain skill
  ↓
replay or evaluate that skill
  ↓
record evidence
  ↓
adapt routing + priorities
```

This creates measurable improvement without uncontrolled self-modification.

## 9. Live model-weight mutation remains the wrong default

Nexus can export training candidates and collect high-quality evidence, but production weight changes remain a separate curated offline process. That separation preserves rollback, reproducibility, and benchmark integrity.

## 10. Specialist intelligence should remain inspectable

The adaptive score is intentionally composed from visible inputs: quality, reliability, benchmark performance, trend, and regression pressure. Operators can understand why a specialist is improving, declining, or being prioritized for more training.
