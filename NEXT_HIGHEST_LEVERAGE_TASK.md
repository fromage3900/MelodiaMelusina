# Project Priority Plan

## Immediate Next Actions (from NEXT_ACTIONS.md)

# Next Actions - Universal Environment Platform

## Current Priority

Build the generic material/look-dev spine without touching `L_SakuraPath`.

## Recently Completed

- Done: Melodia portfolio components deployed - 7 animated components copied into `my-site/melodia-design-system/wix/`.
- Done: Professional editorial index page created - full portfolio layout in `wix/index.html`.
- Done: Deployment manifest updated - v2.0 with component URL inventory.
- Done: Committed to my-site main - commit `3b420dc` (push still requires GitHub connectivity).
- Done: Package-to-website handoff adapter added - `Content/Python/package_to_website_handoff.py` converts `Saved/Portfolio/portfolio_package.json` into `_github_deploy/generated/*_config.json`.
- Done: Material manifest/package refreshed - `material_family_manifest_full.py` handles UTF-8 BOM instance modules; latest package has 30 materials and zero aggregation warnings.

## Queue

1. Push to GitHub when connectivity and approval are available.
   - Current note from prior agents: local website work is ahead of `origin/main`.
   - Do not publish externally without explicit approval.

2. Produce generic look-dev capture pass.
   - Target: `L_Template`, not Sakura.
   - Capture: showcase material grid, landscape slab, water plane, trimsheet panel.

3. Validate Unreal material-system repairs from Kiro.
   - Check universal A/B/C layer combinations compile and behave.
   - Check Nikki landscape scale/normal behavior if `setup_landscape_height_blend.py` is rebuilt.
   - Check water parameter groups after `setup_master_water.py` changes.

4. Decide whether `my-site-clean/` should replace or supplement `_github_deploy/`.
   - `my-site-clean/` is currently an untracked clean clone with generated design-system/technical files.
   - `_github_deploy/` is the active deploy lane used by the Unreal package adapter.

## Completed Pipeline Commands

1. Generate material family manifest.
   - Command: `python Content/Python/material_family_manifest_full.py`
   - Output: `Saved/Portfolio/Materials/material_family_manifest.json`
   - Output: `Saved/Portfolio/MaterialPreviews/previews_manifest.json`
   - Latest result: 30 materials (`Showcase`: 11, `Zen`: 15, `Baroque`: 4)

2. Aggregate portfolio package.
   - Command: `python Content/Python/portfolio_aggregator.py`
   - Output: `Saved/Portfolio/portfolio_package.json`
   - Latest result: `sections_ok=True`, warnings `0`

3. Build package-to-website handoff.
   - Command: `python Content/Python/package_to_website_handoff.py`
   - Input: `Saved/Portfolio/portfolio_package.json`
   - Output: `_github_deploy/generated/hero_config.json`
   - Output: `_github_deploy/generated/passport_config.json`
   - Output: `_github_deploy/generated/portfolio_package_config.json`
   - Output: `_github_deploy/generated/materials_config.json`
   - Output: `_github_deploy/generated/renders_config.json`
   - Output: `_github_deploy/generated/stats_config.json`

4. Add agent memory docs.
   - `Docs/AgentMemory/Decisions.md`
   - `Docs/AgentMemory/RejectedIdeas.md`
   - `Docs/AgentMemory/MaterialStandards.md`

## Portfolio Deployment Status

| Component | Location | Status |
|-----------|----------|--------|
| Portfolio index | `wix/index.html` | Committed locally |
| Cosmic hero | `wix/melodia-hero-cosmic.html` | Committed locally |
| Navigation | `wix/melodia-navigation-constellation.html` | Committed locally |
| Project cards | `wix/melodia-project-card.html` | Committed locally |
| Gallery grid | `wix/melodia-gallery-grid.html` | Committed locally |
| Breakdown cards | `wix/melodia-breakdown-card.html` | Committed locally |
| Section headers | `wix/melodia-section-header.html` | Committed locally |
| Smooth scroll | `wix/melodia-smooth-scroll.html` | Committed locally |
| Hero embed | `wix/melodia-hero-embed.html` | Committed locally |
| Passport embed | `wix/melodia-passport-embed.html` | Committed locally |
| Deployment manifest | `generated/deployment_manifest.json` | Updated locally |
| Package handoff configs | `_github_deploy/generated/*_config.json` | Generated locally |
| Push to GitHub | `origin/main` | Requires connectivity and approval |

## Red-Line Constraints

- Do not edit Sakura level content.
- Do not delete legacy material assets.
- Do not rewrite master material families.
- Do not publish externally without explicit approval.


---

## Ranked P0-P3 Leverage Plan (from NEXT_HIGHEST_LEVERAGE_TASK.md)

# Next Highest-Leverage Task

