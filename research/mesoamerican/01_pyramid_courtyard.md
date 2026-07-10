# Study: Mesoamerican Pyramid Courtyard

**Style:** mesoamerican  
**Version:** 0.1  
**Sources:** Teotihuacan Street of the Dead plaza grammar; Maya ceremonial court / talud-tablero terraces; Mixtec processional ramps

## Motifs

- Talud (battered retaining face) + tablero (panel band) terrace stacks
- Broad ceremonial stair blocks centered on plaza axes
- Processional ramps flanking or replacing steep stairs for civic approach
- Stone colonnade framing the court
- Round-headed portal into the sacred precinct
- Reflecting / ritual pool as court terminus (not a vertical spine)

## Proportions

- Terrace batter ~0.08–0.12; wall thickness ~0.55–0.65 m
- Stair rise/run ~0.22 / 0.32; width ≥ 2.4 m for processional massing
- Arcade bay ~3.2 m; portal clear ~2.4 × 2.6 m
- Horizontal civic chain preferred over tower / keep / obelisk spines

## Rhythms

1. Lower retaining terrace
2. Ceremonial stair ascent
3. Upper platform retaining band
4. Colonnade walk
5. Stone portal threshold
6. Sacred pool terminus

## Structural rules

- No TOWER / TESSELLATION_TOWER / BELL_TOWER / WATCHTOWER / OBELISK / KEEP in the graph
- Corner markers resolve to pillars / stelae-scale posts, not towers
- Compose style stamps `meso_pyramid_courtyard_v1` with `axis_compression`

## Ornament systems

- Stone material default; recess trim on arcade
- Portal uses `ARCHWAY_ADV` with `ROMAN` (not invalid `ROUND`)

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| `talud_terrace` | `RETAINING_WALL` | Battered stepped terrace |
| `ceremonial_stair` | `GREYBOX_STAIR_BLOCK` | Processional stair mass |
| `court_colonnade` | `GB_ROMANESQUE_ARCADE` | Court arcade stand-in |
| `stone_portal` | `ARCHWAY_ADV` | Precinct gate |
| `ritual_pool` | `PUBLIC_FOUNTAIN` | Sacred terminus |

## OS hooks

- Genome: `meso_pyramid_courtyard_v1`
- Grammar graph: `MESOAMERICAN_PYRAMID`
- Compose style: `MESOAMERICAN_PYRAMID`
