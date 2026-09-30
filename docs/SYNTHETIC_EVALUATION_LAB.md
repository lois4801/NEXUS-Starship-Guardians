# Nexus Starship Guardians — Synthetic Evaluation Lab

The Synthetic Evaluation Lab makes Guardian improvement measurable. It compares a candidate Guardian strategy/model/configuration against a fixed baseline on provenance-tracked synthetic and regression cases.

## Core rule

A new candidate is not promoted because it is newer or because a judge model prefers it once. Promotion requires evidence:

1. no critical regression;
2. candidate pass rate meets the configured minimum;
3. candidate pass rate does not regress versus baseline;
4. candidate average score meets or exceeds the baseline plus the configured score delta.

## Evaluation flow

```text
Curated regression cases ----┐
                             ├-> Evaluation suite -> baseline run
Synthetic task generator ----┘                    -> candidate run
                                                   -> judge(s)
                                                   -> failure taxonomy
                                                   -> evidence store
                                                   -> promotion gate
```

## Provenance

Each `EvalCase` records a stable case ID, task, requirements, tags, source, criticality, and provenance. Evaluation reports are append-only JSONL records so synthetic samples can be traced back to how they were created.

Synthetic tasks should never silently replace regression cases from real failures. Real production/test failures should become durable regression cases after review.

## Judges

`requirements_judge` is a deterministic offline smoke-test judge. Production evaluations can add semantic model judges, but deterministic acceptance checks should remain in the suite so one model judge cannot redefine success by itself.

Recommended judging stack:

1. deterministic unit/integration/security assertions;
2. repository/browser/API verification evidence;
3. one or more semantic Guardian/model judges where appropriate;
4. human approval for consequential releases or model promotion.

## Failure taxonomy

The initial categories are:

- correctness
- completeness
- safety
- tool-use
- regression
- reliability
- unknown

Failure taxonomy counts are stored with every evaluation report and can be used to prioritize future Guardian lessons, regression tests, or training-data curation.

## Promotion and offline fine-tuning

Nexus Starship Guardians does not update production model weights live. High-quality verified episodes may be exported for offline SFT/LoRA curation. Any resulting adapter/model is treated as a candidate and must pass this Evaluation Lab against a fixed baseline before promotion.

## Server-wide learning

The REST/server path now records terminal run outcomes into the same Guardian learning store used by portable swarms. Server scores are explicitly labeled `execution-reliability`; they do not claim semantic answer quality. Semantic quality comes from this evaluation system.

Environment variables:

- `NEXUS_LEARNING_PATH` — append-only Guardian episode/lesson memory
- `NEXUS_EVALUATION_PATH` — append-only evaluation reports
