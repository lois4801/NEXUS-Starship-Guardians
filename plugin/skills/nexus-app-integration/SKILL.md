---
name: nexus-app-integration
description: Use to plan, build, or review a server-side Nexus Starship Guardians adapter for Lucio AI Platform, Ember, Nexus Code, or another app while preserving that app's repository, auth, and tenant security.
---

# Nexus app integration

Canonical source is the current Nexus Starship Guardians repository: architecture/integration docs, `nexus_os/api.py`, `nexus_os/client.py` when present, current SDKs, Mission Intelligence, production-verification docs, and the tested REST v1 contract.

## Workflow

1. Read the target application's real source, instructions, auth mechanism, API structure, deployment model, and data boundaries before proposing changes. If source access is unavailable, provide a scoped plan rather than claiming integration.
2. Preserve current routes, auth, database, feature flags, deployment, and Git history. Add a server-only adapter; authenticate the app's user and authorize that user's access to the correct Nexus project before calling Nexus.
3. Store the app-specific `NEXUS_PROJECT_KEY` only in the existing server-side secret manager. Never send it to browser/mobile clients, source files, logs, screenshots, or generated artifacts. Never reuse one key across Lucio, Ember, Nexus Code, or another app.
4. Validate goal input, project binding, Guardian selection, and tool permissions. REST v1 keeps compatibility fields `agent` / `agents`, but all product-facing UI and documentation should say Guardian / Guardians.
5. Use Mission Classifier / Capability Map output as routing evidence when integrated, but never let classification grant tools. Guardian `allowed_tools` and project boundaries remain authoritative.
6. Treat `pending_approval` as a real stop state. No approval-gated write such as `project_note` proceeds without explicit user action and a second server-side authorization check.
7. Before declaring completion, execute the tests that are actually available: scoped run smoke test, reciprocal 403 isolation, disabled Guardian rejection, unallowlisted tool rejection, approval pause/resume, no client-side secret leakage, provider-contract handling, evidence capture, and honest failure states. Distinguish tests executed from tests merely specified.
8. For production, include rollback instructions and verify the applicable current gates: Python compatibility, Ruff, pytest, live Uvicorn, Docker health, PostgreSQL integration, persistent Guardian metrics, regression capture, and any external-service-specific gated tests.

## Current boundaries

Nexus Starship Guardians now includes durable/distributed execution foundations, adaptive routing, learning/evaluation, worktrees, browser/API verification primitives, and production verification. That does **not** mean this plugin itself has GitHub, browser, shell, MCP, Railway, Supabase, or deployment permissions. Those require explicit host connections and their own tested adapters.
