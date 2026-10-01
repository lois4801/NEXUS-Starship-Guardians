# Nexus Starship Guardians ChatGPT/Codex Plugin v0.3.0

This directory contains the portable, skills-only plugin package aligned with the current **Nexus Starship Guardians v0.3-dev** runtime. The runtime remains in `nexus_os/`; this plugin is a separate integration surface that provides guidance, optional REST operations, and host-tool policies without bundling secrets or infrastructure access.

## Included Skills

- `nexus-project-setup`: isolated per-app project configuration and safe onboarding.
- `nexus-run-operations`: scoped Guardian runs, evidence inspection, and explicit approval handling. Includes an optional Python-standard-library CLI.
- `nexus-app-integration`: server-side Lucio/Ember/Nexus Code adapter workflow and acceptance tests.
- `nexus-readiness-review`: evidence-based security, CI, deployment, and regression-readiness review.
- `host-workspace-operator`: host-tool read-first and authorized mutation policy.
- `sandbox-python-executor`: deterministic Python verification when the current host actually supplies Python.

Both the portable root `plugin.json` and optional Codex compatibility `.codex-plugin/plugin.json` are included.

## Compatibility contract

The product language is **Guardian / Guardians**. The REST v1 API intentionally retains the compatibility field names `agent` and `agents`; plugin instructions call those out explicitly so existing clients continue to work while user-facing terminology stays current.

Current runtime verification includes Python 3.11/3.12/3.13, Ruff, pytest, live Uvicorn HTTP smoke testing, Docker build/health, and PostgreSQL 16 queue integration. This plugin does **not** automatically inherit filesystem, GitHub, browser, MCP, Railway, Supabase, or deployment permissions from the runtime. Those capabilities require the actual authorized host/tool connection.

## Build ZIP

From this `plugin/` directory:

```sh
python -m zipfile -c ../../nexus-starship-guardians-plugin.zip plugin.json .codex-plugin skills assets
```

Package only the plugin contents so `plugin.json` is at archive root. Do not package the backend, `.env`, tokens, project keys, or private credentials.

## Verification expectations

Before publishing or installing a new snapshot:

1. validate both manifests and matching identity/version;
2. verify all six Skill directories exist;
3. run the repository CI matrix;
4. run plugin contract tests against the current REST v1 models;
5. verify the optional CLI against a local/mock authorized API;
6. distinguish deterministic/offline tests from real hosted-provider or external-service integration tests.

## Boundaries

The repository is public, but public plugin distribution is a separate release decision. This package is not an MCP server and does not claim public marketplace approval. If MCP or hosted integrations are added later, review authentication, domain ownership, HTTPS deployment, tool annotations, tenant isolation, approval controls, provider credentials, and real end-to-end tests separately.
