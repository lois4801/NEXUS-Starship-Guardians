---
name: nexus-project-setup
description: Use to plan or register an isolated project in a user's existing NEXUS Agentic OS instance, including agent allowlists, tool permissions, provider selection and secret-safe onboarding.
---

# NEXUS project setup

Source behavior: NEXUS v0.1 `README.md`, `nexus_os/models.py`, `nexus_os/api.py` and `docs/INTEGRATION.md` in the repository declared by this Plugin. Treat newer inspected source as authoritative when it differs.

## Trigger and evidence

Use this Skill when the user wants to onboard Lucio, Ember or another app to NEXUS. Start read-only: inspect their project context and repository instructions when accessible. Determine whether they want a **plan** or actual project registration. Registration requires an authorized, reachable NEXUS instance and an admin token provided to the host as a secret, never pasted into chat or source code.

1. Define a distinct lower-case project ID (`^[a-z][a-z0-9-]{2,47}$`) for each app. Record display name, `provider`, enabled agent IDs and tool allowlist. v0.1 agents are `general`, `builder`, `research`; providers are `demo`, `openai_compatible`; tools are `calculator`, `utc_now`, `project_note`. `max_steps` must be 1-12.
2. Begin with `demo`, `calculator` and `utc_now` unless a real configured model and additional permissions have been verified. The demo model only performs calculator and UTC smoke tasks. Do not claim live coding or web research is enabled.
3. `project_note` is a write requiring explicit approval. Do not enable it without a functioning owning-app approval path. Never share an API key across Lucio, Ember or another app.
4. If and only if actual registration was requested and a secure HTTP-capable host is available, call `POST /v1/projects` with a bearer admin token and the reviewed payload. This endpoint returns the generated API key **once**. Transfer it into the destination application's server-side secret store without echoing the value in conversation, logs, screenshots or artifacts. If no secure destination exists, provide the registration instructions without generating a key.
5. Verify each project through the scoped `GET /v1/projects/{project_id}` endpoint using its own project token. Run a calculator smoke task through the run-operation workflow if the user requested it. Prove wrong-project tokens fail with 403 before treating isolation as verified.
6. Output a small per-app matrix: ID, agents, tools, provider, max steps, whether secret storage and isolation verification actually happened. Label unexecuted steps as pending.

## Boundaries

The plugin grants no host tools or network access. If the current host has no authorized connection, return a runnable, secret-free plan. Do not attempt admin operations with a per-project key, expose secrets client-side, enable `NEXUS_DEV_MODE=true` on a public service, or change unrelated application repositories. Creation is not idempotent: stop on a 409 conflict and inspect before trying again.
