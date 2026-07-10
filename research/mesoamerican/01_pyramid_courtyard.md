# Study: Mesoamerican Pyramid Courtyard

**Style:** mesoamerican  
**Version:** 0.1  
**Sources:** Teotihuacan Ciudadela / Temple of Quetzalcoatl plaza; Maya plaza–stair–platform compounds; Mixtec/Zapotec terrace courts

## Motifs

- Stepped battered retaining tiers (talud) framing a sunken or raised court
- Broad ceremonial stair block as the primary vertical gesture (not a tower spine)
- Upper platform / terrace as the sacred landing
- Stone colonnade or arcade along the court edge
- Round-arch or corbel-adjacent stone portal into the precinct
- Sacred pool / basin as court terminus (cenote / ritual water echo)

## Proportions

- Stair run dominates height: many shallow risers, wide tread (processional, not defensive)
- Retaining batter ~0.08–0.12; wall thickness heavy relative to height
- Court width ≥ 3× stair width; arcade bay ≈ human scale under massive platforms
- Verticality expressed as stacked horizontal terraces, not free-standing towers

## Rhythms

- Approach: lower retaining → stair ascent → upper retaining / platform → arcade → portal → pool
- Horizontal civic chain: terrace → colonnade → gate → water
- Symmetry high along the stair axis; ornament density moderate (stone relief, not filigree)

## Structural rules

- No tower / keep / obelisk spines — banned for this family
- Corner massing uses pillars or battered pier stubs, never watchtowers
- Compose roles map `monument` → ceremonial stair, `sacred` → pool, `gate` → stone portal
- Prefer `axis_compression` so terrace stacks read as compressed sacred topography

## Ornament systems

- Stone material default; recess trim on arcade bays
- Batter and step count carry the style more than applied ornament
- Portal: ROUND archway as greybox stand-in for corbelled / trapezoidal openings

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| `talud_retaining_tier` | `RETAINING_WALL` | Battered stepped terrace seam |
| `ceremonial_stair_block` | `GREYBOX_STAIR_BLOCK` | Processional ascent + landing |
| `court_colonnade_bay` | `GB_ROMANESQUE_ARCADE` | Court-edge arcade stand-in |
| `precinct_stone_portal` | `ARCHWAY_ADV` | Round stone gate into precinct |
| `sacred_court_pool` | `PUBLIC_FOUNTAIN` | Ritual basin / pool terminus |

## OS hooks

- Genome: `meso_pyramid_courtyard_v1`
- Grammar graph: `MESOAMERICAN_PYRAMID`
- Compose style: `MESOAMERICAN_PYRAMID`
