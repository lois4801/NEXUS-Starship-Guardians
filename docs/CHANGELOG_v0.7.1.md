# Changelog — v0.7.1

## Production completion patch

v0.7.1 completes the live wiring for the Adaptive Guardian Intelligence subsystem introduced in v0.7.0.

## Live specialist routing

- Registers all ten elite adaptive specialist Guardians in the default live Guardian Registry.
- Supplies the persistent `AdaptiveGuardianIntelligence` instance to `MissionRuntime` and `AdaptiveGuardianRouter`.
- Preserves the canonical 30-Guardian Artificial Architecture team and all existing compatibility surfaces.
- Adds specialist routing aliases so existing mission-classifier capabilities can select the new specialist profiles without requiring a breaking classifier rewrite.

## Automatic verified specialist learning

- Supplies `AdaptiveGuardianIntelligence` to `ServerLearningRecorder`.
- Automatically records per-skill specialist evidence from terminal runs when objective verification exists.
- Successful runs require a recorded `test`, `api`, `browser`, or `security` tool result before they may reinforce specialist expertise.
- Concrete `provider_error`, `policy_denied`, `tool_error`, or `max_steps_reached` events can teach failure evidence automatically.
- Self-reported successful final answers without objective verification do not update adaptive specialist state.
- Mission-intelligence capabilities become the skill evidence targets; declared specialist capabilities are the fallback when mission capabilities are unavailable.

## Persistent adaptive state

- Adds `Settings.adaptive_intelligence_path`.
- Adds `NEXUS_ADAPTIVE_INTELLIGENCE_PATH`.
- Defaults adaptive state to `./data/adaptive_guardian_intelligence.json`.
- Adds the new variable to `.env.example` and configuration tests.

## API correctness

- Replaces stale hard-coded FastAPI and `/health` version `0.5.0` with package `__version__`.
- Adds `/health` evidence that Adaptive Guardian Intelligence is live.
- Adds live specialist count to `/health`.

## Tests

- Verifies all ten adaptive specialists exist in the default live registry.
- Verifies successful specialist learning occurs automatically only after objective verification.
- Verifies an unverified successful final answer cannot reinforce specialist expertise.
- Verifies concrete specialist failures automatically update failure-side skill evidence.
- Verifies adaptive state path configuration.
- Isolates adaptive state in API test fixtures.
- Replaces stale version assertions with package-version assertions.

## GitHub docs and animated visuals

- Updates `README.md` to v0.7.1 and documents the live automatic-learning path.
- Updates `docs/CURRENT_STATE.md`.
- Updates the animated `docs/assets/current-state-graph.svg` to v0.7.1.
- Updates the animated `docs/assets/adaptive-guardian-intelligence.svg` to show automatic verified learning.
- Updates `docs/ADAPTIVE_GUARDIAN_INTELLIGENCE.md` with live runtime and verification semantics.

## Release metadata

- Python runtime: `0.7.1`.
- ChatGPT plugin: `0.7.1`.
- Codex plugin: `0.7.1`.
- Expected stable release: `v0.7.1`.
- Expected GHCR tags: `0.7.1`, `0.7`, `latest`.

## Governance invariant

Automatic specialist learning changes evidence, confidence, training priorities, and bounded routing preference. It does not grant credentials or permissions, silently approve benchmark truth, overwrite the fixed core corpus, mutate hosted model weights, or bypass promotion/release gates.
