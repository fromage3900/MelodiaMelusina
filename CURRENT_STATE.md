# Current State - Universal Environment Platform

Status labels: `Implemented`, `Partial`, `Broken`, `Planned`, `Research`, `Deprecated`.

## Escher room generators: now 6 total (2 more added 2026-07-02 near dawn)

`Content/Python/build_escher_relativity_room.py` (name is historical, module now covers all 6). Added `build_belvedere()` and `build_waterfall()`, translating `build_gb_escher_belvedere`/`build_gb_escher_waterfall` from the Blender addon — Escher's two most iconic impossible-structure pieces (Belvedere 1958, Waterfall 1961), previously read this session but not yet ported. Both live-verified via the proven spawn/generate/count-in-separate-call pattern: `PCG_EscherBelvedere` 17 instances, `PCG_EscherWaterfall` 16 instances, both exactly matching build output, no crash. Full set: Relativity Room, Penrose Loop, Recursive Room, Gravity Shift Corridor, Belvedere, Waterfall — all in `/Game/EnvSandbox/PCG/Styles/Escher/`, all built from real translated transform math, not hand-placed test points.

## PLAN STEP 3 SCOPING 2026-07-02 (overnight): `AncientTempleRuins` migration needs a different script pattern than `migrate_props_from_source.py`

Inspected `G:/ueprojects/Shepherd_Brennan_10/Content/AncientTempleRuins/` structure: it's organized by **asset type** (`Blueprints/`, `Materials/`, `Textures/`, `Environment/{Construction,Foliage,GroundScatter,Prop,Rock}/`), not by **self-contained per-prop subfolder** like `migrate_props_from_source.py`'s existing `SOURCES` (MagiciansLibrary, Melodia) assume. That script's material-slot repair heuristic ("if a copied subfolder has exactly 1 material, reassign every mesh's slots to it") doesn't apply here — meshes and their materials live in separate top-level folders with many-to-many relationships, not a 1-mesh-1-material-per-folder pattern.

Migrating this correctly needs: (1) raw-copy `Materials/`, `Textures/`, and all of `Environment/*` together (not per-subfolder), (2) a different repair pass that resolves each mesh's actual per-slot material reference (not just "the 1 material in this folder") — likely by reading each source `.uasset`'s dependency list via `AssetRegistryHelpers` before copying, then remapping paths post-copy rather than guessing from folder co-location. Not attempted tonight — a broken migration would produce assets with silently-wrong materials I can't visually verify without the user, and is worse than not migrating at all. Real next step, scoped precisely, not just "do the migration."

## PLAN STEP 2 FINDING 2026-07-02 (overnight, `Broken`, honest report before any fix attempt): `PCG_FractalButtress_BS` and `PCG_M1_GrammarNave_BS` are NOT working recursive/grammar systems — they're scaffolded placeholders

Live-inspected both (safe, static node/property reads, no generate calls needed):

- **`PCG_M1_GrammarNave_BS`** (12 nodes: `PCGCreatePointsSettings → PCGSubdivideSegmentSettings → 5x PCGAttributeFilteringSettings → 5x PCGStaticMeshSpawnerSettings`): the shape looks like real architectural grammar (a spine, subdivided into segments, routed by attribute filters to 5 different element-type spawners) — but the `PCGCreatePointsSettings` source has **only 1 point** (not a spine), and **4 of the 5 `PCGStaticMeshSpawnerSettings` nodes have no mesh assigned (`None`)**. Only 1 of 5 has a mesh, and it's `/Engine/BasicShapes/Sphere` — an engine primitive placeholder, not real content.
- **`PCG_FractalButtress_BS`** (4 nodes: `PCGCreatePointsSettings → PCGSubdivideSegmentSettings → PCGAttributeFilteringSettings → PCGStaticMeshSpawnerSettings`): same pattern — single seed point (no actual recursive/self-similar subdivision visible), 1 spawner using `/Engine/BasicShapes/Cylinder`, another placeholder primitive.

