# NEXUS Execution Swarm

The Execution Swarm turns multi-agent plans into a controlled dependency graph of work. It is designed to let many specialists contribute while keeping state-changing actions bounded, reviewable, and isolated.

## Architecture

```text
Mission
  -> 1-200 logical specialists
  -> lead synthesis
  -> ExecutionTask DAG
       -> read / analyze workers
       -> coding workers
       -> test workers
       -> verification workers
       -> approved write/deploy workers
  -> evidence gate
  -> final release decision
```

## What is implemented

- dependency-aware `ExecutionCoordinator`
- bounded parallel execution from 1 to 200 workers
- unique task IDs and dependency validation
- cycle and unknown-dependency rejection
- explicit `requires_approval` gate
- downstream skip behavior when a dependency fails or is blocked
- per-task verification hook
- failure isolation for independent work
- restricted local process worker using argv execution with no shell
- executable allowlist
- workspace-root containment
- process timeout and output caps

## Why logical agents and execution workers are separate

A 200-agent reasoning swarm may create many findings, but only a subset should be allowed to mutate a repository or environment. NEXUS therefore separates:

1. **specialists** — reason, inspect, review, propose, test plans, find defects;
2. **execution tasks** — concrete work units with dependencies;
3. **workers** — controlled capabilities that can carry out an approved task;
4. **verifiers** — independently check results before dependent tasks or release gates continue.

This prevents a large team from becoming 200 unrestricted terminals.

## Restricted local process worker

`LocalProcessWorker` uses `asyncio.create_subprocess_exec`, never a shell string. Operators configure an explicit executable allowlist and one workspace root. A process cannot select a working directory outside that root through the worker API.

Example policy:

```python
from pathlib import Path
from nexus_os.workers import LocalProcessWorker, ProcessPolicy

worker = LocalProcessWorker(
    ProcessPolicy(
        workspace_root=Path("./workspace"),
        allowed_executables=frozenset({"python", "pytest", "ruff", "git"}),
        timeout_seconds=120,
    )
)
```

Allowlisting an executable does not make every invocation safe. Production deployments should add per-command policies, isolated containers/worktrees, resource limits, secret filtering, network restrictions, and audit logging.

## Next worker adapters

The interfaces are intentionally provider-neutral. Planned adapters include:

- isolated Git worktree coding worker
- GitHub branch / pull-request worker
- filesystem patch worker with path scopes
- container sandbox worker
- browser test worker
- Supabase migration/query worker
- Railway deployment worker
- MCP tool gateway worker
- artifact/evidence collector
- release verifier

Writes, deployment, database mutation, credential changes, and external messaging should remain approval-gated even when reasoning agents are fully automatic.
