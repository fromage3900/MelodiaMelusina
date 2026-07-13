# Study: Tibetan Monastery Courtyard (Gompa Court)

**Style:** tibetan  
**Version:** 0.1  
**Sources:** Jokhang / Samye courtyard plans; kora path typology; dukhang hypostyle halls

## Motifs

- Trapezoidal lintel portal (go-khang / entrance frame)
- Circumambulatory kora corridor around the court
- Processional stair + ramp terraces on hillside compounds
- Hypostyle dukhang assembly hall (column grid under timber roof)
- Courtyard colonnade / arcade facing the open court
- Sacred water basin / offering pool at court center

## Proportions

- Horizontal civic chain preferred — courtyard width dominates vertical massing
- Portal: ~2.4–2.8 m wide lintel opening
- Kora corridor: tileable 8–10 m runs
- Stair block: 10–14 steps, shallow rise for procession
- Dukhang hall: 3×2 or 4×3 column grid

## Rhythms

- Gate → kora → stair ascent → arcade court → dukhang → ramp terrace → basin
- Repeat colonnade bays along court edges; avoid tower spines

## Structural rules

- No TOWER / TESSELLATION_TOWER / BELL_TOWER / WATCHTOWER / OBELISK / KEEP
- Corner markers resolve to pillars (chorten-like posts), not vertical spines
- Axis compression transform keeps the chain horizontal/civic

## Ornament systems

- Recess trim on corridor and arcade bays
- Stone / timber material language (STONE + AUTO)

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| tibetan_lintel_portal | ARCHWAY_ADV (LINTEL) | Entrance go-khang |
| tibetan_kora | GREYBOX_CORRIDOR | Circumambulation spine |
| tibetan_processional_stair | GREYBOX_STAIR_BLOCK | Court ascent |
| tibetan_dukhang | GREYBOX_PILLAR_HALL | Assembly hall |
| tibetan_arcade | GB_ROMANESQUE_ARCADE | Courtyard colonnade |
| tibetan_terrace_ramp | GREYBOX_RAMP | Hillside approach |
| tibetan_court_basin | PUBLIC_FOUNTAIN | Sacred water |

## OS hooks

- Genome: `tibetan_monastery_v1`
- Grammar graph: `TIBETAN_MONASTERY`
- Compose style: `TIBETAN_MONASTERY`
