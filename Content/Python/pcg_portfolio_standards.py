"""EnvSandbox universal PCG portfolio standards â€” paths, tags, presets, ISM bands.

Updated 2026-07-09: Real mesh integration, grand building scale support.
"""
from __future__ import annotations

PCG_ROOT = "/Game/EnvSandbox/PCG"
MELODIA_PCG_ROOT = "/Game/Melodia/_PROJECT/PCG"

DIR_UNIVERSAL = f"{PCG_ROOT}/Universal"
DIR_SUBGRAPHS = f"{PCG_ROOT}/Universal/Subgraphs"
DIR_GREYBOX = f"{PCG_ROOT}/Greybox"
DIR_COLLECTIONS = f"{PCG_ROOT}/Collections"
DIR_STYLES = f"{PCG_ROOT}/Styles"
DIR_DESERT = f"{DIR_STYLES}/Desert"
DIR_CYBERPUNK = f"{DIR_STYLES}/Cyberpunk"
DIR_ALPINE = f"{DIR_STYLES}/Alpine"
DIR_BAROQUE = f"{DIR_STYLES}/Baroque"
DIR_DEPRECATED = f"{PCG_ROOT}/_Deprecated"

GRAPH_FOLIAGE = f"{DIR_UNIVERSAL}/PCG_FoliageDensity"
GRAPH_ROCK = f"{DIR_UNIVERSAL}/PCG_RockScatter"
GRAPH_WALL_IVY = f"{DIR_UNIVERSAL}/PCG_WallIvy"
GRAPH_WALL_MOSS = f"{DIR_UNIVERSAL}/PCG_WallMoss"
GRAPH_WALL_LICHEN = f"{DIR_UNIVERSAL}/PCG_WallLichen"
GRAPH_WALL_DUST = f"{DIR_UNIVERSAL}/PCG_WallDust"
GRAPH_WALL_GRAFFITI = f"{DIR_UNIVERSAL}/PCG_WallGraffiti"
GRAPH_EXCLUSION = f"{DIR_SUBGRAPHS}/PCG_ExclusionFalloff"
GRAPH_MEADOW_BLOOM = f"{DIR_UNIVERSAL}/PCG_MeadowBloom"
GRAPH_BLOSSOM_PATH = f"{DIR_UNIVERSAL}/PCG_BlossomPath"
GRAPH_LANTERN_GROVE = f"{DIR_UNIVERSAL}/PCG_LanternGrove"
GRAPH_GARDEN_RUINS = f"{DIR_UNIVERSAL}/PCG_GardenRuins"
GRAPH_PETAL_DRIFT = f"{DIR_STYLES}/Sakura/PCG_Sakura_PetalDrift"
GRAPH_MOSS_GROUNDCOVER = f"{DIR_STYLES}/Sakura/PCG_Zen_MossGroundcover"
GRAPH_GREYBOX_MINIMAL = f"{DIR_GREYBOX}/PCG_Greybox_Minimal"
GRAPH_GREYBOX_STANDARD = f"{DIR_GREYBOX}/PCG_Greybox_Standard"
GRAPH_SAKURA_SHOWCASE = f"{DIR_STYLES}/Sakura/PCG_Sakura_Showcase"

# Live quarantine: generating these graphs has terminated the editor. They may
# be inspected or salvaged, but automation must never call PCGComponent.generate.
UNSAFE_GENERATE_GRAPHS = frozenset({GRAPH_SAKURA_SHOWCASE})
QUARANTINE_REPLACEMENTS = {
    GRAPH_SAKURA_SHOWCASE: GRAPH_MEADOW_BLOOM,
}
GRAPH_DESERT_ARID = f"{DIR_DESERT}/PCG_Desert_Arid"
GRAPH_DESERT_OASIS = f"{DIR_DESERT}/PCG_Desert_Oasis"
GRAPH_CYBERPUNK_ALLEY = f"{DIR_CYBERPUNK}/PCG_Cyberpunk_Alley"
GRAPH_CYBERPUNK_ROOF = f"{DIR_CYBERPUNK}/PCG_Cyberpunk_Rooftop"
GRAPH_ALPINE_PINE = f"{DIR_ALPINE}/PCG_Alpine_PineForest"
GRAPH_ALPINE_SCREE = f"{DIR_ALPINE}/PCG_Alpine_Scree"
GRAPH_SAKURA_GROVE = f"{DIR_STYLES}/Sakura/PCG_SakuraGrove"
GRAPH_ORNAMENTAL_ARCH = f"{DIR_UNIVERSAL}/PCG_OrnamentalArch"
GRAPH_ORNAMENTAL_DETAIL = f"{DIR_UNIVERSAL}/PCG_OrnamentalDetail"

