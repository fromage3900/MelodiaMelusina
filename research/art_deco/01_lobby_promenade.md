# Study: Art Deco Lobby Promenade (tower-ban rematerialize)

**Style:** art deco / civic lobby  
**Version:** 0.2  
**Sources:** 1920s–30s street-level deco lobbies, cinema foyers, department-store promenades (horizontal civic, not setback skyscraper spines)

## Motifs

- Street facade as primary hero plane (no tessellation tower / obelisk)
- Geometric recessed panel wall as mid-block band
- Chevron / geometric filigree screens
- Cusped deco portal as ceremonial gate
- Balconette as mezzanine accent
- Inclined public ramp as approach monument

## Proportions

- Facade mid-rise (~10–14 m) with 3–5 bay rhythm
- Panel wall long horizontal run (~10–12 m), height ~3.5–4.0 m
- Filigree screens ~1.5–2.2 m
- Ramp rise ~2.0–2.8 m over 7–9 m run

## Rhythms

- Horizontal civic chain: facade → panel wall → filigree → cusped portal → balcony → ramp
- Prefer lateral procession and mezzanine layering over vertical monument stacking
- Corner accents use pillars, never towers / obelisks / keeps

## Structural rules

- Banned arch types in this grammar: TOWER, TESSELLATION_TOWER, BELL_TOWER, WATCHTOWER, OBELISK, KEEP
- Compose `corner_tower` role maps to `_lib_PILLAR`
- Surreal transform: `axis_compression` (horizontal emphasis; replaces `vertical_stretch`)

## Ornament systems

- Recessed trim (`gb_trim_mode: RECESS`) for panel banding
- Geometric filigree (`GEOMETRIC_ARABESQUE`) as secondary accent
- AUTO materials; avoid vertical spire ornament

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| deco_street_facade | BAROQUE_FACADE | Lobby street front |
| geometric_panel_wall | GB_BRUTALIST_PANEL_WALL | Horizontal deco band |
| chevron_filigree | FILIGREE_PANEL | Geometric screen |
| cusped_portal | CUSPED_ARCH | Ceremonial gate |
| lobby_balconette | BALCONY | Mezzanine accent |
| approach_ramp | GREYBOX_RAMP | Public incline monument |

## OS hooks

- Genome: `art_deco_lobby_v1`
- Grammar graph: `ART_DECO`
- Compose style: `ART_DECO`
