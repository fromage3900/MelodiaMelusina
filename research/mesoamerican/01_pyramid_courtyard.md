# Study: Mesoamerican Pyramid Courtyard

**Style:** mesoamerican  
**Version:** 1.0  
**Sources:** Teotihuacan Avenue of the Dead plaza typology; Maya ceremonial court; Aztec temple platform terraces (horizontal civic reading — no tower spine)

## Motifs

- Stepped battered retaining tiers framing a ceremonial court
- Broad stair block as the primary ascent (not a keep/obelisk)
- Processional ramp linking terrace levels
- Stone colonnade / arcade along the court edge
- Round portal into the sacred precinct
- Central sacred pool / fountain as court terminus

## Proportions

- Retaining batter ~0.08–0.10; wall thickness 0.55–0.65 m
- Ceremonial stair: 12 steps × rise 0.22 / run 0.32; width ~2.4 m
- Arcade bay ~3.2 m wide × 4.0 m high
- Portal clear opening ~2.4 × 2.6 m
- Sacred pool radius ~1.5 m, two tiers

## Rhythms

- Horizontal civic chain: retaining → stair → ramp → arcade → portal → pool
- Terrace modules read as layered platforms, not vertical spines
- Colonnade cadence marks the court perimeter before the gate

## Structural rules

- Banned arch types for this family: TOWER, TESSELLATION_TOWER, BELL_TOWER, WATCHTOWER, OBELISK, KEEP
- Compose `corner_tower` role remaps to `_lib_PILLAR` (column marker, not a tower kit)
- Compose `monument` → stair block; `sacred` → public fountain / pool
- Grammar graph `MESOAMERICAN_PYRAMID` is the sole spine for `meso_pyramid_courtyard_v1`

## Ornament systems

- Stone batter faces with recessed trim (`gb_trim_mode: RECESS`)
- Arcade recess panels as colonnade rhythm
- Portal round arch as ceremonial threshold

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| `retaining_terrace` | RETAINING_WALL | battered platform seam |
| `ceremonial_stair` | GREYBOX_STAIR_BLOCK | primary ascent |
| `processional_ramp` | GREYBOX_RAMP | terrace connector |
| `court_colonnade` | GB_ROMANESQUE_ARCADE | court edge arcade |
| `stone_portal` | ARCHWAY_ADV | ROUND style gate |
| `sacred_pool` | PUBLIC_FOUNTAIN | court terminus |

## OS hooks

- Genome: `meso_pyramid_courtyard_v1`
- Grammar graph: `MESOAMERICAN_PYRAMID`
- Compose style: `MESOAMERICAN_PYRAMID`
- Surreal transform: `axis_compression`