> 2026-06-25. Derived from [CURRENT_SYSTEM_MAP.md](CURRENT_SYSTEM_MAP.md) + [PORTFOLIO_PIPELINE_AUDIT.md](PORTFOLIO_PIPELINE_AUDIT.md).
> Constraint honored: no new systems, no redesign. This is the *smallest* change to reach a usable package.

## The goal, restated

```
Unreal Scene → portfolio_package.json → usable portfolio output
```

The pipeline already produces a schema-valid `portfolio_package.json` on every run. It is just **empty** (5 of 7 sections null). "Usable" = the package carries a real scene name, a real asset list, and a real hero render. We are one capture away from that.

---

## THE task: make one capture run populate the package

### Step 1 — Fix the stale level path (the single highest-leverage line in the repo)

**File:** `Content/Python/generate_portfolio.py:30`

```python
# before  (asset does not exist → level never loads → all-null capture)
LEVEL = "/Game/EnvSandbox/Levels/L_SakuraPath"

# after   (actual on-disk location)
LEVEL = "/Game/EnvSandbox/Environments/Sakura/L_SakuraPath"
```

This one edit makes `_load_portfolio_level()` actually load the level, which means `scene_metadata_exporter` scans a populated world → `scene.scene_name`, `scene.level_path`, `scene.engine`, and the whole `assets[]` list populate, and `render_exporter` stamps a real level on the hero plate. **Three sections light up from code that already exists.**

> Why this is the smallest change: every downstream stage (layout, render compiler, aggregator, schema) is already correct. The only thing wrong is that the scan target never loads. Fixing the target is one string.

### Step 2 — Harden the level lookup (belt-and-suspenders, ~6 lines)

`scene_metadata_exporter._get_level_info()` and `render_exporter._get_level_slug()` use the **deprecated** `unreal.EditorLevelLibrary.get_editor_world()`. The legacy `capture_scene_metadata.py` already uses the modern call. Mirror it so identity capture is robust even if the deprecated path returns `None` in UE 5.8:

```python
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
```

(Keep the old call as a fallback. `get_all_level_actors()` already uses the modern `EditorActorSubsystem`, so assets populate regardless — this just secures level name/path/engine.)

### Step 3 — Run it and verify

In-editor (recommended; viewport hero works without Monolith):

```
py Content/Python/generate_portfolio.py
```

**Pass criteria** (`Saved/Portfolio/portfolio_package.json`):
- `scene.scene_name == "L_SakuraPath"`, `scene.level_path` non-null, `scene.engine` non-null
- `assets` is a non-empty array
- `renders.hero[0].level == "L_SakuraPath"` (not `"level"` / null)
- `metadata.validation_warnings` count drops (scene/asset warnings gone)

That output is the first genuinely **usable** `portfolio_package.json` — enough to drive a real breakdown page.

---

## Immediate follow-on (small, independent, bundle if cheap)

These are *not* required for "usable" but are the next cheapest wins, in order:

1. **Light up `materials` (~3 small fixes).** `capture_material_previews.py` is orphaned and broken. Fix it, then add one step to `generate_portfolio.py`:
   - add `from datetime import datetime, timezone` (its `main()` currently NameErrors);
   - replace the `endswith((".mat", ".material"))` filter (matches no UE path) with a real material check (e.g. load the asset and test `is_a(unreal.MaterialInterface)`), or scan via the asset registry by class;
   - wire it into the orchestrator: `step("capture_material_previews", previews.capture_and_write)` between scene metadata and renders.
   - Result: `materials[]` populates from `MaterialPreviews/previews_manifest.json`.

2. **Connect the package to Figma (the real end-to-end tail).** Nothing consumes `portfolio_package.json` yet. The smallest connector: have `melodia-figma-plugin/code.js` read the package's `scene`/`assets`/`renders` instead of hardcoded tokens (or add a tiny adapter that maps package → the plugin's existing input shape). This closes the loop the project goal actually describes.

3. **Stats exporter (new producer, larger).** Write `portfolio_stats_manifest.json` (`triangle_count`, `draw_calls`, instance counts). The schema slot and aggregator mapper already exist; only the producer is missing. Defer until 1–2 land.

---

## Explicitly out of scope (do NOT do now)

- ❌ Rewriting the aggregator, schema, or layout manager — they are production-ready.
- ❌ Building the Monolith material-grid / overlay / trim capture suite — skips by default; unblock the spine first.
- ❌ The advanced gaps in `UNREAL_CAPTURE_GAPS.md` / `UNMAPPED_DATA_POINTS.md` (G-buffer passes, LOD metrics, UDS params, audio bands) — backlog, wrong altitude until the package carries basic data.
- ❌ Merging the duplicate scene scanner — nice cleanup, not blocking; do it opportunistically when touching Step 2.

---

## One-line answer

**Change `LEVEL` in `generate_portfolio.py:30` to `/Game/EnvSandbox/Environments/Sakura/L_SakuraPath` and re-run the pipeline in-editor.** That single fix converts the all-null package into a real scene + asset list + hero render — the smallest possible step from "pipeline runs" to "portfolio is usable."

