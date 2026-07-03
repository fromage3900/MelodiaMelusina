"""Build the lean, Nikki-focused master materials from existing MFs.

Direction approved 2026-07-02: instead of extending the 918-expression
M_Master_Toon_Universal (whose bNikkiHero switch swaps out whole chains and
fights the map inputs -- see MI_IridescentRock's degenerate overrides,
e.g. IridescencePower=5e9), build a small composable master that cherry-picks
the proven families as Material Function calls.

Design rules (all three violated by the old master):
  1. Every scalar param is clamped (slider_min/max) with a neutral default
     (0 = feature off / 1 = nominal), grouped for the instance UI.
  2. Nikki families are modulators, not chain-swappers: iridescence tints
     BaseColor and *attenuates* roughness; ramp/atmosphere lerp from the
     untouched base by a Strength param defaulting to bypass.
  3. Families come from MFs so they are testable in isolation:
     MF_ParallaxCore (UV offset + self-shadow), MF_ColorRamp3 (3-stop color
     ramp with mid position + contrast), MF_IridescenceSheen (color+emissive).

Scope agreed with user: parallax + advanced color ramp + atmospheric depth,
then STOP (no sparkle/gilding/etc. in v1 -- add only when needed).

Builds two masters (idempotent -- deletes and rebuilds):
  /Game/EnvSandbox/Materials/_Scratch/M_Master_Nikki            (surface)
  /Game/EnvSandbox/Materials/_Scratch/M_Master_Nikki_Landscape  (landscape UV)

Run inside the editor (Monolith run_python):
  import build_nikki_masters, importlib
  importlib.reload(build_nikki_masters)
  build_nikki_masters.build_all()
"""
from __future__ import annotations

DEST = "/Game/EnvSandbox/Materials/_Scratch"
MF_PARALLAX = "/Game/EnvSandbox/Materials/Functions/MF_ParallaxCore"
MF_RAMP = "/Game/EnvSandbox/Materials/Functions/MF_ColorRamp3"
MF_IRID = "/Game/EnvSandbox/Materials/_Scratch/MF_IridescenceSheen"


