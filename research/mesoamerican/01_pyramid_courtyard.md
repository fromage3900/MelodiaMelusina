# Study: Mesoamerican Pyramid Courtyard

**Style:** mesoamerican  
**Version:** 0.1  
**Sources:** Teotihuacan Ciudadela / Temple of Quetzalcoatl plaza; Maya ceremonial courts; talud-tablero platform grammar

## Motifs

- Stepped battered retaining tiers (talud) framing a sunken or raised court
- Broad ceremonial stair block on the primary axis
- Processional ramp legs flanking the stair for horizontal civic flow
- Stone colonnade / arcade gallery along the court edge
- Lintel or round-arch portal into the sacred precinct
- Central ritual pool / fountain terminus (no tower spine)

## Proportions

- Court width >> platform height (horizontal civic emphasis)
- Stair run ≈ 0.3 m, rise ≈ 0.22 m — shallow ceremonial climb
- Retaining batter 0.08–0.12 for talud silhouette
- Arcade bay ≈ 3.2 m clear

## Rhythms

- Approach: retaining berm → stair → upper terrace → arcade → portal → pool
- Alternate stair and ramp so the graph reads as a processional chain, not a vertical monument

## Structural rules

- No tower / obelisk / keep spines — verticality expressed only as stepped platforms
- Corner markers are pillars, not watchtowers
- Sacred role is the stair block (ascent), monument is the pool

## Ornament systems

- Stone material default; recess trim on arcade bays
- Minimal cosmic ornament — structural batter carries the style signal

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| talud_retaining | RETAINING_WALL | Battered stepped berm |
| ceremonial_stair | GREYBOX_STAIR_BLOCK | Primary axis ascent |
| processional_ramp | GREYBOX_RAMP | Horizontal civic approach |
| court_arcade | GB_ROMANESQUE_ARCADE | Gallery along court |
| precinct_portal | ARCHWAY_ADV | Stone gate (ROMAN) |
| ritual_pool | PUBLIC_FOUNTAIN | Court terminus |

## OS hooks

- Genome: `meso_pyramid_courtyard_v1`
- Grammar graph: `MESOAMERICAN_PYRAMID`
- Compose style: `MESOAMERICAN_PYRAMID`
