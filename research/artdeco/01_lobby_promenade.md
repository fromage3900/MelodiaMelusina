# Study: Art Deco Lobby Promenade (Tower-Ban Rematerialize)

**Style:** artdeco / civic  
**Version:** 0.2  
**Sources:** Chrysler Building lobby motifs, Miami Beach Streamline Deco street walls, setback massing without vertical spines

## Motifs

- Horizontal chevron and sunburst filigree on panel walls
- Stepped geometric facade bays (not tower shafts)
- Cusped / pointed portal as ceremonial gate
- Inclined promenade ramp linking lobby levels
- Colonnade / pillar rhythm at corners instead of corner towers
- Fountain court terminus (no obelisk spire)

## Proportions

- Facade height ~2.5–3.5× bay width
- Ramp rise ~0.35–0.5 of facade height over 8–12 m run
- Filigree panels ~1.4–1.8 m wide inset screens
- Pillar height matches arcade / panel wall (~3.6–4.2 m)

## Rhythms

1. Geometric facade hero → panel wall walk
2. Chevron filigree accent → cusped portal threshold
3. Balconette → ramp promenade → fountain terminus

## Structural rules

- **No tower spines** — banned: TOWER, TESSELLATION_TOWER, BELL_TOWER, WATCHTOWER, OBELISK, KEEP
- Corner role maps to `PILLAR` (colonnade post), not tessellation tower
- Prefer `axis_compression` over `vertical_stretch` for horizontal civic chain
- Monument role is fountain / civic water, not obelisk

## Ornament systems

- `FILIGREE_PANEL` with `GEOMETRIC_ARABESQUE` (chevron / lattice read)
- Recessed trim on brutalist panel walls as Deco setback shadow lines
- Cusped arch as Deco portal silhouette

## Extracted atoms

| Atom ID | Kit / part | Notes |
|---------|------------|-------|
| deco_facade_bay | BAROQUE_FACADE | Horizontal civic hero massing |
| deco_panel_wall | GB_BRUTALIST_PANEL_WALL | Geometric setback wall |
| deco_chevron_screen | FILIGREE_PANEL | Chevron / geometric ironwork |
| deco_cusped_portal | CUSPED_ARCH | Lobby gate |
| deco_balconette | BALCONY | Mid-level accent |
| deco_promenade_ramp | GREYBOX_RAMP | Inclined civic connector |
| deco_corner_pillar | PILLAR | Replaces corner tower |
| deco_fountain_court | PUBLIC_FOUNTAIN | Terminus monument |

## OS hooks

- Genome: `art_deco_lobby_v1`
- Grammar graph: `ART_DECO`
- Compose style: `ART_DECO`
- Transform: `axis_compression`
