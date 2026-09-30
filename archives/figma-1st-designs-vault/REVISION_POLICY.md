# Figma 1st Designs Vault — Live Update Policy

Canonical vault label: `FIGMA_VAULT_V1.0`

## Operating model

`FIGMA_VAULT_V1.0` is now the live canonical vault. We will update and overwrite the canonical files and Supabase records as the designs are improved.

The rule is simple:

**Stage → Build → Test → Verify → Update Canonical GitHub → Sync Canonical Supabase → Verify Again**

Nothing replaces the canonical vault until the proposed change has passed its required checks.

## Source-of-truth rules

1. GitHub and Supabase must use the same project names, Figma file keys, page names, node IDs, scene names, prototype references, asset names, and canonical vault label.
2. The canonical label remains `FIGMA_VAULT_V1.0` while this design vault evolves continuously.
3. Canonical files may be overwritten only after the candidate update is verified working.
4. GitHub commit history is the rollback/history mechanism for text, manifests, specifications, and production code.
5. Supabase stores the current verified metadata and binary/media assets under matching logical names.
6. Original Figma references remain recorded even when the website implementation is improved.
7. Unknown, missing, or unverified cinematic behavior must be marked pending rather than guessed.
8. Never publish an update as working until functional checks, responsive checks, and cinematic/motion checks pass where applicable.

## Canonical GitHub paths

Repository: `lois4801/NEXUS-Agentic-OS`
Branch: `archive/figma-1st-designs-vault-v1`
Vault root: `archives/figma-1st-designs-vault/`

Canonical files include:
- `README.md`
- `VAULT_MANIFEST.json`
- `SCENES.json`
- `PRESERVATION_STATUS.md`
- `CURRENT_REVISION.json`
- `REVISION_LOG.md`
- `REVISION_POLICY.md`
- future website source, motion specifications, tests, and reconstruction code

The existing `revisions/FIGMA_VAULT_V1.0/` folder is retained as the original baseline reference, but routine future work updates the canonical files at the vault root instead of creating a new revision folder for every change.

## Canonical Supabase locations

Project: `Websites`
Schema: `figma_vault`
Private bucket: `figma-1st-designs-vault`
Canonical label: `FIGMA_VAULT_V1.0`

Supabase project/page/scene/asset records are updated only after validation. The canonical `FIGMA_VAULT_V1.0` snapshot may then be refreshed to match the verified GitHub state.

## Required validation before overwrite

For each website/design change, check as applicable:
- source/build completes without errors
- page renders correctly
- desktop layout works
- tablet layout works
- mobile layout works
- navigation and CTAs work
- images/video assets load
- cinematic scroll sequence works
- prototype-equivalent states are represented correctly
- animations work forward and backward where intended
- reduced-motion fallback works
- no major console/runtime errors
- no broken links/assets
- performance is acceptable for the current development stage

## Update procedure

1. Inspect the current canonical source.
2. Build the proposed improvement in a staging/work area or isolated branch/state.
3. Run the applicable validation checks.
4. Fix failures and repeat tests until passing.
5. Overwrite/update the canonical GitHub files only after passing.
6. Update the matching Supabase metadata/media using the same names.
7. Refresh the canonical Supabase snapshot for `FIGMA_VAULT_V1.0`.
8. Re-read/verify both GitHub and Supabase to confirm they match.
9. Add a dated entry to `REVISION_LOG.md` describing what changed and what was tested.

## Rollback

If a later update causes a problem, restore the previous verified GitHub commit and resync the corresponding canonical Supabase records/assets.
