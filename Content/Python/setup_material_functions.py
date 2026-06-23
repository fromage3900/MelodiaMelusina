"""Build shared MF_* material function library for full-stack toon materials.

Run headless:
  UnrealEditor-Cmd.exe BS_GodFile.uproject ^
    -ExecutePythonScript="G:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_material_functions.py"
"""
from __future__ import annotations

import json
import sys
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
    ("MF_AnimeSkinWrap", "Wrap lighting + soft skin shadow mask"),
    ("MF_ParallaxCore", "Height parallax UV offset — modes 0/1/2"),
    ("MF_NormalAdjust", "Normal strength + power + per-layer scale"),
    ("MF_WaterDepthColor", "Lerp shallow/deep water tint by normalized depth"),
    ("MF_WaterShorelineFade", "Pond UV edge fade + foam boost"),
    ("MF_WaterFoam", "Stylized wave-crest foam mask"),
    ("MF_LandscapeHeightCompete", "Rock/grass/mud height competition alphas"),
    ("MF_NikkiDreamGrade", "Pastel lift + dream saturation/contrast grade"),
    ("MF_NikkiRimGlow", "Fresnel rim + inner glow additive"),
    ("MF_NikkiSparkle", "Mask-driven ground sparkle twinkle"),
    ("MF_NikkiIridescenceSheen", "View iridescence + fabric sheen tint"),
    ("MF_MacroDetail", "Macro variation albedo breakup + detail normal blend"),
    ("MF_Magical", "Henshin wipe + motif mask emissive + palette shift"),
    ("MF_LayerHeightCompete", "Dual-layer height competition alpha"),
    ("MF_LayerBlendAdvanced", "Per-channel layer A/B blend with softness"),
    ("MF_ShadowDreamGrade", "N·L shadow tint with MPC bias + contact boost"),
    ("MF_ShadowFlowerProject", "Texture petal shadows in world space"),
    ("MF_AudioBeatModulator", "BeatPhase sine envelope for rhythm hooks"),
]


def _clear_function_graph(mf: unreal.MaterialFunction) -> None:
    try:
        if not hasattr(unreal.MaterialEditingLibrary, "get_function_expressions"):
            return
        exprs = unreal.MaterialEditingLibrary.get_function_expressions(mf)
        for expr in list(exprs or []):
            unreal.MaterialEditingLibrary.delete_material_expression(mf, expr)
    except Exception as exc:
        unreal.log_warning(f"[MF] clear graph {mf.get_name()}: {exc}")


def _create_or_rebuild_mf(name: str, *, force: bool = False) -> unreal.MaterialFunction:
    lib.ensure_directory(lib.FUNCTION_DIR)
    path = lib.asset_path(lib.FUNCTION_DIR, name)
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        mf = unreal.load_asset(path)
        if mf and not force:
            unreal.log(f"[MF] skip existing {path}")
            return mf
        if mf and force:
            _clear_function_graph(mf)
            return mf

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.MaterialFunctionFactoryNew()
    mf = asset_tools.create_asset(name, lib.FUNCTION_DIR, unreal.MaterialFunction, factory)
    if mf:
        return mf

    # Fallback: duplicate a sibling MF when create_asset returns None (ghost delete / registry lag).
    for template in ("MF_MapComposite", "MF_RealParallax", "MF_GildingOverlay"):
        src = lib.asset_path(lib.FUNCTION_DIR, template)
        if not unreal.EditorAssetLibrary.does_asset_exist(src):
            continue
        dest = f"{lib.FUNCTION_DIR}/{name}"
        dup = unreal.EditorAssetLibrary.duplicate_asset(src, dest)
        if dup and unreal.EditorAssetLibrary.does_asset_exist(path):
            mf = unreal.load_asset(path)
            if mf:
                if force:
                    _clear_function_graph(mf)
                unreal.log(f"[MF] duplicated {template} -> {name}")
                return mf

    raise RuntimeError(f"Failed to create {name} at {lib.FUNCTION_DIR}")


def _add_function_output(mf, from_expr, output_name: str, x: int, y: int) -> None:
    out = lib.create_expression(mf, unreal.MaterialExpressionFunctionOutput, x, y)
    out.set_editor_property("output_name", output_name)
    lib.connect(from_expr, "", out, "")


def _fn_input(mf, name: str, x: int, y: int, *, sort: int = 0):
    """Material function input exposed on MaterialFunctionCall pins."""
    inp = lib.create_expression(mf, unreal.MaterialExpressionFunctionInput, x, y)
    inp.set_editor_property("input_name", name)
    try:
        inp.set_editor_property("sort_priority", sort)
    except Exception:
        pass
    if name in ("UV",):
        try:
            inp.set_editor_property("input_type", unreal.FunctionInputType.FIT_FLOAT2)
        except Exception:
            pass
    if name == "HeightTexture":
        try:
            inp.set_editor_property("input_type", unreal.FunctionInputType.FIT_TEXTURE2D)
        except Exception:
            pass
    return inp


def _view_xy(mf, x: int, y: int):
    """Camera vector XY as float2 for parallax offset."""
    view = lib.create_expression(mf, unreal.MaterialExpressionCameraVectorWS, x, y)
    view_r = lib.create_expression(mf, unreal.MaterialExpressionComponentMask, x + 160, y - 40)
    view_r.set_editor_property("r", True)
    view_r.set_editor_property("g", False)
    view_r.set_editor_property("b", False)
    view_r.set_editor_property("a", False)
    lib.connect_unary(view, view_r)
    view_g = lib.create_expression(mf, unreal.MaterialExpressionComponentMask, x + 160, y + 40)
    view_g.set_editor_property("r", False)
    view_g.set_editor_property("g", True)
    view_g.set_editor_property("b", False)
    view_g.set_editor_property("a", False)
    lib.connect_unary(view, view_g)
    xy = lib.create_expression(mf, unreal.MaterialExpressionAppendVector, x + 320, y)
    lib.connect_append2(view_r, view_g, xy)
    return xy


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
    """MPC-driven reactivity scalar: Global * weights * band mix."""
    global_r = _fn_input(mf, "GlobalReactivity", -1200, 0, sort=0)
    bass = _fn_input(mf, "Bass", -1200, 120, sort=1)
    mid = _fn_input(mf, "Mid", -1200, 240, sort=2)
    treble = _fn_input(mf, "Treble", -1200, 360, sort=3)
    reactivity = lib.scalar_param(mf, "AudioReactivity", "Audio", 0.0, -1200, 480)
    bass_w = lib.scalar_param(mf, "BassWeight", "Audio", 1.0, -1200, 600)
    mid_w = lib.scalar_param(mf, "MidWeight", "Audio", 0.5, -1200, 720)
    treble_w = lib.scalar_param(mf, "TrebleWeight", "Audio", 0.25, -1200, 840)

    bw = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -900, 80)
    lib.connect(bass, "", bw, "A")
    lib.connect(bass_w, "", bw, "B")
    mw = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -900, 200)
    lib.connect(mid, "", mw, "A")
    lib.connect(mid_w, "", mw, "B")
    tw = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -900, 320)
    lib.connect(treble, "", tw, "A")
    lib.connect(treble_w, "", tw, "B")
    band_add = lib.create_expression(mf, unreal.MaterialExpressionAdd, -700, 160)
    lib.connect(bw, "", band_add, "A")
    mid_add = lib.create_expression(mf, unreal.MaterialExpressionAdd, -700, 280)
    lib.connect(mw, "", mid_add, "A")
    lib.connect(tw, "", mid_add, "B")
    lib.connect(mid_add, "", band_add, "B")
    band_sat = lib.create_expression(mf, unreal.MaterialExpressionSaturate, -520, 200)
    lib.connect(band_add, "", band_sat, "Input")

    gate = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -340, 120)
    lib.connect(global_r, "", gate, "A")
    lib.connect(reactivity, "", gate, "B")
    out = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -160, 160)
    lib.connect(gate, "", out, "A")
    lib.connect(band_sat, "", out, "B")
    _add_function_output(mf, out, "Result", 20, 160)


