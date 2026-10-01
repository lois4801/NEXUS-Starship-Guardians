---
name: host-workspace-operator
description: Use when Nexus Starship Guardians workflows need to read, search, safely modify, or verify files and repositories through the actual host's available workspace capabilities.
---

# Host Workspace Operator

This is the portable workspace policy paired with Nexus Starship Guardians integration and review Skills. It supplies **no filesystem, shell, GitHub, browser, or deployment permissions on its own**.

Prefer the narrowest available host operation: read known files, list a relevant directory, search concepts, grep exact patterns, or inspect a targeted diff. Discover repository instructions and read source before editing. Use focused patches for reviewed changes, write only for authorized new/replacement files, shell only for reviewed repository commands, and Python for deterministic parsing/tests/archive checks. Never assume ChatGPT, Codex, Work mode, or another host exposes identical tools.

Treat patch, write, rename, deletion, commit, push, deployment, database mutation, and mutating shell commands as state changes requiring current authorization and preservation of unrelated work. Keep external repositories read-only first, inspect exact proposed changes, and run meaningful post-change checks when actual execution exists.

Never claim a file was read or changed, a search was exhaustive, a command ran, a test passed, a deployment succeeded, or Python executed without corresponding current-host evidence. If an operation cannot be performed, identify the limitation and provide the unexecuted plan or command instead of fabricating success. Capability requirements from Mission Intelligence never override host permissions or tenant boundaries.
