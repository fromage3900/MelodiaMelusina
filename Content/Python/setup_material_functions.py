"""Build shared MF_* material function library for full-stack toon materials.

Run headless:
  UnrealEditor-Cmd.exe BS_GodFile.uproject ^
    -ExecutePythonScript="G:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_material_functions.py"
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import unreal

import material_lib as lib

REPORT_PATH = Path(__file__).resolve().parents[2] / "Saved" / "Audit" / "material_functions_build.json"

# (name, description) — each MF exposes Result output for master MaterialFunctionCall wiring
MF_SPECS: list[tuple[str, str]] = [
    ("MF_UVTransform", "UV scale + rotation transform"),
    ("MF_RealParallax", "Height-based parallax UV offset"),
    ("MF_CurvatureOrnament", "Curvature-driven ornament mask"),
    ("MF_Impressionist_BrushStroke", "Directional oil paint stroke mask"),
    ("MF_Impressionist_Impasto", "Impasto height from stroke mask"),
    ("MF_Impressionist_Temporal", "Temporal FBm noise modulation"),
    ("MF_Impressionist_InkPool", "Valley ink pooling mask"),
    ("MF_AudioReactiveBlend", "Audio MPC-driven blend factor"),
    ("MF_GildingOverlay", "Gold tint overlay blend"),
    ("MF_MapComposite", "Normal/roughness map composite factor"),
    ("MF_SDF_BandRelief", "World SDF band relief mask"),
]


def _create_or_rebuild_mf(name: str) -> unreal.MaterialFunction:
    lib.ensure_directory(lib.FUNCTION_DIR)
    path = lib.asset_path(lib.FUNCTION_DIR, name)
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.MaterialFunctionFactoryNew()
    mf = asset_tools.create_asset(name, lib.FUNCTION_DIR, unreal.MaterialFunction, factory)
    if not mf:
        raise RuntimeError(f"Failed to create {name}")
    return mf


def _add_function_output(mf, from_expr, output_name: str, x: int, y: int) -> None:
    out = lib.create_expression(mf, unreal.MaterialExpressionFunctionOutput, x, y)
    out.set_editor_property("output_name", output_name)
    lib.connect(from_expr, "", out, "")


def _build_uv_transform(mf: unreal.MaterialFunction) -> None:
    uv = lib.create_expression(mf, unreal.MaterialExpressionTextureCoordinate, -800, 0)
    uv.set_editor_property("coordinate_index", 0)
    scale = lib.scalar_param(mf, "UVScale", "UV", 1.0, -800, 120)
    rot = lib.scalar_param(mf, "UVRotation", "UV", 0.0, -800, 220)
    mul = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -560, 40)
    lib.connect(uv, "", mul, "A")
    lib.connect(scale, "", mul, "B")
    rot_rad = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -560, 180)
    const_pi = lib.create_expression(mf, unreal.MaterialExpressionConstant, -720, 260)
    const_pi.set_editor_property("r", 0.0174533)
    lib.connect(rot, "", rot_rad, "A")
    lib.connect(const_pi, "", rot_rad, "B")
    cos_n = lib.create_expression(mf, unreal.MaterialExpressionCosine, -360, 120)
    sin_n = lib.create_expression(mf, unreal.MaterialExpressionSine, -360, 220)
    lib.connect_unary(rot_rad, cos_n)
    lib.connect_unary(rot_rad, sin_n)
    _add_function_output(mf, mul, "Result", -120, 40)


def _build_real_parallax(mf: unreal.MaterialFunction) -> None:
    height = lib.scalar_param(mf, "Height", "Parallax", 0.5, -800, 0)
    scale = lib.scalar_param(mf, "ParallaxScale", "Parallax", 0.05, -800, 100)
    view = lib.create_expression(mf, unreal.MaterialExpressionCameraVectorWS, -800, 220)
    offset = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -480, 80)
    lib.connect(height, "", offset, "A")
    lib.connect(scale, "", offset, "B")
    parallax = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -240, 80)
    lib.connect(offset, "", parallax, "A")
    lib.connect(view, "", parallax, "B")
    _add_function_output(mf, parallax, "Result", -40, 80)


def _build_curvature_ornament(mf: unreal.MaterialFunction) -> None:
    normal = lib.create_expression(mf, unreal.MaterialExpressionPixelNormalWS, -800, 0)
    ddx = lib.create_expression(mf, unreal.MaterialExpressionDDX, -600, -80)
    ddy = lib.create_expression(mf, unreal.MaterialExpressionDDY, -600, 80)
    lib.connect_unary(normal, ddx)
    lib.connect_unary(normal, ddy)
    curve = lib.create_expression(mf, unreal.MaterialExpressionAdd, -400, 0)
    lib.connect(ddx, "", curve, "A")
    lib.connect(ddy, "", curve, "B")
    sens = lib.scalar_param(mf, "CurvatureSensitivity", "Ornament", 2.0, -800, 180)
    style = lib.scalar_param(mf, "OrnamentStyle", "Ornament", 0.0, -800, 280)
    mod = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -200, 40)
    lib.connect(curve, "", mod, "A")
    lib.connect(sens, "", mod, "B")
    styled = lib.create_expression(mf, unreal.MaterialExpressionAdd, 0, 40)
    lib.connect(mod, "", styled, "A")
    lib.connect(style, "", styled, "B")
    mask = lib.create_expression(mf, unreal.MaterialExpressionAbs, 160, 40)
    lib.connect_unary(styled, mask)
    _add_function_output(mf, mask, "Result", 320, 40)


def _build_brush_stroke(mf: unreal.MaterialFunction) -> None:
    world = lib.create_expression(mf, unreal.MaterialExpressionWorldPosition, -900, 0)
    mask_xy = lib.create_expression(mf, unreal.MaterialExpressionComponentMask, -720, 0)
    mask_xy.set_editor_property("r", True)
    mask_xy.set_editor_property("g", True)
    mask_xy.set_editor_property("b", False)
    mask_xy.set_editor_property("a", False)
    lib.connect(world, "", mask_xy, "")
    brush_scale = lib.scalar_param(mf, "BrushScale", "OilPaint", 0.045, -900, 120)
    stroke = lib.scalar_param(mf, "StrokeStrength", "OilPaint", 0.55, -900, 220)
    scale_mul = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -540, 40)
    lib.connect(mask_xy, "", scale_mul, "A")
    lib.connect(brush_scale, "", scale_mul, "B")
    sin_n = lib.create_expression(mf, unreal.MaterialExpressionSine, -360, 40)
    sin_n.set_editor_property("period", 1.0)
    lib.connect_unary(scale_mul, sin_n)
    abs_n = lib.create_expression(mf, unreal.MaterialExpressionAbs, -180, 40)
    lib.connect_unary(sin_n, abs_n)
    out = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 0, 40)
    lib.connect(abs_n, "", out, "A")
    lib.connect(stroke, "", out, "B")
    _add_function_output(mf, out, "Result", 180, 40)


def _build_impasto(mf: unreal.MaterialFunction) -> None:
    stroke = lib.scalar_param(mf, "StrokeMask", "Impasto", 0.5, -600, 0)
    strength = lib.scalar_param(mf, "ImpastoStrength", "Impasto", 0.35, -600, 100)
    height = lib.scalar_param(mf, "ImpastoHeight", "Impasto", 0.025, -600, 200)
    h1 = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -320, 40)
    lib.connect(stroke, "", h1, "A")
    lib.connect(strength, "", h1, "B")
    h2 = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -120, 40)
    lib.connect(h1, "", h2, "A")
    lib.connect(height, "", h2, "B")
    _add_function_output(mf, h2, "Result", 80, 40)


def _build_temporal(mf: unreal.MaterialFunction) -> None:
    world = lib.create_expression(mf, unreal.MaterialExpressionWorldPosition, -900, 0)
    mask_xy = lib.create_expression(mf, unreal.MaterialExpressionComponentMask, -720, 0)
    mask_xy.set_editor_property("r", True)
    mask_xy.set_editor_property("g", True)
    mask_xy.set_editor_property("b", False)
    mask_xy.set_editor_property("a", False)
    lib.connect(world, "", mask_xy, "")
    time = lib.create_expression(mf, unreal.MaterialExpressionTime, -900, 140)
    noise_scale = lib.scalar_param(mf, "NoiseScale", "Temporal", 1.5, -900, 260)
    temporal = lib.scalar_param(mf, "TemporalStrength", "Temporal", 0.12, -900, 360)
    wind = lib.scalar_param(mf, "WindSpeed", "Temporal", 0.15, -900, 460)
    wind_mul = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -720, 160)
    lib.connect(time, "", wind_mul, "A")
    lib.connect(wind, "", wind_mul, "B")
    scaled = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -540, 40)
    lib.connect(mask_xy, "", scaled, "A")
    lib.connect(noise_scale, "", scaled, "B")
    phase = lib.create_expression(mf, unreal.MaterialExpressionAdd, -360, 60)
    lib.connect(scaled, "", phase, "A")
    lib.connect(wind_mul, "", phase, "B")
    sine = lib.create_expression(mf, unreal.MaterialExpressionSine, -180, 60)
    sine.set_editor_property("period", 1.0)
    lib.connect_unary(phase, sine)
    out = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 0, 60)
    lib.connect(sine, "", out, "A")
    lib.connect(temporal, "", out, "B")
    _add_function_output(mf, out, "Result", 180, 60)


def _build_ink_pool(mf: unreal.MaterialFunction) -> None:
    stroke = lib.scalar_param(mf, "StrokeMask", "Ink", 0.5, -600, 0)
    wetness = lib.scalar_param(mf, "Wetness", "Ink", 0.0, -600, 100)
    ink = lib.scalar_param(mf, "InkIntensity", "Ink", 0.0, -600, 200)
    pooling = lib.scalar_param(mf, "PoolingStrength", "Ink", 0.5, -600, 300)
    inv = lib.create_expression(mf, unreal.MaterialExpressionOneMinus, -360, 0)
    lib.connect_unary(stroke, inv)
    wet = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -180, 40)
    lib.connect(inv, "", wet, "A")
    lib.connect(wetness, "", wet, "B")
    ink_w = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 0, 40)
    lib.connect(wet, "", ink_w, "A")
    lib.connect(ink, "", ink_w, "B")
    pool = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 180, 40)
    lib.connect(ink_w, "", pool, "A")
    lib.connect(pooling, "", pool, "B")
    _add_function_output(mf, pool, "Result", 360, 40)


def _build_audio_blend(mf: unreal.MaterialFunction) -> None:
    reactivity = lib.scalar_param(mf, "AudioReactivity", "Audio", 0.0, -600, 0)
    bass_w = lib.scalar_param(mf, "BassWeight", "Audio", 1.0, -600, 100)
    mid_w = lib.scalar_param(mf, "MidWeight", "Audio", 0.5, -600, 200)
    treble_w = lib.scalar_param(mf, "TrebleWeight", "Audio", 0.25, -600, 300)
    blend = lib.create_expression(mf, unreal.MaterialExpressionAdd, -240, 120)
    lib.connect(bass_w, "", blend, "A")
    mid_add = lib.create_expression(mf, unreal.MaterialExpressionAdd, -400, 160)
    lib.connect(mid_w, "", mid_add, "A")
    lib.connect(treble_w, "", mid_add, "B")
    lib.connect(mid_add, "", blend, "B")
    out = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 0, 80)
    lib.connect(reactivity, "", out, "A")
    lib.connect(blend, "", out, "B")
    _add_function_output(mf, out, "Result", 180, 80)


def _build_gilding(mf: unreal.MaterialFunction) -> None:
    strength = lib.scalar_param(mf, "GildingStrength", "Gilding", 0.0, -600, 0)
    gold = lib.vector_param(mf, "GoldTint", "Gilding", (0.85, 0.65, 0.25, 1.0), -600, 120)
    emissive = lib.scalar_param(mf, "GoldEmissive", "Gilding", 0.0, -600, 260)
    out = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -240, 80)
    lib.connect(strength, "", out, "A")
    lib.connect(gold, "", out, "B")
    _add_function_output(mf, out, "Color", 0, 80)
    _add_function_output(mf, emissive, "Emissive", 0, 260)


def _build_map_composite(mf: unreal.MaterialFunction) -> None:
    rough_map = lib.texture_param(mf, "RoughnessMap", "Maps", -600, 0)
    normal_map = lib.texture_param(mf, "NormalMap", "Maps", -600, 160)
    rough_const = lib.scalar_param(mf, "RoughnessScalar", "Maps", 0.75, -600, 320)
    rough_mul = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -240, 40)
    lib.connect(rough_map, "", rough_mul, "A")
    lib.connect(rough_const, "", rough_mul, "B")
    _add_function_output(mf, rough_mul, "Roughness", 0, 40)
    _add_function_output(mf, normal_map, "Normal", 0, 160)


def _build_sdf_band(mf: unreal.MaterialFunction) -> None:
    world = lib.create_expression(mf, unreal.MaterialExpressionWorldPosition, -900, 0)
    mask_xy = lib.create_expression(mf, unreal.MaterialExpressionComponentMask, -720, 0)
    mask_xy.set_editor_property("r", True)
    mask_xy.set_editor_property("g", True)
    mask_xy.set_editor_property("b", False)
    mask_xy.set_editor_property("a", False)
    lib.connect(world, "", mask_xy, "")
    band_scale = lib.scalar_param(mf, "BandScale", "SDF", 0.035, -900, 120)
    band_strength = lib.scalar_param(mf, "BandStrength", "SDF", 0.22, -900, 220)
    scale_mul = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -540, 40)
    lib.connect(mask_xy, "", scale_mul, "A")
    lib.connect(band_scale, "", scale_mul, "B")
    sin_n = lib.create_expression(mf, unreal.MaterialExpressionSine, -360, 40)
    sin_n.set_editor_property("period", 1.0)
    lib.connect_unary(scale_mul, sin_n)
    abs_n = lib.create_expression(mf, unreal.MaterialExpressionAbs, -180, 40)
    lib.connect_unary(sin_n, abs_n)
    out = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 0, 40)
    lib.connect(abs_n, "", out, "A")
    lib.connect(band_strength, "", out, "B")
    _add_function_output(mf, out, "Result", 180, 40)


BUILDERS = {
    "MF_UVTransform": _build_uv_transform,
    "MF_RealParallax": _build_real_parallax,
    "MF_CurvatureOrnament": _build_curvature_ornament,
    "MF_Impressionist_BrushStroke": _build_brush_stroke,
    "MF_Impressionist_Impasto": _build_impasto,
    "MF_Impressionist_Temporal": _build_temporal,
    "MF_Impressionist_InkPool": _build_ink_pool,
    "MF_AudioReactiveBlend": _build_audio_blend,
    "MF_GildingOverlay": _build_gilding,
    "MF_MapComposite": _build_map_composite,
    "MF_SDF_BandRelief": _build_sdf_band,
}


def build_all() -> list[str]:
    unreal.log("=== Building material function library ===")
    created: list[str] = []
    for name, _desc in MF_SPECS:
        builder = BUILDERS[name]
        mf = _create_or_rebuild_mf(name)
        builder(mf)
        try:
            unreal.MaterialEditingLibrary.recompile_material_function(mf)
        except Exception:
            pass
        lib.save_package(mf)
        path = lib.asset_path(lib.FUNCTION_DIR, name)
        created.append(path)
        unreal.log(f"[MF] built {path}")
    return created


def main() -> int:
    paths = build_all()
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "functions": paths,
        "count": len(paths),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    unreal.log(f"[MF] complete: {len(paths)} functions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