def _build_audio_beat_modulator(mf: unreal.MaterialFunction) -> None:
    beat = _fn_input(mf, "BeatPhase", -900, 0, sort=0)
    strength = _fn_input(mf, "BeatPhaseStrength", -900, 120, sort=1)
    tau = lib.create_expression(mf, unreal.MaterialExpressionConstant, -720, 40)
    tau.set_editor_property("r", 6.2831853)
    phase = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -540, 40)
    lib.connect(beat, "", phase, "A")
    lib.connect(tau, "", phase, "B")
    wave = lib.create_expression(mf, unreal.MaterialExpressionSine, -360, 40)
    wave.set_editor_property("period", 1.0)
    lib.connect_unary(phase, wave)
    half = lib.create_expression(mf, unreal.MaterialExpressionConstant, -540, 160)
    half.set_editor_property("r", 0.5)
    centered = lib.create_expression(mf, unreal.MaterialExpressionAdd, -180, 80)
    lib.connect(wave, "", centered, "A")
    lib.connect(half, "", centered, "B")
    mod = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 0, 80)
    lib.connect(centered, "", mod, "A")
    lib.connect(strength, "", mod, "B")
    _add_function_output(mf, mod, "Result", 180, 80)


def _build_layer_height_compete(mf: unreal.MaterialFunction) -> None:
    h_a = _fn_input(mf, "HeightA", -1200, 0, sort=0)
    h_b = _fn_input(mf, "HeightB", -1200, 120, sort=1)
    bias = _fn_input(mf, "BlendBias", -1200, 240, sort=2)
    sharp = _fn_input(mf, "BlendSharpness", -1200, 360, sort=3)
    diff = lib.create_expression(mf, unreal.MaterialExpressionSubtract, -900, 80)
    lib.connect(h_b, "", diff, "A")
    lib.connect(h_a, "", diff, "B")
    scaled = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -700, 80)
    lib.connect(diff, "", scaled, "A")
    lib.connect(sharp, "", scaled, "B")
    half = lib.create_expression(mf, unreal.MaterialExpressionConstant, -900, 220)
    half.set_editor_property("r", 0.5)
    biased = lib.create_expression(mf, unreal.MaterialExpressionAdd, -520, 120)
    lib.connect(scaled, "", biased, "A")
    lib.connect(half, "", biased, "B")
    biased2 = lib.create_expression(mf, unreal.MaterialExpressionAdd, -340, 120)
    lib.connect(biased, "", biased2, "A")
    lib.connect(bias, "", biased2, "B")
    alpha = lib.create_expression(mf, unreal.MaterialExpressionSaturate, -160, 120)
    lib.connect(biased2, "", alpha, "Input")
    _add_function_output(mf, alpha, "BlendAlpha", 20, 120)


def _build_layer_blend_advanced(mf: unreal.MaterialFunction) -> None:
    alb_a = _fn_input(mf, "AlbedoA", -1400, 0, sort=0)
    alb_b = _fn_input(mf, "AlbedoB", -1400, 120, sort=1)
    nrm_a = _fn_input(mf, "NormalA", -1400, 240, sort=2)
    nrm_b = _fn_input(mf, "NormalB", -1400, 360, sort=3)
    orm_a = _fn_input(mf, "OrmA", -1400, 480, sort=4)
    orm_b = _fn_input(mf, "OrmB", -1400, 600, sort=5)
    tex_a = _fn_input(mf, "TexEffA", -1400, 720, sort=6)
    tex_b = _fn_input(mf, "TexEffB", -1400, 840, sort=7)
    alpha_in = _fn_input(mf, "BlendAlpha", -1400, 960, sort=8)
    softness = _fn_input(mf, "BlendSoftness", -1400, 1080, sort=9)
    nrm_blend = _fn_input(mf, "NormalBlendStrength", -1400, 1200, sort=10)
    rough_blend = _fn_input(mf, "RoughnessBlendStrength", -1400, 1320, sort=11)

    one = lib.create_expression(mf, unreal.MaterialExpressionConstant, -1100, 1080)
    one.set_editor_property("r", 1.0)
    sm_b = lib.create_expression(mf, unreal.MaterialExpressionAdd, -920, 1020)
    lib.connect(one, "", sm_b, "A")
    lib.connect(softness, "", sm_b, "B")
    pow_n = lib.create_expression(mf, unreal.MaterialExpressionPower, -740, 960)
    lib.connect(alpha_in, "", pow_n, "Base")
    lib.connect(sm_b, "", pow_n, "Exp")
    blend_alpha = lib.create_expression(mf, unreal.MaterialExpressionLinearInterpolate, -560, 960)
    lib.connect(alpha_in, "", blend_alpha, "A")
    lib.connect(pow_n, "", blend_alpha, "B")
    lib.connect(softness, "", blend_alpha, "Alpha")

    nrm_alpha = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -360, 1200)
    lib.connect(blend_alpha, "", nrm_alpha, "A")
    lib.connect(nrm_blend, "", nrm_alpha, "B")
    rough_alpha = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -360, 1320)
    lib.connect(blend_alpha, "", rough_alpha, "A")
    lib.connect(rough_blend, "", rough_alpha, "B")

    alb_out = lib.create_expression(mf, unreal.MaterialExpressionLinearInterpolate, -160, 60)
    lib.connect(alb_a, "", alb_out, "A")
    lib.connect(alb_b, "", alb_out, "B")
    lib.connect(blend_alpha, "", alb_out, "Alpha")
    nrm_out = lib.create_expression(mf, unreal.MaterialExpressionLinearInterpolate, -160, 300)
    lib.connect(nrm_a, "", nrm_out, "A")
    lib.connect(nrm_b, "", nrm_out, "B")
    lib.connect(nrm_alpha, "", nrm_out, "Alpha")
    orm_out = lib.create_expression(mf, unreal.MaterialExpressionLinearInterpolate, -160, 540)
    lib.connect(orm_a, "", orm_out, "A")
    lib.connect(orm_b, "", orm_out, "B")
    lib.connect(rough_alpha, "", orm_out, "Alpha")
    tex_out = lib.create_expression(mf, unreal.MaterialExpressionLinearInterpolate, -160, 780)
    lib.connect(tex_a, "", tex_out, "A")
    lib.connect(tex_b, "", tex_out, "B")
    lib.connect(blend_alpha, "", tex_out, "Alpha")

    _add_function_output(mf, alb_out, "Albedo", 40, 60)
    _add_function_output(mf, nrm_out, "Normal", 40, 300)
    _add_function_output(mf, orm_out, "ORM", 40, 540)
    _add_function_output(mf, tex_out, "TexEff", 40, 780)


