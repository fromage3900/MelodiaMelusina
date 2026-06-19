"""Create themed MI_* instances for M_Master_Toon_Universal.

Run after setup_master_universal.py:
  py "G:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_universal_instances.py"
"""
from __future__ import annotations

import json
from pathlib import Path

import material_lib as lib
from universal_instance_presets import EXTRA_INSTANCES

MASTER = f"{lib.MASTER_DIR}/M_Master_Toon_Universal.M_Master_Toon_Universal"
REPORT = Path(__file__).resolve().parents[2] / "Saved" / "Audit" / "universal_instances.json"

CORE_INSTANCES: list[dict] = [
    {
        "name": "MI_Universal_Default",
        "profile": "TP_Default",
        "vectors": {"BaseTint": (0.62, 0.58, 0.55, 1.0)},
        "scalars": {"TextureWeight": 1.0, "UVScale": 1.0, "Roughness": 0.65, "Metallic": 0.0},
    },
    {
        "name": "MI_Universal_DreamyPastel",
        "profile": "TP_Default",
        "vectors": {
            "BaseTint": (0.78, 0.72, 0.82, 1.0),
            "DreamTint": (1.0, 0.88, 0.96, 1.0),
            "ShadowDreamTint": (0.55, 0.48, 0.72, 1.0),
            "GlowColor": (1.0, 0.92, 0.98, 1.0),
        },
        "scalars": {
            "PastelLift": 0.42,
            "InnerGlowIntensity": 0.25,
            "GlowIntensity": 0.12,
            "ShadowDreamStrength": 0.55,
            "ShadowSoftness": 0.7,
            "BloomBoost": 0.15,
        },
    },
    {
        "name": "MI_Universal_Constellation",
        "profile": "TP_Default",
        "vectors": {
            "BaseTint": (0.06, 0.07, 0.14, 1.0),
            "ConstellationRampLow": (0.02, 0.03, 0.10, 1.0),
            "ConstellationRampMid": (0.42, 0.18, 0.58, 1.0),
            "ConstellationRampHigh": (0.88, 0.78, 1.0, 1.0),
            "RimColor": (0.55, 0.75, 1.0, 1.0),
        },
        "scalars": {
            "ConstellationStrength": 0.92,
            "ConstellationScale": 2.8,
            "CelestialStarIntensity": 1.2,
            "CelestialTwinkle": 0.35,
            "CelestialNebulaStrength": 0.72,
            "CelestialNebulaScale": 0.42,
            "CelestialGalaxyStrength": 0.55,
            "CelestialGalaxyScale": 0.15,
            "CelestialGalaxyArms": 4.0,
            "RimIntensity": 0.35,
            "RimPower": 4.5,
            "Metallic": 0.12,
        },
    },
    {
        "name": "MI_Universal_CelestialNebula",
        "profile": "TP_Default",
        "vectors": {
            "BaseTint": (0.08, 0.06, 0.16, 1.0),
            "ConstellationRampLow": (0.01, 0.02, 0.08, 1.0),
            "ConstellationRampMid": (0.55, 0.22, 0.68, 1.0),
            "ConstellationRampHigh": (0.95, 0.65, 0.92, 1.0),
        },
        "scalars": {
            "ConstellationStrength": 1.0,
            "CelestialNebulaStrength": 0.95,
            "CelestialGalaxyStrength": 0.25,
            "CelestialStarIntensity": 0.8,
            "BloomBoost": 0.2,
        },
    },
    {
        "name": "MI_Universal_LayeredStone",
        "profile": "TP_Default",
        "vectors": {"BaseTint": (0.55, 0.50, 0.46, 1.0)},
        "scalars": {
            "LayerBlend": 0.35,
            "LayerA_TextureWeight": 1.0,
            "LayerB_TextureWeight": 0.85,
            "ParallaxStrength": 0.55,
            "ParallaxScale": 0.06,
            "LayerA_ParallaxScale": 1.0,
            "LayerB_ParallaxScale": 1.4,
            "Roughness": 0.62,
            "Metallic": 0.05,
        },
    },
    {
        "name": "MI_Universal_TemporalInk",
        "profile": "TP_Default",
        "vectors": {
            "BaseTint": (0.72, 0.68, 0.78, 1.0),
            "DreamTint": (0.92, 0.86, 0.98, 1.0),
        },
        "scalars": {
            "TemporalStrength": 0.42,
            "WindSpeed": 0.18,
            "NoiseScale": 2.2,
            "SmearStrength": 0.12,
            "BoilIntensity": 0.08,
            "TextureWeight": 0.85,
            "PastelLift": 0.15,
        },
    },
    {
        "name": "MI_Universal_GoldLeaf",
        "profile": "TP_Gold",
        "vectors": {
            "BaseTint": (0.48, 0.40, 0.34, 1.0),
            "GoldTint": (0.92, 0.72, 0.28, 1.0),
            "GoldEmissive": (0.45, 0.32, 0.08, 1.0),
        },
        "scalars": {
            "GildingStrength": 0.72,
            "CurvatureSensitivity": 3.2,
            "GoldRoughness": 0.22,
            "Metallic": 0.85,
            "Roughness": 0.38,
        },
    },
    {
        "name": "MI_Universal_FairyHearts",
        "profile": "TP_Default",
        "vectors": {
            "BaseTint": (0.82, 0.62, 0.72, 1.0),
            "FairyDustColor": (1.0, 0.55, 0.72, 1.0),
            "DreamTint": (1.0, 0.86, 0.92, 1.0),
        },
        "scalars": {
            "FairyMotifStyle": 1.0,
            "FairyDustIntensity": 0.65,
            "FairyDustScale": 12.0,
            "FairyHighlightThreshold": 0.42,
            "PastelLift": 0.2,
            "BloomBoost": 0.35,
        },
    },
    {
        "name": "MI_Universal_FairyStars",
        "profile": "TP_Default",
        "vectors": {
            "BaseTint": (0.22, 0.28, 0.42, 1.0),
            "FairyDustColor": (0.95, 0.92, 1.0, 1.0),
            "RimColor": (0.65, 0.82, 1.0, 1.0),
        },
        "scalars": {
            "FairyMotifStyle": 2.0,
            "FairyDustIntensity": 0.8,
            "FairyDustScale": 18.0,
            "RimIntensity": 0.28,
            "ConstellationStrength": 0.35,
            "Metallic": 0.25,
        },
    },
    {
        "name": "MI_Universal_FairyGarden",
        "profile": "TP_Default",
        "vectors": {
            "BaseTint": (0.58, 0.72, 0.52, 1.0),
            "FairyDustColor": (1.0, 0.78, 0.92, 1.0),
            "ShadowFlowerColor": (0.95, 0.55, 0.78, 1.0),
            "ShadowDreamTint": (0.42, 0.58, 0.48, 1.0),
        },
        "scalars": {
            "FairyMotifStyle": 3.0,
            "FairyDustIntensity": 0.5,
            "ShadowFlowerStrength": 0.62,
            "ShadowFlowerScale": 6.0,
            "ShadowDreamStrength": 0.4,
            "GildingStrength": 0.15,
        },
    },
    {
        "name": "MI_Universal_MoonlitMetal",
        "profile": "TP_Gold",
        "vectors": {
            "BaseTint": (0.18, 0.20, 0.32, 1.0),
            "FairyDustColor": (0.88, 0.92, 1.0, 1.0),
            "GoldTint": (0.85, 0.78, 0.55, 1.0),
        },
        "scalars": {
            "FairyMotifStyle": 4.0,
            "FairyDustIntensity": 0.45,
            "Metallic": 0.92,
            "Roughness": 0.28,
            "RimIntensity": 0.22,
            "ConstellationStrength": 0.25,
        },
    },
]

