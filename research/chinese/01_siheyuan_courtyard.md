# Study: Chinese Siheyuan Courtyard (四合院)

**Style:** chinese  
**Version:** 0.1  
**Sources:** Beijing siheyuan typology; northern Chinese courtyard house plans; hutong alley → gate → court sequence

## Motifs

- Street **pailou / gate** moment opening from hutong into the compound
- Covered **lang** corridor wrapping the court on one or more sides
- Raised **platform stair** ascent into the main hall (zhengfang)
- Main hall as a horizontal residential block — not a pagoda spine
- Side **arcade / gallery** bays defining court enclosure
- Rear **moon gate** terminus into the garden court (houyuan)

## Proportions

- Courtyard is the primary volume — width dominates height
- Main hall bay module ~5–6 m; corridor length longer than height
- Gate hierarchy: street gate taller than garden moon gate

## Rhythms

1. Pailou street gate
2. Covered lang corridor
3. Platform stair to main hall
4. Zhengfang main hall (hanok-scale hall stand-in)
5. Side arcade gallery
6. Moon gate garden terminus

## Structural rules

- Prefer facades, courts, arcades, stairs, ramps, colonnades — **no tower spines**
- Banned arch types for this grammar: TOWER, TESSELLATION_TOWER, BELL_TOWER, WATCHTOWER, OBELISK, KEEP, CN_TIERED_PAGODA
- Compose `corner_tower` role remaps to `_lib_PILLAR` (corner pier / free-standing column)

## Ornament systems

- Recess trim on greybox corridor / arcade modules
- Stone / wood material defaults on gate and hall kits
- Moon gate as soft garden threshold after hard street gate

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| `pailou_gate` | `CN_PAILOU` | Street entrance |
| `lang_corridor` | `GREYBOX_CORRIDOR` | Covered court walk |
| `platform_stair` | `GREYBOX_STAIR_BLOCK` | Raised hall approach |
| `zhengfang_hall` | `KR_HANOK` | Main hall stand-in |
| `side_arcade` | `GB_ROMANESQUE_ARCADE` | Gallery colonnade |
| `moon_gate` | `CN_MOON_GATE` | Garden terminus |

## OS hooks

- Genome: `chinese_siheyuan_v1`
- Grammar graph: `CHINESE_SIHEYUAN`
- Compose style: `CHINESE_SIHEYUAN`
- Transform: `axis_compression`