def _build_shadow_dream_grade(mf: unreal.MaterialFunction) -> None:
    base = _fn_input(mf, "BaseColor", -1400, 0, sort=0)
    normal = _fn_input(mf, "Normal", -1400, 120, sort=1)
    light_dir = _fn_input(mf, "LightVector", -1400, 240, sort=2)
    shadow_tint = _fn_input(mf, "ShadowTint", -1400, 360, sort=3)
    strength = _fn_input(mf, "Strength", -1400, 480, sort=4)
    softness = _fn_input(mf, "Softness", -1400, 600, sort=5)
    bias = _fn_input(mf, "Bias", -1400, 720, sort=6)
    contact_boost = _fn_input(mf, "ContactBoost", -1400, 840, sort=7)
    contact_mask = _fn_input(mf, "ContactMask", -1400, 960, sort=8)
    ambient_mix = _fn_input(mf, "AmbientMix", -1400, 1080, sort=9)
    ambient_col = _fn_input(mf, "AmbientColor", -1400, 1200, sort=10)

    ndotl = lib.create_expression(mf, unreal.MaterialExpressionDotProduct, -1100, 120)
    lib.connect(normal, "", ndotl, "A")
    lib.connect(light_dir, "", ndotl, "B")
    lit = lib.create_expression(mf, unreal.MaterialExpressionSaturate, -920, 120)
    lib.connect(ndotl, "", lit, "Input")
    shadow_raw = lib.create_expression(mf, unreal.MaterialExpressionOneMinus, -740, 120)
    lib.connect(lit, "", shadow_raw, "Input")
    soft_lo = lib.create_expression(mf, unreal.MaterialExpressionConstant, -920, 280)
    soft_lo.set_editor_property("r", 1.0)
    soft_hi = lib.create_expression(mf, unreal.MaterialExpressionConstant, -920, 380)
    soft_hi.set_editor_property("r", 4.0)
    soft_exp = lib.create_expression(mf, unreal.MaterialExpressionLinearInterpolate, -740, 320)
    lib.connect(soft_lo, "", soft_exp, "A")
    lib.connect(soft_hi, "", soft_exp, "B")
    lib.connect(softness, "", soft_exp, "Alpha")
    shadow_pow = lib.create_expression(mf, unreal.MaterialExpressionPower, -560, 120)
    lib.connect(shadow_raw, "", shadow_pow, "Base")
    lib.connect(soft_exp, "", shadow_pow, "Exp")

    str_bias = lib.create_expression(mf, unreal.MaterialExpressionAdd, -360, 480)
    lib.connect(strength, "", str_bias, "A")
    lib.connect(bias, "", str_bias, "B")
    shadow_amt = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -360, 120)
    lib.connect(shadow_pow, "", shadow_amt, "A")
    lib.connect(str_bias, "", shadow_amt, "B")
    contact_mul = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -180, 840)
    lib.connect(contact_mask, "", contact_mul, "A")
    lib.connect(contact_boost, "", contact_mul, "B")
    one_c = lib.create_expression(mf, unreal.MaterialExpressionConstant, -180, 960)
    one_c.set_editor_property("r", 1.0)
    contact_fac = lib.create_expression(mf, unreal.MaterialExpressionAdd, 0, 900)
    lib.connect(one_c, "", contact_fac, "A")
    lib.connect(contact_mul, "", contact_fac, "B")
    shadow_amt2 = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 0, 120)
    lib.connect(shadow_amt, "", shadow_amt2, "A")
    lib.connect(contact_fac, "", shadow_amt2, "B")
    shadow_sat = lib.create_expression(mf, unreal.MaterialExpressionSaturate, 180, 120)
    lib.connect(shadow_amt2, "", shadow_sat, "Input")

    tint_mix = lib.create_expression(mf, unreal.MaterialExpressionLinearInterpolate, 0, 360)
    lib.connect(shadow_tint, "", tint_mix, "A")
    lib.connect(ambient_col, "", tint_mix, "B")
    lib.connect(ambient_mix, "", tint_mix, "Alpha")
    color_out = lib.create_expression(mf, unreal.MaterialExpressionLinearInterpolate, 360, 80)
    lib.connect(base, "", color_out, "A")
    lib.connect(tint_mix, "", color_out, "B")
    lib.connect(shadow_sat, "", color_out, "Alpha")
    _add_function_output(mf, color_out, "Color", 540, 80)
    _add_function_output(mf, shadow_sat, "ShadowAmount", 540, 240)


def _build_shadow_flower_project(mf: unreal.MaterialFunction) -> None:
    world_xy = _fn_input(mf, "WorldXY", -1400, 0, sort=0)
    shadow_mask = _fn_input(mf, "ShadowMask", -1400, 120, sort=1)
    shadow_amt = _fn_input(mf, "ShadowAmount", -1400, 240, sort=2)
    scale = _fn_input(mf, "Scale", -1400, 360, sort=3)
    scale_fine = _fn_input(mf, "ScaleFine", -1400, 480, sort=4)
    rotation = _fn_input(mf, "Rotation", -1400, 600, sort=5)
    jitter = _fn_input(mf, "Jitter", -1400, 720, sort=6)
    flower_col = _fn_input(mf, "FlowerColor", -1400, 840, sort=7)
    strength = _fn_input(mf, "Strength", -1400, 960, sort=8)
    softness = _fn_input(mf, "Softness", -1400, 1080, sort=9)
    albedo_dark = _fn_input(mf, "AlbedoDarken", -1400, 1200, sort=10)
    pulse = _fn_input(mf, "Pulse", -1400, 1320, sort=11)
    pulse_str = _fn_input(mf, "PulseStrength", -1400, 1440, sort=12)

    def _petal_layer(xy_in, scl_in, rot_in, tag_y: int):
        uv_s = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -1100, tag_y)
        lib.connect(xy_in, "", uv_s, "A")
        lib.connect(scl_in, "", uv_s, "B")
        jx = lib.create_expression(mf, unreal.MaterialExpressionComponentMask, -920, tag_y - 40)
        jx.set_editor_property("r", True)
        jx.set_editor_property("g", False)
        jx.set_editor_property("b", False)
        jx.set_editor_property("a", False)
        lib.connect(xy_in, "", jx, "")
        j_mul = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -760, tag_y)
        lib.connect(jx, "", j_mul, "A")
        lib.connect(jitter, "", j_mul, "B")
        uv_j = lib.create_expression(mf, unreal.MaterialExpressionAdd, -600, tag_y)
        lib.connect(uv_s, "", uv_j, "A")
        lib.connect(j_mul, "", uv_j, "B")
        rot_mul = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -440, tag_y)
        lib.connect(uv_j, "", rot_mul, "A")
        lib.connect(rot_in, "", rot_mul, "B")
        samp = lib.create_expression(mf, unreal.MaterialExpressionTextureSample, -260, tag_y)
        lib.connect(shadow_mask, "Texture", samp, "Texture")
        lib.connect(rot_mul, "", samp, "UVs")
        mask_r = lib.create_expression(mf, unreal.MaterialExpressionComponentMask, -80, tag_y)
        mask_r.set_editor_property("r", True)
        mask_r.set_editor_property("g", False)
        mask_r.set_editor_property("b", False)
        mask_r.set_editor_property("a", False)
        lib.connect(samp, "", mask_r, "")
        return mask_r

    coarse = _petal_layer(world_xy, scale, rotation, 200)
    fine = _petal_layer(world_xy, scale_fine, rotation, 400)
    dual = lib.create_expression(mf, unreal.MaterialExpressionAdd, 120, 300)
    lib.connect(coarse, "", dual, "A")
    lib.connect(fine, "", dual, "B")
    petal = lib.create_expression(mf, unreal.MaterialExpressionSaturate, 300, 300)
    lib.connect(dual, "", petal, "Input")

    soft_one = lib.create_expression(mf, unreal.MaterialExpressionAdd, 300, 420)
    one_s = lib.create_expression(mf, unreal.MaterialExpressionConstant, 300, 500)
    one_s.set_editor_property("r", 1.0)
    lib.connect(one_s, "", soft_one, "A")
    lib.connect(softness, "", soft_one, "B")
    soft_pow = lib.create_expression(mf, unreal.MaterialExpressionPower, 480, 300)
    lib.connect(petal, "", soft_pow, "Base")
    lib.connect(soft_one, "", soft_pow, "Exp")

    pulse_fac = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 480, 480)
    lib.connect(pulse, "", pulse_fac, "A")
    lib.connect(pulse_str, "", pulse_fac, "B")
    pulse_one = lib.create_expression(mf, unreal.MaterialExpressionConstant, 480, 580)
    pulse_one.set_editor_property("r", 1.0)
    pulse_add = lib.create_expression(mf, unreal.MaterialExpressionAdd, 660, 480)
    lib.connect(pulse_one, "", pulse_add, "A")
    lib.connect(pulse_fac, "", pulse_add, "B")

    in_shadow = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 660, 300)
    lib.connect(soft_pow, "", in_shadow, "A")
    lib.connect(shadow_amt, "", in_shadow, "B")
    gated = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 840, 300)
    lib.connect(in_shadow, "", gated, "A")
    lib.connect(strength, "", gated, "B")
    gated2 = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 1020, 300)
    lib.connect(gated, "", gated2, "A")
    lib.connect(pulse_add, "", gated2, "B")

    darken = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 1200, 200)
    lib.connect(gated2, "", darken, "A")
    lib.connect(albedo_dark, "", darken, "B")
    emis = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 1200, 400)
    lib.connect(gated2, "", emis, "A")
    lib.connect(flower_col, "", emis, "B")

    _add_function_output(mf, darken, "ColorDarken", 1380, 200)
    _add_function_output(mf, emis, "EmissiveAdd", 1380, 400)
    _add_function_output(mf, gated2, "Mask", 1380, 300)


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


