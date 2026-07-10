# Study: Art Deco Lobby Promenade (tower-ban)

**Style:** art_deco  
**Version:** 0.2  
**Sources:** 1920s–30s civic lobby / setback facade typology (horizontal promenade, not skyscraper spine)

## Motifs

- Stepped setback street facade (horizontal massing, not tower extrusion)
- Ceremonial lobby stair + processional ramp
- Chevron / geometric filigree screens
- Cusped portal thresholds into a fountain court
- Fluted pillar colonnade markers at corners (not bell towers / obelisks)

## Proportions

- Facade bays 3–5; height ~10–14 m civic scale
- Stair rise ~0.22 m, run ~0.32 m; ramp length ≥ stair run chain
- Filigree panels ~1.4–1.8 m as secondary ornament, not primary mass

## Rhythms

- Facade → stair → panel wall → filigree → portal → ramp/court
- Horizontal civic chain; density falls toward the court terminus

## Structural rules

- **No tower spines** — ban TESSELLATION_TOWER, OBELISK, BELL_TOWER, WATCHTOWER, KEEP
- Corner markers use PILLAR; monument / sacred use PUBLIC_FOUNTAIN
- Prefer facades, stairs, ramps, colonnades, courts

## Ornament systems

- Geometric arabesque filigree (chevron density)
- Recessed panel trim on brutalist-adjacent deco walls
- Cusped arch as gate role

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| deco_setback_facade | BAROQUE_FACADE | Civic setback street wall |
| deco_lobby_stair | GREYBOX_STAIR_BLOCK | Processional stair |
| deco_panel_wall | GB_BRUTALIST_PANEL_WALL | Geometric panel rhythm |
| deco_chevron_screen | FILIGREE_PANEL | GEOMETRIC_ARABESQUE |
| deco_cusped_portal | CUSPED_ARCH | Gate role |
| deco_processional_ramp | GREYBOX_RAMP | Court approach |
| deco_corner_pillar | PILLAR | corner_tower compose role |
| deco_court_fountain | PUBLIC_FOUNTAIN | monument / sacred |

## OS hooks

- Genome: `art_deco_lobby_v1`
- Grammar graph: `ART_DECO`
- Compose style: `ART_DECO`
- Transform: `axis_compression`
