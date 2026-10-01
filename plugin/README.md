# Nexus Starship Guardians ChatGPT/Codex Plugin v0.5.0

This directory contains the portable, skills-only plugin package aligned with the current **Nexus Starship Guardians v0.5.0** runtime. The runtime remains in `nexus_os/`; this plugin is a separate integration surface that provides Intelligence Fabric guidance, mission-planning guidance, optional REST operations, integration-readiness guidance, and host-tool policies without bundling secrets or infrastructure access.

## Included Skills

- `nexus-project-setup`: isolated per-app project configuration and safe onboarding.
- `nexus-run-operations`: scoped Guardian runs, evidence inspection, and explicit approval handling. Includes an optional Python-standard-library CLI.
- `nexus-app-integration`: server-side Lucio/Ember/Nexus Code adapter workflow and acceptance tests.
- `nexus-readiness-review`: evidence-based security, CI, deployment, and regression-readiness review.
- `host-workspace-operator`: host-tool read-first and authorized mutation policy.
- `sandbox-python-executor`: deterministic Python verification when the current host actually supplies Python.

Both the portable root `plugin.json` and optional Codex compatibility `.codex-plugin/plugin.json` are included.

## v0.5 Intelligence Fabric

The runtime now exposes project-scoped Intelligence Fabric planning through:

```text
POST /v1/projects/{project_id}/intelligence-plan
```

The response includes mission kind, confidence, uncertainty, capabilities, required tools, strategy, strategy rationale, required evidence, adversarial guardrail cases, and assumptions. Live runs also record a `strategy_intelligence` event before provider execution.

The plugin should treat this plan as inspectable intelligence evidence. It does **not** grant permissions, credentials, hosted-model access, or external connectivity.

## Mission intelligence and integration readiness

The existing v0.4 mission-planning/readiness contracts remain supported. Mission planning can classify intent, map required capabilities/tools, select a bounded Guardian team, and report missing or project-disabled tools. Integration-readiness contracts cover Lucio AI Platform, Ember, Nexus Code, Railway, and Supabase while explicitly keeping connection state separate from readiness.

## Compatibility contract

The product language is **Guardian / Guardians**. The REST v1 API intentionally retains the compatibility field names `agent` and `agents`; plugin instructions call those out explicitly so existing clients continue to work while user-facing terminology stays current.

Current runtime verification includes Python 3.11/3.12/3.13, Ruff, pytest, live Intelligence/Mission Runtime API behavior, live Uvicorn HTTP smoke testing, Docker build/health, PostgreSQL 16 queue integration, release-artifact builds, and plugin/runtime version alignment. This plugin does **not** automatically inherit filesystem, GitHub, browser, MCP, Railway, Supabase, or deployment permissions from the runtime. Those capabilities require the actual authorized host/tool connection.

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
5. verify Intelligence Fabric, mission-planning/readiness contracts, and permission boundaries;
6. verify the optional CLI against a local/mock authorized API;
7. distinguish deterministic/offline tests from real hosted-provider or external-service integration tests.

## Boundaries

The repository is public, but public plugin distribution is a separate release decision. This package is not an MCP server and does not claim public marketplace approval. If MCP or hosted integrations are added later, review authentication, domain ownership, HTTPS deployment, tool annotations, tenant isolation, approval controls, provider credentials, and real end-to-end tests separately.
