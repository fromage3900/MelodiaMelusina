"""Build M_Master_Toon_Universal — the 'reach for every scene' master.

Adds, on top of the proven Substrate Toon BSDF -> Front Material chain:
  #1 Texture <-> procedural HYBRID: Lerp(BaseTint, sampled Albedo, TextureWeight)
                                    0 = flat toon (blockout), 1 = fully textured
  #2 TRIPLANAR toggle (static switch `bTriplanar`): UV sampling  <->  WorldAligned
                                    projection (no UVs needed — greybox/kit-bash)

Every wire is defensive + logged: the material always compiles via the BSDF (proven),
and UNIVERSAL_RESULT reports exactly which pins connected so we can refine in-editor.

Run (editor open): Tools -> Execute Python Script -> this file
Or Output Log:     py "G:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_master_universal.py"
"""
from __future__ import annotations

import unreal
import material_lib as lib

MASTER_NAME = "M_Master_Toon_Universal"
WAT = "/Engine/Functions/Engine_MaterialFunctions02/Texturing/WorldAlignedTexture"
WAN = "/Engine/Functions/Engine_MaterialFunctions02/Texturing/WorldAlignedNormal"

WIRES: dict[str, bool] = {}


def wire(tag, from_e, to_e, *pins) -> bool:
    """Connect trying each candidate input pin name; record success."""
    for p in pins:
        if from_e is not None and lib.connect(from_e, "", to_e, p):
            WIRES[tag] = True
            return True
    WIRES[tag] = False
    return False


