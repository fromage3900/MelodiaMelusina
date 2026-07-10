# Study: Mesoamerican Pyramid Courtyard

**Style:** mesoamerican  
**Version:** 0.1  
**Sources:** Teotihuacan Avenue of the Dead processional courts; Maya plaza–pyramid compounds; Aztec ceremonial precinct plans

## Motifs

- Stepped battered retaining terraces (talud) framing a horizontal court
- Broad ceremonial stair block as the primary ascent — not a tower spine
- Upper platform terrace as a shallow stage, not a keep
- Stone colonnade / arcade bays along the court edge
- Low stone portal (lintel/roman arch) as processional gate
- Sacred pool / fountain as the court terminus

## Proportions

- Horizontal civic chain preferred over vertical monument spines
- Stair run wider than tall; retaining batter ~0.08–0.12
- Arcade bay height ~4 m; portal clear ~2.4 × 2.6 m
- Court depth reads as a sequence of terraces, not a single tower mass

## Rhythms

- Retain → stair → retain → colonnade → portal → pool
- Alternating solid terrace and open bay creates processional pulse
- Axis compression keeps the chain civic-horizontal under genome verticality

## Structural rules

- No tower / obelisk / keep / watchtower modules in the grammar graph
- Corner markers resolve to pillars, not corner towers
- Retaining walls carry terrain seams; stairs carry ascent
- Gate is ARCHWAY_ADV (ROMAN), not a gatehouse keep

## Ornament systems

- Stone material default; recess trim on arcade bays
- Minimal cosmic ornament — structural batter and stair rhythm carry the style

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| meso_retaining_terrace | RETAINING_WALL | Stepped battered court edge |
| meso_ceremonial_stair | GREYBOX_STAIR_BLOCK | Broad processional ascent |
| meso_colonnade_bay | GB_ROMANESQUE_ARCADE | Court-edge arcade |
| meso_stone_portal | ARCHWAY_ADV | ROMAN processional gate |
| meso_sacred_pool | PUBLIC_FOUNTAIN | Court terminus basin |

## OS hooks

- Genome: `meso_pyramid_courtyard_v1`
- Grammar graph: `MESOAMERICAN_PYRAMID`
- Compose style: `MESOAMERICAN_PYRAMID`
