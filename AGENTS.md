# Multi-Agent Production Framework — Environment Portfolio Platform

This document defines the roles, ownership boundaries, communication protocols, and execution loops for the multi-agent production team responsible for building the **Environment Portfolio Platform** in Unreal Engine 5.8, Blender 5.1, and TouchDesigner 2025+.

> **Update 2026-07-15:** Added 6th agent — TouchDesigner Orchestrator Agent (TOA). See `Docs/TOUCHDESIGNER_MCP_INTEGRATION_PLAN.md` for full integration architecture.

---

## 1. Agent Personas & Specializations

To ensure clean execution, the multi-agent team is divided into six specialized personas. Each agent possesses a specific skill set, tool configurations, and system boundaries.

```
                   ┌───────────────────────────────┐
                   │      QA & SENTINEL AGENT      │
                   │   Audits, validation, status  │
                   └───────────────┬───────────────┘
                                   │
         ┌─────────────────────────┼──────────────────────────┐
         ▼                         ▼                          ▼
┌─────────────────┐   ┌───────────────────────┐   ┌─────────────────┐
│  GEOMETRY AGENT │   │ TD ORCHESTRATOR AGENT │   │ PLACEMENT AGENT │
│   Blender OS,   │   │ Real-time FX, Audio,  │   │   Unreal PCG,   │
│ Style Genomes   │   │ MCP Unification, OSC  │   │  PCGEx scatter  │
└────────┬────────┘   └───────────┬───────────┘   └─────────────────┘
         │                        │
         │      ┌─────────────────┴─────────────┐
         │      ▼                               ▼
         │ ┌─────────────────┐   ┌───────────────────────────┐
         │ │  MATERIAL AGENT │   │     INTEGRATION AGENT     │
         │ │ Masters, PBR,   │   │   Live Link, HISM Import  │
         │ │ Material Maker  │   │   OSC, Spout, NDI bridges │
         │ └────────┬────────┘   └───────────────────────────┘
         │          │
         └──────────┘
```

