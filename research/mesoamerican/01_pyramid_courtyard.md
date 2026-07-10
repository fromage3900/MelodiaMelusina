# Study: Mesoamerican Pyramid Courtyard

**Style:** mesoamerican  
**Version:** 0.1  
**Sources:** Teotihuacan Ciudadela / Avenue of the Dead; Maya plaza–pyramid compounds; Aztec ceremonial courts

## Motifs

- Stepped battered retaining tiers (talud) framing a horizontal plaza
- Broad ceremonial stair block as the primary ascent — not a tower spine
- Colonnade / arcade bays along the court edge
- Stone portal threshold into the sacred precinct
- Central sacred pool / fountain as the court terminus

## Proportions

- Horizontal civic chain dominates: wall → stair → platform → arcade → gate → pool
- Stair rise ~0.22 m, run ~0.32 m (processional, not defensive)
- Retaining batter 0.08–0.10 for talud silhouette
- Arcade bay width ~3.2 m, height ~4.0 m

## Rhythms

- Alternating retaining mass and open court
- Stair as the only strong vertical accent; mass stays low and wide
- Colonnade repeats as a horizontal beat along the plaza edge

## Structural rules

- No tower / obelisk / keep spines — banned for this family
- Prefer facades, courts, arcades, stairs, ramps, colonnades
- Corner role maps to pillar (plaza marker), not a tower kit
- Sacred role is the pool, not a vertical monument

## Ornament systems

- Stone material default; recess trim on arcade
- Round arch portal (not horseshoe / ogee)
- Minimal cosmic ornament — structural logic over filigree

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| meso_retaining_tier | RETAINING_WALL | Talud stepped batter |
| meso_ceremonial_stair | GREYBOX_STAIR_BLOCK | Processional ascent |
| meso_plaza_arcade | GB_ROMANESQUE_ARCADE | Court colonnade |
| meso_stone_portal | ARCHWAY_ADV | Round threshold |
| meso_sacred_pool | PUBLIC_FOUNTAIN | Court terminus |

## OS hooks

- Genome: `meso_pyramid_courtyard_v1`
- Grammar graph: `MESOAMERICAN_PYRAMID`
- Compose style: `MESOAMERICAN_PYRAMID`
- Transform: `axis_compression`
