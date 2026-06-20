"""Sakura PCG portfolio standards — greybox placeholders, expected ISM bounds.

Phase 1 only: one stock graph (ground cover). Petals / path flowers deferred.
"""
from __future__ import annotations

try:
    import unreal
except ImportError:
    unreal = None  # type: ignore

PCG_ROOT = "/Game/EnvSandbox/PCG/Sakura"
MESH_KIT_DIR = "/Game/EnvSandbox/Meshes/Sakura/Greybox"
COLLECTION_PATH = f"{PCG_ROOT}/SMC_Sakura_ScatterKit"

GRAPH_GROUND_COVER = f"{PCG_ROOT}/PCG_Sakura_GroundCover"

LEVEL = "/Game/EnvSandbox/Environments/Sakura/L_SakuraPath"

# Greybox proxies — swap entries in the collection when CC0 kit lands.
SCATTER_MESHES: dict[str, list[str]] = {
    "grass": [
        "/Game/Greybox_Kit/SM_Block_Cube_1.SM_Block_Cube_1",
        "/Engine/BasicShapes/Cone.Cone",
        "/Engine/BasicShapes/Cylinder.Cylinder",
    ],
    "petal": [
        "/Engine/BasicShapes/Plane.Plane",
    ],
    "flower": [
        "/Engine/BasicShapes/Cone.Cone",
    ],
}

MI_GRASS = "/Game/EnvSandbox/Materials/Instances/Sakura/MI_Sakura_Grass"
MI_PETALS = "/Game/EnvSandbox/Materials/Instances/Sakura/MI_Sakura_Petals"

# Ground plane is 60× scale → ~6000 UU half-extent from center.
GROUND_HALF_EXTENT_UU = 3000.0
PCG_VOLUME_CENTER = (0.0, 0.0, 40.0)
PCG_VOLUME_SCALE = (52.0, 52.0, 3.0)  # slightly inset from 60× ground

# Voxel sampler — 150 cm keeps count in a sane band on ~6000² area.
GROUND_VOXEL_CM = 150.0
GRASS_SCALE_MIN = 0.6
GRASS_SCALE_MAX = 1.0

# Validation gates (Melodia-style predictable counts).
GROUND_COVER_ISM_MIN = 400
GROUND_COVER_ISM_MAX = 2500

TAG_GROUND = "PCG_Ground"
TAG_EXCLUDE = "PCG_Exclude"


def resolve_mesh(role: str) -> str | None:
    """First existing mesh path for a scatter role."""
    if unreal is None:
        return SCATTER_MESHES.get(role, [None])[0]
    for path in SCATTER_MESHES.get(role, []):
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            return path
    return None


def configure_grass_spawner(spawner_settings, material_path: str | None = None) -> bool:
    """Wire a single weighted mesh entry on a PCGStaticMeshSpawnerSettings."""
    if unreal is None:
        return False
    mesh_path = resolve_mesh("grass")
    if not mesh_path:
        unreal.log_warning("[SakuraPCG] no grass proxy mesh found")
        return False
    mesh = unreal.load_asset(mesh_path)
    if not mesh:
        unreal.log_warning(f"[SakuraPCG] failed to load mesh {mesh_path}")
        return False
    entry = unreal.PCGMeshSelectorWeightedEntry()
    desc = entry.get_editor_property("descriptor")
    desc.set_editor_property("static_mesh", mesh)
    if material_path and unreal.EditorAssetLibrary.does_asset_exist(material_path):
        mat = unreal.load_asset(material_path)
        if mat:
            desc.set_editor_property("material_override", mat)
    entry.set_editor_property("descriptor", desc)
    entry.set_editor_property("weight", 1)
    selector = spawner_settings.get_editor_property("mesh_selector_parameters")
    selector.set_editor_property("mesh_entries", [entry])
    return True


def apply_grass_transform(settings) -> None:
    """Random yaw, uniform scale band — no position jitter on first pass."""
    if unreal is None:
        return
    smin = float(GRASS_SCALE_MIN)
    smax = float(GRASS_SCALE_MAX)
    try:
        settings.set_editor_property("scale_min", unreal.Vector(smin, smin, smin))
        settings.set_editor_property("scale_max", unreal.Vector(smax, smax, smax))
        settings.set_editor_property("uniform_scale", True)
        settings.set_editor_property("rotation_min", unreal.Rotator(0, 0, 0))
        settings.set_editor_property("rotation_max", unreal.Rotator(0, 359.0, 0))
        settings.set_editor_property("absolute_rotation", False)
    except Exception as exc:
        unreal.log_warning(f"[SakuraPCG] transform settings: {exc}")