def _build_anime_skin_wrap(mf: unreal.MaterialFunction) -> None:
    """Wrapped N·L proxy for anime skin — strength 0 = neutral lit factor (~1)."""
    normal = lib.create_expression(mf, unreal.MaterialExpressionPixelNormalWS, -900, 0)
    light_dir = lib.create_expression(mf, unreal.MaterialExpressionConstant3Vector, -900, 140)
    light_dir.set_editor_property("constant", unreal.LinearColor(0.35, 0.55, 0.85, 1.0))
    ndotl = lib.create_expression(mf, unreal.MaterialExpressionDotProduct, -680, 40)
    lib.connect(normal, "", ndotl, "A")
    lib.connect(light_dir, "", ndotl, "B")
    wrap_str = lib.scalar_param(mf, "WrapStrength", "Skin", 0.0, -900, 280)
    wrap_rad = lib.scalar_param(mf, "WrapRadius", "Skin", 0.55, -900, 380)
    wrap_mul = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -520, 120)
    lib.connect(wrap_rad, "", wrap_mul, "A")
    lib.connect(wrap_str, "", wrap_mul, "B")
    wrap_add = lib.create_expression(mf, unreal.MaterialExpressionAdd, -360, 40)
    lib.connect(ndotl, "", wrap_add, "A")
    lib.connect(wrap_mul, "", wrap_add, "B")
    one = lib.create_expression(mf, unreal.MaterialExpressionConstant, -520, 260)
    one.set_editor_property("r", 1.0)
    wrap_den = lib.create_expression(mf, unreal.MaterialExpressionAdd, -360, 200)
    lib.connect(one, "", wrap_den, "A")
    lib.connect(wrap_rad, "", wrap_den, "B")
    wrap_div = lib.create_expression(mf, unreal.MaterialExpressionDivide, -200, 80)
    lib.connect(wrap_add, "", wrap_div, "A")
    lib.connect(wrap_den, "", wrap_div, "B")
    wrap_sat = lib.create_expression(mf, unreal.MaterialExpressionSaturate, -40, 80)
    lib.connect_unary(wrap_div, wrap_sat)
    std_sat = lib.create_expression(mf, unreal.MaterialExpressionSaturate, -200, 220)
    lib.connect_unary(ndotl, std_sat)
    lit = lib.create_expression(mf, unreal.MaterialExpressionLinearInterpolate, 120, 120)
    lib.connect(std_sat, "", lit, "A")
    lib.connect(wrap_sat, "", lit, "B")
    lib.connect(wrap_str, "", lit, "Alpha")
    _add_function_output(mf, lit, "Result", 300, 120)


def _build_parallax_core(mf: unreal.MaterialFunction) -> None:
    """Parallax UV offset: mode 0 simple, 1 steep, 2 stepped POM proxy."""
    uv_in = _fn_input(mf, "UV", -1400, 0, sort=0)
    ht_in = _fn_input(mf, "HeightTexture", -1400, 120, sort=1)
    scale_in = _fn_input(mf, "ParallaxScale", -1400, 240, sort=2)
    layer_in = _fn_input(mf, "LayerParallaxScale", -1400, 360, sort=3)
    str_in = _fn_input(mf, "ParallaxStrength", -1400, 480, sort=4)
    height_in = _fn_input(mf, "ParallaxHeight", -1400, 600, sort=5)
    steps_in = _fn_input(mf, "ParallaxSteps", -1400, 720, sort=6)
    mode_in = _fn_input(mf, "ParallaxMode", -1400, 840, sort=7)

    h_s = lib.create_expression(mf, unreal.MaterialExpressionTextureSample, -1120, 40)
    lib.connect_any(ht_in, h_s, ("Tex", "TextureObject"))
    lib.connect_any(uv_in, h_s, ("UVs", "Coordinates"))
    h_r = lib.create_expression(mf, unreal.MaterialExpressionComponentMask, -960, 40)
    h_r.set_editor_property("r", True)
    h_r.set_editor_property("g", False)
    h_r.set_editor_property("b", False)
    h_r.set_editor_property("a", False)
    lib.connect_unary(h_s, h_r)

    eff_scale = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -800, 200)
    lib.connect(scale_in, "", eff_scale, "A")
    lib.connect(layer_in, "", eff_scale, "B")
    eff_scale2 = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -640, 200)
    lib.connect(eff_scale, "", eff_scale2, "A")
    lib.connect(height_in, "", eff_scale2, "B")
    pom_s = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -800, 40)
    lib.connect(h_r, "", pom_s, "A")
    lib.connect(eff_scale2, "", pom_s, "B")
    pom_s2 = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -640, 40)
    lib.connect(pom_s, "", pom_s2, "A")
    lib.connect(str_in, "", pom_s2, "B")

    view_xy = _view_xy(mf, -1120, 320)
    off_simple = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -480, 120)
    lib.connect(pom_s2, "", off_simple, "A")
    lib.connect(view_xy, "", off_simple, "B")

    steep_mul = lib.create_expression(mf, unreal.MaterialExpressionConstant, -640, 280)
    steep_mul.set_editor_property("r", 1.75)
    off_steep = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -480, 280)
    lib.connect(off_simple, "", off_steep, "A")
    lib.connect(steep_mul, "", off_steep, "B")

    uv_pre = lib.create_expression(mf, unreal.MaterialExpressionAdd, -320, 120)
    lib.connect(uv_in, "", uv_pre, "A")
    lib.connect(off_simple, "", uv_pre, "B")
    h_s2 = lib.create_expression(mf, unreal.MaterialExpressionTextureSample, -1120, 520)
    lib.connect_any(ht_in, h_s2, ("Tex", "TextureObject"))
    lib.connect_any(uv_pre, h_s2, ("UVs", "Coordinates"))
    h_r2 = lib.create_expression(mf, unreal.MaterialExpressionComponentMask, -960, 520)
    h_r2.set_editor_property("r", True)
    h_r2.set_editor_property("g", False)
    h_r2.set_editor_property("b", False)
    h_r2.set_editor_property("a", False)
    lib.connect_unary(h_s2, h_r2)
    h_blend = lib.create_expression(mf, unreal.MaterialExpressionAdd, -800, 480)
    lib.connect(h_r, "", h_blend, "A")
    lib.connect(h_r2, "", h_blend, "B")
    half = lib.create_expression(mf, unreal.MaterialExpressionConstant, -960, 620)
    half.set_editor_property("r", 0.5)
    h_avg = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -640, 500)
    lib.connect(h_blend, "", h_avg, "A")
    lib.connect(half, "", h_avg, "B")
    steps_norm = lib.create_expression(mf, unreal.MaterialExpressionConstant, -800, 640)
    steps_norm.set_editor_property("r", 0.125)
    steps_mul = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -640, 640)
    lib.connect(steps_in, "", steps_mul, "A")
    lib.connect(steps_norm, "", steps_mul, "B")
    pom_pom = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -480, 500)
    lib.connect(h_avg, "", pom_pom, "A")
    lib.connect(eff_scale2, "", pom_pom, "B")
    pom_pom2 = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -320, 500)
    lib.connect(pom_pom, "", pom_pom2, "A")
    lib.connect(str_in, "", pom_pom2, "B")
    pom_pom3 = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -160, 500)
    lib.connect(pom_pom2, "", pom_pom3, "A")
    lib.connect(steps_mul, "", pom_pom3, "B")
    off_pom = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 0, 500)
    lib.connect(pom_pom3, "", off_pom, "A")
    lib.connect(view_xy, "", off_pom, "B")

    blend_01 = lib.create_expression(mf, unreal.MaterialExpressionSaturate, -320, 840)
    lib.connect_unary(mode_in, blend_01)
    mode_12 = lib.create_expression(mf, unreal.MaterialExpressionSubtract, -480, 920)
    one = lib.create_expression(mf, unreal.MaterialExpressionConstant, -640, 920)
    one.set_editor_property("r", 1.0)
    lib.connect(mode_in, "", mode_12, "A")
    lib.connect(one, "", mode_12, "B")
    blend_12 = lib.create_expression(mf, unreal.MaterialExpressionSaturate, -320, 920)
    lib.connect_unary(mode_12, blend_12)
    off_01 = lib.create_expression(mf, unreal.MaterialExpressionLinearInterpolate, 160, 200)
    lib.connect(off_simple, "", off_01, "A")
    lib.connect(off_steep, "", off_01, "B")
    lib.connect(blend_01, "", off_01, "Alpha")
    off_final = lib.create_expression(mf, unreal.MaterialExpressionLinearInterpolate, 320, 360)
    lib.connect(off_01, "", off_final, "A")
    lib.connect(off_pom, "", off_final, "B")
    lib.connect(blend_12, "", off_final, "Alpha")
    uv_out = lib.create_expression(mf, unreal.MaterialExpressionAdd, 480, 360)
    lib.connect(uv_in, "", uv_out, "A")
    lib.connect(off_final, "", uv_out, "B")
    _add_function_output(mf, uv_out, "UV", 640, 360)


