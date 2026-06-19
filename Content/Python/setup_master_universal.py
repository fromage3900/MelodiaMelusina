"""Build M_Master_Toon_Universal — the 'reach for every scene' master.

Hybrid texture/procedural, dual texture layers (A/B) with per-layer maps and parallax,
temporal boil/smear UV stylization, triplanar, Nikki dreamy glow, celestial ramps,
curvature gold leaf, fairy-dust highlight motifs, dreamy shadow tinting,
shadow-garden flowers, and metallic ORM blend — all defaulting to neutral (0).

Run (editor open):
  py "G:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_master_universal.py"
  py "G:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_master_universal.py" --force

Then instances:
  py "G:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_universal_instances.py"
"""
from __future__ import annotations

import sys

import unreal
import material_lib as lib

MASTER_NAME = "M_Master_Toon_Universal"
WAT = "/Engine/Functions/Engine_MaterialFunctions02/Texturing/WorldAlignedTexture"
WAN = "/Engine/Functions/Engine_MaterialFunctions02/Texturing/WorldAlignedNormal"

WIRES: dict[str, bool] = {}


def wire(tag, from_e, to_e, *pins) -> bool:
    for p in pins:
        if from_e is not None and lib.connect(from_e, "", to_e, p):
            WIRES[tag] = True
            return True
    WIRES[tag] = False
    return False


def const1(m, x, y, val: float = 1.0):
    c = lib.create_expression(m, unreal.MaterialExpressionConstant, x, y)
    c.set_editor_property("r", val)
    return c


