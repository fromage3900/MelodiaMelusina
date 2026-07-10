# Study: Mesoamerican pyramid courtyard

**Style:** mesoamerican  
**Version:** 1.0  
**Sources:** Teotihuacan Ciudadela / Avenue of the Dead plaza typology; Maya ceremonial court with talud-tablero terraces; Aztec temple precinct stairs (horizontal civic chain — no tower spines)

## Motifs

- Stepped battered retaining terraces framing a ceremonial court
- Broad stair block as the primary vertical gesture (ascent, not a tower)
- Colonnade / arcade bay along the court edge
- Stone portal threshold into the precinct
- Sacred pool / fountain as court terminus

## Proportions

- Retaining terrace modules ~1.2 m unit; 3–5 batter steps, batter 0.08–0.10
- Ceremonial stair: 12 steps × 0.22 m rise × 0.32 m run; width ~2.4 m
- Arcade bay ~3.2 m wide × 4.0 m high
- Portal clear opening ~2.4 × 2.6 m; fountain radius ~1.5 m

## Rhythms

- Terrace → stair → terrace → arcade → portal → pool (horizontal civic chain)
- Stair sits between terrace bands as the only strong vertical accent
- Arcade colonnade softens the court edge before the portal

## Structural rules

- Prefer `RETAINING_WALL`, `GREYBOX_STAIR_BLOCK`, arcade, archway, fountain — **no** TOWER / OBELISK / KEEP spines
- Graph `MESOAMERICAN_PYRAMID` externalized in OS grammar
- Compose `corner_tower` maps to `_lib_PILLAR` (not a tower kit); `monument` → stair; `sacred` → pool

## Ornament systems

- Stone batter faces + recess trim on arcade
- Round arch portal as precinct gate
- Two-tier fountain as sacred water terminus

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| `meso_terrace_batter` | `RETAINING_WALL` | Stepped battered terrace band |
| `meso_ceremonial_stair` | `GREYBOX_STAIR_BLOCK` | Broad ascent block |
| `meso_court_arcade` | `GB_ROMANESQUE_ARCADE` | Court-edge colonnade |
| `meso_stone_portal` | `ARCHWAY_ADV` | Precinct threshold |
| `meso_sacred_pool` | `PUBLIC_FOUNTAIN` | Court terminus water |

## OS hooks

- Genome: `meso_pyramid_courtyard_v1`
- Grammar graph: `MESOAMERICAN_PYRAMID`
- Compose style: `MESOAMERICAN_PYRAMID`
- Surreal transform: `axis_compression`
