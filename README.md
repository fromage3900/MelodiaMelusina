# Melodia -- Live Collaborative Environment Art Platform

UE 5.8 + Blender 5.1 production platform for real-time Blender<->Unreal level design bridge, procedural geometry generation, automatic material crosswalk, voice-driven NPCs, rhythm combat, and autonomous agent loops.

> **New here?** Start with [QUICKSTART.md](QUICKSTART.md) - Get running in 5 minutes.
>
> **Level designer?** [Sparse checkout guide](Docs/SETUP_COLLAB.md) -- 50 MB clone, not 300 GB.

---

## Quick Start: Choose Your Path

| Path | Time | What You'll Do | For |
|------|------|----------------|-----|
| **Viewer** | 5 min | Open & explore levels | Reviewers, new team members |
| **Geometry** | 10 min | Build & send assets to UE | Level designers, environment artists |
| **Materials** | 15 min | Create & preview materials | Technical artists, shader folks |
| **Full Collaborator** | 30 min | Complete live workflow | Active contributors |

Setup check: `.\deploy\validate_setup.ps1`

---

## Path 1: Viewer Mode (5 min)

**Step 1** -- Install Unreal Engine 5.8 from Epic Games Launcher.

**Step 2** -- Clone & Open:
```bash
git clone https://github.com/fromage3900/environment-portfolio.git
git lfs pull
# Open BS_GodFile.uproject -- wait for shader compilation (5-10 min first run)
```

**Step 3** -- Explore levels:
- `/Game/Melodia/Levels/L_ZenForestTest` (gameplay demo)
- `/Game/EnvSandbox/Levels/L_Template` (neutral testing)
- `/Game/EnvSandbox/Environments/WP/L_WP_SakuraDream` (World Partition demo)

**Step 4** -- Play the demo:
- Open `L_ZenForestTest`, press `Alt+P`
- WASD to move, walk into trigger -> rhythm battle
- Complete 3 stages -> win the demo

---

## Path 2: Geometry Designer (10 min)