INSTANCES: list[dict] = CORE_INSTANCES + EXTRA_INSTANCES


def _instance_folder(spec: dict) -> str:
    subdir = spec.get("subdir")
    if subdir:
        return f"{lib.ENV_INST_DIR}/{subdir}"
    return lib.ENV_INST_DIR


def build_instances() -> list[dict]:
    import unreal

    if not unreal.EditorAssetLibrary.does_asset_exist(MASTER):
        raise RuntimeError(f"Missing master: {MASTER} — run setup_master_universal.py first")

    profile_names = sorted({spec.get("profile", "TP_Default") for spec in INSTANCES})
    profiles = lib.create_toon_profiles(profile_names)
    results: list[dict] = []
    seen: set[str] = set()

    for spec in INSTANCES:
        name = spec["name"]
        if name in seen:
            unreal.log_warning(f"[UniversalMI] duplicate spec skipped: {name}")
            continue
        seen.add(name)

        folder = _instance_folder(spec)
        inst = lib.create_material_instance(name, folder, MASTER)
        profile = profiles.get(spec.get("profile", "TP_Default"))
        if profile:
            lib.set_instance_toon_profile(inst, profile)
        for pname, rgba in spec.get("vectors", {}).items():
            lib.set_instance_vector(inst, pname, rgba)
        for pname, value in spec.get("scalars", {}).items():
            lib.set_instance_scalar(inst, pname, value)
        for pname, value in spec.get("switches", {}).items():
            lib.set_instance_static_switch(inst, pname, bool(value))
        lib.save_package(inst)
        results.append({"instance": name, "folder": folder, "status": "created_or_updated"})

    return results


def main() -> int:
    try:
        import unreal  # noqa: F401
    except ImportError:
        print("Requires Unreal Editor Python")
        return 1

    results = build_instances()
    report = {"instances": results, "count": len(results)}
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
