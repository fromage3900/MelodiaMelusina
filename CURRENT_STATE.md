# Current State - Universal Environment Platform

Status labels: `Implemented`, `Partial`, `Broken`, `Planned`, `Research`, `Deprecated`.

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
