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

## Recommended team sizing

- Small fix or review: 4-12 agents.
- Feature build: 12-32 agents.
- Cross-stack feature or migration: 24-64 agents.
- Large audit, broad refactor, multi-system integration, or release review: 50-120 agents.
- Full 200-agent mode: reserve for large, highly decomposable missions where independent specialist perspectives materially help.

The scheduler supports 200 agents, but it does not assume that 200 is always faster. For small tasks, coordination overhead can dominate. NEXUS should use the smallest team that covers the required specialties and verification needs.

## Safety and execution

The swarm coordinator performs reasoning/model calls only. State-changing tools should continue through NEXUS approval and tool-policy boundaries. Do not give every specialist unrestricted filesystem, shell, deployment, credential or cross-project access.
