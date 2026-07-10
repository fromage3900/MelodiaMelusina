# Study: Beaux-Arts Civic Plaza

**Style:** beaux_arts  
**Version:** 0.1  
**Sources:** École des Beaux-Arts civic typology; Grand Central / NYPL plaza sequences; City Beautiful movement plans

## Motifs

- Temple-front civic facade with pilaster bay rhythm
- Broad ceremonial stair and inclined approach ramp
- Colonnade / arcade framing the court
- Roman triumphal portal as gate threshold
- Balustraded terrace edge
- Central fountain basin as plaza monument

## Proportions

- Facade height ~12–16 m; odd bay counts (5–7)
- Stair rise ~0.18–0.22 m; run ~0.30–0.34 m; width ≥2.4 m
- Ramp length ≥ stair run chain; gentle civic grade
- Arcade bay width ~3.2–3.6 m; height ~4.0–4.8 m
- Fountain radius ~1.4–1.8 m; 2–3 tiers

## Rhythms

- Horizontal civic chain: facade → stair → ramp → arcade → portal → balustrade → fountain
- No vertical tower spine — plaza reads as a court, not a campanile
- Corner markers are fluted pillars, not bell towers

## Structural rules

- Prefer `axis_compression` over `vertical_stretch` (horizontal civic emphasis)
- `corner_tower` compose role maps to `PILLAR` (tower ban)
- Archway style must be `ROMAN` (not `ROUND`)
- Banned arch types: TOWER, TESSELLATION_TOWER, BELL_TOWER, WATCHTOWER, OBELISK, KEEP

## Ornament systems

- Corinthian / Ionic order on facade
- Recess trim on arcade and greybox modules
- Marble / stone material defaults for civic permanence

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| civic_facade | BAROQUE_FACADE | Temple-front hero bay |
| ceremonial_stair | GREYBOX_STAIR_BLOCK | Broad public stair |
| approach_ramp | GREYBOX_RAMP | Inclined civic approach |
| plaza_colonnade | GB_ROMANESQUE_ARCADE | Round-arch colonnade |
| triumphal_portal | ARCHWAY_ADV (ROMAN) | Gate threshold |
| terrace_rail | BAROQUE_BALUSTRADE | Court edge |
| plaza_fountain | PUBLIC_FOUNTAIN | Monument basin |
| corner_pillar | PILLAR | Non-tower corner marker |

## OS hooks

- Genome: `beaux_arts_plaza_v1`
- Grammar graph: `BEAUX_ARTS_PLAZA`
- Compose style: `BEAUX_ARTS_PLAZA`
