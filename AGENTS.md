# NEXUS Repository Conventions for Coding Agents

This repository is **Nexus Starship Guardians v0.8.0** — a Guardian engineering
runtime (Python namespace `nexus_os`). Any coding agent (OpenCode, Claude Code,
Codex, Gemini CLI, …) working in this repo MUST follow these conventions.

## Hard rules

1. **Evidence before claims.** Never state that code was written, tested, or
   verified unless tool results prove it. A Guardian saying "done" is not
   verification — only `test`, `api`, `browser`, or `security` evidence counts.
2. **Compatibility contract.** Keep the canonical product name
   "Nexus Starship Guardians", the canonical CLI `nexus-guardians`
   (legacy alias `nexus-portable`), REST v1 wire fields `agent`/`agents`,
   and the `NEXUS_*` environment-variable prefix. Do not rename public surfaces.
3. **No permission inflation.** Never add filesystem, GitHub, cloud, database,
   deployment, browser, or model permissions as a side effect of a task.
   Authorization stays in the Controlled Tool Gateway, separate from intelligence.
4. **Governed learning only.** Do not auto-approve Benchmark Vault candidates,
   overwrite frozen benchmark corpora, or bypass promotion/release gates.

## Quality gates (must pass before any PR)

```powershell
ruff check nexus_os tests examples
$env:NEXUS_DEV_MODE = "true"; pytest -q
nexus-guardians doctor
```

Tests run in explicit local-only dev mode (`NEXUS_DEV_MODE=true`); production
fails closed without `NEXUS_ADMIN_TOKEN`.

## Structure map

- `nexus_os/` — runtime package (providers, swarm, guardians, learning, benchmarks)
- `nexus_os/portable/` — desktop CLI providers (`ollama`, `opencode`, `cli`) and the
  `nexus-guardians` CLI entrypoint
- `plugin/` — ChatGPT/Codex plugin manifest and skills
- `sdk/typescript` — TypeScript client SDK
- `tests/` — pytest suite mirroring module names
- `docs/` — architecture and governance documentation
- `.opencode/agent/` — the ten specialist Guardians as OpenCode subagents

## Ten specialist Guardians

The `.opencode/agent/*.md` files define the specialist wing. Invoke them as
subagents for work in their specialty; they carry Nexus governance in their
system prompts. The canonical 30-Guardian Artificial Architecture team remains
available through `nexus-guardians swarm`.

Nexus governance rules (always apply):
- Never claim code was written, tested, or verified unless tool results prove it.
  Self-reported success is not verification; evidence comes from test, api,
  browser, or security tool results.
- Preserve the compatibility contract: Python namespace `nexus_os`, CLI
  `nexus-guardians` (alias `nexus-portable`), REST v1 wire fields
  `agent`/`agents`, and the `NEXUS_*` environment-variable prefix.
- Run the quality gates before considering work done:
  `ruff check nexus_os tests examples` and `NEXUS_DEV_MODE=true pytest -q`.
- Peer lessons transfer knowledge, never status: reuse verified patterns,
  but never copy another Guardian's scores, permissions, or authority.
- You may adapt evidence and recommendations; you may never grant
  filesystem, GitHub, cloud, database, or deployment permissions.
