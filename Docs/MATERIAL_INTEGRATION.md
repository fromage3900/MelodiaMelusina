# Material integration (2026-06-19)

Session summary for portfolio masters, SDF expansion, compositing textures, and editor tooling.

## What landed

| Area | Result |
|------|--------|
| **Universal masters** | `M_Master_Toon_Universal`, `M_Master_SDF_Toon`, `M_Master_Toon_Unified` — 18/18 texture params wired, Substrate Toon, compile OK |
| **Starter instances** | 10 curated `MI_Show_*` under `Instances/Showcase/` — one master capability each (see below) |
| **Legacy MI_Universal_*** | 141+ presets deprecated; move to `Instances/_Archive/` via `archive_unused_instances.py` (no delete) |
| **SDF masters** | All 50 `_PROJECT` `M_SDF_*` ported to `EnvSandbox/Materials/Masters/` (incl. 9 aquatic) |
| **Aquatic instances** | `MI_SDF_AbyssalVent_Deep` … `MI_SDF_ThermalGlow_Vent` under `SDF/Instances/` |
| **Toon conversion** | Batches 1–4 via `run_phase_a_safe.py` (baroque, hybrid, aquatic, math/musical expansion) |
| **Storybook PP** | `M_PP_StorybookVines` + `_Inst` rebuilt; stack after `M_PP_ToonOutline` |
| **Blender Live Link** | Menu: **LiveLink → Start/Stop/Status** (not Window → Live Link); see `BLENDER_LIVELINK.md` |

## Master parameter organization (`M_Master_Toon_Universal`)

Groups in the Material Editor (rebuild master with `--force` after group renames):

| Group | Purpose |
|-------|---------|
| **Textures / LayerA / LayerB** | Albedo, normal, ORM, height, detail |
| **Triplanar / Temporal** | World-aligned UVs, ink boil/smear |
| **Parallax** | **`MF_ParallaxCore`** — modes 0/1/2 height UV offset; **`MF_NormalAdjust`** — `NormalStrength`, `NormalPower`, per-layer strengths; `ParallaxSteps` wired |
| **Nikki** | Pastel lift, rim, sparkle, iridescence, bloom, fabric sheen |
| **Celestial** | **`MF_SpaceParallax`** — parallax stars/nebula/galaxy with toon-banded nebula; `StarMap` texture + `CelestialToonSteps`; legacy `ConstellationPhase` / `CelestialTwinkle` / `CelestialGalaxyArms` kept for MI compat (no graph wiring) |
| **Gilding** | Curvature gold leaf |
| **ShadowDream** | Soft N·L shadow color tint |
| **FlowerShadow** | Projected petal silhouettes in shadow (was `ShadowGarden`) |
| **FairyDust** | Highlight motif styles (heart/star/flower/moon) |
| **Magical** | Henshin wipe, `MotifMask`, palette shift, transform glow |
| **Character** | Skin wrap, cheek warmth, eye highlight, hair sheen |
| **Elemental / Cinematic** | Hydro/py/etc., contact rim, distance fade |

Key expansion params have inline `desc` tooltips when the master is rebuilt via `setup_master_universal.py`.

## Starter instances (10)

Canonical set on `M_Master_Toon_Universal` — one isolated capability each. Folder: `/Game/EnvSandbox/Materials/Instances/Showcase`. Source of truth: `Content/Python/starter_instances.py` (`STARTER_INSTANCES`, `STARTER_NAMES`).