**Conclusion: the "grammar"/"fractal" naming reflects design intent, not implemented behavior.** This is NOT the genuine massive-scale recursion lever the plan hoped for — it's an early scaffold (single-point source, mostly-unwired spawners, placeholder primitive meshes) that was never finished. Building a real self-similar/recursive architectural generator here would be new work, not a fix — a good candidate for a dedicated focused session (ideally leaning on the math-translation technique already proven with the 4 Escher room generators) rather than a late-night patch. Not attempted tonight; flagging honestly per the plan's Step 2 instruction to report the traced structure before proposing changes.

## RESOLVED 2026-07-02 (overnight): unattended-boot hang was TWO stacked issues, both fixed

The editor appeared to "crash on relaunch" repeatedly overnight, but the real problem for most of the night was a **hang**, not a crash: process alive, memory flat, log frozen — not the PCGExCreateShapes bug (that only fires when a Baroque graph is generated, and boot never got that far).

1. **`GaeaUnrealTools` plugin version mismatch** (built for 5.7.0, project runs 5.8) logs a warning right before the hang point every time. Fixed: disabled it in `BS_GodFile.uproject` (`"Enabled": false`).
2. **A second, separate blocking modal** (`LogMonolith: Warning: MODAL_OPEN ... title='' text=''`) opens immediately after `LogInit: Display: Engine is initialized` — Monolith itself logs this and confirms MCP is unresponsive until dismissed, which is exactly the observed symptom (frozen log/memory, `monolith_status` failing). With no one at the keyboard overnight, this blocked every relaunch after the Gaea fix too.

**Fix: launch with the `-unattended` command-line flag**, which auto-dismisses blocking modal dialogs. Confirmed working — `monolith_status` responded immediately after an `-unattended` launch where every prior relaunch attempt (via `cmd.exe /c start`, direct exe, and PowerShell `Start-Process` without the flag) hung indefinitely.

