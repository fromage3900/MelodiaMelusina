# Study: Hindu Mandapa Courtyard (मंडप)

**Style:** hindu  
**Version:** 0.1  
**Sources:** South Indian temple prakara / mandapa typology; Dravidian temple court plans; open sabha-mandapa colonnades

## Motifs

- Ornate **torana** portal threshold (cusped / multi-lobed) — gate moment, not a gopuram tower spine
- Covered **prakara** ambulatory corridor wrapping the court
- Open **mandapa** hypostyle hall as the primary civic volume
- Side **arcade / colonnade** bays defining sabha enclosure
- Raised **jagati** plinth stair into the sacred platform
- Processional **ramp** approach for festival paths and chariot routes
- Temple **kund / pushkarini** tank as the court monument terminus

## Proportions

- Courtyard and mandapa width dominate height — horizontal civic chain
- Pillar bay module ~3.5–4 m; corridor length longer than height
- Torana portal taller than arcade bay but not a tower

## Rhythms

1. Torana portal (cusped arch gate)
2. Prakara ambulatory corridor
3. Open mandapa pillar hall
4. Sabha arcade colonnade
5. Jagati plinth stair
6. Processional ramp
7. Temple tank (compose monument) / garbhagriha stand-in (compose sacred)

## Structural rules

- Prefer facades, courts, arcades, stairs, ramps, colonnades — **no tower spines**
- Banned arch types for this grammar: TOWER, TESSELLATION_TOWER, BELL_TOWER, WATCHTOWER, OBELISK, KEEP
- Compose `corner_tower` role remaps to `_lib_PILLAR` (free-standing pillar / stambha)

## Ornament systems

- Cusped multi-lobed portal edge on the torana
- Recess trim on greybox corridor / arcade / pillar-hall modules
- Stone material defaults on processional and colonnade kits

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| `torana_portal` | `CUSPED_ARCH` | Ornate temple gate |
| `prakara_corridor` | `GREYBOX_CORRIDOR` | Covered ambulatory |
| `mandapa_hall` | `GREYBOX_PILLAR_HALL` | Open hypostyle mandapa |
| `sabha_arcade` | `GB_ROMANESQUE_ARCADE` | Colonnade bay |
| `jagati_stair` | `GREYBOX_STAIR_BLOCK` | Raised plinth ascent |
| `processional_ramp` | `GREYBOX_RAMP` | Festival / chariot ramp |

## OS hooks

- Genome: `hindu_mandapa_v1`
- Grammar graph: `HINDU_MANDAPA`
- Compose style: `HINDU_MANDAPA`
- Transform: `axis_compression`
