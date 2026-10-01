# Changelog — v0.8.0

## Guardian Cognitive Evolution

v0.8.0 adds a persistent meta-learning layer above Adaptive Guardian Intelligence so the ten specialist Guardians can compound verified knowledge across missions without unrestricted self-modification.

## New cognitive intelligence

- persistent `CognitiveEvolutionEngine`;
- verified `CognitiveLesson` generation;
- cross-Guardian lesson retrieval by skill overlap;
- confidence calibration against observed outcomes;
- persistent recurring-failure clustering;
- counterfactual replay strategy generation;
- personalized self-training curricula;
- small bounded cognitive routing signal layered above direct verified skill evidence.

## Automatic live learning

Every objectively verified specialist terminal run can now update:

1. general learning memory;
2. direct per-skill adaptive evidence;
3. cognitive lessons and confidence calibration.

Verified failures additionally generate a counterfactual replay cycle automatically. Successful final answers without objective verification still cannot reinforce specialist expertise.

## Knowledge-transfer invariant

Peer lessons transfer information, not status. A receiving Guardian does not inherit another Guardian's success rate, adaptive score, benchmark rate, confidence, or permissions. It must prove the capability with its own verified outcomes.

## Live inspection

Adds:

`GET /v1/projects/{project_id}/guardians/{guardian_id}/cognitive-summary`

The endpoint returns adaptive skill evidence together with verified cognitive episodes, authored lessons, confidence reliability, counterfactual-cycle count, and the current self-curriculum.

## Persistence

Adds:

`NEXUS_COGNITIVE_EVOLUTION_PATH=./data/guardian_cognitive_evolution.json`

Cognitive state is deliberately separated from episodic learning memory and direct adaptive competence state.

## Routing

Guardian routing can now use:

- Registry utility;
- bounded direct adaptive evidence;
- an even smaller bounded cognitive/calibration signal.

Permissions remain independent from performance and learning.

## Tests

Adds coverage for:

- verified-only cognitive learning;
- cross-Guardian lesson transfer without score cloning;
- failure clustering;
- counterfactual strategy generation;
- self-curriculum generation;
- confidence-calibration penalties;
- persistent cognitive state;
- automatic live cognitive learning;
- project-scoped cognitive-summary inspection;
- cognitive state environment configuration.

## Release metadata

- Python runtime: `0.8.0`.
- ChatGPT plugin: `0.8.0`.
- Codex plugin: `0.8.0`.
- Expected stable release: `v0.8.0`.
- Expected GHCR tags: `0.8.0`, `0.8`, `latest`.

## Governance invariant

Cognitive Evolution may adapt verified lessons, confidence calibration, failure intelligence, replay strategies, self-curricula, and bounded routing preference. It may not grant credentials or permissions, copy peer competence scores, silently approve benchmark truth, overwrite the fixed corpus, mutate hosted model weights live, or bypass promotion and release gates.
