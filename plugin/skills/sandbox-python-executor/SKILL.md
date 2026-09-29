---
name: sandbox-python-executor
description: Use when a NEXUS workflow needs host-native Python for deterministic parsing, package checks, hashing, test execution or local verification and the current host actually offers a Python tool.
---

# Sandbox Python Executor

Use the **python tool** in ChatGPT when it is available and relevant, or an authorized Python environment in Codex. This Skill does not provide an MCP runtime or grant a tool.

Before executing target-repository scripts, inspect what they do. Prefer deterministic local parsing, hashing and archive verification. Keep target source read-only unless a write was authorized. Never assume sandbox internet access or secrets are available. Run checks and report actual exit status, important output and limitations rather than pasting commands and describing them as executed. Avoid leaking private file contents or credentials in logs.

For NEXUS, use Python to validate manifest JSON, inspect plugin archives, check source snippets or invoke inspected `pytest` only when dependencies and safe execution exist. Record exact skipped integration/real-model checks rather than declaring them passed.