| Instance | Theme | Purpose | Key params (editor group) |
|----------|-------|---------|---------------------------|
| `MI_Show_Default` | Default showcase | Neutral tint, full texture weight, zero stylization | `BaseTint`, `TextureWeight`, `Roughness` |
| `MI_Show_StoneCliff` | Stone | Triplanar cliff + **MF_ParallaxCore** POM + normal power | `ParallaxStrength`, `ParallaxSteps`, `NormalStrength` (Parallax) |
| `MI_Show_CherryBlossom` | Flower shadow | Projected petal shadows + sparkle on soft pink | `ShadowFlowerStrength`, `ShadowFlowerScale` (FlowerShadow) |
| `MI_Show_CelestialNebula` | Nebula | **MF_SpaceParallax** constellation ramp + parallax nebula + galaxy | `CelestialNebulaStrength`, `ConstellationRamp*`, `StarMap`, `CelestialToonSteps` (Celestial) |
| `MI_Show_FairyHearts` | Magic / fairy | Heart motif, fairy dust, partial henshin wipe | `MagicalTransform`, `MotifColor`, `FairyDustIntensity` (Magical + FairyDust) |
| `MI_Show_SkinSoft` | Nikki character | Skin wrap, cheek warmth, soft pastel base | `SkinWrapStrength`, `PastelLift`, `CheekWarmthStrength` (Character + Nikki) |
| `MI_Show_ForestFoliage` | Foliage | Mossy forest floor with dreamy shadow tint | `ShadowDreamStrength`, `MossConcavityStrength` (World + ShadowDream) |
| `MI_Show_ContactRimHero` | Cinematic | Contact rim + atmospheric distance fade | `ContactRimStrength`, `DistanceFadeStrength` (Cinematic) |
| `MI_Show_ElementHydro` | Elemental | Wet iridescent hydro glass (`ElementType=2`) | `ElementStrength`, `WetnessStrength` (Elemental) |
| `MI_Show_InkWash` | Stylized ink | Temporal boil + smear + wind | `TemporalStrength`, `SmearStrength`, `WindSpeed` (Temporal) |

Legacy `MI_Universal_*` names map via `LEGACY_ALIASES` in `starter_instances.py` (e.g. `MI_Universal_DreamyPastel` → `MI_Show_SkinSoft`).

## Python scripts (run order)

```text
python Content/Python/repair_crash_assets.py
python Content/Python/portfolio_texture_catalog.py          # disk audit, no editor
python Content/Python/integrate_compositing_textures.py
python Content/Python/run_phase_a_safe.py
```

**Starter pipeline (editor or headless):**

```text
py Content/Python/setup_master_universal.py                 # or --force to refresh groups
py Content/Python/apply_starter_instances.py              # create/update 10 MI_Show_*
py Content/Python/archive_unused_instances.py             # optional: move legacy Environment MIs
py Content/Python/review_portfolio_masters.py             # masters + starter texture pass (editor)
py Content/Python/setup_template_showcase.py              # L_Template sphere row
```

Headless:

```text
set BS_STARTERS_ONLY=1
UnrealEditor-Cmd.exe BS_GodFile.uproject ^
  -ExecutePythonScript="G:/EnvironmentPortfolio/BS_GodFile/Content/Python/apply_starter_instances.py" ^
  -unattended -nullrhi
```

Editor one-shot: `py ".../run_editor_integration.py"`

## Headless notes

- **Monolith** (optional, currently **disabled** in `BS_GodFile.uproject`): requires **GameplayStateTree** and a source rebuild of `Plugins/Monolith` for UE 5.8. Prebuilt DLLs crash at `UMonolithSettings::Get()` / `FMonolithConfigModule::StartupModule()` (null deref) — no `Plugins/Monolith/Source` in this repo. Re-enable only after rebuilding Monolith locally. Until then use **UnrealMCP :55557** or headless Python (`run_sakura_niagara_plan.py`).
- **Never run** `patch_portfolio_texture_paths.py` / `patch_portfolio_uasset_paths.py` (corrupts uassets).
- Close material tabs before batch saves to avoid Error 32 file locks.

## Audit reports (local, gitignored)

`Saved/Audit/`: `master_review.json`, `master_texture_loop.json`, `master_param_loop.json`, `master_param_loop_state.json`, `master_param_catalog_audit.json`, `compositing_integration.json`, `compositing_texture_defaults.json`, `starter_instances.json`, `dead_material_nodes.json`, `ensure_portfolio_instances.json`, `substrate_toon_conversion.json`, `storybook_outline_build.json`

## Not in git

- `/Game/Textures` compositing library (local SBS packs)
- `Content/Python/livelink_unreal.pyc` (3DRedbox client; copy from purchase)
- `Saved/`, `Intermediate/`, audit JSON outputs

## Loop progress

### Tick #1 (2026-06-19) — universal master organization + starter curation

| Task | Status |
|------|--------|
| Parameter groups on `M_Master_Toon_Universal` (Nikki, FlowerShadow, Celestial, Magical, …) | Done — `GROUP_*` in `setup_master_universal.py` |
| Texture catalog audit (`portfolio_texture_catalog.py`) | Done — sparkle/sakura/magical defaults; Perlin demoted to fallback |
| Curate 10 starters (`starter_instances.py`) | Done — `MI_Show_*` under `Instances/Showcase` |
| Starters-only apply script | Done — `apply_starter_instances.py`, `BS_STARTERS_ONLY=1` / `--starters-only` |
| Archive helper for legacy MIs | Done — `archive_unused_instances.py` (no delete) |

