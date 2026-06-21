"""Composer library — bake Layer-1 pieces into SurrealArch_Library."""

from __future__ import annotations

import bpy

LIBRARY_COLLECTION = "SurrealArch_Library"

SURREAL_LIBRARY_SPEC = {
    "KEEP": {"base_radius": 1.4, "height": 7.0},
    "WATCHTOWER": {"base_radius": 1.1, "height": 6.0},
    "GATEHOUSE": {"base_radius": 1.2, "height": 5.5},
    "BARBICAN": {"base_radius": 1.0, "height": 4.5},
    "CURTAIN_WALL": {"rail_length": 4.0, "height": 3.5, "wall_thickness": 0.5},
    "CURVED_WALL": {
        "wall_arc_angle": 90.0,
        "wall_arc_radius": 5.0,
        "wall_height": 3.5,
        "wall_thickness": 0.45,
        "crenel_merlon_count": 8,
    },
    "CHAPEL": {"base_radius": 1.3, "height": 4.0},
    "BELL_TOWER": {"base_radius": 1.0, "height": 7.0},
    "TOWN_HOUSE": {"base_radius": 1.0, "height": 4.0},
    "TAVERN": {"base_radius": 1.2, "height": 3.8},
    "BLACKSMITH": {"base_radius": 1.0, "height": 3.2},
    "STABLE": {"base_radius": 1.0},
    "TOWN_HALL": {"base_radius": 1.6, "height": 5.0},
    "WINDMILL": {"base_radius": 1.0, "height": 6.5},
    "CN_TIERED_PAGODA": {"pagoda_tiers": 4, "pagoda_base_radius": 2.0, "pagoda_tier_height": 1.5},
    "CN_PAILOU": {"base_radius": 1.2, "height": 5.0},
    "CN_MOON_GATE": {"base_radius": 1.5},
    "CN_TING_PAVILION": {"base_radius": 1.5, "height": 4.0},
    "KR_HANOK": {"teahouse_width": 5.0, "teahouse_depth": 4.0, "teahouse_height": 3.0},
    "JP_KURA_STOREHOUSE": {"base_radius": 1.2, "height": 3.5},
    "OBELISK": {"base_radius": 0.7, "height": 5.0},
    "STREET_LAMP": {"height": 3.5},
    "PUBLIC_FOUNTAIN": {"fountain_radius": 1.2},
    "VILLAGE_WELL": {"base_radius": 0.7},
    "MARKET_STALL": {"base_radius": 1.0, "height": 3.0},
    "STYLIZED_TREE": {"height": 4.0},
    "BOULDER_PILE": {"base_radius": 0.8},
    "HERALDIC_BANNER": {"height": 3.5},
    "ZEN_TORII": {"torii_width": 3.6, "torii_height": 4.2},
    "ZEN_TEAHOUSE": {"teahouse_width": 5.0, "teahouse_depth": 4.0},
    "ZEN_LANTERN": {"zen_lantern_height": 1.6},
    "ZEN_STONE_GARDEN": {"stone_garden_size": 6.0},
    "ZEN_BRIDGE": {"zen_bridge_span": 4.0, "zen_bridge_rise": 0.6},
}


def library_collection(create=True):
    coll = bpy.data.collections.get(LIBRARY_COLLECTION)
    if coll is None and create:
        coll = bpy.data.collections.new(LIBRARY_COLLECTION)
        if coll.name not in [c.name for c in bpy.context.scene.collection.children]:
            bpy.context.scene.collection.children.link(coll)
        coll.hide_viewport = True
        coll.hide_render = True
    return coll


def bake_library_piece(monolith, arch_type, params, target_coll, force=False):
    """Headless-safe: mesh/object API instead of bpy.ops.mesh.primitive_cube_add."""
    lib_name = f"_lib_{arch_type}"
    existing = bpy.data.objects.get(lib_name)
    if existing and not force:
        return existing, False
    if existing:
        bpy.data.objects.remove(existing, do_unlink=True)

    mesh = bpy.data.meshes.new(f"{lib_name}_host")
    obj = bpy.data.objects.new(lib_name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    if not hasattr(obj, "surreal_arch_props"):
        bpy.data.objects.remove(obj, do_unlink=True)
        return None, False

    p = obj.surreal_arch_props
    auto_flag = getattr(monolith, "_AUTO_UPDATE_RUNNING", False)
    monolith._AUTO_UPDATE_RUNNING = True
    try:
        try:
            p.arch_type = arch_type
        except TypeError:
            bpy.data.objects.remove(obj, do_unlink=True)
            return None, False
        for k, v in params.items():
            try:
                setattr(p, k, v)
            except Exception:
                pass
    finally:
        monolith._AUTO_UPDATE_RUNNING = auto_flag

    try:
        bpy.ops.surreal_arch.generate()
        for mod in list(obj.modifiers):
            if mod.name.startswith("SurrealArch"):
                try:
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                except Exception:
                    pass
                break
    except Exception as e:
        print(f"[SurrealWorld] Library bake failed for {arch_type}: {e}")

    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    target_coll.objects.link(obj)
    obj.hide_viewport = True
    obj.hide_render = True
    obj.select_set(False)
    return obj, True


def init_library(monolith, force_refresh=False, types_only=None):
    coll = library_collection(create=True)
    baked, skipped, failed = 0, 0, 0
    failures = []
    spec = SURREAL_LIBRARY_SPEC
    if types_only:
        spec = {k: v for k, v in spec.items() if k in types_only}
    for arch_type, params in spec.items():
        obj, did_bake = bake_library_piece(monolith, arch_type, params, coll, force=force_refresh)
        if obj is None:
            failed += 1
            failures.append(arch_type)
        elif did_bake:
            baked += 1
        else:
            skipped += 1
    return {"baked": baked, "skipped": skipped, "failed": failed, "failures": failures, "collection": coll}


def library_piece_count(coll=None):
    coll = coll or library_collection(create=False)
    if coll is None:
        return 0
    return len([o for o in coll.objects if o.name.startswith("_lib_")])


VERIFY_LIBRARY_TYPES = frozenset({
    "KEEP", "CURTAIN_WALL", "WATCHTOWER", "GATEHOUSE", "TOWN_HOUSE", "MARKET_STALL", "CHAPEL",
    "TOWN_HALL", "TAVERN", "BLACKSMITH", "VILLAGE_WELL", "BELL_TOWER",
    "KR_HANOK", "CN_TING_PAVILION", "JP_KURA_STOREHOUSE", "CN_TIERED_PAGODA", "CN_PAILOU", "CN_MOON_GATE",
    "ZEN_TORII", "ZEN_TEAHOUSE", "ZEN_LANTERN", "ZEN_STONE_GARDEN", "ZEN_BRIDGE", "BOULDER_PILE",
})


def ensure_verify_library(monolith):
    missing = []
    for at in VERIFY_LIBRARY_TYPES:
        if bpy.data.objects.get(f"_lib_{at}") is None:
            missing.append(at)
    if missing:
        return init_library(monolith, force_refresh=False, types_only=set(missing))
    coll = library_collection(create=False)
    return {
        "baked": 0,
        "skipped": len(VERIFY_LIBRARY_TYPES),
        "failed": 0,
        "failures": [],
        "collection": coll,
    }