SMC_PORTFOLIO = f"{DIR_COLLECTIONS}/SMC_Portfolio_ScatterKit"
SMC_GREYBOX = f"{DIR_COLLECTIONS}/SMC_Greybox_ScatterKit"
SMC_SAKURA = f"{DIR_STYLES}/Sakura/SMC_Sakura_ScatterKit"
SMC_BAROQUE = f"{DIR_STYLES}/Baroque/SMC_Baroque_ScatterKit"

ORPHAN_MEADOW_SCATTER = f"{PCG_ROOT}/PCG_MeadowScatter"
DEPRECATED_MEADOW = f"{DIR_DEPRECATED}/PCG_MeadowScatter"
ORPHAN_SAKURA_GROVE = f"{PCG_ROOT}/PCG_SakuraGrove"

LEVEL_TEMPLATE = "/Game/EnvSandbox/_Template/L_Template"
LEVEL_SAKURA = "/Game/EnvSandbox/Environments/Sakura/L_SakuraPath"
LEVEL_WP_ROOT = "/Game/EnvSandbox/Environments/WP"
WP_PILLAR_LEVELS = (
    f"{LEVEL_WP_ROOT}/L_WP_SakuraDream",
    f"{LEVEL_WP_ROOT}/L_WP_SpaceCathedral",
    f"{LEVEL_WP_ROOT}/L_WP_BaroqueGrotto",
    f"{LEVEL_WP_ROOT}/L_WP_CosmicOrrery",
)

SHIPPING_LEVELS = (
    LEVEL_TEMPLATE,
    LEVEL_SAKURA,
    *WP_PILLAR_LEVELS,
)

TAG_GROUND = "PCG_Ground"
TAG_EXCLUDE = "PCG_Exclude"
TAG_SPLINE = "PCG_Spline"
TAG_PATH = "PCG_Path"
TAG_POND = "PCG_Pond"

ACTOR_GROUND_COVER = "PCG_Greybox_GroundCover"
ACTOR_ROCKS = "PCG_Greybox_Rocks"
ACTOR_EXCLUDE_PREFIX = "PCG_Exclude_"
ACTOR_SAKURA_VOLUME = "PCG_Sakura_GroundCover"
ACTOR_WP_SURFACE = "PCG_WP_Surface"

# Grand building scale constants (UE units = cm)
DEFAULT_VOXEL_CM = 180.0
DEFAULT_DENSITY = 0.42
DEFAULT_EXCLUDE_FALLOFF = 220.0
SPACING_PRUNE_RADIUS_CM = 85.0

SEED_FOLIAGE = 4242
SEED_ROCKS = 5150
SEED_BLOSSOMS = 6161
SEED_DECOR = 7171
SEED_PETALS = 8181
SEED_ARCH = 9191

GROUND_HALF_EXTENT_UU = 3000.0
PCG_VOLUME_CENTER = (0.0, 0.0, 28.0)
# Greybox volumes are deliberately route-scale, not terrain-scale. The PCG
# volume brush is ~100 cm wide before actor scale, so 52 produced an 11.4 km
# scatter footprint and made valid instances visually disappear across the WP
# terrain. Keep the first slice focused on the authored 1.2-1.6 km spine.
PCG_VOLUME_SCALE = (10.0, 10.0, 3.0)

GRASS_SCALE_MIN = 0.6
GRASS_SCALE_MAX = 1.0
ROCK_SCALE_MIN = 0.4
ROCK_SCALE_MAX = 1.2
PETAL_SCALE_MIN = 0.18
PETAL_SCALE_MAX = 0.55
FLOWER_SCALE_MIN = 0.35
FLOWER_SCALE_MAX = 0.85
DECOR_SCALE_MIN = 0.65
DECOR_SCALE_MAX = 1.35

# Architectural scale ranges for grand buildings (castles, cathedrals)
COLUMN_HEIGHT_MIN = 200.0
COLUMN_HEIGHT_MAX = 400.0
ARCH_WIDTH_MIN = 100.0
ARCH_WIDTH_MAX = 500.0
FLOOR_TILE_SIZE = 400.0  # 4x4 floor tile

