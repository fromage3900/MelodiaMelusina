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
GROUP_TEXTURES = "Textures"

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

    if not unreal.EditorAssetLibrary.does_asset_exist(f"{lib.FUNCTION_DIR}/MF_SpaceParallax"):
        try:
            import setup_material_functions as mf_setup

            mf_setup.build_all(force=False)
        except Exception as exc:
            unreal.log_warning(f"[Universal] MF library: {exc}")
    for _mf in ("MF_ParallaxCore", "MF_NormalAdjust"):
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

    # ---- Dreamy shadows (N·L tint in shadow) ----
    shadow_tint = lib.vector_param(m, "ShadowDreamTint", "ShadowDream", (0.48, 0.42, 0.62, 1.0), -2100, 4900)
    shadow_str = lib.scalar_param(m, "ShadowDreamStrength", "ShadowDream", 0.0, -2100, 5000)
    shadow_soft = lib.scalar_param(m, "ShadowSoftness", "ShadowDream", 0.5, -2100, 5100)
    # ---- Flower shadow garden (projected petal silhouettes in shadow) ----
    flower_str = lib.scalar_param(
        m, "ShadowFlowerStrength", "FlowerShadow", 0.0, -2100, 5220,
        desc="Petal shadow projection intensity",
    )
    flower_scale = lib.scalar_param(
        m, "ShadowFlowerScale", "FlowerShadow", 5.0, -2100, 5320,
        desc="World-space petal repeat scale",
    )
    flower_color = lib.vector_param(
        m, "ShadowFlowerColor", "FlowerShadow", (0.92, 0.45, 0.72, 1.0), -2100, 5420,
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

    color_nikki = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 220, 120)
    wire("nikki_base_A", color, color_nikki, "A")
    wire("nikki_base_B", dream_tint, color_nikki, "B")
    wire("nikki_base_alpha", pastel, color_nikki, "Alpha")

    # Nikki grading (environment-safe): optional pastel grading before emissive adds.
    # Defaults are neutral (all 0).
    lum = lib.create_expression(m, unreal.MaterialExpressionDotProduct, 60, 200)
    wire("dream_lumA", color_nikki, lum, "A")
    lum_w = const3(m, -40, 280, 0.299, 0.587, 0.114)
    wire("dream_lumB", lum_w, lum, "B")
    gray = lib.create_expression(m, unreal.MaterialExpressionMultiply, 220, 200)
    wire("dream_grayA", lum, gray, "A")
    wire("dream_grayB", const1(m, 60, 280, 1.0), gray, "B")
    sat_lerp = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 400, 200)
    wire("dream_satA", color_nikki, sat_lerp, "A")
    wire("dream_satB", gray, sat_lerp, "B")
    wire("dream_satAlpha", dream_sat, sat_lerp, "Alpha")
    mid = const1(m, 400, 320, 0.5)
    sub = lib.create_expression(m, unreal.MaterialExpressionSubtract, 560, 200)
    wire("dream_con_subA", sat_lerp, sub, "A")
    wire("dream_con_subB", mid, sub, "B")
    c_mul = lib.create_expression(m, unreal.MaterialExpressionMultiply, 720, 200)
    wire("dream_con_mulA", sub, c_mul, "A")
    con_scale = lib.create_expression(m, unreal.MaterialExpressionAdd, 560, 320)
    wire("dream_con_scaleA", const1(m, 560, 360, 1.0), con_scale, "A")
    wire("dream_con_scaleB", dream_contrast, con_scale, "B")
    wire("dream_con_mulB", con_scale, c_mul, "B")
    con_add = lib.create_expression(m, unreal.MaterialExpressionAdd, 880, 200)
    wire("dream_con_addA", c_mul, con_add, "A")
    wire("dream_con_addB", mid, con_add, "B")
    # shadow lift / highlight soft from luminance
    sh_mask = lib.create_expression(m, unreal.MaterialExpressionOneMinus, 560, 420)
    wire("dream_sh_inv", lum, sh_mask, "Input")
    sh = lib.create_expression(m, unreal.MaterialExpressionMultiply, 720, 420)
    wire("dream_shA", sh_mask, sh, "A")
    wire("dream_shB", dream_shadow_lift, sh, "B")
    hi = lib.create_expression(m, unreal.MaterialExpressionMultiply, 720, 500)
    wire("dream_hiA", lum, hi, "A")
    wire("dream_hiB", dream_high_soft, hi, "B")
    grade_add = lib.create_expression(m, unreal.MaterialExpressionAdd, 1040, 260)
    wire("dream_gradeA", sh, grade_add, "A")
    wire("dream_gradeB", hi, grade_add, "B")
    dream_grade = lib.create_expression(m, unreal.MaterialExpressionAdd, 1200, 200)
    wire("dream_gradeAddA", con_add, dream_grade, "A")
    wire("dream_gradeAddB", grade_add, dream_grade, "B")
    color_nikki = dream_grade

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

    # shared world-XY coords for shadow garden + fairy dust motifs
    wxy = world_xy(m, 220, 300)

    # shadow garden flowers (world clover in shadow)
    flower_uv = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1220, 900)
    wire("fl_uvA", wxy, flower_uv, "A")
    wire("fl_uvB", flower_scale, flower_uv, "B")
    petal_x = lib.create_expression(m, unreal.MaterialExpressionSine, 1400, 860)
    petal_x.set_editor_property("period", 1.0)
    flower_x = mask_channel(m, flower_uv, "r", "fl_x", 1220, 860)
    wire("petal_x", flower_x, petal_x, "Input")
    petal_y = lib.create_expression(m, unreal.MaterialExpressionSine, 1400, 980)
    petal_y.set_editor_property("period", 1.0)
    flower_y = mask_channel(m, flower_uv, "g", "fl_y", 1220, 980)
    flower_uv2 = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1400, 920)
    wire("fl2A", flower_y, flower_uv2, "A")
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
    # macro: tiled UV noise -> subtle albedo brightness/tint variation (kills tiling)
    mac_tc = lib.create_expression(m, unreal.MaterialExpressionTextureCoordinate, 3600, 620)
    mac_scl = lib.create_expression(m, unreal.MaterialExpressionMultiply, 3760, 620)
    wire("mac_tcA", mac_tc, mac_scl, "A"); wire("mac_tcB", macro_scale, mac_scl, "B")
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

    # ---- Magical-girl transform (henshin wipe + motif mask; defaults off) ----
    mtransform = lib.scalar_param(
        m, "MagicalTransform", "Magical", 0.0, 4800, 120,
        desc="0→1 henshin driver (sync MPC_Magical)",
    )
    motif_mask = tex_object(m, "MotifMask", 4800, 200, "Magical")  # T_Magic_Heart/Bow/Star
    motif_scale = lib.scalar_param(m, "MotifScale", "Magical", 6.0, 4800, 360)
    motif_color = lib.vector_param(m, "MotifColor", "Magical", (1.0, 0.45, 0.72, 1.0), 4800, 440)
    transform_glow = lib.scalar_param(m, "TransformGlow", "Magical", 3.0, 4800, 520)
    wipe_soft = lib.scalar_param(m, "WipeSoftness", "Magical", 0.25, 4800, 600, desc="World-Z wipe edge softness")
    magical_palette = lib.vector_param(m, "MagicalPalette", "Magical", (1.0, 0.72, 0.86, 1.0), 4800, 680)
    # wipe sweep over world-Z, revealed by MagicalTransform
    mg_wp = lib.create_expression(m, unreal.MaterialExpressionWorldPosition, 4800, 780)
    mg_z = lib.create_expression(m, unreal.MaterialExpressionComponentMask, 4960, 780)
    mg_z.set_editor_property("r", False); mg_z.set_editor_property("g", False)
    mg_z.set_editor_property("b", True); mg_z.set_editor_property("a", False)
    wire("mg_z", mg_wp, mg_z, "")
    mg_zs = lib.create_expression(m, unreal.MaterialExpressionMultiply, 5120, 780)
    wire("mg_zsA", mg_z, mg_zs, "A"); wire("mg_zsB", const1(m, 4960, 880, 0.004), mg_zs, "B")
    mg_sub = lib.create_expression(m, unreal.MaterialExpressionSubtract, 5280, 760)
    wire("mg_subA", mtransform, mg_sub, "A"); wire("mg_subB", mg_zs, mg_sub, "B")
    mg_div = lib.create_expression(m, unreal.MaterialExpressionDivide, 5440, 760)
    wire("mg_divA", mg_sub, mg_div, "A"); wire("mg_divB", wipe_soft, mg_div, "B")
    mg_wipe = lib.create_expression(m, unreal.MaterialExpressionSaturate, 5600, 760)
    wire("mg_wipe", mg_div, mg_wipe, "Input", "")
    # motif mask sample
    mg_tc = lib.create_expression(m, unreal.MaterialExpressionTextureCoordinate, 4800, 980)
    mg_uv = lib.create_expression(m, unreal.MaterialExpressionMultiply, 4960, 980)
    wire("mg_uvA", mg_tc, mg_uv, "A"); wire("mg_uvB", motif_scale, mg_uv, "B")
    mg_s = lib.create_expression(m, unreal.MaterialExpressionTextureSample, 5120, 980)
    wire("mg_obj", motif_mask, mg_s, "Tex", "TextureObject")
    wire("mg_suv", mg_uv, mg_s, "UVs", "Coordinates")
    mg_sr = lib.create_expression(m, unreal.MaterialExpressionComponentMask, 5280, 980)
    mg_sr.set_editor_property("r", True); mg_sr.set_editor_property("g", False)
    mg_sr.set_editor_property("b", False); mg_sr.set_editor_property("a", False)
    wire("mg_sr", mg_s, mg_sr, "")
    # reveal = wipe * motif * MagicalTransform
    mg_rev1 = lib.create_expression(m, unreal.MaterialExpressionMultiply, 5760, 860)
    wire("mg_rev1A", mg_wipe, mg_rev1, "A"); wire("mg_rev1B", mg_sr, mg_rev1, "B")
    mg_rev = lib.create_expression(m, unreal.MaterialExpressionMultiply, 5920, 860)
    wire("mg_revA", mg_rev1, mg_rev, "A"); wire("mg_revB", mtransform, mg_rev, "B")
    # motif emissive = reveal * MotifColor * TransformGlow
    mg_ec = lib.create_expression(m, unreal.MaterialExpressionMultiply, 6080, 860)
    wire("mg_ecA", mg_rev, mg_ec, "A"); wire("mg_ecB", motif_color, mg_ec, "B")
    mg_emis = lib.create_expression(m, unreal.MaterialExpressionMultiply, 6240, 860)
    wire("mg_emisA", mg_ec, mg_emis, "A"); wire("mg_emisB", transform_glow, mg_emis, "B")
    # palette shift toward MagicalPalette by MagicalTransform*0.5
    mg_pal_amt = lib.create_expression(m, unreal.MaterialExpressionMultiply, 5760, 480)
    wire("mg_palA", mtransform, mg_pal_amt, "A"); wire("mg_palB", const1(m, 5600, 560, 0.5), mg_pal_amt, "B")
    mg_color = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 5920, 480)
    wire("mg_colA", final_color, mg_color, "A"); wire("mg_colB", magical_palette, mg_color, "B"); wire("mg_colAlpha", mg_pal_amt, mg_color, "Alpha")
    final_color = mg_color
    # add motif emissive to the emissive sum
    mg_emis_add = lib.create_expression(m, unreal.MaterialExpressionAdd, 6400, 1100)
    wire("mg_emis_addA", emissive, mg_emis_add, "A"); wire("mg_emis_addB", mg_emis, mg_emis_add, "B")
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

    wrap_mul = lib.create_expression(m, unreal.MaterialExpressionMultiply, 6840, 200)
    wire("wrap_mulA", skin_wrap_rad, wrap_mul, "A")
    wire("wrap_mulB", skin_wrap_str, wrap_mul, "B")
    wrap_add = lib.create_expression(m, unreal.MaterialExpressionAdd, 7000, 120)
    wire("wrap_addA", ndotl, wrap_add, "A")
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
    WIRES["std_lit"] = lib.connect_unary(ndotl, std_lit)
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
    WIRES["toon_basecolor"] = lib.connect_toon_pin(toon, final_color, ("BaseColor", "DiffuseColor"))
    WIRES["toon_roughness"] = lib.connect_toon_pin(toon, rough_gold, ("Roughness",))
    WIRES["toon_normal"] = lib.connect_toon_pin(toon, nrm, ("Normal", "TangentNormal", "NormalMap"))
    WIRES["toon_metallic"] = lib.connect_toon_pin(toon, metal_gold, ("Metallic", "Metalness"))
    WIRES["toon_emissive"] = lib.connect_toon_pin(toon, emissive, ("Emissive Color", "EmissiveColor", "Emissive"))
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
