# Surreal Architecture — Changelog

## v2.71.0 — Zen architecture expansion (engawa, bamboo fence, tobi-ishi)

- **`zen_kit.py`** — `GB_ZEN_ENGAWA`, `GB_ZEN_BAMBOO_FENCE`, `GB_ZEN_TOBIISHI` greybox builders + snap hooks
- **Graph library** — `ZEN_TEA_GARDEN` chain; roji/shrine graphs updated with new modules
- **Research presets** — engawa veranda, bamboo fence, tobi-ishi path quick-launch
- **World** — `spawn_zen_temple_plan` L-shaped compound + `plan_spawn_zen_temple` operator
- **Trim export** — per-kit trim groups for new zen greybox modules
- **Verify** — zen kit smoke + `ld_temple` world tier

## v2.70.0 — Beavel / Synthia / Higgsas pipeline + Polyhedra library

- **`bevel_bridge.py`** — Beavel Pro (`mesh.beavel_operator`) hybrid with native `MOD_BEVEL`; `bevel_backend` + `surreal_arch.bake_beavel`
- **`synthia_bridge.py`** — spawn wrapper, tagged capture, 4 `SYNTHIA_*` arch types with bmesh fallback; panel re-enabled
- **`higgsas_bridge.py`** — library path preference, `load_arch_nodes`, post-generate `higgsas_detail` pass
- **`capabilities.py` + `pipeline.py`** — optional-deps detection + ordered post-generate stages
- **`polyhedra.py`** — 14-shape registry (Kepler–Poinsot, Platonic, Archimedean, compounds); `spawn_polyhedron` operator
- **`bootstrap.py`** — addon preferences for Higgsas/Synthia paths; `repatch()` helper
- **Unicode** — `deploy/tools/fix_mojibake.py` + UI string restoration
- **Verify** — polyhedra smoke, bridge tiers, `_surreal_patched` assert; `register_overhaul` in headless path
- **UI** — Level Design: Bake Beavel Pro; Synthia panel dependency status; `FILE_TICK` icon fix

## v2.69.0 — World pipeline review + TD/LD contracts

- **TD manifest contract** — [`SURREAL_WORLD_MANIFEST.md`](SURREAL_WORLD_MANIFEST.md), `schema_version`, `hism_groups`, project MI paths in `ROLE_UE_HINTS`
- **LD QA checklist** — [`SURREAL_WORLD_LD_QA.md`](SURREAL_WORLD_LD_QA.md) + automated metrics tier in `_mcp_verify_world.py`
- **Unified verify** — `_mcp_verify_all.py` + `run_verify.ps1` (always `--factory-startup`)
- **FBX export verify tier** — per-role batch export in world verify
- **Layer 2 monolith extract** — library/compose/castle plan delegate to `surreal_world/` (no duplicate implementations)
- **UE importer** — [`Content/Python/import_world_manifest.py`](../Content/Python/import_world_manifest.py)

## v2.68.0 — Procedural world compose pipeline (AAA)

- **`surreal_world/` package** — library bake, plans, COLLECTION compose, UE manifest export
- **COLLECTION mode (default)** — non-destructive WorldRoot + linked instances + per-piece metadata
- **Fixes** — `is_sacred` tag dispatch, `BOULDER_PILE` in library spec, headless-safe library bake
- **ZEN_SHRINE** compose style + Zen Roji plan spawner
- **`export_world_ue`** operator — `surreal_arch_world_v1` JSON manifest
- **Verify** — `_mcp_verify_world.py` + dedicated `surreal_world_loop.ps1`

## v2.67.0 — Zen modular kit expansion

- **`zen_kit.py`** — `GB_ZEN_ROJI_STEP`, `GB_ZEN_TORII_GATE`, `GB_ZEN_TSUKUBAI` greybox builders + snap hooks for `ZEN_*` architecture types
- **Graph library** — `ZEN_ROJI_PATH`, `ZEN_SHRINE_COURTYARD` module chains (style: zen)
- **Research presets** — roji step, modular torii gate, tsukubai basin quick-launch
- **Trim export** — per-kit trim groups for zen greybox modules
- **Verify** — zen kit smoke + trim_groups tier in `_mcp_verify_overhaul.py`