### 1.1 Procedural Geometry Agent (PGA)
*   **Role**: Procedural Architect & Systems Designer (Blender).
*   **Specialization**: Core asset generation, modular kit snapping, grammatical axis creation, and non-Euclidean transforms.
*   **System Ownership**:
    *   Blender generation core: [surreal_architecture_gen.py](file:///g:/EnvironmentPortfolio/BS_GodFile/deploy/surreal_architecture_gen.py)
    *   Style genomes & schema definitions: [deploy/surreal_os/](file:///g:/EnvironmentPortfolio/BS_GodFile/deploy/surreal_os/)
    *   Blender primitives & mesh utilities: [deploy/surreal_greybox/](file:///g:/EnvironmentPortfolio/BS_GodFile/deploy/surreal_greybox/)
    *   Architectural studies & research: [research/](file:///g:/EnvironmentPortfolio/BS_GodFile/research/)
*   **Tooling**: Blender 5.1 Python API, YAML/JSON parsing libraries, mesh topology analysis.

### 1.2 Material Pipeline Agent (MPA)
*   **Role**: Technical Material Artist & Shader Engineer (Unreal Engine & Material Maker).
*   **Specialization**: Substrate Toon conversion, master material node tree wiring, triplanar mapping, temporal visual effects, and procedural PBR generation.
*   **System Ownership**:
    *   Universal surface master & script: [setup_master_universal.py](file:///g:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_master_universal.py)
    *   Landscape master & script: [setup_landscape_height_blend.py](file:///g:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_landscape_height_blend.py)
    *   Water master & script: [setup_master_water.py](file:///g:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_master_water.py)
    *   Impressionist master & script: [setup_impressionist_materials.py](file:///g:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_impressionist_materials.py)
    *   Material Maker graphs & Python builders: [Tools/MaterialMaker/](file:///g:/EnvironmentPortfolio/BS_GodFile/Tools/MaterialMaker/)
    *   Material function generator library: [setup_material_functions.py](file:///g:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_material_functions.py)
    *   Substrate Toon profile presets: `/Game/EnvSandbox/Materials/ToonProfiles/`
*   **Tooling**: Unreal Engine Material Graph Python API (`unreal.MaterialEditingLibrary`), Material Maker `.ptex` graph compiler.

### 1.3 Procedural Placement Agent (PPA)
*   **Role**: Environment Scatter Specialist (Unreal Engine).
*   **Specialization**: PCG graph construction, PCGEx integration, density-falloff systems, and salvage of legacy assets.
*   **System Ownership**:
    *   PCG builder API: [pcg_graph_builder.py](file:///g:/EnvironmentPortfolio/BS_GodFile/Content/Python/pcg_graph_builder.py)
    *   PCG standards & paths: [pcg_portfolio_standards.py](file:///g:/EnvironmentPortfolio/BS_GodFile/Content/Python/pcg_portfolio_standards.py)
    *   Universal scatter graphs: `/Game/EnvSandbox/PCG/Graphs/Universal/`
    *   Style wrappers & builders: [setup_pcg_universal.py](file:///g:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_pcg_universal.py), [setup_pcg_sakura.py](file:///g:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_pcg_sakura.py)
    *   Melodia salvage mapping: `/Game/_PROJECT/PCG/`
*   **Tooling**: Unreal Engine PCG & PCGEx C++/Python API, point-cloud operations, volume/spline samplers.

### 1.4 World Integration Agent (WIA)
*   **Role**: Pipeline & Tools Engineer (Blender & Unreal Engine).
*   **Specialization**: Coordinate space transformations, Live Link networking, instancing optimization, and manifest parsing.
*   **System Ownership**:
    *   Live Link connection controller: [livelink_unreal.pyc](file:///g:/EnvironmentPortfolio/BS_GodFile/Content/Python/livelink_unreal.pyc)
    *   Editor startup integration: [init_unreal.py](file:///g:/EnvironmentPortfolio/BS_GodFile/Content/Python/init_unreal.py)
    *   World manifest importer: [import_world_manifest.py](file:///g:/EnvironmentPortfolio/BS_GodFile/Content/Python/import_world_manifest.py)
    *   Blender Live Link addon: [Tools/BlenderLiveLink/](file:///g:/EnvironmentPortfolio/BS_GodFile/Tools/BlenderLiveLink/)
    *   World export compiler: `deploy/surreal_world/export.py`
*   **Tooling**: Socket communication (TCP/UDP), FBX automated import scripts, HISM (Hierarchical Instanced Static Mesh) spawn interfaces.

### 1.5 QA & Sentinel Agent (SQA)
*   **Role**: Build & Release Engineer / Quality Assurance.
*   **Specialization**: Automated test execution, database verification, naming rule enforcement, and dead reference pruning.
*   **System Ownership**:
    *   Verification orchestrators: [run_verify.ps1](file:///g:/EnvironmentPortfolio/BS_GodFile/deploy/run_verify.ps1), [_mcp_verify_world.py](file:///g:/EnvironmentPortfolio/BS_GodFile/deploy/_mcp_verify_world.py)
    *   Asset audit scripts: `Content/Python/audit_*.py`
    *   Redirector and path patchers: [fix_migration_redirectors.py](file:///g:/EnvironmentPortfolio/BS_GodFile/Content/Python/fix_migration_redirectors.py), [fix_pcg_dead_systems.py](file:///g:/EnvironmentPortfolio/BS_GodFile/Content/Python/fix_pcg_dead_systems.py)
*   **Tooling**: Command-line verification runners (`UnrealEditor-Cmd.exe`), JSON report diffing, and dependency validation interfaces.

### 1.6 TouchDesigner Orchestrator Agent (TOA)
*   **Role**: Real-Time Interaction & MCP Unification Specialist.
*   **Specialization**: TouchDesigner network architecture, audio-reactive visual design, real-time GLSL shader prototyping, multi-DCC MCP orchestration (Embody/Envoy + Monolith + Blender MCP).
*   **System Ownership**:
    *   TD project files: `_TouchDesigner/*.toe`, `_TouchDesigner/components/*.tox`
    *   TDN-exported networks: `_TouchDesigner/networks/*.tdn`
    *   OSC routing schema: `BS_GodFile/deploy/osc_routing.json`
    *   UE↔TD bridge script: `BS_GodFile/Content/Python/td_bridge.py`
    *   GLSL shader prototypes: `_AssetLibrary/TD_Shaders/`
*   **Tooling**: TouchDesigner 2025.32820+ (Commercial license), Embody/Envoy MCP (53 tools on `localhost:9870`), OSC protocol, Spout SDK, GLSL, Python 3.11 (`td` module), NDI.
*   **Integration Plan**: See `Docs/TOUCHDESIGNER_MCP_INTEGRATION_PLAN.md` for full architecture, phase planning, and risk analysis.

---

## 2. Ownership Boundaries

Agents must respect ownership domains. Modifying files outside of an agent's designated system requires coordination or explicit API integration.

| File Path Prefix / Directory | Primary Owner | Read Access | Write Access | Action Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `g:/.../BS_GodFile/Source/` | *Core Engine* | All Agents | None | **Do not modify** (handled by manual build) |
| `g:/.../BS_GodFile/Config/` | *Core Engine* | All Agents | MPA / WIA | Only for Project settings (`DefaultEngine.ini`) |
| `g:/.../BS_GodFile/deploy/surreal_os/` | **PGA** | WIA / SQA | **PGA** | Modifying genome requires updating taxonomy |
| `g:/.../BS_GodFile/deploy/surreal_world/` | **WIA** | PGA / SQA | **WIA** | Schema changes must update import script |
| `g:/.../BS_GodFile/Content/Python/` (Material) | **MPA** | SQA | **MPA** | Node changes must keep output pins unchanged |
| `g:/.../BS_GodFile/Content/Python/` (PCG) | **PPA** | SQA | **PPA** | Standard tags must remain backward-compatible |
| `g:/.../BS_GodFile/Tools/MaterialMaker/` | **MPA** | PGA | **MPA** | Texture dimensions must be power-of-two |
| `g:/.../_TouchDesigner/` | **TOA** | All Agents | **TOA** | Networks must be TDN-exported before commit |
| `g:/.../_TouchDesigner/networks/` | **TOA** | All Agents | **TOA** | .tdn files are git-tracked; diff before merge |
| `g:/.../_AssetLibrary/TD_Shaders/` | **TOA** | MPA, PGA | **TOA** | GLSL must compile in both TD and UE |
| `g:/.../BS_GodFile/deploy/osc_routing.json` | **TOA** | WIA, SQA | **TOA, WIA** | Schema changes require SQA approval |
| `g:/.../BS_GodFile/Content/Python/td_bridge.py` | **TOA** | WIA | **TOA, WIA** | Must handle connection loss gracefully |
| `g:/.../BS_GodFile/Docs/` | **All Agents** | All Agents | All Agents | Append only, preserve history |

---

## 3. Communication Protocols & Contracts

Agents communicate via structured file formats, ports, and logical metadata mappings.

### 3.1 World Manifest Contract (`surreal_arch_world_v1`)
*   **Publisher**: **PGA** (via Blender addon export).
*   **Subscriber**: **WIA** (via `import_world_manifest.py`).
*   **Data Structure**: JSON file `{WorldRoot}.world.json`.
*   **Coordinate Standard**: Blender Z-Up (Matrix 4x4, meters) converted to UE Left-Handed Z-Up (cm) by WIA.

### 3.2 Material Mapping Interface (`ROLE_UE_HINTS`)
*   **Definition**: `deploy/surreal_world/export.py` contains mapping from structural role to EnvSandbox material instance paths.
*   **Contract**:
    *   **PGA** assigns roles (`large`, `medium`, `wall`, `sacred`) to generated geometries.
    *   **MPA** guarantees that matching target material instances (`MI_Show_StoneCliff`, `MI_Trimsheet_HeavyWear`, `MI_Zen_Karesansui`) exist, compile, and use the correct Substrate Toon parameters.

### 3.3 Live Link Connection Protocol
*   **TCP/IP Port**: Default port `55557` (established by UnrealMCP/livelink client).
*   **Payload Format**: JSON command packets containing mesh name, transform vectors, snap indices, and export path cues.

### 3.4 Audit & Status Reports
*   **Output Directory**: `/Saved/Audit/` inside the project folder.
*   **File Format**: `{system}_audit.json`.
*   **Usage**: **SQA** writes status; other agents read these files to identify dead systems, unassigned materials, or missing assets before running their cycles.

### 3.5 OSC Routing Contract (`osc_routing_v1`)
*   **Publisher**: **TOA** (via `osc_routing.json` schema definition).
*   **Subscribers**: **PGA** (Blender NodeOSC), **WIA** (UE OSC Plugin), **MPA** (UE material params).
*   **Data Structure**: JSON file `BS_GodFile/deploy/osc_routing.json`.
*   **Routes**:
    *   `/melusina/pitch` (float) — VoiceSynth pitch → UE shader warp
    *   `/melusina/amp` (float) — VoiceSynth amplitude → UE particle spawn rate
    *   `/melusina/formants` (float[5]) — Formant data → TD particle palette
    *   `/material/toon` (float[12]) — TD → UE Substrate Toon parameter group
    *   `/material/preset` (int 0-4) — Style preset selector (Nikki/Madoka/Celestial/Itto/Sakura)
    *   `/time/cycle` (float 0-1) — Day/night cycle position
    *   `/time/beat` (float 0-1) — Beat-sync clock
    *   `/ue/camera` (float[16]) — UE camera matrix → TD
    *   `/td/camera` (float[16]) — TD camera matrix → UE

### 3.6 Spout Stream Registry
*   **Publisher**: **TOA** (TD Spout Out TOP) / **WIA** (UE SpoutSender).
*   **Subscribers**: All agents.
*   **Streams**:
    *   `TD_ShaderPreview` — TD TOP → UE (1920x1080, RGBA8)
    *   `UE_RenderTarget` — UE → TD (variable, RGBA16F)
    *   `Blender_Viewport` — Blender → TD (variable, RGBA8)

### 3.7 MCP Unification Contract
*   **Servers**: Envoy (`localhost:9870`), Monolith (`localhost:9316`), Blender MCP (`localhost:9877`).
*   **Configuration**: `.mcp.json` at project root registers all three servers.
*   **Session Management**: Envoy provides `claim_scope` / `release_scope` for multi-agent coordination.
*   **Usage**: AI agents query all three tools in a single session; TOA coordinates cross-tool workflows.

---

## 4. Coordination Framework & Autonomous Loops

Agents run in periodic loops managed by PowerShell sentinel runners.

```text
[Loop Runner] ──► [SQA Check] ──► [PGA Generator] ──► [TOA Audio/OSC] ──► [WIA Importer] ──► [MPA Builder] ──► [SQA Verification]
       ▲                                                                                                       │
       └─────────────────────────────────── Next Cycle ────────────────────────────────────────────────────────┘
```

1.  **Triggering Loop Cycles**:
    *   `start_surreal_loop.ps1` runs the **PGA** cycle (Interval: 120s) with sentinel `AGENT_LOOP_TICK_surreal_tierb`.
    *   `start_td_loop.ps1` runs the **TOA** cycle (Interval: 60s) with sentinel `AGENT_LOOP_TICK_td_orch` — handles audio analysis, OSC routing, and Spout stream health.
    *   `start_world_loop.ps1` runs the **WIA** cycle (Interval: 600s) with sentinel `AGENT_LOOP_TICK_world_micro10`.
    *   `run_material_aaa_loop_tick.py` runs the **MPA** cycle (Interval: 15m) with sentinel `AGENT_LOOP_WAKE_material_aaa`.
2.  **Safety Interlocks**:
    *   If **SQA** verification fails (`run_verify.ps1` returns non-zero), the loops halt immediately, creating a `*_LOOP_STOP` file on disk. No agent can publish changes until the block is resolved.
    *   No file writes to `Content/_PROJECT/` are permitted. All ports and exports must target `/Game/EnvSandbox/` or `deploy/`.

---

## 5. Recursive Learner Agent (RLA)

*Introduced in v0.1.0 — branch `feature/recursive-learner`*

A meta-agent that autonomously reads, analyzes, and improves the UE Python utility scripts (`Content/Python/`) using local LLMs via Ollama. All generated code passes through human review before execution.

### 5.1 Role

*   **Role**: Self-Improving Code Automation Specialist.
*   **Specialization**: Reads audit outputs, dependency graphs, and loop state files; uses local LLMs to generate targeted improvements to existing Python scripts or create new ones.
*   **System Boundaries**:
    *   Write access: `Content/Python/` (only after human approval via staging queue)
    *   Read access: `Saved/Audit/`, `Saved/Analysis/`, `Saved/Memory/`, `Content/Python/`, `learner/`
    *   Never modifies: `Source/`, `Config/`, `deploy/surreal_os/`, `deploy/surreal_world/`, asset files (`.uasset`)

### 5.2 Architecture

```
learner/
├── config.yaml                    # Ollama model config, execution paths, circuit breakers
├── model_router.py                # Ollama API abstraction, model selection by task type
├── code_analyzer.py               # AST-based script map, dependency graph, gap analysis
├── memory.py                      # Persistent tick history, model perf, circuit breaker state
├── plan_engine.py                 # Target ranking (impact, fragility, freshness, feasibility)
├── code_generator.py              # Ollama prompt builder with codebase context injection
├── staging.py                     # Human review queue (approve/reject/edit workflow)
├── ue_executor.py                 # Headless UE (UnrealEditor-Cmd.exe) + MCP (port 9316) execution
├── verifier.py                    # Post-execution audit check, banned-pattern scan, syntax verify
└── run_recursive_learner.py       # Main loop entry point (single tick or --loop)
```

### 5.3 Loop Cycle (9 Steps)

```
[DISCOVER] → [ANALYZE] → [PLAN] → [GENERATE] → [STAGE] → [CHECK] → [EXECUTE] → [VERIFY] → [LEARN]
     ↑                                                                                       │
     └─────────────────────────── Next Tick ────────────────────────────────────────────────┘
```

1.  **DISCOVER** — `code_analyzer.py` scans `Content/Python/`, builds dependency graph, classifies 177+ scripts into 29 system categories.
2.  **ANALYZE** — Reads `Saved/Memory/` (past tick results), `Saved/Audit/` (loop state files), circuit breaker status.
3.  **PLAN** — `plan_engine.py` scores each script by impact (dependents), fragility (failure rate), freshness (time since last attempt), feasibility (complexity). Returns ranked targets.
4.  **GENERATE** — `code_generator.py` builds an Ollama prompt with target script content + reference libraries + schemas. Model (deepseek-coder / codellama) returns improved code.
5.  **STAGE** — Generated code written to `_staging/learner_generated/tick_NNNN/` with metadata. Human must review.
6.  **CHECK** — On subsequent ticks, scans staging queue for approved items.
7.  **EXECUTE** — Two paths: **MCP** (`localhost:9316`, when editor is running) or **Headless** (`UnrealEditor-Cmd.exe -nullrhi`). 28 MCP tools available.
8.  **VERIFY** — Checks exit code, audit JSON pass/fail, banned `/Engine/` references, error lines in logs.
9.  **LEARN** — Records success/failure per target, tracks model performance per task type, engages circuit breaker after 3 consecutive failures (24h cooldown).

### 5.4 Local Models (Ollama)

| Task | Primary Model | Fallback Model |
|------|--------------|----------------|
| Code Generation | `deepseek-coder:6.7b` | `codellama:7b` |
| Code Review | `llama3:8b` | `qwen2.5:7b` |
| Planning | `llama3:8b` | `mixtral:8x7b` |
| Analysis | `deepseek-coder:6.7b` | `codellama:7b` |

Configured in `learner/config.yaml`.

### 5.5 Commands

| Action | Command |
|--------|---------|
| Manual tick | `python learner/run_recursive_learner.py` |
| Continuous loop | `python learner/run_recursive_learner.py --loop` |
| Detached loop | `deploy/start_recursive_learner.ps1` |
| Stop loop | `deploy/stop_recursive_learner.ps1` |
| Analysis only | `python learner/run_recursive_learner.py --analyze-only` |
| List pending | `python learner/run_recursive_learner.py --list-pending` |
| Approve tick | `python learner/run_recursive_learner.py --approve N [--feedback "note"]` |
| Reject tick | `python learner/run_recursive_learner.py --reject N --feedback "reason"` |
| Test Ollama | `python learner/run_recursive_learner.py --test-ollama` |
| Test MCP | `python learner/run_recursive_learner.py --test-mcp` |

### 5.6 Safety & Circuit Breakers

*   **Staging gate**: All generated code lands in `_staging/learner_generated/`. Human approval required before any write to `Content/Python/`.
*   **Circuit breaker**: 3 consecutive failures on the same target → 24h cooldown.
*   **Banned pattern detection**: Verifier rejects code containing `/Engine/` texture references.
*   **Rollback support**: Every staged tick includes the full generated code, diff summary, and model reasoning.
*   **Rate limiting**: 1 script per tick max, 24 scripts per day max (configurable in `config.yaml`).

---

## Anchored Summary

### Objective
Complete GN overhaul: fix all crash bugs, build composable `melodia_gn/` library (gazebo-style circular array + instance on spline), integrate as stackable Bagapie-like modifier system in Melodia Studio, then continue UI re-theme.

### Completed Changes (Current Session — 2026-07-11)

| Change | Description | Files |
|--------|------------|-------|
| **P0 Ghost Fixes** | Category → `"Melodia Studio"` (7 panels + genome_carousel + tutorial); tutorial persists via WindowManager BoolProperty; `bl_order=99`; orphan operators uncommented; `accessory_toggles` wired to `hide_viewport`/`hide_render`; `icon_loader.py` — Figma icon loader helper | `ui.py`, `genome_carousel.py`, `tutorial.py`, `integration.py`, `icon_loader.py` |
| **GN0-B1..B7 (6/7 crash bugs)** | Higgsas `_HIGGSAS_LIB_PATH`→`library_path()`, `_HIGGSAS_ARCH_NODES`→`HIGGSAS_ARCH_NODES`, `_higg_load`→`load_node()`; 9 dead Synthia operators uncommented; hardcoded `_KOMIKAZE_BLEND_PATH`→Preferences StringProperty; `_DEFAULT_HIGGSAS` import fixed | `surreal_architecture_gen.py`, `capabilities.py`, `bootstrap.py` |
| **melodia_gn/ package scaffold** | 7 files: `core.py` (safe_node, link_sockets, color_node, param helpers, TREE_TYPES, GROUP_BUILDERS), `primitives.py` (circular_array, linear_array, grid_array, bounding_box, instance_on_spline), `profiles.py` (column, baluster, post, rail, star_finial, lissajous_curve), `math_ops.py` (add/subtract geometry, power_scale, exponent_blend, store_named_attr, attribute_math), `structures.py` (gazebo, arch, portico), `stack.py` (CollectionProperty stack model + N-panel UI + add/remove/move/clear operators), `bake.py` (bake_all, save_library, load_library) | `deploy/surreal_arch/melodia_gn/*.py` |
| **All files py_compile clean** | Verified via `python -m py_compile` | All edited files |
| **Sync script** | `sync_surreal_to_live.ps1` updated to push SSOT to live Blender 5.1 addon dir | `deploy/sync_surreal_to_live.ps1` |

### Pending
- **GN0-B5**: 40 orphan param specs (~200 lines plumbing) — deferred
- **Wire melodia_gn into integration.py + Melodia Studio N-panel tab**
- **Sync to live addon dir + test** (Blender MCP on 9877 not responding — need user to verify)
- Convert magic effects from legacy modifiers to GN
- Fix Sverchok flicker

### Key Technical Constraints
| Constraint | Impact | Workaround |
|-----------|--------|------------|
| Blender MCP ports 9877/9317 not responding | Cannot run code in Blender remotely | User must enable addon + start MCP manually |
| Blender LiveLink on port 9876 (HTTP) | Read-only GET endpoints, no Python execution | Merge/restart check only |
| Edit SSOT is `G:\EnvironmentPortfolio\BS_GodFile\deploy\` | Sync to live dir required | `sync_surreal_to_live.ps1` |
| Target Blender 5.1 at `C:\Users\froma\AppData\Roaming\Blender Foundation\Blender\5.1\scripts\addons\` | Must match exact path | Verified directory exists |
| UI category = "Melodia Studio" | Replaces "Surreal" and "SurrealArch" | Updated in 7+ panels |

### Next Moves
1. Wire melodia_gn into `integration.py` (register CLASSES, register_props, stack panel)
2. Sync to live addon dir, test via `py_compile` + Blender MCP if available
3. GN0-B5: 40 orphan param specs
4. Build GN library .blend via `bake.bake_all()`
5. Convert magic effects → GN
6. Sverchok flicker fix
