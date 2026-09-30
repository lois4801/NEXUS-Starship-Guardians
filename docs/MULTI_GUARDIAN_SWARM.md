# Nexus Starship Guardians — Multi-Guardian Swarm

Nexus Starship Guardians supports **up to 200 logical Guardians per mission**. Logical team size and physical concurrency are deliberately separate: a mission can involve 200 Guardians while only a safe number of model/process calls run at once.

## Why bounded concurrency

Launching 200 simultaneous local-model or CLI processes can make a workstation slower, exhaust RAM/VRAM, trigger provider throttles, or increase duplicate work. Nexus Starship Guardians therefore uses a bounded semaphore. The default parallelism is based on CPU count and capped at 16; operators can override it per run.

## CLI

```bash
nexus-portable swarm --provider ollama --model llama3.2 --guardians 24 \
  "Build and verify a production-ready FastAPI service"
```

Maximum logical team:

```bash
nexus-portable swarm --provider ollama --model llama3.2 --guardians 200 --max-parallel 8 \
  "Audit, improve, test, document, and prepare this project for release"
```

For an authenticated coding CLI adapter, configure `NEXUS_LLM_COMMAND` as documented in `PORTABLE_LLM_RUNTIME.md`, then use `--provider cli`.

## Coordination model

1. Nexus Starship Guardians builds a diverse Guardian roster across architecture, frontend, backend, API, database, security, DevOps, QA, debugging, performance, UX, accessibility, research, evidence, documentation, product, integration, release, observability, data, AI engineering, code review, migration, CI/CD, compliance and related roles.
2. Guardians receive the same mission plus a role-specific assignment.
3. Calls run concurrently up to `max_parallel`.
4. One Guardian failure is isolated; the remaining Guardians continue.
5. Successful outputs are compacted into a bounded evidence payload.
6. A lead Guardian synthesizes the work, resolves conflicts, removes duplication, orders dependencies, and defines verification gates.

## Recommended team sizing

- Small fix or review: 4-12 Guardians.
- Feature build: 12-32 Guardians.
- Cross-stack feature or migration: 24-64 Guardians.
- Large audit, broad refactor, multi-system integration, or release review: 50-120 Guardians.
- Full 200-Guardian mode: reserve for large, highly decomposable missions where independent specialist perspectives materially help.

The scheduler supports 200 Guardians, but it does not assume that 200 is always faster. For small tasks, coordination overhead can dominate. Nexus Starship Guardians should use the smallest team that covers the required specialties and verification needs.

## Execution contract

The current swarm layer is a reasoning and coordination engine. It can fan out provider/model calls and synthesize the results. It does not grant 200 Guardians unrestricted write access to GitHub, the filesystem, terminals, deployments, or databases. Those state-changing capabilities remain behind permissions, approvals, isolated workspaces, and verification gates.

## Safety and execution

The swarm coordinator performs reasoning/model calls only. State-changing tools continue through approval and tool-policy boundaries. Do not give every Guardian unrestricted filesystem, shell, deployment, credential, or cross-project access.
