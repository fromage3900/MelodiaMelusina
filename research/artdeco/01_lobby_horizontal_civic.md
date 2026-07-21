# Study: Art Deco Lobby — Horizontal Civic Rematerialize

**Style:** artdeco  
**Version:** 1.0  
**Sources:** 1920s American setback lobbies, Rockefeller Center plazas, civic Deco promenades (not tower spines)

## Motifs

- Stepped facade bays and sunburst geometry at pedestrian scale
- Chevron / geometric filigree screens along lobby walls
- Processional stair and ramp pairs into a court fountain
- Colonnade / arcade rhythm instead of vertical tessellation spines
- Cusped or rounded portal thresholds (no obelisk terminus)

## Proportions

- Facade bay width ≈ 2–3× human height; lobby walk length dominates height
- Stair run:rise ≈ 0.32:0.22; ramp length ≥ stair footprint
- Colonnade spacing ≈ 3–3.5 m bay centers
- Fountain as sacred court terminus, not monument spire

## Rhythms

- Facade → stair → panel wall → filigree → colonnade → portal → ramp → fountain
- Horizontal civic chain; density peaks at filigree + portal, not at a tower crown

## Structural rules

- **Banned** as grammar or hero modules: TOWER, TESSELLATION_TOWER, BELL_TOWER, WATCHTOWER, OBELISK, KEEP
- `corner_tower` compose role maps to **PILLAR** (vertical accent without spine typology)
- Prefer `axis_compression` over `vertical_stretch` for lobby walks

## Ornament systems

- Geometric arabesque filigree (chevron / lattice)
- Recessed trim on panel walls (`gb_trim_mode: RECESS`)
- Cusped portal as gate role

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| deco_facade_bay | BAROQUE_FACADE | Civic stepped frontispiece stand-in |
| deco_stair_procession | GREYBOX_STAIR_BLOCK | Lobby stair block |
| deco_panel_wall | GB_BRUTALIST_PANEL_WALL | Geometric panel field |
| deco_filigree | FILIGREE_PANEL | Chevron / geometric screen |
| deco_colonnade | GB_ROMANESQUE_ARCADE | Pedestrian colonnade |
| deco_portal | CUSPED_ARCH | Lobby gate |
| deco_ramp | GREYBOX_RAMP | Accessibility / processional ramp |
| deco_fountain | PUBLIC_FOUNTAIN | Court terminus |

## OS hooks

- Genome: `art_deco_lobby_v1`
- Grammar graph: `ART_DECO`
- Compose style: `ART_DECO`
