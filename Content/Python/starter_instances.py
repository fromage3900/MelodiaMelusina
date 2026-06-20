"""Curated starter MI_* set for M_Master_Toon_Universal (10 showcase instances).

Each instance isolates ONE master capability (Nikki, flower shadow, nebula, magic, etc.).
Legacy MI_Universal_* under Instances/Environment are deprecated — not deleted; use
archive_unused_instances.py to move them to Instances/_Archive.

Imported by rebuild_material_instances.py, apply_starter_instances.py, and docs.
"""
from __future__ import annotations

import material_lib as lib

MASTER = f"{lib.MASTER_DIR}/M_Master_Toon_Universal.M_Master_Toon_Universal"
SHOWCASE_DIR = f"{lib.MATERIALS_ROOT}/Instances/Showcase"
LEGACY_ENV_DIR = lib.ENV_INST_DIR
ARCHIVE_ROOT = f"{lib.MATERIALS_ROOT}/Instances/_Archive"

# Canonical 10 starters — one capability each (see Docs/MATERIAL_INTEGRATION.md)
STARTER_INSTANCES: list[dict] = [
    {
        "name": "MI_Show_Default",
        "purpose": "Default showcase — neutral tint, full texture weight, zero stylization",
        "profile": "TP_Default",
        "vectors": {"BaseTint": (0.62, 0.58, 0.55, 1.0)},
        "scalars": {
            "TextureWeight": 1.0,
            "UVScale": 1.0,
            "Roughness": 0.65,
            "Metallic": 0.0,
        },
        "key_params": "BaseTint, TextureWeight, Roughness (Palette + Hybrid)",
    },
    {
        "name": "MI_Show_StoneCliff",
        "purpose": "Stone surface — triplanar cliff with MF_ParallaxCore depth + normal power",
        "profile": "TP_Stone",
        "vectors": {"BaseTint": (0.44, 0.41, 0.38, 1.0)},
        "scalars": {
            "TextureWeight": 0.9,
            "Roughness": 0.85,
            "TriplanarTiling": 320.0,
            "ParallaxStrength": 0.55,
            "ParallaxScale": 0.06,
            "ParallaxSteps": 10.0,
            "ParallaxMode": 2.0,
            "NormalStrength": 1.35,
            "NormalPower": 0.85,
            "MacroVariationStrength": 0.6,
            "MacroScale": 0.0006,
            "DetailStrength": 0.6,
            "DetailTiling": 12.0,
        },
        "switches": {"bTriplanar": True},
        "key_params": "ParallaxStrength, ParallaxSteps, NormalStrength (Parallax + Triplanar)",
    },
    {
        "name": "MI_Show_CherryBlossom",
        "purpose": "Flower shadow garden — projected petal shadows + sparkle on soft pink",
        "profile": "TP_Default",
        "vectors": {
            "BaseTint": (1.0, 0.76, 0.85, 1.0),
            "ShadowFlowerColor": (0.92, 0.46, 0.72, 1.0),
            "SparkleColor": (1.0, 0.95, 0.85, 1.0),
        },
        "scalars": {
            "TextureWeight": 0.3,
            "Roughness": 0.7,
            "PastelLift": 0.45,
            "ShadowFlowerStrength": 0.7,
            "ShadowFlowerScale": 5.0,
            "SparkleIntensity": 1.4,
            "SparkleScale": 11.0,
        },
        "textures": {"SparkleMask": "twinkle", "FairyGlyphMask": "flower"},
        "key_params": "ShadowFlowerStrength, ShadowFlowerScale (FlowerShadow)",
    },
    {
        "name": "MI_Show_CelestialNebula",
        "purpose": "Nebula shading — MF_SpaceParallax constellation ramp + parallax nebula + galaxy",
        "profile": "TP_Default",
        "vectors": {
            "BaseTint": (0.05, 0.06, 0.12, 1.0),
            "ConstellationRampLow": (0.02, 0.03, 0.10, 1.0),
            "ConstellationRampMid": (0.45, 0.22, 0.55, 1.0),
            "ConstellationRampHigh": (0.88, 0.76, 1.0, 1.0),
            "GlowColor": (0.7, 0.6, 1.0, 1.0),
        },
        "scalars": {
            "TextureWeight": 0.15,
            "Roughness": 0.6,
            "ConstellationStrength": 0.85,
            "ConstellationScale": 1.8,
            "CelestialNebulaStrength": 0.95,
            "CelestialNebulaScale": 0.42,
            "CelestialGalaxyStrength": 0.5,
            "CelestialStarIntensity": 1.4,
            "CelestialToonSteps": 4.0,
            "GlowIntensity": 0.35,
        },
        "textures": {"StarMap": "twinkle", "SparkleMask": "twinkle"},
        "key_params": "CelestialNebulaStrength, ConstellationRamp*, StarMap (Celestial)",
    },
    {
        "name": "MI_Show_FairyHearts",
        "purpose": "Magic / fairy — heart motif, fairy dust, partial henshin wipe",
        "profile": "TP_Default",
        "vectors": {
            "BaseTint": (0.9, 0.72, 0.88, 1.0),
            "FairyDustColor": (1.0, 0.92, 0.98, 1.0),
            "MotifColor": (1.0, 0.45, 0.72, 1.0),
            "MagicalPalette": (1.0, 0.72, 0.86, 1.0),
        },
        "scalars": {
            "TextureWeight": 0.3,
            "Roughness": 0.5,
            "FairyMotifStyle": 1.0,
            "FairyDustIntensity": 1.0,
            "FairyDustScale": 14.0,
            "FairyHighlightThreshold": 0.35,
            "MagicalTransform": 0.35,
            "MotifScale": 6.0,
            "TransformGlow": 3.0,
            "WipeSoftness": 0.25,
        },
        "textures": {"FairyGlyphMask": "heart", "MotifMask": "heart", "SparkleMask": "sparkle4"},
        "key_params": "MagicalTransform, MotifColor, FairyDustIntensity (Magical + FairyDust)",
    },
    {
        "name": "MI_Show_SkinSoft",
        "purpose": "Nikki-style character skin — wrap shadow, cheek warmth, soft pastel base",
        "profile": "TP_Default",
        "vectors": {
            "BaseTint": (1.0, 0.86, 0.80, 1.0),
            "DreamTint": (1.0, 0.92, 0.88, 1.0),
            "SkinShadowTint": (0.92, 0.7, 0.66, 1.0),
            "CheekWarmthColor": (1.0, 0.72, 0.62, 1.0),
            "RimColor": (1.0, 0.88, 0.92, 1.0),
        },
        "scalars": {
            "TextureWeight": 0.35,
            "Roughness": 0.42,
            "PastelLift": 0.18,
            "RimIntensity": 0.12,
            "SkinWrapStrength": 0.72,
            "SkinWrapRadius": 0.62,
            "SkinShadowStrength": 0.48,
            "CheekWarmthStrength": 0.38,
            "CheekWarmthBias": 0.45,
        },
        "key_params": "SkinWrapStrength, PastelLift, CheekWarmthStrength (Character + Nikki)",
    },
    {
        "name": "MI_Show_ForestFoliage",
        "purpose": "Foliage / forest floor — mossy green with dreamy shadow tint",
        "profile": "TP_Default",
        "vectors": {
            "BaseTint": (0.28, 0.32, 0.22, 1.0),
            "ShadowDreamTint": (0.18, 0.22, 0.12, 1.0),
            "MossColor": (0.25, 0.42, 0.2, 1.0),
        },
        "scalars": {
            "TextureWeight": 0.9,
            "Roughness": 0.92,
            "ShadowDreamStrength": 0.45,
            "ShadowSoftness": 0.75,
            "MossConcavityStrength": 0.55,
            "MossCurvatureSens": 2.2,
        },
        "key_params": "ShadowDreamStrength, MossConcavityStrength (World + ShadowDream)",
    },
    {
        "name": "MI_Show_ContactRimHero",
        "purpose": "Cinematic — contact rim + atmospheric distance fade",
        "profile": "TP_Default",
        "vectors": {
            "BaseTint": (0.5, 0.52, 0.58, 1.0),
            "ContactRimColor": (1.0, 0.95, 0.88, 1.0),
            "AtmosphericFadeColor": (0.62, 0.72, 0.82, 1.0),
        },
        "scalars": {
            "TextureWeight": 0.7,
            "Roughness": 0.6,
            "ContactRimStrength": 1.0,
            "ContactRimPower": 5.0,
            "DistanceFadeStrength": 0.6,
            "DistanceFadeStart": 4500.0,
            "DistanceFadeEnd": 18000.0,
        },
        "key_params": "ContactRimStrength, DistanceFadeStrength (Cinematic)",
    },
    {
        "name": "MI_Show_ElementHydro",
        "purpose": "Elemental hydro — wet iridescent glass with emissive boost",
        "profile": "TP_Default",
        "vectors": {
            "BaseTint": (0.34, 0.52, 0.66, 1.0),
            "IridescenceTint": (0.8, 0.7, 0.95, 1.0),
        },
        "scalars": {
            "TextureWeight": 0.2,
            "Roughness": 0.14,
            "Metallic": 0.0,
            "ElementType": 2.0,
            "ElementStrength": 0.8,
            "ElementEmissiveBoost": 0.4,
            "Iridescence": 0.3,
            "WetnessStrength": 0.6,
            "WetnessRoughness": 0.1,
        },
        "key_params": "ElementType=2 (Hydro), ElementStrength, WetnessStrength",
    },
    {
        "name": "MI_Show_InkWash",
        "purpose": "Stylized ink wash — temporal boil + smear + wind",
        "profile": "TP_Default",
        "vectors": {
            "BaseTint": (0.86, 0.84, 0.80, 1.0),
            "DreamTint": (0.92, 0.86, 0.98, 1.0),
        },
        "scalars": {
            "TextureWeight": 0.55,
            "Roughness": 0.75,
            "TemporalStrength": 0.7,
            "BoilIntensity": 0.12,
            "SmearStrength": 0.14,
            "WindSpeed": 0.2,
            "NoiseScale": 1.8,
        },
        "textures": {"MotifMask": "bow"},
        "key_params": "TemporalStrength, SmearStrength, WindSpeed (Temporal)",
    },
]

STARTER_NAMES: frozenset[str] = frozenset(s["name"] for s in STARTER_INSTANCES)

# Legacy MI_Universal_* names superseded by starters (for archive / migration docs)
LEGACY_ALIASES: dict[str, str] = {
    "MI_Universal_Default": "MI_Show_Default",
    "MI_Universal_LayeredStone": "MI_Show_StoneCliff",
    "MI_Universal_DreamyPastel": "MI_Show_SkinSoft",
    "MI_Universal_CherryBlossom": "MI_Show_CherryBlossom",
    "MI_Universal_CelestialNebula": "MI_Show_CelestialNebula",
    "MI_Universal_FairyHearts": "MI_Show_FairyHearts",
    "MI_Universal_ForestFloor": "MI_Show_ForestFoliage",
    "MI_Universal_ContactRimHero": "MI_Show_ContactRimHero",
    "MI_Universal_ElementHydro": "MI_Show_ElementHydro",
    "MI_Universal_TemporalInk": "MI_Show_InkWash",
}