def tex_object(m, name, x, y, group: str = "Textures"):
    e = lib.create_expression(m, unreal.MaterialExpressionTextureObjectParameter, x, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("group", group)
    return e


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
    wp = lib.create_expression(m, unreal.MaterialExpressionWorldPosition, x, y)
    mask = lib.create_expression(m, unreal.MaterialExpressionComponentMask, x + 160, y)
    mask.set_editor_property("r", True)
    mask.set_editor_property("g", True)
    mask.set_editor_property("b", False)
    mask.set_editor_property("a", False)
    wire("wxy_wp", wp, mask, "")
    return mask


def style_peak(m, style, target: float, tag: str, x, y):
    """Weight ~1 when style scalar equals target, ~0 elsewhere."""
    tgt = const1(m, x, y, target)
    sub = lib.create_expression(m, unreal.MaterialExpressionSubtract, x + 120, y)
    wire(f"{tag}_subA", style, sub, "A")
    wire(f"{tag}_subB", tgt, sub, "B")
    ab = lib.create_expression(m, unreal.MaterialExpressionAbs, x + 260, y)
    wire(f"{tag}_abs", sub, ab, "Input")
    scale = const1(m, x + 120, y + 80, 2.0)
    sc = lib.create_expression(m, unreal.MaterialExpressionMultiply, x + 400, y)
    wire(f"{tag}_scA", ab, sc, "A")
    wire(f"{tag}_scB", scale, sc, "B")
    inv = lib.create_expression(m, unreal.MaterialExpressionOneMinus, x + 540, y)
    wire(f"{tag}_inv", sc, inv, "Input")
    return inv


def scalar_switch(m, name, group, x, y, default=False):
    return static_switch(m, name, group, x, y, default)


def apply_temporal_uv(m, uv, temporal_str, wind, noise_scale, smear, boil, tag: str):
    """World-space boil/smear offset on UVs (strength 0 = passthrough)."""
    wxy = world_xy(m, -2400, 6200)
    t = lib.create_expression(m, unreal.MaterialExpressionTime, -2400, 6320)
    wind_t = lib.create_expression(m, unreal.MaterialExpressionMultiply, -2240, 6320)
    wire(f"{tag}_wtA", t, wind_t, "A")
    wire(f"{tag}_wtB", wind, wind_t, "B")
    nscale = lib.create_expression(m, unreal.MaterialExpressionMultiply, -2240, 6200)
    wire(f"{tag}_nsA", wxy, nscale, "A")
    wire(f"{tag}_nsB", noise_scale, nscale, "B")
    phase = lib.create_expression(m, unreal.MaterialExpressionAdd, -2080, 6260)
    wire(f"{tag}_phA", nscale, phase, "A")
    wire(f"{tag}_phB", wind_t, phase, "B")
    s = lib.create_expression(m, unreal.MaterialExpressionSine, -1920, 6260)
    s.set_editor_property("period", 1.0)
    wire(f"{tag}_sin", phase, s, "Input")
    boil_off = lib.create_expression(m, unreal.MaterialExpressionMultiply, -1760, 6260)
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


def parallax_uv_offset(m, uv, height_tex, scale, strength, tag: str):
    """Height-map POM proxy: offset UV before map samples."""
    h_s = lib.create_expression(m, unreal.MaterialExpressionTextureSample, -2400, 6600)
    wire(f"{tag}_h_obj", height_tex, h_s, "Tex", "TextureObject")
    wire(f"{tag}_h_uv", uv, h_s, "UVs", "Coordinates")
    h_r = lib.create_expression(m, unreal.MaterialExpressionComponentMask, -2240, 6600)
    h_r.set_editor_property("r", True)
    h_r.set_editor_property("g", False)
    h_r.set_editor_property("b", False)
    h_r.set_editor_property("a", False)
    wire(f"{tag}_h_r", h_s, h_r, "")
    view = lib.create_expression(m, unreal.MaterialExpressionCameraVectorWS, -2400, 6720)
    view_xy = lib.create_expression(m, unreal.MaterialExpressionComponentMask, -2240, 6720)
    view_xy.set_editor_property("r", True)
    view_xy.set_editor_property("g", True)
    view_xy.set_editor_property("b", False)
    view_xy.set_editor_property("a", False)
    wire(f"{tag}_vxy", view, view_xy, "")
    pom_s = lib.create_expression(m, unreal.MaterialExpressionMultiply, -2080, 6660)
    wire(f"{tag}_psA", h_r, pom_s, "A")
    wire(f"{tag}_psB", scale, pom_s, "B")
    pom_s2 = lib.create_expression(m, unreal.MaterialExpressionMultiply, -1920, 6660)
    wire(f"{tag}_ps2A", pom_s, pom_s2, "A")
    wire(f"{tag}_ps2B", strength, pom_s2, "B")
    off = lib.create_expression(m, unreal.MaterialExpressionMultiply, -1760, 6660)
    wire(f"{tag}_offA", pom_s2, off, "A")
    wire(f"{tag}_offB", view_xy, off, "B")
    out = lib.create_expression(m, unreal.MaterialExpressionAdd, -1600, 6620)
    wire(f"{tag}_pA", uv, out, "A")
    wire(f"{tag}_pB", off, out, "B")
    return out


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
        wire(f"{tt}_true", tri_e or uv_e, sw, "A", "True")
        wire(f"{tt}_false", uv_e, sw, "B", "False")
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
    force = "--force" in sys.argv
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

    # ---- Layer B (overlay) texture set ----
    alb_b = tex_object(m, "LayerB_Albedo", -2100, 1280, "LayerB")
    nrm_b = tex_object(m, "LayerB_NormalMap", -2100, 1440, "LayerB")
    orm_b = tex_object(m, "LayerB_ORM", -2100, 1600, "LayerB")
    height_b = tex_object(m, "LayerB_HeightMap", -2100, 1760, "LayerB")
    layer_b_weight = lib.scalar_param(m, "LayerB_TextureWeight", "LayerB", 1.0, -2100, 1880)
    layer_b_parallax = lib.scalar_param(m, "LayerB_ParallaxScale", "LayerB", 1.0, -2100, 1980)
    layer_blend = lib.scalar_param(m, "LayerBlend", "Layers", 0.0, -2100, 2100)

    # ---- Parallax (shared + per-layer) ----
    parallax_scale = lib.scalar_param(m, "ParallaxScale", "Parallax", 0.04, -2100, 2320)
    parallax_str = lib.scalar_param(m, "ParallaxStrength", "Parallax", 0.0, -2100, 2420)
    parallax_steps = lib.scalar_param(m, "ParallaxSteps", "Parallax", 8.0, -2100, 2520)

    # ---- Temporal stylization ----
    temporal_str = lib.scalar_param(m, "TemporalStrength", "Temporal", 0.0, -2100, 2740)
    wind_speed = lib.scalar_param(m, "WindSpeed", "Temporal", 0.12, -2100, 2840)
    temporal_noise = lib.scalar_param(m, "NoiseScale", "Temporal", 1.5, -2100, 2940)
    smear_str = lib.scalar_param(m, "SmearStrength", "Temporal", 0.08, -2100, 3040)
    boil_int = lib.scalar_param(m, "BoilIntensity", "Temporal", 0.05, -2100, 3140)

    # ---- UV + temporal ----
    tc = lib.create_expression(m, unreal.MaterialExpressionTextureCoordinate, -1800, 460)
    uv = lib.create_expression(m, unreal.MaterialExpressionMultiply, -1620, 460)
    wire("uv_tc", tc, uv, "A")
    wire("uv_scale", uv_scale, uv, "B")
    uv_time = apply_temporal_uv(
        m, uv, temporal_str, wind_speed, temporal_noise, smear_str, boil_int, "temporal"
    )

    # Parallax per layer (strength gated)
    pom_a = parallax_uv_offset(m, uv_time, height_a, parallax_scale, layer_a_parallax, "pomA")
    pom_b = parallax_uv_offset(m, uv_time, height_b, parallax_scale, layer_b_parallax, "pomB")
    uv_a = lerp3(m, uv_time, pom_a, parallax_str, "uv_pomA", -1480, 480)
    uv_b = lerp3(m, uv_time, pom_b, parallax_str, "uv_pomB", -1480, 1280)

    alb_a, nrm_a, orm_a = sample_maps_uv(m, uv_a, albedo, normal, orm, tri_tiling, "layA", 480)
    alb_b_s, nrm_b_s, orm_b_s = sample_maps_uv(m, uv_b, alb_b, nrm_b, orm_b, tri_tiling, "layB", 1280)

    alb_blend = lerp3(m, alb_a, alb_b_s, layer_blend, "alb_lerp", -680, 520)
    nrm_blend = lerp3(m, nrm_a, nrm_b_s, layer_blend, "nrm_lerp", -680, 680)
    orm_blend = lerp3(m, orm_a, orm_b_s, layer_blend, "orm_lerp", -680, 840)

    alb = alb_blend
    nrm_s = nrm_blend
    orm_s = orm_blend

    # Per-layer texture weights into hybrid
    tex_a_w = lib.create_expression(m, unreal.MaterialExpressionMultiply, -360, 120)
    wire("tawA", tex_weight, tex_a_w, "A")
    wire("tawB", layer_a_weight, tex_a_w, "B")
    tex_b_w = lib.create_expression(m, unreal.MaterialExpressionMultiply, -360, 240)
    wire("tbwA", tex_weight, tex_b_w, "A")
    wire("tbwB", layer_b_weight, tex_b_w, "B")
    tex_eff = lerp3(m, tex_a_w, tex_b_w, layer_blend, "tex_eff", -200, 180)

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

    # ---- Nikki dreamy layer ----
    rim_color = lib.vector_param(m, "RimColor", "Nikki", (0.70, 0.85, 1.00, 1.0), -2100, 1040)
    rim_power = lib.scalar_param(m, "RimPower", "Nikki", 3.0, -2100, 1140)
    rim_int = lib.scalar_param(m, "RimIntensity", "Nikki", 0.0, -2100, 1240)
    dream_tint = lib.vector_param(m, "DreamTint", "Nikki", (1.00, 0.85, 0.92, 1.0), -2100, 1340)
    pastel = lib.scalar_param(m, "PastelLift", "Nikki", 0.0, -2100, 1440)
    irid = lib.scalar_param(m, "Iridescence", "Nikki", 0.0, -2100, 1540)
    irid_tint = lib.vector_param(m, "IridescenceTint", "Nikki", (0.80, 0.60, 1.00, 1.0), -2100, 1640)
    spark_mask = lib.texture_param(m, "SparkleMask", "Nikki", -2100, 1740)
    spark_scale = lib.scalar_param(m, "SparkleScale", "Nikki", 8.0, -2100, 1840)
    spark_int = lib.scalar_param(m, "SparkleIntensity", "Nikki", 0.0, -2100, 1940)
    spark_color = lib.vector_param(m, "SparkleColor", "Nikki", (1.00, 0.95, 0.80, 1.0), -2100, 2040)
    glow_color = lib.vector_param(m, "GlowColor", "Nikki", (1.00, 0.90, 0.95, 1.0), -2100, 2140)
    glow_int = lib.scalar_param(m, "GlowIntensity", "Nikki", 0.0, -2100, 2240)
    rim_soft = lib.scalar_param(m, "RimSoftness", "Nikki", 0.35, -2100, 2340)
    inner_glow = lib.scalar_param(m, "InnerGlowIntensity", "Nikki", 0.0, -2100, 2440)
    inner_color = lib.vector_param(m, "InnerGlowColor", "Nikki", (1.00, 0.92, 0.98, 1.0), -2100, 2540)
    bloom = lib.scalar_param(m, "BloomBoost", "Nikki", 0.0, -2100, 2640)
    sheen = lib.scalar_param(m, "FabricSheen", "Nikki", 0.0, -2100, 2740)
    sheen_tint = lib.vector_param(m, "SheenTint", "Nikki", (1.00, 1.00, 1.00, 1.0), -2100, 2840)
    sheen_power = lib.scalar_param(m, "SheenPower", "Nikki", 6.0, -2100, 2940)

    # ---- Celestial ramps (dark stars / nebula mid / galaxy highlight) ----
    const_low = lib.vector_param(m, "ConstellationRampLow", "Celestial", (0.02, 0.03, 0.10, 1.0), -2100, 3060)
    const_mid = lib.vector_param(m, "ConstellationRampMid", "Celestial", (0.45, 0.22, 0.55, 1.0), -2100, 3160)
    const_high = lib.vector_param(m, "ConstellationRampHigh", "Celestial", (0.85, 0.72, 1.00, 1.0), -2100, 3260)
    const_str = lib.scalar_param(m, "ConstellationStrength", "Celestial", 0.0, -2100, 3360)
    const_scale = lib.scalar_param(m, "ConstellationScale", "Celestial", 1.8, -2100, 3460)
    const_phase = lib.scalar_param(m, "ConstellationPhase", "Celestial", 0.0, -2100, 3560)
    star_int = lib.scalar_param(m, "CelestialStarIntensity", "Celestial", 1.0, -2100, 3660)
    star_twinkle = lib.scalar_param(m, "CelestialTwinkle", "Celestial", 0.0, -2100, 3760)
    nebula_str = lib.scalar_param(m, "CelestialNebulaStrength", "Celestial", 0.65, -2100, 3860)
    nebula_scale = lib.scalar_param(m, "CelestialNebulaScale", "Celestial", 0.35, -2100, 3960)
    galaxy_str = lib.scalar_param(m, "CelestialGalaxyStrength", "Celestial", 0.45, -2100, 4060)
    galaxy_scale = lib.scalar_param(m, "CelestialGalaxyScale", "Celestial", 0.12, -2100, 4160)
    galaxy_arms = lib.scalar_param(m, "CelestialGalaxyArms", "Celestial", 3.0, -2100, 4260)

    # ---- Gold leaf on curvature ----
    gild_str = lib.scalar_param(m, "GildingStrength", "Gilding", 0.0, -2100, 4380)
    gold_tint = lib.vector_param(m, "GoldTint", "Gilding", (0.92, 0.72, 0.28, 1.0), -2100, 4480)
    gold_rough = lib.scalar_param(m, "GoldRoughness", "Gilding", 0.18, -2100, 4580)
    gold_emis = lib.vector_param(m, "GoldEmissive", "Gilding", (0.35, 0.25, 0.05, 1.0), -2100, 4680)
    curve_sens = lib.scalar_param(m, "CurvatureSensitivity", "Gilding", 2.5, -2100, 4780)

    # ---- Dreamy shadows + shadow garden ----
    shadow_tint = lib.vector_param(m, "ShadowDreamTint", "ShadowDream", (0.48, 0.42, 0.62, 1.0), -2100, 4900)
    shadow_str = lib.scalar_param(m, "ShadowDreamStrength", "ShadowDream", 0.0, -2100, 5000)
    shadow_soft = lib.scalar_param(m, "ShadowSoftness", "ShadowDream", 0.5, -2100, 5100)
    flower_str = lib.scalar_param(m, "ShadowFlowerStrength", "ShadowGarden", 0.0, -2100, 5220)
    flower_scale = lib.scalar_param(m, "ShadowFlowerScale", "ShadowGarden", 5.0, -2100, 5320)
    flower_color = lib.vector_param(m, "ShadowFlowerColor", "ShadowGarden", (0.92, 0.45, 0.72, 1.0), -2100, 5420)

    # ---- Fairy dust motifs (0=off, 1=heart, 2=star, 3=flower, 4=moon) ----
    fairy_style = lib.scalar_param(m, "FairyMotifStyle", "FairyDust", 0.0, -2100, 5540)
    fairy_int = lib.scalar_param(m, "FairyDustIntensity", "FairyDust", 0.0, -2100, 5640)
    fairy_scale = lib.scalar_param(m, "FairyDustScale", "FairyDust", 14.0, -2100, 5740)
    fairy_color = lib.vector_param(m, "FairyDustColor", "FairyDust", (1.0, 0.92, 0.98, 1.0), -2100, 5840)
    fairy_thresh = lib.scalar_param(m, "FairyHighlightThreshold", "FairyDust", 0.35, -2100, 5940)
    fairy_glyph = lib.texture_param(m, "FairyGlyphMask", "FairyDust", -2100, 6040)

    color_nikki = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 220, 120)
    wire("nikki_base_A", color, color_nikki, "A")
    wire("nikki_base_B", dream_tint, color_nikki, "B")
    wire("nikki_base_alpha", pastel, color_nikki, "Alpha")

    # ---- celestial: tier 1 stars on dark void, tier 2 nebula wash, tier 3 galaxy core ----
    wxy = world_xy(m, 220, 300)
    const_mul = lib.create_expression(m, unreal.MaterialExpressionMultiply, 400, 300)
    wire("const_mulA", wxy, const_mul, "A")
    wire("const_mulB", const_scale, const_mul, "B")
    phase_add = lib.create_expression(m, unreal.MaterialExpressionAdd, 560, 300)
    wire("phase_A", const_mul, phase_add, "A")
    wire("phase_B", const_phase, phase_add, "B")
    frac_n = lib.create_expression(m, unreal.MaterialExpressionFrac, 720, 300)
    wire("frac_in", phase_add, frac_n, "Input")
    star_dist = lib.create_expression(m, unreal.MaterialExpressionDistance, 900, 300)
    star_ctr = lib.create_expression(m, unreal.MaterialExpressionConstant2Vector, 720, 420)
    star_ctr.set_editor_property("r", 0.5)
    star_ctr.set_editor_property("g", 0.5)
    wire("dist_A", frac_n, star_dist, "A")
    wire("dist_B", star_ctr, star_dist, "B")
    star_inv = lib.create_expression(m, unreal.MaterialExpressionOneMinus, 1080, 300)
    wire("star_inv", star_dist, star_inv, "Input")
    star_pow = lib.create_expression(m, unreal.MaterialExpressionPower, 1240, 300)
    wire("star_powA", star_inv, star_pow, "Base")
    three = const1(m, 1080, 420, 3.5)
    wire("star_powB", three, star_pow, "Exp")
    time_n = lib.create_expression(m, unreal.MaterialExpressionTime, 720, 520)
    twinkle_ph = lib.create_expression(m, unreal.MaterialExpressionMultiply, 880, 520)
    wire("twinkle_t", time_n, twinkle_ph, "A")
    wire("twinkle_s", star_twinkle, twinkle_ph, "B")
    twinkle_sin = lib.create_expression(m, unreal.MaterialExpressionSine, 1040, 520)
    twinkle_sin.set_editor_property("period", 1.0)
    wire("twinkle_sin", twinkle_ph, twinkle_sin, "Input")
    twinkle = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1200, 400)
    wire("twinkleA", star_pow, twinkle, "A")
    twinkle_mod = lib.create_expression(m, unreal.MaterialExpressionAdd, 1040, 620)
    wire("tw_modA", twinkle_sin, twinkle_mod, "A")
    wire("tw_modB", const1(m, 880, 620, 0.65), twinkle_mod, "B")
    wire("twinkleB", twinkle_mod, twinkle, "B")
    star_pts = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1360, 360)
    wire("star_ptsA", twinkle, star_pts, "A")
    wire("star_ptsB", star_int, star_pts, "B")
    star_col = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 1540, 280)
    wire("star_cA", const_low, star_col, "A")
    wire("star_cB", const_high, star_col, "B")
    wire("star_c_alpha", star_pts, star_col, "Alpha")

    # nebula: soft multi-frequency sine clouds in world XY
    neb_mul = lib.create_expression(m, unreal.MaterialExpressionMultiply, 400, 680)
    wire("neb_mulA", wxy, neb_mul, "A")
    wire("neb_mulB", nebula_scale, neb_mul, "B")
    neb_sx = lib.create_expression(m, unreal.MaterialExpressionSine, 560, 640)
    neb_sx.set_editor_property("period", 1.0)
    wire("neb_sx", neb_mul, neb_sx, "Input")
    neb_sy = lib.create_expression(m, unreal.MaterialExpressionSine, 560, 760)
    neb_sy.set_editor_property("period", 1.0)
    neb_mul2 = lib.create_expression(m, unreal.MaterialExpressionMultiply, 400, 820)
    wire("neb2A", neb_mul, neb_mul2, "A")
    wire("neb2B", const1(m, 400, 900, 1.73), neb_mul2, "B")
    wire("neb_sy", neb_mul2, neb_sy, "Input")
    neb_prod = lib.create_expression(m, unreal.MaterialExpressionMultiply, 720, 700)
    wire("neb_pA", neb_sx, neb_prod, "A")
    wire("neb_pB", neb_sy, neb_prod, "B")
    neb_abs = lib.create_expression(m, unreal.MaterialExpressionAbs, 880, 700)
    wire("neb_abs", neb_prod, neb_abs, "Input")
    neb_soft = lib.create_expression(m, unreal.MaterialExpressionPower, 1040, 700)
    wire("neb_softA", neb_abs, neb_soft, "Base")
    wire("neb_softB", const1(m, 880, 800, 0.55), neb_soft, "Exp")
    neb_w = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1200, 700)
    wire("neb_wA", neb_soft, neb_w, "A")
    wire("neb_wB", nebula_str, neb_w, "B")
    nebula_col = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 1380, 520)
    wire("neb_cA", star_col, nebula_col, "A")
    wire("neb_cB", const_mid, nebula_col, "B")
    wire("neb_c_alpha", neb_w, nebula_col, "Alpha")

    # galaxy: radial core + spiral arm proxy
    gal_mul = lib.create_expression(m, unreal.MaterialExpressionMultiply, 400, 980)
    wire("gal_mulA", wxy, gal_mul, "A")
    wire("gal_mulB", galaxy_scale, gal_mul, "B")
    gal_len = lib.create_expression(m, unreal.MaterialExpressionLength, 560, 980)
    wire("gal_len", gal_mul, gal_len, "Input")
    gal_fall = lib.create_expression(m, unreal.MaterialExpressionOneMinus, 720, 980)
    wire("gal_fall_in", gal_len, gal_fall, "Input")
    gal_rad = lib.create_expression(m, unreal.MaterialExpressionPower, 880, 980)
    wire("gal_radA", gal_fall, gal_rad, "Base")
    wire("gal_radB", const1(m, 720, 1080, 1.8), gal_rad, "Exp")
    gal_x = lib.create_expression(m, unreal.MaterialExpressionComponentMask, 560, 1100)
    gal_x.set_editor_property("r", True)
    gal_x.set_editor_property("g", False)
    gal_x.set_editor_property("b", False)
    gal_x.set_editor_property("a", False)
    wire("gal_x", gal_mul, gal_x, "")
    gal_y = lib.create_expression(m, unreal.MaterialExpressionComponentMask, 560, 1180)
    gal_y.set_editor_property("r", False)
    gal_y.set_editor_property("g", True)
    gal_y.set_editor_property("b", False)
    gal_y.set_editor_property("a", False)
    wire("gal_y", gal_mul, gal_y, "")
    gal_spiral = lib.create_expression(m, unreal.MaterialExpressionSine, 720, 1140)
    gal_spiral.set_editor_property("period", 1.0)
    gal_ang = lib.create_expression(m, unreal.MaterialExpressionMultiply, 560, 1260)
    wire("gal_angA", gal_x, gal_ang, "A")
    wire("gal_angB", galaxy_arms, gal_ang, "B")
    gal_phase = lib.create_expression(m, unreal.MaterialExpressionAdd, 720, 1220)
    wire("gal_phA", gal_ang, gal_phase, "A")
    wire("gal_phB", gal_len, gal_phase, "B")
    wire("gal_spiral_in", gal_phase, gal_spiral, "Input")
    gal_arm = lib.create_expression(m, unreal.MaterialExpressionAbs, 880, 1140)
    wire("gal_arm", gal_spiral, gal_arm, "Input")
    gal_core = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1040, 1060)
    wire("gal_cA", gal_rad, gal_core, "A")
    wire("gal_cB", gal_arm, gal_core, "B")
    gal_w = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1200, 1060)
    wire("gal_wA", gal_core, gal_w, "A")
    wire("gal_wB", galaxy_str, gal_w, "B")
    celestial = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 1380, 900)
    wire("cel_A", nebula_col, celestial, "A")
    wire("cel_B", const_high, celestial, "B")
    wire("cel_alpha", gal_w, celestial, "Alpha")
    color_stars = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 1780, 120)
    wire("stars_A", color_nikki, color_stars, "A")
    wire("stars_B", celestial, color_stars, "B")
    wire("stars_alpha", const_str, color_stars, "Alpha")

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

    # dreamy shadow tint (N·L proxy)
    light_dir = lib.create_expression(m, unreal.MaterialExpressionConstant3Vector, 220, 760)
    light_dir.set_editor_property("constant", unreal.LinearColor(0.35, 0.55, 0.85, 1.0))
    ndotl = lib.create_expression(m, unreal.MaterialExpressionDotProduct, 400, 760)
    wire("ndotl_A", pnormal, ndotl, "A")
    wire("ndotl_B", light_dir, ndotl, "B")
    shadow_raw = lib.create_expression(m, unreal.MaterialExpressionOneMinus, 560, 760)
    wire("shadow_raw", ndotl, shadow_raw, "Input")
    soft_exp = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 720, 860)
    wire("soft_A", const1(m, 560, 900, 1.0), soft_exp, "A")
    wire("soft_B", const1(m, 560, 980, 4.0), soft_exp, "B")
    wire("soft_alpha", shadow_soft, soft_exp, "Alpha")
    shadow_pow = lib.create_expression(m, unreal.MaterialExpressionPower, 880, 760)
    wire("shadow_powA", shadow_raw, shadow_pow, "Base")
    wire("shadow_powB", soft_exp, shadow_pow, "Exp")
    shadow_amt = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1040, 760)
    wire("shadow_amtA", shadow_pow, shadow_amt, "A")
    wire("shadow_amtB", shadow_str, shadow_amt, "B")
    final_color = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 1420, 120)
    wire("dream_A", color_gold, final_color, "A")
    wire("dream_B", shadow_tint, final_color, "B")
    wire("dream_alpha", shadow_amt, final_color, "Alpha")

    # shadow garden flowers (world clover in shadow)
    flower_uv = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1220, 900)
    wire("fl_uvA", wxy, flower_uv, "A")
    wire("fl_uvB", flower_scale, flower_uv, "B")
    petal_x = lib.create_expression(m, unreal.MaterialExpressionSine, 1400, 860)
    petal_x.set_editor_property("period", 1.0)
    wire("petal_x", flower_uv, petal_x, "Input")
    petal_y = lib.create_expression(m, unreal.MaterialExpressionSine, 1400, 980)
    petal_y.set_editor_property("period", 1.0)
    flower_uv2 = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1400, 920)
    wire("fl2A", flower_uv, flower_uv2, "A")
    const_swap = const1(m, 1220, 1040, 0.7)
    wire("fl2B", const_swap, flower_uv2, "B")
    wire("petal_y_in", flower_uv2, petal_y, "Input")
    petal = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1580, 920)
    wire("petalA", petal_x, petal, "A")
    wire("petalB", petal_y, petal, "B")
    petal_abs = lib.create_expression(m, unreal.MaterialExpressionAbs, 1740, 920)
    wire("petal_abs", petal, petal_abs, "Input")
    flower_mask = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1900, 900)
    wire("fl_maskA", shadow_amt, flower_mask, "A")
    wire("fl_maskB", petal_abs, flower_mask, "B")
    flower_w = lib.create_expression(m, unreal.MaterialExpressionMultiply, 2060, 900)
    wire("fl_wA", flower_mask, flower_w, "A")
    wire("fl_wB", flower_str, flower_w, "B")
    flower_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 2220, 900)
    wire("fl_eA", flower_w, flower_e, "A")
    wire("fl_eB", flower_color, flower_e, "B")

    # fresnel + Nikki emissive stack
    fres = lib.create_expression(m, unreal.MaterialExpressionFresnel, 220, 1100)
    wire("fresnel_exp", rim_power, fres, "ExponentIn")
    rim_soft_m = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 220, 1180)
    wire("rim_soft_A", fres, rim_soft_m, "A")
    rim_inv = lib.create_expression(m, unreal.MaterialExpressionOneMinus, 60, 1240)
    wire("rim_soft_inv", rim_soft, rim_inv, "Input")
    rim_soft_b = lib.create_expression(m, unreal.MaterialExpressionMultiply, 60, 1300)
    wire("rim_soft_bA", fres, rim_soft_b, "A")
    wire("rim_soft_bB", rim_inv, rim_soft_b, "B")
    wire("rim_soft_alpha", rim_soft, rim_soft_m, "Alpha")
    wire("rim_soft_B", rim_soft_b, rim_soft_m, "B")
    rim_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 400, 1100)
    wire("rim_mA", rim_soft_m, rim_m, "A")
    wire("rim_mB", rim_int, rim_m, "B")
    rim_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 580, 1100)
    wire("rim_eA", rim_m, rim_e, "A")
    wire("rim_eB", rim_color, rim_e, "B")
    irid_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 400, 1280)
    wire("irid_mA", rim_soft_m, irid_m, "A")
    wire("irid_mB", irid, irid_m, "B")
    irid_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 580, 1280)
    wire("irid_eA", irid_m, irid_e, "A")
    wire("irid_eB", irid_tint, irid_e, "B")

    spark_uv = lib.create_expression(m, unreal.MaterialExpressionMultiply, 220, 1420)
    wire("spark_uvA", uv, spark_uv, "A")
    wire("spark_uvB", spark_scale, spark_uv, "B")
    wire("spark_mask_uv", spark_uv, spark_mask, "UVs", "Coordinates")
    spark_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 400, 1420)
    wire("spark_mA", spark_mask, spark_m, "A")
    wire("spark_mB", spark_int, spark_m, "B")
    spark_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 580, 1420)
    wire("spark_eA", spark_m, spark_e, "A")
    wire("spark_eB", spark_color, spark_e, "B")

    glow_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 400, 1580)
    wire("glow_eA", glow_color, glow_e, "A")
    wire("glow_eB", glow_int, glow_e, "B")

    inner_inv = lib.create_expression(m, unreal.MaterialExpressionOneMinus, 220, 1280)
    wire("inner_inv", rim_soft_m, inner_inv, "Input")
    inner_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 400, 1360)
    wire("inner_mA", inner_inv, inner_m, "A")
    wire("inner_mB", inner_glow, inner_m, "B")
    inner_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 580, 1360)
    wire("inner_eA", inner_m, inner_e, "A")
    wire("inner_eB", inner_color, inner_e, "B")

    sheen_f = lib.create_expression(m, unreal.MaterialExpressionFresnel, 220, 1520)
    wire("sheen_exp", sheen_power, sheen_f, "ExponentIn")
    sheen_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 400, 1520)
    wire("sheen_mA", sheen_f, sheen_m, "A")
    wire("sheen_mB", sheen, sheen_m, "B")
    sheen_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 580, 1520)
    wire("sheen_eA", sheen_m, sheen_e, "A")
    wire("sheen_eB", sheen_tint, sheen_e, "B")

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
    wire("star_sx", fairy_uv, star_sx, "Input")
    star_sy = lib.create_expression(m, unreal.MaterialExpressionSine, 400, 1880)
    star_sy.set_editor_property("period", 5.0)
    fairy_uv_y = lib.create_expression(m, unreal.MaterialExpressionComponentMask, 220, 1880)
    fairy_uv_y.set_editor_property("r", False)
    fairy_uv_y.set_editor_property("g", True)
    fairy_uv_y.set_editor_property("b", False)
    fairy_uv_y.set_editor_property("a", False)
    wire("fuv_y", fairy_uv, fairy_uv_y, "")
    wire("star_sy", fairy_uv_y, star_sy, "Input")
    star_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 560, 1820)
    wire("star_mA", star_sx, star_m, "A")
    wire("star_mB", star_sy, star_m, "B")
    star_abs = lib.create_expression(m, unreal.MaterialExpressionAbs, 720, 1820)
    wire("star_abs", star_m, star_abs, "Input")
    # flower motif for fairy dust (separate from shadow-garden petals)
    fairy_px = lib.create_expression(m, unreal.MaterialExpressionSine, 400, 1960)
    fairy_px.set_editor_property("period", 1.0)
    wire("fairy_px", fairy_uv, fairy_px, "Input")
    fairy_py = lib.create_expression(m, unreal.MaterialExpressionSine, 400, 2080)
    fairy_py.set_editor_property("period", 1.0)
    fairy_uv_y2 = lib.create_expression(m, unreal.MaterialExpressionComponentMask, 220, 2080)
    fairy_uv_y2.set_editor_property("r", False)
    fairy_uv_y2.set_editor_property("g", True)
    fairy_uv_y2.set_editor_property("b", False)
    fairy_uv_y2.set_editor_property("a", False)
    wire("fuv_y2", fairy_uv, fairy_uv_y2, "")
    wire("fairy_py", fairy_uv_y2, fairy_py, "Input")
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
    # optional glyph texture overlay
    wire("glyph_uv", fairy_uv, fairy_glyph, "UVs", "Coordinates")
    motif_tex = lib.create_expression(m, unreal.MaterialExpressionAdd, 1700, 1820)
    wire("motif_texA", motif, motif_tex, "A")
    wire("motif_texB", fairy_glyph, motif_tex, "B")
    highlight = lib.create_expression(m, unreal.MaterialExpressionSubtract, 1220, 1580)
    wire("hl_A", rim_soft_m, highlight, "A")
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
    emissive_raw = lib.create_expression(m, unreal.MaterialExpressionAdd, 3520, 1760)
    wire("emi8A", a7, emissive_raw, "A")
    wire("emi8B", flower_e, emissive_raw, "B")
    bloom_m = lib.create_expression(m, unreal.MaterialExpressionAdd, 3680, 1760)
    wire("bloom_add_A", const1(m, 3520, 1860, 1.0), bloom_m, "A")
    wire("bloom_add_B", bloom, bloom_m, "B")
    emissive = lib.create_expression(m, unreal.MaterialExpressionMultiply, 3840, 1760)
    wire("bloom_mul_A", emissive_raw, emissive, "A")
    wire("bloom_mul_B", bloom_m, emissive, "B")

    # ---- Macro variation + detail (group 'MacroDetail', defaults neutral) ----
    macro_str = lib.scalar_param(m, "MacroVariationStrength", "MacroDetail", 0.0, 3600, 120)
    macro_scale = lib.scalar_param(m, "MacroScale", "MacroDetail", 0.0008, 3600, 200)
    det_tex = tex_object(m, "DetailNormal", 3600, 280, "MacroDetail")
    det_tiling = lib.scalar_param(m, "DetailTiling", "MacroDetail", 8.0, 3600, 440)
    det_str = lib.scalar_param(m, "DetailStrength", "MacroDetail", 0.0, 3600, 520)
    # macro: low-freq world noise -> subtle albedo brightness/tint variation (kills tiling)
    mac_wp = lib.create_expression(m, unreal.MaterialExpressionWorldPosition, 3600, 620)
    mac_scl = lib.create_expression(m, unreal.MaterialExpressionMultiply, 3760, 620)
    wire("mac_wpA", mac_wp, mac_scl, "A"); wire("mac_wpB", macro_scale, mac_scl, "B")
    mac_noise = lib.create_expression(m, unreal.MaterialExpressionNoise, 3920, 620)
    wire("mac_noise_pos", mac_scl, mac_noise, "Position", "")
    mac_sub = lib.create_expression(m, unreal.MaterialExpressionSubtract, 4080, 620)
    wire("mac_subA", mac_noise, mac_sub, "A"); wire("mac_subB", const1(m, 3920, 720, 0.5), mac_sub, "B")
    mac_amt = lib.create_expression(m, unreal.MaterialExpressionMultiply, 4240, 620)
    wire("mac_amtA", mac_sub, mac_amt, "A"); wire("mac_amtB", macro_str, mac_amt, "B")
    mac_fac = lib.create_expression(m, unreal.MaterialExpressionAdd, 4400, 600)
    wire("mac_facA", const1(m, 4240, 720, 1.0), mac_fac, "A"); wire("mac_facB", mac_amt, mac_fac, "B")
    color_macro = lib.create_expression(m, unreal.MaterialExpressionMultiply, 4560, 480)
    wire("mac_colA", final_color, color_macro, "A"); wire("mac_colB", mac_fac, color_macro, "B")
    final_color = color_macro
    # detail normal: high-freq tiled normal blended into nrm
    det_tc = lib.create_expression(m, unreal.MaterialExpressionTextureCoordinate, 3600, 900)
    det_uv = lib.create_expression(m, unreal.MaterialExpressionMultiply, 3760, 900)
    wire("det_uvA", det_tc, det_uv, "A"); wire("det_uvB", det_tiling, det_uv, "B")
    det_s = lib.create_expression(m, unreal.MaterialExpressionTextureSample, 3920, 900)
    lib.try_set_editor_property(det_s, "sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    wire("det_obj", det_tex, det_s, "Tex", "TextureObject")
    wire("det_uv", det_uv, det_s, "UVs", "Coordinates")
    nrm_det = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 4240, 900)
    wire("ndA", nrm, nrm_det, "A"); wire("ndB", det_s, nrm_det, "B"); wire("ndAlpha", det_str, nrm_det, "Alpha")
    nrm = nrm_det

    profiles = lib.create_toon_profiles(["TP_Default", "TP_Gold", "TP_Stone"])
    toon = lib.create_expression(m, unreal.MaterialExpressionSubstrateToonBSDF, 4040, 480)
    lib.try_set_editor_property(toon, "toon_profile", profiles.get("TP_Default"))
    WIRES["toon_basecolor"] = lib.connect_toon_pin(toon, final_color, ("BaseColor", "DiffuseColor"))
    WIRES["toon_roughness"] = lib.connect_toon_pin(toon, rough_gold, ("Roughness",))
    WIRES["toon_normal"] = lib.connect_toon_pin(toon, nrm, ("Normal", "TangentNormal", "NormalMap"))
    WIRES["toon_metallic"] = lib.connect_toon_pin(toon, metal_gold, ("Metallic", "Metalness"))
    WIRES["toon_emissive"] = lib.connect_toon_pin(toon, emissive, ("Emissive Color", "EmissiveColor", "Emissive"))
    lib.connect_front_material(m, toon)

    unreal.MaterialEditingLibrary.recompile_material(m)
    lib.save_package(m)

    failed = sorted(k for k, v in WIRES.items() if not v)
    unreal.log(f"[Universal] built {path}")
    unreal.log(f"[Universal] wires ok={sum(WIRES.values())}/{len(WIRES)} | failed={failed}")
    print(f"UNIVERSAL_RESULT path={path} ok={sum(WIRES.values())}/{len(WIRES)} failed={failed}")

    try:
        import setup_universal_instances as inst
        inst.build_instances()
    except Exception as exc:
        unreal.log_warning(f"[Universal] instances: {exc}")

    return path


if __name__ == "__main__":
    build()
