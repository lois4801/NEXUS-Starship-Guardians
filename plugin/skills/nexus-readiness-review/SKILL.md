---
name: nexus-readiness-review
description: Use to review the security, quality gates, integration evidence, and deployment readiness of a Nexus Starship Guardians integration using actual repository and test evidence rather than simulated results.
---

# Nexus Starship Guardians readiness review

When asked to evaluate a Nexus instance or planned launch:

1. Inspect the exact source revision, intended app/project, configuration, and deployment architecture. Never ask users to reveal admin or project tokens.
2. Confirm the current implemented scope rather than repeating historical v0.1 assumptions. Current main includes FastAPI REST, project-scoped keys, Guardian/tool allowlists, portable provider adapters, learning/evaluation, regression protection, worktrees, bounded repair, persistent Guardian metrics, PostgreSQL distributed-queue foundations, Docker/live-HTTP verification, Mission Intelligence, and observability foundations.
3. Treat compatibility names honestly: REST v1 still uses `agent` / `agents` fields and the Python namespace remains `nexus_os`; those are tested compatibility surfaces, not current product branding.
4. Inspect and, when safe execution exists, run the applicable quality gates: Python 3.11/3.12/3.13, Ruff, pytest, canonical/legacy CLI smoke tests, REST import/title, live Uvicorn `/health`, Docker build/health, PostgreSQL integration, and plugin contract tests.
5. Check secrets remain server-side, `NEXUS_DEV_MODE` is disabled outside local development, remote transport uses TLS, write tools require explicit approval, project isolation is enforced, and external-provider/infrastructure integrations have their own credentialed tests before being called verified.
6. Separate `source inspected`, `tests executed`, `runtime verified`, `external integration verified`, and `production ready`. For every unverified condition, name the missing evidence instead of waiving it.
7. Confirm verified failures can feed regression protection only after an evidence gate; learning must not treat model confidence as proof.
8. Deliver findings by severity with precise file/endpoint evidence, remediation steps, rollback considerations, and a retest sequence. Never auto-deploy or auto-promote a consequential change solely because a model says it passed.

This Skill is read-only by default. Implement changes only when the user explicitly requests them and the current host has authorized workspace access.
