# Scene: SakuraPath — cute dreamy cherry-blossom garden

First portfolio **vertical slice**. UE 5.8 · Substrate Toon · `M_Master_Toon_Universal`.

## Concept
A cozy storybook Japanese garden path under blooming sakura at soft dusk — Infinity-Nikki
dreaminess: pastel pink/cream, gentle glow, drifting petals that catch the light.

## Mood / palette
- Soft warm **dusk**: pink-gold key light, lavender-blue ambient.
- Pastel pink blossom · cream stone · moss green · muted vermilion torii · warm lantern glow.
- Dreamy **bloom**, light volumetric fog for depth, gentle **petal shimmer** (Nikki sparkle).

## Composition (hero shot)
- **Foreground:** mossy stepping-stone path leading the eye in.
- **Midground:** arched canopy of 2–3 sakura trees framing the path.
- **Focal point:** a small red **torii gate** (or stone lantern) in a soft-lit clearing.
- **Background:** more blossom canopy fading into pastel fog; a hint of koi pond + arched bridge to one side.

## Asset kit (CC0 / Fab-Megascans / Blender)
| Asset | Source plan |
|---|---|
| Sakura tree (trunk + blossom canopy) | Sketchfab CC0 / Blender (sapling + blossom cards) |
| Blossom petals (scatter cards) | Blender / CC0 alpha (`T_Spark`/petal mask) |
| Torii gate | Sketchfab CC0 |
| Stone lantern (tōrō) | Sketchfab CC0 / Megascans |
| Stepping stones / rocks | Megascans (CC0 via Fab) |
| Wooden arched bridge | Sketchfab CC0 |
| Koi pond (water plane) | toon water material |
| Grass / moss / small flowers | Megascans / PCG scatter |

## Materials (all MI on `M_Master_Toon_Universal`)
| Instance | Setup |
|---|---|
| `MI_Sakura_Blossom` | pink albedo, high `PastelLift`, pink `RimColor`, `SparkleIntensity` (petal shimmer), low `GlowIntensity` |
| `MI_Sakura_Bark` | bark texture, low `TextureWeight` stylization |
| `MI_Sakura_StonePath` | stone tex, triplanar, moss in cavities (curvature) |
| `MI_Sakura_Moss` | soft green |
| `MI_Sakura_Water` | toon water — pastel reflection, gentle ripple |
| `MI_Sakura_ToriiRed` | muted vermilion lacquer, slight gloss |
| `MI_Sakura_Lantern` | weathered stone + warm emissive glow |
| `MI_Sakura_Grass` | two-sided, soft green, gentle wind |

## Lighting
- Directional sun: low dusk angle, warm pink-gold, soft Lumen shadows.
- SkyAtmosphere + pastel-gradient sky / dusk HDRI.
- Exponential height fog (subtle) + volumetric god-rays through canopy.
- Warm point lights inside lanterns (MegaLights).
- PostProcess: manual exposure, AgX, **Bloom up** (the Nikki glow), gentle vignette.

## PCG scatter
- Fallen petals on path + ground (density falloff near trees).
- Grass + tiny flowers. (Later: drifting-petal Niagara.)

## Shots (Movie Render Graph)
1. **Hero:** low path-to-torii, canopy framing — 2560×1440.
2. **Detail:** petals on a mossy stepping stone, shallow DOF.
3. **Detail:** lantern glow at dusk.
4. **Flythrough:** slow push down the path — 1080p/4K.

## Build order (the prep — what the loop is doing)
1. Source the kit assets (trees, torii, lantern, rocks, bridge) — CC0, license-checked.
2. Build the `MI_Sakura_*` set on the universal master.
3. Greybox layout (path + tree positions + focal point) in `L_SakuraPath` from `_Template`.
4. Replace greybox with kit assets; PCG-scatter petals + grass.
5. Light + post (dusk + bloom).
6. Render hero shots.

## Nanite + Niagara plan
- **Nanite:** enable on the imported high-poly kit (rocks, lantern, torii, tree trunks) — no manual LODs under Lumen. Blossom canopy → Nanite if dense geo, else masked alpha cards.
- **Niagara:**
  - `NS_SakuraPetals` — GPU petal drift: spawn from canopy bounds, gentle wind + flutter, soft pink, light-catching (emissive tint).
  - `NS_MagicalBurst` — sparkle/heart burst for the magical-girl beat (synced to `MagicalTransform`): radial pop of `T_Magic`/`T_Spark` sprites + pastel glow, triggered via Sequencer/BP.
- **PCG:** fallen petals (density falloff near trunks) + grass / tiny flowers on the ground.

## Prep progress (autonomous loop)
- ✅ Master ① macro/detail + ② magical-girl — **code-ready, one rebuild pending** (`py setup_master_universal.py`, full path)
- ✅ Materials — `setup_sakura_instances.py` (8 `MI_Sakura_*`)
- ✅ Scene — `setup_sakura_scene.py` (`L_SakuraPath`: dusk rig + toon/bloom post + greybox torii/path/trunks + CineCamera)
- ✅ Motif alphas — `_AssetLibrary/Magical/` (heart/star/ribbon)
- ⏳ CC0 kit assets (tree/torii/lantern/rocks/bridge) — sourcing pending (license-checked)
- ⏳ Niagara petals/burst + PCG scatter graphs — pending
- ⏸️ Master ③ MF-refactor — deferred until rebuild verified

**Run order when live:** `setup_master_universal.py` → `setup_sakura_instances.py` → `setup_sakura_scene.py` → import CC0 kit → swap greybox → PCG/Niagara → light + render.

---
*Prepared autonomously by the sakura loop (job 7c4186f8). Status updated each iteration.*
