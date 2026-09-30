# Nexus Universe Agents — Parallel Coding Workflow

Nexus Universe Agents can decompose a software mission into isolated coding tasks and assign each task its own Git worktree and branch.

## Flow

1. Analyze the mission and select the smallest useful specialist team.
2. Convert implementation work into dependency-aware tasks.
3. Create one isolated Git worktree per writable coding task.
4. Run coding/planning agents in parallel with bounded concurrency.
5. Apply changes only through an explicitly configured execution worker; model text is never treated as shell code.
6. Run project tests, linting, type checks, security checks, or browser tests as configured.
7. Send results to independent review/verification agents.
8. Commit only verified worktree changes.
9. Push reviewed branches and create draft pull requests through the user's authenticated GitHub tooling.
10. Merge or deploy only after required approval and CI gates pass.

## Implemented modules

- `nexus_os.coding_worktrees.WorktreeManager`: creates/removes isolated Git worktrees and commits reviewed changes.
- `nexus_os.parallel_coding.ParallelCodingCoordinator`: runs multiple coding-agent proposals against isolated worktrees with bounded concurrency.
- `nexus_os.verification_pipeline.VerificationPipeline`: executes allowlisted quality gates in a task worktree using the restricted process worker.
- `nexus_os.github_pr.PullRequestPublisher`: creates draft PRs and inspects PR checks through an already authenticated `gh` CLI.

## Isolation

Branches use the `nua/task-<task-id>` convention. Worktree paths are constrained under a configured workspace root. Task IDs are restricted to safe characters and Git commands use argv execution instead of a shell.

## Parallelism

A mission may involve up to 200 logical agents, but writable worktrees and active coding processes should remain bounded. Reasoning/review teams can be much larger than the number of agents permitted to modify code simultaneously.

Example policy:

- 1–200 logical specialist agents
- 4–16 simultaneous model calls on a workstation
- 2–8 simultaneous writable coding worktrees
- independent test/review workers after implementation
- one release integrator responsible for final merge ordering

## Pull requests

`PullRequestPublisher` uses an already authenticated `gh` CLI. Nexus Universe Agents does not accept a GitHub token from model output and never bypasses the user's GitHub permissions.

## Current boundary

The current coordinator creates isolated workspaces, obtains coding proposals, runs allowlisted verification gates, and provides safe process/PR primitives. Fully autonomous patch application is intentionally not performed by interpreting arbitrary model-generated shell commands. A future structured patch worker can apply file-level edits while preserving workspace and approval constraints.
