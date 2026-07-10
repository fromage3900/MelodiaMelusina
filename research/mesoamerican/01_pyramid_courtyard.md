# Study: Mesoamerican Pyramid Courtyard

**Style:** mesoamerican  
**Version:** 0.1  
**Sources:** Teotihuacan Avenue of the Dead plaza typology; Maya ceremonial plaza + talud-tablero terrace grammar; Tenochtitlan sacred precinct processional stairs

## Motifs

- Stepped battered retaining terraces (talud) framing a horizontal plaza
- Broad ceremonial stair block as the primary ascent — not a tower spine
- Processional ramp / secondary terrace for lateral approach
- Stone colonnade framing the court edge
- Roman-semicircle stone portal as court threshold
- Sacred pool / fountain as plaza terminus (cenote / ritual basin stand-in)

## Proportions

- Terrace batter ~0.08–0.12; wall thickness 0.55–0.65
- Stair rise ~0.22, run ~0.32, width ≥2.4 (processional)
- Colonnade bay ~3.2 wide × 4.0 high
- Portal opening ~2.4 × 2.6 with shallow depth

## Rhythms

- Horizontal civic chain: terrace → stair → ramp/terrace → colonnade → portal → pool
- Symmetry high; verticality expressed as stacked terraces, not free-standing towers
- Ornament density moderate — stone massing over filigree

## Structural rules

- No tower spines (TOWER / TESSELLATION_TOWER / BELL_TOWER / WATCHTOWER / OBELISK / KEEP banned)
- Corner markers resolve to pillars / colonnade posts
- Sacred role is the court pool, not a vertical monument
- Gate role is ARCHWAY_ADV (ROMAN), not a keep/gatehouse tower

## Ornament systems

- Battered stone courses + recess trim on arcade
- Keystoned Roman portal band
- Tiered basin as ritual water terminus

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| `meso_terrace_wall` | RETAINING_WALL | Stepped battered plaza terrace |
| `meso_ceremonial_stair` | GREYBOX_STAIR_BLOCK | Broad processional stair |
| `meso_processional_ramp` | GREYBOX_RAMP | Lateral / secondary ascent |
| `meso_court_colonnade` | GB_ROMANESQUE_ARCADE | Court-edge arcade |
| `meso_stone_portal` | ARCHWAY_ADV | ROMAN threshold |
| `meso_sacred_pool` | PUBLIC_FOUNTAIN | Ritual basin terminus |

## OS hooks

- Genome: `meso_pyramid_courtyard_v1`
- Grammar graph: `MESOAMERICAN_PYRAMID`
- Compose style: `MESOAMERICAN_PYRAMID`
- Transform: `axis_compression`
