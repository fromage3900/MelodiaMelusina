# Study: Art Deco Lobby Plaza (Horizontal Civic)

**Style:** artdeco  
**Version:** 1.0  
**Sources:** Chrysler / Empire setback massing (horizontal reading), Rockefeller plaza courts, Miami Beach Streamline lobby sequences, Deco cinema foyers

## Motifs

- Stepped **setback facade** read as a civic frontage, not a tower spine
- Geometric **panel wall** rhythm and chevron / sunburst filigree screens
- Processional **lobby stair** + accessible **ramp** chain into a colonnade hall
- Cusped / ornamental portal as gate; court fountain as terminus

## Proportions

- Facade bays 5–7; height kept mid-rise (horizontal plaza scale)
- Stair rise ~0.18–0.22 m; ramp length longer than rise (gentle procession)
- Colonnade grid 3×2 or 4×2 with 3.5–4.0 m spacing

## Rhythms

1. Facade frontage → 2. Lobby stair → 3. Geometric panel wall → 4. Chevron filigree  
5. Pillar-hall colonnade → 6. Cusped portal → 7. Processional ramp → 8. Court fountain

## Structural rules

- **No tower spines** — ban `TOWER`, `TESSELLATION_TOWER`, `BELL_TOWER`, `WATCHTOWER`, `OBELISK`, `KEEP`
- Compose `corner_tower` maps to `_lib_PILLAR` (pilaster accent, not vertical monument)
- Prefer facades, courts, arcades, stairs, ramps, colonnades

## Ornament systems

- Geometric arabesque filigree (chevron / zig-zag)
- Recessed trim on panel walls
- Cusped portal as Deco gate cue

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| deco_setback_facade | BAROQUE_FACADE | Civic frontage stand-in |
| deco_lobby_stair | GREYBOX_STAIR_BLOCK | Processional stair |
| deco_panel_wall | GB_BRUTALIST_PANEL_WALL | Geometric cladding |
| deco_chevron_screen | FILIGREE_PANEL | GEOMETRIC_ARABESQUE |
| deco_colonnade | GREYBOX_PILLAR_HALL | Lobby hypostyle |
| deco_portal | CUSPED_ARCH | Gate |
| deco_ramp | GREYBOX_RAMP | Horizontal procession |
| deco_court_fountain | PUBLIC_FOUNTAIN | Monument / sacred court |

## OS hooks

- Genome: `art_deco_lobby_v1`
- Grammar graph: `ART_DECO`
- Compose style: `ART_DECO`
- Transform: `axis_compression` (horizontal civic)
