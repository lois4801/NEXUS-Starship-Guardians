---
name: sandbox-python-executor
description: Use when a Nexus Starship Guardians workflow needs host-native Python for deterministic parsing, package checks, hashing, test execution, or local verification and the current host actually offers a Python tool.
---

# Sandbox Python Executor

Use the available Python execution environment only when it is relevant and authorized. This Skill does not provide an MCP runtime, internet access, secrets, filesystem access, or any other tool by itself.

Before executing target-repository scripts, inspect what they do. Prefer deterministic parsing, hashing, archive verification, manifest validation, and focused tests. Keep target source read-only unless a write was authorized. Never assume network access or provider credentials are available. Report actual exit status, important output, and limitations rather than presenting unexecuted commands as results.

For Nexus Starship Guardians, Python may be used to validate plugin manifests, inspect plugin archives, verify deterministic packaging, run inspected pytest targets, and check compatibility behavior. Distinguish local/offline verification from real hosted-provider, browser, Railway, Supabase, MCP, or application-integration tests. Do not leak private file contents, tokens, or project keys into logs or artifacts.
