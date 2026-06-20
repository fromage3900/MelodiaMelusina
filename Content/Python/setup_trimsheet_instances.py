"""Trimsheet layer-blend material instances on M_Master_Toon_Universal.

Exposes Layer A/B albedo+height, LayerBlend, parallax, and macro variation for
crack/wear variation across trim sheets.

Run (editor or headless):
  py "G:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_trimsheet_instances.py"
"""
from __future__ import annotations

import json
from pathlib import Path

import material_lib as lib

MASTER = f"{lib.MASTER_DIR}/M_Master_Toon_Universal.M_Master_Toon_Universal"
REPORT = Path(__file__).resolve().parents[2] / "Saved" / "Audit" / "trimsheet_instances.json"
FOLDER = f"{lib.ENV_INST_DIR}/Stylized"

# Artist guide (also written to REPORT):
# - Layer A = primary trimsheet (clean albedo + height in LayerA group)
# - Layer B = variation/crack overlay (LayerB_* maps)
# - LayerBlend 0→1 cross-fades B over A (use vertex paint / mask texture later)
# - ParallaxStrength + LayerA/B_ParallaxScale = height-driven crack depth
# - MacroVariationStrength + MacroScale = world-space wear breakup across instances

TRIMSHEET_INSTANCES: list[dict] = [
    {
        "name": "MI_Trimsheet_VariationCracks",
        "profile": "TP_Stone",
        "vectors": {"BaseTint": (0.58, 0.52, 0.48, 1.0)},
        "scalars": {
            "TextureWeight": 1.0,
            "LayerBlend": 0.42,
            "LayerA_TextureWeight": 1.0,
            "LayerB_TextureWeight": 0.9,
            "ParallaxStrength": 0.62,
            "ParallaxScale": 0.055,
            "ParallaxSteps": 12.0,
            "ParallaxMode": 2.0,
            "NormalStrength": 1.2,
            "LayerA_ParallaxScale": 1.0,
            "LayerB_ParallaxScale": 1.35,
            "MacroVariationStrength": 0.28,
            "MacroScale": 0.0012,
            "DetailStrength": 0.18,
            "DetailTiling": 10.0,
            "Roughness": 0.68,
            "Metallic": 0.04,
        },
    },
    {
        "name": "MI_Universal_TrimsheetBlend",
        "profile": "TP_Default",
        "vectors": {"BaseTint": (0.62, 0.56, 0.50, 1.0)},
        "scalars": {
            "TextureWeight": 1.0,
            "LayerBlend": 0.25,
            "LayerA_TextureWeight": 1.0,
            "LayerB_TextureWeight": 0.75,
            "ParallaxStrength": 0.45,
            "ParallaxScale": 0.04,
            "MacroVariationStrength": 0.15,
            "MacroScale": 0.0009,
            "Roughness": 0.72,
        },
    },
    {
        "name": "MI_Trimsheet_HeavyWear",
        "profile": "TP_Stone",
        "vectors": {"BaseTint": (0.48, 0.44, 0.40, 1.0)},
        "scalars": {
            "LayerBlend": 0.68,
            "LayerB_TextureWeight": 1.0,
            "ParallaxStrength": 0.75,
            "LayerB_ParallaxScale": 1.6,
            "MacroVariationStrength": 0.42,
            "MacroScale": 0.0015,
            "MossConcavityStrength": 0.22,
            "Roughness": 0.78,
        },
    },
]


def build() -> list[dict]:
    import unreal

    if not unreal.EditorAssetLibrary.does_asset_exist(MASTER):
        raise RuntimeError(f"Missing master: {MASTER} — run setup_master_universal.py first")

    profiles = lib.create_toon_profiles(["TP_Default", "TP_Stone"])
    results: list[dict] = []

    for spec in TRIMSHEET_INSTANCES:
        inst = lib.create_material_instance(spec["name"], FOLDER, MASTER)
        profile = profiles.get(spec.get("profile", "TP_Default"))
        if profile:
            lib.set_instance_toon_profile(inst, profile)
        for pname, rgba in spec.get("vectors", {}).items():
            lib.set_instance_vector(inst, pname, rgba)
        for pname, value in spec.get("scalars", {}).items():
            lib.set_instance_scalar(inst, pname, value)
        lib.save_package(inst)
        path = lib.asset_path(FOLDER, spec["name"])
        results.append({"instance": spec["name"], "path": path, "status": "created_or_updated"})

    return results


def main() -> int:
    try:
        import unreal  # noqa: F401
    except ImportError:
        print("Requires Unreal Editor Python")
        return 1

    results = build()
    report = {
        "instances": results,
        "count": len(results),
        "folder": FOLDER,
        "artist_guide": {
            "LayerA": "Albedo, NormalMap, ORM, HeightMap — primary trimsheet",
            "LayerB": "LayerB_Albedo, LayerB_NormalMap, LayerB_ORM, LayerB_HeightMap — crack/wear overlay",
            "LayerBlend": "0=clean A, 1=full B overlay (lerp all maps + texture weights)",
            "Parallax": "ParallaxStrength gates height offset; LayerA/B_ParallaxScale per-layer depth",
            "MacroDetail": "MacroVariationStrength/MacroScale break tiling; DetailNormal for micro cracks",
            "verify": "Assign trim textures on MI, set LayerBlend 0→1 in Details panel, enable ParallaxStrength",
        },
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