ISM_BAND_PORTFOLIO = (250, 1600)
ISM_BAND_SAKURA = (320, 1800)
ISM_BAND_MINIMAL = (120, 900)
ISM_BAND_ARCH = (50, 800)  # Smaller band for architectural detail

MI_GREYBOX_GRASS = "/Game/EnvSandbox/Materials/Instances/Showcase/MI_Show_ForestFoliage"
MI_GREYBOX_ROCK = "/Game/EnvSandbox/Materials/Instances/Landscape/MI_Landscape_Meadow"
MI_SAKURA_GRASS = "/Game/EnvSandbox/Materials/Instances/Sakura/MI_Sakura_Grass"
MI_SAKURA_PETALS = "/Game/EnvSandbox/Materials/Instances/Sakura/MI_Sakura_Petals"
MI_EXPERIMENTAL_GRASS_CARD = "/Game/EnvSandbox/Materials/Instances/Environment/MI_ExperimentalGrassCard"

SCATTER_MESHES: dict[str, list[str]] = {
    # Updated 2026-07-09 for grand building scale/alignment
    "grass": [
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Cube_1m.SM_Greybox_Cube_1m",
    ],
    "rock": [
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Rock_A.SM_Greybox_Rock_A",
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Rock_B.SM_Greybox_Rock_B",
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Rock_C.SM_Greybox_Rock_C",
    ],
    "petal": [
        "/Game/EnvSandbox/Meshes/Sakura/SM_SakuraPetal_Nanite/StaticMeshes/SM_Sakura_PetalProxy_Sphere.SM_Sakura_PetalProxy_Sphere",
    ],
    "flower": [
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Star.SM_Greybox_Star",
    ],
    "moss": [
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Cube_1m.SM_Greybox_Cube_1m",
    ],
    "lantern": [
        "/Game/EnvSandbox/Library/Migrated/MagiciansLibrary/Lantern/SM_Lantern.SM_Lantern",
        "/Game/EnvSandbox/Library/Migrated/MagiciansLibrary/LanternGlass/SM_LanternGlass.SM_LanternGlass",
    ],
    "ruin": [
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Wall_4x3.SM_Greybox_Wall_4x3",
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Column_05.SM_Greybox_Column_05",
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Rock_A.SM_Greybox_Rock_A",
    ],
    "decor": [
        "/Game/EnvSandbox/Library/Migrated/MagiciansLibrary/Deco1/SM_Kit_Ornament_A.SM_Kit_Ornament_A",
        "/Game/EnvSandbox/Library/Migrated/MagiciansLibrary/Deco2/SM_Kit_Ornament_B.SM_Kit_Ornament_B",
        "/Game/EnvSandbox/Library/Migrated/MagiciansLibrary/Deco3/SM_Kit_Ornament_C.SM_Kit_Ornament_C",
        "/Game/EnvSandbox/Library/Migrated/MagiciansLibrary/Deco4/SM_Deco4.SM_Deco4",
        "/Game/EnvSandbox/Library/Migrated/MagiciansLibrary/Box/SM_Box.SM_Box",
        "/Game/EnvSandbox/Library/Migrated/MagiciansLibrary/GlassBottle/SM_GlassBottle_Object1715.SM_GlassBottle_Object1715",
    ],
    "cactus": [
        "/Engine/BasicShapes/Cylinder.Cylinder",
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Pillar_03.SM_Greybox_Pillar_03",
    ],
    "neon": [
        "/Engine/BasicShapes/Cube.Cube",
        "/Game/EnvSandbox/Library/Migrated/MagiciansLibrary/GlassBottle/SM_GlassBottle_Object1715.SM_GlassBottle_Object1715",
    ],
    "scree": [
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Rock_A.SM_Greybox_Rock_A",
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Rock_B.SM_Greybox_Rock_B",
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Rock_C.SM_Greybox_Rock_C",
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Rock_C.SM_Greybox_Rock_C",
    ],
    "alpine_ground": [
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Rock_A.SM_Greybox_Rock_A",
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Rock_C.SM_Greybox_Rock_C",
        "/Engine/BasicShapes/Sphere.Sphere",
    ],
    "structural": [
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Cube_1m.SM_Greybox_Cube_1m",
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Wall_4x3.SM_Greybox_Wall_4x3",
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Column_05.SM_Greybox_Column_05",
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Pillar_03.SM_Greybox_Pillar_03",
    ],
    # Grand building architecture roles - for castles, cathedrals, large-scale structures
    "column": [
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Column_05.SM_Greybox_Column_05",
        "/Game/EnvSandbox/Greybox_Kit/SM_column_02.SM_column_02",
    ],
    "arch": [
        "/Game/EnvSandbox/Greybox_Kit/SM_arch_02.SM_arch_02",
        "/Game/EnvSandbox/Greybox_Kit/SM_arch_03_a.SM_arch_03_a",
        "/Game/EnvSandbox/Greybox_Kit/SM_arch_04_a_002.SM_arch_04_a_002",
    ],
    "floor": [
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Floor_4x4.SM_Greybox_Floor_4x4",
        "/Game/EnvSandbox/Greybox_Kit/SM_Block_Floor_4x4.SM_Block_Floor_4x4",
    ],
    "stair": [
        "/Game/EnvSandbox/Greybox_Kit/SM_Greybox_Step_2.SM_Greybox_Step_2",
        "/Game/EnvSandbox/Greybox_Kit/SM_Block_Step_2.SM_Block_Step_2",
    ],
    # Procedural ornamental architecture (15 meshes from generate_ornamental_meshes.py)
    "ornamental_hero": [
        "/Game/EnvSandbox/Meshes/Ornament/SM_Orn_RoseWindow_8Petal.SM_Orn_RoseWindow_8Petal",
        "/Game/EnvSandbox/Meshes/Ornament/SM_Orn_OculusFrame.SM_Orn_OculusFrame",
        "/Game/EnvSandbox/Meshes/Ornament/SM_Orn_SpiralStaircase.SM_Orn_SpiralStaircase",
        "/Game/EnvSandbox/Meshes/Ornament/SM_Orn_VaultRibs.SM_Orn_VaultRibs",
    ],
    "ornamental_detail": [
        "/Game/EnvSandbox/Meshes/Ornament/SM_Orn_ColumnCapital.SM_Orn_ColumnCapital",
        "/Game/EnvSandbox/Meshes/Ornament/SM_Orn_CorbelBracket.SM_Orn_CorbelBracket",
        "/Game/EnvSandbox/Meshes/Ornament/SM_Orn_CrownMolding.SM_Orn_CrownMolding",
        "/Game/EnvSandbox/Meshes/Ornament/SM_Orn_DoorArchway.SM_Orn_DoorArchway",
        "/Game/EnvSandbox/Meshes/Ornament/SM_Orn_FiligreeRing.SM_Orn_FiligreeRing",
        "/Game/EnvSandbox/Meshes/Ornament/SM_Orn_GothicTracery.SM_Orn_GothicTracery",
        "/Game/EnvSandbox/Meshes/Ornament/SM_Orn_PendantFinial.SM_Orn_PendantFinial",
        "/Game/EnvSandbox/Meshes/Ornament/SM_Orn_QuatrefoilArch.SM_Orn_QuatrefoilArch",
        "/Game/EnvSandbox/Meshes/Ornament/SM_Orn_RosetteMedallion.SM_Orn_RosetteMedallion",
        "/Game/EnvSandbox/Meshes/Ornament/SM_Orn_TorusKnot.SM_Orn_TorusKnot",
        "/Game/EnvSandbox/Meshes/Ornament/SM_Orn_WovenRing.SM_Orn_WovenRing",
    ],
}