Legacy `MI_Universal_*` (141+) under `Instances/Environment` are **not deleted**. Use `archive_unused_instances.py` to move them to `Instances/_Archive` when ready.

### Tick #2 (2026-06-19) — docs + headless apply

| Task | Status |
|------|--------|
| Deduplicate `MATERIAL_INTEGRATION.md` starter table | Done — single table aligned with `starter_instances.py` |
| Headless `apply_starter_instances.py` (UE 5.8, `-nullrhi`, Monolith off) | **OK** — 10/10 `created_or_updated`; audit `Saved/Audit/starter_instances.json` @ 2026-06-20T01:12:30Z; log `Saved/Logs/apply_starters_tick2.log` |
| `review_portfolio_masters.py` | Skipped — requires Unreal `unreal` module (not a disk-only script) |

If a future headless run fails with **Error 32** (file lock), close the editor and any open material tabs, then re-run; otherwise run `apply_starter_instances.py` from an open editor session.

### Tick #3 (2026-06-20) — master force rebuild

| Task | Status |
|------|--------|
| Headless `setup_master_universal.py` with `BS_MASTER_FORCE=1` | **OK** — rebuilt in-place; 656/656 wires; FlowerShadow group + param `desc` tooltips baked |
| Headless `--force` via argv | Fixed — UE-Cmd does not pass `-force` to `sys.argv`; use `BS_MASTER_FORCE=1` env |

**Next tick:** editor `setup_template_showcase.py` (10-sphere row) + `review_portfolio_masters.py` viewport check on nebula/cherry blossom starters.

## Master texture loop (no `/Engine/` textures)

**Hard rule:** Never assign `DefaultTexture`, `WhiteSquareTexture`, or any `/Engine/` path on master texture parameters. All defaults come from `/Game/Textures` compositing catalog via [`portfolio_texture_catalog.py`](Content/Python/portfolio_texture_catalog.py).

| Mechanism | Purpose |
|-----------|---------|
| `material_lib.BANNED_TEXTURE_PATHS` + `sanitize_candidates()` | Block `/Engine/` at assign time |
| `apply_master_defaults(..., force=True)` | Force rewire from compositing catalog |
| `scan_master_texture_violations()` | Audit banned / unwired / wrong-role ORM |
| `run_master_material_loop_tick.py` | One idempotent loop pass (60s cadence) |

**Run (headless, editor closed):**

```text
set BS_MASTER_FORCE=1
py Content/Python/run_master_material_loop_tick.py
```

**Audit:** `Saved/Audit/master_texture_loop.json` — success when `summary.clean` is true (0 banned, 0 unwired).

### Texture loop tick #0 (2026-06-20)

| Master | Result |
|--------|--------|
| `M_Master_Toon_Universal` | 12/12 slots on `/Game/Textures` + alphas; 0 banned; compile OK |
| `M_Master_SDF_Toon` | 3/3 on compositing + SDF marble; 0 banned |
| `M_Master_Toon_Unified` | 3/3 on compositing + SDF marble; 0 banned |

ORM slots use SDF marble packs (not Perlin height noise). Normal slots use compositing `Perlin_10` (no `DefaultNormal`).

## Master parameter loop (group / desc / sort)

**Scope:** Non-texture metadata on `M_Master_Toon_Universal` (scalar, vector, static switch). Texture wiring stays in the texture loop. SDF masters (`M_SDF_*`, `M_Master_SDF_Toon`, `M_Master_Toon_Unified`) get a Palette + Toon subset audit only.

| Mechanism | Purpose |
|-----------|---------|
| `master_param_catalog.PARAM_REGISTRY` | Canonical param → `{group, desc, kind}` for universal master |
| `master_param_catalog.ALL_GROUPS` | Professional MI editor panel sort order |
| `scan_master_param_violations()` | Audit ungrouped, wrong_group, missing_desc, unknown, placeholders |
| `apply_master_param_organization()` | Fix group, tooltip desc, sort_priority (metadata only) |
| `is_master_organized()` | Success: 0 ungrouped, 0 wrong_group, missing_desc under threshold |
| `run_master_param_loop_tick.py` | One idempotent loop pass; rotates 10 focus slices |

**Run (editor open):**

```text
py Content/Python/run_master_param_loop_tick.py
```

**Run (headless, editor closed):**

```text
py Content/Python/run_master_param_loop_tick.py
```

