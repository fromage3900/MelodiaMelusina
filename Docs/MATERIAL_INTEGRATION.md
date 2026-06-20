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
| **Nikki** | Pastel lift, rim, sparkle, iridescence, bloom, fabric sheen |
| **Celestial** | Constellation stars, **nebula wash**, galaxy core (procedural) |
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
| `MI_Show_StoneCliff` | Stone | Triplanar cliff + macro/detail layering | `TriplanarTiling`, `MacroVariationStrength`, `DetailTiling` |
| `MI_Show_CherryBlossom` | Flower shadow | Projected petal shadows + sparkle on soft pink | `ShadowFlowerStrength`, `ShadowFlowerScale` (FlowerShadow) |
| `MI_Show_CelestialNebula` | Nebula | Constellation ramp + procedural nebula + galaxy emissive | `CelestialNebulaStrength`, `ConstellationRamp*` (Celestial) |
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
  -DisablePlugins=Monolith -unattended -nullrhi
```

Editor one-shot: `py ".../run_editor_integration.py"`

## Headless notes

- Pass `-DisablePlugins=Monolith` (or disable in `.uproject`) — missing `MonolithBABridge` aborts UE-Cmd.
- **Never run** `patch_portfolio_texture_paths.py` / `patch_portfolio_uasset_paths.py` (corrupts uassets).
- Close material tabs before batch saves to avoid Error 32 file locks.

## Audit reports (local, gitignored)

`Saved/Audit/`: `master_review.json`, `master_texture_loop.json`, `compositing_integration.json`, `compositing_texture_defaults.json`, `starter_instances.json`, `dead_material_nodes.json`, `ensure_portfolio_instances.json`, `substrate_toon_conversion.json`, `storybook_outline_build.json`

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
