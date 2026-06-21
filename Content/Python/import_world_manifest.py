"""Import surreal_arch_world_v1 manifest into UE5 as instanced static mesh actors.

Run in Unreal Editor Python console:
  import import_world_manifest
  import_world_manifest.import_manifest(r"path/to/WorldRoot.world.json")

Optional FBX import: place role FBX files in same folder as manifest under WorldExport/.
"""
from __future__ import annotations

import json
import os
import math

try:
    import unreal
except ImportError:
    unreal = None  # type: ignore

FORMAT_ID = "surreal_arch_world_v1"
IMPORT_ROOT = "/Game/EnvSandbox/WorldImport"
MATERIALS_ROOT = "/Game/EnvSandbox/Materials/Instances/Environment"


def _load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate_manifest(payload: dict) -> list[str]:
    errors = []
    if payload.get("format") != FORMAT_ID:
        errors.append(f"format must be {FORMAT_ID}")
    if payload.get("schema_version", 0) < 1:
        errors.append("schema_version must be >= 1")
    if payload.get("instance_count", 0) != len(payload.get("instances", [])):
        errors.append("instance_count mismatch")
    return errors


def _blender_to_ue_location(matrix: list[list[float]]) -> tuple[float, float, float]:
    """Convert Blender matrix translation to UE coordinates (cm, left-handed)."""
    bx, by, bz = matrix[0][3], matrix[1][3], matrix[2][3]
    return (bx * 100.0, by * 100.0, bz * 100.0)


def _blender_to_ue_rotation(matrix: list[list[float]]) -> unreal.Rotator:
    """Approximate rotation from Blender matrix (Z-up) to UE (Z-up, different forward)."""
    import math as _math
    m00, m10 = matrix[0][0], matrix[1][0]
    yaw = _math.degrees(_math.atan2(m10, m00))
    return unreal.Rotator(0.0, yaw, 0.0)


def resolve_material(hint: str):
    if unreal is None:
        return None
    if not hint:
        return None
    asset = unreal.load_asset(hint)
    if asset:
        return asset
    stem = hint.rsplit("/", 1)[-1]
    fallback = f"{MATERIALS_ROOT}/Stylized/MI_Show_Default"
    return unreal.load_asset(fallback)


def resolve_static_mesh(lib_name: str, world_root: str, import_dir: str | None):
    if unreal is None:
        return None
    slug = lib_name.replace("_lib_", "") if lib_name else "Unknown"
    candidates = [
        f"{IMPORT_ROOT}/{world_root}/SM_{slug}",
        f"{IMPORT_ROOT}/{world_root}/World_{slug}",
    ]
    for path in candidates:
        mesh = unreal.load_asset(path)
        if mesh:
            return mesh
    if import_dir:
        fbx = os.path.join(import_dir, f"World_{slug}.fbx")
        if os.path.isfile(fbx):
            task = unreal.AssetImportTask()
            task.set_editor_property("filename", fbx)
            task.set_editor_property("destination_path", f"{IMPORT_ROOT}/{world_root}")
            task.set_editor_property("automated", True)
            task.set_editor_property("save", True)
            task.set_editor_property("replace_existing", True)
            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
            return unreal.load_asset(f"{IMPORT_ROOT}/{world_root}/{os.path.splitext(os.path.basename(fbx))[0]}")
    return None


def spawn_hism_group(world, group: dict, world_root: str, import_dir: str | None):
    if unreal is None:
        return None
    lib = group.get("lib", "")
    mesh = resolve_static_mesh(lib, world_root, import_dir)
    if mesh is None:
        unreal.log_warning(f"[WorldImport] no mesh for {lib} — skipping group")
        return None

    mat = resolve_material(group.get("ue_material_hint", ""))
    labels = []
    for i, xf in enumerate(group.get("transforms", [])):
        loc = _blender_to_ue_location(xf)
        rot = _blender_to_ue_rotation(xf)
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.StaticMeshActor,
            unreal.Vector(*loc),
            rot,
        )
        role = group.get("role", "misc")
        actor.set_actor_label(f"World_{role}_{lib.replace('_lib_', '')}_{i:03d}")
        sm = actor.static_mesh_component
        sm.set_static_mesh(mesh)
        if mat:
            sm.set_material(0, mat)
        labels.append(actor.get_actor_label())

    unreal.log(f"[WorldImport] spawned {len(labels)} actors for {lib}")
    return labels


def import_manifest(manifest_path: str, import_fbx_dir: str | None = None) -> dict:
    """Import a .world.json manifest. Returns summary dict."""
    if unreal is None:
        raise RuntimeError("unreal module not available — run inside Unreal Editor")

    payload = _load_json(manifest_path)
    errors = validate_manifest(payload)
    if errors:
        raise ValueError(f"Invalid manifest: {errors}")

    world_root = payload.get("world_root", "World")
    import_dir = import_fbx_dir or os.path.join(os.path.dirname(manifest_path), "WorldExport")
    unreal.EditorAssetLibrary.make_directory(f"{IMPORT_ROOT}/{world_root}")

    spawned = []
    for group in payload.get("hism_groups", []):
        labels = spawn_hism_group(unreal.EditorLevelLibrary.get_editor_world(), group, world_root, import_dir)
        if labels:
            spawned.extend(labels)

    summary = {
        "world_root": world_root,
        "style": payload.get("style"),
        "instance_count": payload.get("instance_count", 0),
        "hism_groups": len(payload.get("hism_groups", [])),
        "spawned_actors": spawned,
    }
    unreal.log(f"[WorldImport] {summary}")
    print(f"[WorldImport] {summary}")
    return summary


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: import_world_manifest.py <path/to/world.json>")
    else:
        import_manifest(sys.argv[1])
