# Study: Greek Stoa Colonnade / Agora Walk

**Style:** greek / classical civic  
**Version:** 0.1  
**Sources:** Athenian Agora (Stoa of Attalos); Hellenistic agora colonnades; Vitruvius on porticoes; Delos processional courts

## Motifs

- Long covered colonnade (stoa) as the public walking spine
- Hypostyle pillar hall depth behind the arcade face
- Freestanding column markers at corners — never towers
- Propylon / Roman arch portal as civic gate
- Processional stair or ramp into the agora court
- Fountain court terminus for gathering — horizontal civic chain only

## Proportions

- Stoa hall wider than tall (colonnade reading, not vertical monument)
- Arcade bays roughly square to slightly wider-than-tall
- Column height ~4–5 m with modest flute density
- Approach rise modest relative to run (civic stair, not pyramid climb)
- Corner markers are pillars / piers, never bell towers or obelisks

## Rhythms

1. Hypostyle stoa hall (deep covered walk)
2. Arcade colonnade face
3. Freestanding column marker
4. Processional stair approach
5. Propylon / Roman portal
6. Agora fountain court terminus

## Structural rules

- Prefer horizontal civic chains: hall → arcade → column → stair → portal → court
- Banned vertical spines: TOWER, TESSELLATION_TOWER, BELL_TOWER, WATCHTOWER, OBELISK, KEEP
- Compose `corner_tower` maps to pillar pier, not a tower kit
- `axis_compression` keeps the chain ground-hugging

## Ornament systems

- Recessed trim bands (`gb_trim_mode: RECESS`)
- Fluted pillars as classical ornament stand-in
- Stone / MARBLE materials for civic permanence

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| greek_stoa_hall | GREYBOX_PILLAR_HALL | Deep covered stoa |
| greek_colonnade | GB_ROMANESQUE_ARCADE | Arcade face stand-in |
| greek_column | PILLAR | Freestanding Doric/Ionic marker |
| greek_approach_stair | GREYBOX_STAIR_BLOCK | Processional approach |
| greek_propylon | ARCHWAY_ADV (ROMAN) | Civic portal |
| greek_agora_fountain | PUBLIC_FOUNTAIN | Court terminus |

## OS hooks

- Genome: `greek_stoa_v1`
- Grammar graph: `GREEK_STOA`
- Compose style: `GREEK_STOA`
