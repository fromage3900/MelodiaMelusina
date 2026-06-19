# Material Migration — Melodia → BS_GodFile (UE 5.8 Substrate Toon)

Stock UE 5.8 **Substrate Toon BSDF + Toon Profile** replaces MooaToon / Default Lit. SDF materials are the first migration priority.

**Systematic playbook:** see [`TOON_MIGRATION_RUNBOOK.md`](TOON_MIGRATION_RUNBOOK.md) for full inventory, phased pipeline, batch schedule, automation, and daily workflow.

**Inventory scan:** `Content/Python/scan_melodia_materials.py` (517 material-like assets in Melodia as of 2026-06-19).

---

## Folder & naming schema

All portfolio materials live under `/Game/EnvSandbox/Materials/`:

```
/Game/EnvSandbox/Materials/
  Masters/              M_* master materials (few, shared)
  SDF/
    Instances/          MI_Toon_SDF_* — SDF look-dev instances (batch 1)
    Textures/           T_* SDF distance/offset maps (when copied from Melodia)
  Instances/
    Environment/        MI_* non-SDF environment surfaces (later)
    Stylized/           MI_* stylized non-SDF (later)
  Functions/            MF_* reusable graph logic
  ToonProfiles/         TP_* Substrate toon ramp profiles
  PostProcess/          M_PP_* outline / color grade (later)
```

**Prefixes (Epic standard):** `M_` master, `MI_` instance, `MF_` function, `TP_` toon profile, `T_` texture (`_D/_N/_ORM` suffixes).

**SDF naming:** `M_Toon_SDF` (master), `MI_Toon_SDF_<Role>` (instance). Role = `Wall`, `Floor`, `Accent`, `Rim`, `Ornamental`, `Stone`, etc. — portfolio terms, not Melodia codenames.

**Do not use:** Melodia game names (`Musical`, `BeatSync`, character codenames) unless renamed for portfolio.

Per-environment overrides stay in `/Game/EnvSandbox/Environments/<StyleName>/Materials/` (style-local `MI_*` only).

**Legacy library:** `Content/_PROJECT/` (~1800+ Melodia assets) is retained permanently as source work. Migration rewires `/Game/EnvSandbox/Materials/` to portfolio paths; it does not delete or archive `_PROJECT`.

---

## Toon shading approach (UE 5.8 stock)

| Layer | Asset / node | Role |
|-------|--------------|------|
| Shading | `MaterialExpressionSubstrateToonBSDF` | Cel ramps, specular bands, shadow hatching |
| Profile | `UToonProfile` (`TP_*`) | Diffuse/specular ramps, shadow extinction, hatching |
| Output | **Front Material** pin (not legacy Base Color) | Substrate root |
| SDF proxy | World-aligned sin bands on master | Faux panel relief until raymarched SDF pass |
| Outline | Post-process material (future) | Not per-mesh MooaToon hull |

**Project settings:** `r.Substrate=True`, `r.Substrate.ProjectGBufferFormat=0` (Blendable GBuffer). Restart editor after first enable.

**Not ported:** MooaToon plugin, custom C++ material nodes, raymarched SDF graphs, audio-reactive/game VFX shaders.

---

## Melodia inventory summary (2026-06-19 scan)

| Category | Total | Masters (M) | Status |
|----------|------:|------------:|--------|
| SDF Tier A | 40 | 30 | 6 source → batch 1; 5 new → batch 2; **12 copied, need Toon conversion**; **17 not copied** |
| SDF underwater (Tier B) | 9 | 9 | Defer |
| SDF math-art (Tier B) | 5 | 5 | Defer |
| Environment | 186 | 145 | Batch 4 (`M_Master_Toon`) |
| Stylized / MooaToon | 56 | 49 | Batch 4–7 |
| Landscape | 12 | 5 | Batch 5 |
| Foliage | 5 | 3 | Batch 5 |
| Defer (game/VFX/dev/layers/UI) | 46 | — | Do not migrate |
| **BS EnvSandbox on disk** | **47** | **18 M + 14 MI** | Includes batch 1–2 + robocopy copies |

**Remaining portfolio work:** ~95 masters + instances. **Next batch:** Batch 3 — convert 12 copied SDF masters (Strategy C) + robocopy 6 cathedral-priority masters.

---

## SDF inventory (Melodia `G:\Melodia\Content`)

