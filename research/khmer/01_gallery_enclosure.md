# Study: Khmer Gallery Enclosure

**Style:** khmer  
**Version:** 0.1  
**Sources:** Angkor Wat / Angkor Thom gallery typology; gopura → enclosure → baray processional chain

## Motifs

- Gopura lintel portal as ceremonial threshold
- Long enclosed stone galleries with colonnade rhythm
- Processional stair and ramp ascents between terrace levels
- Hypostyle sanctuary hall as sacred terminus
- Baray / sacred pool as court monument

## Proportions

- Horizontal civic chain preferred over vertical spines
- Gallery bays ~3–4 m; stair runs ceremonial and wide
- Ramp rise modest relative to length (processional, not tower)

## Rhythms

- Gate → gallery corridor → stair → arcade colonnade → ramp → pool
- Alternating enclosed corridor and open arcade bays
- Pillar cadence as corner markers (no tower spines)

## Structural rules

- No TOWER / TESSELLATION_TOWER / BELL_TOWER / WATCHTOWER / OBELISK / KEEP
- `corner_tower` compose role maps to `PILLAR`
- Prefer facades, courts, arcades, stairs, ramps, colonnades

## Ornament systems

- Stone lintel portals; recess trim on greybox galleries
- Arcade colonettes stand in for Khmer half-vault gallery language

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| khmer_gopura | ARCHWAY_ADV (LINTEL) | Ceremonial gate |
| khmer_gallery | GREYBOX_CORRIDOR | Enclosed gallery walk |
| khmer_stair | GREYBOX_STAIR_BLOCK | Terrace ascent |
| khmer_arcade | GB_ROMANESQUE_ARCADE | Open colonnade bay |
| khmer_ramp | GREYBOX_RAMP | Processional ramp |
| khmer_baray | PUBLIC_FOUNTAIN | Sacred pool terminus |
| khmer_hypostyle | GREYBOX_PILLAR_HALL | Sanctuary hall (compose large/sacred) |

## OS hooks

- Genome: `khmer_gallery_v1`
- Grammar graph: `KHMER_GALLERY`
- Compose style: `KHMER_GALLERY`
- Transform: `axis_compression`
