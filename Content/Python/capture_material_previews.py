"""Capture material thumbnail previews to Saved/Portfolio/MaterialPreviews/.

Scans MASTER_DIR and ENV_INST_DIR for materials, renders a small preview
using UE automation thumbnail capture when available, otherwise records
metadata only.

Run (editor):
  py "G:/EnvironmentPortfolio/BS_GodFile/Content/Python/capture_material_previews.py"
"""
from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import material_lib as lib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = PROJECT_ROOT / "Saved" / "Portfolio" / "MaterialPreviews"
REPORT = OUT_DIR / "previews_manifest.json"


def _material_label(asset) -> str:
    try:
        return asset.get_editor_property("asset_name") or asset.get_name()
    except Exception:
        return asset.get_name()


def _thumb_path(asset_path: str, asset_name: str) -> Path:
    digest = hashlib.sha1(asset_path.encode("utf-8")).hexdigest()[:10]
    safe_name = "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in asset_name)
    return OUT_DIR / f"thumb_{safe_name}_{digest}.png"


def _capture_thumbnail(asset, *, asset_path: str) -> tuple[str | None, str | None]:
    import unreal

    try:
        options = unreal.AssetThumbnailCaptureOptions()
        options.size = unreal.IntPoint(256, 256)
        options.render_background = True
        options.background_color = unreal.LinearColor(0.15, 0.15, 0.15, 1.0)
        if not hasattr(unreal, "AutomationLibrary"):
            return None, "AutomationLibrary missing (cannot take thumbnails in this context)"
        out_path = _thumb_path(asset_path, asset.get_name())
        unreal.AutomationLibrary.take_thumbnail(asset, str(out_path), options)
        return str(out_path), None
    except Exception as exc:
        return None, str(exc)


def capture_material_previews() -> dict:
    import unreal

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dirs = [lib.MASTER_DIR, lib.ENV_INST_DIR]
    results = {}
    duplicates: list[dict] = []
    failures: list[dict] = []
    captured = 0
    scanned = 0

    automation_available = hasattr(unreal, "AutomationLibrary") and hasattr(
        unreal.AutomationLibrary, "take_thumbnail"
    )
    for folder in dirs:
        try:
            asset_list = unreal.EditorAssetLibrary.list_assets(folder, recursive=True)
        except Exception:
            asset_list = []
        for asset_path in asset_list:
            asset = unreal.load_asset(asset_path)
            if not asset:
                continue
            try:
                if not asset.is_a(unreal.MaterialInterface.static_class()):
                    continue
            except Exception:
                continue
            scanned += 1
            name = asset.get_name()
            entry = {"path": asset_path, "label": _material_label(asset)}
            thumb, error = _capture_thumbnail(asset, asset_path=asset_path)
            if thumb:
                captured += 1
                entry["thumbnail"] = thumb
                try:
                    entry["thumbnail_rel"] = str(Path(thumb).resolve().relative_to(PROJECT_ROOT))
                except Exception:
                    entry["thumbnail_rel"] = None
            elif error:
                # Keep only a small sample of failure details to avoid huge manifests.
                if len(failures) < 25:
                    failures.append({"material": name, "path": asset_path, "error": error})

            key = name
            if key in results:
                digest = hashlib.sha1(asset_path.encode("utf-8")).hexdigest()[:10]
                key = f"{name}__{digest}"
                duplicates.append({"name": name, "key": key, "path": asset_path})
            results[key] = entry

    return {
        "ok": True,
        "count": len(results),
        "materials": results,
        "stats": {
            "folders_scanned": dirs,
            "assets_scanned": scanned,
            "thumbnails_captured": captured,
            "automation_available": automation_available,
            "duplicates": len(duplicates),
            "failure_samples": len(failures),
        },
        "duplicates": duplicates,
        "failure_samples": failures,
    }


def write_previews_manifest() -> Path:
    """Capture previews and write previews_manifest.json; returns the path."""
    result = capture_material_previews()
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "capture_material_previews.py",
        "ok": result.get("ok", False),
        **result,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return REPORT


def main() -> int:
    path = write_previews_manifest()
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(f"MATERIAL_PREVIEWS captured={payload.get('count', 0)} -> {path}")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())