**Total SDF-tagged assets:** 54 masters/instances in core+underwater+math folders (plus 26 `ML_*` layers deferred).

### Priority A — Portfolio environment (migrate first)

| Melodia asset | Role | BS_GodFile target | Status |
|---------------|------|-------------------|--------|
| `M_SDF_TrueParallax` | Façade relief / parallax panels | `MI_Toon_SDF_Wall` | **Migrated (batch 1)** |
| `M_SDF_GildedStucco` | Stucco walls / terrace | `MI_Toon_SDF_Wall`, `MI_Toon_SDF_Floor` | **Migrated (batch 1)** |
| `M_SDF_GildedFiligree` | Gold filigree trim | `MI_Toon_SDF_Accent` | **Migrated (batch 1)** |
| `M_SDF_OrnamentLayer` / `_Enhanced` | Layered ornament relief | `MI_Toon_SDF_Ornamental` | **Migrated (batch 1)** |
| `M_SDF_Baroque` | Dark architectural trim | `MI_Toon_SDF_Rim` | **Migrated (batch 1)** |
| `M_SDF_GothicArchitecture` / `_Enhanced` | Gothic masonry | `MI_Toon_SDF_Wall` (tune) | Deferred — tune instance |
| `M_SDF_RoseWindow` / `M_SDF_GothicRoseWindow` | Rose window SDF | New `MI_Toon_SDF_Glass` | Deferred — needs texture pass |
| `M_HybridStone_SDF` | Stone mesh blend + SDF edge | `M_Toon_SDF` + stone instance | Deferred — hybrid pass |
| `M_HybridLandscape_MooaToonSDF` | Landscape height + SDF | Landscape master (later) | Deferred |
| `M_SDF_Grass_Field` | Stylized ground SDF | Foliage/landscape master | Deferred |
| `M_SDF_CathedralVault`, `M_SDF_FlyingButtress` | Vault geometry SDF | Environment style pack | Deferred |

Baroque folder duplicates (`baroque/M_SDF_*`) map to same portfolio instances as core `SDF/` masters.

### Priority B — Stylized / niche environment

Underwater set (`SDF/Underwater/M_SDF_*`, 9 masters): coral, kelp, caustics — defer until underwater environment style.

Math-art SDF (`M_SDF_Mandelbulb_*`, `JuliaSet`, `Klein_Bottle`, etc.): demo/reference only, not portfolio core.

### Priority C — Defer (game-specific)

| Melodia asset | Reason |
|---------------|--------|
| `M_SDF_Musical`, `M_SDF_FloatingNotes`, `M_SDF_GrandStaff_*`, `M_SDF_SheetMusic_Score`, `M_SDF_VinylRecord`, `M_SDF_TrebleClef_Ornament` | Rhythm-game motifs |
| `M_MusicalSDF_PulsingGeometry`, `MI_Music_*`, `MI_MusicalSDF_*` | Audio-reactive gameplay |
| `M_SDF_MagicOrb`, `M_SDF_CosmicPortal` | Combat/VFX |
| `M_SDF_TestBench`, `Dev/` | Dev only |

Material layers (`04_Materials/MATERIALLAYERS/SDF/ML_*`): MooaToon layer stack — reference only; rebuild as `MF_*` if needed.

---

## Batch 1 — created by `setup_sdf_materials.py`

| Asset | Path |
|-------|------|
| Master | `/Game/EnvSandbox/Materials/Masters/M_Toon_SDF` | **Built** |
| Profiles | `/Game/EnvSandbox/Materials/ToonProfiles/TP_{Default,Stucco,Gold,Ornamental}` | **Built** |
| Instances | `/Game/EnvSandbox/Materials/SDF/Instances/MI_Toon_SDF_{Wall,Floor,Accent,Rim,Ornamental}` | **Built** (via `setup_sdf_materials.py`) |

**Parameters on master:** `BaseTint`, `AccentTint`, `SDF_BandScale`, `SDF_BandStrength`.

**Graph:** WorldPosition.XY × BandScale → Sin → Abs → Lerp tints → Substrate Toon BSDF → Front Material.

---

## Batch 2 — fancy SDF masters (via UnrealMCP, 2026-06-19)

Built live in-editor through **UnrealMCP** material tools (`create_material_asset`, `add_material_expression`, `connect_material_expressions`, `create_material_instance`). Portfolio originals inspired by migrated Melodia raymarch/noise patterns — not copies.

