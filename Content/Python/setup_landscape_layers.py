"""Create Landscape LayerInfo assets for M_Master_Toon_Landscape_HeightBlend painted layers.

Layer names must match MaterialExpressionLandscapeLayerSample parameter_name values
in setup_landscape_height_blend.py (Rock, Grass, Mud, Path).

Run (editor):
  py Content/Python/setup_landscape_layers.py

Headless:
  python Content/Python/setup_landscape_layers.py

Workflow:
  1. Create Landscape actor in editor
  2. Assign MI_Landscape_* from Instances/Landscape/
  3. Paint Rock / Grass / Mud / Path using these LayerInfo assets
  4. Enable bUsePaintedLayers on the MI when weights are painted (procedural fallback when sum ~ 0)
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LAYER_DIR = "/Game/EnvSandbox/Materials/Landscape"
REPORT = PROJECT_ROOT / "Saved" / "Audit" / "landscape_layers.json"
UE_CMD = Path(r"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe")
UPROJECT = PROJECT_ROOT / "BS_GodFile.uproject"

LAYER_SPECS: list[tuple[str, str, tuple[float, float, float, float]]] = [
    # Asset name == landscape layer name (LayerName is read-only after create_asset)
    ("Rock", "Rock", (0.55, 0.52, 0.50, 1.0)),
    ("Grass", "Grass", (0.20, 0.55, 0.18, 1.0)),
    ("Mud", "Mud", (0.35, 0.28, 0.18, 1.0)),
    ("Path", "Path", (0.62, 0.58, 0.52, 1.0)),
]

def _create_layer_info(tools, asset_name: str):
    import unreal

    li = tools.create_asset(asset_name, LAYER_DIR, unreal.LandscapeLayerInfoObject, None)
    if li:
        return li
    raise RuntimeError(f"Could not create LandscapeLayerInfoObject for {asset_name}")


def build() -> dict:
    import unreal

    unreal.EditorAssetLibrary.make_directory(LAYER_DIR)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    created: list[str] = []
    updated: list[str] = []

    for asset_name, layer_name, color in LAYER_SPECS:
        path = f"{LAYER_DIR}/{asset_name}"
        full = f"{path}.{asset_name}"
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            li = unreal.load_asset(full)
            updated.append(path)
        else:
            li = _create_layer_info(tools, asset_name)
            created.append(path)

        li.set_editor_property("hardness", 0.5)
        li.set_editor_property("phys_material", None)
        try:
            usage = getattr(unreal, "LandscapeLayerUsage", None)
            if usage and hasattr(usage, "LU_Default"):
                li.set_editor_property("layer_usage", usage.LU_Default)
        except Exception:
            pass
        try:
            li.set_editor_property(
                "layer_color",
                unreal.LinearColor(color[0], color[1], color[2], color[3]),
            )
        except Exception:
            pass
        unreal.EditorAssetLibrary.save_loaded_asset(li, only_if_is_dirty=False)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "folder": LAYER_DIR,
        "layers": [{"asset": f"{LAYER_DIR}/{n}", "name": ln} for n, ln, _ in LAYER_SPECS],
        "created": created,
        "updated": updated,
        "paint_workflow": [
            "Create Landscape → assign MI_Landscape_Meadow (or SakuraGarden)",
            "Paint Rock/Grass/Mud/Path using LayerInfo assets in this folder",
            "Set bUsePaintedLayers=true on MI when painted weights exist",
            "Empty landscape falls back to procedural height competition",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"LANDSCAPE_LAYERS_OK created={len(created)} updated={len(updated)} -> {REPORT}")
    return report


def main() -> int:
    try:
        import unreal  # noqa: F401
        build()
        return 0
    except ImportError:
        if not UE_CMD.exists():
            print(f"ERROR: {UE_CMD}")

            return 1
        log = PROJECT_ROOT / "Saved" / "Logs" / "setup_landscape_layers.log"
        cmd = [
            str(UE_CMD), str(UPROJECT),
            f"-ExecutePythonScript={(PROJECT_ROOT / 'Content/Python/setup_landscape_layers.py').as_posix()}",
            "-stdout", "-unattended", "-nullrhi", "-DisablePlugins=Monolith",
            f"-log={log}",
        ]
        return subprocess.run(cmd, cwd=str(PROJECT_ROOT)).returncode


if __name__ == "__main__":
    raise SystemExit(main())
