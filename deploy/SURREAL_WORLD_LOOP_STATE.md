# Surreal World — Loop State

**Version:** 2.69.0  
**Loop sentinel:** `AGENT_LOOP_TICK_world_micro10`  
**Interval:** 600s (10 min)  
**Stop:** `deploy/stop_world_loop.ps1` or `deploy/SURREAL_WORLD_LOOP_STOP`  
**Start:** `deploy/start_world_loop.ps1` (detached — survives Cursor shell exit)  
**Log:** `deploy/SURREAL_WORLD_LOOP.log`  
**PID:** `deploy/SURREAL_WORLD_LOOP.pid`

## Phase 0–3 — Initial implementation (2026-06-20)

- **`surreal_world/` package** — library, plans, compose, instance, export, tags, patch
- **COLLECTION compose mode** (default AAA) — WorldRoot + linked instances + metadata
- **Fixes** — `is_sacred` dispatch, `BOULDER_PILE` in library spec, headless-safe library bake
- **ZEN_SHRINE** style + `SurrealPlan_ZenRoji` + `plan_spawn_zen_roji` operator
- **`export_world_ue`** — `surreal_arch_world_v1` manifest JSON
- **Verify** — `_mcp_verify_world.py` (library, compose, recompose, sacred, export)
- **Probe** — `probe_world_pipeline.py`
- **Research** — `SURREAL_WORLD_RESEARCH.md` v0.1

## v2.69 — Review plan implementation (2026-06-21)

- TD manifest contract + UE importer
- LD automated metrics verify tier
- Unified verify (`run_verify.ps1`, `--factory-startup`)
- FBX export verify tier
- Monolith Layer 2 delegates (no duplicate compose/library code)

## Loop infra fix (2026-06-21)

- **Problem:** inline Cursor background shells exit when agent session ends
- **Fix:** `start_world_loop.ps1` → detached `Start-Process` + PID file + log + per-tick verify health check
- **Commands:** `start_world_loop.ps1` / `stop_world_loop.ps1`

## Loop tick 4 (2026-06-21) — loop resumed + motte/bailey extract

- **Slice:** `spawn_motte_bailey_plan` → `surreal_world/plans.py` + WESTERN_CASTLE verify tier
- **Loop:** restarted (PID 34460, old PID 12760 had died)
- **Verify:** PASS — `ld_motte: OK` (37 instances)
- **Next slice:** coastal/starfort plan extract OR JOINED legacy verify

## Loop tick 3 (2026-06-21) — grid city plan extract

- **Slice:** `spawn_grid_city_plan` → `surreal_world/plans.py` + ASIAN_CITY verify tier
- **Also:** Asian library types in `VERIFY_LIBRARY_TYPES`
- **Verify:** PASS — `ld_city: OK` (82 instances, 4x4 grid ASIAN_CITY)
- **Next slice:** motte/bailey plan extract OR JOINED legacy mode verify

## Loop tick 2 (2026-06-21) — one_click_castle COLLECTION verify

- **Slice:** `one_click_castle` explicit COLLECTION + WorldRoot resolution; verify tier (Layer 3 disabled)
- **Verify:** PASS — `one_click_castle: OK` (20 instances, WorldRoot, COLLECTION)
- **Next slice:** grid city plan extract to `surreal_world/plans.py`

## Loop tick 1 (2026-06-21) — village plan extract

- **Slice:** migrate `spawn_village_plan` to `surreal_world/plans.py` + WESTERN_VILLAGE verify tier
- **Also:** extended `VERIFY_LIBRARY_TYPES` with TOWN_HALL, TAVERN, BLACKSMITH, VILLAGE_WELL, BELL_TOWER
- **Verify:** PASS — `run_verify.ps1 -Mode world` (25 village instances, ld_village OK)
- **Next slice:** grid city plan extract OR `one_click_castle` COLLECTION verify

## Backlog (next ticks)

1. GN terrain node group (`terrain_gn.py`)
2. Slope-aware scatter integration with Layer 3
3. ~~Per-role FBX batch export verify in CI~~ (done v2.69)
4. ~~WFC-style grid city plan generator~~ (basic grid extract tick 3; WFC deferred)
5. ~~`one_click_castle` end-to-end verify with COLLECTION + Layer 3 disabled~~ (tick 2)

## Notes

- Sync: `deploy/sync_surreal_to_live.ps1` (includes `surreal_world/`)
- Verify: Blender MCP or `blender --background --python deploy/_mcp_verify_world.py`
- Compose panel: Zen Roji Plan + Export World to UE buttons
