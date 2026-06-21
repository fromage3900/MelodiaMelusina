# Surreal Architecture — Loop State

**Version:** 2.66.11  
**Loop sentinel:** `AGENT_LOOP_TICK_surreal_micro10`  
**Interval:** 600s (10 min)

## Completed — Growth plan (v2.66.0)

- **Trim bake** — `trim_bake.py`, UE5 export hook, Bake Trim Attributes operator
- **Graph registry UI** — style-grouped graph library in Level Design panel
- **register_kit()** — `kit_registration.py`; Sci-Fi door + Romanesque apse migrated
- **surreal_greybox/** — primitives + snaps extracted and bound at register
- **Verify expansion** — all GB_* kits, graphs, presets, trim bake in `_mcp_verify_overhaul.py`
- **Content graphs** — ROMANESQUE_APSE, VENETIAN_CANAL, SCI_FI_DECK_EXPANSION
- **GB_ROMANESQUE_APSE** — new kit type + snaps + trim metadata
- **Workflow polls** — BLOCKOUT/ARCHITECTURE panel filtering
- **Docs** — `SURREAL_ARCH_CHANGELOG.md`, research doc synced to v2.66.0

### Iteration 10 (tick 26 — 2026-06-20)
- **v2.66.2** — Per-face trim zones in GN + graph snap polish + apse preset

### Iteration 11 (ticks 27–31 — 2026-06-20)
- **v2.66.3** — surreal_greybox phase 2: corridor + room shell extraction

### Iteration 12 (ticks 32–34 — 2026-06-20)
- **v2.66.4** — surreal_greybox phase 3: extracted junction builders

### Iteration 13 (ticks 43–56 — 2026-06-20)
- **v2.66.5** — Asset Browser publishing operator + Level Design panel button

### Iteration 14 (tick 66 — 2026-06-20)
- **v2.66.6** — ARCH_CATALOG drives dispatch
- `catalog_dispatch.py` — `_CATALOG_DISPATCH` registry, greybox param spec stubs, `sync_catalog_dispatch()`
- `kit_registration.py` + `catalog.py` — builder_attr wired through catalog metadata

### Iteration 15 (ticks 67–68 — 2026-06-20)
- **v2.66.7** — Named trim zones in overhaul kits
- Kit `_gb_box` labels now use `trim:group_id` matching `build_trim_groups` (romanesque, brutalist, venetian, scifi, corridor offset)

### Iteration 16 (ticks 69–74 — 2026-06-20)
- **v2.66.8** — Catalog enum codegen stub export
- `catalog_enum.py` — `generate_enum_items()`, export operator writes `catalog_arch_type_items.py` from ARCH_CATALOG
- Level Design → Asset Browser: **Export Catalog Enum Stub** button

### Iteration 17 (ticks 75–79 — 2026-06-20)
- **v2.66.9** — Trim zone GN join fix
- All `_gb_box` geometry stamped with `surreal_trim_zone` / `surreal_trim_id` (body=0, trim=zone)
- Arch/vault procedural segments tagged so JoinGeometry preserves face attributes

**Version:** 2.66.10  

### Iteration 18 (ticks 80–85 — 2026-06-20)
- **v2.66.10** — Trim bake verify: re-apply `_gb_box` trim wrapper after every `attach_all` (hot-reload safe)

## Backlog (next ticks)

1. **Loop hygiene** — shell checks `deploy/SURREAL_ARCH_LOOP_STOP` (optional); user can also say **"stop nap loop"**

### Micro-cycle 2 (2026-06-20)
- UE5 export now writes **`<name>.snap.json` sidecar** next to FBX (`snap_export.write_sidecar_json`)
- Snap contract normalization (`normalize_snap_points`) in export payload
- Level Design panel: **Bake & Export UE5** + Snap JSON buttons (export parity)

### Micro-cycle 3 (2026-06-20)
- Verify: **export contract** tier (payload format, snap normalization, sidecar write)
- Changelog updated for v2.66.6–v2.66.8
- **Hotfix**: repaired syntax corruption in `greybox_offset.py`, `venetian_kit.py`, `scifi_kit.py` (restored snap/trim hooks)
- Post-fix verify: **all GB_* kits pass** (snaps + trim_groups)

### Micro-cycle 4 (2026-06-20)
- QA pass: full `_mcp_verify_overhaul.py` green on live **v2.66.10**
- Docs: changelog + research synced for v2.66.9 (GN trim zones) and v2.66.10 (trim wrapper hot-reload)

### Micro-cycle 5 (2026-06-20)
- Verify: **trim zone GN** tier — brutalist RECESS kit must stamp `surreal_trim_zone` on evaluated mesh (JoinGeometry regression guard)

### Micro-cycle 6 (2026-06-20)
- **UX**: Level Design shows trim group count + GN trim-zone face count after generate
- **Export**: sidecar payload includes `gn_trim_zone_faces` when trim zones present (`count_eval_trim_zone_faces`)
- Verify: export payload asserts `gn_trim_zone_faces` on RECESS brutalist

### Micro-cycle 7 (2026-06-20)
- Export contract verify: reload `snap_export`, assert `gn_trim_zone_faces` in payload + written sidecar JSON
- Changelog **v2.66.11** micro slice; loop stop sentinel path documented (`deploy/SURREAL_ARCH_LOOP_STOP`)

### Micro-cycle 8 (2026-06-20)
- Verify: **catalog enum** tier — `generate_enum_items` covers all GB_* kits; stub export format smoke
- Research doc: sidecar `gn_trim_zone_faces` field documented

### Micro-cycle 9 (2026-06-20)
- **Loop hygiene**: `deploy/surreal_micro_loop.ps1` honors `SURREAL_ARCH_LOOP_STOP`; `deploy/sync_surreal_to_live.ps1` one-shot deploy→live sync
- Verify: **pipeline operators** tier (export UE5, snap JSON, trim bake, catalog enum, assembly check, overlay, asset publish)

### Micro-cycle 10 (2026-06-20)
- **v2.66.11** `bl_info` bump (aligns with changelog micro slice)
- Verify: **catalog dispatch** tier — `_KIT_DISPATCH` mirrored in `_CATALOG_DISPATCH`, builders resolve

### Micro-cycle 11 (2026-06-20)
- Verify: **surreal_greybox extract** tier — core `_gb_*` bindings present after `patch_monolith`
- Research doc version header → **v2.66.11**

### Micro-cycle 12 (2026-06-20)
- Verify: **workflow modes** tier — BLOCKOUT vs ARCHITECTURE panel/style filtering
- LOOP_STATE header synced (v2.66.11, 10m sentinel)

### Micro-cycle 13 (2026-06-20)
- **Pipeline**: `gb_bake_trim_colors` → per-face `SURREAL_TRIM` via `bake_trim_vertex_colors` in `apply_trim_bake`
- GN-only meshes: bake uses `meshes.new_from_object` (Blender 5 eval→mesh contract)
- Verify: trim bake asserts zone color layer when `gb_bake_trim_colors` enabled
- **Sync fix**: `sync_surreal_to_live.ps1` force-copies each `.py` (folder recurse was skipping updates)

### Micro-cycle 14 (2026-06-20)
- Sidecar payload: `trim_color_layer` + `trim_bake_mode` when `SURREAL_TRIM` baked
- UE5 export passes monolith into `apply_trim_bake` for correct trim groups
- Export contract verify asserts zone-bake metadata in payload

### Micro-cycle 15 (2026-06-20)
- Verify: **`resolve_trim_zone`** maps `trim:group_id` labels; non-trim labels return `None`
- Docs: changelog + research synced for zone bake + sidecar trim fields

### Micro-cycle 16 (2026-06-20)
- Verify: **kit snap hooks** tier — `_gb_compute_snap_points` returns snaps for all GB_* kits without full GN generate

## Notes
- Deploy: `deploy/surreal_architecture_gen.py` + `deploy/surreal_arch/` + `deploy/surreal_greybox/`
- Live sync: run `deploy/sync_surreal_to_live.ps1` or copy manually to `%APPDATA%\Blender Foundation\Blender\5.1\scripts\addons\`
- Stop nap loop: say **"stop nap loop"** or create empty `deploy/SURREAL_ARCH_LOOP_STOP`
- **Loop stopped** 2026-06-20 — pivoted to Zen library expansion (tick 17+ ignored)
- Do not edit `surreal_architecture_overhaul_a4161727.plan.md`
