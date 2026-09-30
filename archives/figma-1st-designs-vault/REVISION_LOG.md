# Figma 1st Designs Vault — Revision Log

## FIGMA_VAULT_V1.0

Status: live canonical vault

Initial scope preserved:
- 9 Figma source projects
- 86 catalogued pages
- 56 GRIGOLETTO templates
- 26 identified cinematic/UI/animation scene records
- Elevation House prototype reference
- Figma file keys, page IDs, node IDs, dimensions, tags, and known motion notes
- Supabase project/page/scene/version metadata mirror
- Private Supabase Storage bucket prepared for binary media

GitHub branch:
`archive/figma-1st-designs-vault-v1`

Supabase:
- project: `Websites`
- schema: `figma_vault`
- bucket: `figma-1st-designs-vault`

Pending binary preservation:
- `.fig` local copies
- source MP4/WebM files
- original image/SVG exports
- exact prototype playback recordings
- full-page visual captures

### Policy update — live verified overwrite model

The vault now uses a test-before-overwrite workflow rather than creating a new numbered revision for every routine update.

Workflow:
`stage → build → test → verify → update canonical GitHub → sync canonical Supabase → verify sync`

`FIGMA_VAULT_V1.0` remains the canonical vault label. Canonical files and Supabase records may be updated/overwritten only after the proposed change passes all applicable tests. Git commit history provides rollback for repository content. The original `revisions/FIGMA_VAULT_V1.0/` snapshot remains preserved as the initial baseline reference.

Every future update should append a dated change entry here describing:
- what changed
- which website/design was affected
- what tests were run
- whether the update passed
- what GitHub/Supabase records were synchronized
