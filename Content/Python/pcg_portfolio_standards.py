"""EnvSandbox universal PCG portfolio standards — paths, tags, presets, ISM bands."""
from __future__ import annotations

PCG_ROOT = "/Game/EnvSandbox/PCG"
MELODIA_PCG_ROOT = "/Game/_PROJECT/PCG"

DIR_UNIVERSAL = f"{PCG_ROOT}/Universal"
DIR_SUBGRAPHS = f"{PCG_ROOT}/Universal/Subgraphs"
DIR_GREYBOX = f"{PCG_ROOT}/Greybox"
DIR_COLLECTIONS = f"{PCG_ROOT}/Collections"
DIR_STYLES = f"{PCG_ROOT}/Styles"
DIR_DEPRECATED = f"{PCG_ROOT}/_Deprecated"

GRAPH_FOLIAGE = f"{DIR_UNIVERSAL}/PCG_FoliageDensity"
GRAPH_ROCK = f"{DIR_UNIVERSAL}/PCG_RockScatter"
GRAPH_WALL = f"{DIR_UNIVERSAL}/PCG_WallDetail"
GRAPH_EXCLUSION = f"{DIR_SUBGRAPHS}/PCG_ExclusionFalloff"
GRAPH_GREYBOX_MINIMAL = f"{DIR_GREYBOX}/PCG_Greybox_Minimal"
GRAPH_GREYBOX_STANDARD = f"{DIR_GREYBOX}/PCG_Greybox_Standard"
GRAPH_SAKURA_SHOWCASE = f"{DIR_STYLES}/Sakura/PCG_Sakura_Showcase"

SMC_PORTFOLIO = f"{DIR_COLLECTIONS}/SMC_Portfolio_ScatterKit"
SMC_GREYBOX = f"{DIR_COLLECTIONS}/SMC_Greybox_ScatterKit"
SMC_SAKURA = f"{DIR_STYLES}/Sakura/SMC_Sakura_ScatterKit"
SMC_BAROQUE = f"{DIR_STYLES}/Baroque/SMC_Baroque_ScatterKit"

ORPHAN_MEADOW_SCATTER = f"{PCG_ROOT}/PCG_MeadowScatter"
DEPRECATED_MEADOW = f"{DIR_DEPRECATED}/PCG_MeadowScatter"

LEVEL_TEMPLATE = "/Game/EnvSandbox/_Template/L_Template"
LEVEL_SAKURA = "/Game/EnvSandbox/Environments/Sakura/L_SakuraPath"

SHIPPING_LEVELS = (
    LEVEL_TEMPLATE,
    LEVEL_SAKURA,
    "/Game/EnvSandbox/VFX/_Showcase/L_VFX_Showcase",
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

# Melodia salvage defaults (Tier B — meadow/forest reference).
DEFAULT_VOXEL_CM = 180.0
DEFAULT_DENSITY = 0.42
DEFAULT_EXCLUDE_FALLOFF = 220.0
SPACING_PRUNE_RADIUS_CM = 85.0

GROUND_HALF_EXTENT_UU = 3000.0
PCG_VOLUME_CENTER = (0.0, 0.0, 28.0)
PCG_VOLUME_SCALE = (52.0, 52.0, 3.0)

GRASS_SCALE_MIN = 0.6
GRASS_SCALE_MAX = 1.0
ROCK_SCALE_MIN = 0.4
ROCK_SCALE_MAX = 1.2

ISM_BAND_PORTFOLIO = (250, 1600)
ISM_BAND_SAKURA = (320, 1800)
ISM_BAND_MINIMAL = (120, 900)

MI_GREYBOX_GRASS = "/Game/EnvSandbox/Materials/Instances/Showcase/MI_Show_ForestFoliage"
MI_GREYBOX_ROCK = "/Game/EnvSandbox/Materials/Instances/Landscape/MI_Landscape_Meadow"
MI_SAKURA_GRASS = "/Game/EnvSandbox/Materials/Instances/Sakura/MI_Sakura_Grass"
MI_SAKURA_PETALS = "/Game/EnvSandbox/Materials/Instances/Sakura/MI_Sakura_Petals"

SCATTER_MESHES: dict[str, list[str]] = {
    "grass": [
        "/Game/Greybox_Kit/SM_Block_Cube_1.SM_Block_Cube_1",
        "/Engine/BasicShapes/Cone.Cone",
        "/Engine/BasicShapes/Cylinder.Cylinder",
    ],
    "rock": [
        "/Game/Greybox_Kit/SM_Block_Cube_1.SM_Block_Cube_1",
        "/Engine/BasicShapes/Cube.Cube",
    ],
    "petal": ["/Engine/BasicShapes/Plane.Plane"],
    "flower": ["/Engine/BasicShapes/Cone.Cone"],
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
        "foliage_graph": GRAPH_SAKURA_SHOWCASE,
    },
}

# Melodia salvage tier hints by asset name fragment.
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
    GRAPH_WALL: "setup_pcg_universal.py",
    GRAPH_EXCLUSION: "setup_pcg_universal.py",
    GRAPH_GREYBOX_MINIMAL: "setup_pcg_greybox.py",
    GRAPH_GREYBOX_STANDARD: "setup_pcg_greybox.py",
    GRAPH_SAKURA_SHOWCASE: "setup_pcg_greybox.py",
}

ALL_PORTFOLIO_DIRS = (
    PCG_ROOT,
    DIR_UNIVERSAL,
    DIR_SUBGRAPHS,
    DIR_GREYBOX,
    DIR_COLLECTIONS,
    f"{DIR_STYLES}/Sakura",
    f"{DIR_STYLES}/Baroque",
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