def tex_object(m, name, x, y):
    e = lib.create_expression(m, unreal.MaterialExpressionTextureObjectParameter, x, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("group", "Textures")
    return e


def mf_call(m, path, x, y):
    if not unreal.EditorAssetLibrary.does_asset_exist(path):
        return None
    c = lib.create_expression(m, unreal.MaterialExpressionMaterialFunctionCall, x, y)
    c.set_editor_property("material_function", unreal.load_asset(path))
    return c


def static_switch(m, x, y):
    sw = lib.create_expression(m, unreal.MaterialExpressionStaticSwitchParameter, x, y)
    sw.set_editor_property("parameter_name", "bTriplanar")
    sw.set_editor_property("group", "Triplanar")
    sw.set_editor_property("default_value", False)
    return sw


def build():
    lib.ensure_directory(lib.MASTER_DIR)
    path = lib.asset_path(lib.MASTER_DIR, MASTER_NAME)
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)

    at = unreal.AssetToolsHelpers.get_asset_tools()
    m = at.create_asset(MASTER_NAME, lib.MASTER_DIR, unreal.Material, unreal.MaterialFactoryNew())
    if not m:
        raise RuntimeError("create_asset failed")
    m.set_editor_property("material_domain", unreal.MaterialDomain.MD_SURFACE)
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_OPAQUE)
    lib.try_set_editor_property(m, "bUsesSubstrate", True)

    # ---- parameters ----
    base_tint = lib.vector_param(m, "BaseTint", "Palette", (0.60, 0.55, 0.50, 1.0), -1500, -220)
    tex_weight = lib.scalar_param(m, "TextureWeight", "Hybrid", 1.0, -1500, -100)   # 0 flat <-> 1 textured
    uv_scale = lib.scalar_param(m, "UVScale", "UV", 1.0, -1500, 20)
    roughness_s = lib.scalar_param(m, "Roughness", "Surface", 0.70, -1500, 140)
    tri_tiling = lib.scalar_param(m, "TriplanarTiling", "Triplanar", 256.0, -1500, 260)
    albedo = tex_object(m, "Albedo", -1500, 400)
    normal = tex_object(m, "NormalMap", -1500, 560)
    orm = tex_object(m, "ORM", -1500, 720)

    # ---- UV coords ----
    tc = lib.create_expression(m, unreal.MaterialExpressionTextureCoordinate, -1200, 380)
    uv = lib.create_expression(m, unreal.MaterialExpressionMultiply, -1020, 380)
    wire("uv_tc", tc, uv, "A"); wire("uv_scale", uv_scale, uv, "B")

    def uv_sample(tag, tobj, yy):
        s = lib.create_expression(m, unreal.MaterialExpressionTextureSample, -820, yy)
        wire(f"{tag}_obj", tobj, s, "Tex", "TextureObject")
        wire(f"{tag}_uv", uv, s, "UVs", "Coordinates")
        return s

    alb_uv = uv_sample("alb", albedo, 400)
    nrm_uv = uv_sample("nrm", normal, 560)
    orm_uv = uv_sample("orm", orm, 720)

    # ---- triplanar (WorldAligned*) ----
    waT = mf_call(m, WAT, -640, 400)
    waN = mf_call(m, WAN, -640, 560)
    waR = mf_call(m, WAT, -640, 720)
    for tag, fn, tobj in (("triA", waT, albedo), ("triN", waN, normal), ("triR", waR, orm)):
        if fn:
            wire(f"{tag}_obj", tobj, fn, "TextureObject (T2d)", "TextureObject", "Tex")
            wire(f"{tag}_size", tri_tiling, fn, "Texture Size", "WorldSize", "Size")

    def switch(tag, uv_e, tri_e, yy):
        sw = static_switch(m, -460, yy)
        wire(f"{tag}_true", tri_e or uv_e, sw, "A", "True")   # bTriplanar = True
        wire(f"{tag}_false", uv_e, sw, "B", "False")          # bTriplanar = False (UV)
        return sw

    alb = switch("swA", alb_uv, waT, 400)
    nrm_s = switch("swN", nrm_uv, waN, 560)
    orm_s = switch("swR", orm_uv, waR, 720)

    # ---- #1 hybrid: Lerp(BaseTint, Albedo, TextureWeight) ----
    color = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 60, 120)
    wire("color_A", base_tint, color, "A")
    wire("color_B", alb, color, "B")
    wire("color_alpha", tex_weight, color, "Alpha")

    # ---- roughness: Lerp(Roughness, ORM.G, TextureWeight) ----
    org = lib.create_expression(m, unreal.MaterialExpressionComponentMask, 60, 720)
    org.set_editor_property("r", False); org.set_editor_property("g", True)
    org.set_editor_property("b", False); org.set_editor_property("a", False)
    lib.connect_unary(orm_s, org)
    rough = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 280, 720)
    wire("rough_A", roughness_s, rough, "A")
    wire("rough_B", org, rough, "B")
    wire("rough_alpha", tex_weight, rough, "Alpha")

    # ---- normal: Lerp(flat, sampled, TextureWeight) ----
    flat = lib.create_expression(m, unreal.MaterialExpressionConstant3Vector, 60, 560)
    flat.set_editor_property("constant", unreal.LinearColor(0.0, 0.0, 1.0, 1.0))
    nrm = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 280, 560)
    wire("nrm_A", flat, nrm, "A")
    wire("nrm_B", nrm_s, nrm, "B")
    wire("nrm_alpha", tex_weight, nrm, "Alpha")

    # ---- Infinity-Nikki dreamy layer (group 'Nikki', all default 0 = neutral) ----
    rim_color = lib.vector_param(m, "RimColor", "Nikki", (0.70, 0.85, 1.00, 1.0), -1500, 900)
    rim_power = lib.scalar_param(m, "RimPower", "Nikki", 3.0, -1500, 1000)
    rim_int = lib.scalar_param(m, "RimIntensity", "Nikki", 0.0, -1500, 1100)
    dream_tint = lib.vector_param(m, "DreamTint", "Nikki", (1.00, 0.85, 0.92, 1.0), -1500, 1200)
    pastel = lib.scalar_param(m, "PastelLift", "Nikki", 0.0, -1500, 1300)
    irid = lib.scalar_param(m, "Iridescence", "Nikki", 0.0, -1500, 1400)
    irid_tint = lib.vector_param(m, "IridescenceTint", "Nikki", (0.80, 0.60, 1.00, 1.0), -1500, 1500)
    spark_mask = lib.texture_param(m, "SparkleMask", "Nikki", -1500, 1600)   # assign T_Spark_Twinkle8
    spark_scale = lib.scalar_param(m, "SparkleScale", "Nikki", 8.0, -1500, 1700)
    spark_int = lib.scalar_param(m, "SparkleIntensity", "Nikki", 0.0, -1500, 1800)
    spark_color = lib.vector_param(m, "SparkleColor", "Nikki", (1.00, 0.95, 0.80, 1.0), -1500, 1900)
    glow_color = lib.vector_param(m, "GlowColor", "Nikki", (1.00, 0.90, 0.95, 1.0), -1500, 2000)
    glow_int = lib.scalar_param(m, "GlowIntensity", "Nikki", 0.0, -1500, 2100)
    rim_soft = lib.scalar_param(m, "RimSoftness", "Nikki", 0.35, -1500, 2200)
    inner_glow = lib.scalar_param(m, "InnerGlowIntensity", "Nikki", 0.0, -1500, 2300)
    inner_color = lib.vector_param(m, "InnerGlowColor", "Nikki", (1.00, 0.92, 0.98, 1.0), -1500, 2400)
    bloom = lib.scalar_param(m, "BloomBoost", "Nikki", 0.0, -1500, 2500)
    sheen = lib.scalar_param(m, "FabricSheen", "Nikki", 0.0, -1500, 2600)
    sheen_tint = lib.vector_param(m, "SheenTint", "Nikki", (1.00, 1.00, 1.00, 1.0), -1500, 2700)
    sheen_power = lib.scalar_param(m, "SheenPower", "Nikki", 6.0, -1500, 2800)

    # pastel push: Lerp(color, DreamTint, PastelLift) -> final base color
    color_nikki = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 340, 120)
    wire("nikki_base_A", color, color_nikki, "A")
    wire("nikki_base_B", dream_tint, color_nikki, "B")
    wire("nikki_base_alpha", pastel, color_nikki, "Alpha")

    # fresnel rim mask (drives rim glow + iridescence)
    fres = lib.create_expression(m, unreal.MaterialExpressionFresnel, 340, 900)
    wire("fresnel_exp", rim_power, fres, "ExponentIn")
    rim_soft_m = lib.create_expression(m, unreal.MaterialExpressionLinearInterpolate, 340, 980)
    wire("rim_soft_A", fres, rim_soft_m, "A")
    one = lib.create_expression(m, unreal.MaterialExpressionConstant, 180, 980)
    one.set_editor_property("r", 1.0)
    rim_inv = lib.create_expression(m, unreal.MaterialExpressionOneMinus, 180, 1040)
    wire("rim_soft_inv", rim_soft, rim_inv, "Input")
    rim_soft_b = lib.create_expression(m, unreal.MaterialExpressionMultiply, 180, 1100)
    wire("rim_soft_bA", fres, rim_soft_b, "A")
    wire("rim_soft_bB", rim_inv, rim_soft_b, "B")
    wire("rim_soft_alpha", rim_soft, rim_soft_m, "Alpha")
    wire("rim_soft_B", rim_soft_b, rim_soft_m, "B")
    rim_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 520, 900)
    wire("rim_mA", rim_soft_m, rim_m, "A"); wire("rim_mB", rim_int, rim_m, "B")
    rim_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 700, 900)
    wire("rim_eA", rim_m, rim_e, "A"); wire("rim_eB", rim_color, rim_e, "B")
    irid_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 520, 1080)
    wire("irid_mA", rim_soft_m, irid_m, "A"); wire("irid_mB", irid, irid_m, "B")
    irid_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 700, 1080)
    wire("irid_eA", irid_m, irid_e, "A"); wire("irid_eB", irid_tint, irid_e, "B")

    # sparkle: SparkleMask(uv * SparkleScale) * SparkleIntensity * SparkleColor
    spark_uv = lib.create_expression(m, unreal.MaterialExpressionMultiply, 340, 1300)
    wire("spark_uvA", uv, spark_uv, "A"); wire("spark_uvB", spark_scale, spark_uv, "B")
    wire("spark_mask_uv", spark_uv, spark_mask, "UVs", "Coordinates")
    spark_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 520, 1300)
    wire("spark_mA", spark_mask, spark_m, "A"); wire("spark_mB", spark_int, spark_m, "B")
    spark_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 700, 1300)
    wire("spark_eA", spark_m, spark_e, "A"); wire("spark_eB", spark_color, spark_e, "B")

    # soft glow: GlowColor * GlowIntensity
    glow_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 520, 1500)
    wire("glow_eA", glow_color, glow_e, "A"); wire("glow_eB", glow_int, glow_e, "B")

    # inner glow: (1 - fresnel) * InnerGlowColor * InnerGlowIntensity
    inner_inv = lib.create_expression(m, unreal.MaterialExpressionOneMinus, 340, 1180)
    wire("inner_inv", rim_soft_m, inner_inv, "Input")
    inner_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 520, 1180)
    wire("inner_mA", inner_inv, inner_m, "A"); wire("inner_mB", inner_glow, inner_m, "B")
    inner_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 700, 1180)
    wire("inner_eA", inner_m, inner_e, "A"); wire("inner_eB", inner_color, inner_e, "B")

    # fabric sheen: second fresnel lobe
    sheen_f = lib.create_expression(m, unreal.MaterialExpressionFresnel, 340, 1360)
    wire("sheen_exp", sheen_power, sheen_f, "ExponentIn")
    sheen_m = lib.create_expression(m, unreal.MaterialExpressionMultiply, 520, 1360)
    wire("sheen_mA", sheen_f, sheen_m, "A"); wire("sheen_mB", sheen, sheen_m, "B")
    sheen_e = lib.create_expression(m, unreal.MaterialExpressionMultiply, 700, 1360)
    wire("sheen_eA", sheen_m, sheen_e, "A"); wire("sheen_eB", sheen_tint, sheen_e, "B")

    # emissive total = rim + iridescence + sparkle + glow + inner + sheen, then BloomBoost
    a1 = lib.create_expression(m, unreal.MaterialExpressionAdd, 900, 1000)
    wire("emi1A", rim_e, a1, "A"); wire("emi1B", irid_e, a1, "B")
    a2 = lib.create_expression(m, unreal.MaterialExpressionAdd, 1060, 1120)
    wire("emi2A", a1, a2, "A"); wire("emi2B", spark_e, a2, "B")
    a3 = lib.create_expression(m, unreal.MaterialExpressionAdd, 1220, 1240)
    wire("emi3A", a2, a3, "A"); wire("emi3B", glow_e, a3, "B")
    a4 = lib.create_expression(m, unreal.MaterialExpressionAdd, 1380, 1240)
    wire("emi4A", a3, a4, "A"); wire("emi4B", inner_e, a4, "B")
    emissive_raw = lib.create_expression(m, unreal.MaterialExpressionAdd, 1540, 1240)
    wire("emi5A", a4, emissive_raw, "A"); wire("emi5B", sheen_e, emissive_raw, "B")
    bloom_m = lib.create_expression(m, unreal.MaterialExpressionAdd, 1700, 1240)
    one_bloom = lib.create_expression(m, unreal.MaterialExpressionConstant, 1540, 1320)
    one_bloom.set_editor_property("r", 1.0)
    wire("bloom_add_A", one_bloom, bloom_m, "A"); wire("bloom_add_B", bloom, bloom_m, "B")
    emissive = lib.create_expression(m, unreal.MaterialExpressionMultiply, 1860, 1240)
    wire("bloom_mul_A", emissive_raw, emissive, "A"); wire("bloom_mul_B", bloom_m, emissive, "B")

    # ---- Substrate Toon BSDF -> Front Material (your proven chain) ----
    profiles = lib.create_toon_profiles(["TP_Default"])
    toon = lib.create_expression(m, unreal.MaterialExpressionSubstrateToonBSDF, 1460, 360)
    lib.try_set_editor_property(toon, "toon_profile", profiles.get("TP_Default"))
    WIRES["toon_basecolor"] = lib.connect_toon_pin(toon, color_nikki, ("BaseColor", "DiffuseColor"))
    WIRES["toon_roughness"] = lib.connect_toon_pin(toon, rough, ("Roughness",))
    WIRES["toon_normal"] = lib.connect_toon_pin(toon, nrm, ("Normal", "TangentNormal", "NormalMap"))
    WIRES["toon_emissive"] = lib.connect_toon_pin(toon, emissive, ("Emissive Color", "EmissiveColor", "Emissive"))
    lib.connect_front_material(m, toon)

    unreal.MaterialEditingLibrary.recompile_material(m)
    lib.save_package(m)

    failed = sorted(k for k, v in WIRES.items() if not v)
    unreal.log(f"[Universal] built {path}")
    unreal.log(f"[Universal] wires ok={sum(WIRES.values())}/{len(WIRES)} | failed={failed}")
    print(f"UNIVERSAL_RESULT path={path} ok={sum(WIRES.values())}/{len(WIRES)} failed={failed}")
    return path


if __name__ == "__main__":
    build()
