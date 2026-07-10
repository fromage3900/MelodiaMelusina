# Study: Mesoamerican Pyramid Courtyard

**Style:** mesoamerican  
**Version:** 0.1  
**Sources:** Teotihuacan Ciudadela / Avenue of the Dead; Maya plaza–pyramid compounds; Mixtec/Zapotec platform courts

## Motifs

- Stepped battered retaining tiers (talud) framing a ceremonial court
- Broad frontal stair block as the primary ascent — not a tower spine
- Processional ramp / side approach linking terrace levels
- Stone colonnade / arcade along the court edge
- Round portal threshold into the sacred precinct
- Central pool / fountain as the sacred terminus (cenote / plaza basin analogue)

## Proportions

- Horizontal civic chain dominates: wall → stair → ramp → arcade → gate → pool
- Verticality expressed as stacked retaining batters, not free-standing towers
- Stair width ≈ 2.0–2.4 m; arcade bay ≈ 3.2 m; pool radius ≈ 1.5 m

## Rhythms

- Retaining step count (3–5) sets terrace cadence
- Stair rise/run (0.22 / 0.32) keeps ceremonial climb readable
- Arcade repeats as the court colonnade rhythm

## Structural rules

- No tower / obelisk / keep kits in the grammar graph or hero preset
- Corner “tower” compose role maps to a pillar (vertical accent without spine)
- Monument role = stair block; sacred role = public fountain / pool
- Prefer stone material + RECESS trim for greybox readability

## Ornament systems

- Batter angle on retaining walls (0.08–0.10)
- Round arch portal as the only ornamental gate type in v1
- Pool tiers (2) as the sacred ornament focus

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| `retaining_terrace` | `RETAINING_WALL` | Stepped battered platform mass |
| `ceremonial_stair` | `GREYBOX_STAIR_BLOCK` | Frontal ascent |
| `processional_ramp` | `GREYBOX_RAMP` | Side / upper approach |
| `court_colonnade` | `GB_ROMANESQUE_ARCADE` | Court-edge arcade |
| `stone_portal` | `ARCHWAY_ADV` | Round threshold |
| `sacred_pool` | `PUBLIC_FOUNTAIN` | Plaza basin terminus |

## OS hooks

- Genome: `meso_pyramid_courtyard_v1`
- Grammar graph: `MESOAMERICAN_PYRAMID`
- Compose style: `MESOAMERICAN_PYRAMID`
- Surreal transform: `axis_compression`