| Master | Instance | Role | Key parameters |
|--------|----------|------|----------------|
| `M_SDF_ReliefPanel` | `MI_SDF_ReliefPanel_Baroque` | Deep parallax relief bands + Voronoi/Perlin ornament | `BaseTint`, `AccentTint`, `DeepTint`, `BandScale`, `ReliefDepth`, `NoiseScale` |
| `M_SDF_FiligreeRim` | `MI_SDF_FiligreeRim_Gold` | Animated gilded filigree + normal-based rim accent | `GoldTint`, `HighlightTint`, `FiligreeScale`, `RimStrength`, `AnimSpeed` |
| `M_SDF_GothicTracery` | `MI_SDF_GothicTracery_Rose` | Radial rose-window tracery (sin×cos rings) + Voronoi stone | `BaseTint`, `LeadTint`, `GoldTint`, `RadialScale`, `TraceryMix` |
| `M_SDF_HybridStone` | `MI_SDF_HybridStone_Worn` | Marble + Voronoi cracks + edge gold wear (MeshBlend-friendly) | `StoneTint`, `MossTint`, `GoldEdge`, `WearAmount`, `StoneTiling` |
| `M_SDF_ParallaxPulse` | `MI_SDF_ParallaxPulse_Violet` | Time-animated parallax bands + emissive pulse | `BaseTint`, `PulseTint`, `BandScale`, `PulseSpeed`, `GlowStrength` |

**Textures wired:** `SDF/Textures/Voronoi/*`, `Perlin/*`, `Marble/*`.

**Viewport test:** Assign any `MI_SDF_*` from batch 2 to `StaticMeshActor_0` or `Floor_0` in `_Template`; orbit camera — FiligreeRim shows rim boost on edges, ParallaxPulse animates emissive bands, GothicTracery reads best on large flat faces.

---

## Batch 3 — Tier A SDF toon conversion (2026-06-19)

**Goal:** Substrate Toon BSDF → Front Material on all copied Melodia SDF masters.

| Action | Status |
|--------|--------|
| Convert 16 batch masters (Strategy C via Python) | **Done** — `convert_masters_to_substrate_toon.py` |
| Assign `TP_*` on instances | **Done** — 14 instances via `assign_instance_profiles.py` |
| Fix MeshBlend dead refs | Run `fix_meshblend_activator_refs.py` after MF repair |
| Robocopy cathedral gaps | **Queued** — `CathedralVault`, `FlyingButtress`, etc. |

**Automation**

| Script | Purpose |
|--------|---------|
| `Content/Python/run_toon_conversion.py` | Full batch: convert all + MCP param rename + profiles |
| `Content/Python/run_toon_conversion_pending.py` | Disk-detect retry for unsaved masters |
| `Content/Python/assign_instance_profiles.py` | Instance `TP_*` assignment only |
| `Content/Python/audit_material_parameters.py` | Parameter cohesion audit → `Saved/Audit/material_parameter_audit.json` |

Reports: `Saved/Audit/substrate_toon_conversion.json`

---

## Toon library cohesion (param + profile matrix)

### Material families

| Family | Path | Master pattern | Canonical params |
|--------|------|----------------|------------------|
| **SDF Core** | `Masters/M_SDF_*` (Melodia copies), `M_Toon_SDF` | Strategy C converted raymarch/SDF | `BaseTint`, `AccentTint`, `SDF_BandScale`, `SDF_BandStrength` |
| **SDF MCP** | `Masters/M_SDF_{ReliefPanel,FiligreeRim,...}` | MCP-built procedural | `BaseTint`, `AccentTint`, `DeepTint`, `BandScale`, `ReliefDepth`, `NoiseScale`, … |
| **Impressionist** | `Impressionist/Masters/M_Master_Impressionist_Toon*` | Brush/impasto toon | `ColorRampLow/Mid/High`, `BrushScale`, `StrokeStrength`, `ImpastoStrength`, `Wetness` |
| **Environment** | `Instances/Environment/` (future) | `M_Master_Toon` (batch 4) | Stone/wood/fabric palette tints |

### Toon Profile assignment

