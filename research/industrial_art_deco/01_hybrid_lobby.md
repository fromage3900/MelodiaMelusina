# Study: Industrial Art Deco Hybrid Lobby

**Style:** industrial art deco / civic lobby  
**Version:** 0.1  
**Sources:** 1920s–30s factory showrooms, power-station lobbies, deco machine-age civic halls

## Motifs

- Geometric panel wall as primary facade plane (no setback tower)
- Catwalk mezzanine as industrial horizontal spine
- Chevron / geometric filigree screens
- Hypostyle pillar hall as lobby volume
- Inclined public ramp approach
- Cusped deco portal as ceremonial gate

## Proportions

- Panel wall mid-rise (~3.5–4.5 m) with long horizontal run
- Catwalk length 8–12 m, shallow width (~1.5 m)
- Pillar hall 3×2 or 4×3 bay grid, spacing ~3.5–4.0 m
- Ramp rise ~2.0–3.0 m over 7–9 m run

## Rhythms

- Horizontal civic chain: panel wall → catwalk → filigree → pillar hall → ramp → cusped portal
- Prefer lateral procession and mezzanine layering over vertical monument stacking
- Corner accents use pillars, never towers / obelisks / keeps

## Structural rules

- Banned arch types in this grammar: TOWER, TESSELLATION_TOWER, BELL_TOWER, WATCHTOWER, OBELISK, KEEP
- Compose `corner_tower` role maps to `_lib_PILLAR`
- Surreal transform: `axis_compression` (horizontal emphasis)

## Ornament systems

- Recessed trim (`gb_trim_mode: RECESS`) for panel banding
- Geometric filigree (`GEOMETRIC_ARABESQUE`) as secondary accent
- AUTO / stone materials; avoid vertical spire ornament

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| deco_panel_wall | GB_BRUTALIST_PANEL_WALL | Geometric lobby facade |
| industrial_catwalk | GREYBOX_CATWALK | Mezzanine spine |
| chevron_filigree | FILIGREE_PANEL | Geometric screen |
| lobby_hypostyle | GREYBOX_PILLAR_HALL | Colonnaded hall |
| approach_ramp | GREYBOX_RAMP | Public incline |
| cusped_portal | CUSPED_ARCH | Ceremonial gate |

## OS hooks

- Genome: `art_deco_industrial_v1`
- Grammar graph: `ART_DECO_INDUSTRIAL`
- Compose style: `ART_DECO_INDUSTRIAL`
