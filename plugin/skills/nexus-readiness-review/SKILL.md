---
name: nexus-readiness-review
description: Use to review the security, quality gates and deployment readiness of a NEXUS Agentic OS integration using actual repository and test evidence rather than simulated results.
---

# NEXUS readiness review

When asked to evaluate a NEXUS instance or planned launch:

1. Inspect the exact source revision, intended app/project, config and deployment architecture. Never ask users to reveal admin or project tokens.
2. Confirm actual v0.1 scope: FastAPI REST, per-project keys stored as hashes, per-project allowed agents/tools, demo or OpenAI-compatible model provider, bounded synchronous loop, SQLite traces and approval-required `project_note`. List anything not actually implemented as roadmap only.
3. Inspect relevant tests for token validation, cross-tenant access, denied agents/tools, calculator outcome, fail-closed model output, approval and denial, and limits. Run the repository's `pytest` and `ruff` checks only on inspected, trusted source and when safe host execution exists; do not equate a test recipe with a test run.
4. Check that production secrets remain server-side, `NEXUS_DEV_MODE` is disabled outside local dev, remote transport uses TLS, sensitive write tools require approval, and deployment uses a single worker while SQLite and in-process locking remain. Flag missing security controls and public-readiness blockers as concrete findings.
5. Separate `source inspected`, `tests executed`, `integration verified` and `production ready` evidence. For unverified conditions state the missing test or prerequisite; never waive failures automatically.
6. Deliver findings by severity with precise file/endpoint evidence and a scoped remediation and retest sequence. No automatic irreversible deployment.

This review Skill is read-only by default. Implement or patch only when the user explicitly asks for the change and the host grants authorized workspace access.
