# Figma 1st Designs Vault

Version: `FIGMA_VAULT_V1.0`

This is a preservation mirror of the first Figma design collection being prepared for the Lucio AI Platform design system. The original Figma files remain the source of truth and are not modified by this archive.

## Current inventory

- 9 Figma source files
- 86 catalogued Figma pages
- 26 identified UI / cinematic / animation scene records
- 56 GRIGOLETTO template pages
- 8 Arkkhe design studies with dedicated Cover / Ui / Animations pages

## Preservation model

The GitHub mirror stores text-based manifests, Figma IDs, prototype references, motion notes, reconstruction specifications, and future source code. Heavy binary assets such as MP4s, exported imagery, `.fig` local copies, and large media are intended to live in the private Supabase Storage bucket `figma-1st-designs-vault`, with their paths and checksums referenced here.

## Supabase mirror

Supabase project: `Websites`

Archive schema: `figma_vault`

Private Storage bucket: `figma-1st-designs-vault`

Tables:
- `figma_vault.projects`
- `figma_vault.pages`
- `figma_vault.scenes`
- `figma_vault.assets`
- `figma_vault.versions`

## Source projects

1. GRIGOLETTO — 56 templates
2. New Arkkhe 05 — Altura
3. New Arkkhe 07 — Vulka
4. New Arkkhe 06 — Scarabyte
5. New Arkkhe 04 — Mystral
6. New Arkkhe 03 — Veldrah
7. New Arkkhe 02 — Elevation House
8. New Arkkhe 01 — VYRA
9. New Arkkhe 08 — Longyu

## Archive rule

Original designs must never be overwritten. Improved Lucio versions should be stored as new versions such as `V1.1 faithful recreation`, `V2 responsive`, `V3 optimized`, and later production editions.