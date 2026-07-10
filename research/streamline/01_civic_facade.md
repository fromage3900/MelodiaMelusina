# Study: Streamline Moderne Civic Facade

**Style:** streamline / art deco late  
**Version:** 0.1  
**Sources:** Miami Beach Art Deco Historic District; Raymond Loewy transport design; 1930s civic terminals and ocean-liner hotels

## Motifs

- Long horizontal banding and continuous parapet lines
- Soft rounded corners (ocean-liner / speed-form curves)
- Flat lintel portals instead of pointed or towered gates
- Processional ramps and low stair blocks into a civic court
- Colonnade / arcade as the public walking spine
- Balconette ribbons and fountain court terminus — no vertical spines

## Proportions

- Facade height stays mid-rise (panel wall ~3.5–4.0 m bands)
- Ramp rise modest relative to length (civic approach, not monument climb)
- Arcade bays wider than tall for horizontal reading
- Corner markers are pillars / piers, never towers or obelisks

## Rhythms

1. Curved retaining / street wall (speed-form edge)
2. Horizontal panel facade band
3. Approach ramp
4. Arcade colonnade walk
5. Lintel civic portal
6. Fountain court terminus

## Structural rules

- Prefer horizontal civic chains: facade → ramp → arcade → portal → court
- Banned vertical spines: TOWER, TESSELLATION_TOWER, BELL_TOWER, WATCHTOWER, OBELISK, KEEP
- Compose `corner_tower` maps to pillar pier, not a tower kit
- `axis_compression` keeps the chain ground-hugging

## Ornament systems

- Recessed trim bands (`gb_trim_mode: RECESS`)
- Geometric filigree optional as secondary accent (not required in spine)
- Stone / AUTO materials for civic permanence

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| streamline_curve_wall | CURVED_WALL | Speed-form street edge |
| streamline_panel_band | GB_BRUTALIST_PANEL_WALL | Horizontal banding stand-in |
| streamline_ramp | GREYBOX_RAMP | Civic approach |
| streamline_arcade | GB_ROMANESQUE_ARCADE | Colonnade walk |
| streamline_lintel_gate | ARCHWAY_ADV (LINTEL) | Flat moderne portal |
| streamline_court_fountain | PUBLIC_FOUNTAIN | Court terminus |

## OS hooks

- Genome: `streamline_moderne_v1`
- Grammar graph: `STREAMLINE_MODERNE`
- Compose style: `STREAMLINE_MODERNE`
