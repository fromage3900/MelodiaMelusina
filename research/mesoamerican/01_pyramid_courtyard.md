# Study: Mesoamerican Pyramid Courtyard

**Style:** mesoamerican  
**Version:** 0.1  
**Sources:** Teotihuacan Avenue of the Dead processional grammar; Maya plaza–temple courts; Aztec ceremonial platforms (talud-tablero massing)

## Motifs

- Stepped battered retaining terraces (talud) forming horizontal civic platforms
- Broad ceremonial stair blocks and processional ramps — ascent as sequence, not a tower spine
- Colonnade / arcade bays framing the upper court
- Stone portal thresholds into sacred precincts
- Cenote / sacred pool as court terminus (not an obelisk or keep)

## Proportions

- Terrace batter ~0.08–0.12; wall thickness heavy relative to height
- Stair rise ~0.20–0.24 m, run ~0.30–0.34 m — monumental but walkable
- Arcade bay width ~3.0–3.4 m; portal clear height ~2.4–2.8 m
- Court pool radius ~1.4–1.8 m as contemplative terminus

## Rhythms

1. Lower retaining terrace (mass / batter)
2. Processional ramp approach
3. Ceremonial stair block to upper platform
4. Colonnade court bay
5. Stone portal threshold
6. Sacred pool terminus

## Structural rules

- **No tower spines** — banned TOWER / TESSELLATION_TOWER / BELL_TOWER / WATCHTOWER / OBELISK / KEEP
- Prefer horizontal civic chains: facades, courts, arcades, stairs, ramps, colonnades
- Corner markers use pillars / stelae-scale posts, never watchtowers
- Sacred role resolves to the court pool (cenote metaphor), not a vertical monument

## Ornament systems

- Stone material default; recess trim for arcade / portal edges
- Batter and step count carry the “pyramid” reading — massing, not a free-standing spire

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| `meso_retaining_terrace` | `RETAINING_WALL` | Battered stepped terrace |
| `meso_processional_ramp` | `GREYBOX_RAMP` | Inclined approach |
| `meso_ceremonial_stair` | `GREYBOX_STAIR_BLOCK` | Monumental stair + landing |
| `meso_court_colonnade` | `GB_ROMANESQUE_ARCADE` | Court arcade bay |
| `meso_stone_portal` | `ARCHWAY_ADV` | Round stone threshold |
| `meso_sacred_pool` | `PUBLIC_FOUNTAIN` | Cenote / court pool |

## OS hooks

- Genome: `meso_pyramid_courtyard_v1`
- Grammar graph: `MESOAMERICAN_PYRAMID`
- Compose style: `MESOAMERICAN_PYRAMID`
- Transform: `axis_compression`
