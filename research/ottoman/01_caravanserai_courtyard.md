# Study: Ottoman Caravanserai (Han) Courtyard

**Style:** ottoman  
**Version:** 0.1  
**Sources:** Seljuk/Ottoman han typology; Sultan Han; Rüstem Pasha Caravanserai; courtyard riwaq grammar

## Motifs

- Monumental entry facade with deep iwan portal
- Horseshoe / pointed arch gate as threshold
- Arabesque screen panels along the court edge
- Continuous riwaq arcade wrapping the sahn
- Stable / service corridor bays behind the arcade
- Processional ramp or stair to upper gallery
- Central courtyard fountain as terminus

## Proportions

- Horizontal civic chain — low verticality, strong axial approach
- Arcade bay width ~3.2–3.6 m; portal clear ~2.6–2.8 m
- Courtyard depth dominates over height (axis compression friendly)

## Rhythms

- Facade → iwan → arabesque → arcade → corridor → ramp → fountain
- Alternating solid screen / open arcade along the court perimeter
- No tower spines; corners resolve as freestanding pillars

## Structural rules

- Prefer facades, courts, arcades, stairs/ramps, colonnades
- Banned: TOWER, TESSELLATION_TOWER, BELL_TOWER, WATCHTOWER, OBELISK, KEEP
- Compose `corner_tower` maps to `_lib_PILLAR`

## Ornament systems

- Geometric arabesque filigree on screens
- Stone trim recess on arcade and corridor greybox modules
- Horseshoe archway style for the iwan gate

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| han_facade | BAROQUE_FACADE | Entry frontispiece |
| iwan_portal | ARCHWAY_ADV (HORSESHOE) | Deep threshold |
| arabesque_screen | FILIGREE_PANEL | Court edge ornament |
| riwaq_arcade | GB_ROMANESQUE_ARCADE | Wrapped colonnade |
| stable_bay | GREYBOX_CORRIDOR | Service / lodging bay |
| gallery_ramp | GREYBOX_RAMP | Upper gallery access |
| sahn_fountain | PUBLIC_FOUNTAIN | Courtyard terminus |

## OS hooks

- Genome: `ottoman_caravanserai_v1`
- Grammar graph: `OTTOMAN_CARAVANSERAI`
- Compose style: `OTTOMAN_CARAVANSERAI`
- Transform: `axis_compression`
