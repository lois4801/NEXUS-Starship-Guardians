---
name: nexus-run-operations
description: Use to submit or inspect bounded tasks in an existing authorized NEXUS Agentic OS instance, explain real run events, and handle project-scoped approvals only when explicitly authorized.
---

# NEXUS run operations

Use this for task submission, run inspection, or explicit pending-approval decisions. Source contracts: `nexus_os/api.py`, `nexus_os/orchestrator.py` and `nexus_os/models.py` from the source repo.

## Procedure

1. Establish the NEXUS project ID, enabled agent, endpoint and what the user wants to do. Do not request that the user paste access tokens into chat. Use host-managed environment secrets `NEXUS_URL` and `NEXUS_PROJECT_KEY` when a local shell/Python host exists. Every NEXUS app must use its **own** project key.
2. Inspect an existing run with `GET /v1/runs/{run_id}`, or submit a goal through `POST /v1/projects/{project_id}/runs` with JSON `{"goal":"...", "agent":"general"}` if the user asked for execution. If Python and authorized network access exist, use the bundled `scripts/nexus_cli.py` for these calls. Otherwise explain how the owner can perform them; do not report a fabricated run.
3. Report actual status (`completed`, `pending_approval`, `failed`, `max_steps`) and distinguish `tool_result`, `tool_error`, `provider_error`, `policy_denied`, and `approval_requested`. A final assistant message from the demo provider is not evidence that code was changed.
4. For `pending_approval`, show the exact proposed tool and arguments (redact secrets and sensitive data). Explain consequences and ask the authorized user to explicitly approve or deny. Never infer authorization from a general instruction to "keep going"; never silently auto-approve writes.
5. Only after that explicit decision, the current authorized host may call `POST /v1/runs/{run_id}/approval` with `{"approved":true}` or `false` using the *owning project's* token. Inspect the updated run and verify an `approval_granted`/`approval_denied` event.
6. Provide the run ID, verified status, summary of evidence, open questions and any unverified integrations.

## Optional CLI

Run from this Skill directory only when the host actually has Python 3.11+ and permitted network access, e.g.:

```sh
python scripts/nexus_cli.py health
python scripts/nexus_cli.py run --project lucio-dev --agent general --goal "calculate 12 * 7"
python scripts/nexus_cli.py inspect --run-id RUN_ID
```

`NEXUS_URL` and `NEXUS_PROJECT_KEY` must come from secure host environment configuration. Use `approve --run-id RUN_ID --decision yes` **only** after explicit approval; `no` only for explicit denial. `inspect --full` may show private run events and should only be used where that disclosure is authorized.

Never claim this Skill is an MCP connection. It does not deploy NEXUS or provide model, GitHub, terminal, browsing, or deployment features absent from the running backend.
