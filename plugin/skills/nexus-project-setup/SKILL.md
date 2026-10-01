---
name: nexus-project-setup
description: Use to plan or register an isolated project in an existing Nexus Starship Guardians instance, including Guardian allowlists, tool permissions, provider selection, and secret-safe onboarding.
---

# Nexus project setup

Current source of truth: `README.md`, `nexus_os/models.py`, `nexus_os/api.py`, and current integration/production-verification docs in the Nexus Starship Guardians repository. When inspected source differs from this Skill, inspected source wins.

## Trigger and evidence

Use this Skill when the user wants to onboard Lucio AI Platform, Ember, Nexus Code, or another app to Nexus Starship Guardians. Start read-only. Determine whether the user wants a plan or actual project registration. Registration requires an authorized reachable Nexus instance and an admin token supplied to the host as a secret, never pasted into chat or source code.

1. Define a distinct lower-case project ID (`^[a-z][a-z0-9-]{2,47}$`) for each app. Record display name, provider, enabled Guardian IDs, tool allowlist, and bounded `max_steps`.
2. REST v1 currently retains the compatibility JSON field `agents` even though product terminology is **Guardians**. Supported compatibility IDs are `general`, `builder`, and `research`; providers are `demo` and `openai_compatible`; tools are `calculator`, `utc_now`, and approval-gated `project_note`; `max_steps` is 1-12.
3. Begin conservatively with the demo provider and read-only/deterministic tools unless a real configured provider and additional permissions are verified. Capability detection never grants tool access.
4. `project_note` is a write requiring explicit approval. Do not enable or approve it without a functioning owning-app approval path and a second authorization check.
5. For actual registration, call `POST /v1/projects` only from an authorized secure host using the admin bearer token and reviewed payload. The generated project API key is returned once; transfer it directly into the destination application's server-side secret store without echoing it in conversation, logs, screenshots, or artifacts.
6. Verify each project through `GET /v1/projects/{project_id}` using its own token. Prove wrong-project tokens fail with 403 before treating isolation as verified.
7. Output a concise matrix: project ID, Guardians, tools, provider, max steps, secret-storage status, and isolation-verification status. Mark unexecuted steps as pending.

## Boundaries

The plugin grants no host tools, network access, provider credentials, GitHub permissions, browser access, MCP connection, or deployment rights on its own. Do not attempt admin operations with a project key, expose secrets client-side, enable `NEXUS_DEV_MODE=true` on a public service, or reuse one project key across apps. Stop on a 409 project conflict and inspect before retrying.
