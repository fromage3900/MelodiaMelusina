# Study: Egyptian Temple Court (Processional)

**Style:** egyptian  
**Version:** 0.1  
**Sources:** Karnak / Luxor processional courts; pylons as gate masses (not tower spines); hypostyle halls; sacred lake typology

## Motifs

- Twin battered pylon masses framing a lintel gateway
- Processional stair and ramp into the open court
- Dense hypostyle column hall before the sanctuary
- Peristyle arcade around the court
- Sacred lake / reflecting pool as terminus

## Proportions

- Horizontal civic chain — width dominates height
- Pylon batter ~8–12% on retaining flanks
- Hypostyle bay spacing ~3.5–4.5 m; column height ~4 m
- Court arcade bay ~3.2 m wide

## Rhythms

- Gate → stair → hypostyle → arcade → ramp → sacred lake
- Alternating solid mass (pylon / retaining) and void (court / lake)

## Structural rules

- No tower spines, obelisks, or keep masses in the grammar graph
- Corner markers resolve to freestanding pillars (tower-ban)
- Lintel portal preferred over arched Roman forms for the gate

## Ornament systems

- Stone trim recess on arcade and panel walls
- Fluted pillars as hypostyle stand-ins
- Low ornament density relative to Baroque / Beaux-Arts

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| pylon_flank | RETAINING_WALL / GB_BRUTALIST_PANEL_WALL | Battered mass |
| pylon_gate | ARCHWAY_ADV (LINTEL) | Processional portal |
| processional_stair | GREYBOX_STAIR_BLOCK | Court approach |
| hypostyle | GREYBOX_PILLAR_HALL | Column forest |
| peristyle | GB_ROMANESQUE_ARCADE | Court arcade |
| processional_ramp | GREYBOX_RAMP | Sanctuary approach |
| sacred_lake | PUBLIC_FOUNTAIN | Reflecting pool |

## OS hooks

- Genome: `egyptian_temple_court_v1`
- Grammar graph: `EGYPTIAN_TEMPLE_COURT`
- Compose style: `EGYPTIAN_TEMPLE_COURT`
