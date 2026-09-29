# REV1 — NEXUS Agentic OS · Architecture & Roadmap

**Status:** v0.1 development starter | **Updated:** September 29, 2026 | **Canonical owner:** `lois4801/NEXUS-Agentic-OS`

## Decision

Use one independent **control plane** and **execution runtime** for Lucio AI Platform, Ember and future applications. Keep every application's own business logic and credentials within its existing repository and infrastructure. Supply **project-scoped adapters/agent packs**, rather than cloning the OS per project. Do not relocate Clawd-Code or Nexus-Code2 into this repository; any future integration should be via an authenticated adapter, preserving original repositories and their licences.

## Code and responsibility boundaries

| Boundary | Implemented now | Next release |
|---|---|---|
| Identity | Admin bearer token; randomly generated per-project key, hash stored in SQLite | Key rotation, OIDC, workload identities |
| Tenant isolation | Project ID enforced per endpoint, note namespace isolated | Postgres row-level security, isolation tests |
| Orchestration | Bounded synchronous agent loop; event log; approval pause/resume | Durable queue, cancellation, timeouts, retries |
| Agents | General, builder, research prompt profiles with per-project enable flags | Skill registry, structured typed plans, evaluator |
| Models | Deterministic demo and a configurable OpenAI-compatible endpoint | Verified provider-specific adapters, budget/fallback routing |
| Tools | Calculator, UTC time, project notes | GitHub, file sandbox, MCP, web evidence, CRM connectors |
| Client integrations | Python, server-side TS SDK | Streaming run view, telemetry, Lucio/Ember UI integrations |
| QA | Offline API/isolation/approval tests | Real-model E2E, pen test, concurrency and load tests |

## Threat boundaries

**Trusted:** server config, admin operator, code-reviewed tool handlers. **Untrusted:** prompts, model outputs, external tool results, user-supplied URLs, arbitrary repository content. Validate actions server-side; never allow a model response to select or instantiate arbitrary shell commands. No model-owned production secrets, cross-project credentials or unrestricted outbound web access. Sensitive writes require explicit approval. Tool adapters added later must implement audit traces, strong input schemas, idempotency where applicable and default-deny privileges.

## Storage / API contracts

**Tables:** `projects(project_id, spec_json, key_hash)`, `runs(run_id, project_id, agent, goal, status, answer, steps_used, events_json, pending_json)`, `notes(note_id, project_id, content)`. `project_id` is the tenant partition key. SQLite is for a single process and local integration; migrate with revisions to PostgreSQL for multiple workers/production.

**Endpoints:** `GET /health`; admin `POST /v1/projects`; scoped `GET /v1/projects/{project_id}`; scoped `POST /v1/projects/{project_id}/runs`; scoped `GET /v1/runs/{run_id}`; scoped `POST /v1/runs/{run_id}/approval`; scoped `GET /v1/projects/{project_id}/notes`.

**Run event types:** `tool_result`, `tool_error`, `approval_requested`, `approval_granted`, `approval_denied`, `policy_denied`, `provider_error`, `final`, `max_steps_reached`. An approval response is the **only** way to execute an approval-required tool.

## Extension protocol

1. Write and test a bounded tool handler in `nexus_os/tools.py` (no side effects without declared permissions).
2. Add its tool ID to the validated `ToolId` schema and tool description registry.
3. Mark all write/destructive/external side-effect tools as approval-required unless an explicit, reviewed alternative policy is adopted.
4. Enable it only for the project that needs it.
5. Add an integration test verifying normal execution, denial, cross-project isolation and fail-closed behavior.

## Exit criteria by phase

**Phase 1:** Clone the independent repo; install; `pytest` passes; register 2 different projects; run a calculator task with trace; cross-project access returns 403; approval is enforced; README and SDKs present.

**Phase 2:** GitHub connector only accesses approved repositories via scoped tokens; coding agents run in short-lived isolated workspaces; no writes to protected branches; user approves publishing; each task has reproducible test artifacts.

**Phase 3:** Add real multi-project PostgreSQL and a durable worker queue; migrate and verify row-level access; add task cancellation/timeout/quota/metering; provide a supported MCP registry.

**Phase 4:** Wire Lucio App Builder and Ember server-side routes to NEXUS; run real model+tool E2E; verify no client-side secrets or cross-project data leaks; prove rollback and disaster recovery.

## Change log

REV1 (2026-09-29): Independent private GitHub repository; implement runnable multi-project skeleton, model/provider adapter, allowlisted tools, approval gate, REST API, two SDKs, Docker and offline tests. No existing project source code modified.
