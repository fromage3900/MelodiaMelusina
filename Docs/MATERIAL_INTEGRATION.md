# Material integration (2026-06-19)

Session summary for portfolio masters, SDF expansion, compositing textures, and editor tooling.

## What landed

| Area | Result |
|------|--------|
| **Universal masters** | `M_Master_Toon_Universal`, `M_Master_SDF_Toon`, `M_Master_Toon_Unified` — 18/18 texture params wired, Substrate Toon, compile OK |
| **MI_Universal_*** | 141 instances, compositing + SDF texture defaults (`/Game/Textures` + `SDF/Textures`) |
| **SDF masters** | All 50 `_PROJECT` `M_SDF_*` ported to `EnvSandbox/Materials/Masters/` (incl. 9 aquatic) |
| **Aquatic instances** | `MI_SDF_AbyssalVent_Deep` … `MI_SDF_ThermalGlow_Vent` under `SDF/Instances/` |
| **Toon conversion** | Batches 1–4 via `run_phase_a_safe.py` (baroque, hybrid, aquatic, math/musical expansion) |
| **Storybook PP** | `M_PP_StorybookVines` + `_Inst` rebuilt; stack after `M_PP_ToonOutline` |
| **Blender Live Link** | Menu: **LiveLink → Start/Stop/Status** (not Window → Live Link); see `BLENDER_LIVELINK.md` |

## Python scripts (run order)

```text
python Content/Python/repair_crash_assets.py
python Content/Python/integrate_compositing_textures.py
python Content/Python/run_phase_a_safe.py
python Content/Python/review_portfolio_masters.py
python Content/Python/run_storybook_rebuild.py
```

Editor one-shot: `py ".../run_editor_integration.py"`

## Headless notes

- Pass `-DisablePlugins=Monolith` (or disable in `.uproject`) — missing `MonolithBABridge` aborts UE-Cmd.
- **Never run** `patch_portfolio_texture_paths.py` / `patch_portfolio_uasset_paths.py` (corrupts uassets).
- Close material tabs before batch saves to avoid Error 32 file locks.

## Audit reports (local, gitignored)

`Saved/Audit/`: `master_review.json`, `compositing_integration.json`, `compositing_texture_defaults.json`, `dead_material_nodes.json`, `ensure_portfolio_instances.json`, `substrate_toon_conversion.json`, `storybook_outline_build.json`

## Not in git

- `/Game/Textures` compositing library (local SBS packs)
- `Content/Python/livelink_unreal.pyc` (3DRedbox client; copy from purchase)
- `Saved/`, `Intermediate/`, audit JSON outputs