## v2.66.11 — Trim export QA (micro)

- **`gn_trim_zone_faces`** in UE sidecar payload when GN trim zones are present
- Level Design QA row: trim group + GN trim-zone face counts
- Verify: trim-zone GN tier + export contract checks sidecar field (hot-reload safe)
- **`gb_bake_trim_colors`** routes `apply_trim_bake` through per-face `SURREAL_TRIM` vertex colors (`meshes.new_from_object` for GN-only meshes)
- Sidecar fields **`trim_color_layer`** / **`trim_bake_mode`** when zone bake active

## v2.66.10 — Trim wrapper hot-reload

- **`_wire_trim_box_wrapper`** re-applies after `surreal_greybox.attach_all` on every `patch_monolith` (fixes lost trim face attrs on addon reload)
- Verify tier unchanged; all GB_* kits still pass snaps + trim_groups

## v2.66.9 — Per-face trim zones in GN

- `_gb_box` geometry stamped with `surreal_trim_zone` / `surreal_trim_id` via `trim_color_bake.tag_trim_geometry`
- Arch/vault procedural segments tagged so **JoinGeometry** preserves face attributes through kit joins

## v2.66.8 — UE export sidecar

- **FBX sidecar JSON** — `write_sidecar_json()` writes `<fbx>.snap.json` on Bake & Export UE5
- **Snap normalization** — `normalize_snap_points()` standardizes type/rule casing in export payload
- **Level Design export row** — Bake & Export UE5 + Snap JSON buttons in N-panel / Level Design

## v2.66.6–2.66.7 — Stability + catalog dispatch

- ARCH_CATALOG-driven dispatch registry (`catalog_dispatch.py`)
- Named trim zones on kit `_gb_box` labels
- Verify script re-patches monolith after `importlib.reload`
- Gothic tracery panel snap points; idempotent overhaul class registration

## v2.66.0 — Growth plan implementation

### UE pipeline
- **Trim attribute bake** (`surreal_arch/trim_bake.py`) — writes `trim_id` vertex color layer + face attribute from trim metadata
- **Bake & Export to UE5** — auto-applies trim bake on baked mesh before FBX export
- **Bake Trim Attributes** operator in Level Design panel
- Extended snap JSON export with trim groups and UE material slot hints

### Engineering
- **`register_kit()` API** (`surreal_arch/kit_registration.py`) — single-call kit registration for builder + snap + dispatch
- **`surreal_greybox/` package** — extracted `_gb_box`, `_gb_join`, `_gb_bool_diff`, trim helpers, snap load utilities
- **Dynamic `_KIT_DISPATCH`** hook in generation pipeline
- **Workflow panel polls** — BLOCKOUT mode hides music, magic, Sverchok, Escher, effects, etc.

### Content
- **`GB_ROMANESQUE_APSE`** — semicircular choir apse with recess shell
- **Graph library** (style-grouped UI):
  - Romanesque Choir + Apse
  - Venetian Canal Block
  - Sci-Fi Command Deck (expanded)

### QA
- Extended `_mcp_verify_overhaul.py` — all `GB_*` kits, graphs, research presets, trim bake

---

## v2.65.x — Overhaul iterations

- v2.65.0 — Romanesque arcade, corridor offset, research presets, window reveals
- v2.65.1 — Brutalist panel wall, Romanesque cloister graph
- v2.65.2 — Venetian loggia bay
- v2.65.3 — Sci-Fi pressure door + airlock graph
- v2.65.4+ — ARCH_CATALOG glossary, quick-launch parity

## v2.64.0 — UI overhaul

- Searchable architecture picker, workflow modes, VIEW_3D panels
- Gothic kit, snap overlay, room graphs