def _build_normal_adjust(mf: unreal.MaterialFunction) -> None:
    """Unpack normal map, scale XY, power Z, per-layer strength."""
    n_in = _fn_input(mf, "Normal", -1000, 0, sort=0)
    str_in = _fn_input(mf, "NormalStrength", -1000, 120, sort=1)
    pow_in = _fn_input(mf, "NormalPower", -1000, 240, sort=2)
    layer_in = _fn_input(mf, "LayerNormalStrength", -1000, 360, sort=3)

    two = lib.create_expression(mf, unreal.MaterialExpressionConstant, -800, 80)
    two.set_editor_property("r", 2.0)
    n_unpk = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -640, 40)
    lib.connect(n_in, "", n_unpk, "A")
    lib.connect(two, "", n_unpk, "B")
    one = lib.create_expression(mf, unreal.MaterialExpressionConstant, -800, 160)
    one.set_editor_property("r", 1.0)
    n_off = lib.create_expression(mf, unreal.MaterialExpressionSubtract, -480, 40)
    lib.connect(n_unpk, "", n_off, "A")
    lib.connect(one, "", n_off, "B")

    eff_str = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -640, 280)
    lib.connect(str_in, "", eff_str, "A")
    lib.connect(layer_in, "", eff_str, "B")
    n_xy = lib.create_expression(mf, unreal.MaterialExpressionComponentMask, -320, 0)
    n_xy.set_editor_property("r", True)
    n_xy.set_editor_property("g", True)
    n_xy.set_editor_property("b", False)
    n_xy.set_editor_property("a", False)
    lib.connect_unary(n_off, n_xy)
    n_z = lib.create_expression(mf, unreal.MaterialExpressionComponentMask, -320, 120)
    n_z.set_editor_property("r", False)
    n_z.set_editor_property("g", False)
    n_z.set_editor_property("b", True)
    n_z.set_editor_property("a", False)
    lib.connect_unary(n_off, n_z)
    xy_s = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -160, 0)
    lib.connect(n_xy, "", xy_s, "A")
    lib.connect(eff_str, "", xy_s, "B")
    half = lib.create_expression(mf, unreal.MaterialExpressionConstant, -480, 200)
    half.set_editor_property("r", 0.5)
    z_pos = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -320, 200)
    lib.connect(n_z, "", z_pos, "A")
    lib.connect(half, "", z_pos, "B")
    z_pos2 = lib.create_expression(mf, unreal.MaterialExpressionAdd, -160, 200)
    lib.connect(z_pos, "", z_pos2, "A")
    lib.connect(half, "", z_pos2, "B")
    z_sat = lib.create_expression(mf, unreal.MaterialExpressionSaturate, 0, 200)
    lib.connect_unary(z_pos2, z_sat)
    z_pow = lib.create_expression(mf, unreal.MaterialExpressionPower, 160, 200)
    lib.connect(z_sat, "", z_pow, "Base")
    lib.connect(pow_in, "", z_pow, "Exp")
    z_back = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 320, 200)
    lib.connect(z_pow, "", z_back, "A")
    lib.connect(two, "", z_back, "B")
    z_final = lib.create_expression(mf, unreal.MaterialExpressionSubtract, 480, 200)
    lib.connect(z_back, "", z_final, "A")
    lib.connect(one, "", z_final, "B")
    n_ts = lib.create_expression(mf, unreal.MaterialExpressionAppendVector, 320, 40)
    lib.connect_append2(xy_s, z_final, n_ts)
    len_n = lib.create_expression(mf, unreal.MaterialExpressionSquareRoot, 640, 80)
    dot = lib.create_expression(mf, unreal.MaterialExpressionDotProduct, 480, 80)
    lib.connect(n_ts, "", dot, "A")
    lib.connect(n_ts, "", dot, "B")
    lib.connect_unary(dot, len_n)
    eps = lib.create_expression(mf, unreal.MaterialExpressionConstant, 480, 180)
    eps.set_editor_property("r", 0.001)
    len_safe = lib.create_expression(mf, unreal.MaterialExpressionAdd, 640, 180)
    lib.connect(len_n, "", len_safe, "A")
    lib.connect(eps, "", len_safe, "B")
    n_norm = lib.create_expression(mf, unreal.MaterialExpressionDivide, 800, 80)
    lib.connect(n_ts, "", n_norm, "A")
    lib.connect(len_safe, "", n_norm, "B")
    half_v = lib.create_expression(mf, unreal.MaterialExpressionConstant, 800, 200)
    half_v.set_editor_property("r", 0.5)
    n_pack = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 960, 80)
    lib.connect(n_norm, "", n_pack, "A")
    lib.connect(half_v, "", n_pack, "B")
    n_pack2 = lib.create_expression(mf, unreal.MaterialExpressionAdd, 1120, 80)
    lib.connect(n_pack, "", n_pack2, "A")
    lib.connect(half_v, "", n_pack2, "B")
    _add_function_output(mf, n_pack2, "Normal", 1280, 80)


def _build_water_depth_color(mf: unreal.MaterialFunction) -> None:
    shallow = _fn_input(mf, "WaterColorShallow", -1200, 0, sort=0)
    deep = _fn_input(mf, "WaterColorDeep", -1200, 120, sort=1)
    fade_in = _fn_input(mf, "DepthFadeDistance", -1200, 240, sort=2)
    depth_in = _fn_input(mf, "Depth", -1200, 360, sort=3)

    safe = lib.create_expression(mf, unreal.MaterialExpressionConstant, -960, 280)
    safe.set_editor_property("r", 0.001)
    fade_safe = lib.create_expression(mf, unreal.MaterialExpressionAdd, -800, 240)
    lib.connect(fade_in, "", fade_safe, "A")
    lib.connect(safe, "", fade_safe, "B")
    norm = lib.create_expression(mf, unreal.MaterialExpressionDivide, -640, 300)
    lib.connect(depth_in, "", norm, "A")
    lib.connect(fade_safe, "", norm, "B")
    alpha = lib.create_expression(mf, unreal.MaterialExpressionSaturate, -480, 300)
    lib.connect_unary(norm, alpha)
    lerp = lib.create_expression(mf, unreal.MaterialExpressionLinearInterpolate, -320, 80)
    lib.connect(shallow, "", lerp, "A")
    lib.connect(deep, "", lerp, "B")
    lib.connect(alpha, "", lerp, "Alpha")
    _add_function_output(mf, lerp, "Color", 0, 80)