**Going forward, always launch this project as:**
```powershell
Start-Process -FilePath "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe" -ArgumentList '"G:\EnvironmentPortfolio\BS_GodFile\BS_GodFile.uproject"','-unattended' -PassThru
```
via the PowerShell tool (not Bash's `cmd.exe /c start`, which did not reliably produce a surviving process in this environment — verify with `Get-Process -Id $p.Id`, not just `tasklist`, immediately after).

## CRASH BUG FOUND 2026-07-02 (overnight, `Broken`): one of the 9 Baroque `*Ex` graphs contains a `PCGExCreateShapes` node that hard-crashes the engine on generate

Root-caused via log inspection (`Saved/Logs/BS_GodFile.log`) after two consecutive editor crashes during the Step 1 batch-verification sweep. Crash signature: native C++ crash (unrecoverable from Python, `try/except` does not help) inside `UnrealEditor-PCGExElementsShapes.dll!PCGExCreateShapes::FProcessor::OutputPerSeed()` → `PCGExPointArrayDataHelpers::SetNumPointsAllocated()` — a background-worker-thread crash during `ParallelFor`, consistent with a bad/negative point count being requested by a `PCGExCreateShapes` node. Timestamp of the crash lines up exactly with the batch-spawn-and-generate script that triggered all 9 `TEST_Baroque_*Ex` actors in one shot (`AtriumEx/BalconyEx/ColonnadeEx/CorniceEx/FacadeEx/NaveVaultEx/PilasterEx/RotundaEx/EntryEx`) — meaning **one of these 9 graphs, not yet identified, contains the crashing node**.

**Do not batch-generate these 9 graphs again.** Test them ONE AT A TIME with an editor-status check between each (`monolith_status`), so a crash can be attributed to the specific graph instead of taking down the whole batch. Once identified, either delete/disable the `PCGExCreateShapes` node in that graph or replace it with a vanilla `PCGCreatePointsSettings` node (the pattern already proven working in the Escher `*Ex` fixes and the 4 new Escher room generators).

`GothicCorridorEx`'s real path resolved: `/Game/EnvSandbox/PCG/Styles/Baroque/PCG_GothicCorridorEx` (no `Baroque` prefix, unlike its 9 siblings).

**Step 1 (Baroque `*Ex` sweep) complete, live-verified, all 10 graphs:**
- **Risky (contains `PCGExCreateShapesSettings`, NOT generated this session, avoid batch-testing)**: `AtriumEx`, `ColonnadeEx`, `FacadeEx`, `RotundaEx` — all 4 share the same `PCGVolumeSamplerSettings → PCGExCreateShapesSettings → PCGExCreateShapeGridSettings → ... → PCGSubgraphSettings` shape. One (unidentified which) of these 4 is confirmed to hard-crash the engine on generate.
- **Safe, tested, 0 instances (need a spline/path input — same root cause as the ~13 Bezier-blocked graphs elsewhere, not yet fixed)**: `BalconyEx`, `CorniceEx`, `NaveVaultEx`, `PilasterEx`, `GothicCorridorEx` — all use `PCGExSplineToPathSettings` or similar as their first node, which needs a real spline actor input (the `BP_PathSplineProvider` pattern), not a bare `PCGVolume`.
- **Safe, tested, WORKING**: `EntryEx` — 845 instances, uses the plain `PCGVolumeSamplerSettings → PCGStaticMeshSpawnerSettings` pattern (the already-proven "Volume" pin fix).

**Step 1 fully closed. Crash bug isolated to a specific node PATTERN, not the `PCGExCreateShapesSettings` node type in general:**
- **Crash confirmed**: `AtriumEx`, `ColonnadeEx`, `RotundaEx` — all 3 share `PCGVolumeSamplerSettings → PCGExCreateShapesSettings → PCGExCreateShapeGridSettings → ...`. All 3 crashed the engine identically on generate; all 3 recovered cleanly via `-unattended` relaunch (~1 min each).
- **Safe (no crash), but non-functional (0 instances)**: `FacadeEx` — same `PCGExCreateShapesSettings`/`PCGExCreateShapeGridSettings` pair, but fed from `PCGSurfaceSamplerSettings` instead of `PCGVolumeSamplerSettings`. Strongly suggests the crash is specifically about what a bare `PCGVolume`'s volume sampler feeds into `CreateShapes` (likely a degenerate/huge point count from the default volume bounds hitting `SetNumPointsAllocated` with a bad value) — not a defect in the `CreateShapes`/`ShapeGrid` nodes themselves.
- Static Python reflection on `PCGExCreateShapesSettings` properties didn't work cleanly for diagnosis (most fields are C++-protected, `dir()`-based enumeration throws on protected getters) — direct one-at-a-time live testing was faster and more conclusive once `-unattended` made crash recovery cheap.

**Fix scope decision**: NOT attempted tonight. Replacing `PCGExCreateShapesSettings` with vanilla `PCGCreatePointsSettings` (the proven Escher `*Ex` pattern) would erase real authored shape-grid content (these are architectural room-shape generators, not simple point scatters) without understanding what art direction they were producing — a guess-replacement risks losing real work, unlike the Escher `*Ex` fixes which were re-deriving simple test points from scratch. Needs either: (a) a real Volume actor with sane bounds instead of a bare test `PCGVolume` (the crash may be purely a test-harness artifact — a properly-placed/sized volume in the real level might never hit the bad path), or (b) tracing `PCGExCreateShapesSettings`'s actual seed/count inputs in-editor (Material/Graph Editor UI, not headless Python) to find the real bad param. Flagging as a clear next step rather than guessing at a destructive fix.

## RESEARCH 2026-07-02 (overnight): UE5.8 PCG capabilities + Escher precedent, both `Research` status

- **UE5.8 added "Mesh Terrain"** — a terrain system based on 3D meshes instead of heightmaps, natively PCG-integrated, explicitly supports overlapping geometry (caves, overhangs, complex structures). [Unreal Engine 5.8 Preview](https://www.biunivoca.com/en/blog/unreal-engine-5-8-preview), [UE 5.8 release notes](https://www.unrealengine.com/news/unreal-engine-5-8-is-now-available)
  - **Investigated 2026-07-02, `Broken`/no-API confirmed**: Mesh Terrain has **no Python-exposed creation/authoring class** (`unreal.MeshTerrain*`, `AMeshTerrain`, `/Script/Landmass.MeshTerrain` all resolve to nothing) — same limitation as classic Landscape. What IS exposed: 5 PCG-side classes for reading/baking an *already-authored* Mesh Terrain (`PCGGetMeshTerrainSectionSettings`, `PCGGetMeshTerrainSectionActorSettings`, `PCGGetMeshTerrainSectionChannelTexturesSettings`, `PCGBakeMeshTerrainSectionMeshSettings`, `PCGMeshTerrainSectionData`). **Conclusion: does not unblock the "landscape creation has no API" gap** — a human still has to create the Mesh Terrain in-editor first; PCG can then query/bake from it. Worth remembering for later (once a Mesh Terrain exists in a level, these 5 nodes are real scriptable integration points), but not a path to headless terrain authoring.
- **UE5.8 PCG also added edit-on-top-of-procedural-content** — manual art-direction edits no longer break the underlying procedural graph, so upstream params stay live-adjustable after hand-tweaking. Relevant to any future "hand-finish a generated cathedral" pass. [PCG Framework Node Reference (5.8 docs)](https://dev.epgames.com/documentation/unreal-engine/procedural-content-generation-framework-node-reference-in-unreal-engine)
- **No existing UE PCG literature documents Escher-style impossible-geometry generation** — confirmed via search, this remains a genuine gap; the closest precedent (Monument Valley, Scott Kim's 1994 "Escher Interactive") is hand-authored puzzle content, not procedural. This project's math-translated room generators (Relativity/Penrose Loop/Recursive/Gravity-Shift, see MAJOR FINDING below) are, as far as this research found, a novel application — not derivative of a known PCG technique. Worth stating that plainly in any portfolio write-up rather than implying prior art exists.
- Escher's technique in art-historical terms: locally-consistent, globally-inconsistent geometry (Penrose Triangle-style) — useful framing for future room generators: each individual box/segment must obey normal Euclidean placement rules relative to its neighbor, only the *global loop closure* breaks consistency. This matches exactly what `_penrose_loop_points()` and `_gravity_shift_corridor_points()` already do (each arm/segment placed consistently, the paradox is only apparent over the full loop) — validates the existing math approach rather than suggesting a new one.

## MAJOR FINDING 2026-07-02 (overnight autonomous session): a far more sophisticated Escher/surreal architecture generator already exists outside the PCG system

`deploy/surreal_architecture_gen.py` (~15,700 lines, Blender addon, currently v2.131.0 in this repo -- confirmed newer than a June 4 backup zip found on the user's OneDrive Desktop, which was v2.55.0 and explicitly a "base" recovery snapshot for baroque interior presets lost on 2026-06-03 and never recovered) contains real, fully-wired Escher room generators built as Blender GeometryNodes, e.g.:
- `build_gb_escher_relativity()` (line ~6332) — "Relativity Room: a chamber where 3 gravity directions coexist. Based on Escher's 'Relativity' (1953)" — floor/wall/ceiling staircases in one room, real UI preset (`SURREAL_ARCH_OT_preset_gb_escher_relativity`), fully operator-wired.
- A "Print Gallery"/"Smaller and Smaller" recursive room generator (line ~6705) — "hub room for recursive puzzle levels."
- Also: real spiral staircase mesh generator (`_make_spiral_staircase_mesh`), Rotunda with gallery+oculus dome, Vault Cluster (barrel-vaulted chamber grid), Lighthouse, Greybox Pillar Hall.

This is **architecturally more sophisticated than the current UE-native PCG Baroque/Escher work** (which uses hand-placed `PCGCreatePointsSettings` points, not real room-grammar generation). It outputs Blender meshes + a `.world.json` manifest (see `deploy/SURREAL_WORLD_RESEARCH.md`, `surreal_world/compose.py`/`export.py`) meant for HISM import into UE — that bridge exists in concept but its actual current working state (does it run, does the export produce valid UE-importable data) has NOT been verified this session. This is a serious candidate for the "massive scale cathedral + Escher environment" goal — likely more powerful than continuing to iterate on the UE-side PCG graphs alone. Needs a dedicated investigation pass: (1) confirm the Blender addon still runs cleanly in the user's current Blender version, (2) generate a test Relativity Room + export via the world.json pipeline, (3) confirm the UE import side (`surreal_world` Python package or manual HISM import) actually works end-to-end, (4) only then decide whether to lean on this system vs. continuing pure-PCG expansion.

**READ THIS FILE FIRST, before trusting any other plan doc's asset-state claims.** Multiple
tools/sessions edit the same materials and PCG graphs without reading each other's history —
confirmed concretely on 2026-07-01/02: `PCG_Sub_BaroqueSpawn` got fixed by another session with
no record; `bNikkiFast`/`bNikkiHero` orphan switches were deleted then silently recreated;
`M_Master_Toon_Universal`'s `bTriplanar` switch and `TriplanarTileSize`/`TriplanarBlendSharpness`
scalars were removed/renamed to `TriplanarTiling`/`TriplanarBlend` (no boolean gate) within the
same session; `PCG_RockScatter` was renamed or removed entirely between two checks an hour apart.
**Numbers below are last-verified live reads, not assumptions — if you're about to script an edit
against a specific parameter/node name, re-verify it exists first (`get_material_expressions` /
`list_assets`), don't trust this table blindly either.**

**Last verified:** 2026-07-02, by Claude (live `MaterialEditingLibrary`/`EditorAssetLibrary` reads, not doc inference)
- `M_Master_Toon_Universal`: 916 expressions, 10 static switches (`UseUDSTimeOfDay`, `bLayerA_Active`, `bLayerB_Active`, `bLayerC_Active`, `bNikkiHero`, `bSheenUsesNormal`, `bSparkleAdvanced`, `bUseHeightToNormal`, `bUseSeparateMetallicMap`, `bUseSeparateRoughnessMap`), 0 orphaned switches, BSDF fully wired (BaseColor/Metallic/Roughness/Normal/EmissiveColor all non-null).
- `M_Master_Toon_Landscape_HeightBlend`: 280 exprs, 7 switches, 0 orphans. `M_Water_Master_Grand_v6`: 61 exprs, 0 switches. `M_Master_Impressionist_Toon`: 122 exprs, 2 switches, 0 orphans.
- Iridescence/Sheen family confirmed live on Universal: `Iridescence`/`IridescencePower`/`IridescenceBias`/`IridescenceRoughnessAtten`, `FabricSheen`/`SheenPower`/`SheenWidth`/`SheenBias`, `HairSheenStrength`/`HairSheenPower`, 3 Fresnel nodes, all consumed.
- `Content/EnvSandbox/PCG/`: 77 total assets (Styles 53, Universal 20, Collections 2, Legacy_Portfolio 1, _Deprecated 1) — down from an 89-asset count observed earlier the same session; some Universal graphs (e.g. `PCG_RockScatter`) were renamed/consolidated mid-session, re-verify exact paths before scripting against them.
- Escher `*Ex` graphs: `PCG_EscherFloatingIslandEx`/`GravityBridgeEx`/`ImpossibleArchEx` fixed and live-verified generating (8/5/8 instances respectively) via disconnected-StaticMeshSpawner repair. `PCG_EscherPenroseStairEx` still produces 0 — needs a spline/path input (same root cause as the ~13 Bezier-blocked graphs, not yet fixed).
- 4-scene flagship Material Instances built/upgraded: `MI_Sakura_ToriiRed`, `MI_Baroque_GildedFiligree`, `MI_Escher_ImpossibleTile`, `MI_Grotto_CrystallineSpire` (this last one had a dead parent reference — WorldGridMaterial fallback — reparented to Universal as part of the fix).
- 54 prop folders (`Content/Library/Migrated/{MagiciansLibrary,Melodia}/`) migrated via raw-copy + material-slot repair script (`Content/Python/migrate_props_from_source.py`) — not yet wired into any `SCATTER_MESHES` role.
- Master split experiment (Step 8, `Content/EnvSandbox/Materials/_Scratch/`): proved the pattern works -- `MF_IridescenceSheen` extracted as a standalone Material Function, wired into a duplicate base, verified via instance parameter readback. API note: `MaterialEditingLibrary.duplicate_material_expression` only works within one graph, can't copy nodes across into a Function -- extraction means faithful reimplementation, not literal copy-paste. Production master untouched (916 exprs confirmed before/after). Layer A/B/C blend chains (now cleanly grouped, see param-group entry below) are the next extraction candidates.
- PCGEx: 381 `PCGExSettings` classes confirmed available (`Content/Python/probe_pcgex_nodes.py` → `Saved/Audit/pcgex_node_probe.json`). Concrete unused-but-relevant candidates for organic Nikki-style scatter: `PCGExLloydRelax2DSettings`/`PCGExLloydRelaxSettings` (even point distribution, prevents clumping), `PCGExFusePointsSettings` (dedupe near-overlapping instances), `PCGExDistanceFilterProviderSettings` (already in use in `PCG_Sub_WalkabilityFilter`).
- `PCG_SimpleScatter` + `PCG_ClusteringScatter` (8 spawners) remapped from `/Engine/BasicShapes/Cube` to real migrated meshes, live-verified via post-save re-read. Both currently still produce 0 generated instances for reasons unrelated to the mesh fix — `PCG_SimpleScatter` needs a landscape/surface for its `PCGSurfaceSamplerSettings` node, `PCG_ClusteringScatter` has a pre-existing input-chain issue and was never in the confirmed-14-working set. Fix the point-source problem and the correct meshes are already waiting.
- **`MF_Gemstone` built** (`Content/EnvSandbox/Materials/_Scratch/`, scratch only, production master untouched at 916 exprs) -- jewelry-material family (chromatic dispersion Fresnel + facet specular variance), distinct from Iridescence/Sheen, params verified propagating via readback. Honest limitation: no clearly distinguishable visual difference in `capture_material_grid` even after 4x magnitude amplification -- needs real-time in-editor tuning (Material Editor live preview), not resolvable via headless scripting alone. Don't re-attempt the same headless amplification approach; if picking this up again, either tune interactively in-editor or trace why the additive contribution is being visually absorbed (check interaction with the co-installed MF_IridescenceSheen on the same scratch base, or the SubstrateToonBSDF's response to small BaseColor deltas).
- **`capture_material_grid` (Monolith `editor` action) is a genuinely trustworthy visual verification path** for M_Master_Toon_Universal instances -- unlike `render_preview` (documented unreliable, shows identical output regardless of color params), a before/after test on 4 flagship instances showed real, visible hue/richness differences matching the parameter changes made. Call params must be nested under a `params` object (not top-level) when using the generic `editor_query` action dispatcher. Use this, not `render_preview`, for future material instance visual checks on this master.
- **`BaseTint` (group "01 | Base Surface", default flat 0.5/0.5/0.5 grey) is the actual base color driving every instance's overall hue** -- every prior session's flagship-instance work (including the "4-scene Nikki-styled library" built earlier) only touched effect-layer params (Iridescence/Sheen/Layer blends) on top of this untouched grey default, which is why they read as washed-out/pale rather than richly colored. Also unused until now: `DreamTint`, `IridescenceTint`, `GoldTint` (group "11 | Gilding"), `ShadowDreamTint` (group "13 | Shadow Dream") -- a full tint ecosystem. Check `BaseTint` first on any instance that "doesn't read well."
- **`bSparkleAdvanced` + the full "09 | Nikki Sparkle" family (`SparkleScale/Intensity/Threshold/Contrast/DriftSpeed/TwinkleSpeed/NoiseScale/ColorLerp`, `SparkleColor/Low/High`) is fully wired and unused** -- traced end-to-end this session (both switch branches populated, reaches a real TextureSampleParameter2D chain, not an orphan). Now activated on the 4 flagship instances.
- **`PCGVolumeSamplerSettings` wiring fix (broadly useful)**: its "Volume" input pin must be wired from the graph's own Input node's "In" output pin using the exact target pin name `"Volume"`, not the generic `"In"` name used elsewhere in PCG -- easy typo, silently produces 0 points with no error. Confirmed live: 0 -> 27,000 instances once corrected. Check any future VolumeSampler-based graph showing 0 output for this exact mistake before assuming a deeper problem.
- **`PCGExAssetStagingSettings` -> `PCGExMeshSelectorStaged` handoff confirmed still broken/unclear** even with the VolumeSampler fix applied and points correctly reaching the staging node (tested with both a broken collection and a clean 3-entry collection, `output_mode=ATTRIBUTES`, correct `In`/`Out` pin wiring) -- staging node produces 0 spawned instances downstream. The blocker is specifically in this node pairing's attribute contract (likely a `asset_path_attribute_name` mismatch between what staging writes and what the selector reads, or missing required config on `PCGExMeshSelectorStaged` not discoverable from CDO property inspection alone). Needs PCGEx source reading, not more trial-and-error -- two separate sessions have now hit this same wall.
- `PCGCol_Environment_GroundCover`/`PCGCol_Environment_Rocks` (`PCGExMeshCollection` assets, real weighted mesh entries, built by parallel tooling) are 100% unreferenced by any graph — same "built but not wired" pattern as `PCG_Sub_BaroqueSpawn` was. `PCGExAssetStagingSettings` is the PCGEx node meant to consume them but its wiring contract (property `collection_source`, `selector_mode`, output pin behavior) wasn't reverse-engineered this session — needs dedicated investigation before attempting.

## Ownership Boundary

`L_SakuraPath` art direction, hero composition, set dressing, and final scene polish are human-owned. Japanese/Sakura-themed materials and instances are allowed as reusable platform/look-dev work. This state file tracks the reusable platform around that work.

## Platform Systems

| System | Status | Current Truth | Next Platform Action |
|---|---|---|---|
| Universal master material | Implemented | `M_Master_Toon_Universal` is the central mesh/prop/trimsheet master with many style families. | Keep architecture; audit latest update, parameter metadata, duplicate params, stale refs. |
| Landscape height blend | Implemented | `M_Master_Toon_Landscape_HeightBlend` supports reusable terrain look-dev. | Document generic usage presets and capture requirements. |
| Grand water | Implemented | `M_Water_Master_Grand_v6` is canonical reusable water. | Treat as platform pillar; capture generic pond/shoreline examples in template context. |
| Material instances | Implemented | `MI_Show_*`, `MI_Landscape_*`, `MI_GrandWater_*`, trimsheet, Zen, Baroque families exist. | Generate material family manifest and preview readiness report. |
| Material manifest | Partial | Portfolio schema expects material metadata, but no stable producer existed. | Use `Content/Python/material_family_manifest.py` as the thin contract producer. |
| L_Template look-dev stage | Partial | Template stage exists and is referenced by setup scripts. | Promote as generic look-dev validation stage; avoid Sakura dependency. |
| PCG universal stack | Implemented | Universal and style wrapper PCG graphs are documented and audited. | Keep generic scatter contracts separate from Sakura art pass. |
| Capture/package stack | Implemented | Render exporter, plate compiler, output layout, and aggregator exist. | Add completeness reports and generic material preview inputs. |
| Website deploy lane | Implemented | `_github_deploy/generated` contains generated web artifacts. | Add package-to-website metadata handoff map. |
| Figma/design system | Implemented | Design system and Figma guide are mature. | Connect package schema to design tokens via adapter docs. |
| Recursive agents | Partial | Agent roles, boundaries, and loops exist. | Add Producer, Material TD, Look-Dev Capture roles and autonomy lanes. |

## Known Technical Debt

| Area | Status | Detail |
|---|---|---|
| Universal inline vs MF duplication | Partial | `MATERIAL_SYSTEM_REVIEW.md` flags Nikki/Parallax duplication. |
| Duplicate material params | Partial | Duplicate declarations are tracked in audits; should be reduced cautiously. |
| Archive instance duplication | Partial | `_Archive` mirrors active instance trees in places. Do not delete without explicit approval. |
| Material preview producer | Partial | Existing preview capture was under-wired; manifest producer now supplies metadata, not images. |
| Figma API sync | Planned | Design contract exists; automatic package consumption is not the priority until generic package is stable. |

## Out Of Scope For Automation

- Editing `L_SakuraPath` composition.
- Replacing Sakura hero props.
- Publishing external portfolio updates without approval.
- Broad shader-family redesign.
- Destructive cleanup of legacy assets.