def build(name: str, landscape: bool = False) -> dict:
    import unreal
    MEL = unreal.MaterialEditingLibrary
    AT = unreal.AssetToolsHelpers.get_asset_tools()

    full = f"{DEST}/{name}"
    # NEVER delete_asset here: deleting a material the user has open in a
    # Material Editor tab hard-crashes the editor (ObjectTools.cpp:4043
    # ensure, hit live 2026-07-02). Rebuild in place instead.
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        mat = unreal.EditorAssetLibrary.load_asset(full)
        MEL.delete_all_material_expressions(mat)
    else:
        mat = AT.create_asset(name, DEST, unreal.Material, unreal.MaterialFactoryNew())
    if mat is None:
        raise RuntimeError(f"load/create returned None for {full}")

    def expr(cls, x, y):
        return MEL.create_material_expression(mat, cls, x, y)

    def sparam(pname, default, smin, smax, group, x, y):
        p = expr(unreal.MaterialExpressionScalarParameter, x, y)
        p.set_editor_property("parameter_name", pname)
        p.set_editor_property("default_value", default)
        p.set_editor_property("slider_min", smin)
        p.set_editor_property("slider_max", smax)
        p.set_editor_property("group", group)
        return p

    def vparam(pname, rgba, group, x, y):
        p = expr(unreal.MaterialExpressionVectorParameter, x, y)
        p.set_editor_property("parameter_name", pname)
        p.set_editor_property("default_value", unreal.LinearColor(*rgba))
        p.set_editor_property("group", group)
        return p

    def mfcall(path, x, y):
        c = expr(unreal.MaterialExpressionMaterialFunctionCall, x, y)
        c.set_editor_property("material_function", unreal.EditorAssetLibrary.load_asset(path))
        return c

    con = MEL.connect_material_expressions

    def tsamp(pname, group, x, y, uv_src=None, uv_pin="", is_normal=False):
        t = expr(unreal.MaterialExpressionTextureSampleParameter2D, x, y)
        t.set_editor_property("parameter_name", pname)
        t.set_editor_property("group", group)
        if is_normal:
            t.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
            t.set_editor_property("texture", unreal.EditorAssetLibrary.load_asset("/Engine/EngineMaterials/FlatNormal"))
        if uv_src is not None:
            con(uv_src, uv_pin, t, "UVs")
        return t

    if not landscape:
        # ---- Surface front-end: TexCoord * UVScale -> MF_ParallaxCore ----
        uv = expr(unreal.MaterialExpressionTextureCoordinate, -2300, 0)
        uvscale = sparam("UVScale", 1.0, 0.05, 10.0, "Base", -2300, 140)
        uvmul = expr(unreal.MaterialExpressionMultiply, -2100, 40)
        con(uv, "", uvmul, "A")
        con(uvscale, "", uvmul, "B")

        # Parallax via engine BumpOffset (MF_ParallaxCore has broken input
        # typing -- float2/texture2D casts fail; part of the old master's
        # parallax jank). One clamped strength param, predictable response.
        hsamp = tsamp("HeightMap", "Parallax", -2100, 220, uvmul, "")
        p_strength = sparam("ParallaxStrength", 0.0, 0.0, 1.0, "Parallax", -2100, 420)
        p_ratio = expr(unreal.MaterialExpressionMultiply, -1950, 440)
        p_max = expr(unreal.MaterialExpressionConstant, -2100, 500)
        p_max.set_editor_property("r", 0.1)
        con(p_strength, "", p_ratio, "A")
        con(p_max, "", p_ratio, "B")
        par = expr(unreal.MaterialExpressionBumpOffset, -1850, 100)
        con(uvmul, "", par, "Coordinate")
        con(hsamp, "R", par, "Height")
        con(p_ratio, "", par, "HeightRatioInput")

        albedo = tsamp("Albedo", "Base", -1550, -200, par, "")
        normal = tsamp("NormalMap", "Base", -1550, 420, par, "", is_normal=True)
        orm = tsamp("ORM", "Base", -1550, 140, par, "")
        base_src, base_pin = albedo, "RGB"
        normal_src, normal_pin = normal, "RGB"
        rough_src, rough_pin = orm, "G"
        metal_src, metal_pin = orm, "B"
    else:
        # ---- Landscape front-end: painted-weight LandscapeLayerBlend ----
        # (user note 2026-07-02: old landscape master "struggles to use
        # painted layers" -- this one is built around them. 3 layers, each
        # with own Albedo/Normal/UVScale/Roughness, weight-blended by paint.
        # Parallax deliberately omitted: POM under painted weight blends
        # shimmers at layer transitions.)
        LAYERS = ["Ground", "Grass", "Rock"]

        def layer_blend(x, y):
            lb = expr(unreal.MaterialExpressionLandscapeLayerBlend, x, y)
            arr = []
            for ln in LAYERS:
                li = unreal.LayerBlendInput()
                li.set_editor_property("layer_name", ln)
                li.set_editor_property("blend_type", unreal.LandscapeLayerBlendType.LB_WEIGHT_BLEND)
                li.set_editor_property("preview_weight", 1.0 if ln == "Ground" else 0.0)
                arr.append(li)
            lb.set_editor_property("layers", arr)
            return lb

        alb_blend = layer_blend(-1550, -260)
        nrm_blend = layer_blend(-1550, 420)
        rgh_blend = layer_blend(-1550, 140)

        for i, ln in enumerate(LAYERS):
            ly = -900 + i * 620
            luv = expr(unreal.MaterialExpressionLandscapeLayerCoords, -2300, ly)
            lscale = sparam(f"{ln}_UVScale", 1.0, 0.05, 10.0, f"Layer {ln}", -2300, ly + 130)
            lmul = expr(unreal.MaterialExpressionMultiply, -2100, ly + 40)
            con(luv, "", lmul, "A")
            con(lscale, "", lmul, "B")
            la = tsamp(f"{ln}_Albedo", f"Layer {ln}", -1900, ly - 60, lmul, "")
            lnorm = tsamp(f"{ln}_NormalMap", f"Layer {ln}", -1900, ly + 240, lmul, "", is_normal=True)
            lrough = sparam(f"{ln}_Roughness", 0.8, 0.0, 1.0, f"Layer {ln}", -1900, ly + 170)
            con(la, "RGB", alb_blend, f"Layer {ln}")
            con(lnorm, "RGB", nrm_blend, f"Layer {ln}")
            con(lrough, "", rgh_blend, f"Layer {ln}")

        base_src, base_pin = alb_blend, ""
        normal_src, normal_pin = nrm_blend, ""
        rough_src, rough_pin = rgh_blend, ""
        metal_src, metal_pin = None, ""

    # ---- BaseColor: base * BaseTint ----
    tint = vparam("BaseTint", (1, 1, 1, 1), "Base", -1550, -420)
    tintmul = expr(unreal.MaterialExpressionMultiply, -1300, -300)
    con(base_src, base_pin, tintmul, "A")
    con(tint, "", tintmul, "B")

    # ---- Advanced color ramp (MF_ColorRamp3), lerp by RampStrength ----
    lum_w = expr(unreal.MaterialExpressionConstant3Vector, -1300, -140)
    lum_w.set_editor_property("constant", unreal.LinearColor(0.299, 0.587, 0.114, 0.0))
    lum = expr(unreal.MaterialExpressionDotProduct, -1120, -180)
    con(tintmul, "", lum, "A")
    con(lum_w, "", lum, "B")

    r_low = vparam("RampLow", (0.20, 0.15, 0.30, 1), "ColorRamp", -1120, -620)
    r_mid = vparam("RampMid", (0.85, 0.60, 0.75, 1), "ColorRamp", -1120, -480)
    r_high = vparam("RampHigh", (1.0, 0.95, 0.90, 1), "ColorRamp", -1120, -340)
    r_pos = sparam("RampPosMid", 0.5, 0.05, 0.95, "ColorRamp", -1120, -60)
    r_con = sparam("RampContrast", 1.0, 0.1, 4.0, "ColorRamp", -1120, 0)
    r_str = sparam("RampStrength", 0.0, 0.0, 1.0, "ColorRamp", -1120, 60)

    ramp = mfcall(MF_RAMP, -880, -400)
    con(r_low, "", ramp, "RampLow")
    con(r_mid, "", ramp, "RampMid")
    con(r_high, "", ramp, "RampHigh")
    con(r_pos, "", ramp, "RampPosMid")
    con(lum, "", ramp, "Mask")
    con(r_con, "", ramp, "RampContrast")

    graded = expr(unreal.MaterialExpressionLinearInterpolate, -680, -300)
    con(tintmul, "", graded, "A")
    con(ramp, "Color", graded, "B")
    con(r_str, "", graded, "Alpha")

    # ---- Iridescence/Sheen as modulator ----
    irid = mfcall(MF_IRID, -480, -300)
    con(graded, "", irid, "BaseColorIn")

    # ---- Roughness: remap ORM.G through [RoughnessMin, RoughnessMax] ----
    # (user note 2026-07-02: old master lacked a per-map roughness slider;
    # a min/max remap gives full control over the map's response curve)
    rmin = sparam("RoughnessMin", 0.0, 0.0, 1.0, "Base", -1300, 100)
    rmax = sparam("RoughnessMax", 1.0, 0.0, 1.5, "Base", -1300, 160)
    rmul = expr(unreal.MaterialExpressionLinearInterpolate, -1100, 160)
    con(rmin, "", rmul, "A")
    con(rmax, "", rmul, "B")
    con(rough_src, rough_pin, rmul, "Alpha")
    fres = expr(unreal.MaterialExpressionFresnel, -1100, 260)
    iratt = sparam("IridescenceRoughnessAtten", 0.0, 0.0, 1.0, "Nikki", -1100, 380)
    attmul = expr(unreal.MaterialExpressionMultiply, -920, 300)
    con(fres, "", attmul, "A")
    con(iratt, "", attmul, "B")
    one = expr(unreal.MaterialExpressionConstant, -920, 420)
    one.set_editor_property("r", 1.0)
    sub = expr(unreal.MaterialExpressionSubtract, -780, 340)
    con(one, "", sub, "A")
    con(attmul, "", sub, "B")
    rfinal = expr(unreal.MaterialExpressionMultiply, -650, 200)
    con(rmul, "", rfinal, "A")
    con(sub, "", rfinal, "B")

    # ---- Metallic (flat scalar on landscape; map * scale on surface) ----
    mscale = sparam("MetallicScale", 0.0, 0.0, 1.0, "Base", -1300, 520)
    if metal_src is not None:
        mmul = expr(unreal.MaterialExpressionMultiply, -1100, 520)
        con(metal_src, metal_pin, mmul, "A")
        con(mscale, "", mmul, "B")
    else:
        mmul = mscale

    # ---- Atmospheric depth fade ----
    depth = expr(unreal.MaterialExpressionPixelDepth, -680, -700)
    d_start = sparam("AtmosphericStart", 5000.0, 0.0, 100000.0, "Atmosphere", -680, -580)
    d_end = sparam("AtmosphericEnd", 50000.0, 1000.0, 500000.0, "Atmosphere", -680, -520)
    d_str = sparam("AtmosphericStrength", 0.0, 0.0, 1.0, "Atmosphere", -680, -460)
    fade_col = vparam("AtmosphericColor", (0.62, 0.72, 0.82, 1), "Atmosphere", -680, -880)

    dsub = expr(unreal.MaterialExpressionSubtract, -500, -650)
    con(depth, "", dsub, "A")
    con(d_start, "", dsub, "B")
    drange = expr(unreal.MaterialExpressionSubtract, -500, -540)
    con(d_end, "", drange, "A")
    con(d_start, "", drange, "B")
    ddiv = expr(unreal.MaterialExpressionDivide, -360, -600)
    con(dsub, "", ddiv, "A")
    con(drange, "", ddiv, "B")
    dsat = expr(unreal.MaterialExpressionSaturate, -240, -600)
    con(ddiv, "", dsat, "")
    dmul = expr(unreal.MaterialExpressionMultiply, -120, -560)
    con(dsat, "", dmul, "A")
    con(d_str, "", dmul, "B")

    atmos = expr(unreal.MaterialExpressionLinearInterpolate, -80, -300)
    con(irid, "ColorOut", atmos, "A")
    con(fade_col, "", atmos, "B")
    con(dmul, "", atmos, "Alpha")

    # ---- Emissive: iridescence emissive * strength, faded by atmosphere ----
    estr = sparam("NikkiEmissiveStrength", 1.0, 0.0, 4.0, "Nikki", -480, -120)
    emul = expr(unreal.MaterialExpressionMultiply, -300, -140)
    con(irid, "EmissiveOut", emul, "A")
    con(estr, "", emul, "B")
    einv = expr(unreal.MaterialExpressionOneMinus, -120, -80)
    con(dmul, "", einv, "")
    efinal = expr(unreal.MaterialExpressionMultiply, 20, -120)
    con(emul, "", efinal, "A")
    con(einv, "", efinal, "B")

    # ---- Substrate Toon BSDF ----
    bsdf = expr(unreal.MaterialExpressionSubstrateToonBSDF, 260, -100)
    con(atmos, "", bsdf, "BaseColor")
    con(rfinal, "", bsdf, "Roughness")
    con(mmul, "", bsdf, "Metallic")
    con(normal_src, normal_pin, bsdf, "Normal")
    con(efinal, "", bsdf, "EmissiveColor")
    MEL.connect_material_property(bsdf, "", unreal.MaterialProperty.MP_FRONT_MATERIAL)

    # (bUsedWithLandscape is not Python-exposed; the editor auto-sets usage
    # flags on first assignment to a Landscape -- bAutomaticallySetUsageInEditor)
    MEL.recompile_material(mat)
    ok = unreal.EditorAssetLibrary.save_asset(full, only_if_is_dirty=False)
    return {"material": full, "saved": bool(ok), "landscape": landscape}


def build_all() -> list:
    return [build("M_Master_Nikki", landscape=False),
            build("M_Master_Nikki_Landscape", landscape=True)]


if __name__ == "__main__":
    import json
    print(json.dumps(build_all(), indent=2))