PRESETS: dict[str, dict] = {
    "minimal": {
        "density": 0.28,
        "voxel_cm": 240.0,
        "spawn_rocks": False,
        "spawn_exclusion": False,
        "use_surface_tag": False,
        "transform_jitter": 12.0,
        "ism_band": ISM_BAND_MINIMAL,
        "volume_scale": (38.0, 38.0, 1.6),
        "volume_center_z": 22.0,
    },
    "standard": {
        "density": 0.38,
        "voxel_cm": 200.0,
        "spawn_rocks": True,
        "spawn_exclusion": False,
        "use_surface_tag": False,
        "transform_jitter": 18.0,
        "ism_band": ISM_BAND_PORTFOLIO,
        "volume_scale": (44.0, 44.0, 2.0),
        "volume_center_z": 26.0,
    },
    "showcase": {
        "density": 0.32,
        "voxel_cm": 220.0,
        "spawn_rocks": True,
        "spawn_exclusion": True,
        "use_surface_tag": True,
        "transform_jitter": 24.0,
        "ism_band": ISM_BAND_SAKURA,
        "volume_scale": (46.0, 46.0, 1.8),
        "volume_center_z": 24.0,
        "foliage_graph": GRAPH_MEADOW_BLOOM,
    },
    "arch": {
        "density": 0.45,
        "voxel_cm": 300.0,
        "spawn_rocks": False,
        "spawn_exclusion": False,
        "use_surface_tag": True,
        "transform_jitter": 15.0,
        "ism_band": ISM_BAND_ARCH,
        "volume_scale": (60.0, 60.0, 4.0),
        "volume_center_z": 40.0,
    },
}

