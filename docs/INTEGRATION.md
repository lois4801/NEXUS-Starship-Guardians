# Lucio / Ember integration playbook

## First deploy NEXUS separately

Deploy NEXUS as its own backend service on a trusted server with HTTPS. For a smoke test, use local `127.0.0.1`. Set a unique strong `NEXUS_ADMIN_TOKEN`, persist the SQLite volume and use **exactly one worker** for v0.1. For public or multi-worker deployment, complete the PostgreSQL + job-queue and security phase first.

## Register projects separately

The NEXUS admin registers `lucio-dev` and `ember-dev` as different project records. Capture each `api_key` **once** and store it in each application's **server-side secrets**. Never share one project API key between apps.

Suggested starter profiles: Lucio = agents `general,builder,research`, tools `calculator,utc_now`, model provider `demo` until an authorized model is connected; Ember = agents `general,builder`, same starter tools. Do not register `project_note` unless that app has an explicit approval UI.

## Lucio backend adapter

Create a server-only route (e.g. `/api/agents/run`) in your existing application. Authenticate the **Lucio end user** using Lucio's existing auth. Validate that user's access to the requested Lucio project. Call NEXUS with the saved `lucio-dev` project API key using the server-side TypeScript SDK. Forward only authorized goal text, supported agent IDs and appropriate run status; do not forward upstream raw credentials, other tenant identifiers or full NEXUS trace if it contains internal data. Render the `events` and `pending_approval` status in the existing UI.

## Ember backend adapter

Create the equivalent server-only adapter using Ember's own project key. Retain Ember's current authentication, data storage and application-specific coding engine. Keep a narrow tool bridge; do not give NEXUS broad database administrator or GitHub account-wide tokens. The v0.1 OS is independent of Ember and cannot diagnose or alter its source without adding and verifying a separately authorized integration.

## CI and acceptance tests

1. Register distinct projects and store separate secrets.
2. Verify a `calculate 12 * 7` task returns a real `84` calculator event from each app.
3. Verify Lucio's key cannot read Ember's project, notes or runs, and vice versa.
4. Verify non-enabled agent IDs and unallowlisted tools are denied.
5. Add the approval UI before enabling any write tool.
6. For real AI behavior, connect a supported local/hosted model; test JSON-action adherence and handle invalid outputs as errors, not simulated success.

## Follow-on integration prompt for a coding agent

> Read `docs/ARCHITECTURE.md`, `docs/INTEGRATION.md` and the existing application's actual source. Preserve all current app routes, user auth, databases, deployments and the entire Git history. Add a server-side NEXUS SDK adapter only. Use a distinct per-app project key in server secrets; never expose it in browser bundles. Add auth checks and cross-tenant tests. First prove the offline calculator smoke test and real event tracing. Do not claim the app-builder, GitHub coding, deployment or web-scraping capabilities work until a real tool integration and repeatable tests demonstrate it. Submit a tested pull request, not a direct production merge.
