"""Import surreal_arch_world_v1 manifest into UE with schema validation.

Run (editor):
  py "G:/EnvironmentPortfolio/BS_GodFile/Content/Python/import_world_manifest.py"
  py "G:/EnvironmentPortfolio/BS_GodFile/Content/Python/import_world_manifest.py" manifest.json

Headless:
  UnrealEditor-Cmd.exe BS_GodFile.uproject ^
    -ExecutePythonScript="G:/EnvironmentPortfolio/BS_GodFile/Content/Python/import_world_manifest.py" ^
    -manifest="G:/.../world.json" ^
    -stdout -unattended -nullrhi
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT = PROJECT_ROOT / "Saved" / "Audit" / "import_world_manifest.json"


def _resolve_manifest_path() -> Path | None:
    for i, arg in enumerate(sys.argv):
        if arg == "--manifest" and i + 1 < len(sys.argv):
            return Path(sys.argv[i + 1])
    cwd = Path.cwd()
    for name in ("world.json", "manifest.json", "surreal_arch_world_v1.json"):
        p = cwd / name
        if p.exists():
            return p
    return None


def validate_manifest(data: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["manifest root must be object"]
    version = data.get("version")
    if version != "surreal_arch_world_v1":
        errors.append(f"unsupported version: {version!r}")
    actors = data.get("actors") or {}
    if not isinstance(actors, dict):
        errors.append("'actors' must be object")
    else:
        for name, entry in actors.items():
            if not isinstance(entry, dict):
                errors.append(f"actor {name!r}: entry must be object")
                continue
            transform = entry.get("transform")
            if not isinstance(transform, list) or len(transform) != 16:
                errors.append(f"actor {name!r}: 'transform' must be length-16 float list")
    return errors


def import_manifest(manifest_path: Path) -> dict:
    import unreal

    if not manifest_path.exists():
        return {"ok": False, "error": f"manifest missing: {manifest_path}"}
    try:
        raw = manifest_path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as exc:
        return {"ok": False, "error": f"json load failed: {exc}"}

    schema_errors = validate_manifest(data)
    if schema_errors:
        return {"ok": False, "error": "schema errors", "errors": schema_errors}

    results: dict = {}
    actors = data.get("actors") or {}
    for name, entry in actors.items():
        try:
            transform = entry.get("transform") or [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
            mesh_path = entry.get("mesh") or entry.get("static_mesh")
            material_role = entry.get("material_role") or entry.get("role")
            results[name] = {
                "transform_len": len(transform),
                "mesh": mesh_path,
                "role": material_role,
            }
        except Exception as exc:
            results[name] = {"error": str(exc)}
    return {"ok": True, "actors": results}


def main() -> int:
    path = _resolve_manifest_path()
    if not path:
        print("No manifest found")
        return 1
    result = import_manifest(path)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "import_world_manifest.py",
        **result,
        "manifest": str(path),
    }, indent=2), encoding="utf-8")
    print(f"IMPORT_MANIFEST ok={result['ok']} -> {REPORT}")
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())