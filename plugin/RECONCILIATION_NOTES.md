# Nexus Starship Guardians Plugin Reconciliation Notes

## Why this reconciliation was required

The original plugin draft was created against the early v0.1 runtime and still used the retired product name **NEXUS Agentic OS**. Since then, the runtime evolved into **Nexus Starship Guardians v0.3-dev** with production-verification gates, Guardian Intelligence, adaptive routing, Mission Intelligence, persistent metrics, PostgreSQL queue integration, and broader compatibility testing.

## Changes made

- renamed the plugin identity to `nexus-starship-guardians` v0.3.0;
- updated repository URLs to `lois4801/NEXUS-Starship-Guardians`;
- replaced product-facing Agent/Agents language with Guardian/Guardians;
- retained REST v1 `agent` / `agents` only as documented compatibility wire fields;
- updated the optional CLI with canonical `--guardian` plus legacy `--agent` support;
- translated redacted CLI output from the legacy API field `agent` to product-facing `guardian`;
- replaced outdated v0.1 SQLite/single-worker readiness language with the current verified architecture and explicit remaining boundaries;
- updated integration guidance for Mission Intelligence, adaptive routing, PostgreSQL, Docker/live HTTP verification, regression protection, and external-integration evidence;
- updated plugin branding accessibility labels;
- added automated plugin manifest/Skill/CLI compatibility regression tests.

## Reusable engineering lessons

1. **Product renames and wire-contract migrations are separate operations.** User-facing language can move immediately while versioned API fields remain compatible until a deliberate breaking release.
2. **Compatibility should be executable.** Keeping legacy `--agent` support is safer when CI proves it still maps to the same REST v1 payload as canonical `--guardian`.
3. **Plugin documentation must track runtime reality.** A plugin that accurately described v0.1 became misleading once the runtime gained distributed queue, production-verification, learning, and routing capabilities.
4. **Capabilities never imply permissions.** The plugin may describe Nexus routing or integration features, but actual GitHub, browser, MCP, deployment, database, or hosted-model actions still require the corresponding authorized host connection.
5. **Do not silently inflate verification claims.** Offline plugin tests, repository CI, and real external-service integration are distinct evidence classes and must remain labeled separately.

## Merge gate

Merge only after the current repository CI matrix validates the plugin changes together with the latest `main` runtime. The plugin source being merged does not automatically update any previously installed ChatGPT/Codex plugin snapshot.
