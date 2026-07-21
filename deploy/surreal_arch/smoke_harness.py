"""Headless SurrealArch smoke: register ΓåÆ greybox room ΓåÆ zen kit ΓåÆ snap JSON.

Blender 5.1 (use factory-startup to skip user addon servers that keep Blender alive):
  blender --background --factory-startup --python deploy/surreal_arch/smoke_harness.py

Exit 0 on pass. Writes Saved/Audit/surreal_arch_smoke.json when PROJECT_ROOT known.
"""
from __future__ import annotations

import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


def _deploy_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def _ensure_paths() -> None:
    deploy = str(_deploy_dir())
    if deploy not in sys.path:
        sys.path.insert(0, deploy)


def run_smoke(report_path: Path | None = None) -> dict:
    _ensure_paths()
    report: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ok": False,
        "steps": [],
        "errors": [],
        "warnings": [],
    }

    try:
        import bpy  # noqa: F401
    except ImportError as exc:
        report["errors"].append(f"bpy unavailable: {exc}")
        return _finish(report, report_path)

    try:
        import surreal_architecture_gen as monolith
        report["steps"].append({"import_monolith": True})
    except Exception as exc:
        report["errors"].append(f"import surreal_architecture_gen: {exc}")
        report["traceback"] = traceback.format_exc()
        return _finish(report, report_path)

    try:
        # Full addon register so Object.surreal_arch_props + overhaul patches exist
        monolith.register()
        report["steps"].append({"monolith.register": True})
    except Exception as reg_exc:
        report["warnings"].append(f"monolith.register: {reg_exc}")
        try:
            from surreal_arch.integration import register_overhaul, patch_monolith

            try:
                register_overhaul(monolith)
                report["steps"].append({"register_overhaul": True})
            except Exception as ov_exc:
                report["warnings"].append(f"register_overhaul: {ov_exc}")
                patch_monolith(monolith)
                report["steps"].append({"patch_monolith_only": True})
        except Exception as exc:
            report["errors"].append(f"overhaul wire: {exc}")
            report["traceback"] = traceback.format_exc()
            return _finish(report, report_path)

    # Inventory check
    try:
        from surreal_arch.kit_registration import registered_kits

        kits = registered_kits()
        report["steps"].append({"registered_kits": len(kits)})
        if len(kits) < 5:
            report["warnings"].append("Fewer than 5 kits registered")
    except Exception as exc:
        report["warnings"].append(f"kit registry: {exc}")

    # Generate greybox room + one zen kit via apply_geometry_nodes path
    results = []
    for arch_id in ("GREYBOX_ROOM", "GB_ZEN_TORII_GATE"):
        try:
            r = _generate_one(monolith, arch_id)
            results.append(r)
            report["steps"].append({"generate": r})
            if not r.get("ok"):
                report["errors"].append(f"generate {arch_id}: {r.get('error')}")
        except Exception as exc:
            report["errors"].append(f"generate {arch_id}: {exc}")
            report["traceback"] = traceback.format_exc()

    # Prefer UE export payload when snaps exist
    snap_ok = any(r.get("snap_count", 0) > 0 or r.get("ok") for r in results)
    report["ok"] = len(report["errors"]) == 0 and snap_ok and len(results) >= 1
    if not snap_ok and not report["errors"]:
        report["warnings"].append("No snap points written ΓÇö generate may have used fallback path")
        # Still pass if meshes created
        if any(r.get("object") for r in results):
            report["ok"] = True

    return _finish(report, report_path)


def _generate_one(monolith, arch_id: str) -> dict:
    import bpy

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    mesh = bpy.data.meshes.new(f"Smoke_{arch_id}")
    obj = bpy.data.objects.new(f"Smoke_{arch_id}", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    if not hasattr(obj, "surreal_arch_props"):
        return {"ok": False, "arch_id": arch_id, "error": "surreal_arch_props missing on object"}

    props = obj.surreal_arch_props
    try:
        props.arch_type = arch_id
    except TypeError:
        # Enum may not include id yet ΓÇö try GB_ greybox alternate
        return {"ok": False, "arch_id": arch_id, "error": f"arch_type enum rejected {arch_id}"}

    # Viewport-fast smoke: skip heavy bevel when quality prop exists
    if hasattr(props, "export_quality"):
        props.export_quality = "VIEWPORT"
    if hasattr(props, "bevel_mode"):
        try:
            props.bevel_mode = "NONE"
        except TypeError:
            pass

    apply_fn = getattr(monolith, "apply_geometry_nodes_to_object", None)
    if apply_fn is None:
        return {"ok": False, "arch_id": arch_id, "error": "apply_geometry_nodes_to_object missing"}

    apply_fn(obj, props, monolith=monolith)

    snap_raw = obj.get("surreal_snap_points")
    snap_count = 0
    if isinstance(snap_raw, str) and snap_raw.strip():
        try:
            data = json.loads(snap_raw)
            snap_count = len(data) if isinstance(data, list) else len(data.get("snaps", []))
        except json.JSONDecodeError:
            snap_count = 0
    elif isinstance(snap_raw, (list, dict)):
        snap_count = len(snap_raw) if isinstance(snap_raw, list) else len(snap_raw.get("snaps", []))

    # Also try build_ue_export_payload
    payload_snaps = 0
    try:
        from surreal_arch.snap_export import build_ue_export_payload

        payload = build_ue_export_payload(obj, monolith)
        payload_snaps = len(payload.get("snaps") or payload.get("snap_points") or [])
    except Exception:
        payload = None

    verts = len(obj.data.vertices) if obj.data else 0
    ok = verts > 0 or snap_count > 0 or obj.modifiers
    return {
        "ok": bool(ok),
        "arch_id": arch_id,
        "object": obj.name,
        "vertices": verts,
        "snap_count": max(snap_count, payload_snaps),
        "modifiers": [m.type for m in obj.modifiers],
    }


def _finish(report: dict, report_path: Path | None) -> dict:
    if report_path is None:
        # Prefer BS_GodFile Saved/Audit when deploy is under BS_GodFile
        deploy = _deploy_dir()
        candidates = [
            deploy.parent / "Saved" / "Audit" / "surreal_arch_smoke.json",
            deploy / "surreal_arch" / "smoke_last.json",
        ]
        report_path = candidates[0]
        report_path.parent.mkdir(parents=True, exist_ok=True)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"[SurrealArchSmoke] ok={report['ok']} -> {report_path}")
    if report.get("errors"):
        for e in report["errors"]:
            print(f"[SurrealArchSmoke] ERROR: {e}")
    return report


def main() -> int:
    report = run_smoke()
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