(Outer launcher spawns `UnrealEditor-Cmd` when `unreal` is not importable.)

**One-shot organize + audit:**

```text
py Content/Python/master_param_catalog.py
```

**State / audit paths:**

- State: `Saved/Audit/master_param_loop_state.json` (`tick_index`, `last_focus`)
- Report: `Saved/Audit/master_param_loop.json`
- Catalog audit: `Saved/Audit/master_param_catalog_audit.json`

**Success criteria:** `summary.organized` is `true` on `M_Master_Toon_Universal` in `master_param_loop.json` (0 ungrouped, 0 wrong_group, missing_desc ≤ threshold). Log: `Saved/Logs/master_param_loop.log`.

**Focus rotation (10 ticks):** `audit_full` → `core_palette` → `layers_parallax` → `triplanar_temporal` → `nikki_character` → `celestial_shadow` → `magical_fairy` → `gilding_macro` → `world_elemental` → `cinematic_tod`.

## Master parameter loop (scalar / vector / switch organization)

**Scope:** All non-texture MI editor categories on `M_Master_Toon_Universal` — groups, tooltips, canonical naming. Textures stay on the 60s texture loop.

| Mechanism | Purpose |
|-----------|---------|
| `master_param_catalog.PARAM_REGISTRY` | Canonical group + tooltip per param |
| `scan_master_param_violations()` | Ungrouped, wrong group, missing desc |
| `apply_master_param_organization()` | In-place group/desc fixes per focus |
| `run_master_param_loop_tick.py` | Rotating 10-focus pass (180s cadence) |

**Run (headless, editor closed):**

```text
py Content/Python/run_master_param_loop_tick.py
```

**Audit:** `Saved/Audit/master_param_loop.json` — success when `summary.organized` is true (`organization_score` ≥ 0.95, 0 ungrouped, 0 wrong group).

**Focus rotation (tick % 10):** `audit_full` → `core_palette` → `layers_parallax` → `triplanar_temporal` → `nikki_character` → `celestial_shadow` → `magical_fairy` → `gilding_macro` → `world_elemental` → `cinematic_tod`.

### Param loop tick #0 (2026-06-20)

| Check | Universal master |
|-------|------------------|
| `summary.organized` | **true** |
| Ungrouped / wrong group | 0 / 0 |
| Numbered MI panels | `organize_master_groups.py` every tick (01–21 panel order) |
| Catalog | `master_param_catalog.py` — groups, sort_priority, tooltips |

**Loops running:** `AGENT_LOOP_TICK_master_texture` (60s) + `AGENT_LOOP_TICK_master_params` (180s). Close editor before headless ticks to avoid Error 32.

## Environment specialists (landscape + water)

| Master | Role | Build |
|--------|------|-------|
| `M_Master_Toon_Landscape_HeightBlend` | Toon terrain — triplanar Rock/Grass/Mud height competition + slope cliffs + snow | `py Content/Python/setup_landscape_height_blend.py` |
| `M_Water_Master_Grand_v6` | **Canonical grand water** — Gerstner waves, caustics, magical intensity | `py Content/Python/setup_master_water.py` |

**Do not use** `M_Master_Toon_Water` — deprecated duplicate. Expand grand water only.

**Instances:** `MI_GrandWater_OceanDeep`, `MI_GrandWater_RiverClear`, `MI_GrandWater_PondStylized` → `Instances/Water/`

```text
python Content/Python/setup_master_water.py
```

**Audit:** `Saved/Audit/grand_water_expand.json`

## Japanese ornament textures + themed instances

**Source pack:** `/Game/Textures/70_Japanese_Ornament_Alphas_vfxMed` (52 `JRO_JP_Ornament*` alpha masks).

Wired into `M_Master_Toon_Universal` `MotifMask` / `FairyGlyphMask` defaults via `portfolio_texture_catalog.py` (`JAPANESE_ORNAMENT`).

**Theme instances** (8) — `py Content/Python/apply_theme_instances.py`:

| Folder | Instances |
|--------|-----------|
| `Instances/Environment/Baroque/` | `MI_Baroque_GildedFiligree`, `MI_Baroque_CathedralSurreal`, `MI_Baroque_EscherOrnament`, `MI_Baroque_FiligreeDream` |
| `Instances/Environment/Zen/` | `MI_Zen_MossGarden`, `MI_Zen_InkWash`, `MI_Zen_BambooMist`, `MI_Zen_Karesansui` |

**Audit:** `Saved/Audit/theme_instances.json`