STYLE_PRESETS: dict[str, dict] = {
    "meadow_bloom": {
        "label": "Meadow Bloom",
        "graph": GRAPH_MEADOW_BLOOM,
        "role": "flower",
        "material": MI_GREYBOX_GRASS,
        "density": 0.26,
        "voxel_cm": 190.0,
        "use_surface_tag": True,
        "spawn_exclusion": True,
        "transform_jitter": 20.0,
        "scale": (FLOWER_SCALE_MIN, FLOWER_SCALE_MAX),
        "seed": SEED_BLOSSOMS,
        "notes": "Soft flower/ground accent layer for fantasy meadow and garden scenes.",
    },
    "blossom_path": {
        "label": "Blossom Path",
        "graph": GRAPH_BLOSSOM_PATH,
        "role": "petal",
        "material": MI_SAKURA_PETALS,
        "density": 0.18,
        "voxel_cm": 160.0,
        "use_surface_tag": True,
        "spawn_exclusion": True,
        "transform_jitter": 32.0,
        "scale": (PETAL_SCALE_MIN, PETAL_SCALE_MAX),
        "seed": SEED_PETALS,
        "notes": "Readable petal scatter intended for paths, shrine approaches, and reveal shots.",
    },
    "lantern_grove": {
        "label": "Lantern Grove",
        "graph": GRAPH_LANTERN_GROVE,
        "role": "lantern",
        "material": MI_SAKURA_GRASS,
        "density": 0.08,
        "voxel_cm": 420.0,
        "use_surface_tag": False,
        "spawn_exclusion": True,
        "transform_jitter": 40.0,
        "scale": (DECOR_SCALE_MIN, DECOR_SCALE_MAX),
        "seed": SEED_DECOR,
        "notes": "Sparse vertical accent scatter for magical grove or festival staging.",
    },
    "garden_ruins": {
        "label": "Garden Ruins",
        "graph": GRAPH_GARDEN_RUINS,
        "role": "ruin",
        "material": MI_GREYBOX_ROCK,
        "density": 0.10,
        "voxel_cm": 360.0,
        "use_surface_tag": False,
        "spawn_exclusion": True,
        "transform_jitter": 28.0,
        "scale": (0.8, 1.8),
        "seed": SEED_DECOR + 1,
        "notes": "Low-frequency blockout ruin accents for garden/courtyard compositions.",
    },
    "sakura_petal_drift": {
        "label": "Sakura Petal Drift",
        "graph": GRAPH_PETAL_DRIFT,
        "role": "petal",
        "material": MI_SAKURA_PETALS,
        "density": 0.22,
        "voxel_cm": 150.0,
        "use_surface_tag": True,
        "spawn_exclusion": True,
        "transform_jitter": 45.0,
        "scale": (PETAL_SCALE_MIN, PETAL_SCALE_MAX),
        "seed": SEED_PETALS + 1,
        "notes": "Sakura-specific petal layer that stays separate from universal grass.",
    },
    "zen_moss_groundcover": {
        "label": "Zen Moss Groundcover",
        "graph": GRAPH_MOSS_GROUNDCOVER,
        "role": "moss",
        "material": MI_SAKURA_GRASS,
        "density": 0.34,
        "voxel_cm": 210.0,
        "use_surface_tag": True,
        "spawn_exclusion": True,
        "transform_jitter": 18.0,
        "scale": (0.45, 0.9),
        "seed": SEED_FOLIAGE + 1,
        "notes": "Quiet Zen groundcover layer for shrine gardens and neutral template captures.",
    },
    "desert_arid": {
        "label": "Desert Arid",
        "graph": GRAPH_DESERT_ARID,
        "role": "cactus",
        "material": MI_GREYBOX_ROCK,
        "density": 0.12,
        "voxel_cm": 400.0,
        "use_surface_tag": False,
        "spawn_exclusion": True,
        "transform_jitter": 35.0,
        "scale": (0.8, 2.2),
        "seed": SEED_DECOR + 2,
        "notes": "Arid desert floor with sparse cactus/agave accents and wind-swept rock formations.",
    },
    "desert_oasis": {
        "label": "Desert Oasis",
        "graph": GRAPH_DESERT_OASIS,
        "role": "grass",
        "material": MI_SAKURA_GRASS,
        "density": 0.28,
        "voxel_cm": 200.0,
        "use_surface_tag": True,
        "spawn_exclusion": True,
        "transform_jitter": 22.0,
        "scale": (0.5, 0.9),
        "seed": SEED_BLOSSOMS + 1,
        "notes": "Dense green groundcover pocket for oasis reveal in desert compositions.",
    },
    "cyberpunk_alley": {
        "label": "Cyberpunk Alley",
        "graph": GRAPH_CYBERPUNK_ALLEY,
        "role": "neon",
        "material": MI_GREYBOX_GRASS,
        "density": 0.15,
        "voxel_cm": 320.0,
        "use_surface_tag": False,
        "spawn_exclusion": True,
        "transform_jitter": 30.0,
        "scale": (0.6, 1.5),
        "seed": SEED_DECOR + 3,
        "notes": "Neon-lit urban alley scatter: glass bottles, metallic debris, holographic deco.",
    },
    "cyberpunk_rooftop": {
        "label": "Cyberpunk Rooftop",
        "graph": GRAPH_CYBERPUNK_ROOF,
        "role": "structural",
        "material": MI_GREYBOX_ROCK,
        "density": 0.08,
        "voxel_cm": 500.0,
        "use_surface_tag": False,
        "spawn_exclusion": False,
        "transform_jitter": 45.0,
        "scale": (0.7, 1.8),
        "seed": SEED_DECOR + 4,
        "notes": "Sparse rooftop structural kit for elevated cyberpunk cityscapes.",
    },
    "alpine_pine_forest": {
        "label": "Alpine Pine Forest",
        "graph": GRAPH_ALPINE_PINE,
        "role": "alpine_ground",
        "material": MI_GREYBOX_GRASS,
        "density": 0.30,
        "voxel_cm": 220.0,
        "use_surface_tag": True,
        "spawn_exclusion": True,
        "transform_jitter": 20.0,
        "scale": (0.5, 1.2),
        "seed": SEED_FOLIAGE + 2,
        "notes": "Pine forest ground layer with rocky scree and mossy boulder accents.",
    },
    "alpine_scree": {
        "label": "Alpine Scree",
        "graph": GRAPH_ALPINE_SCREE,
        "role": "scree",
        "material": MI_GREYBOX_ROCK,
        "density": 0.18,
        "voxel_cm": 300.0,
        "use_surface_tag": False,
        "spawn_exclusion": True,
        "transform_jitter": 28.0,
        "scale": (0.4, 1.0),
        "seed": SEED_ROCKS + 1,
        "notes": "High-altitude scree slope: fractured rock, loose talus, sparse alpine groundcover.",
    },
    "sakura_grove": {
        "label": "Sakura Grove",
        "graph": GRAPH_SAKURA_GROVE,
        "role": "flower",
        "material": MI_SAKURA_GRASS,
        "density": 0.35,
        "voxel_cm": 180.0,
        "use_surface_tag": True,
        "spawn_exclusion": True,
        "transform_jitter": 25.0,
        "scale": (FLOWER_SCALE_MIN, FLOWER_SCALE_MAX),
        "seed": SEED_BLOSSOMS,
        "notes": "Sakura tree grove with scattered blossoms on surface.",
    },
    "ornamental_architecture": {
        "label": "Ornamental Architecture",
        "graph": GRAPH_ORNAMENTAL_ARCH,
        "role": "ornamental_hero",
        "material": MI_GREYBOX_ROCK,
        "density": 0.03,
        "voxel_cm": 600.0,
        "use_surface_tag": True,
        "spawn_exclusion": True,
        "transform_jitter": 15.0,
        "scale": (0.8, 1.5),
        "seed": SEED_ARCH,
        "notes": "Landmark ornamental pieces: rose windows, oculus frames, spiral staircases, vault ribs for cathedral/castle reveals.",
    },
    "ornamental_detail_layer": {
        "label": "Ornamental Detail Layer",
        "graph": GRAPH_ORNAMENTAL_DETAIL,
        "role": "ornamental_detail",
        "material": MI_GREYBOX_ROCK,
        "density": 0.08,
        "voxel_cm": 300.0,
        "use_surface_tag": True,
        "spawn_exclusion": True,
        "transform_jitter": 25.0,
        "scale": (0.5, 1.2),
        "seed": SEED_DECOR + 5,
        "notes": "Secondary ornamental scatter: capitals, corbels, moldings, filigree, tracery for architectural richness.",
    },
}
MELODIA_TIER_HINTS: dict[str, str] = {
    "PCGCol_": "A",
    "MeadowFalloff": "B",
    "MelodiaForest": "B",
    "ForestScatter": "B",
    "SplinePath": "B",
    "WallGarden": "B",
    "Sub_Baroque": "C",
    "Baroque": "C",
    "DreamWalls": "D",
    "Bezier": "D",
    "PCGResearch": "E",
    "Escher": "E",
    "Penrose": "E",
}

