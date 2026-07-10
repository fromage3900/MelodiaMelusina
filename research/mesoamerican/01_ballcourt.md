# Study: Mesoamerican Ballcourt (I-shaped)

**Style:** mesoamerican  
**Version:** 0.1  
**Sources:** Maya / Central Mexican tlachtli (pok-ta-pok) courts; Copán, Chichén Itzá Great Ball Court; I-plan alley typology

## Motifs

- Long playing alley framed by battered side berms (talud)
- Sloping playing walls / ramps along the alley flanks
- I-shaped end zones with raised terraces and lintel portals
- Spectator colonnade / arcade gallery parallel to the alley
- Center-line stone markers (pillars), never tower spines

## Proportions

- Alley length >> width (strong horizontal civic axis)
- End-zone terraces wider than the alley (I-plan terminals)
- Ramp rise shallow (≈2–2.5 m) relative to alley length
- Portal clear ≈2.4 m wide, lintel head

## Rhythms

- Approach: lintel portal → retaining berm → sloping ramp wall → corridor alley → end stair terrace → spectator arcade
- Alternate berm and ramp so the graph reads as a processional I-court, not a vertical monument

## Structural rules

- No tower / obelisk / keep / watchtower spines
- Corner markers are pillars (center-ring stand-ins)
- Sacred role is the end-zone stair terrace; monument is the center pillar marker
- Gate is a stone lintel portal into the alley

## Ornament systems

- Stone material default; recess trim on arcade bays
- Structural batter and ramp slope carry the style signal

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| alley_portal | ARCHWAY_ADV (LINTEL) | End-zone entry |
| alley_berm | RETAINING_WALL | Talud side wall |
| playing_ramp | GREYBOX_RAMP | Sloping flank |
| alley_spine | GREYBOX_CORRIDOR | Long court floor/spine |
| end_terrace | GREYBOX_STAIR_BLOCK | I-plan terminal |
| spectator_arcade | GB_ROMANESQUE_ARCADE | Gallery |

## OS hooks

- Genome: `meso_ballcourt_v1`
- Grammar graph: `MESOAMERICAN_BALLCOURT`
- Compose style: `MESOAMERICAN_BALLCOURT`
