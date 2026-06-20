"""Compositing texture catalog: /Game/Textures + SDF/Textures roles for masters/instances.

Run audit (no editor):
  python Content/Python/portfolio_texture_catalog.py

Used by integrate_compositing_textures.py and setup_universal_instances.py.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTENT = PROJECT_ROOT / "Content"
REPORT = PROJECT_ROOT / "Saved" / "Audit" / "compositing_texture_catalog.json"

SDF = "/Game/EnvSandbox/Materials/SDF/Textures"
TEX = "/Game/Textures"

# Schema targets (portfolio SDF folder)
MARBLE = {
    "warm_stone": f"{SDF}/Marble/Marble_7_-_512x512.Marble_7_-_512x512",
    "cool_stone": f"{SDF}/Marble/Marble_3_-_512x512.Marble_3_-_512x512",
    "worn": f"{SDF}/Marble/Marble_5_-_512x512.Marble_5_-_512x512",
    "dark": f"{SDF}/Marble/Marble_9_-_512x512.Marble_9_-_512x512",
    "light": f"{SDF}/Marble/Marble_1_-_512x512.Marble_1_-_512x512",
}
HEIGHT = {
    "perlin": f"{TEX}/sbs_-_noise_texture_pack_-_512x512/512x512/Perlin/Perlin_1_-_512x512.Perlin_1_-_512x512",
    "perlin_sdf": f"{SDF}/Perlin/Perlin_1_-_512x512.Perlin_1_-_512x512",
}
MASK = {
    "voronoi_crack": f"{SDF}/Voronoi/Voronoi_2_-_512x512.Voronoi_2_-_512x512",
    "voronoi_swirl": f"{SDF}/Voronoi/Voronoi_11_-_512x512.Voronoi_11_-_512x512",
}
# /Game/Textures compositing library (SBS packs)
COMPOSITING = {
    "crack_overlay": f"{TEX}/sbs_-_noise_texture_pack_-_512x512/512x512/Cracks/Cracks_3_-_512x512.Cracks_3_-_512x512",
    "crack_heavy": f"{TEX}/sbs_-_noise_texture_pack_-_512x512/512x512/Cracks/Cracks_10_-_512x512.Cracks_10_-_512x512",
    "noise_fine": f"{TEX}/sbs_-_noise_texture_pack_-_512x512/512x512/Perlin/Perlin_10_-_512x512.Perlin_10_-_512x512",
    "abstract_a": f"{TEX}/sbs_-_seamless_abstract_pack_-_512x512/512x512/Texture_512x512_1.Texture_512x512_1",
    "gradient_warm": f"{TEX}/sbs_-_gradient_texture_pack_-_512x512/512x512/Basic/Horizontal_1_-_512x512.Horizontal_1_-_512x512",
    "space_nebula": (
        f"{TEX}/sbs_-_seamless_space_backgrounds_-_large_1024x1024/"
        "Large_1024x1024/Blue_Nebula/Blue_Nebula_1_-_1024x1024.Blue_Nebula_1_-_1024x1024"
    ),
}

# Fallback chains (first existing wins in editor)
def _chain(*paths: str) -> list[str]:
    return list(paths)


MASTER_TEXTURE_DEFAULTS: dict[str, list[str]] = {
    "Albedo": _chain(MARBLE["warm_stone"], MARBLE["light"], COMPOSITING["abstract_a"]),
    "NormalMap": _chain(
        "/Engine/EngineMaterials/DefaultNormal.DefaultNormal",
        HEIGHT["perlin"],
        HEIGHT["perlin_sdf"],
    ),
    "ORM": _chain(MARBLE["worn"], COMPOSITING["noise_fine"]),
    "HeightMap": _chain(HEIGHT["perlin"], HEIGHT["perlin_sdf"], COMPOSITING["noise_fine"]),
    "LayerB_Albedo": _chain(MASK["voronoi_crack"], COMPOSITING["crack_overlay"]),
    "LayerB_NormalMap": _chain(
        "/Engine/EngineMaterials/DefaultNormal.DefaultNormal",
        COMPOSITING["noise_fine"],
    ),
    "LayerB_ORM": _chain(COMPOSITING["crack_heavy"], MARBLE["dark"]),
    "LayerB_HeightMap": _chain(COMPOSITING["crack_heavy"], HEIGHT["perlin"], MASK["voronoi_crack"]),
    "DetailNormal": _chain(
        "/Engine/EngineMaterials/DefaultNormal.DefaultNormal",
        COMPOSITING["noise_fine"],
    ),
    "SparkleMask": _chain(
        f"{TEX}/sbs_-_noise_texture_pack_-_512x512/512x512/Perlin/Perlin_10_-_512x512.Perlin_10_-_512x512",
        HEIGHT["perlin"],
    ),
    "FairyGlyphMask": _chain(COMPOSITING["abstract_a"], MASK["voronoi_swirl"]),
    "MotifMask": _chain(COMPOSITING["abstract_a"], MASK["voronoi_crack"]),
}

# M_Master_Toon_Unified / M_Master_SDF_Toon (TextureSampleParameter2D, no Albedo slot)
UNIFIED_SDF_TEXTURE_DEFAULTS: dict[str, list[str]] = {
    "NormalMap": _chain(
        "/Engine/EngineMaterials/DefaultNormal.DefaultNormal",
        HEIGHT["perlin"],
        HEIGHT["perlin_sdf"],
    ),
    "RoughnessMap": _chain(MARBLE["worn"], COMPOSITING["noise_fine"], HEIGHT["perlin"]),
    "HeightMap": _chain(HEIGHT["perlin"], HEIGHT["perlin_sdf"], COMPOSITING["crack_overlay"]),
}

INSTANCE_TEXTURE_DEFAULTS: dict[str, dict[str, list[str]]] = {
    "MI_Universal_Default": {
        "Albedo": _chain(MARBLE["warm_stone"]),
        "HeightMap": _chain(HEIGHT["perlin"]),
    },
    "MI_Universal_LayeredStone": {
        "Albedo": _chain(MARBLE["warm_stone"]),
        "LayerB_Albedo": _chain(MASK["voronoi_crack"], COMPOSITING["crack_overlay"]),
        "HeightMap": _chain(HEIGHT["perlin"]),
        "LayerB_HeightMap": _chain(COMPOSITING["crack_heavy"]),
    },
    "MI_Universal_CrackedClay": {
        "Albedo": _chain(MARBLE["worn"]),
        "LayerB_Albedo": _chain(COMPOSITING["crack_heavy"]),
        "HeightMap": _chain(HEIGHT["perlin"]),
    },
    "MI_Universal_WetStone": {
        "Albedo": _chain(MARBLE["cool_stone"]),
        "HeightMap": _chain(HEIGHT["perlin"]),
    },
    "MI_Universal_MossStone": {
        "Albedo": _chain(MARBLE["dark"]),
        "HeightMap": _chain(HEIGHT["perlin"]),
    },
    "MI_Universal_SnowDusted": {
        "Albedo": _chain(MARBLE["light"]),
        "HeightMap": _chain(HEIGHT["perlin"]),
    },
    "MI_Universal_DeepSpace": {
        "Albedo": _chain(COMPOSITING["space_nebula"], MARBLE["dark"]),
    },
    "MI_Universal_CelestialNebula": {
        "Albedo": _chain(COMPOSITING["space_nebula"]),
        "SparkleMask": _chain(f"/Game/Alphas_Sparkles/T_Spark_Twinkle8.T_Spark_Twinkle8"),
    },
    "MI_Trimsheet_VariationCracks": {
        "Albedo": _chain(MARBLE["warm_stone"]),
        "LayerB_Albedo": _chain(COMPOSITING["crack_overlay"]),
        "HeightMap": _chain(HEIGHT["perlin"]),
        "LayerB_HeightMap": _chain(COMPOSITING["crack_heavy"]),
    },
}

# Any instance with TextureWeight / layer weights but no explicit textures gets base pack
INSTANCE_FALLBACK_TEXTURES: dict[str, list[str]] = {
    "Albedo": MASTER_TEXTURE_DEFAULTS["Albedo"],
    "HeightMap": MASTER_TEXTURE_DEFAULTS["HeightMap"],
    "NormalMap": MASTER_TEXTURE_DEFAULTS["NormalMap"],
    "LayerB_Albedo": MASTER_TEXTURE_DEFAULTS["LayerB_Albedo"],
    "LayerB_HeightMap": MASTER_TEXTURE_DEFAULTS["LayerB_HeightMap"],
    "DetailNormal": MASTER_TEXTURE_DEFAULTS["DetailNormal"],
    "SparkleMask": MASTER_TEXTURE_DEFAULTS["SparkleMask"],
}

# Keyword rules: first match wins (order matters)
INSTANCE_TEXTURE_RULES: list[tuple[tuple[str, ...], dict[str, list[str]]]] = [
    (
        ("deepspace", "nebula", "constellation", "celestial", "galaxy", "cosmic", "starfield"),
        {
            "Albedo": _chain(COMPOSITING["space_nebula"], MARBLE["dark"]),
            "HeightMap": _chain(HEIGHT["perlin"], COMPOSITING["noise_fine"]),
        },
    ),
    (
        ("ember", "volcanic", "ash", "lava"),
        {
            "Albedo": _chain(MARBLE["dark"], MARBLE["worn"]),
            "HeightMap": _chain(MASK["voronoi_crack"], HEIGHT["perlin"]),
            "LayerB_Albedo": _chain(COMPOSITING["crack_heavy"]),
        },
    ),
    (
        ("crack", "clay", "trim", "variationcracks", "weathered", "worn"),
        {
            "Albedo": _chain(MARBLE["worn"], MARBLE["warm_stone"]),
            "LayerB_Albedo": _chain(COMPOSITING["crack_heavy"], COMPOSITING["crack_overlay"]),
            "LayerB_HeightMap": _chain(COMPOSITING["crack_heavy"], MASK["voronoi_crack"]),
            "HeightMap": _chain(HEIGHT["perlin"], MASK["voronoi_crack"]),
        },
    ),
    (
        ("snow", "ice", "frost", "crust"),
        {
            "Albedo": _chain(MARBLE["light"], COMPOSITING["gradient_warm"]),
            "HeightMap": _chain(HEIGHT["perlin"], COMPOSITING["noise_fine"]),
            "SparkleMask": _chain(
                f"{TEX}/sbs_-_noise_texture_pack_-_512x512/512x512/Perlin/Perlin_10_-_512x512.Perlin_10_-_512x512"
            ),
        },
    ),
    (
        ("moss", "garden", "foliage", "grass", "fern"),
        {
            "Albedo": _chain(MARBLE["dark"], MARBLE["cool_stone"]),
            "HeightMap": _chain(HEIGHT["perlin"], MASK["voronoi_swirl"]),
        },
    ),
    (
        ("gold", "gild", "filigree", "ornament", "baroque"),
        {
            "Albedo": _chain(MARBLE["warm_stone"], MARBLE["worn"]),
            "HeightMap": _chain(MASK["voronoi_crack"], HEIGHT["perlin"]),
            "LayerB_Albedo": _chain(MASK["voronoi_swirl"], COMPOSITING["crack_overlay"]),
        },
    ),
    (
        ("wood", "timber", "bark"),
        {
            "Albedo": _chain(MARBLE["worn"], MARBLE["warm_stone"]),
            "HeightMap": _chain(HEIGHT["perlin"], COMPOSITING["noise_fine"]),
        },
    ),
    (
        ("ancientruin", "ruin", "cathedral", "hybrid"),
        {
            "Albedo": _chain(MARBLE["cool_stone"], MARBLE["worn"]),
            "LayerB_Albedo": _chain(COMPOSITING["crack_overlay"], MASK["voronoi_crack"]),
            "HeightMap": _chain(HEIGHT["perlin_sdf"], HEIGHT["perlin"]),
        },
    ),
    (
        ("forest", "mossy", "fern", "canopy"),
        {
            "Albedo": _chain(MARBLE["dark"], COMPOSITING["abstract_a"]),
            "HeightMap": _chain(MASK["voronoi_swirl"], HEIGHT["perlin"]),
        },
    ),
    (
        ("frost", "sakura"),
        {
            "Albedo": _chain(MARBLE["light"], COMPOSITING["gradient_warm"]),
            "HeightMap": _chain(COMPOSITING["noise_fine"], HEIGHT["perlin"]),
        },
    ),
    (
        ("ocean", "foam", "wet", "cobble", "rain", "storm"),
        {
            "Albedo": _chain(MARBLE["cool_stone"], MARBLE["dark"]),
            "HeightMap": _chain(HEIGHT["perlin"], COMPOSITING["noise_fine"]),
            "DetailNormal": _chain("/Engine/EngineMaterials/DefaultNormal.DefaultNormal"),
        },
    ),
    (
        ("desert", "sand", "dune"),
        {
            "Albedo": _chain(MARBLE["light"], COMPOSITING["gradient_warm"]),
            "HeightMap": _chain(HEIGHT["perlin"], COMPOSITING["noise_fine"]),
        },
    ),
    (
        ("stone", "rock", "masonry", "layered", "brick"),
        {
            "Albedo": _chain(MARBLE["warm_stone"], MARBLE["cool_stone"]),
            "LayerB_Albedo": _chain(MASK["voronoi_crack"], COMPOSITING["crack_overlay"]),
            "HeightMap": _chain(HEIGHT["perlin"], HEIGHT["perlin_sdf"]),
        },
    ),
    (
        ("crystal", "glass", "prism", "irid", "opal"),
        {
            "Albedo": _chain(COMPOSITING["abstract_a"], MARBLE["cool_stone"]),
            "HeightMap": _chain(COMPOSITING["noise_fine"], HEIGHT["perlin"]),
        },
    ),
    (
        ("fairy", "dream", "blush", "lavender", "peach", "cotton", "pastel", "satin", "magical"),
        {
            "Albedo": _chain(COMPOSITING["abstract_a"], MARBLE["light"]),
            "SparkleMask": _chain(
                f"{TEX}/sbs_-_noise_texture_pack_-_512x512/512x512/Perlin/Perlin_10_-_512x512.Perlin_10_-_512x512"
            ),
            "HeightMap": _chain(HEIGHT["perlin"], COMPOSITING["noise_fine"]),
        },
    ),
    (
        ("ink", "temporal", "impression", "wind", "smear"),
        {
            "Albedo": _chain(MARBLE["light"], COMPOSITING["abstract_a"]),
            "HeightMap": _chain(HEIGHT["perlin"], COMPOSITING["noise_fine"]),
        },
    ),
]


def scan_disk_catalog() -> dict:
    tex_root = CONTENT / "Textures"
    sdf_root = CONTENT / "EnvSandbox" / "Materials" / "SDF" / "Textures"
    packs: dict[str, int] = {}
    if tex_root.exists():
        for p in tex_root.rglob("*.uasset"):
            rel = p.relative_to(tex_root)
            key = rel.parts[0] if len(rel.parts) > 1 else "(root)"
            packs[key] = packs.get(key, 0) + 1
    sdf_count = len(list(sdf_root.rglob("*.uasset"))) if sdf_root.exists() else 0
    return {
        "textures_pack_counts": packs,
        "textures_total": sum(packs.values()),
        "sdf_textures_total": sdf_count,
        "roles": {
            "marble": MARBLE,
            "height": HEIGHT,
            "mask": MASK,
            "compositing": COMPOSITING,
        },
    }


def _param_name(expr) -> str | None:
    for prop in ("parameter_name", "ParameterName"):
        try:
            raw = expr.get_editor_property(prop)
            if raw is not None:
                return str(raw)
        except Exception:
            continue
    return None


def _master_default_map(material_path: str) -> dict[str, list[str]]:
    stem = material_path.rsplit("/", 1)[-1].lower()
    if "universal" in stem:
        return MASTER_TEXTURE_DEFAULTS
    if stem in ("m_master_toon_unified", "m_master_sdf_toon"):
        return UNIFIED_SDF_TEXTURE_DEFAULTS
    return {**MASTER_TEXTURE_DEFAULTS, **UNIFIED_SDF_TEXTURE_DEFAULTS}


def resolve_instance_texture_map(instance_name: str) -> dict[str, list[str]]:
    """Merge explicit preset, keyword rules, and fallbacks for an MI name."""
    merged: dict[str, list[str]] = {}
    for pname, candidates in INSTANCE_FALLBACK_TEXTURES.items():
        merged[pname] = list(candidates)
    key = instance_name.lower().replace("mi_universal_", "").replace("mi_", "")
    for keywords, spec in INSTANCE_TEXTURE_RULES:
        if any(kw in key for kw in keywords):
            for pname, candidates in spec.items():
                merged[pname] = list(candidates)
            break
    explicit = INSTANCE_TEXTURE_DEFAULTS.get(instance_name, {})
    for pname, candidates in explicit.items():
        merged[pname] = list(candidates)
    return merged


def apply_master_defaults(material, material_path: str | None = None) -> dict[str, str]:
    """Set default textures on master parameter nodes (editor only)."""
    import unreal
    import material_lib as lib

    if material_path is None:
        try:
            material_path = str(material.get_path_name().split(".", 1)[0])
        except Exception:
            material_path = ""
    defaults = _master_default_map(material_path)
    wired: dict[str, str] = {}
    param_exprs: dict[str, object] = {}
    expr_owners: dict[str, object] = {}
    for expr, owner in lib.iter_texture_parameter_expressions(material):
        pname = _param_name(expr)
        if pname and pname not in param_exprs:
            param_exprs[pname] = expr
            expr_owners[pname] = owner

    texture_params = lib.texture_parameter_names(material)
    if not param_exprs and texture_params:
        unreal.log_warning(
            f"[texture_catalog] master {material_path}: params {texture_params[:12]} "
            "found via MaterialEditingLibrary but no graph nodes located"
        )

    modified_owners: set[object] = set()
    for pname, candidates in defaults.items():
        expr = param_exprs.get(pname)
        if not expr:
            continue
        current = None
        me = unreal.MaterialEditingLibrary
        if hasattr(me, "get_material_default_texture_parameter_value"):
            try:
                current = me.get_material_default_texture_parameter_value(material, pname)
            except Exception:
                current = None
        if current and not lib.is_placeholder_texture(current):
            wired[pname] = lib.texture_asset_path(current) or ""
            continue
        path = lib.set_expression_texture(expr, candidates)
        if path:
            wired[pname] = path
            owner = expr_owners.get(pname)
            if owner:
                modified_owners.add(owner)
        else:
            unreal.log_warning(f"[texture_catalog] no asset for master {pname} on {material_path}")

    for owner in modified_owners:
        lib.save_package(owner)
    if not wired and texture_params:
        unmatched = [p for p in texture_params if p in defaults]
        if unmatched:
            unreal.log_warning(
                f"[texture_catalog] master {material_path}: {len(texture_params)} texture params "
                f"{texture_params[:12]} — wired 0, unmatched defaults for {unmatched[:8]}"
            )
        else:
            unreal.log_warning(
                f"[texture_catalog] master {material_path}: {len(texture_params)} texture params "
                f"{texture_params[:12]} — wired 0 (param names not in catalog defaults)"
            )
    if wired:
        try:
            unreal.MaterialEditingLibrary.recompile_material(material)
        except Exception:
            pass
    return wired


def apply_instance_texture_defaults(instance, instance_name: str, existing: dict | None = None) -> dict[str, str]:
    """Fill instance texture params from catalog rules + fallbacks."""
    import material_lib as lib

    existing = dict(existing or {})
    spec = resolve_instance_texture_map(instance_name)
    wired: dict[str, str] = {}
    for pname, candidates in spec.items():
        if pname in existing:
            continue
        path = lib.set_instance_texture(instance, pname, candidates)
        if path:
            wired[pname] = path
    return wired


def refresh_all_instance_textures(instances_root: str = "/Game/EnvSandbox/Materials/Instances") -> dict[str, dict]:
    """Walk portfolio MI folders and apply compositing texture defaults."""
    import unreal
    import material_lib as lib

    results: dict[str, dict] = {}
    if not unreal.EditorAssetLibrary.does_directory_exist(instances_root):
        return results
    for asset_path in unreal.EditorAssetLibrary.list_assets(instances_root, recursive=True, include_folder=False):
        if not asset_path.startswith("/Game/") or "/MI_" not in asset_path:
            continue
        base = asset_path.split(".", 1)[0]
        stem = base.rsplit("/", 1)[-1]
        if not stem.startswith("MI_"):
            continue
        inst = unreal.load_asset(f"{base}.{stem}")
        if not inst:
            continue
        wired = apply_instance_texture_defaults(inst, stem, {})
        if wired:
            lib.save_package(inst)
        results[base] = wired
    return results


def main() -> int:
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **scan_disk_catalog(),
        "master_defaults": {k: v for k, v in MASTER_TEXTURE_DEFAULTS.items()},
        "instance_presets": list(INSTANCE_TEXTURE_DEFAULTS.keys()),
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(REPORT), "textures_total": report["textures_total"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