def _build_water_shoreline_fade(mf: unreal.MaterialFunction) -> None:
    uv_in = _fn_input(mf, "UV", -1200, 0, sort=0)
    width_in = _fn_input(mf, "ShorelineWidth", -1200, 120, sort=1)
    foam_in = _fn_input(mf, "ShorelineFoam", -1200, 240, sort=2)

    half = lib.create_expression(mf, unreal.MaterialExpressionConstant, -960, 40)
    half.set_editor_property("r", 0.5)
    uv_c = lib.create_expression(mf, unreal.MaterialExpressionSubtract, -800, 0)
    lib.connect(uv_in, "", uv_c, "A")
    lib.connect(half, "", uv_c, "B")
    dist = lib.create_expression(mf, unreal.MaterialExpressionDistance, -640, 0)
    lib.connect(uv_c, "", dist, "A")
    zero = lib.create_expression(mf, unreal.MaterialExpressionConstant, -800, 120)
    zero.set_editor_property("r", 0.0)
    lib.connect(zero, "", dist, "B")
    two = lib.create_expression(mf, unreal.MaterialExpressionConstant, -800, 200)
    two.set_editor_property("r", 2.0)
    dist_n = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -480, 0)
    lib.connect(dist, "", dist_n, "A")
    lib.connect(two, "", dist_n, "B")
    one = lib.create_expression(mf, unreal.MaterialExpressionConstant, -640, 200)
    one.set_editor_property("r", 1.0)
    inv_w = lib.create_expression(mf, unreal.MaterialExpressionSubtract, -480, 160)
    lib.connect(one, "", inv_w, "A")
    lib.connect(width_in, "", inv_w, "B")
    edge = lib.create_expression(mf, unreal.MaterialExpressionSmoothStep, -320, 80)
    lib.connect(inv_w, "", edge, "Min")
    lib.connect(one, "", edge, "Max")
    lib.connect(dist_n, "", edge, "Value")
    foam = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -160, 160)
    lib.connect(foam_in, "", foam, "A")
    lib.connect(edge, "", foam, "B")
    _add_function_output(mf, edge, "Alpha", 0, 80)
    _add_function_output(mf, foam, "Foam", 160, 160)


def _build_water_foam(mf: unreal.MaterialFunction) -> None:
    normal_in = _fn_input(mf, "Normal", -1000, 0, sort=0)
    strength = _fn_input(mf, "FoamStrength", -1000, 120, sort=1)
    n_z = lib.create_expression(mf, unreal.MaterialExpressionComponentMask, -760, 0)
    n_z.set_editor_property("r", False)
    n_z.set_editor_property("g", False)
    n_z.set_editor_property("b", True)
    n_z.set_editor_property("a", False)
    lib.connect_unary(normal_in, n_z)
    crest = lib.create_expression(mf, unreal.MaterialExpressionPower, -560, 0)
    lib.connect(n_z, "", crest, "Base")
    exp_c = lib.create_expression(mf, unreal.MaterialExpressionConstant, -760, 120)
    exp_c.set_editor_property("r", 4.0)
    lib.connect(exp_c, "", crest, "Exp")
    foam = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -360, 0)
    lib.connect(crest, "", foam, "A")
    lib.connect(strength, "", foam, "B")
    _add_function_output(mf, foam, "Foam", -160, 0)


def _build_landscape_height_compete(mf: unreal.MaterialFunction) -> None:
    rock_h = _fn_input(mf, "RockHeight", -1200, 0, sort=0)
    grass_h = _fn_input(mf, "GrassHeight", -1200, 120, sort=1)
    mud_h = _fn_input(mf, "MudHeight", -1200, 240, sort=2)
    blend_str = _fn_input(mf, "HeightBlendStrength", -1200, 360, sort=3)
    grass_amt = _fn_input(mf, "GrassAmount", -1200, 480, sort=4)
    mud_amt = _fn_input(mf, "MudAmount", -1200, 600, sort=5)

    diff_gr = lib.create_expression(mf, unreal.MaterialExpressionSubtract, -900, 80)
    lib.connect(grass_h, "", diff_gr, "A")
    lib.connect(rock_h, "", diff_gr, "B")
    diff_gm = lib.create_expression(mf, unreal.MaterialExpressionSubtract, -900, 220)
    lib.connect(grass_h, "", diff_gm, "A")
    lib.connect(mud_h, "", diff_gm, "B")
    mod_gr = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -700, 80)
    lib.connect(diff_gr, "", mod_gr, "A")
    lib.connect(blend_str, "", mod_gr, "B")
    mod_gm = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -700, 220)
    lib.connect(diff_gm, "", mod_gm, "A")
    lib.connect(blend_str, "", mod_gm, "B")
    alpha_grass = lib.create_expression(mf, unreal.MaterialExpressionClamp, -500, 80)
    lib.connect(mod_gr, "", alpha_grass, "Input")
    alpha_mud = lib.create_expression(mf, unreal.MaterialExpressionClamp, -500, 220)
    lib.connect(mod_gm, "", alpha_mud, "Input")
    grass_gate = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -300, 80)
    lib.connect(alpha_grass, "", grass_gate, "A")
    lib.connect(grass_amt, "", grass_gate, "B")
    mud_gate = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -300, 220)
    lib.connect(alpha_mud, "", mud_gate, "A")
    lib.connect(mud_amt, "", mud_gate, "B")
    _add_function_output(mf, grass_gate, "GrassAlpha", 0, 80)
    _add_function_output(mf, mud_gate, "MudAlpha", 0, 220)


def _build_nikki_dream_grade(mf: unreal.MaterialFunction) -> None:
    base = _fn_input(mf, "BaseColor", -1200, 0, sort=0)
    pastel = _fn_input(mf, "PastelLift", -1200, 120, sort=1)
    dream_tint = _fn_input(mf, "DreamTint", -1200, 240, sort=2)
    dream_sat = _fn_input(mf, "DreamSaturation", -1200, 360, sort=3)
    dream_con = _fn_input(mf, "DreamContrast", -1200, 480, sort=4)
    shadow_lift = _fn_input(mf, "DreamShadowLift", -1200, 600, sort=5)

    pastel_mix = lib.create_expression(mf, unreal.MaterialExpressionLinearInterpolate, -900, 80)
    lib.connect(base, "", pastel_mix, "A")
    lib.connect(dream_tint, "", pastel_mix, "B")
    lib.connect(pastel, "", pastel_mix, "Alpha")

    lum = lib.create_expression(mf, unreal.MaterialExpressionDotProduct, -720, 200)
    weights = lib.create_expression(mf, unreal.MaterialExpressionConstant3Vector, -900, 200)
    weights.set_editor_property("constant", unreal.LinearColor(0.299, 0.587, 0.114, 1.0))
    lib.connect(pastel_mix, "", lum, "A")
    lib.connect(weights, "", lum, "B")

    sat_mul = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -540, 80)
    lib.connect(pastel_mix, "", sat_mul, "A")
    sat_one = lib.create_expression(mf, unreal.MaterialExpressionConstant, -720, 40)
    sat_one.set_editor_property("r", 1.0)
    sat_add = lib.create_expression(mf, unreal.MaterialExpressionAdd, -720, 120)
    lib.connect(sat_one, "", sat_add, "A")
    lib.connect(dream_sat, "", sat_add, "B")
    lib.connect(sat_add, "", sat_mul, "B")

    con_sub = lib.create_expression(mf, unreal.MaterialExpressionSubtract, -360, 80)
    lib.connect(sat_mul, "", con_sub, "A")
    con_mid = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -540, 200)
    lib.connect(lum, "", con_mid, "A")
    lib.connect(dream_con, "", con_mid, "B")
    lib.connect(con_mid, "", con_sub, "B")

    lifted = lib.create_expression(mf, unreal.MaterialExpressionAdd, -180, 80)
    lib.connect(con_sub, "", lifted, "A")
    lib.connect(shadow_lift, "", lifted, "B")
    _add_function_output(mf, lifted, "Color", 0, 80)


