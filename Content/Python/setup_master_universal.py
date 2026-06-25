"""Build M_Master_Toon_Universal — the 'reach for every scene' master.

Hybrid texture/procedural, dual texture layers (A/B) with per-layer maps and parallax,
temporal boil/smear UV stylization, triplanar, Nikki dreamy glow, celestial ramps,
curvature gold leaf, fairy-dust highlight motifs, dreamy shadow tinting,
shadow-garden flowers, and metallic ORM blend — all defaulting to neutral (0).

Run (editor open):
  py "G:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_master_universal.py"
  py "G:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_master_universal.py" --force

Then instances:
  py "G:/EnvironmentPortfolio/BS_GodFile/Content/Python/apply_starter_instances.py"

Parameter groups (Material Editor):
  Textures | LayerA/B | Triplanar | Temporal | Nikki | Celestial | Gilding
  ShadowDream | FlowerShadow | FairyDust | Magical | Character | Elemental | Cinematic
"""
from __future__ import annotations

import os
import sys

import unreal
import material_lib as lib

MASTER_NAME = "M_Master_Toon_Universal"
WAT = "/Engine/Functions/Engine_MaterialFunctions02/Texturing/WorldAlignedTexture"
WAN = "/Engine/Functions/Engine_MaterialFunctions02/Texturing/WorldAlignedNormal"
MF_SKIN_WRAP = f"{lib.FUNCTION_DIR}/MF_AnimeSkinWrap"
MF_SPACE_PARALLAX = f"{lib.FUNCTION_DIR}/MF_SpaceParallax"
MF_PARALLAX_CORE = f"{lib.FUNCTION_DIR}/MF_ParallaxCore"
MF_NORMAL_ADJUST = f"{lib.FUNCTION_DIR}/MF_NormalAdjust"
MF_NIKKI_DREAM = f"{lib.FUNCTION_DIR}/MF_NikkiDreamGrade"
MF_NIKKI_RIM = f"{lib.FUNCTION_DIR}/MF_NikkiRimGlow"
MF_NIKKI_SPARKLE = f"{lib.FUNCTION_DIR}/MF_NikkiSparkle"
MF_NIKKI_IRID = f"{lib.FUNCTION_DIR}/MF_NikkiIridescenceSheen"
MF_MACRO_DETAIL = f"{lib.FUNCTION_DIR}/MF_MacroDetail"
MF_MAGICAL = f"{lib.FUNCTION_DIR}/MF_Magical"
MF_LAYER_HEIGHT = f"{lib.FUNCTION_DIR}/MF_LayerHeightCompete"
MF_LAYER_BLEND = f"{lib.FUNCTION_DIR}/MF_LayerBlendAdvanced"
MF_SHADOW_DREAM = f"{lib.FUNCTION_DIR}/MF_ShadowDreamGrade"
MF_SHADOW_FLOWER = f"{lib.FUNCTION_DIR}/MF_ShadowFlowerProject"
MF_AUDIO_BLEND = f"{lib.FUNCTION_DIR}/MF_AudioReactiveBlend"
MF_AUDIO_BEAT = f"{lib.FUNCTION_DIR}/MF_AudioBeatModulator"
MPC_MAGICAL = "/Game/EnvSandbox/VFX/MPC/MPC_Magical"
MPC_AUDIO = f"{lib.MPC_DIR}/MPC_Portfolio_Audio"
MPC_PALETTE = f"{lib.MPC_DIR}/MPC_Portfolio_Palette"
MPC_SAKURA = "/Game/EnvSandbox/VFX/MPC/MPC_SakuraDream"

# Material Instance editor parameter groups (keep in sync with starter_instances key_params)
GROUP_PALETTE = "Palette"
GROUP_HYBRID = "Hybrid"
GROUP_UV = "UV"
GROUP_SURFACE = "Surface"
GROUP_TRIPLANAR = "Triplanar"
GROUP_LAYER_A = "LayerA"
GROUP_LAYER_B = "LayerB"
GROUP_LAYERS = "Layers"
GROUP_PARALLAX = "Parallax"
GROUP_TEMPORAL = "Temporal"
GROUP_NIKKI = "Nikki"
GROUP_CELESTIAL = "Celestial"
GROUP_GILDING = "Gilding"
GROUP_SHADOW_DREAM = "ShadowDream"
GROUP_SHADOW_GARDEN = "ShadowGarden"
GROUP_FAIRY_DUST = "FairyDust"
GROUP_MACRO_DETAIL = "MacroDetail"
GROUP_MAGICAL = "Magical"
GROUP_CHARACTER = "Character"
GROUP_ELEMENTAL = "Elemental"
GROUP_TIME_OF_DAY = "TimeOfDay"
GROUP_WORLD = "World"
GROUP_CINEMATIC = "Cinematic"
GROUP_AUDIO = "Audio"
GROUP_TEXTURES = "Textures"
GROUP_MADOKA = "Madoka"
GROUP_ITTO = "Itto"

PARAM_GROUPS = {
    "nikki": GROUP_NIKKI,
    "flower_shadow": (GROUP_SHADOW_GARDEN, GROUP_SHADOW_DREAM),
    "nebula": GROUP_CELESTIAL,
    "magic": (GROUP_MAGICAL, GROUP_FAIRY_DUST),
}

WIRES: dict[str, bool] = {}


def wire(tag, from_e, to_e, *pins) -> bool:
    if from_e is None or to_e is None:
        WIRES[tag] = False
        return False
    if not pins or pins in (("Input",), ("Input", ""), ("input",), ("input", "")):
        ok = lib.connect_unary(from_e, to_e)
    else:
        ok = lib.connect_any(from_e, to_e, pins)
    WIRES[tag] = ok
    return ok


def const1(m, x, y, val: float = 1.0):
    c = lib.create_expression(m, unreal.MaterialExpressionConstant, x, y)
    c.set_editor_property("r", val)
    return c


def tex_object(m, name, x, y, group: str = "Textures"):
    e = lib.create_expression(m, unreal.MaterialExpressionTextureObjectParameter, x, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("group", group)
    _wire_catalog_texture(e, name)
    return e


def _wire_catalog_texture(expr, param_name: str) -> None:
    import portfolio_texture_catalog as catalog

    candidates = catalog.MASTER_TEXTURE_DEFAULTS.get(param_name)
    if candidates:
        lib.set_expression_texture(expr, candidates)


def mf_call(m, path, x, y):
    if not unreal.EditorAssetLibrary.does_asset_exist(path):
        return None
    c = lib.create_expression(m, unreal.MaterialExpressionMaterialFunctionCall, x, y)
    c.set_editor_property("material_function", unreal.load_asset(path))
    return c


def static_switch(m, name, group, x, y, default=False):
    sw = lib.create_expression(m, unreal.MaterialExpressionStaticSwitchParameter, x, y)
    sw.set_editor_property("parameter_name", name)
    sw.set_editor_property("group", group)
    sw.set_editor_property("default_value", default)
    return sw


def world_xy(m, x, y):
    """World XY procedural coords as stable float2 (Frac after mask avoids LWC typing)."""
    wp = lib.create_expression(m, unreal.MaterialExpressionWorldPosition, x, y)
    mask = lib.create_expression(m, unreal.MaterialExpressionComponentMask, x + 160, y)
    mask.set_editor_property("r", True)
    mask.set_editor_property("g", True)
    mask.set_editor_property("b", False)
    mask.set_editor_property("a", False)
    lib.connect_unary(wp, mask)
    scl = lib.create_expression(m, unreal.MaterialExpressionMultiply, x + 320, y)
    lib.connect(mask, "", scl, "A")
    tiny = lib.create_expression(m, unreal.MaterialExpressionConstant, x + 160, y + 100)
    tiny.set_editor_property("r", 0.0025)
    lib.connect(tiny, "", scl, "B")
    stable = lib.create_expression(m, unreal.MaterialExpressionFrac, x + 480, y)
    lib.connect_unary(scl, stable)
    return stable


def style_peak(m, style, target: float, tag: str, x, y):
    """Weight ~1 when style scalar equals target, ~0 elsewhere."""
    tgt = const1(m, x, y, target)
    sub = lib.create_expression(m, unreal.MaterialExpressionSubtract, x + 120, y)
    wire(f"{tag}_subA", style, sub, "A")
    wire(f"{tag}_subB", tgt, sub, "B")
    ab = lib.create_expression(m, unreal.MaterialExpressionAbs, x + 260, y)
    WIRES[f"{tag}_abs"] = lib.connect_unary(sub, ab)
    scale = const1(m, x + 120, y + 80, 2.0)
    sc = lib.create_expression(m, unreal.MaterialExpressionMultiply, x + 400, y)
    wire(f"{tag}_scA", ab, sc, "A")
    wire(f"{tag}_scB", scale, sc, "B")
    inv = lib.create_expression(m, unreal.MaterialExpressionOneMinus, x + 540, y)
    WIRES[f"{tag}_inv"] = lib.connect_unary(sc, inv)
    return inv


def scalar_switch(m, name, group, x, y, default=False):
    return static_switch(m, name, group, x, y, default)


def apply_temporal_uv(m, uv, temporal_str, wind, noise_scale, smear, boil, tag: str):
    """UV-space boil/smear offset (strength 0 = passthrough). Uses TC, not world pos (avoids LWC/float2 mix)."""
    tc_noise = lib.create_expression(m, unreal.MaterialExpressionTextureCoordinate, -2400, 6200)
    t = lib.create_expression(m, unreal.MaterialExpressionTime, -2400, 6320)
    wind_t = lib.create_expression(m, unreal.MaterialExpressionMultiply, -2240, 6320)
    wire(f"{tag}_wtA", t, wind_t, "A")
    wire(f"{tag}_wtB", wind, wind_t, "B")
    nscale = lib.create_expression(m, unreal.MaterialExpressionMultiply, -2240, 6200)
    wire(f"{tag}_nsA", tc_noise, nscale, "A")
    wire(f"{tag}_nsB", noise_scale, nscale, "B")
    phase = lib.create_expression(m, unreal.MaterialExpressionAdd, -2080, 6260)
    wire(f"{tag}_phA", nscale, phase, "A")
    wire(f"{tag}_phB", wind_t, phase, "B")
    phase_x = lib.create_expression(m, unreal.MaterialExpressionComponentMask, -1920, 6260)
    phase_x.set_editor_property("r", True)
    phase_x.set_editor_property("g", False)
    phase_x.set_editor_property("b", False)
    phase_x.set_editor_property("a", False)
    wire(f"{tag}_phx", phase, phase_x, "")
    s = lib.create_expression(m, unreal.MaterialExpressionSine, -1760, 6260)
    s.set_editor_property("period", 1.0)
    wire(f"{tag}_sin", phase_x, s, "Input")
    boil_off = lib.create_expression(m, unreal.MaterialExpressionMultiply, -1600, 6260)
    wire(f"{tag}_boilA", s, boil_off, "A")
    wire(f"{tag}_boilB", boil, boil_off, "B")
    boil_uv = lib.create_expression(m, unreal.MaterialExpressionAdd, -1600, 6220)
    wire(f"{tag}_buvA", uv, boil_uv, "A")
    wire(f"{tag}_buvB", boil_off, boil_uv, "B")
    c = lib.create_expression(m, unreal.MaterialExpressionConstant, -1920, 6380)
    c.set_editor_property("r", 0.017)
    smear_off = lib.create_expression(m, unreal.MaterialExpressionMultiply, -1760, 6380)
    wire(f"{tag}_smA", s, smear_off, "A")
    wire(f"{tag}_smB", smear, smear_off, "B")
    smear_mul = lib.create_expression(m, unreal.MaterialExpressionMultiply, -1600, 6380)
    wire(f"{tag}_smM", c, smear_mul, "A")
    wire(f"{tag}_smO", smear_off, smear_mul, "B")
    smear_uv = lib.create_expression(m, unreal.MaterialExpressionAdd, -1440, 6300)
    wire(f"{tag}_suvA", boil_uv, smear_uv, "A")
    wire(f"{tag}_suvB", smear_mul, smear_uv, "B")
    out = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, -1280, 6240)
    wire(f"{tag}_outA", uv, out, "A")
    wire(f"{tag}_outB", smear_uv, out, "B")
    wire(f"{tag}_out_alpha", temporal_str, out, "Alpha")
    return out


def parallax_uv_offset(
    m, uv, height_tex, scale, layer_scale, strength, steps, mode, height_mul, tag: str, y_base: int = 6600,
):
    """MF_ParallaxCore — height parallax UV offset (modes 0/1/2)."""
    call = mf_call(m, MF_PARALLAX_CORE, -2400, y_base)
    if not call:
        unreal.log_warning(f"[Universal] MF_ParallaxCore missing — {tag} passthrough UV")
        return uv
    wire(f"{tag}_px_uv", uv, call, "UV")
    wire(f"{tag}_px_ht", height_tex, call, "HeightTexture", "Height")
    wire(f"{tag}_px_sc", scale, call, "ParallaxScale")
    wire(f"{tag}_px_lsc", layer_scale, call, "LayerParallaxScale")
    wire(f"{tag}_px_str", strength, call, "ParallaxStrength")
    wire(f"{tag}_px_h", height_mul, call, "ParallaxHeight")
    wire(f"{tag}_px_st", steps, call, "ParallaxSteps")
    wire(f"{tag}_px_md", mode, call, "ParallaxMode")
    return call


def adjust_normal_map(m, nrm_sample, n_str, n_pow, layer_str, tag: str, y: int):
    """MF_NormalAdjust — strength, power, per-layer scale on sampled normal."""
    call = mf_call(m, MF_NORMAL_ADJUST, -1280, y)
    if not call:
        return nrm_sample
    wire(f"{tag}_n_in", nrm_sample, call, "Normal")
    wire(f"{tag}_n_str", n_str, call, "NormalStrength")
    wire(f"{tag}_n_pow", n_pow, call, "NormalPower")
    wire(f"{tag}_n_lay", layer_str, call, "LayerNormalStrength")
    return call


def sample_maps_uv(
    m, uv, albedo, normal, orm, tri_tiling, tag: str, y0: int,
):
    """UV-path texture samples + triplanar switch."""
    alb_s = lib.create_expression(m, unreal.MaterialExpressionTextureSample, -1420, y0)
    wire(f"{tag}_alb_obj", albedo, alb_s, "Tex", "TextureObject")
    wire(f"{tag}_alb_uv", uv, alb_s, "UVs", "Coordinates")
    nrm_s = lib.create_expression(m, unreal.MaterialExpressionTextureSample, -1420, y0 + 160)
    wire(f"{tag}_nrm_obj", normal, nrm_s, "Tex", "TextureObject")
    wire(f"{tag}_nrm_uv", uv, nrm_s, "UVs", "Coordinates")
    orm_s = lib.create_expression(m, unreal.MaterialExpressionTextureSample, -1420, y0 + 320)
    wire(f"{tag}_orm_obj", orm, orm_s, "Tex", "TextureObject")
    wire(f"{tag}_orm_uv", uv, orm_s, "UVs", "Coordinates")

    waT = mf_call(m, WAT, -1240, y0)
    waN = mf_call(m, WAN, -1240, y0 + 160)
    waR = mf_call(m, WAT, -1240, y0 + 320)
    for ttag, fn, tobj in (
        (f"{tag}_triA", waT, albedo),
        (f"{tag}_triN", waN, normal),
        (f"{tag}_triR", waR, orm),
    ):
        if fn:
            wire(f"{ttag}_obj", tobj, fn, "TextureObject (T2d)", "TextureObject", "Tex")
            wire(f"{ttag}_size", tri_tiling, fn, "Texture Size", "WorldSize", "Size")

    def tri_sw(tt, uv_e, tri_e, yy):
        sw = static_switch(m, "bTriplanar", "Triplanar", -1060, yy)
        WIRES[f"{tt}_sw"] = lib.connect_static_switch(sw, tri_e or uv_e, uv_e)
        return sw

    alb = tri_sw(f"{tag}_swA", alb_s, waT, y0)
    nrm = tri_sw(f"{tag}_swN", nrm_s, waN, y0 + 160)
    orm_out = tri_sw(f"{tag}_swR", orm_s, waR, y0 + 320)
    return alb, nrm, orm_out


def lerp3(m, a, b, alpha, tag: str, x: int, y: int):
    n = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, x, y)
    wire(f"{tag}_A", a, n, "A")
    wire(f"{tag}_B", b, n, "B")
    wire(f"{tag}_alpha", alpha, n, "Alpha")
    return n


def sample_height_r(m, height_tex, uv_expr, tag: str, x: int, y: int):
    """Sample height map R channel at UV."""
    s = lib.create_expression(m, unreal.MaterialExpressionTextureSample, x, y)
    wire(f"{tag}_ht", height_tex, s, "Tex", "TextureObject")
    wire(f"{tag}_uv", uv_expr, s, "UVs", "Coordinates")
    r = lib.create_expression(m, unreal.MaterialExpressionComponentMask, x + 160, y)
    r.set_editor_property("r", True)
    r.set_editor_property("g", False)
    r.set_editor_property("b", False)
    r.set_editor_property("a", False)
    wire(f"{tag}_sr", s, r, "")
    return r


def const3(m, x, y, r: float, g: float, b: float):
    c = lib.create_expression(m, unreal.MaterialExpressionConstant3Vector, x, y)
    c.set_editor_property("constant", unreal.LinearColor(r, g, b, 1.0))
    return c


def mask_channel(m, expr, channel: str, tag: str, x: int, y: int):
    """Extract one channel from float2/float3 for scalar world-XY stylization."""
    mask = lib.create_expression(m, unreal.MaterialExpressionComponentMask, x, y)
    mask.set_editor_property("r", channel in ("r", "x"))
    mask.set_editor_property("g", channel in ("g", "y"))
    mask.set_editor_property("b", channel in ("b", "z"))
    mask.set_editor_property("a", False)
    wire(f"{tag}_m", expr, mask, "")
    return mask


def concavity_mask(m, curve_abs, sens, tag: str, x: int, y: int):
    """High in cavities — inverse of convex curvature magnitude."""
    sc = lib.create_expression(m, unreal.MaterialExpressionMultiply, x, y)
    wire(f"{tag}_scA", curve_abs, sc, "A")
    wire(f"{tag}_scB", sens, sc, "B")
    inv = lib.create_expression(m, unreal.MaterialExpressionOneMinus, x + 140, y)
    wire(f"{tag}_inv", sc, inv, "Input")
    sat = lib.create_expression(m, unreal.MaterialExpressionSaturate, x + 280, y)
    wire(f"{tag}_sat", inv, sat, "Input")
    return sat


