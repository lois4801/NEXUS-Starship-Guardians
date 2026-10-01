# Learning — Mission intent must outrank supporting work

## What CI found

The first Mission Classifier implementation treated the presence of the word `test` as a stronger signal than the word `build`. A mission such as:

> Build a production FastAPI API with PostgreSQL, security tests, Docker and telemetry

was therefore classified as a **TEST** mission even though the primary delivery intent was clearly to build a feature.

## Root cause

Mission-kind rules were evaluated in this order:

1. bug fix;
2. refactor;
3. test;
4. deploy;
5. research;
6. feature.

Supporting work such as tests could therefore hijack the mission kind before the delivery verb was evaluated.

## Fix

The classifier now gives primary delivery intent precedence:

1. bug/fix intent;
2. refactor intent;
3. feature/build/create/implement/add intent;
4. deploy intent;
5. research intent;
6. explicit test-only intent.

Testing still appears in `MissionRequirements.capabilities`; it simply does not replace a feature mission's primary kind.

## Regression coverage

The suite now explicitly verifies both sides of the boundary:

- `Build a new API and add tests for every endpoint` → **FEATURE** plus the `testing` capability;
- `Test and verify the existing authentication workflow` → **TEST**.

## Reusable lesson

**Classifiers should separate primary intent from supporting capabilities.** Words describing validation, documentation, deployment, or other secondary work should enrich routing requirements without accidentally changing the mission's main delivery objective.
