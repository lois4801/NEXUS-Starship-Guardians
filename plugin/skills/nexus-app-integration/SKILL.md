---
name: nexus-app-integration
description: Use to plan, build or review a server-side NEXUS Agentic OS adapter for Lucio AI Platform, Ember, or another app while preserving that app's repository and tenant-specific security.
---

# NEXUS app integration

Canonical source: `docs/ARCHITECTURE.md`, `docs/INTEGRATION.md`, `nexus_os/client.py`, and `sdk/typescript/src/client.ts` in the NEXUS repository.

## Workflow

1. Read the target application's actual source, its instructions, current auth mechanism and existing API structure before offering a patch. If code access is unavailable, provide a scoped implementation plan rather than claiming integration.
2. Preserve current app routes, auth, database, feature flags, deployment and Git history. Add one server-only adapter; authenticate the app's end user and authorize access to that app's project before calling NEXUS.
3. Use the app-specific NEXUS project key in the existing server secret manager. Never send it to browser or mobile clients, source files, logs or screenshots. Do not reuse it across apps.
4. Use the existing Python SDK or server-side TypeScript SDK. Validate goal input, agent allowlist and project binding; never let an untrusted client select an upstream arbitrary project ID. Provide a bounded request timeout and handle failure, max-steps and pending approval states distinctly.
5. Display approval requests to the correct owning user. No `project_note` approval call happens without explicit action and a second server-side authorization check.
6. Before declaring completion, execute available tests: one calculator event per app, reciprocal 403 isolation, non-enabled agents denied, unallowlisted tools denied, approval pause/resume, no client-side secret leakage, real event traces and honest failure handling. Identify which were actually run versus specified.
7. Produce a focused change list, test evidence, rollback plan and clear stop conditions. For public/multi-worker deployments, flag v0.1 SQLite/single-worker limitations and the need for TLS, quotas, rate limits, production secret management, PostgreSQL and a durable queue.

Do not claim v0.1 has GitHub editing, sandboxed coding, MCP server, browsing, cost routing, durable workers or deployment capabilities. Any such integration needs its own reviewed adapter and tests.
