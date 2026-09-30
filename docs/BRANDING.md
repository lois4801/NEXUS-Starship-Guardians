# Nexus Universe Agents

**Nexus Universe Agents** is the product name for this project going forward.

The existing GitHub repository name (`NEXUS-Agentic-OS`), Python import namespace (`nexus_os`), package name (`nexus-agentic-os`), executable (`nexus-portable`), and environment-variable prefixes remain temporarily unchanged for backward compatibility. Renaming those identifiers in one step would break existing clones, imports, scripts, plugin references, and integrations.

## Migration policy

- Product-facing UI, documentation, prompts, and future releases should use **Nexus Universe Agents**.
- Existing technical identifiers are compatibility aliases until a versioned migration is released.
- New integrations should not hard-code the old product name in user-facing text.
- A future major release may introduce new package/CLI identifiers with compatibility shims and deprecation notices.

## Product shorthand

Use **Nexus Universe** or **NUA** where a shorter internal label is useful. Do not silently rename repository/package identifiers until migration tooling exists.
