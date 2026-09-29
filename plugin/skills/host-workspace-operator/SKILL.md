---
name: host-workspace-operator
description: Use when NEXUS workflows need to read, search, safely modify or verify files and repositories through the actual host's available workspace capabilities.
---

# Host Workspace Operator

This is the portable workspace policy paired with the NEXUS integration and review Skills; it supplies **no** filesystem permissions on its own.

Prefer the narrowest available host operation: read known files; list a relevant directory; search concepts; grep exact patterns. Discover repository instructions and read source before editing. Use patch for focused changes, write for authorized new/replace operations, shell for reviewed repository commands and Python for deterministic parsing, tests or archive checks. Never assume ChatGPT and Codex expose identical tools.

Treat patch, write, rename, deletion and mutating shell commands as state changes requiring the user's authorization and preservation of unrelated work. Use the same read-only-first policy for external connected repositories and inspect exact proposed changes. Run meaningful post-change checks when actual execution exists.

Never claim a file was read or changed, a search was exhaustive, a shell command ran or Python executed without corresponding current-host tool evidence. If an operation cannot be performed, return the unexecuted command or plan, identify the limitation and do not fabricate a result. Do not turn an app integration into unrestricted shell or cross-tenant access.
