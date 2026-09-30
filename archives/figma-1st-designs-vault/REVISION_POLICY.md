# Figma 1st Designs Vault — Revision Policy

Current baseline: `FIGMA_VAULT_V1.0`

## Naming rule

GitHub and Supabase must always use the exact same revision label.

Revision sequence:
- `FIGMA_VAULT_V1.0` — immutable first baseline
- `FIGMA_VAULT_V1.1` — next additive update
- `FIGMA_VAULT_V1.2` — next additive update
- continue sequentially for catalog/metadata/preservation updates
- use `FIGMA_VAULT_V2.0` only for a major vault-architecture or production-generation change

## Preservation rules

1. Never overwrite or delete a prior revision snapshot.
2. Every new update creates a new revision folder in GitHub and a matching revision row/snapshot in Supabase.
3. Project names, Figma file keys, page names, node IDs, scene names, and prototype URLs must remain identical across GitHub and Supabase.
4. Binary assets keep the same logical project/revision names in Supabase Storage.
5. Original Figma references remain preserved even after improved Lucio versions are created.
6. Unknown or unavailable assets must be marked pending, not assumed archived.
7. Each revision must record counts for projects, pages, scenes, assets, and versions.

## GitHub canonical paths

Current mirror root:
`archives/figma-1st-designs-vault/`

Immutable snapshots:
`archives/figma-1st-designs-vault/revisions/<REVISION_LABEL>/`

## Supabase canonical locations

Project: `Websites`
Schema: `figma_vault`
Private bucket: `figma-1st-designs-vault`

Revision labels in Supabase must match the GitHub folder name exactly.

## Update procedure

For every future vault change:
1. Determine next revision label.
2. Scan/import new Figma information.
3. Update Supabase project/page/scene/asset records.
4. Create immutable Supabase revision snapshot.
5. Create matching GitHub revision folder and snapshot files.
6. Update `CURRENT_REVISION.json` and `REVISION_LOG.md`.
7. Verify GitHub and Supabase counts/names match before declaring the revision complete.
