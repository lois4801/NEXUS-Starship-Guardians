# NEXUS Multi-Agent Swarm

NEXUS supports **up to 200 logical agents per mission**. Logical team size and physical concurrency are deliberately separate: a mission can involve 200 specialists while only a safe number of model/process calls run at once.

## Why bounded concurrency

Launching 200 simultaneous local-model or CLI processes can make a workstation slower, exhaust RAM/VRAM, trigger provider throttles, or increase duplicate work. NEXUS therefore uses a bounded semaphore. The default parallelism is based on CPU count and capped at 16; operators can override it per run.

## CLI

```bash
nexus-portable swarm --provider ollama --model llama3.2 --agents 24 \
  "Build and verify a production-ready FastAPI service"
```

Maximum logical team:

```bash
nexus-portable swarm --provider ollama --model llama3.2 --agents 200 --max-parallel 8 \
  "Audit, improve, test, document, and prepare this project for release"
```

For an authenticated coding CLI adapter, configure `NEXUS_LLM_COMMAND` as documented in `PORTABLE_LLM_RUNTIME.md`, then use `--provider cli`.

## Coordination model

1. NEXUS builds a diverse specialist roster across architecture, frontend, backend, API, database, security, DevOps, QA, debugging, performance, UX, accessibility, research, evidence, documentation, product, integration, release, observability, data, AI engineering, code review, migration, CI/CD, compliance and related roles.
2. Specialists receive the same mission plus a role-specific assignment.
3. Calls run concurrently up to `max_parallel`.
4. One agent failure is isolated; the remaining team continues.
5. Successful outputs are compacted into a bounded evidence payload.
6. A lead orchestrator synthesizes the work, resolves conflicts, removes duplication, orders dependencies, and defines verification gates.

## Important operating rule

`--agents 200` means **200 collaborating logical specialists**, not 200 unrestricted simultaneous shell processes. This distinction is intentional. More agents are not automatically faster for small tasks; large teams are most useful for broad builds, audits, migrations, testing matrices, research and independent verification. Start with 12-32 for normal development and scale toward 200 for genuinely decomposable work.

## Safety and execution

The swarm coordinator performs reasoning/model calls only. State-changing tools should continue through NEXUS approval and tool-policy boundaries. Do not give every specialist unrestricted filesystem, shell, deployment, credential or cross-project access.
