# Study: Art Deco Lobby Promenade

**Style:** art deco / civic lobby  
**Version:** 0.2  
**Sources:** 1920s–30s cinema and hotel lobbies, civic deco promenades, machine-age horizontal banding (tower-ban rematerialize)

## Motifs

- Stepped baroque-scale facade as lobby frontispiece (no setback tower)
- Geometric panel wall as long horizontal band
- Chevron / geometric filigree screens
- Cusped deco portal as ceremonial gate
- Balconette overlook along the promenade
- Inclined public ramp as approach terminus

## Proportions

- Facade mid-rise (~10–12 m) with 3–5 bay rhythm
- Panel wall run 8–12 m, height ~3.5–4.0 m
- Filigree screen ~1.5×2.2 m
- Ramp rise ~2.0–2.5 m over 7–9 m run

## Rhythms

- Horizontal civic chain: facade → panel wall → filigree → cusped portal → balcony → ramp
- Prefer lateral procession and mezzanine layering over vertical monument stacking
- Corner accents use pillars, never towers / obelisks / keeps

## Structural rules

- Banned arch types in this grammar: TOWER, TESSELLATION_TOWER, BELL_TOWER, WATCHTOWER, OBELISK, KEEP
- Compose `corner_tower` role maps to `_lib_PILLAR`
- Compose `large` → facade; `monument` → ramp (horizontal civic marker)
- Surreal transform: `axis_compression` (horizontal emphasis; demoted from `vertical_stretch`)

## Ornament systems

- Recessed trim (`gb_trim_mode: RECESS`) for panel banding
- Geometric filigree (`GEOMETRIC_ARABESQUE`) as secondary accent
- AUTO materials; avoid vertical spire ornament

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| deco_lobby_facade | BAROQUE_FACADE | Horizontal frontispiece (replaces tessellation tower) |
| deco_panel_wall | GB_BRUTALIST_PANEL_WALL | Geometric lobby band |
| chevron_filigree | FILIGREE_PANEL | Geometric screen |
| cusped_portal | CUSPED_ARCH | Ceremonial gate |
| lobby_balcony | BALCONY | Promenade overlook |
| approach_ramp | GREYBOX_RAMP | Public incline (replaces obelisk) |

## OS hooks

- Genome: `art_deco_lobby_v1`
- Grammar graph: `ART_DECO`
- Compose style: `ART_DECO`
