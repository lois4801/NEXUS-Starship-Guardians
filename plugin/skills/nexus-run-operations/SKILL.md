---
name: nexus-run-operations
description: Use to submit or inspect bounded tasks in an existing authorized Nexus Starship Guardians instance, explain real run evidence, and handle project-scoped approvals only when explicitly authorized.
---

# Nexus run operations

Use this Skill for task submission, run inspection, or explicit pending-approval decisions. Current source contracts are `nexus_os/api.py`, `nexus_os/orchestrator.py`, and `nexus_os/models.py`.

## Procedure

1. Establish the Nexus project ID, enabled Guardian, endpoint, and requested operation. Do not ask users to paste access tokens into chat. Use host-managed secrets `NEXUS_URL` and `NEXUS_PROJECT_KEY` where an authorized shell/Python host exists. Each application must use its own project key.
2. Inspect an existing run with `GET /v1/runs/{run_id}` or submit a goal through `POST /v1/projects/{project_id}/runs`. REST v1 intentionally retains the compatibility payload field `agent`, e.g. `{"goal":"...", "agent":"general"}`, while product terminology remains Guardian.
3. If Python and authorized network access exist, use the bundled `scripts/nexus_cli.py`. Otherwise provide the exact unexecuted request/command and do not fabricate a run.
4. Report actual status (`completed`, `pending_approval`, `failed`, `max_steps`) and distinguish tool/provider/policy/approval evidence. A model statement alone is not proof that files, deployments, tests, or external services changed.
5. For `pending_approval`, show the proposed tool and safely redacted arguments, explain consequences, and require an explicit approve/deny decision. Never infer approval from a generic instruction to continue.
6. Only after explicit authorization may the current authorized host call `POST /v1/runs/{run_id}/approval` with `{"approved": true}` or `false` using the owning project's token. Inspect the resulting run and evidence after the decision.
7. Return the run ID, verified status, relevant evidence, remaining uncertainty, and any external integrations that were not actually exercised.

## Optional CLI

```sh
python scripts/nexus_cli.py health
python scripts/nexus_cli.py run --project lucio-dev --guardian general --goal "calculate 12 * 7"
python scripts/nexus_cli.py inspect --run-id RUN_ID
```

The CLI also accepts legacy `--agent` for compatibility. It sends the current REST v1 wire field `agent` internally. `NEXUS_URL` and `NEXUS_PROJECT_KEY` must come from secure host configuration. Use `approve --run-id RUN_ID --decision yes|no` only for an explicit current decision.

This Skill is not itself an MCP connection and does not grant GitHub, terminal, browser, provider, infrastructure, or deployment permissions.