def _clear_material_graph(material) -> None:
    try:
        exprs = unreal.MaterialEditingLibrary.get_material_expressions(material)
        for expr in list(exprs or []):
            unreal.MaterialEditingLibrary.delete_material_expression(material, expr)
    except Exception as exc:
        unreal.log_warning(f"[Universal] clear graph: {exc}")


def build():
    lib.ensure_directory(lib.MASTER_DIR)
    path = lib.asset_path(lib.MASTER_DIR, MASTER_NAME)
    exists = unreal.EditorAssetLibrary.does_asset_exist(path)
    force = any("force" in str(a).lower() for a in sys.argv) or os.environ.get(
        "BS_MASTER_FORCE", ""
    ).strip().lower() in ("1", "true", "yes")
    if exists and not force:
        unreal.log_warning(
            f"[Universal] {path} exists — skipping rebuild. "
            "Delete in Content Browser or run with --force."
        )
        try:
            import setup_universal_instances as inst
            inst.build_instances()
        except Exception as exc:
            unreal.log_warning(f"[Universal] instances: {exc}")
        return path

    m = None
    if exists and force:
        m = unreal.load_asset(path)
        if m:
            _clear_material_graph(m)
            unreal.log(f"[Universal] rebuilding in-place {path}")
    if not m:
        at = unreal.AssetToolsHelpers.get_asset_tools()
        m = at.create_asset(MASTER_NAME, lib.MASTER_DIR, unreal.Material, unreal.MaterialFactoryNew())
    if not m:
        raise RuntimeError("create_asset failed — close material tabs and retry")

    if force:
        try:
            import setup_material_functions as mf_setup

            mf_setup.build_all(force=True)
        except Exception as exc:
            unreal.log_warning(f"[Universal] MF library force rebuild: {exc}")
    elif not unreal.EditorAssetLibrary.does_asset_exist(f"{lib.FUNCTION_DIR}/MF_SpaceParallax"):
        try:
            import setup_material_functions as mf_setup

            mf_setup.build_all(force=False)
        except Exception as exc:
            unreal.log_warning(f"[Universal] MF library: {exc}")
    for _mf in (
        "MF_ParallaxCore", "MF_NormalAdjust", "MF_NikkiDreamGrade", "MF_MacroDetail", "MF_Magical",
        "MF_LayerHeightCompete", "MF_LayerBlendAdvanced", "MF_ShadowDreamGrade", "MF_ShadowFlowerProject",
        "MF_AudioReactiveBlend", "MF_AudioBeatModulator",
    ):
        if not unreal.EditorAssetLibrary.does_asset_exist(f"{lib.FUNCTION_DIR}/{_mf}"):
            try:
                import setup_material_functions as mf_setup

                mf_setup.build_all(force=False)
                break
            except Exception as exc:
                unreal.log_warning(f"[Universal] MF parallax/normal: {exc}")
                break

    m.set_editor_property("material_domain", unreal.MaterialDomain.MD_SURFACE)
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_OPAQUE)
    lib.try_set_editor_property(m, "bUsesSubstrate", True)

    # ---- core parameters ----
    base_tint = lib.vector_param(m, "BaseTint", "Palette", (0.60, 0.55, 0.50, 1.0), -2100, -220)
    tex_weight = lib.scalar_param(m, "TextureWeight", "Hybrid", 1.0, -2100, -100)
    uv_scale = lib.scalar_param(m, "UVScale", "UV", 1.0, -2100, 20)
    roughness_s = lib.scalar_param(m, "Roughness", "Surface", 0.70, -2100, 140)
    metallic_s = lib.scalar_param(m, "Metallic", "Surface", 0.0, -2100, 240)
    tri_tiling = lib.scalar_param(m, "TriplanarTiling", "Triplanar", 256.0, -2100, 340)

    # ---- Layer A (primary) texture set ----
    albedo = tex_object(m, "Albedo", -2100, 480, "LayerA")
    normal = tex_object(m, "NormalMap", -2100, 640, "LayerA")
    orm = tex_object(m, "ORM", -2100, 800, "LayerA")
    height_a = tex_object(m, "HeightMap", -2100, 960, "LayerA")
    layer_a_weight = lib.scalar_param(m, "LayerA_TextureWeight", "LayerA", 1.0, -2100, 1080)
    layer_a_parallax = lib.scalar_param(m, "LayerA_ParallaxScale", "LayerA", 1.0, -2100, 1180)
    layer_a_nrm_str = lib.scalar_param(m, "LayerA_NormalStrength", "LayerA", 1.0, -2100, 1230)

    # ---- Layer B (overlay) texture set ----
    alb_b = tex_object(m, "LayerB_Albedo", -2100, 1280, "LayerB")
    nrm_b = tex_object(m, "LayerB_NormalMap", -2100, 1440, "LayerB")
    orm_b = tex_object(m, "LayerB_ORM", -2100, 1600, "LayerB")
    height_b = tex_object(m, "LayerB_HeightMap", -2100, 1760, "LayerB")
    layer_b_weight = lib.scalar_param(m, "LayerB_TextureWeight", "LayerB", 1.0, -2100, 1880)
    layer_b_parallax = lib.scalar_param(m, "LayerB_ParallaxScale", "LayerB", 1.0, -2100, 1980)
    layer_b_nrm_str = lib.scalar_param(m, "LayerB_NormalStrength", "LayerB", 1.0, -2100, 2030)
    layer_blend = lib.scalar_param(m, "LayerBlend", "Layers", 0.0, -2100, 2100)
    layer_blend_mode = lib.scalar_param(
        m, "LayerBlendMode", "Layers", 0.0, -2100, 2140,
        desc="0=manual LayerBlend 1=height compete 2=height+manual mix",
    )
    layer_height_bias = lib.scalar_param(m, "LayerHeightBias", "Layers", 0.0, -2100, 2180)
    layer_height_sharp = lib.scalar_param(m, "LayerHeightSharpness", "Layers", 4.0, -2100, 2220)
    layer_blend_soft = lib.scalar_param(m, "LayerBlendSoftness", "Layers", 0.0, -2100, 2260)
    layer_normal_blend = lib.scalar_param(m, "LayerNormalBlend", "Layers", 1.0, -2100, 2300)
    layer_rough_blend = lib.scalar_param(m, "LayerRoughnessBlend", "Layers", 1.0, -2100, 2340)
    layer_manual_mix = lib.scalar_param(
        m, "LayerManualMix", "Layers", 0.5, -2100, 2380,
        desc="Manual vs height alpha when LayerBlendMode=2",
    )

    # ---- Parallax (shared + per-layer) ----
    parallax_scale = lib.scalar_param(m, "ParallaxScale", "Parallax", 0.04, -2100, 2320)
    parallax_str = lib.scalar_param(m, "ParallaxStrength", "Parallax", 0.0, -2100, 2420)
    parallax_steps = lib.scalar_param(
        m, "ParallaxSteps", "Parallax", 8.0, -2100, 2520,
        desc="POM step count (mode 2; MF_ParallaxCore)",
    )
    parallax_mode = lib.scalar_param(
        m, "ParallaxMode", "Parallax", 0.0, -2100, 2550,
        desc="0=simple offset 1=steep 2=stepped POM (MF_ParallaxCore)",
    )
    parallax_height = lib.scalar_param(
        m, "ParallaxHeight", "Parallax", 1.0, -2100, 2580,
        desc="Height multiplier — MI compat alias for depth scale",
    )
    normal_strength = lib.scalar_param(
        m, "NormalStrength", "Parallax", 1.0, -2100, 2610,
        desc="Global normal map XY amplitude (MF_NormalAdjust)",
    )
    normal_power = lib.scalar_param(
        m, "NormalPower", "Parallax", 1.0, -2100, 2640,
        desc="Normal Z flatten/power before renormalize (MF_NormalAdjust)",
    )

    # ---- Temporal stylization ----
    temporal_str = lib.scalar_param(m, "TemporalStrength", "Temporal", 0.0, -2100, 2740)
    wind_speed = lib.scalar_param(m, "WindSpeed", "Temporal", 0.12, -2100, 2840)
    temporal_noise = lib.scalar_param(m, "NoiseScale", "Temporal", 1.5, -2100, 2940)
    smear_str = lib.scalar_param(m, "SmearStrength", "Temporal", 0.08, -2100, 3040)
    boil_int = lib.scalar_param(m, "BoilIntensity", "Temporal", 0.05, -2100, 3140)

    # ---- Audio reactivity (MPC_Portfolio_Audio) ----
    audio_reactivity = lib.scalar_param(m, "AudioReactivity", GROUP_AUDIO, 0.0, -2100, 3240)
    audio_bass_w = lib.scalar_param(m, "BassWeight", GROUP_AUDIO, 1.0, -2100, 3340)
    audio_mid_w = lib.scalar_param(m, "MidWeight", GROUP_AUDIO, 0.5, -2100, 3440)
    audio_treble_w = lib.scalar_param(m, "TrebleWeight", GROUP_AUDIO, 0.25, -2100, 3540)
    audio_emis_pulse = lib.scalar_param(m, "AudioEmissiveStrength", GROUP_AUDIO, 0.0, -2100, 3640)
    audio_rough_pulse = lib.scalar_param(m, "AudioRoughnessPulse", GROUP_AUDIO, 0.0, -2100, 3740)
    audio_layer_pulse = lib.scalar_param(m, "AudioLayerBlendPulse", GROUP_AUDIO, 0.0, -2100, 3840)
    audio_temporal_pulse = lib.scalar_param(m, "AudioTemporalPulse", GROUP_AUDIO, 0.0, -2100, 3940)
    beat_phase_str = lib.scalar_param(m, "BeatPhaseStrength", GROUP_AUDIO, 0.0, -2100, 4040)
    b_beat_layer_wipe = static_switch(m, "bBeatLayerWipe", GROUP_AUDIO, -2100, 4140, default=False)
    mpc_audio_global = lib.collection_scalar(m, MPC_AUDIO, "GlobalReactivity", -1900, 3240)
    mpc_audio_bass = lib.collection_scalar(m, MPC_AUDIO, "Bass", -1900, 3340)
    mpc_audio_mid = lib.collection_scalar(m, MPC_AUDIO, "Mid", -1900, 3440)
    mpc_audio_treble = lib.collection_scalar(m, MPC_AUDIO, "Treble", -1900, 3540)
    mpc_audio_beat = lib.collection_scalar(m, MPC_AUDIO, "BeatPhase", -1900, 4040)

    # ---- UV + temporal ----
    tc = lib.create_expression(m, unreal.MaterialExpressionTextureCoordinate, -1800, 460)
    uv = lib.create_expression(m, unreal.MaterialExpressionMultiply, -1620, 460)
    wire("uv_tc", tc, uv, "A")
    wire("uv_scale", uv_scale, uv, "B")
    uv_time = apply_temporal_uv(
        m, uv, temporal_str, wind_speed, temporal_noise, smear_str, boil_int, "temporal"
    )

    # Parallax per layer (MF_ParallaxCore + strength gate)
    pom_a = parallax_uv_offset(
        m, uv_time, height_a, parallax_scale, layer_a_parallax, parallax_str,
        parallax_steps, parallax_mode, parallax_height, "pomA", 6600,
    )
    pom_b = parallax_uv_offset(
        m, uv_time, height_b, parallax_scale, layer_b_parallax, parallax_str,
        parallax_steps, parallax_mode, parallax_height, "pomB", 7000,
    )
    uv_a = lerp3(m, uv_time, pom_a, parallax_str, "uv_pomA", -1480, 480)
    uv_b = lerp3(m, uv_time, pom_b, parallax_str, "uv_pomB", -1480, 1280)

    alb_a, nrm_a, orm_a = sample_maps_uv(m, uv_a, albedo, normal, orm, tri_tiling, "layA", 480)
    alb_b_s, nrm_b_s, orm_b_s = sample_maps_uv(m, uv_b, alb_b, nrm_b, orm_b, tri_tiling, "layB", 1280)
    nrm_a = adjust_normal_map(m, nrm_a, normal_strength, normal_power, layer_a_nrm_str, "nrmAdjA", 480)
    nrm_b_s = adjust_normal_map(m, nrm_b_s, normal_strength, normal_power, layer_b_nrm_str, "nrmAdjB", 1280)

    h_a_r = sample_height_r(m, height_a, uv_a, "hgtA", -900, 480)
    h_b_r = sample_height_r(m, height_b, uv_b, "hgtB", -900, 1280)
    height_alpha = layer_blend
    compete_mf = mf_call(m, MF_LAYER_HEIGHT, -720, 880)
    if compete_mf:
        wire("comp_hA", h_a_r, compete_mf, "HeightA")
        wire("comp_hB", h_b_r, compete_mf, "HeightB")
        wire("comp_bias", layer_height_bias, compete_mf, "BlendBias")
        wire("comp_sharp", layer_height_sharp, compete_mf, "BlendSharpness")
        height_alpha = compete_mf
    mode_half = const1(m, -520, 720, 0.5)
    mode_onehalf = const1(m, -520, 820, 1.5)
    mode_two = const1(m, -520, 920, 2.0)
    height_sub = lib.create_expression(m, unreal.MaterialExpressionSubtract, -360, 720)
    wire("hsubA", layer_blend_mode, height_sub, "A")
    wire("hsubB", mode_half, height_sub, "B")
    height_gate = lib.create_expression(m, unreal.MaterialExpressionSaturate, -200, 720)
    wire("hg_in", height_sub, height_gate, "Input")
    height_gate_raw = lib.create_expression(m, unreal.MaterialExpressionMultiply, -40, 720)
    wire("hg2A", height_gate, height_gate_raw, "A")
    wire("hg2B", mode_two, height_gate_raw, "B")
    height_gate2 = lib.create_expression(m, unreal.MaterialExpressionSaturate, 120, 720)
    wire("hg2_sat", height_gate_raw, height_gate2, "Input")
    mix_sub = lib.create_expression(m, unreal.MaterialExpressionSubtract, -360, 880)
    wire("msubA", layer_blend_mode, mix_sub, "A")
    wire("msubB", mode_onehalf, mix_sub, "B")
    mix_gate = lib.create_expression(m, unreal.MaterialExpressionSaturate, -200, 880)
    wire("mg_in", mix_sub, mix_gate, "Input")
    mix_gate_raw = lib.create_expression(m, unreal.MaterialExpressionMultiply, -40, 880)
    wire("mg2A", mix_gate, mix_gate_raw, "A")
    wire("mg2B", mode_two, mix_gate_raw, "B")
    mix_gate2 = lib.create_expression(m, unreal.MaterialExpressionSaturate, 120, 880)
    wire("mg2_sat", mix_gate_raw, mix_gate2, "Input")
    manual_h_mix = lerp3(m, layer_blend, height_alpha, layer_manual_mix, "mh_mix", -360, 1000)
    blend_sel = lerp3(m, layer_blend, height_alpha, height_gate2, "blend_sel", 160, 760)
    blend_alpha = lerp3(m, blend_sel, manual_h_mix, mix_gate2, "blend_alpha", 360, 880)

    audio_react_mf = mf_call(m, MF_AUDIO_BLEND, 560, 1040)
    audio_react = const1(m, 560, 1140, 0.0)
    if audio_react_mf:
        wire("aud_glob", mpc_audio_global, audio_react_mf, "GlobalReactivity")
        wire("aud_bass", mpc_audio_bass, audio_react_mf, "Bass")
        wire("aud_mid", mpc_audio_mid, audio_react_mf, "Mid")
        wire("aud_treb", mpc_audio_treble, audio_react_mf, "Treble")
        wire("aud_react", audio_reactivity, audio_react_mf, "AudioReactivity")
        wire("aud_bw", audio_bass_w, audio_react_mf, "BassWeight")
        wire("aud_mw", audio_mid_w, audio_react_mf, "MidWeight")
        wire("aud_tw", audio_treble_w, audio_react_mf, "TrebleWeight")
        audio_react = audio_react_mf
    beat_mod_mf = mf_call(m, MF_AUDIO_BEAT, 760, 1040)
    beat_mod = const1(m, 760, 1140, 0.0)
    if beat_mod_mf:
        wire("beat_ph", mpc_audio_beat, beat_mod_mf, "BeatPhase")
        wire("beat_str", beat_phase_str, beat_mod_mf, "BeatPhaseStrength")
        beat_mod = beat_mod_mf
    beat_wipe = lib.create_expression(m, unreal.MaterialExpressionFrac, 940, 1040)
    wire("beat_frac", mpc_audio_beat, beat_wipe, "Input")
    WIRES["beat_wipe_sw"] = lib.connect_static_switch(b_beat_layer_wipe, beat_wipe, blend_alpha)
    blend_alpha_base = b_beat_layer_wipe
    audio_layer_add = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1280, 1040)
    wire("alaA", audio_react, audio_layer_add, "A")
    wire("alaB", audio_layer_pulse, audio_layer_add, "B")
    blend_alpha = lib.create_expression(m, unreal.MaterialExpressionAdd, 1460, 1040)
    wire("blaA", blend_alpha_base, blend_alpha, "A")
    wire("blaB", audio_layer_add, blend_alpha, "B")

    tex_a_w = lib.create_expression(m, unreal.MaterialExpressionMultiply, -360, 120)
    wire("tawA", tex_weight, tex_a_w, "A")
    wire("tawB", layer_a_weight, tex_a_w, "B")
    tex_b_w = lib.create_expression(m, unreal.MaterialExpressionMultiply, -360, 240)
    wire("tbwA", tex_weight, tex_b_w, "A")
    wire("tbwB", layer_b_weight, tex_b_w, "B")

    layer_mf = mf_call(m, MF_LAYER_BLEND, -200, 520)
    if layer_mf:
        wire("lay_albA", alb_a, layer_mf, "AlbedoA")
        wire("lay_albB", alb_b_s, layer_mf, "AlbedoB")
        wire("lay_nrmA", nrm_a, layer_mf, "NormalA")
        wire("lay_nrmB", nrm_b_s, layer_mf, "NormalB")
        wire("lay_ormA", orm_a, layer_mf, "OrmA")
        wire("lay_ormB", orm_b_s, layer_mf, "OrmB")
        wire("lay_texA", tex_a_w, layer_mf, "TexEffA")
        wire("lay_texB", tex_b_w, layer_mf, "TexEffB")
        wire("lay_alpha", blend_alpha, layer_mf, "BlendAlpha")
        wire("lay_soft", layer_blend_soft, layer_mf, "BlendSoftness")
        wire("lay_nblend", layer_normal_blend, layer_mf, "NormalBlendStrength")
        wire("lay_rblend", layer_rough_blend, layer_mf, "RoughnessBlendStrength")
        alb = layer_mf
        nrm_s = layer_mf
        orm_s = layer_mf
        tex_eff = layer_mf
    else:
        alb_blend = lerp3(m, alb_a, alb_b_s, blend_alpha, "alb_lerp", -680, 520)
        nrm_blend = lerp3(m, nrm_a, nrm_b_s, blend_alpha, "nrm_lerp", -680, 680)
        orm_blend = lerp3(m, orm_a, orm_b_s, blend_alpha, "orm_lerp", -680, 840)
        alb = alb_blend
        nrm_s = nrm_blend
        orm_s = orm_blend
        tex_eff = lerp3(m, tex_a_w, tex_b_w, blend_alpha, "tex_eff", -200, 180)

    # hybrid base color / roughness / normal / metallic
    color = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, -40, 120)
    wire("color_A", base_tint, color, "A")
    wire("color_B", alb, color, "B")
    wire("color_alpha", tex_eff, color, "Alpha")

    org = lib.create_expression(m, unreal.MaterialExpressionComponentMask, -200, 800)
    org.set_editor_property("r", False)
    org.set_editor_property("g", True)
    org.set_editor_property("b", False)
    org.set_editor_property("a", False)
    lib.connect_unary(orm_s, org)
    rough = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 20, 800)
    wire("rough_A", roughness_s, rough, "A")
    wire("rough_B", org, rough, "B")
    wire("rough_alpha", tex_eff, rough, "Alpha")

    orm_r = lib.create_expression(m, unreal.MaterialExpressionComponentMask, -200, 960)
    orm_r.set_editor_property("r", True)
    orm_r.set_editor_property("g", False)
    orm_r.set_editor_property("b", False)
    orm_r.set_editor_property("a", False)
    lib.connect_unary(orm_s, orm_r)
    metal = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 20, 960)
    wire("metal_A", metallic_s, metal, "A")
    wire("metal_B", orm_r, metal, "B")
    wire("metal_alpha", tex_eff, metal, "Alpha")

    flat_n = lib.create_expression(m, unreal.MaterialExpressionConstant3Vector, -200, 640)
    flat_n.set_editor_property("constant", unreal.LinearColor(0.0, 0.0, 1.0, 1.0))
    nrm = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 20, 640)
    wire("nrm_A", flat_n, nrm, "A")
    wire("nrm_B", nrm_s, nrm, "B")
    wire("nrm_alpha", tex_eff, nrm, "Alpha")

    # temporal color boil (subtle impressionist shimmer on final tint path)
    temp_col = lib.create_expression(m, unreal.MaterialExpressionMultiply, 120, 40)
    wire("tcA", color, temp_col, "A")
    t_mod = lib.create_expression(m, unreal.MaterialExpressionAdd, 0, 120)
    wire("tc_modA", const1(m, -40, 120, 1.0), t_mod, "A")
    wire("tc_modB", temporal_str, t_mod, "B")
    wire("tcB", t_mod, temp_col, "B")
    color = temp_col

    # ---- Nikki dreamy layer (pastel lift, rim, sparkle, bloom) ----
    rim_color = lib.vector_param(
        m, "RimColor", "Nikki", (0.70, 0.85, 1.00, 1.0), -2100, 1040,
        desc="Fresnel rim tint — anime edge glow",
    )
    rim_power = lib.scalar_param(m, "RimPower", "Nikki", 3.0, -2100, 1140, desc="Rim falloff exponent")
    rim_int = lib.scalar_param(m, "RimIntensity", "Nikki", 0.0, -2100, 1240, desc="Rim brightness (0=off)")
    rim_width = lib.scalar_param(
        m, "RimWidth", "Nikki", 1.0, -2100, 1290,
        desc="Rim remap width (1=neutral, higher=tighter)",
    )
    rim_bias = lib.scalar_param(
        m, "RimBias", "Nikki", 0.0, -2100, 1315,
        desc="Rim remap bias (-inward / +outward)",
    )
    rim_clamp = lib.scalar_param(
        m, "RimClamp", "Nikki", 10.0, -2100, 1335,
        desc="Clamp for rim emissive (high=neutral)",
    )
    dream_tint = lib.vector_param(
        m, "DreamTint", "Nikki", (1.00, 0.85, 0.92, 1.0), -2100, 1340,
        desc="Pastel color lift target",
    )
    pastel = lib.scalar_param(m, "PastelLift", "Nikki", 0.0, -2100, 1440, desc="Blend toward DreamTint")
    dream_sat = lib.scalar_param(
        m, "DreamSaturation", "Nikki", 0.0, -2100, 1490,
        desc="Saturation adjustment (0=off)",
    )
    dream_contrast = lib.scalar_param(
        m, "DreamContrast", "Nikki", 0.0, -2100, 1515,
        desc="Contrast adjustment (0=off)",
    )
    dream_shadow_lift = lib.scalar_param(
        m, "DreamShadowLift", "Nikki", 0.0, -2100, 1535,
        desc="Shadow lift (0=off)",
    )
    dream_high_soft = lib.scalar_param(
        m, "DreamHighlightSoft", "Nikki", 0.0, -2100, 1555,
        desc="Highlight softening (0=off)",
    )
    dream_hue = lib.scalar_param(
        m, "DreamHueShift", "Nikki", 0.0, -2100, 1575,
        desc="Hue shift (0=off; subtle)",
    )
    irid = lib.scalar_param(m, "Iridescence", "Nikki", 0.0, -2100, 1540, desc="View-dependent rainbow sheen")
    irid_tint = lib.vector_param(m, "IridescenceTint", "Nikki", (0.80, 0.60, 1.00, 1.0), -2100, 1640)
    irid_pow = lib.scalar_param(
        m, "IridescencePower", "Nikki", 1.0, -2100, 1680,
        desc="Iridescence mask exponent (1=neutral)",
    )
    irid_bias = lib.scalar_param(
        m, "IridescenceBias", "Nikki", 0.0, -2100, 1700,
        desc="Iridescence mask bias (0=neutral)",
    )
    irid_rough_atten = lib.scalar_param(
        m, "IridescenceRoughnessAtten", "Nikki", 0.0, -2100, 1720,
        desc="Reduce iridescence on rough surfaces (0=off)",
    )
    spark_mask = lib.texture_param(
        m, "SparkleMask", "Nikki", -2100, 1740,
        desc="Alpha sparkles / bokeh (T_Spark_*)",
    )
    _wire_catalog_texture(spark_mask, "SparkleMask")
    spark_scale = lib.scalar_param(m, "SparkleScale", "Nikki", 8.0, -2100, 1840)
    spark_int = lib.scalar_param(m, "SparkleIntensity", "Nikki", 0.0, -2100, 1940)
    spark_color = lib.vector_param(m, "SparkleColor", "Nikki", (1.00, 0.95, 0.80, 1.0), -2100, 2040)
    spark_thresh = lib.scalar_param(
        m, "SparkleThreshold", "Nikki", 0.0, -2100, 2080,
        desc="Mask cutoff (0=off)",
    )
    spark_contrast = lib.scalar_param(
        m, "SparkleContrast", "Nikki", 0.0, -2100, 2100,
        desc="Tighten sparkle mask (0=off)",
    )
    spark_drift = lib.scalar_param(
        m, "SparkleDriftSpeed", "Nikki", 0.0, -2100, 2120,
        desc="UV drift speed (0=off)",
    )
    spark_twinkle = lib.scalar_param(
        m, "SparkleTwinkleSpeed", "Nikki", 0.0, -2100, 2140,
        desc="Twinkle speed (0=off)",
    )
    spark_noise = lib.scalar_param(
        m, "SparkleNoiseScale", "Nikki", 0.0, -2100, 2160,
        desc="Procedural breakup scale (0=off)",
    )
    spark_col_lo = lib.vector_param(
        m, "SparkleColorLow", "Nikki", (1.00, 1.00, 1.00, 1.0), -2100, 2180,
        desc="Optional sparkle gradient low (default neutral)",
    )
    spark_col_hi = lib.vector_param(
        m, "SparkleColorHigh", "Nikki", (1.00, 1.00, 1.00, 1.0), -2100, 2200,
        desc="Optional sparkle gradient high (default neutral)",
    )
    spark_col_lerp = lib.scalar_param(
        m, "SparkleColorLerp", "Nikki", 0.0, -2100, 2220,
        desc="Blend sparkle gradient (0=off)",
    )
    glow_color = lib.vector_param(m, "GlowColor", "Nikki", (1.00, 0.90, 0.95, 1.0), -2100, 2140)
    glow_int = lib.scalar_param(m, "GlowIntensity", "Nikki", 0.0, -2100, 2240)
    rim_soft = lib.scalar_param(m, "RimSoftness", "Nikki", 0.35, -2100, 2340)
    inner_glow = lib.scalar_param(m, "InnerGlowIntensity", "Nikki", 0.0, -2100, 2440)
    inner_width = lib.scalar_param(
        m, "InnerGlowWidth", "Nikki", 1.0, -2100, 2490,
        desc="Inner glow falloff width (1=neutral)",
    )
    inner_color = lib.vector_param(m, "InnerGlowColor", "Nikki", (1.00, 0.92, 0.98, 1.0), -2100, 2540)
    bloom = lib.scalar_param(m, "BloomBoost", "Nikki", 0.0, -2100, 2640, desc="Extra emissive for post bloom")
    sheen = lib.scalar_param(m, "FabricSheen", "Nikki", 0.0, -2100, 2740)
    sheen_tint = lib.vector_param(m, "SheenTint", "Nikki", (1.00, 1.00, 1.00, 1.0), -2100, 2840)
    sheen_power = lib.scalar_param(m, "SheenPower", "Nikki", 6.0, -2100, 2940)
    sheen_width = lib.scalar_param(
        m, "SheenWidth", "Nikki", 1.0, -2100, 2990,
        desc="Sheen remap width (1=neutral)",
    )
    sheen_bias = lib.scalar_param(
        m, "SheenBias", "Nikki", 0.0, -2100, 3010,
        desc="Sheen remap bias (0=neutral)",
    )
    nikki_fast = static_switch(m, "bNikkiFast", "Nikki", -2100, 3040, default=True)
    nikki_hero = static_switch(m, "bNikkiHero", "Nikki", -2100, 3080, default=False)
    sparkle_adv = static_switch(m, "bSparkleAdvanced", "Nikki", -2100, 3120, default=False)
    sheen_use_normal = static_switch(m, "bSheenUsesNormal", "Nikki", -2100, 3160, default=False)

    # ---- Madoka (Ethereal / witch barrier) ----
    madoka_glow = lib.scalar_param(m, "MadokaGlowAmount", "Madoka", 0.0, -2100, 3260)
    madoka_radial_bands = lib.scalar_param(m, "MadokaRadialBands", "Madoka", 3.0, -2100, 3360)
    madoka_radial_speed = lib.scalar_param(m, "MadokaRadialSpeed", "Madoka", 0.0, -2100, 3460)
    madoka_emissive_bright = lib.scalar_param(m, "MadokaEmissiveBrightness", "Madoka", 0.0, -2100, 3560)
    madoka_cute_bias = lib.scalar_param(m, "MadokaCuteBias", "Madoka", 0.5, -2100, 3660)
    madoka_vein_emissive = lib.scalar_param(m, "MadokaVeinEmissive", "Madoka", 0.0, -2100, 3760)
    witch_wallpaper_scale = lib.scalar_param(m, "WitchBarrierWallpaperScale", "Madoka", 4.0, -2100, 3860)
    witch_maze_tightness = lib.scalar_param(m, "WitchBarrierMazeTightness", "Madoka", 0.5, -2100, 3960)
    witch_phase_speed = lib.scalar_param(m, "WitchBarrierPhaseSpeed", "Madoka", 0.45, -2100, 4060)

    # ---- Itto (Heavy / mythic / carved) ----
    itto_pattern_scale = lib.scalar_param(m, "IttoPatternScale", "Itto", 3.0, -2100, 4160)
    itto_crack_depth = lib.scalar_param(m, "IttoCrackDepth", "Itto", 0.0, -2100, 4260)
    itto_wear_amount = lib.scalar_param(m, "IttoWearAmount", "Itto", 0.0, -2100, 4360)
    itto_breakup = lib.scalar_param(m, "IttoBreakupAmount", "Itto", 0.0, -2100, 4460)
    itto_erosion = lib.scalar_param(m, "IttoErosionStrength", "Itto", 0.0, -2100, 4560)
    itto_wear_depth = lib.scalar_param(m, "IttoWearDepth", "Itto", 0.0, -2100, 4660)
    itto_ink = lib.scalar_param(m, "IttoInkStrength", "Itto", 0.0, -2100, 4760)

    # ---- Celestial / nebula (MF_SpaceParallax: parallax stars + toon-banded nebula + galaxy) ----
    const_low = lib.vector_param(m, "ConstellationRampLow", "Celestial", (0.02, 0.03, 0.10, 1.0), -2100, 3060)
    const_mid = lib.vector_param(m, "ConstellationRampMid", "Celestial", (0.45, 0.22, 0.55, 1.0), -2100, 3160)
    const_high = lib.vector_param(m, "ConstellationRampHigh", "Celestial", (0.85, 0.72, 1.00, 1.0), -2100, 3260)
    const_str = lib.scalar_param(m, "ConstellationStrength", "Celestial", 0.0, -2100, 3360)
    const_scale = lib.scalar_param(m, "ConstellationScale", "Celestial", 1.8, -2100, 3460)
    const_phase = lib.scalar_param(
        m, "ConstellationPhase", "Celestial", 0.0, -2100, 3560,
        desc="Legacy — replaced by MF_SpaceParallax (no graph wiring)",
    )
    star_int = lib.scalar_param(m, "CelestialStarIntensity", "Celestial", 1.0, -2100, 3660)
    star_twinkle = lib.scalar_param(
        m, "CelestialTwinkle", "Celestial", 0.0, -2100, 3760,
        desc="Legacy — replaced by MF_SpaceParallax (no graph wiring)",
    )
    nebula_str = lib.scalar_param(
        m, "CelestialNebulaStrength", "Celestial", 0.65, -2100, 3860,
        desc="Soft nebula cloud wash strength",
    )
    nebula_scale = lib.scalar_param(
        m, "CelestialNebulaScale", "Celestial", 0.35, -2100, 3960,
        desc="Nebula parallax depth (MF_SpaceParallax NebulaDepth)",
    )
    galaxy_str = lib.scalar_param(m, "CelestialGalaxyStrength", "Celestial", 0.45, -2100, 4060)
    galaxy_scale = lib.scalar_param(
        m, "CelestialGalaxyScale", "Celestial", 0.12, -2100, 4160,
        desc="Galaxy parallax depth (MF_SpaceParallax GalaxyDepth)",
    )
    galaxy_arms = lib.scalar_param(
        m, "CelestialGalaxyArms", "Celestial", 3.0, -2100, 4260,
        desc="Legacy — replaced by MF_SpaceParallax (no graph wiring)",
    )
    star_map = tex_object(m, "StarMap", -2100, 4310, "Celestial")
    _wire_catalog_texture(star_map, "StarMap")
    toon_steps = lib.scalar_param(
        m, "CelestialToonSteps", "Celestial", 4.0, -2100, 4410,
        desc="Nebula toon cel-band count (MF_SpaceParallax ToonSteps)",
    )

    # ---- Gold leaf on curvature ----
    gild_str = lib.scalar_param(m, "GildingStrength", "Gilding", 0.0, -2100, 4380)
    gold_tint = lib.vector_param(m, "GoldTint", "Gilding", (0.92, 0.72, 0.28, 1.0), -2100, 4480)
    gold_rough = lib.scalar_param(m, "GoldRoughness", "Gilding", 0.18, -2100, 4580)
    gold_emis = lib.vector_param(m, "GoldEmissive", "Gilding", (0.35, 0.25, 0.05, 1.0), -2100, 4680)
    curve_sens = lib.scalar_param(m, "CurvatureSensitivity", "Gilding", 2.5, -2100, 4780)

    # ---- Dreamy shadows (MF_ShadowDreamGrade) ----
    shadow_tint = lib.vector_param(m, "ShadowDreamTint", "ShadowDream", (0.48, 0.42, 0.62, 1.0), -2100, 4900)
    shadow_str = lib.scalar_param(m, "ShadowDreamStrength", "ShadowDream", 0.0, -2100, 5000)
    shadow_soft = lib.scalar_param(m, "ShadowSoftness", "ShadowDream", 0.5, -2100, 5100)
    shadow_dream_hue = lib.scalar_param(m, "ShadowDreamHueShift", "ShadowDream", 0.0, -2100, 5150)
    shadow_dream_sat = lib.scalar_param(m, "ShadowDreamSaturation", "ShadowDream", 0.0, -2100, 5200)
    shadow_contact_boost = lib.scalar_param(m, "ShadowContactBoost", "ShadowDream", 0.0, -2100, 5250)
    shadow_ambient_mix = lib.scalar_param(m, "ShadowDreamAmbientMix", "ShadowDream", 0.0, -2100, 5300)
    shadow_ambient_col = lib.vector_param(
        m, "ShadowDreamAmbientColor", "ShadowDream", (0.55, 0.48, 0.72, 1.0), -2100, 5400,
    )
    b_shadow_scene_light = static_switch(
        m, "bShadowUseSceneLight", "ShadowDream", -2100, 5500, default=False,
    )
    mpc_shadow_bias = lib.collection_scalar(m, MPC_PALETTE, "ShadowDreamBias", -1900, 5000)
    mpc_sakura_pulse = lib.collection_scalar(m, MPC_SAKURA, "SparklePulse", -1900, 5100)
    # ---- Flower shadow garden (MF_ShadowFlowerProject) ----
    flower_str = lib.scalar_param(
        m, "ShadowFlowerStrength", "FlowerShadow", 0.0, -2100, 5620,
        desc="Petal shadow projection intensity",
    )
    flower_scale = lib.scalar_param(
        m, "ShadowFlowerScale", "FlowerShadow", 5.0, -2100, 5720,
        desc="World-space petal repeat scale",
    )
    flower_scale_fine = lib.scalar_param(m, "ShadowFlowerScaleFine", "FlowerShadow", 12.0, -2100, 5820)
    flower_rotation = lib.scalar_param(m, "ShadowFlowerRotation", "FlowerShadow", 0.35, -2100, 5920)
    flower_jitter = lib.scalar_param(m, "ShadowFlowerJitter", "FlowerShadow", 0.25, -2100, 6020)
    flower_softness = lib.scalar_param(m, "ShadowFlowerSoftness", "FlowerShadow", 0.4, -2100, 6120)
    flower_albedo_dark = lib.scalar_param(m, "ShadowFlowerAlbedoDarken", "FlowerShadow", 0.35, -2100, 6220)
    flower_pulse_str = lib.scalar_param(m, "ShadowFlowerPulseStrength", "FlowerShadow", 0.0, -2100, 6320)
    flower_mask = tex_object(m, "ShadowFlowerMask", -2100, 6420, "FlowerShadow")
    _wire_catalog_texture(flower_mask, "FairyGlyphMask")
    flower_color = lib.vector_param(
        m, "ShadowFlowerColor", "FlowerShadow", (0.92, 0.45, 0.72, 1.0), -2100, 6520,
        desc="Tint of projected flower shadows",
    )

    # ---- Fairy dust motifs (0=off, 1=heart, 2=star, 3=flower, 4=moon) ----
    fairy_style = lib.scalar_param(m, "FairyMotifStyle", "FairyDust", 0.0, -2100, 5540)
    fairy_int = lib.scalar_param(m, "FairyDustIntensity", "FairyDust", 0.0, -2100, 5640)
    fairy_scale = lib.scalar_param(m, "FairyDustScale", "FairyDust", 14.0, -2100, 5740)
    fairy_color = lib.vector_param(m, "FairyDustColor", "FairyDust", (1.0, 0.92, 0.98, 1.0), -2100, 5840)
    fairy_thresh = lib.scalar_param(m, "FairyHighlightThreshold", "FairyDust", 0.35, -2100, 5940)
    fairy_glyph = lib.texture_param(m, "FairyGlyphMask", "FairyDust", -2100, 6040)
    _wire_catalog_texture(fairy_glyph, "FairyGlyphMask")

    # ---- Nikki dreamy layer via MF stack (parity with landscape) ----
    nikki_plain = color
    nikki_col = nikki_plain
    dream_mf = mf_call(m, MF_NIKKI_DREAM, 220, 120)
    if dream_mf:
        wire("nikki_dream_bc", nikki_plain, dream_mf, "BaseColor")
        wire("nikki_dream_pastel", pastel, dream_mf, "PastelLift")
        wire("nikki_dream_tint", dream_tint, dream_mf, "DreamTint")
        wire("nikki_dream_sat", dream_sat, dream_mf, "DreamSaturation")
        wire("nikki_dream_con", dream_contrast, dream_mf, "DreamContrast")
        wire("nikki_dream_sh", dream_shadow_lift, dream_mf, "DreamShadowLift")
        nikki_col = dream_mf
    rim_mf = mf_call(m, MF_NIKKI_RIM, 420, 120)
    if rim_mf:
        wire("nikki_rim_bc", nikki_col, rim_mf, "BaseColor")
        wire("nikki_rim_n", nrm, rim_mf, "Normal")
        wire("nikki_rim_col", rim_color, rim_mf, "RimColor")
        wire("nikki_rim_int", rim_int, rim_mf, "RimIntensity")
        wire("nikki_rim_w", rim_width, rim_mf, "RimWidth")
        wire("nikki_rim_glow", glow_int, rim_mf, "GlowIntensity")
        wire("nikki_rim_bloom", bloom, rim_mf, "BloomBoost")
        nikki_col = rim_mf
    nikki_fast_col = nikki_col
    sparkle_mf = mf_call(m, MF_NIKKI_SPARKLE, 620, 120)
    if sparkle_mf:
        wire("nikki_spark_bc", nikki_col, sparkle_mf, "BaseColor")
        wire("nikki_spark_uv", uv, sparkle_mf, "UV")
        wire("nikki_spark_mask", spark_mask, sparkle_mf, "SparkleMask", "Texture")
        wire("nikki_spark_int", spark_int, sparkle_mf, "SparkleIntensity")
        wire("nikki_spark_thr", spark_thresh, sparkle_mf, "SparkleThreshold")
        wire("nikki_spark_col", spark_color, sparkle_mf, "SparkleColor")
        nikki_col = sparkle_mf
    irid_mf = mf_call(m, MF_NIKKI_IRID, 820, 120)
    if irid_mf:
        wire("nikki_irid_bc", nikki_col, irid_mf, "BaseColor")
        wire("nikki_irid_n", nrm, irid_mf, "Normal")
        wire("nikki_irid_amt", irid, irid_mf, "Iridescence")
        wire("nikki_irid_tint", irid_tint, irid_mf, "IridescenceTint")
        wire("nikki_irid_pow", irid_pow, irid_mf, "IridescencePower")
        wire("nikki_irid_sheen", sheen, irid_mf, "FabricSheen")
        wire("nikki_irid_sheen_t", sheen_tint, irid_mf, "SheenTint")
        nikki_col = irid_mf
    nikki_hero_col = nikki_col
    WIRES["nikki_fast_sw"] = lib.connect_static_switch(nikki_fast, nikki_fast_col, nikki_plain)
    WIRES["nikki_hero_sw"] = lib.connect_static_switch(nikki_hero, nikki_hero_col, nikki_fast)
    color_nikki = nikki_hero

    # ---- celestial: MF_SpaceParallax ----
    space_px = mf_call(m, MF_SPACE_PARALLAX, 400, 300)
    if not space_px:
        unreal.log_error("[Universal] MF_SpaceParallax missing — celestial stack skipped")
        celestial = color_nikki
    else:
        wire("spx_galaxy_tint", const_low, space_px, "GalaxyTint")
        wire("spx_nebula_tint", const_mid, space_px, "NebulaTint")
        wire("spx_star_tint", const_high, space_px, "StarTint")
        wire("spx_nebula_str", nebula_str, space_px, "NebulaStrength")
        wire("spx_galaxy_str", galaxy_str, space_px, "GalaxyStrength")
        wire("spx_nebula_depth", nebula_scale, space_px, "NebulaDepth")
        wire("spx_galaxy_depth", galaxy_scale, space_px, "GalaxyDepth")
        wire("spx_star_depth", const_scale, space_px, "StarDepth")
        wire("spx_toon_steps", toon_steps, space_px, "ToonSteps")
        wire("spx_star_map", star_map, space_px, "StarMap", "Texture")
        star_str_mul = lib.create_expression(m, unreal.MaterialExpressionMultiply, 200, 420)
        wire("spx_star_strA", star_int, star_str_mul, "A")
        wire("spx_star_strB", const_str, star_str_mul, "B")
        wire("spx_star_str", star_str_mul, space_px, "StarStrength")
        celestial = space_px
    color_stars = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 1780, 120)
    wire("stars_A", color_nikki, color_stars, "A")
    wire("stars_B", celestial, color_stars, "B")
    wire("stars_alpha", const_str, color_stars, "Alpha")

    # ---- Madoka graph: witch barrier voronoi + veins + emissive ----
    madoka_wxy = world_xy(m, 2200, 300)
    madoka_voronoi = lib.create_expression(m, unreal.MaterialExpressionNoise, 2200, 400)
    wire("madoka_vor_wxy", madoka_wxy, madoka_voronoi, "Position", "")
    madoka_vor_scale = lib.create_expression(m, unreal.MaterialExpressionMultiply, 2200, 500)
    wire("madoka_vor_scaleA", madoka_voronoi, madoka_vor_scale, "A")
    wire("madoka_vor_scaleB", witch_wallpaper_scale, madoka_vor_scale, "B")
    madoka_vor_sat = lib.create_expression(m, unreal.MaterialExpressionSaturate, 2200, 600)
    wire("madoka_vor_sat", madoka_vor_scale, madoka_vor_sat, "Input")
    madoka_veins = lib.create_edge_detect_scalar(m, madoka_vor_sat, 2200, 700, "madoka_veins")
    madoka_vein_mask = lib.create_expression(m, unreal.MaterialExpressionMultiply, 2200, 800)
    wire("madoka_vein_maskA", madoka_veins, madoka_vein_mask, "A")
    wire("madoka_vein_maskB", madoka_vein_emissive, madoka_vein_mask, "B")
    madoka_vein_glow = lib.create_expression(m, unreal.MaterialExpressionMultiply, 2200, 900)
    wire("madoka_vein_glowA", madoka_vein_mask, madoka_vein_glow, "A")
    madoka_glow_tint = lib.create_expression(m, unreal.MaterialExpressionConstant3Vector, 2200, 1000)
    madoka_glow_tint.set_editor_property("constant", unreal.LinearColor(0.6, 0.3, 0.8, 1.0))
    wire("madoka_glow_tintB", madoka_glow_tint, madoka_vein_glow, "B")
    madoka_glow_scaled = lib.create_expression(m, unreal.MaterialExpressionMultiply, 2200, 1100)
    wire("madoka_glow_scaledA", madoka_vein_glow, madoka_glow_scaled, "A")
    wire("madoka_glow_scaledB", madoka_glow, madoka_glow_scaled, "B")
    madoka_emi_base = const1(m, 2200, 1150, 0.0)
    madoka_emissive_add = lib.create_expression(m, unreal.MaterialExpressionAdd, 2200, 1200)
    wire("madoka_emi_addA", madoka_emi_base, madoka_emissive_add, "A")
    wire("madoka_emi_addB", madoka_glow_scaled, madoka_emissive_add, "B")
    madoka_color_blend = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 2200, 1300)
    wire("madoka_cA", color_stars, madoka_color_blend, "A")
    wire("madoka_cB", madoka_glow_tint, madoka_color_blend, "B")
    wire("madoka_cAlpha", madoka_glow, madoka_color_blend, "Alpha")
    color_stars = madoka_color_blend

    # ---- Madoka: cute/corrupt + radial rings + SSS glow extension ----
    madoka_cute = lib.create_expression(m, unreal.MaterialExpressionConstant3Vector, 2200, 1900)
    madoka_cute.set_editor_property("constant", unreal.LinearColor(0.92, 0.55, 0.88, 1.0))
    madoka_corrupt = lib.create_expression(m, unreal.MaterialExpressionConstant3Vector, 2200, 2000)
    madoka_corrupt.set_editor_property("constant", unreal.LinearColor(0.55, 0.12, 0.18, 1.0))
    madoka_color_mix = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 2200, 2100)
    wire("mk_cA", madoka_cute, madoka_color_mix, "A")
    wire("mk_cB", madoka_corrupt, madoka_color_mix, "B")
    wire("mk_cAlpha", madoka_cute_bias, madoka_color_mix, "Alpha")

    madoka_radial_c = lib.create_expression(m, unreal.MaterialExpressionConstant2Vector, 2200, 2200)
    madoka_radial_c.set_editor_property("r", 0.5)
    madoka_radial_c.set_editor_property("g", 0.5)
    madoka_dist = lib.create_expression(m, unreal.MaterialExpressionDistance, 2200, 2300)
    wire("mk_distA", madoka_wxy, madoka_dist, "A")
    wire("mk_distB", madoka_radial_c, madoka_dist, "B")
    madoka_dist_scaled = lib.create_expression(m, unreal.MaterialExpressionMultiply, 2200, 2400)
    wire("mk_dist_sA", madoka_dist, madoka_dist_scaled, "A")
    wire("mk_dist_sB", madoka_radial_bands, madoka_dist_scaled, "B")
    madoka_rings_sin = lib.create_expression(m, unreal.MaterialExpressionSine, 2200, 2500)
    madoka_rings_sin.set_editor_property("period", 1.0)
    wire("mk_rings_sin", madoka_dist_scaled, madoka_rings_sin, "Input")
    madoka_rings_abs = lib.create_expression(m, unreal.MaterialExpressionAbs, 2200, 2600)
    wire("mk_rings_abs", madoka_rings_sin, madoka_rings_abs, "Input")
    madoka_rings_radial = lib.create_expression(m, unreal.MaterialExpressionMultiply, 2200, 2700)
    wire("mk_rings_A", madoka_rings_abs, madoka_rings_radial, "A")
    wire("mk_rings_B", madoka_glow, madoka_rings_radial, "B")
    madoka_rings_add = lib.create_expression(m, unreal.MaterialExpressionAdd, 2200, 2800)
    wire("mk_rings_addA", madoka_color_mix, madoka_rings_add, "A")
    wire("mk_rings_addB", madoka_rings_radial, madoka_rings_add, "B")
    madoka_color_final = madoka_rings_add

    madoka_blur = lib.create_blur(m, madoka_color_final, 2200, 2900, sigma=8.0, tag="madoka")
    madoka_glow_add = lib.create_expression(m, unreal.MaterialExpressionAdd, 2200, 3000)
    wire("mk_glowA", madoka_glow_scaled, madoka_glow_add, "A")
    wire("mk_glowB", madoka_blur, madoka_glow_add, "B")
    madoka_glow_final = lib.create_expression(m, unreal.MaterialExpressionMultiply, 2200, 3100)
    wire("mk_gfA", madoka_glow_add, madoka_glow_final, "A")
    wire("mk_gfB", madoka_glow, madoka_glow_final, "B")

    madoka_emissive_extend = lib.create_expression(m, unreal.MaterialExpressionAdd, 2200, 3200)
    wire("mk_emiA", madoka_emissive_add, madoka_emissive_extend, "A")
    wire("mk_emiB", madoka_glow_final, madoka_emissive_extend, "B")

    madoka_final_blend = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 2200, 3300)
    wire("mk_fA", color_stars, madoka_final_blend, "A")
    wire("mk_fB", madoka_color_final, madoka_final_blend, "B")
    wire("mk_fAlpha", madoka_glow, madoka_final_blend, "Alpha")
    color_stars = madoka_final_blend

    # curvature gold leaf
    pnormal = lib.create_expression(m, unreal.MaterialExpressionPixelNormalWS, 220, 520)
    ddx = lib.create_expression(m, unreal.MaterialExpressionDDX, 400, 460)
    ddy = lib.create_expression(m, unreal.MaterialExpressionDDY, 400, 580)
    wire("ddx_n", pnormal, ddx, "Input")
    wire("ddy_n", pnormal, ddy, "Input")
    curve_sum = lib.create_expression(m, unreal.MaterialExpressionAdd, 560, 520)
    wire("curve_A", ddx, curve_sum, "A")
    wire("curve_B", ddy, curve_sum, "B")
    curve_abs = lib.create_expression(m, unreal.MaterialExpressionAbs, 720, 520)
    wire("curve_abs", curve_sum, curve_abs, "Input")
    curve_mul = lib.create_expression(m, unreal.MaterialExpressionMultiply, 880, 520)
    wire("curve_mulA", curve_abs, curve_mul, "A")
    wire("curve_mulB", curve_sens, curve_mul, "B")
    gold_mask = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1040, 520)
    wire("gold_maskA", curve_mul, gold_mask, "A")
    wire("gold_maskB", gild_str, gold_mask, "B")
    color_gold = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 1220, 120)
    wire("gold_cA", color_stars, color_gold, "A")
    wire("gold_cB", gold_tint, color_gold, "B")
    wire("gold_c_alpha", gold_mask, color_gold, "Alpha")
    rough_gold = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 1220, 800)
    wire("gold_rA", rough, rough_gold, "A")
    wire("gold_rB", gold_rough, rough_gold, "B")
    wire("gold_r_alpha", gold_mask, rough_gold, "Alpha")
    metal_gold = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 1220, 960)
    wire("gold_mA", metal, metal_gold, "A")
    one_m = const1(m, 1040, 1080, 1.0)
    wire("gold_mB", one_m, metal_gold, "B")
    wire("gold_m_alpha", gold_mask, metal_gold, "Alpha")
    gold_emis_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1220, 640)
    wire("gold_eA", gold_mask, gold_emis_m, "A")
    wire("gold_eB", gold_emis, gold_emis_m, "B")

    # ---- Itto graph: truchet + cracks + wear (after gold leaf so roughness stacks correctly) ----
    itto_wxy = world_xy(m, 2400, 1080)
    itto_truchet = lib.create_expression(m, unreal.MaterialExpressionNoise, 2400, 1180)
    wire("itto_tru_wxy", itto_wxy, itto_truchet, "Position", "")
    itto_tru_scale = lib.create_expression(m, unreal.MaterialExpressionMultiply, 2400, 1280)
    wire("itto_tru_scaleA", itto_truchet, itto_tru_scale, "A")
    wire("itto_tru_scaleB", itto_pattern_scale, itto_tru_scale, "B")
    itto_tru_sat = lib.create_expression(m, unreal.MaterialExpressionSaturate, 2400, 1380)
    wire("itto_tru_sat", itto_tru_scale, itto_tru_sat, "Input")
    itto_cracks = lib.create_edge_detect_scalar(m, itto_tru_sat, 2400, 1480, "itto_cracks")
    itto_crack_mask = lib.create_expression(m, unreal.MaterialExpressionMultiply, 2400, 1580)
    wire("itto_crack_maskA", itto_cracks, itto_crack_mask, "A")
    wire("itto_crack_maskB", itto_crack_depth, itto_crack_mask, "B")
    itto_wear = lib.create_expression(m, unreal.MaterialExpressionMultiply, 2400, 1680)
    wire("itto_wearA", curve_abs, itto_wear, "A")
    wire("itto_wearB", itto_wear_amount, itto_wear, "B")
    itto_surface_blend = lib.create_expression(m, unreal.MaterialExpressionAdd, 2400, 1780)
    wire("itto_surfA", itto_crack_mask, itto_surface_blend, "A")
    wire("itto_surfB", itto_wear, itto_surface_blend, "B")
    itto_surface_scaled = lib.create_expression(m, unreal.MaterialExpressionMultiply, 2400, 1880)
    wire("itto_surf_scaledA", itto_surface_blend, itto_surface_scaled, "A")
    wire("itto_surf_scaledB", itto_breakup, itto_surface_scaled, "B")
    itto_rough_add = lib.create_expression(m, unreal.MaterialExpressionAdd, 2400, 1980)
    wire("itto_roughA", rough_gold, itto_rough_add, "A")
    wire("itto_roughB", itto_surface_scaled, itto_rough_add, "B")
    rough_gold = itto_rough_add
    # Note: IttoInkStrength / IttoErosionStrength / IttoWearDepth reserved for Phase 2 (height + ink)

    # ShadowDream MF (replaces inline N·L tint)
    light_dir_fixed = lib.create_expression(m, unreal.MaterialExpressionConstant3Vector, 220, 760)
    light_dir_fixed.set_editor_property("constant", unreal.LinearColor(0.35, 0.55, 0.85, 1.0))
    light_dir = light_dir_fixed
    shadow_dream_mf = mf_call(m, MF_SHADOW_DREAM, 1420, 120)
    shadow_amt = const1(m, 1420, 220, 0.0)
    final_color = color_gold
    if shadow_dream_mf:
        wire("sd_bc", color_gold, shadow_dream_mf, "BaseColor")
        wire("sd_n", pnormal, shadow_dream_mf, "Normal")
        wire("sd_ld", light_dir, shadow_dream_mf, "LightVector")
        wire("sd_tint", shadow_tint, shadow_dream_mf, "ShadowTint")
        wire("sd_str", shadow_str, shadow_dream_mf, "Strength")
        wire("sd_soft", shadow_soft, shadow_dream_mf, "Softness")
        wire("sd_bias", mpc_shadow_bias, shadow_dream_mf, "Bias")
        wire("sd_contact", shadow_contact_boost, shadow_dream_mf, "ContactBoost")
        wire("sd_cmask", gold_mask, shadow_dream_mf, "ContactMask")
        wire("sd_ambmix", shadow_ambient_mix, shadow_dream_mf, "AmbientMix")
        wire("sd_ambcol", shadow_ambient_col, shadow_dream_mf, "AmbientColor")
        final_color = shadow_dream_mf
        shadow_amt = shadow_dream_mf

    wxy = world_xy(m, 220, 300)
    flower_e = const3(m, 2220, 900, 0.0, 0.0, 0.0)
    flower_darken = const1(m, 1600, 900, 0.0)
    shadow_flower_mf = mf_call(m, MF_SHADOW_FLOWER, 1220, 900)
    if shadow_flower_mf:
        wire("sf_xy", wxy, shadow_flower_mf, "WorldXY")
        wire("sf_mask", flower_mask, shadow_flower_mf, "ShadowMask", "Texture")
        wire("sf_shamt", shadow_amt, shadow_flower_mf, "ShadowAmount")
        wire("sf_scale", flower_scale, shadow_flower_mf, "Scale")
        wire("sf_sfine", flower_scale_fine, shadow_flower_mf, "ScaleFine")
        wire("sf_rot", flower_rotation, shadow_flower_mf, "Rotation")
        wire("sf_jit", flower_jitter, shadow_flower_mf, "Jitter")
        wire("sf_col", flower_color, shadow_flower_mf, "FlowerColor")
        wire("sf_str", flower_str, shadow_flower_mf, "Strength")
        wire("sf_soft", flower_softness, shadow_flower_mf, "Softness")
        wire("sf_dark", flower_albedo_dark, shadow_flower_mf, "AlbedoDarken")
        wire("sf_pulse", mpc_sakura_pulse, shadow_flower_mf, "Pulse")
        wire("sf_pstr", flower_pulse_str, shadow_flower_mf, "PulseStrength")
        flower_e = shadow_flower_mf
        flower_darken = shadow_flower_mf
        fc_pre = final_color
        color_flower_sub = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1600, 120)
        wire("cf_subA", const1(m, 1440, 120, 1.0), color_flower_sub, "A")
        wire("cf_subB", flower_darken, color_flower_sub, "B")
        final_color_mul = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1780, 120)
        wire("fcA", fc_pre, final_color_mul, "A")
        wire("fcB", color_flower_sub, final_color_mul, "B")
        final_color = final_color_mul

    # fresnel + Nikki stack (rim/glow/sparkle grading) — defaults are neutral/off.
    fres = lib.create_expression(m, unreal.MaterialExpressionFresnel, 220, 1100)
    wire("fresnel_exp", rim_power, fres, "ExponentIn")
    fres_sat = lib.create_expression(m, unreal.MaterialExpressionSaturate, 60, 1100)
    wire("fres_sat", fres, fres_sat, "Input")

    # Rim remap: (fres - bias) * width -> saturate -> multiply intensity
    rim_bias_sub = lib.create_expression(m, unreal.MaterialExpressionSubtract, 220, 1180)
    wire("rim_bias_subA", fres_sat, rim_bias_sub, "A")
    wire("rim_bias_subB", rim_bias, rim_bias_sub, "B")
    rim_width_mul = lib.create_expression(m, unreal.MaterialExpressionMultiply, 400, 1180)
    wire("rim_width_mulA", rim_bias_sub, rim_width_mul, "A")
    wire("rim_width_mulB", rim_width, rim_width_mul, "B")
    rim_mask = lib.create_expression(m, unreal.MaterialExpressionSaturate, 580, 1180)
    wire("rim_mask_sat", rim_width_mul, rim_mask, "Input")

    rim_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 740, 1100)
    wire("rim_mA", rim_mask, rim_m, "A")
    wire("rim_mB", rim_int, rim_m, "B")
    rim_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 920, 1100)
    wire("rim_eA", rim_m, rim_e, "A")
    wire("rim_eB", rim_color, rim_e, "B")
    rim_e_clamp = lib.create_expression(m, unreal.MaterialExpressionMin, 1100, 1100)
    wire("rim_clampA", rim_e, rim_e_clamp, "A")
    wire("rim_clampB", rim_clamp, rim_e_clamp, "B")
    rim_e = rim_e_clamp

    # Iridescence mask: rim_mask^(IridescencePower) with bias; atten by roughness if requested
    irid_bias_add = lib.create_expression(m, unreal.MaterialExpressionAdd, 740, 1280)
    wire("irid_biasA", rim_mask, irid_bias_add, "A")
    wire("irid_biasB", irid_bias, irid_bias_add, "B")
    irid_bias_sat = lib.create_expression(m, unreal.MaterialExpressionSaturate, 920, 1280)
    wire("irid_bias_sat", irid_bias_add, irid_bias_sat, "Input")
    irid_pow_node = lib.create_expression(m, unreal.MaterialExpressionPower, 1100, 1280)
    wire("irid_powA", irid_bias_sat, irid_pow_node, "Base")
    wire("irid_powB", irid_pow, irid_pow_node, "Exp")
    rough_mul = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1100, 1440)
    wire("irid_rA", rough, rough_mul, "A")
    wire("irid_rB", irid_rough_atten, rough_mul, "B")
    rough_inv = lib.create_expression(m, unreal.MaterialExpressionOneMinus, 1280, 1440)
    wire("irid_r_inv", rough_mul, rough_inv, "Input")
    irid_mask = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1280, 1280)
    wire("irid_maskA", irid_pow_node, irid_mask, "A")
    wire("irid_maskB", rough_inv, irid_mask, "B")
    irid_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1460, 1280)
    wire("irid_mA", irid_mask, irid_m, "A")
    wire("irid_mB", irid, irid_m, "B")
    irid_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1640, 1280)
    wire("irid_eA", irid_m, irid_e, "A")
    wire("irid_eB", irid_tint, irid_e, "B")

    # Sparkles: base mask with optional drift/twinkle/threshold/contrast (gated)
    t = lib.create_expression(m, unreal.MaterialExpressionTime, 220, 1380)
    drift_mul = lib.create_expression(m, unreal.MaterialExpressionMultiply, 400, 1380)
    wire("spark_driftA", t, drift_mul, "A")
    wire("spark_driftB", spark_drift, drift_mul, "B")
    drift_add = lib.create_expression(m, unreal.MaterialExpressionAdd, 580, 1380)
    wire("spark_drift_addA", drift_mul, drift_add, "A")
    wire("spark_drift_addB", const1(m, 400, 1460, 1.0), drift_add, "B")
    drift_sin = lib.create_expression(m, unreal.MaterialExpressionSine, 740, 1380)
    drift_sin.set_editor_property("period", 1.0)
    wire("spark_drift_sin", drift_add, drift_sin, "Input")
    drift_uv = lib.create_expression(m, unreal.MaterialExpressionMultiply, 920, 1380)
    wire("spark_drift_uvA", drift_sin, drift_uv, "A")
    wire("spark_drift_uvB", const1(m, 740, 1460, 0.015), drift_uv, "B")
    uv_scaled = lib.create_expression(m, unreal.MaterialExpressionMultiply, 220, 1420)
    wire("spark_uvA", uv, uv_scaled, "A")
    wire("spark_uvB", spark_scale, uv_scaled, "B")
    uv_adv = lib.create_expression(m, unreal.MaterialExpressionAdd, 400, 1420)
    wire("spark_uv_advA", uv_scaled, uv_adv, "A")
    wire("spark_uv_advB", drift_uv, uv_adv, "B")
    # gate advanced UV
    spark_uv = lib.create_expression(m, unreal.MaterialExpressionStaticSwitchParameter, 580, 1420)
    spark_uv.set_editor_property("parameter_name", "bSparkleAdvanced")
    spark_uv.set_editor_property("group", "Nikki")
    spark_uv.set_editor_property("default_value", False)
    WIRES["spark_uv_sw"] = lib.connect_static_switch(spark_uv, uv_adv, uv_scaled)

    wire("spark_mask_uv", spark_uv, spark_mask, "UVs", "Coordinates")
    spark_base = spark_mask
    spark_cut = lib.create_expression(m, unreal.MaterialExpressionSubtract, 740, 1420)
    wire("spark_cutA", spark_base, spark_cut, "A")
    wire("spark_cutB", spark_thresh, spark_cut, "B")
    spark_cut_sat = lib.create_expression(m, unreal.MaterialExpressionSaturate, 920, 1420)
    wire("spark_cut_sat", spark_cut, spark_cut_sat, "Input")
    spark_pow = lib.create_expression(m, unreal.MaterialExpressionPower, 1100, 1420)
    wire("spark_powA", spark_cut_sat, spark_pow, "Base")
    wire("spark_powB", const1(m, 920, 1500, 1.0), spark_pow, "Exp")
    # contrast via exponent (1 + contrast*6)
    con_mul = lib.create_expression(m, unreal.MaterialExpressionMultiply, 920, 1540)
    wire("spark_conA", spark_contrast, con_mul, "A")
    wire("spark_conB", const1(m, 740, 1540, 6.0), con_mul, "B")
    con_add = lib.create_expression(m, unreal.MaterialExpressionAdd, 1100, 1540)
    wire("spark_con_addA", const1(m, 920, 1620, 1.0), con_add, "A")
    wire("spark_con_addB", con_mul, con_add, "B")
    spark_pow2 = lib.create_expression(m, unreal.MaterialExpressionPower, 1280, 1420)
    wire("spark_pow2A", spark_pow, spark_pow2, "Base")
    wire("spark_pow2B", con_add, spark_pow2, "Exp")
    # twinkle mod
    tw_mul = lib.create_expression(m, unreal.MaterialExpressionMultiply, 740, 1600)
    wire("spark_twA", t, tw_mul, "A")
    wire("spark_twB", spark_twinkle, tw_mul, "B")
    tw_sin = lib.create_expression(m, unreal.MaterialExpressionSine, 920, 1600)
    tw_sin.set_editor_property("period", 1.0)
    wire("spark_tw_sin", tw_mul, tw_sin, "Input")
    tw_abs = lib.create_expression(m, unreal.MaterialExpressionAbs, 1100, 1600)
    wire("spark_tw_abs", tw_sin, tw_abs, "Input")
    spark_tw = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 1280, 1600)
    wire("spark_twA", const1(m, 1100, 1680, 1.0), spark_tw, "A")
    wire("spark_twB", tw_abs, spark_tw, "B")
    wire("spark_twAlpha", spark_twinkle, spark_tw, "Alpha")
    spark_mask_final = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1460, 1420)
    wire("spark_mask_finalA", spark_pow2, spark_mask_final, "A")
    wire("spark_mask_finalB", spark_tw, spark_mask_final, "B")

    spark_col_grad = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 1640, 1480)
    wire("spark_col_gradA", spark_col_lo, spark_col_grad, "A")
    wire("spark_col_gradB", spark_col_hi, spark_col_grad, "B")
    wire("spark_col_gradAlpha", spark_col_lerp, spark_col_grad, "Alpha")
    spark_col = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1820, 1480)
    wire("spark_colA", spark_color, spark_col, "A")
    wire("spark_colB", spark_col_grad, spark_col, "B")

    spark_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1640, 1420)
    wire("spark_mA", spark_mask_final, spark_m, "A")
    wire("spark_mB", spark_int, spark_m, "B")
    spark_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1820, 1420)
    wire("spark_eA", spark_m, spark_e, "A")
    wire("spark_eB", spark_col, spark_e, "B")

    glow_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 400, 1580)
    wire("glow_eA", glow_color, glow_e, "A")
    wire("glow_eB", glow_int, glow_e, "B")

    # Inner glow uses separate width control (1=neutral)
    inner_inv = lib.create_expression(m, unreal.MaterialExpressionOneMinus, 220, 1280)
    wire("inner_inv", rim_mask, inner_inv, "Input")
    inner_w_mul = lib.create_expression(m, unreal.MaterialExpressionMultiply, 60, 1360)
    wire("inner_wA", inner_inv, inner_w_mul, "A")
    wire("inner_wB", inner_width, inner_w_mul, "B")
    inner_mask = lib.create_expression(m, unreal.MaterialExpressionSaturate, 220, 1360)
    wire("inner_mask_sat", inner_w_mul, inner_mask, "Input")
    inner_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 400, 1360)
    wire("inner_mA", inner_mask, inner_m, "A")
    wire("inner_mB", inner_glow, inner_m, "B")
    inner_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 580, 1360)
    wire("inner_eA", inner_m, inner_e, "A")
    wire("inner_eB", inner_color, inner_e, "B")

    # Sheen remap: fresnel with width/bias; optional normal influence
    sheen_f = lib.create_expression(m, unreal.MaterialExpressionFresnel, 220, 1520)
    wire("sheen_exp", sheen_power, sheen_f, "ExponentIn")
    sheen_sat = lib.create_expression(m, unreal.MaterialExpressionSaturate, 60, 1520)
    wire("sheen_sat", sheen_f, sheen_sat, "Input")
    sheen_bias_sub = lib.create_expression(m, unreal.MaterialExpressionSubtract, 220, 1600)
    wire("sheen_biasA", sheen_sat, sheen_bias_sub, "A")
    wire("sheen_biasB", sheen_bias, sheen_bias_sub, "B")
    sheen_w_mul = lib.create_expression(m, unreal.MaterialExpressionMultiply, 400, 1600)
    wire("sheen_wA", sheen_bias_sub, sheen_w_mul, "A")
    wire("sheen_wB", sheen_width, sheen_w_mul, "B")
    sheen_mask = lib.create_expression(m, unreal.MaterialExpressionSaturate, 580, 1600)
    wire("sheen_mask_sat", sheen_w_mul, sheen_mask, "Input")
    # optional normal influence (cheap): saturate(dot(N, V))
    pn = lib.create_expression(m, unreal.MaterialExpressionPixelNormalWS, 60, 1680)
    cv = lib.create_expression(m, unreal.MaterialExpressionCameraVectorWS, 60, 1760)
    ndv = lib.create_expression(m, unreal.MaterialExpressionDotProduct, 220, 1720)
    wire("sheen_ndvA", pn, ndv, "A")
    wire("sheen_ndvB", cv, ndv, "B")
    ndv_sat = lib.create_expression(m, unreal.MaterialExpressionSaturate, 400, 1720)
    wire("sheen_ndv_sat", ndv, ndv_sat, "Input")
    sheen_mask_n = lib.create_expression(m, unreal.MaterialExpressionMultiply, 580, 1720)
    wire("sheen_mask_nA", sheen_mask, sheen_mask_n, "A")
    wire("sheen_mask_nB", ndv_sat, sheen_mask_n, "B")
    sheen_mask_gated = lib.create_expression(m, unreal.MaterialExpressionStaticSwitchParameter, 740, 1680)
    sheen_mask_gated.set_editor_property("parameter_name", "bSheenUsesNormal")
    sheen_mask_gated.set_editor_property("group", "Nikki")
    sheen_mask_gated.set_editor_property("default_value", False)
    WIRES["sheen_mask_sw"] = lib.connect_static_switch(sheen_mask_gated, sheen_mask_n, sheen_mask)

    sheen_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 920, 1520)
    wire("sheen_mA", sheen_mask_gated, sheen_m, "A")
    wire("sheen_mB", sheen, sheen_m, "B")
    sheen_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 580, 1520)
    wire("sheen_eA", sheen_m, sheen_e, "A")
    wire("sheen_eB", sheen_tint, sheen_e, "B")

    # Inline Nikki emissive only when bNikkiHero (fast MF path owns color glow)
    rim_e_h = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1240, 1100)
    wire("rim_hA", rim_e, rim_e_h, "A")
    wire("rim_hB", nikki_hero, rim_e_h, "B")
    rim_e = rim_e_h
    irid_e_h = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1800, 1280)
    wire("irid_hA", irid_e, irid_e_h, "A")
    wire("irid_hB", nikki_hero, irid_e_h, "B")
    irid_e = irid_e_h
    spark_e_h = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1960, 1420)
    wire("spark_hA", spark_e, spark_e_h, "A")
    wire("spark_hB", nikki_hero, spark_e_h, "B")
    spark_e = spark_e_h
    glow_e_h = lib.create_expression(m, unreal.MaterialExpressionMultiply, 540, 1580)
    wire("glow_hA", glow_e, glow_e_h, "A")
    wire("glow_hB", nikki_hero, glow_e_h, "B")
    glow_e = glow_e_h
    inner_e_h = lib.create_expression(m, unreal.MaterialExpressionMultiply, 720, 1360)
    wire("inner_hA", inner_e, inner_e_h, "A")
    wire("inner_hB", nikki_hero, inner_e_h, "B")
    inner_e = inner_e_h
    sheen_e_h = lib.create_expression(m, unreal.MaterialExpressionMultiply, 720, 1520)
    wire("sheen_hA", sheen_e, sheen_e_h, "A")
    wire("sheen_hB", nikki_hero, sheen_e_h, "B")
    sheen_e = sheen_e_h

    # fairy dust procedural motifs on world UV
    fairy_uv = lib.create_expression(m, unreal.MaterialExpressionMultiply, 220, 1680)
    wire("fairy_uvA", wxy, fairy_uv, "A")
    wire("fairy_uvB", fairy_scale, fairy_uv, "B")
    # heart: pinched radial
    heart_r = lib.create_expression(m, unreal.MaterialExpressionDistance, 400, 1640)
    heart_c = lib.create_expression(m, unreal.MaterialExpressionConstant2Vector, 220, 1780)
    heart_c.set_editor_property("r", 0.5)
    heart_c.set_editor_property("g", 0.42)
    wire("heart_distA", fairy_uv, heart_r, "A")
    wire("heart_distB", heart_c, heart_r, "B")
    heart_inv = lib.create_expression(m, unreal.MaterialExpressionOneMinus, 560, 1640)
    wire("heart_inv", heart_r, heart_inv, "Input")
    # star: high-frequency sine grid
    star_sx = lib.create_expression(m, unreal.MaterialExpressionSine, 400, 1760)
    star_sx.set_editor_property("period", 5.0)
    fairy_fx2 = mask_channel(m, fairy_uv, "r", "fairy_fx2", 220, 1760)
    wire("star_sx", fairy_fx2, star_sx, "Input")
    star_sy = lib.create_expression(m, unreal.MaterialExpressionSine, 400, 1880)
    star_sy.set_editor_property("period", 5.0)
    fairy_fy2 = mask_channel(m, fairy_uv, "g", "fairy_fy2", 220, 1880)
    wire("star_sy", fairy_fy2, star_sy, "Input")
    star_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 560, 1820)
    wire("star_mA", star_sx, star_m, "A")
    wire("star_mB", star_sy, star_m, "B")
    star_abs = lib.create_expression(m, unreal.MaterialExpressionAbs, 720, 1820)
    wire("star_abs", star_m, star_abs, "Input")
    # flower motif for fairy dust (separate from shadow-garden petals)
    fairy_px = lib.create_expression(m, unreal.MaterialExpressionSine, 400, 1960)
    fairy_px.set_editor_property("period", 1.0)
    fairy_fx = mask_channel(m, fairy_uv, "r", "fairy_fx", 220, 1960)
    wire("fairy_px", fairy_fx, fairy_px, "Input")
    fairy_py = lib.create_expression(m, unreal.MaterialExpressionSine, 400, 2080)
    fairy_py.set_editor_property("period", 1.0)
    fairy_fy = mask_channel(m, fairy_uv, "g", "fairy_fy", 220, 2080)
    wire("fairy_py", fairy_fy, fairy_py, "Input")
    flower_motif = lib.create_expression(m, unreal.MaterialExpressionMultiply, 560, 2020)
    wire("fl_mA", fairy_px, flower_motif, "A")
    wire("fl_mB", fairy_py, flower_motif, "B")
    flower_m_abs = lib.create_expression(m, unreal.MaterialExpressionAbs, 720, 1960)
    wire("fl_m_abs", flower_motif, flower_m_abs, "Input")
    # moon: crescent from two radii
    moon_r = lib.create_expression(m, unreal.MaterialExpressionDistance, 400, 2080)
    moon_c = lib.create_expression(m, unreal.MaterialExpressionConstant2Vector, 220, 2180)
    moon_c.set_editor_property("r", 0.45)
    moon_c.set_editor_property("g", 0.5)
    wire("moon_distA", fairy_uv, moon_r, "A")
    wire("moon_distB", moon_c, moon_r, "B")
    moon_sub = lib.create_expression(m, unreal.MaterialExpressionSubtract, 560, 2080)
    wire("moon_subA", const1(m, 400, 2180, 0.35), moon_sub, "A")
    wire("moon_subB", moon_r, moon_sub, "B")
    moon_clamp = lib.create_expression(m, unreal.MaterialExpressionSaturate, 720, 2080)
    wire("moon_sat", moon_sub, moon_clamp, "Input")

    w_heart = style_peak(m, fairy_style, 1.0, "wh", 860, 1640)
    w_star = style_peak(m, fairy_style, 2.0, "ws", 860, 1760)
    w_flower = style_peak(m, fairy_style, 3.0, "wf", 860, 1880)
    w_moon = style_peak(m, fairy_style, 4.0, "wm", 860, 2000)
    m_h = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1040, 1640)
    wire("m_hA", heart_inv, m_h, "A")
    wire("m_hB", w_heart, m_h, "B")
    m_s = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1040, 1760)
    wire("m_sA", star_abs, m_s, "A")
    wire("m_sB", w_star, m_s, "B")
    m_f = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1040, 1880)
    wire("m_fA", flower_m_abs, m_f, "A")
    wire("m_fB", w_flower, m_f, "B")
    m_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1040, 2000)
    wire("m_mA", moon_clamp, m_m, "A")
    wire("m_mB", w_moon, m_m, "B")
    motif_a = lib.create_expression(m, unreal.MaterialExpressionAdd, 1220, 1720)
    wire("motif_aA", m_h, motif_a, "A")
    wire("motif_aB", m_s, motif_a, "B")
    motif_b = lib.create_expression(m, unreal.MaterialExpressionAdd, 1380, 1780)
    wire("motif_bA", motif_a, motif_b, "A")
    wire("motif_bB", m_f, motif_b, "B")
    motif = lib.create_expression(m, unreal.MaterialExpressionAdd, 1540, 1820)
    wire("motif_cA", motif_b, motif, "A")
    wire("motif_cB", m_m, motif, "B")
    # optional glyph texture overlay (mesh UV — not world LWC)
    wire("glyph_uv", uv, fairy_glyph, "UVs", "Coordinates")
    motif_tex = lib.create_expression(m, unreal.MaterialExpressionAdd, 1700, 1820)
    wire("motif_texA", motif, motif_tex, "A")
    wire("motif_texB", fairy_glyph, motif_tex, "B")
    highlight = lib.create_expression(m, unreal.MaterialExpressionSubtract, 1220, 1580)
    wire("hl_A", rim_mask, highlight, "A")
    wire("hl_B", fairy_thresh, highlight, "B")
    highlight_sat = lib.create_expression(m, unreal.MaterialExpressionSaturate, 1380, 1580)
    wire("hl_sat", highlight, highlight_sat, "Input")
    fairy_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1860, 1700)
    wire("fairy_mA", motif_tex, fairy_m, "A")
    wire("fairy_mB", highlight_sat, fairy_m, "B")
    fairy_w = lib.create_expression(m, unreal.MaterialExpressionMultiply, 2020, 1700)
    wire("fairy_wA", fairy_m, fairy_w, "A")
    wire("fairy_wB", fairy_int, fairy_w, "B")
    fairy_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 2180, 1700)
    wire("fairy_eA", fairy_w, fairy_e, "A")
    wire("fairy_eB", fairy_color, fairy_e, "B")

    # emissive sum + bloom
    a1 = lib.create_expression(m, unreal.MaterialExpressionAdd, 2400, 1200)
    wire("emi1A", rim_e, a1, "A")
    wire("emi1B", irid_e, a1, "B")
    a2 = lib.create_expression(m, unreal.MaterialExpressionAdd, 2560, 1280)
    wire("emi2A", a1, a2, "A")
    wire("emi2B", spark_e, a2, "B")
    a3 = lib.create_expression(m, unreal.MaterialExpressionAdd, 2720, 1360)
    wire("emi3A", a2, a3, "A")
    wire("emi3B", glow_e, a3, "B")
    a4 = lib.create_expression(m, unreal.MaterialExpressionAdd, 2880, 1440)
    wire("emi4A", a3, a4, "A")
    wire("emi4B", inner_e, a4, "B")
    a5 = lib.create_expression(m, unreal.MaterialExpressionAdd, 3040, 1520)
    wire("emi5A", a4, a5, "A")
    wire("emi5B", sheen_e, a5, "B")
    a6 = lib.create_expression(m, unreal.MaterialExpressionAdd, 3200, 1600)
    wire("emi6A", a5, a6, "A")
    wire("emi6B", gold_emis_m, a6, "B")
    a7 = lib.create_expression(m, unreal.MaterialExpressionAdd, 3360, 1680)
    wire("emi7A", a6, a7, "A")
    wire("emi7B", fairy_e, a7, "B")
    audio_emis_w = lib.create_expression(m, unreal.MaterialExpressionMultiply, 3440, 1880)
    wire("aewA", audio_react, audio_emis_w, "A")
    wire("aewB", audio_emis_pulse, audio_emis_w, "B")
    audio_emis_vec = lib.create_expression(m, unreal.MaterialExpressionMultiply, 3600, 1880)
    wire("aevA", audio_emis_w, audio_emis_vec, "A")
    wire("aevB", glow_color, audio_emis_vec, "B")
    a7_audio = lib.create_expression(m, unreal.MaterialExpressionAdd, 3760, 1760)
    wire("a7aA", a7, a7_audio, "A")
    wire("a7aB", audio_emis_vec, a7_audio, "B")
    emissive_raw = lib.create_expression(m, unreal.MaterialExpressionAdd, 3520, 1760)
    wire("emi8A", a7_audio, emissive_raw, "A")
    wire("emi8B", flower_e, emissive_raw, "B")
    bloom_m = lib.create_expression(m, unreal.MaterialExpressionAdd, 3680, 1760)
    wire("bloom_add_A", const1(m, 3520, 1860, 1.0), bloom_m, "A")
    wire("bloom_add_B", bloom, bloom_m, "B")
    emissive = lib.create_expression(m, unreal.MaterialExpressionMultiply, 3840, 1760)
    wire("bloom_mul_A", emissive_raw, emissive, "A")
    wire("bloom_mul_B", bloom_m, emissive, "B")
    emissive_madoka = lib.create_expression(m, unreal.MaterialExpressionAdd, 4000, 1760)
    wire("madoka_emi_mergeA", emissive, emissive_madoka, "A")
    wire("madoka_emi_mergeB", madoka_emissive_extend, emissive_madoka, "B")
    emissive = emissive_madoka

    # ---- Macro variation + detail (MF_MacroDetail) ----
    macro_mf_node = None
    magical_mf_node = None
    macro_str = lib.scalar_param(m, "MacroVariationStrength", "MacroDetail", 0.0, 3600, 120)
    macro_scale = lib.scalar_param(m, "MacroScale", "MacroDetail", 0.0008, 3600, 200)
    det_tex = tex_object(m, "DetailNormal", 3600, 280, "MacroDetail")
    det_tiling = lib.scalar_param(m, "DetailTiling", "MacroDetail", 8.0, 3600, 440)
    det_str = lib.scalar_param(m, "DetailStrength", "MacroDetail", 0.0, 3600, 520)
    macro_mf = mf_call(m, MF_MACRO_DETAIL, 3800, 480)
    if macro_mf:
        wire("macro_bc", final_color, macro_mf, "BaseColor")
        wire("macro_n", nrm, macro_mf, "Normal")
        wire("macro_str_in", macro_str, macro_mf, "MacroVariationStrength")
        wire("macro_scale_in", macro_scale, macro_mf, "MacroScale")
        wire("macro_det_str", det_str, macro_mf, "DetailStrength")
        wire("macro_det_tile", det_tiling, macro_mf, "DetailTiling")
        final_color = macro_mf
        macro_mf_node = macro_mf
    else:
        mac_tc = lib.create_expression(m, unreal.MaterialExpressionTextureCoordinate, 3600, 620)
        mac_scl = lib.create_expression(m, unreal.MaterialExpressionMultiply, 3760, 620)
        wire("mac_tcA", mac_tc, mac_scl, "A")
        wire("mac_tcB", macro_scale, mac_scl, "B")
        mac_tile = lib.create_expression(m, unreal.MaterialExpressionMultiply, 3920, 620)
        wire("mac_tlA", mac_scl, mac_tile, "A")
        wire("mac_tlB", const1(m, 3760, 720, 48.0), mac_tile, "B")
        mac_nx = mask_channel(m, mac_tile, "r", "mac_nx", 3920, 560)
        mac_ny = mask_channel(m, mac_tile, "g", "mac_ny", 3920, 640)
        mac_nz = const1(m, 3920, 720, 0.0)
        mac_pos = lib.connect_append3_from_scalars(mac_nx, mac_ny, mac_nz, m, 4080, 620)
        mac_noise = lib.create_expression(m, unreal.MaterialExpressionNoise, 4240, 620)
        wire("mac_noise_pos", mac_pos, mac_noise, "Position", "")
        mac_sub = lib.create_expression(m, unreal.MaterialExpressionSubtract, 4400, 620)
        wire("mac_subA", mac_noise, mac_sub, "A")
        wire("mac_subB", const1(m, 4240, 720, 0.5), mac_sub, "B")
        mac_amt = lib.create_expression(m, unreal.MaterialExpressionMultiply, 4560, 620)
        wire("mac_amtA", mac_sub, mac_amt, "A")
        wire("mac_amtB", macro_str, mac_amt, "B")
        mac_fac = lib.create_expression(m, unreal.MaterialExpressionAdd, 4720, 600)
        wire("mac_facA", const1(m, 4560, 720, 1.0), mac_fac, "A")
        wire("mac_facB", mac_amt, mac_fac, "B")
        color_macro = lib.create_expression(m, unreal.MaterialExpressionMultiply, 4720, 480)
        wire("mac_colA", final_color, color_macro, "A")
        wire("mac_colB", mac_fac, color_macro, "B")
        final_color = color_macro
        det_tc = lib.create_expression(m, unreal.MaterialExpressionTextureCoordinate, 3600, 900)
        det_uv = lib.create_expression(m, unreal.MaterialExpressionMultiply, 3760, 900)
        wire("det_uvA", det_tc, det_uv, "A")
        wire("det_uvB", det_tiling, det_uv, "B")
        det_s = lib.create_expression(m, unreal.MaterialExpressionTextureSample, 3920, 900)
        lib.try_set_editor_property(det_s, "sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        wire("det_obj", det_tex, det_s, "Tex", "TextureObject")
        wire("det_uv", det_uv, det_s, "UVs", "Coordinates")
        nrm_det = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 4240, 900)
        wire("ndA", nrm, nrm_det, "A")
        wire("ndB", det_s, nrm_det, "B")
        wire("ndAlpha", det_str, nrm_det, "Alpha")
        nrm = nrm_det

    # ---- Magical-girl transform (MF_Magical + MPC_Magical) ----
    mtransform = lib.scalar_param(
        m, "MagicalTransform", "Magical", 0.0, 4800, 120,
        desc="0→1 henshin driver (sync MPC_Magical)",
    )
    motif_mask = tex_object(m, "MotifMask", 4800, 200, "Magical")
    motif_scale = lib.scalar_param(m, "MotifScale", "Magical", 6.0, 4800, 360)
    motif_color = lib.vector_param(m, "MotifColor", "Magical", (1.0, 0.45, 0.72, 1.0), 4800, 440)
    transform_glow = lib.scalar_param(m, "TransformGlow", "Magical", 3.0, 4800, 520)
    wipe_soft = lib.scalar_param(m, "WipeSoftness", "Magical", 0.25, 4800, 600, desc="World-Z wipe edge softness")
    magical_palette = lib.vector_param(m, "MagicalPalette", "Magical", (1.0, 0.72, 0.86, 1.0), 4800, 680)
    mpc_mag = lib.collection_scalar(m, MPC_MAGICAL, "MagicalTransform", 4800, 40)
    mt_add = lib.create_expression(m, unreal.MaterialExpressionAdd, 4960, 120)
    wire("mt_addA", mtransform, mt_add, "A")
    wire("mt_addB", mpc_mag, mt_add, "B")
    mt_beat = lib.create_expression(m, unreal.MaterialExpressionAdd, 5040, 200)
    wire("mt_beatA", mt_add, mt_beat, "A")
    wire("mt_beatB", beat_mod, mt_beat, "B")
    mt_combined = lib.create_expression(m, unreal.MaterialExpressionSaturate, 5120, 120)
    wire("mt_sat", mt_beat, mt_combined, "Input", "")
    magical_mf_node = None
    magical_mf = mf_call(m, MF_MAGICAL, 5280, 480)
    if magical_mf:
        wire("mag_bc", final_color, magical_mf, "BaseColor")
        wire("mag_em", emissive, magical_mf, "Emissive")
        wire("mag_mt", mt_combined, magical_mf, "MagicalTransform")
        wire("mag_mask", motif_mask, magical_mf, "MotifMask", "Texture")
        wire("mag_scale", motif_scale, magical_mf, "MotifScale")
        wire("mag_col", motif_color, magical_mf, "MotifColor")
        wire("mag_glow", transform_glow, magical_mf, "TransformGlow")
        wire("mag_wipe", wipe_soft, magical_mf, "WipeSoftness")
        wire("mag_pal", magical_palette, magical_mf, "MagicalPalette")
        wire("mag_uv", uv, magical_mf, "UV")
        final_color = magical_mf
        magical_mf_node = magical_mf
    else:
        mg_wp = lib.create_expression(m, unreal.MaterialExpressionWorldPosition, 4800, 780)
        mg_z = lib.create_expression(m, unreal.MaterialExpressionComponentMask, 4960, 780)
        mg_z.set_editor_property("r", False)
        mg_z.set_editor_property("g", False)
        mg_z.set_editor_property("b", True)
        mg_z.set_editor_property("a", False)
        wire("mg_z", mg_wp, mg_z, "")
        mg_zs = lib.create_expression(m, unreal.MaterialExpressionMultiply, 5120, 780)
        wire("mg_zsA", mg_z, mg_zs, "A")
        wire("mg_zsB", const1(m, 4960, 880, 0.004), mg_zs, "B")
        mg_sub = lib.create_expression(m, unreal.MaterialExpressionSubtract, 5280, 760)
        wire("mg_subA", mt_combined, mg_sub, "A")
        wire("mg_subB", mg_zs, mg_sub, "B")
        mg_div = lib.create_expression(m, unreal.MaterialExpressionDivide, 5440, 760)
        wire("mg_divA", mg_sub, mg_div, "A")
        wire("mg_divB", wipe_soft, mg_div, "B")
        mg_wipe = lib.create_expression(m, unreal.MaterialExpressionSaturate, 5600, 760)
        wire("mg_wipe", mg_div, mg_wipe, "Input", "")
        mg_tc = lib.create_expression(m, unreal.MaterialExpressionTextureCoordinate, 4800, 980)
        mg_uv = lib.create_expression(m, unreal.MaterialExpressionMultiply, 4960, 980)
        wire("mg_uvA", mg_tc, mg_uv, "A")
        wire("mg_uvB", motif_scale, mg_uv, "B")
        mg_s = lib.create_expression(m, unreal.MaterialExpressionTextureSample, 5120, 980)
        wire("mg_obj", motif_mask, mg_s, "Tex", "TextureObject")
        wire("mg_suv", mg_uv, mg_s, "UVs", "Coordinates")
        mg_sr = lib.create_expression(m, unreal.MaterialExpressionComponentMask, 5280, 980)
        mg_sr.set_editor_property("r", True)
        mg_sr.set_editor_property("g", False)
        mg_sr.set_editor_property("b", False)
        mg_sr.set_editor_property("a", False)
        wire("mg_sr", mg_s, mg_sr, "")
        mg_rev1 = lib.create_expression(m, unreal.MaterialExpressionMultiply, 5760, 860)
        wire("mg_rev1A", mg_wipe, mg_rev1, "A")
        wire("mg_rev1B", mg_sr, mg_rev1, "B")
        mg_rev = lib.create_expression(m, unreal.MaterialExpressionMultiply, 5920, 860)
        wire("mg_revA", mg_rev1, mg_rev, "A")
        wire("mg_revB", mt_combined, mg_rev, "B")
        mg_ec = lib.create_expression(m, unreal.MaterialExpressionMultiply, 6080, 860)
        wire("mg_ecA", mg_rev, mg_ec, "A")
        wire("mg_ecB", motif_color, mg_ec, "B")
        mg_emis = lib.create_expression(m, unreal.MaterialExpressionMultiply, 6240, 860)
        wire("mg_emisA", mg_ec, mg_emis, "A")
        wire("mg_emisB", transform_glow, mg_emis, "B")
        mg_pal_amt = lib.create_expression(m, unreal.MaterialExpressionMultiply, 5760, 480)
        wire("mg_palA", mt_combined, mg_pal_amt, "A")
        wire("mg_palB", const1(m, 5600, 560, 0.5), mg_pal_amt, "B")
        mg_color = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 5920, 480)
        wire("mg_colA", final_color, mg_color, "A")
        wire("mg_colB", magical_palette, mg_color, "B")
        wire("mg_colAlpha", mg_pal_amt, mg_color, "Alpha")
        final_color = mg_color
        mg_emis_add = lib.create_expression(m, unreal.MaterialExpressionAdd, 6400, 1100)
        wire("mg_emis_addA", emissive, mg_emis_add, "A")
        wire("mg_emis_addB", mg_emis, mg_emis_add, "B")
        emissive = mg_emis_add

    # ---- Character / Elemental / World / Cinematic (Hoyoverse stack, default 0) ----
    # --- Character: skin wrap, cheek warmth, eye/crystal spec, hair sheen ---
    skin_wrap_str = lib.scalar_param(m, "SkinWrapStrength", "Character", 0.0, 6600, 120)
    skin_wrap_rad = lib.scalar_param(m, "SkinWrapRadius", "Character", 0.55, 6600, 220)
    skin_shadow_tint = lib.vector_param(m, "SkinShadowTint", "Character", (0.92, 0.72, 0.68, 1.0), 6600, 320)
    skin_shadow_str = lib.scalar_param(m, "SkinShadowStrength", "Character", 0.0, 6600, 420)
    cheek_warm_str = lib.scalar_param(m, "CheekWarmthStrength", "Character", 0.0, 6600, 520)
    cheek_warm_col = lib.vector_param(m, "CheekWarmthColor", "Character", (1.0, 0.72, 0.62, 1.0), 6600, 620)
    cheek_warm_bias = lib.scalar_param(m, "CheekWarmthBias", "Character", 0.55, 6600, 720)
    eye_hi_str = lib.scalar_param(m, "EyeHighlightStrength", "Character", 0.0, 6600, 820)
    eye_hi_pow = lib.scalar_param(m, "EyeHighlightPower", "Character", 48.0, 6600, 920)
    eye_hi_col = lib.vector_param(m, "EyeHighlightColor", "Character", (1.0, 1.0, 1.0, 1.0), 6600, 1020)
    hair_sheen_str = lib.scalar_param(m, "HairSheenStrength", "Character", 0.0, 6600, 1120)
    hair_sheen_pow = lib.scalar_param(m, "HairSheenPower", "Character", 10.0, 6600, 1220)
    hair_sheen_tint = lib.vector_param(m, "HairSheenTint", "Character", (0.95, 0.92, 0.88, 1.0), 6600, 1320)

    skin_ndotl = lib.create_expression(m, unreal.MaterialExpressionDotProduct, 6680, 120)
    wire("sndotl_A", pnormal, skin_ndotl, "A")
    wire("sndotl_B", light_dir, skin_ndotl, "B")
    wrap_mul = lib.create_expression(m, unreal.MaterialExpressionMultiply, 6840, 200)
    wire("wrap_mulA", skin_wrap_rad, wrap_mul, "A")
    wire("wrap_mulB", skin_wrap_str, wrap_mul, "B")
    wrap_add = lib.create_expression(m, unreal.MaterialExpressionAdd, 7000, 120)
    wire("wrap_addA", skin_ndotl, wrap_add, "A")
    wire("wrap_addB", wrap_mul, wrap_add, "B")
    wrap_den = lib.create_expression(m, unreal.MaterialExpressionAdd, 6840, 280)
    wire("wrap_denA", const1(m, 6680, 280, 1.0), wrap_den, "A")
    wire("wrap_denB", skin_wrap_rad, wrap_den, "B")
    wrap_div = lib.create_expression(m, unreal.MaterialExpressionDivide, 7160, 160)
    wire("wrap_divA", wrap_add, wrap_div, "A")
    wire("wrap_divB", wrap_den, wrap_div, "B")
    wrap_sat = lib.create_expression(m, unreal.MaterialExpressionSaturate, 7320, 160)
    WIRES["wrap_sat"] = lib.connect_unary(wrap_div, wrap_sat)
    std_lit = lib.create_expression(m, unreal.MaterialExpressionSaturate, 7160, 280)
    WIRES["std_lit"] = lib.connect_unary(skin_ndotl, std_lit)
    skin_lit = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 7480, 200)
    wire("skin_litA", std_lit, skin_lit, "A")
    wire("skin_litB", wrap_sat, skin_lit, "B")
    wire("skin_lit_alpha", skin_wrap_str, skin_lit, "Alpha")
    skin_shadow = lib.create_expression(m, unreal.MaterialExpressionOneMinus, 7000, 120)
    WIRES["skin_sh_in"] = lib.connect_unary(skin_lit, skin_shadow)
    skin_sh_amt = lib.create_expression(m, unreal.MaterialExpressionMultiply, 7160, 120)
    wire("skin_shA", skin_shadow, skin_sh_amt, "A")
    skin_sh_gate = lib.create_expression(m, unreal.MaterialExpressionMultiply, 7000, 240)
    wire("skin_shgA", skin_shadow_str, skin_sh_gate, "A")
    wire("skin_shgB", skin_wrap_str, skin_sh_gate, "B")
    wire("skin_shB", skin_sh_gate, skin_sh_amt, "B")
    skin_col = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 7320, 80)
    wire("skin_cA", final_color, skin_col, "A")
    wire("skin_cB", skin_shadow_tint, skin_col, "B")
    wire("skin_c_alpha", skin_sh_amt, skin_col, "Alpha")
    final_color = skin_col

    vert_n = lib.create_expression(m, unreal.MaterialExpressionVertexNormalWS, 6840, 360)
    cheek_up = lib.create_expression(m, unreal.MaterialExpressionConstant3Vector, 6840, 480)
    cheek_up.set_editor_property("constant", unreal.LinearColor(0.0, 1.0, 0.35, 1.0))
    cheek_dot = lib.create_expression(m, unreal.MaterialExpressionDotProduct, 7000, 400)
    wire("cheek_dotA", vert_n, cheek_dot, "A")
    wire("cheek_dotB", cheek_up, cheek_dot, "B")
    cheek_sat = lib.create_expression(m, unreal.MaterialExpressionSaturate, 7160, 400)
    wire("cheek_sat", cheek_dot, cheek_sat, "Input")
    cheek_pow = lib.create_expression(m, unreal.MaterialExpressionPower, 7320, 400)
    wire("cheek_powA", cheek_sat, cheek_pow, "Base")
    wire("cheek_powB", cheek_warm_bias, cheek_pow, "Exp")
    cheek_amt = lib.create_expression(m, unreal.MaterialExpressionMultiply, 7480, 400)
    wire("cheek_amtA", cheek_pow, cheek_amt, "A")
    wire("cheek_amtB", cheek_warm_str, cheek_amt, "B")
    cheek_col = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 7640, 360)
    wire("cheek_cA", final_color, cheek_col, "A")
    wire("cheek_cB", cheek_warm_col, cheek_col, "B")
    wire("cheek_c_alpha", cheek_amt, cheek_col, "Alpha")
    final_color = cheek_col

    view_ws = lib.create_expression(m, unreal.MaterialExpressionCameraVectorWS, 6840, 640)
    view_neg = lib.create_expression(m, unreal.MaterialExpressionMultiply, 7000, 640)
    wire("view_negA", view_ws, view_neg, "A")
    wire("view_negB", const1(m, 6840, 760, -1.0), view_neg, "B")
    eye_dp = lib.create_expression(m, unreal.MaterialExpressionDotProduct, 7160, 640)
    wire("eye_dpA", pnormal, eye_dp, "A")
    wire("eye_dpB", view_neg, eye_dp, "B")
    eye_sat = lib.create_expression(m, unreal.MaterialExpressionSaturate, 7320, 640)
    wire("eye_sat", eye_dp, eye_sat, "Input")
    eye_pow = lib.create_expression(m, unreal.MaterialExpressionPower, 7480, 640)
    wire("eye_powA", eye_sat, eye_pow, "Base")
    wire("eye_powB", eye_hi_pow, eye_pow, "Exp")
    eye_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 7640, 640)
    wire("eye_mA", eye_pow, eye_m, "A")
    wire("eye_mB", eye_hi_str, eye_m, "B")
    eye_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 7800, 640)
    wire("eye_eA", eye_m, eye_e, "A")
    wire("eye_eB", eye_hi_col, eye_e, "B")

    hair_xy = world_xy(m, 6840, 820)
    hair_x = lib.create_expression(m, unreal.MaterialExpressionComponentMask, 7000, 820)
    hair_x.set_editor_property("r", True)
    hair_x.set_editor_property("g", False)
    hair_x.set_editor_property("b", False)
    hair_x.set_editor_property("a", False)
    wire("hair_x", hair_xy, hair_x, "")
    hair_phase = lib.create_expression(m, unreal.MaterialExpressionMultiply, 7160, 820)
    wire("hair_phA", hair_x, hair_phase, "A")
    wire("hair_phB", const1(m, 7000, 940, 8.0), hair_phase, "B")
    hair_sin = lib.create_expression(m, unreal.MaterialExpressionSine, 7320, 820)
    hair_sin.set_editor_property("period", 1.0)
    WIRES["hair_sin"] = lib.connect_unary(hair_phase, hair_sin)
    hair_abs = lib.create_expression(m, unreal.MaterialExpressionAbs, 7480, 820)
    WIRES["hair_abs"] = lib.connect_unary(hair_sin, hair_abs)
    hair_pow = lib.create_expression(m, unreal.MaterialExpressionPower, 7480, 820)
    wire("hair_powA", hair_abs, hair_pow, "Base")
    wire("hair_powB", hair_sheen_pow, hair_pow, "Exp")
    hair_view = lib.create_expression(m, unreal.MaterialExpressionDotProduct, 7640, 900)
    wire("hair_vA", pnormal, hair_view, "A")
    wire("hair_vB", view_neg, hair_view, "B")
    hair_view_sat = lib.create_expression(m, unreal.MaterialExpressionSaturate, 7800, 900)
    WIRES["hair_vsat"] = lib.connect_unary(hair_view, hair_view_sat)
    hair_spec = lib.create_expression(m, unreal.MaterialExpressionMultiply, 7960, 860)
    wire("hair_spA", hair_pow, hair_spec, "A")
    wire("hair_spB", hair_view_sat, hair_spec, "B")
    hair_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 8120, 860)
    wire("hair_mA", hair_spec, hair_m, "A")
    wire("hair_mB", hair_sheen_str, hair_m, "B")
    hair_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 8120, 840)
    wire("hair_eA", hair_m, hair_e, "A")
    wire("hair_eB", hair_sheen_tint, hair_e, "B")

    # --- Elemental: Genshin-style element grade + time-of-day warmth ---
    element_type = lib.scalar_param(m, "ElementType", "Elemental", 0.0, 6600, 1500)
    element_str = lib.scalar_param(m, "ElementStrength", "Elemental", 0.0, 6600, 1600)
    element_emis = lib.scalar_param(m, "ElementEmissiveBoost", "Elemental", 0.0, 6600, 1700)
    tod_warmth = lib.scalar_param(m, "TimeOfDayWarmth", "Elemental", 0.0, 6600, 1800)

    pyro_c = const3(m, 6680, 1420, 1.0, 0.42, 0.18)
    hydro_c = const3(m, 6680, 1500, 0.22, 0.62, 0.98)
    anemo_c = const3(m, 6680, 1580, 0.55, 0.92, 0.82)
    electro_c = const3(m, 6680, 1660, 0.62, 0.38, 0.95)
    dendro_c = const3(m, 6680, 1740, 0.42, 0.82, 0.28)
    geo_c = const3(m, 6680, 1820, 0.92, 0.78, 0.32)

    w_pyro = style_peak(m, element_type, 1.0, "el_pyro", 6840, 1420)
    w_hydro = style_peak(m, element_type, 2.0, "el_hydro", 6840, 1500)
    w_anemo = style_peak(m, element_type, 3.0, "el_anemo", 6840, 1580)
    w_electro = style_peak(m, element_type, 4.0, "el_electro", 6840, 1660)
    w_dendro = style_peak(m, element_type, 5.0, "el_dendro", 6840, 1740)
    w_geo = style_peak(m, element_type, 6.0, "el_geo", 6840, 1820)

    el_mix_a = lib.create_expression(m, unreal.MaterialExpressionAdd, 7000, 1480)
    wire("el_maA", w_pyro, el_mix_a, "A")
    wire("el_maB", w_hydro, el_mix_a, "B")
    el_mix_b = lib.create_expression(m, unreal.MaterialExpressionAdd, 7160, 1540)
    wire("el_mbA", el_mix_a, el_mix_b, "A")
    wire("el_mbB", w_anemo, el_mix_b, "B")
    el_mix_c = lib.create_expression(m, unreal.MaterialExpressionAdd, 7320, 1600)
    wire("el_mcA", el_mix_b, el_mix_c, "A")
    wire("el_mcB", w_electro, el_mix_c, "B")
    el_mix_d = lib.create_expression(m, unreal.MaterialExpressionAdd, 7480, 1660)
    wire("el_mdA", el_mix_c, el_mix_d, "A")
    wire("el_mdB", w_dendro, el_mix_d, "B")
    el_mix = lib.create_expression(m, unreal.MaterialExpressionAdd, 7640, 1720)
    wire("el_mA", el_mix_d, el_mix, "A")
    wire("el_mB", w_geo, el_mix, "B")

    el_c1 = lerp3(m, pyro_c, hydro_c, w_hydro, "el_c1", 7800, 1460)
    el_c2 = lerp3(m, el_c1, anemo_c, w_anemo, "el_c2", 7960, 1520)
    el_c3 = lerp3(m, el_c2, electro_c, w_electro, "el_c3", 8120, 1580)
    el_c4 = lerp3(m, el_c3, dendro_c, w_dendro, "el_c4", 8280, 1640)
    el_tint = lerp3(m, el_c4, geo_c, w_geo, "el_tint", 8440, 1700)
    el_w = lib.create_expression(m, unreal.MaterialExpressionMultiply, 8600, 1680)
    wire("el_wA", el_mix, el_w, "A")
    wire("el_wB", element_str, el_w, "B")
    el_col = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 8760, 1640)
    wire("el_colA", final_color, el_col, "A")
    wire("el_colB", el_tint, el_col, "B")
    wire("el_col_alpha", el_w, el_col, "Alpha")
    final_color = el_col
    el_emis_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 8760, 1780)
    wire("el_emA", el_w, el_emis_m, "A")
    wire("el_emB", element_emis, el_emis_m, "B")
    el_emis_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 8920, 1780)
    wire("el_emisA", el_emis_m, el_emis_e, "A")
    wire("el_emisB", el_tint, el_emis_e, "B")

    tod_neutral = const3(m, 6840, 1920, 1.0, 1.0, 1.0)
    tod_warm_vec = const3(m, 6840, 1980, 1.12, 1.0, 0.92)
    tod_cool_vec = const3(m, 6840, 2040, 0.94, 1.0, 1.06)
    tod_neg = lib.create_expression(m, unreal.MaterialExpressionMultiply, 6680, 2120)
    wire("tod_negA", tod_warmth, tod_neg, "A")
    wire("tod_negB", const1(m, 6520, 2120, -1.0), tod_neg, "B")
    warm_amt = lib.create_expression(m, unreal.MaterialExpressionMax, 7000, 1920)
    wire("warm_amtA", tod_warmth, warm_amt, "A")
    wire("warm_amtB", const1(m, 6840, 2020, 0.0), warm_amt, "B")
    cool_amt = lib.create_expression(m, unreal.MaterialExpressionMax, 7000, 2080)
    wire("cool_amtA", tod_neg, cool_amt, "A")
    wire("cool_amtB", const1(m, 6840, 2180, 0.0), cool_amt, "B")
    tod_warm_blend = lerp3(m, tod_neutral, tod_warm_vec, warm_amt, "tod_warm", 7160, 1960)
    tod_vec = lerp3(m, tod_warm_blend, tod_cool_vec, cool_amt, "tod_vec", 7320, 2020)

    # --- UDS sync: UltraDynamicWeather_Parameters MPC (live Time of Day / Sun Vector) ---
    uds_mpc = "/Game/UltraDynamicSky/Materials/Weather/UltraDynamicWeather_Parameters"
    uds_dtn_color = (
        "/Game/UltraDynamicSky/Materials/Material_Functions/Sky_Utilities/Day_to_Night_Color"
    )
    uds_leaf = "UltraDynamicWeather_Parameters"
    uds_ok = unreal.EditorAssetLibrary.does_asset_exist(f"{uds_mpc}.{uds_leaf}")
    use_uds_tod = static_switch(m, "UseUDSTimeOfDay", "TimeOfDay", 6360, 1880, default=False)
    tod_mpc_str = lib.scalar_param(m, "TimeOfDayMPCStrength", "TimeOfDay", 1.0, 6360, 1980)
    tod_vec_final = tod_vec
    if uds_ok:
        mf_color = mf_call(m, uds_dtn_color, 6520, 1860)
        if mf_color:
            wire("uds_day", tod_warm_vec, mf_color, "Day", "Daytime", "Day Value")
            wire("uds_night", tod_cool_vec, mf_color, "Night", "Nighttime", "Night Value")
            uds_blend = lerp3(m, tod_vec, mf_color, tod_mpc_str, "uds_tod_blend", 6680, 1920)
            WIRES["uds_tod_sw"] = lib.connect_static_switch(use_uds_tod, uds_blend, tod_vec)
            tod_vec_final = use_uds_tod
            unreal.log("[Universal] UDS TimeOfDay MPC sync wired (UseUDSTimeOfDay static switch)")
        else:
            unreal.log_warning("[Universal] Day_to_Night_Color missing — UDS sync skipped")
    else:
        unreal.log_warning(
            "[Universal] UltraDynamicWeather_Parameters not found — manual TimeOfDayWarmth only"
        )

    tod_col = lib.create_expression(m, unreal.MaterialExpressionMultiply, 7480, 2000)
    wire("tod_cA", final_color, tod_col, "A")
    wire("tod_cB", tod_vec_final, tod_col, "B")
    final_color = tod_col

    # --- World: wetness, snow dusting, moss concavity ---
    wet_str = lib.scalar_param(m, "WetnessStrength", "World", 0.0, 9000, 120)
    wet_rough = lib.scalar_param(m, "WetnessRoughness", "World", 0.12, 9000, 220)
    wet_dark = lib.scalar_param(m, "WetnessDarken", "World", 0.38, 9000, 320)
    wet_flat = lib.scalar_param(m, "WetnessNormalFlatten", "World", 0.65, 9000, 420)
    snow_str = lib.scalar_param(m, "SnowDustStrength", "World", 0.0, 9000, 520)
    snow_col = lib.vector_param(m, "SnowDustColor", "World", (0.92, 0.95, 0.98, 1.0), 9000, 620)
    snow_bias = lib.scalar_param(m, "SnowUpBias", "World", 2.2, 9000, 720)
    moss_str = lib.scalar_param(m, "MossConcavityStrength", "World", 0.0, 9000, 820)
    moss_col = lib.vector_param(m, "MossColor", "World", (0.28, 0.42, 0.22, 1.0), 9000, 920)
    moss_sens = lib.scalar_param(m, "MossCurvatureSens", "World", 1.8, 9000, 1020)

    up_n = lib.create_expression(m, unreal.MaterialExpressionConstant3Vector, 9160, 120)
    up_n.set_editor_property("constant", unreal.LinearColor(0.0, 0.0, 1.0, 1.0))
    wet_up = lib.create_expression(m, unreal.MaterialExpressionDotProduct, 9320, 120)
    wire("wet_upA", pnormal, wet_up, "A")
    wire("wet_upB", up_n, wet_up, "B")
    wet_inv = lib.create_expression(m, unreal.MaterialExpressionOneMinus, 9480, 120)
    wire("wet_inv", wet_up, wet_inv, "Input")
    wet_mask = lib.create_expression(m, unreal.MaterialExpressionMultiply, 9640, 120)
    wire("wet_mA", wet_inv, wet_mask, "A")
    wire("wet_mB", wet_str, wet_mask, "B")
    rough_wet = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 9800, 80)
    wire("rw_A", rough_gold, rough_wet, "A")
    wire("rw_B", wet_rough, rough_wet, "B")
    wire("rw_alpha", wet_mask, rough_wet, "Alpha")
    rough_gold = rough_wet
    wet_dark_f = lib.create_expression(m, unreal.MaterialExpressionAdd, 9640, 240)
    wire("wd_fA", const1(m, 9480, 340, 1.0), wet_dark_f, "A")
    wet_d_neg = lib.create_expression(m, unreal.MaterialExpressionMultiply, 9480, 280)
    wire("wd_nA", wet_dark, wet_d_neg, "A")
    wire("wd_nB", const1(m, 9320, 340, -1.0), wet_d_neg, "B")
    wire("wd_fB", wet_d_neg, wet_dark_f, "B")
    wet_dark_mul = lib.create_expression(m, unreal.MaterialExpressionMultiply, 9800, 220)
    wire("wdm_A", final_color, wet_dark_mul, "A")
    wire("wdm_B", wet_dark_f, wet_dark_mul, "B")
    wet_col = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 9960, 180)
    wire("wc_A", final_color, wet_col, "A")
    wire("wc_B", wet_dark_mul, wet_col, "B")
    wire("wc_alpha", wet_mask, wet_col, "Alpha")
    final_color = wet_col
    flat_up = lib.create_expression(m, unreal.MaterialExpressionConstant3Vector, 9160, 380)
    flat_up.set_editor_property("constant", unreal.LinearColor(0.0, 0.0, 1.0, 1.0))
    nrm_flat = lerp3(m, nrm, flat_up, wet_flat, "wet_nrm", 9320, 360)
    nrm_wet = lerp3(m, nrm, nrm_flat, wet_mask, "wet_nrm2", 9480, 360)
    nrm = nrm_wet

    snow_up = lib.create_expression(m, unreal.MaterialExpressionDotProduct, 9160, 520)
    wire("snow_upA", pnormal, snow_up, "A")
    wire("snow_upB", up_n, snow_up, "B")
    snow_sat = lib.create_expression(m, unreal.MaterialExpressionSaturate, 9320, 520)
    wire("snow_sat", snow_up, snow_sat, "Input")
    snow_pow = lib.create_expression(m, unreal.MaterialExpressionPower, 9480, 520)
    wire("snow_powA", snow_sat, snow_pow, "Base")
    wire("snow_powB", snow_bias, snow_pow, "Exp")
    snow_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 9640, 520)
    wire("snow_mA", snow_pow, snow_m, "A")
    wire("snow_mB", snow_str, snow_m, "B")
    snow_col_l = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 9800, 500)
    wire("snow_cA", final_color, snow_col_l, "A")
    wire("snow_cB", snow_col, snow_col_l, "B")
    wire("snow_c_alpha", snow_m, snow_col_l, "Alpha")
    final_color = snow_col_l

    moss_mask = concavity_mask(m, curve_abs, moss_sens, "moss", 9160, 720)
    moss_amt = lib.create_expression(m, unreal.MaterialExpressionMultiply, 9480, 720)
    wire("moss_amtA", moss_mask, moss_amt, "A")
    wire("moss_amtB", moss_str, moss_amt, "B")
    moss_col_l = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 9640, 700)
    wire("moss_cA", final_color, moss_col_l, "A")
    wire("moss_cB", moss_col, moss_col_l, "B")
    wire("moss_c_alpha", moss_amt, moss_col_l, "Alpha")
    final_color = moss_col_l

    audio_rough_w = lib.create_expression(m, unreal.MaterialExpressionMultiply, 9800, 640)
    wire("arwA", audio_react, audio_rough_w, "A")
    wire("arwB", audio_rough_pulse, audio_rough_w, "B")
    rough_audio = lib.create_expression(m, unreal.MaterialExpressionSubtract, 9960, 640)
    wire("raA", rough_gold, rough_audio, "A")
    wire("raB", audio_rough_w, rough_audio, "B")
    rough_gold = lib.create_expression(m, unreal.MaterialExpressionSaturate, 10120, 640)
    wire("ra_sat", rough_audio, rough_gold, "Input")

    # --- Cinematic: contact rim, distance fade, dither dissolve edge ---
    contact_rim_str = lib.scalar_param(m, "ContactRimStrength", "Cinematic", 0.0, 10200, 120)
    contact_rim_pow = lib.scalar_param(m, "ContactRimPower", "Cinematic", 5.5, 10200, 220)
    contact_rim_col = lib.vector_param(m, "ContactRimColor", "Cinematic", (1.0, 0.95, 0.88, 1.0), 10200, 320)
    dist_fade_str = lib.scalar_param(m, "DistanceFadeStrength", "Cinematic", 0.0, 10200, 420)
    dist_fade_start = lib.scalar_param(m, "DistanceFadeStart", "Cinematic", 4500.0, 10200, 520)
    dist_fade_end = lib.scalar_param(m, "DistanceFadeEnd", "Cinematic", 18000.0, 10200, 620)
    atmo_fade_col = lib.vector_param(m, "AtmosphericFadeColor", "Cinematic", (0.62, 0.72, 0.82, 1.0), 10200, 720)
    dither_str = lib.scalar_param(m, "DitherDissolveStrength", "Cinematic", 0.0, 10200, 820)
    dither_edge_glow = lib.scalar_param(m, "DitherEdgeGlow", "Cinematic", 2.5, 10200, 920)

    contact_fres = lib.create_expression(m, unreal.MaterialExpressionFresnel, 10360, 120)
    wire("contact_fexp", contact_rim_pow, contact_fres, "ExponentIn")
    contact_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 10520, 120)
    wire("contact_mA", contact_fres, contact_m, "A")
    wire("contact_mB", contact_rim_str, contact_m, "B")
    contact_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 10680, 120)
    wire("contact_eA", contact_m, contact_e, "A")
    wire("contact_eB", contact_rim_col, contact_e, "B")

    cam_pos = lib.create_expression(m, unreal.MaterialExpressionCameraPositionWS, 10360, 360)
    obj_pos = lib.create_expression(m, unreal.MaterialExpressionWorldPosition, 10360, 480)
    dist_vec = lib.create_expression(m, unreal.MaterialExpressionSubtract, 10520, 420)
    wire("dist_vA", obj_pos, dist_vec, "A")
    wire("dist_vB", cam_pos, dist_vec, "B")
    dist_len = lib.create_expression(m, unreal.MaterialExpressionLength, 10680, 420)
    wire("dist_len", dist_vec, dist_len, "Input")
    dist_rng = lib.create_expression(m, unreal.MaterialExpressionSubtract, 10840, 420)
    wire("dist_rngA", dist_len, dist_rng, "A")
    wire("dist_rngB", dist_fade_start, dist_rng, "B")
    dist_span = lib.create_expression(m, unreal.MaterialExpressionSubtract, 10360, 560)
    wire("dist_spanA", dist_fade_end, dist_span, "A")
    wire("dist_spanB", dist_fade_start, dist_span, "B")
    dist_norm = lib.create_expression(m, unreal.MaterialExpressionDivide, 11000, 420)
    wire("dist_normA", dist_rng, dist_norm, "A")
    wire("dist_normB", dist_span, dist_norm, "B")
    dist_sat = lib.create_expression(m, unreal.MaterialExpressionSaturate, 11160, 420)
    wire("dist_sat", dist_norm, dist_sat, "Input")
    dist_amt = lib.create_expression(m, unreal.MaterialExpressionMultiply, 11320, 420)
    wire("dist_amtA", dist_sat, dist_amt, "A")
    wire("dist_amtB", dist_fade_str, dist_amt, "B")
    dist_col = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 11480, 400)
    wire("dist_cA", final_color, dist_col, "A")
    wire("dist_cB", atmo_fade_col, dist_col, "B")
    wire("dist_c_alpha", dist_amt, dist_col, "Alpha")
    final_color = dist_col

    pix_x = lib.create_expression(m, unreal.MaterialExpressionPixelDepth, 10360, 640)
    pix_y = lib.create_expression(m, unreal.MaterialExpressionTime, 10360, 760)
    dith_a = lib.create_expression(m, unreal.MaterialExpressionMultiply, 10520, 700)
    wire("dith_aA", pix_x, dith_a, "A")
    wire("dith_aB", const1(m, 10360, 880, 12.9898), dith_a, "B")
    dith_b = lib.create_expression(m, unreal.MaterialExpressionMultiply, 10520, 820)
    wire("dith_bA", pix_y, dith_b, "A")
    wire("dith_bB", const1(m, 10360, 960, 78.233), dith_b, "B")
    dith_add = lib.create_expression(m, unreal.MaterialExpressionAdd, 10680, 760)
    wire("dith_addA", dith_a, dith_add, "A")
    wire("dith_addB", dith_b, dith_add, "B")
    dith_sin = lib.create_expression(m, unreal.MaterialExpressionSine, 10840, 760)
    dith_sin.set_editor_property("period", 1.0)
    wire("dith_sin", dith_add, dith_sin, "Input")
    dith_abs = lib.create_expression(m, unreal.MaterialExpressionFrac, 11000, 760)
    wire("dith_frac", dith_sin, dith_abs, "Input")
    dith_sub = lib.create_expression(m, unreal.MaterialExpressionSubtract, 11160, 720)
    wire("dith_subA", mtransform, dith_sub, "A")
    wire("dith_subB", dith_abs, dith_sub, "B")
    dith_edge = lib.create_expression(m, unreal.MaterialExpressionAbs, 11320, 720)
    wire("dith_edge", dith_sub, dith_edge, "Input")
    dith_inv = lib.create_expression(m, unreal.MaterialExpressionOneMinus, 11480, 720)
    dith_edge_s = lib.create_expression(m, unreal.MaterialExpressionMultiply, 11320, 840)
    wire("dith_esA", dith_edge, dith_edge_s, "A")
    wire("dith_esB", const1(m, 11160, 940, 18.0), dith_edge_s, "B")
    wire("dith_inv_in", dith_edge_s, dith_inv, "Input")
    dith_edge_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 11640, 720)
    wire("dith_emA", dith_inv, dith_edge_m, "A")
    dith_gate = lib.create_expression(m, unreal.MaterialExpressionMultiply, 11480, 860)
    wire("dith_gA", dither_str, dith_gate, "A")
    wire("dith_gB", mtransform, dith_gate, "B")
    wire("dith_emB", dith_gate, dith_edge_m, "B")
    dith_glow = lib.create_expression(m, unreal.MaterialExpressionMultiply, 11800, 720)
    wire("dith_glA", dith_edge_m, dith_glow, "A")
    wire("dith_glB", dither_edge_glow, dith_glow, "B")
    dith_col = lib.create_expression(m, unreal.MaterialExpressionMultiply, 11960, 680)
    wire("dith_cA", final_color, dith_col, "A")
    wire("dith_cB", dith_inv, dith_col, "B")
    dith_blend = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 12120, 660)
    wire("dith_blA", final_color, dith_blend, "A")
    wire("dith_blB", dith_col, dith_blend, "B")
    wire("dith_bl_alpha", dither_str, dith_blend, "Alpha")
    final_color = dith_blend

    # character + elemental emissive additions
    char_emis_a = lib.create_expression(m, unreal.MaterialExpressionAdd, 8280, 640)
    wire("char_eA", eye_e, char_emis_a, "A")
    wire("char_eB", hair_e, char_emis_a, "B")
    char_emis_b = lib.create_expression(m, unreal.MaterialExpressionAdd, 8440, 700)
    wire("char_e2A", char_emis_a, char_emis_b, "A")
    wire("char_e2B", el_emis_e, char_emis_b, "B")
    cine_emis_a = lib.create_expression(m, unreal.MaterialExpressionAdd, 12000, 200)
    wire("cine_eA", contact_e, cine_emis_a, "A")
    wire("cine_eB", dith_glow, cine_emis_a, "B")
    emis_hoyo = lib.create_expression(m, unreal.MaterialExpressionAdd, 12160, 400)
    wire("hoyo_eA", emissive, emis_hoyo, "A")
    wire("hoyo_eB", char_emis_b, emis_hoyo, "B")
    emissive = lib.create_expression(m, unreal.MaterialExpressionAdd, 12320, 480)
    wire("hoyo_e2A", emis_hoyo, emissive, "A")
    wire("hoyo_e2B", cine_emis_a, emissive, "B")

    profiles = lib.create_toon_profiles(["TP_Default", "TP_Gold", "TP_Stone"])
    toon = lib.create_expression(m, unreal.MaterialExpressionSubstrateToonBSDF, 4040, 480)
    lib.try_set_editor_property(toon, "toon_profile", profiles.get("TP_Default"))
    if magical_mf_node:
        WIRES["toon_basecolor"] = lib.connect(magical_mf_node, "Color", toon, "BaseColor")
        WIRES["toon_emissive"] = lib.connect(
            magical_mf_node, "Emissive", toon, "Emissive Color",
        ) or lib.connect(magical_mf_node, "Emissive", toon, "EmissiveColor")
    else:
        WIRES["toon_basecolor"] = lib.connect_toon_pin(toon, final_color, ("BaseColor", "DiffuseColor"))
        WIRES["toon_emissive"] = lib.connect_toon_pin(
            toon, emissive, ("Emissive Color", "EmissiveColor", "Emissive"),
        )
    WIRES["toon_roughness"] = lib.connect_toon_pin(toon, rough_gold, ("Roughness",))
    if macro_mf_node:
        WIRES["toon_normal"] = lib.connect(macro_mf_node, "Normal", toon, "Normal") or lib.connect(
            macro_mf_node, "Normal", toon, "TangentNormal",
        )
    else:
        WIRES["toon_normal"] = lib.connect_toon_pin(toon, nrm, ("Normal", "TangentNormal", "NormalMap"))
    WIRES["toon_metallic"] = lib.connect_toon_pin(toon, metal_gold, ("Metallic", "Metalness"))
    lib.connect_front_material(m, toon)

    unreal.MaterialEditingLibrary.recompile_material(m)
    lib.save_package(m)

    import portfolio_texture_catalog as catalog

    wired_tex = catalog.apply_master_defaults(m, path, force=True)
    violations = catalog.scan_master_texture_violations(m)
    unreal.log(f"[Universal] compositing defaults wired: {len(wired_tex)} -> {list(wired_tex.keys())}")
    if violations["banned"] or violations["unwired"]:
        unreal.log_error(f"[Universal] texture violations (must fix): {violations}")

    failed = sorted(k for k, v in WIRES.items() if not v)
    unreal.log(f"[Universal] built {path}")
    unreal.log(f"[Universal] wires ok={sum(WIRES.values())}/{len(WIRES)} | failed={failed}")
    print(f"UNIVERSAL_RESULT path={path} ok={sum(WIRES.values())}/{len(WIRES)} failed={failed}")

    if not force:
        try:
            import setup_universal_instances as inst

            inst.build_instances()
        except Exception as exc:
            unreal.log_warning(f"[Universal] instances: {exc}")

    return path


if __name__ == "__main__":
    build()