def _build_nikki_rim_glow(mf: unreal.MaterialFunction) -> None:
    base = _fn_input(mf, "BaseColor", -1200, 0, sort=0)
    normal = _fn_input(mf, "Normal", -1200, 120, sort=1)
    rim_col = _fn_input(mf, "RimColor", -1200, 240, sort=2)
    rim_int = _fn_input(mf, "RimIntensity", -1200, 360, sort=3)
    rim_width = _fn_input(mf, "RimWidth", -1200, 480, sort=4)
    glow_int = _fn_input(mf, "GlowIntensity", -1200, 600, sort=5)
    bloom = _fn_input(mf, "BloomBoost", -1200, 720, sort=6)

    fresnel = lib.create_expression(mf, unreal.MaterialExpressionFresnel, -800, 200)
    lib.connect(normal, "", fresnel, "Normal")
    lib.connect(rim_width, "", fresnel, "ExponentIn")
    rim_mul = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -560, 200)
    lib.connect(fresnel, "", rim_mul, "A")
    lib.connect(rim_int, "", rim_mul, "B")
    rim_col_mul = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -360, 200)
    lib.connect(rim_mul, "", rim_col_mul, "A")
    lib.connect(rim_col, "", rim_col_mul, "B")

    glow = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -360, 360)
    lib.connect(glow_int, "", glow, "A")
    lib.connect(bloom, "", glow, "B")
    glow_col = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -180, 280)
    lib.connect(rim_col_mul, "", glow_col, "A")
    lib.connect(glow, "", glow_col, "B")

    out = lib.create_expression(mf, unreal.MaterialExpressionAdd, 0, 120)
    lib.connect(base, "", out, "A")
    lib.connect(glow_col, "", out, "B")
    _add_function_output(mf, out, "Color", 180, 120)


def _build_nikki_sparkle(mf: unreal.MaterialFunction) -> None:
    base = _fn_input(mf, "BaseColor", -1200, 0, sort=0)
    uv = _fn_input(mf, "UV", -1200, 120, sort=1)
    sparkle_mask = _fn_input(mf, "SparkleMask", -1200, 240, sort=2)
    sparkle_int = _fn_input(mf, "SparkleIntensity", -1200, 360, sort=3)
    threshold = _fn_input(mf, "SparkleThreshold", -1200, 480, sort=4)
    sparkle_col = _fn_input(mf, "SparkleColor", -1200, 600, sort=5)

    sample = lib.create_expression(mf, unreal.MaterialExpressionTextureSample, -900, 240)
    lib.connect(sparkle_mask, "Texture", sample, "Texture")
    lib.connect(uv, "", sample, "UVs")

    thr_sub = lib.create_expression(mf, unreal.MaterialExpressionSubtract, -700, 240)
    lib.connect(sample, "R", thr_sub, "A")
    lib.connect(threshold, "", thr_sub, "B")
    spark = lib.create_expression(mf, unreal.MaterialExpressionSaturate, -520, 240)
    lib.connect(thr_sub, "", spark, "Input")
    spark_mul = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -340, 200)
    lib.connect(spark, "", spark_mul, "A")
    lib.connect(sparkle_int, "", spark_mul, "B")
    tint = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -160, 200)
    lib.connect(spark_mul, "", tint, "A")
    lib.connect(sparkle_col, "", tint, "B")
    out = lib.create_expression(mf, unreal.MaterialExpressionAdd, 20, 80)
    lib.connect(base, "", out, "A")
    lib.connect(tint, "", out, "B")
    _add_function_output(mf, out, "Color", 200, 80)


def _build_nikki_iridescence_sheen(mf: unreal.MaterialFunction) -> None:
    base = _fn_input(mf, "BaseColor", -1200, 0, sort=0)
    normal = _fn_input(mf, "Normal", -1200, 120, sort=1)
    irid = _fn_input(mf, "Iridescence", -1200, 240, sort=2)
    irid_tint = _fn_input(mf, "IridescenceTint", -1200, 360, sort=3)
    irid_pow = _fn_input(mf, "IridescencePower", -1200, 480, sort=4)
    sheen = _fn_input(mf, "FabricSheen", -1200, 600, sort=5)
    sheen_tint = _fn_input(mf, "SheenTint", -1200, 720, sort=6)

    fresnel = lib.create_expression(mf, unreal.MaterialExpressionFresnel, -800, 200)
    lib.connect(normal, "", fresnel, "Normal")
    lib.connect(irid_pow, "", fresnel, "ExponentIn")
    irid_mask = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -560, 200)
    lib.connect(fresnel, "", irid_mask, "A")
    lib.connect(irid, "", irid_mask, "B")
    irid_col = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -360, 200)
    lib.connect(irid_mask, "", irid_col, "A")
    lib.connect(irid_tint, "", irid_col, "B")

    sheen_mul = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -360, 400)
    lib.connect(sheen, "", sheen_mul, "A")
    lib.connect(sheen_tint, "", sheen_mul, "B")

    combined = lib.create_expression(mf, unreal.MaterialExpressionAdd, -160, 280)
    lib.connect(irid_col, "", combined, "A")
    lib.connect(sheen_mul, "", combined, "B")
    out = lib.create_expression(mf, unreal.MaterialExpressionAdd, 20, 120)
    lib.connect(base, "", out, "A")
    lib.connect(combined, "", out, "B")
    _add_function_output(mf, out, "Color", 200, 120)