PCG_PYTHON_OWNERS: dict[str, str] = {
    GRAPH_FOLIAGE: "setup_pcg_universal.py",
    GRAPH_ROCK: "setup_pcg_universal.py",
    GRAPH_WALL_IVY: "setup_pcg_universal.py",
    GRAPH_WALL_MOSS: "setup_pcg_universal.py",
    GRAPH_WALL_LICHEN: "setup_pcg_universal.py",
    GRAPH_WALL_DUST: "setup_pcg_universal.py",
    GRAPH_WALL_GRAFFITI: "setup_pcg_universal.py",
    GRAPH_EXCLUSION: "setup_pcg_universal.py",
    GRAPH_MEADOW_BLOOM: "setup_pcg_universal.py",
    GRAPH_BLOSSOM_PATH: "setup_pcg_universal.py",
    GRAPH_LANTERN_GROVE: "setup_pcg_universal.py",
    GRAPH_GARDEN_RUINS: "setup_pcg_universal.py",
    GRAPH_PETAL_DRIFT: "setup_pcg_universal.py",
    GRAPH_MOSS_GROUNDCOVER: "setup_pcg_universal.py",
    GRAPH_GREYBOX_MINIMAL: "setup_pcg_greybox.py",
    GRAPH_GREYBOX_STANDARD: "setup_pcg_greybox.py",
    GRAPH_SAKURA_SHOWCASE: "setup_pcg_greybox.py",
    GRAPH_DESERT_ARID: "setup_pcg_universal.py",
    GRAPH_DESERT_OASIS: "setup_pcg_universal.py",
    GRAPH_CYBERPUNK_ALLEY: "setup_pcg_universal.py",
    GRAPH_CYBERPUNK_ROOF: "setup_pcg_universal.py",
    GRAPH_ALPINE_PINE: "setup_pcg_universal.py",
    GRAPH_ALPINE_SCREE: "setup_pcg_universal.py",
    GRAPH_SAKURA_GROVE: "setup_pcg_universal.py",
}

ALL_PORTFOLIO_DIRS = (
    PCG_ROOT,
    DIR_UNIVERSAL,
    DIR_SUBGRAPHS,
    DIR_GREYBOX,
    DIR_COLLECTIONS,
    f"{DIR_STYLES}/Sakura",
    f"{DIR_STYLES}/Baroque",
    DIR_DESERT,
    DIR_CYBERPUNK,
    DIR_ALPINE,
    DIR_DEPRECATED,
)


def resolve_mesh(role: str):
    try:
        import unreal
    except ImportError:
        paths = SCATTER_MESHES.get(role, [])
        return paths[0] if paths else None
    for path in SCATTER_MESHES.get(role, []):
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            return path
    return None


def melodia_tier(asset_name: str) -> str:
    for frag, tier in MELODIA_TIER_HINTS.items():
        if frag in asset_name:
            return tier
    if asset_name.startswith("PCG_"):
        return "B"
    return "E"
