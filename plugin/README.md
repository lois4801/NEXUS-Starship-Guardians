# NEXUS ChatGPT/Codex Plugin v0.1.0

This directory contains the portable, skills-only plugin generated from the existing private NEXUS Agentic OS v0.1 development starter. Source runtime code in `nexus_os/` and existing applications remain unchanged.

## Included Skills

- `nexus-project-setup`: separate per-app project configuration and safe onboarding.
- `nexus-run-operations`: scoped runs, real event inspection, explicit write approvals. Includes an optional Python-standard-library CLI.
- `nexus-app-integration`: server-only Lucio/Ember adapter workflow and acceptance tests.
- `nexus-readiness-review`: evidence-based security/QA readiness.
- `host-workspace-operator`: host-tool read-first and authorized mutation policy.
- `sandbox-python-executor`: actual deterministic Python verification when host supplies Python.

Both the portable root `plugin.json` and optional Codex compatibility `.codex-plugin/plugin.json` are included. This package intentionally declares **no MCP server, apps, hooks, screenshots or hard-coded credentials**: NEXUS v0.1 does not implement an MCP server. It cannot make ChatGPT call the live NEXUS API unless the current host actually supplies authorized HTTP or shell/Python access to a running NEXUS instance.

## Build ZIP

From this `plugin/` directory:

```sh
python -m zipfile -c ../../nexus-agentic-os-plugin.zip plugin.json .codex-plugin skills assets
```

For a clean archive, ZIP the contents of this directory so `plugin.json` lives at archive root. The Python one-liner above may be adapted for your preferred release process; don't package the NEXUS backend, `.env` or private credentials into the Plugin ZIP. Upload privately through Plugin Creator or use a compatible local marketplace. The approved plugin version is an independent snapshot; merging this source branch does not update the installed plugin automatically.

## Boundaries

Keep this repository and package private until a deliberate public-distribution review. The source repository has no declared open-source license, and no verified OpenAI publisher identity or public support/privacy/terms URLs are supplied. The Plugin is not submitted, approved or public. If an MCP integration is later implemented, separately review authentication, domain ownership, HTTPS deployment, tool annotations, approval controls and real end-to-end tests.
