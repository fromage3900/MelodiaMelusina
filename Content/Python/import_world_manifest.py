"""Validate or apply the canonical Surreal world manifest in Unreal Engine.

Default execution is a non-mutating preflight. Pass ``--apply`` to create one
actor containing HISM components grouped by canonical static mesh and role.
Applying requires every group to resolve a ``/Game/...`` static mesh path.
"""
from __future__ import annotations

import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from gmm.pcg.manifest import manifest_summary, validate_manifest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT = PROJECT_ROOT / "Saved" / "Audit" / "import_world_manifest.json"


def _has_arg(name: str) -> bool:
    return any(arg.lower() == name.lower() for arg in sys.argv)


def _resolve_manifest_path() -> Path | None:
    for i, arg in enumerate(sys.argv):
        if arg in ("--manifest", "-manifest") and i + 1 < len(sys.argv):
            return Path(sys.argv[i + 1])
        if arg.startswith("-manifest="):
            return Path(arg.split("=", 1)[1].strip('"'))
    for arg in sys.argv[1:]:
        candidate = Path(arg.strip('"'))
        if candidate.suffix.lower() == ".json" and candidate.is_file():
            return candidate
    cwd = Path.cwd()
    candidates = sorted(cwd.glob("*.world.json"))
    for name in ("world.json", "manifest.json", "surreal_arch_world_v1.json"):
        path = cwd / name
        if path.exists():
            candidates.append(path)
    return candidates[0] if candidates else None


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_") or "World"


def _blender_matrix_to_unreal(matrix: list[list[float]]):
    """Convert a Blender Z-up/metres matrix to an Unreal transform.

    The Y reflection changes handedness; translation is converted to cm.
    """
    import unreal

    c = (1.0, -1.0, 1.0)
    basis = [[c[row] * float(matrix[row][col]) * c[col] for col in range(3)] for row in range(3)]
    scales = [math.sqrt(sum(basis[row][col] ** 2 for row in range(3))) for col in range(3)]
    if any(scale <= 1e-8 for scale in scales):
        raise ValueError("matrix contains a zero-scale axis")
    rotation = [[basis[row][col] / scales[col] for col in range(3)] for row in range(3)]

    sy = math.sqrt(rotation[0][0] ** 2 + rotation[1][0] ** 2)
    if sy > 1e-6:
        roll = math.atan2(rotation[2][1], rotation[2][2])
        pitch = math.atan2(-rotation[2][0], sy)
        yaw = math.atan2(rotation[1][0], rotation[0][0])
    else:
        roll = math.atan2(-rotation[1][2], rotation[1][1])
        pitch = math.atan2(-rotation[2][0], sy)
        yaw = 0.0

    location = unreal.Vector(
        float(matrix[0][3]) * 100.0,
        -float(matrix[1][3]) * 100.0,
        float(matrix[2][3]) * 100.0,
    )
    rotator = unreal.Rotator(math.degrees(pitch), math.degrees(yaw), math.degrees(roll))
    scale = unreal.Vector(*scales)
    return unreal.Transform(location, rotator, scale)


def _find_actor(eas, label: str):
    for actor in eas.get_all_level_actors() or []:
        if actor.get_actor_label() == label:
            return actor
    return None


def _apply_manifest(data: dict, *, replace: bool = True) -> dict:
    import unreal

    errors = validate_manifest(data, require_resolved_meshes=True)
    if errors:
        return {"ok": False, "applied": False, "errors": errors}

    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    label = f"GMM_World_{_safe_name(str(data.get('world_root', 'World')))}"
    previous = _find_actor(eas, label)
    if previous and not replace:
        return {"ok": False, "applied": False, "errors": [f"actor {label!r} already exists"]}

    actor = eas.spawn_actor_from_class(unreal.Actor, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(0.0, 0.0, 0.0))
    if not actor:
        return {"ok": False, "applied": False, "errors": ["failed to create world actor"]}
    actor.set_actor_label(f"{label}__IMPORTING")
    actor.tags = [unreal.Name("GMM.WorldManifest"), unreal.Name(str(data.get("format")))]

    groups_result: list[dict] = []
    try:
        for index, group in enumerate(data.get("hism_groups", [])):
            mesh_path = group.get("static_mesh_path", "")
            mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
            if not mesh:
                raise RuntimeError(f"group {index} mesh failed to load: {mesh_path}")
            component_name = f"HISM_{index:03d}_{_safe_name(str(group.get('role', 'Role')))}"
            component = unreal.new_object(unreal.HierarchicalInstancedStaticMeshComponent, actor, component_name)
            if not component:
                raise RuntimeError(f"failed to create {component_name}")
            component.set_static_mesh(mesh)
            material_path = group.get("ue_material_hint", "")
            if material_path:
                material = unreal.EditorAssetLibrary.load_asset(material_path)
                if material:
                    component.set_material(0, material)
            actor.add_instance_component(component)
            component.register_component()
            for matrix in group.get("transforms", []):
                transform = _blender_matrix_to_unreal(matrix)
                try:
                    component.add_instance(transform, world_space=True)
                except TypeError:
                    component.add_instance(transform)
            groups_result.append({
                "component": component_name,
                "role": group.get("role"),
                "mesh": mesh_path,
                "instance_count": component.get_instance_count(),
            })
    except Exception as exc:
        eas.destroy_actor(actor)
        return {
            "ok": False,
            "applied": False,
            "errors": [str(exc)],
            "rolled_back": previous is not None,
            "previous_actor_preserved": previous is not None,
        }

    if previous:
        eas.destroy_actor(previous)
    actor.set_actor_label(label)
    return {
        "ok": True,
        "applied": True,
        "actor": label,
        "group_count": len(groups_result),
        "instance_count": sum(group["instance_count"] for group in groups_result),
        "groups": groups_result,
    }


def import_manifest(manifest_path: Path, *, apply: bool = False, replace: bool = True) -> dict:
    if not manifest_path.exists():
        return {"ok": False, "error": f"manifest missing: {manifest_path}"}
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"ok": False, "error": f"JSON load failed: {exc}"}

    summary = manifest_summary(data, require_resolved_meshes=apply)
    if not summary["ok"]:
        return {"ok": False, "applied": False, "validation": summary}
    if not apply:
        return {"ok": True, "applied": False, "mode": "preflight", "validation": summary}
    return {"validation": summary, **_apply_manifest(data, replace=replace)}


def main() -> int:
    path = _resolve_manifest_path()
    if not path:
        print("No manifest found; pass --manifest <path>")
        return 1
    result = import_manifest(path, apply=_has_arg("--apply"), replace=not _has_arg("--no-replace"))
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "import_world_manifest.py",
        **result,
        "manifest": str(path.resolve()),
    }, indent=2), encoding="utf-8")
    print(f"IMPORT_MANIFEST ok={result.get('ok', False)} applied={result.get('applied', False)} -> {REPORT}")
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
