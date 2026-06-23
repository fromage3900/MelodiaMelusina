"""Create MPC_Portfolio_Palette for scene-wide color cohesion (Melodia-style).

Scalars/vectors drive global grade; instances sample via CollectionParameter nodes
on M_Master_Toon_Universal (ShadowDreamBias wired in setup_master_universal;
full palette tint deferred).

Run headless:
  UnrealEditor-Cmd.exe BS_GodFile.uproject ^
    -ExecutePythonScript="G:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_portfolio_mpc.py"
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import unreal

import material_lib as lib

REPORT = Path(__file__).resolve().parents[2] / "Saved" / "Audit" / "portfolio_mpc.json"
MPC_NAME = "MPC_Portfolio_Palette"
MPC_PATH = f"{lib.MPC_DIR}/{MPC_NAME}"

MPC_SCALARS = [
    ("BaseTintShift", 1.0),       # multiply global base tint (1=neutral)
    ("ShadowDreamBias", 0.0),     # add to ShadowDreamStrength on instances
    ("RimWarmth", 0.0),           # add to RimIntensity (warm rim push)
    ("ElementalGrade", 0.0),      # add to ElementStrength
    ("TimeOfDayWarmth", 0.0),     # global TOD warmth (-1 cool .. +1 warm)
]

MPC_VECTORS = [
    ("PaletteTint", (1.0, 1.0, 1.0, 1.0)),  # multiply final grade vector
]


def _add_scalar(mpc, name: str, default: float) -> None:
    try:
        param = unreal.CollectionScalarParameter()
        param.parameter_name = name
        param.default_value = default
        mpc.add_scalar_parameter(param)
    except Exception:
        try:
            mpc.set_scalar_parameter_default_value(name, default)
        except Exception as exc:
            unreal.log_warning(f"[MPC Palette] scalar {name}: {exc}")


def _add_vector(mpc, name: str, default: tuple[float, float, float, float]) -> None:
    try:
        param = unreal.CollectionVectorParameter()
        param.parameter_name = name
        param.default_value = unreal.LinearColor(*default)
        mpc.add_vector_parameter(param)
    except Exception:
        try:
            mpc.set_vector_parameter_default_value(name, unreal.LinearColor(*default))
        except Exception as exc:
            unreal.log_warning(f"[MPC Palette] vector {name}: {exc}")


def build_mpc() -> str:
    lib.ensure_directory(lib.MPC_DIR)
    path = lib.asset_path(lib.MPC_DIR, MPC_NAME)
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.log(f"[MPC Palette] reusing {path}")
        return path

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.MaterialParameterCollectionFactoryNew()
    mpc = asset_tools.create_asset(MPC_NAME, lib.MPC_DIR, unreal.MaterialParameterCollection, factory)
    if not mpc:
        raise RuntimeError(f"Failed to create {MPC_NAME}")

    for name, default in MPC_SCALARS:
        _add_scalar(mpc, name, default)
    for name, default in MPC_VECTORS:
        _add_vector(mpc, name, default)

    lib.save_package(mpc)
    unreal.log(f"[MPC Palette] built {path}")
    return path


def main() -> int:
    path = build_mpc()
    audio_mpc = lib.asset_path(lib.MPC_DIR, "MPC_Portfolio_Audio")
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mpc_palette": path,
        "mpc_audio": audio_mpc if unreal.EditorAssetLibrary.does_asset_exist(audio_mpc) else None,
        "scalars": {n: d for n, d in MPC_SCALARS},
        "vectors": {n: list(v) for n, v in MPC_VECTORS},
        "usage": (
            "Place MPC_Portfolio_Palette in level. M_Master_Toon_Universal reads "
            "ShadowDreamBias via CollectionParameter; BaseTintShift/PaletteTint/RimWarmth "
            "are reserved for a future palette pass. Tune once per scene for cohesive grade."
        ),
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