| Profile | Use for |
|---------|---------|
| `TP_Default` | Neutral stone, hybrid, floor |
| `TP_Stucco` | Walls, masonry, gothic architecture, parallax panels |
| `TP_Gold` | Filigree, rose window, accents, gilded trim |
| `TP_Ornamental` | Ornament layers, relief panels, baroque scrollwork |
| `TP_Impressionist_Dry` | Dry meadow, landscape grass |
| `TP_Impressionist_Wet` | Wet fields, water-adjacent |
| `TP_Impressionist_Impasto` | Heavy impasto stone |

Instance overrides: set `override_toon_profile=True` on each `MI_*` (see `INSTANCE_PROFILE_BY_STEM` in `convert_masters_to_substrate_toon.py`).

### Parameter hygiene rules

1. **No `MCP_N` placeholders** on portfolio masters — batch converter renames to canonical names.
2. **Group params:** `Toon`, `SDF`, `Palette`, `Brush`, `Animation`.
3. **Instance-exposed:** all palette tints + band/relief scalars on masters used for look-dev.
4. Re-run `audit_material_parameters.py` after each batch; target zero placeholders.

---

## Build (editor)

1. Open `BS_GodFile.uproject` in **UE 5.8** (stock, not MooaToon).
2. Confirm `Config/DefaultEngine.ini` has `r.Substrate=True`.
3. **Tools → Execute Python Script** → `Content/Python/setup_sdf_materials.py`  
   Or Output Log:  
   `py "G:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_sdf_materials.py"`
4. Assign `MI_Toon_SDF_Wall` to a test mesh; compare visually to Melodia `M_SDF_TrueParallax` reference screenshots.

Safe to re-run: rebuilds master/instances; reuses existing Toon Profiles.

---

## Manual editor follow-up

1. **Tune Toon Profiles** — open each `TP_*` asset; sculpt diffuse/specular ramps for portfolio baroque look (flat shadow steps, gold specular band on `TP_Gold`).
2. **Post-process outline** — create `M_PP_ToonOutline` under `PostProcess/`; assign to `_Template` PPV (see `setup_template.py` comment).
3. **True SDF textures** — export distance-field textures from Melodia `M_SDF_*` (if embedded) into `SDF/Textures/`; wire as Toon Profile `DiffuseRampOffsetTexture` on a v2 master.
4. **Raymarched SDF** — full parity with Melodia `M_SDF_*` raymarch graphs is a later pass; current master uses world-band proxy only.
5. **Hybrid stone/water** — after batch 1 validates, extend master or add `M_Toon_SDF_Hybrid` for mesh-blend companions.
6. **Remove ad-hoc paths** — if `/Game/EnvSandbox/Shared/Materials/` or `/Game/EnvSandbox/Shared/Materials/Masters/M_Master_Toon` exist from early experiments, delete or migrate to schema above.

---

## Melodia → portfolio mapping (PCG / baroque kit)

| Catalog use | Melodia production | BS_GodFile batch 1 |
|-------------|-------------------|-------------------|
| Façade / wall | `M_SDF_TrueParallax` | `MI_Toon_SDF_Wall` |
| Floor / terrace | `M_SDF_GildedStucco` | `MI_Toon_SDF_Floor` |
| Gold trim | `M_SDF_GildedFiligree` | `MI_Toon_SDF_Accent` |
| Dark rim | `M_SDF_Baroque` | `MI_Toon_SDF_Rim` |
| Ornament relief | `M_SDF_OrnamentLayer` | `MI_Toon_SDF_Ornamental` |

---

## Generic environment materials (deferred)

Non-SDF MooaToon masters (`M_Stone_*_Toon`, `M_Wood_Toon`, `M_Fabric_Toon`, `M_Universal_Enhanced_*`) → future `M_Master_Toon` under `Masters/` with instances in `Instances/Environment/`.

---

## MCP tooling

| Plugin | Status in BS_GodFile | Notes |
|--------|---------------------|-------|
| **UnrealMCP** | **Active** (`Plugins/UnrealMCP`) | Connected; used for batch 2 material build |
| **Monolith** | Not installed | Available at `G:\Melodia\Plugins\Monolith` — no MooaToon dep; optional upgrade (1387 MCP actions, source compile for UE 5.8) |
| **VibeUE** | Not installed | Melodia has 5.7 build; Fab plugin, redundant with UnrealMCP |
| **it-is-unreal** | N/A | Community MCP server name (pre-5.8); superseded by stock UE 5.8 `ModelContextProtocol` + UnrealMCP |

---

*Last updated: 2026-06-19 — runbook + inventory scan added*
