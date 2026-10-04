# OpenCode Provider

Nexus Starship Guardians can dispatch Guardian missions to the
[OpenCode CLI](https://opencode.ai) — the free, open-source terminal coding
agent (75+ model providers) — running on your local desktop. This lets a
Guardian swarm execute with a provider free tier (for example Google Gemini:
60 requests/min, 1,000 requests/day) or fully local models, with no paid
subscription.

OpenCode is an **execution backend**, not a permission grant. The Controlled
Tool Gateway, approval gates, and evidence requirements are unchanged, and
NEXUS never stores provider credentials — whichever model OpenCode is signed
into is the model the Guardians get.

## Install OpenCode (Windows)

```powershell
irm opencode.ai/install.ps1 | iex
opencode          # first run: choose a provider or paste an API key
```

Get a free Google key at [aistudio.google.com](https://aistudio.google.com)
if you want the zero-cost tier.

## Run Guardians through OpenCode

```powershell
# Single prompt
nexus-guardians ask --provider opencode "Explain the Nexus swarm coordinator"

# A 30-Guardian swarm on your desktop, free Gemini model
nexus-guardians swarm --provider opencode --model google/gemini-3-flash `
    --guardians 30 "Build, review, test, repair, evaluate, and document this feature"

# Use OpenCode's own configured default model (omit --model)
nexus-guardians swarm --provider opencode --guardians 12 "Audit the provider adapters"
```

## 200-Guardian brainstorm

```powershell
# 200 logical Guardians: divergent ideas -> candidate plan -> red-team critique -> refined plan
nexus-guardians brainstorm --provider opencode --model google/gemini-3-flash `
    "Design the v1 architecture for a multi-tenant AI app"
```

`brainstorm` runs two swarm passes (diverge and critique), so a 200-Guardian
mission makes roughly 400 provider requests plus synthesis, refinement, and the
learned-lesson reflection. At the Gemini free tier (60 requests/min) expect on
the order of 10 minutes end-to-end — well inside the 15-minute per-worker
timeout. Scale `--guardians` and `--max-parallel` to your quota.

The output prints the candidate plan (pre-review), the final refined plan, and
one learned lesson persisted to the Guardian learning memory.

Check detection with:

```powershell
nexus-guardians doctor
```

`doctor` reports whether the `opencode` executable is on PATH alongside
`ollama`, `claude`, `codex`, and `gemini`.

## Behavior

- Runs `opencode run --format text [--model PROVIDER/MODEL] "<prompt>"`
  headlessly; one OpenCode invocation per Guardian worker.
- Each Guardian worker has a 15-minute timeout; a timeout fails that worker
  only and is reported in the swarm summary, mirroring the bounded-concurrency
  contract (a swarm is up to 200 logical Guardians, not 200 shell processes).
- Non-zero exits surface the CLI's stderr so failures stay diagnosable.

## The ten specialist Guardians as OpenCode agents

The repository ships `.opencode/agent/*.md`: the ten specialist Guardians
(AI Architect, Software Platform Engineer, AI Developer, Coder Specialist,
AI Engineer, Debugger Specialist, AI Scientist, AI Cloud Specialist,
API Specialist, AI Programmer) as OpenCode subagents, each with its own tool
permissions and Nexus governance rules in its system prompt. Repository-wide
conventions live in [`AGENTS.md`](../AGENTS.md). When you run `opencode`
locally in this repo, Guardian behavior follows the same evidence-before-claims
and compatibility-contract rules as the runtime.

## Free-tier limits

Provider free tiers are shared across all parallel workers. With Gemini's
1,000 requests/day, a 30-Guardian swarm consumes roughly 30 requests per pass
plus synthesis — comfortable for daily use, but scale `--guardians` and
`--max-parallel` to your quota.