def _build_macro_detail(mf: unreal.MaterialFunction) -> None:
    base = _fn_input(mf, "BaseColor", -1200, 0, sort=0)
    normal = _fn_input(mf, "Normal", -1200, 120, sort=1)
    macro_str = _fn_input(mf, "MacroVariationStrength", -1200, 240, sort=2)
    macro_scale = _fn_input(mf, "MacroScale", -1200, 360, sort=3)
    det_tiling = _fn_input(mf, "DetailTiling", -1200, 480, sort=4)
    det_str = _fn_input(mf, "DetailStrength", -1200, 600, sort=5)
    det_tex = lib.texture_param(mf, "DetailNormal", "MacroDetail", -1200, 720)

    mac_tc = lib.create_expression(mf, unreal.MaterialExpressionTextureCoordinate, -900, 620)
    mac_scl = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -740, 620)
    lib.connect(mac_tc, "", mac_scl, "A")
    lib.connect(macro_scale, "", mac_scl, "B")
    tile48 = lib.create_expression(mf, unreal.MaterialExpressionConstant, -900, 720)
    tile48.set_editor_property("r", 48.0)
    mac_tile = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -580, 620)
    lib.connect(mac_scl, "", mac_tile, "A")
    lib.connect(tile48, "", mac_tile, "B")
    mac_nx = lib.create_expression(mf, unreal.MaterialExpressionComponentMask, -420, 560)
    mac_nx.set_editor_property("r", True)
    mac_nx.set_editor_property("g", False)
    mac_nx.set_editor_property("b", False)
    mac_nx.set_editor_property("a", False)
    lib.connect(mac_tile, "", mac_nx, "")
    mac_ny = lib.create_expression(mf, unreal.MaterialExpressionComponentMask, -420, 640)
    mac_ny.set_editor_property("r", False)
    mac_ny.set_editor_property("g", True)
    mac_ny.set_editor_property("b", False)
    mac_ny.set_editor_property("a", False)
    lib.connect(mac_tile, "", mac_ny, "")
    mac_nz = lib.create_expression(mf, unreal.MaterialExpressionConstant, -420, 720)
    mac_nz.set_editor_property("r", 0.0)
    mac_pos = lib.create_expression(mf, unreal.MaterialExpressionAppendVector, -260, 620)
    lib.connect(mac_nx, "", mac_pos, "A")
    lib.connect(mac_ny, "", mac_pos, "B")
    mac_noise = lib.create_expression(mf, unreal.MaterialExpressionNoise, -100, 620)
    lib.connect(mac_pos, "", mac_noise, "Position", "")
    half = lib.create_expression(mf, unreal.MaterialExpressionConstant, -260, 720)
    half.set_editor_property("r", 0.5)
    mac_sub = lib.create_expression(mf, unreal.MaterialExpressionSubtract, 60, 620)
    lib.connect(mac_noise, "", mac_sub, "A")
    lib.connect(half, "", mac_sub, "B")
    mac_amt = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 220, 620)
    lib.connect(mac_sub, "", mac_amt, "A")
    lib.connect(macro_str, "", mac_amt, "B")
    one = lib.create_expression(mf, unreal.MaterialExpressionConstant, 60, 720)
    one.set_editor_property("r", 1.0)
    mac_fac = lib.create_expression(mf, unreal.MaterialExpressionAdd, 380, 600)
    lib.connect(one, "", mac_fac, "A")
    lib.connect(mac_amt, "", mac_fac, "B")
    color_out = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 540, 480)
    lib.connect(base, "", color_out, "A")
    lib.connect(mac_fac, "", color_out, "B")

    det_tc = lib.create_expression(mf, unreal.MaterialExpressionTextureCoordinate, -900, 900)
    det_uv = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -740, 900)
    lib.connect(det_tc, "", det_uv, "A")
    lib.connect(det_tiling, "", det_uv, "B")
    det_s = lib.create_expression(mf, unreal.MaterialExpressionTextureSample, -580, 900)
    lib.try_set_editor_property(det_s, "sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    lib.connect(det_tex, "Texture", det_s, "Texture")
    lib.connect(det_uv, "", det_s, "UVs")
    nrm_out = lib.create_expression(mf, unreal.MaterialExpressionLinearInterpolate, -360, 900)
    lib.connect(normal, "", nrm_out, "A")
    lib.connect(det_s, "", nrm_out, "B")
    lib.connect(det_str, "", nrm_out, "Alpha")

    _add_function_output(mf, color_out, "Color", 720, 480)
    _add_function_output(mf, nrm_out, "Normal", 720, 900)


def _build_magical(mf: unreal.MaterialFunction) -> None:
    base = _fn_input(mf, "BaseColor", -1400, 0, sort=0)
    emissive = _fn_input(mf, "Emissive", -1400, 120, sort=1)
    mtransform = _fn_input(mf, "MagicalTransform", -1400, 240, sort=2)
    motif_mask = _fn_input(mf, "MotifMask", -1400, 360, sort=3)
    motif_scale = _fn_input(mf, "MotifScale", -1400, 480, sort=4)
    motif_color = _fn_input(mf, "MotifColor", -1400, 600, sort=5)
    transform_glow = _fn_input(mf, "TransformGlow", -1400, 720, sort=6)
    wipe_soft = _fn_input(mf, "WipeSoftness", -1400, 840, sort=7)
    magical_palette = _fn_input(mf, "MagicalPalette", -1400, 960, sort=8)
    uv = _fn_input(mf, "UV", -1400, 1080, sort=9)

    wp = lib.create_expression(mf, unreal.MaterialExpressionWorldPosition, -1100, 780)
    mg_z = lib.create_expression(mf, unreal.MaterialExpressionComponentMask, -940, 780)
    mg_z.set_editor_property("r", False)
    mg_z.set_editor_property("g", False)
    mg_z.set_editor_property("b", True)
    mg_z.set_editor_property("a", False)
    lib.connect(wp, "", mg_z, "")
    z_scale = lib.create_expression(mf, unreal.MaterialExpressionConstant, -1100, 880)
    z_scale.set_editor_property("r", 0.004)
    mg_zs = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -780, 780)
    lib.connect(mg_z, "", mg_zs, "A")
    lib.connect(z_scale, "", mg_zs, "B")
    mg_sub = lib.create_expression(mf, unreal.MaterialExpressionSubtract, -620, 760)
    lib.connect(mtransform, "", mg_sub, "A")
    lib.connect(mg_zs, "", mg_sub, "B")
    mg_div = lib.create_expression(mf, unreal.MaterialExpressionDivide, -460, 760)
    lib.connect(mg_sub, "", mg_div, "A")
    lib.connect(wipe_soft, "", mg_div, "B")
    mg_wipe = lib.create_expression(mf, unreal.MaterialExpressionSaturate, -300, 760)
    lib.connect(mg_div, "", mg_wipe, "Input", "")

    mg_uv = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -780, 980)
    lib.connect(uv, "", mg_uv, "A")
    lib.connect(motif_scale, "", mg_uv, "B")
    mg_s = lib.create_expression(mf, unreal.MaterialExpressionTextureSample, -620, 980)
    lib.connect(motif_mask, "Texture", mg_s, "Texture")
    lib.connect(mg_uv, "", mg_s, "UVs")
    mg_sr = lib.create_expression(mf, unreal.MaterialExpressionComponentMask, -460, 980)
    mg_sr.set_editor_property("r", True)
    mg_sr.set_editor_property("g", False)
    mg_sr.set_editor_property("b", False)
    mg_sr.set_editor_property("a", False)
    lib.connect(mg_s, "", mg_sr, "")

    mg_rev1 = lib.create_expression(mf, unreal.MaterialExpressionMultiply, -140, 860)
    lib.connect(mg_wipe, "", mg_rev1, "A")
    lib.connect(mg_sr, "", mg_rev1, "B")
    mg_rev = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 20, 860)
    lib.connect(mg_rev1, "", mg_rev, "A")
    lib.connect(mtransform, "", mg_rev, "B")
    mg_ec = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 180, 860)
    lib.connect(mg_rev, "", mg_ec, "A")
    lib.connect(motif_color, "", mg_ec, "B")
    mg_emis = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 340, 860)
    lib.connect(mg_ec, "", mg_emis, "A")
    lib.connect(transform_glow, "", mg_emis, "B")

    half = lib.create_expression(mf, unreal.MaterialExpressionConstant, -140, 560)
    half.set_editor_property("r", 0.5)
    mg_pal_amt = lib.create_expression(mf, unreal.MaterialExpressionMultiply, 20, 480)
    lib.connect(mtransform, "", mg_pal_amt, "A")
    lib.connect(half, "", mg_pal_amt, "B")
    color_out = lib.create_expression(mf, unreal.MaterialExpressionLinearInterpolate, 180, 480)
    lib.connect(base, "", color_out, "A")
    lib.connect(magical_palette, "", color_out, "B")
    lib.connect(mg_pal_amt, "", color_out, "Alpha")

    emis_out = lib.create_expression(mf, unreal.MaterialExpressionAdd, 500, 200)
    lib.connect(emissive, "", emis_out, "A")
    lib.connect(mg_emis, "", emis_out, "B")

    _add_function_output(mf, color_out, "Color", 680, 480)
    _add_function_output(mf, emis_out, "Emissive", 680, 200)


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
    "MF_AnimeSkinWrap": _build_anime_skin_wrap,
    "MF_ParallaxCore": _build_parallax_core,
    "MF_NormalAdjust": _build_normal_adjust,
    "MF_WaterDepthColor": _build_water_depth_color,
    "MF_WaterShorelineFade": _build_water_shoreline_fade,
    "MF_WaterFoam": _build_water_foam,
    "MF_LandscapeHeightCompete": _build_landscape_height_compete,
    "MF_NikkiDreamGrade": _build_nikki_dream_grade,
    "MF_NikkiRimGlow": _build_nikki_rim_glow,
    "MF_NikkiSparkle": _build_nikki_sparkle,
    "MF_NikkiIridescenceSheen": _build_nikki_iridescence_sheen,
    "MF_MacroDetail": _build_macro_detail,
    "MF_Magical": _build_magical,
    "MF_LayerHeightCompete": _build_layer_height_compete,
    "MF_LayerBlendAdvanced": _build_layer_blend_advanced,
    "MF_ShadowDreamGrade": _build_shadow_dream_grade,
    "MF_ShadowFlowerProject": _build_shadow_flower_project,
    "MF_AudioBeatModulator": _build_audio_beat_modulator,
}


def build_all(*, force: bool = False) -> list[str]:
    unreal.log("=== Building material function library ===")
    created: list[str] = []
    for name, _desc in MF_SPECS:
        try:
            builder = BUILDERS[name]
            mf = _create_or_rebuild_mf(name, force=force)
            exprs = []
            try:
                exprs = list(unreal.MaterialEditingLibrary.get_function_expressions(mf) or [])
            except Exception:
                pass
            if force or not exprs:
                builder(mf)
                try:
                    unreal.MaterialEditingLibrary.recompile_material_function(mf)
                except Exception:
                    pass
                lib.save_package(mf)
            path = lib.asset_path(lib.FUNCTION_DIR, name)
            created.append(path)
            unreal.log(f"[MF] built {path}")
        except Exception as exc:
            unreal.log_warning(f"[MF] skip {name}: {exc}")
    return created


def main() -> int:
    force = "--force" in sys.argv
    paths = build_all(force=force)
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