**Step 1** -- Install Blender 5.1+ from [blender.org](https://www.blender.org/).

> **Lightweight clone (50 MB, not 300 GB):** You don't need the full UE project.
> ```powershell
> git clone --filter=blob:none --no-checkout https://github.com/fromage3900/environment-portfolio.git MelodiaCollab
> cd MelodiaCollab
> git sparse-checkout init --cone
> git sparse-checkout set deploy/surreal_arch deploy/surreal_world deploy/surreal_os Content/Python/gmm Content/Python/material_lib.py Content/Python/create_zunzun_bps.py Content/Python/import_zundamon.py Content/Python/resolve_material_crosswalk.py Tools Docs README.md
> git checkout
> ```
> Copy `deploy/surreal_arch/` to Blender's addons folder. [Full guide](Docs/SETUP_COLLAB.md)

**Step 2** -- Open both: `BS_GodFile.uproject` (Unreal) + any `.blend` with SurrealArch loaded.

**Step 3** -- Start the bridge: Blender `N`-panel -> Melodia Studio tab -> **Live Bridge** -> **Refresh Status**. You should see `[OK] LiveLink   [ ] BL MCP   [OK] UE MCP`.

**Step 4** -- Connect: Expand "LiveLink :9876" -> **Start Server** -> status: CONNECTED.

**Step 5** -- Generate: Genome Carousel -> pick ZEN_SHRINE -> **Apply**.

**Step 6** -- Send: Material Bridge -> Scan Slots -> Auto-Match -> Live Bridge -> **Send + Materials**.

**Step 7** -- In Unreal: `/Game/LiveLink/` -> drag asset into viewport -> positioned.

---

## Path 3: Material Designer (15 min)

**Step 1** -- Finish Path 1 (Viewer Mode) first.

**Step 2** -- Open `/Game/EnvSandbox/Levels/L_Template` in Unreal.

**Step 3** -- Explore master materials at `/Game/EnvSandbox/Materials/Masters/`:
- `M_Master_Toon_Universal`
- `M_Master_Toon_Landscape_HeightBlend`
- `M_Water_Master_Grand_v6`

**Step 4** -- Right-click any master -> Create Material Instance -> name it -> double-click to edit.

**Step 5** -- Apply to a test object in the level, adjust parameters in real-time.

**Step 6** -- Material preview script (UE Python console):
```python
import capture_material_grid
capture_material_grid.capture_material("/Game/EnvSandbox/Materials/Instances/MI_Test_MyMaterial")
```

---

## Path 4: Full Collaborator (30 min)

**Step 1** -- Complete Paths 1, 2, and 3 first.

**Step 2** -- Install [VOICEVOX](https://voicevox.hiroshiba.jp/) for NPC voices. Launch and verify: `curl http://127.0.0.1:50021/version`

**Step 3** -- Generate NPC voices:
```powershell
cd G:\EnvironmentPortfolio\BS_GodFile\Tools
$env:PYTHONIOENCODING = "utf-8"
python generate_all_voices.py
```
Creates 102 voice files for 7 characters.

**Step 4** -- Create NPC Blueprints (UE Python console):
```python
import create_zunzun_bps; create_zunzun_bps.run()
```

**Step 5** -- Enable Live Sync (Blender Live Bridge -> toggle "Live Sync ON").

**Step 6** -- Full test: Open `L_ZenForestTest`, press `Alt+P`, walk into trigger -> rhythm battle with voiced NPCs -> complete dungeon.

---

## Live Collaborative Bridge

### Verify bridge ports

| Service | Check |
|---------|-------|
| **UE MCP** | `curl http://127.0.0.1:9316/health` -> `{"status":"ok","tools_registered":1325}` |
| **LiveLink** | Blender N-panel -> Melodia Studio -> Live Bridge -> Refresh Status |
| **VOICEVOX** | `curl http://127.0.0.1:50021/version` -> `"0.25.2"` |

### Generate & send workflow

```
  Blender                              Unreal
  ------                               ------
  Genome Carousel -> Apply            Assets appear at /Game/LiveLink/
  Material Bridge -> Auto-Match       Material slots auto-resolved
  Live Bridge -> Send + Materials     Drag into viewport -> geometry live
```

### Two-designer workflow

| Role | Tool | Responsibility |
|------|------|---------------|
| **Geometry Designer** | Blender | Procedural gen, mesh editing, materials, live sync |
| **Level Scripter** | Unreal | Blueprints, encounters, lighting, PCG scatter, NPCs |

### Port map

| Port | Service | Direction |
|------|---------|-----------|
| `9876` | LiveLink -- FBX/texture/animation stream | Blender -> UE |
| `9316` | UE Monolith MCP -- Python execution (1,325 tools) | Any -> UE |
| `9317` | Blender MCP -- genome/agent control | Any -> Blender |
| `50021` | VOICEVOX -- TTS (7 characters) | Any -> VOICEVOX |
| `50022` | Melusina Voice -- custom SBV2 | Any -> Melusina |

### Troubleshooting

| Problem | Fix |
|---------|-----|
| Port 9876 "in use" | Close extra Blender instances (Task Manager) |
| Materials gray in UE | `resolve_material_crosswalk.resolve_all()` |
| Speaker not found in VOICEVOX | Settings -> Manage Voice Libraries -> download |
| PIE crash on encounter | Rebuild MelodiaCore (.dll) |

### Key scripts

| Script | Does | Where |
|--------|------|-------|
| `Tools/setup_zunzun_studio.py` | Import all ZunZun models + studio layout | Blender |
| `Tools/generate_all_voices.py` | Batch-generate 102 NPC voice WAVs | Terminal |
| `Content/Python/import_zundamon.py` | Import Zundamon FBX + materials | UE |
| `Content/Python/create_zunzun_bps.py` | Auto-create 7 NPC BPs + quests/shop/party | UE |
| `Content/Python/resolve_material_crosswalk.py` | Post-import material auto-resolver | UE |
| `deploy/deploy_all.ps1` | Launch all 11 agent loops | Terminal |

Full guide: [Docs/ONBOARDING_LIVE_COLLAB.md](Docs/ONBOARDING_LIVE_COLLAB.md)

---

## Documentation

**Getting started:**
- [QUICKSTART.md](QUICKSTART.md) -- 5-minute setup
- [DOC_INDEX.md](DOC_INDEX.md) -- complete documentation map (68 docs)
- [CURRENT_STATE.md](CURRENT_STATE.md) -- implemented, partial, broken, planned, research

**Workflows:**
- [UNIVERSAL_ENVIRONMENT_PIPELINE.md](UNIVERSAL_ENVIRONMENT_PIPELINE.md) -- generic production flow
- [MATERIAL_LOOKDEV_PIPELINE.md](MATERIAL_LOOKDEV_PIPELINE.md) -- material and look-dev
- [AGENT_OPERATING_MODEL.md](AGENT_OPERATING_MODEL.md) -- recursive agent roles

**Collaboration:**
- [Docs/LEVEL_DESIGNER_ONBOARDING.md](Docs/LEVEL_DESIGNER_ONBOARDING.md) -- level-design workflow
- [Docs/COLLABORATION_WORKFLOW.md](Docs/COLLABORATION_WORKFLOW.md) -- Git/LFS handoff rules

**Status:**
- [PORTFOLIO_READINESS.md](PORTFOLIO_READINESS.md) -- readiness checklist
- [Docs/REPORTS/MELODIA_CONSOLIDATION_2026-07-13.md](Docs/REPORTS/MELODIA_CONSOLIDATION_2026-07-13.md) -- verified/partial/not-started handoff

---

## Current Focus

- Universal material/look-dev workflow centered on `M_Master_Toon_Universal`, `M_Master_Toon_Landscape_HeightBlend`, and `M_Water_Master_Grand_v6`.
- **SDF Material Factory**: 32 Substrate Toon SDF instances across cathedral, cosmo, and landscape families. 24/7 Ollama-powered autonomous generation loop. [Docs/SDF_FACTORY.md](Docs/SDF_FACTORY.md)
- **WP Pillar Levels**: 4 World Partition environments (SakuraDream, SpaceCathedral, BaroqueGrotto, CosmicOrrery) -- production-ready as of 2026-07-09: WP verified, distinct per-pillar displaced terrain, live-verified PCG scatter (2015/642/1085/6171 instances). Rebuild/verify via `setup_wp_pillar_levels.py` (kick + `--verify` in separate calls).
- **24/7 Agent Grid**: 11 autonomous deployable loops with start/stop dashboard. `deploy_all.ps1` launches everything.
- Generic `L_Template` look-dev stage for material, landscape, water, trimsheet, and PCG proof.
- Portfolio package generation from existing manifests and captures.

## Key Systems

- Material architecture: [MATERIAL_PIPELINE.md](MATERIAL_PIPELINE.md)
- Material review: [MATERIAL_SYSTEM_REVIEW.md](MATERIAL_SYSTEM_REVIEW.md)
- Node tree review: [Docs/MATERIAL_NODE_TREE_REVIEW.md](Docs/MATERIAL_NODE_TREE_REVIEW.md)
- Material integration runbook: [Docs/MATERIAL_INTEGRATION.md](Docs/MATERIAL_INTEGRATION.md)
- Portfolio deep review: [Docs/PROJECT_DEEP_REVIEW_2026-07-08.md](Docs/PROJECT_DEEP_REVIEW_2026-07-08.md)
- Ecosystem unification: [Docs/ECOSYSTEM_UNIFICATION_PLAN.md](Docs/ECOSYSTEM_UNIFICATION_PLAN.md)
- Agent ownership: [AGENTS.md](AGENTS.md), [AGENT_BOUNDARIES.md](AGENT_BOUNDARIES.md), [AGENT_OWNERSHIP.md](AGENT_OWNERSHIP.md)

## Generic Package Flow

```
Material/PCG/world systems
  -> L_Template or neutral test map validation
  -> Saved/Portfolio render and metadata fragments
  -> renders_manifest.json
  -> portfolio_package.json
  -> website / Figma / ArtStation handoff metadata
```

## 24/7 Agent Grid

11 autonomous loops managed by a unified deploy system:

```powershell
.\deploy\deploy_all.ps1     # Launch all 11 loops
.\deploy\stop_all.ps1       # Graceful shutdown
.\deploy\loop_status.ps1    # Live dashboard (PID/state per loop)
```

**Blender-side (4):** surreal_micro10, surreal_micro2, surreal_tierb, world_micro10
**UE Python (6):** material_aaa, master_texture, portfolio_orch, specialist_pcg, specialist_terrain, sdf_factory
**Meta (1):** recursive_learner

## SDF Material Catalog

32 Substrate Toon instances parented to `M_Toon_SDF` + `M_Master_SDF_Toon`:

| Family | Count | Examples |
|--------|-------|----------|
| Cathedral/Gothic | 8 | RoseWindow_Radial, GildedTracery_Arched, Altar_GoldFiligree |
| Cosmo/Atmospheric | 6 | Starfield_Dust, Nebula_Veil, Aurora_Band |
| Landscape | 6 | Terrain_Crystal, Grass_Weave, Sand_Leafcool |
| Stylized | 6 | RosyQuartz, CelestialVinyl, TealCeramic, VoidStarlight |
| Base | 5 | Wall, Floor, Accent, Rim, Ornamental |

Nikki-reviewed: 6 drop-in ready, 16 adaptable with parameter tuning.
See [NEXT_HIGHEST_LEVERAGE_TASK.md](NEXT_HIGHEST_LEVERAGE_TASK.md) for the Nikki scorecard.

Do not automate final Sakura level art direction. `L_SakuraPath` is a human-owned art pass. The platform may provide capture tools, material manifests, PCG standards, and generic look-dev support, but it should not replace the human composition pass.
