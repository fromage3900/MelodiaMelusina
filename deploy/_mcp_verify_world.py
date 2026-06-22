"""Extended verify for Surreal Architecture procedural world pipeline (v2.68).

Launch with --factory-startup for reliable headless runs (~6s vs 10+ min hang):
  blender --background --factory-startup --python deploy/_mcp_verify_world.py
"""
import importlib
import json
import os
import sys
import tempfile

import bpy

print("=== SURREAL WORLD VERIFY v2.69 ===")
print("Blender", bpy.app.version_string)

DEPLOY = os.path.dirname(os.path.abspath(__file__))
LIVE = os.path.join(os.environ.get("APPDATA", ""), "Blender Foundation", "Blender", "5.1", "scripts", "addons")
for p in (DEPLOY, LIVE):
    if p and os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

if "surreal_architecture_gen" in bpy.context.preferences.addons:
    bpy.ops.preferences.addon_disable(module="surreal_architecture_gen")

import surreal_architecture_gen as s

importlib.reload(s)
if not hasattr(bpy.types.Object, "surreal_arch_props"):
    s.register()

try:
    import surreal_arch.integration as _integration

    importlib.reload(_integration)
    _integration.patch_monolith(s)
except Exception as e:
    print(f"Patch monolith skipped: {e}")

from surreal_world import compose, export, library, plans, verify_hooks

all_ok = True
export_root = None
castle_root = None

print("\n--- Library init ---")
try:
    stats = library.ensure_verify_library(s)
    n = library.library_piece_count(stats["collection"])
    need = len(library.VERIFY_LIBRARY_TYPES)
    present = sum(1 for at in library.VERIFY_LIBRARY_TYPES if bpy.data.objects.get(f"_lib_{at}"))
    print(f"  verify_set: {present}/{need} baked={stats['baked']} failed={stats['failed']}")
    if stats["failures"]:
        print(f"  failures: {stats['failures']}")
    if present < need - 1:
        print(f"  !! FAIL: verify library set incomplete ({present}/{need})")
        all_ok = False
except Exception as e:
    print(f"  library_init error: {e}")
    all_ok = False

print("\n--- Castle plan ---")
try:
    plan = plans.spawn_castle_plan(location=(0, 0, 0), size=12.0)
    me = plan.data
    vg = [g.name for g in plan.vertex_groups]
    print(f"  faces={len(me.polygons)} verts={len(me.vertices)} groups={vg}")
    if len(me.polygons) < 5 or "is_gate" not in vg:
        print("  !! FAIL: castle plan topology")
        all_ok = False
except Exception as e:
    print(f"  castle plan error: {e}")
    all_ok = False

print("\n--- Compose COLLECTION ---")
try:
    bpy.context.view_layer.objects.active = plan
    plan.select_set(True)
    root, msg = compose.compose_world(s, bpy.context, plan, "WESTERN_CASTLE", 0.8, "COLLECTION")
    castle_root = root
    print(f"  {msg}")
    inst_count = root.get("surreal_instance_count", 0) if root else 0
    print(f"  instance_count={inst_count}")
    if root is None or inst_count < 3:
        print("  !! FAIL: compose produced too few instances")
        all_ok = False
    if root and root.get("surreal_compose_mode") != "COLLECTION":
        print("  !! FAIL: expected COLLECTION mode")
        all_ok = False
except Exception as e:
    print(f"  compose error: {e}")
    all_ok = False

print("\n--- LD compose metrics (castle) ---")
try:
    metrics = verify_hooks.compose_metrics(castle_root)
    ld_fails = verify_hooks.check_castle_ld_metrics(castle_root)
    print(f"  metrics: {metrics}")
    if ld_fails:
        print(f"  !! FAIL: {ld_fails}")
        all_ok = False
    else:
        print("  ld_castle: OK")
except Exception as e:
    print(f"  ld metrics error: {e}")
    all_ok = False

print("\n--- Recompose idempotency ---")
try:
    before = root.get("surreal_instance_count", 0) if root else 0
    root2, msg2 = compose.recompose_world(s, bpy.context, root)
    after = root2.get("surreal_instance_count", 0) if root2 else 0
    print(f"  before={before} after={after} msg={msg2}")
    if abs(before - after) > 2:
        print("  !! FAIL: recompose instance count drift")
        all_ok = False
    export_root = root2
    castle_root = root2
except Exception as e:
    print(f"  recompose error: {e}")
    all_ok = False

print("\n--- Sacred tag dispatch ---")
try:
    zen = plans.spawn_zen_roji_plan(location=(20, 0, 0))
    zroot, zmsg = compose.compose_world(s, bpy.context, zen, "ZEN_SHRINE", 0.9, "COLLECTION")
    sacred_n = verify_hooks.compose_metrics(zroot).get("sacred", 0) if zroot else 0
    if zroot:
        export_root = zroot
    zen_fails = verify_hooks.check_zen_ld_metrics(zroot)
    print(f"  zen_compose: {zmsg} sacred_instances={sacred_n}")
    if sacred_n < 1 or zen_fails:
        print(f"  !! FAIL: zen LD {zen_fails}")
        all_ok = False
    else:
        print("  ld_zen: OK")
except Exception as e:
    print(f"  sacred tag error: {e}")
    all_ok = False

print("\n--- Zen temple plan compose ---")
try:
    temple = plans.spawn_zen_temple_plan(location=(25, 0, 0))
    troot, tmsg = compose.compose_world(s, bpy.context, temple, "ZEN_SHRINE", 0.9, "COLLECTION")
    tfails = verify_hooks.check_zen_temple_ld_metrics(troot)
    print(f"  temple_compose: {tmsg} metrics={verify_hooks.compose_metrics(troot)}")
    if tfails:
        print(f"  !! FAIL: temple LD {tfails}")
        all_ok = False
    else:
        print("  ld_temple: OK")
except Exception as e:
    print(f"  temple compose error: {e}")
    all_ok = False

print("\n--- Village plan compose ---")
try:
    village = plans.spawn_village_plan(location=(40, 0, 0))
    vroot, vmsg = compose.compose_world(s, bpy.context, village, "WESTERN_VILLAGE", 0.85, "COLLECTION")
    vfails = verify_hooks.check_village_ld_metrics(vroot)
    print(f"  village_compose: {vmsg} metrics={verify_hooks.compose_metrics(vroot)}")
    if vfails:
        print(f"  !! FAIL: village LD {vfails}")
        all_ok = False
    else:
        print("  ld_village: OK")
except Exception as e:
    print(f"  village compose error: {e}")
    all_ok = False

print("\n--- Grid city plan compose ---")
try:
    city = plans.spawn_grid_city_plan(location=(60, 0, 0), grid=4, plot=4.0, street=1.5)
    croot, cmsg = compose.compose_world(s, bpy.context, city, "ASIAN_CITY", 0.85, "COLLECTION")
    cfails = verify_hooks.check_city_ld_metrics(croot)
    print(f"  city_compose: {cmsg} metrics={verify_hooks.compose_metrics(croot)}")
    if cfails:
        print(f"  !! FAIL: city LD {cfails}")
        all_ok = False
    else:
        print("  ld_city: OK")
except Exception as e:
    print(f"  city compose error: {e}")
    all_ok = False

print("\n--- Motte/bailey plan compose ---")
try:
    motte = plans.spawn_motte_bailey_plan(location=(80, 0, 0))
    mroot, mmsg = compose.compose_world(s, bpy.context, motte, "WESTERN_CASTLE", 0.85, "COLLECTION")
    mfails = verify_hooks.check_motte_ld_metrics(mroot)
    print(f"  motte_compose: {mmsg} metrics={verify_hooks.compose_metrics(mroot)}")
    if mfails:
        print(f"  !! FAIL: motte LD {mfails}")
        all_ok = False
    else:
        print("  ld_motte: OK")
except Exception as e:
    print(f"  motte compose error: {e}")
    all_ok = False

print("\n--- One-click castle (COLLECTION, Layer 2 only) ---")
try:
    result = bpy.ops.surreal_arch.one_click_castle(
        style="WESTERN_CASTLE",
        plan_size=12.0,
        with_terrain=False,
        with_vegetation=False,
        with_lighting=False,
        with_komikaze=False,
    )
    if result != {"FINISHED"}:
        raise RuntimeError(f"one_click_castle returned {result}")
    world = bpy.context.active_object
    if world is None or world.type != "EMPTY" or not world.get("surreal_composed_from"):
        raise RuntimeError(f"expected WorldRoot active object, got {world}")
    if world.get("surreal_compose_mode") != "COLLECTION":
        raise RuntimeError("one_click world not COLLECTION mode")
    oc_fails = verify_hooks.check_castle_ld_metrics(world)
    inst = world.get("surreal_instance_count", 0)
    print(f"  one_click: {world.name} instances={inst} mode=COLLECTION")
    if oc_fails:
        print(f"  !! FAIL: one_click LD {oc_fails}")
        all_ok = False
    else:
        print("  one_click_castle: OK")
except Exception as e:
    print(f"  one_click_castle error: {e}")
    all_ok = False

print("\n--- World export manifest ---")
try:
    if export_root is None:
        raise RuntimeError("no export_root from compose tests")
    manifest = export.build_world_manifest(export_root)
    assert manifest.get("format") == "surreal_arch_world_v1"
    assert manifest.get("schema_version", 0) >= 1
    assert manifest.get("instance_count", 0) >= 3
    assert len(manifest.get("hism_groups", [])) >= 1
    val_errors = export.validate_manifest(manifest)
    if val_errors:
        raise RuntimeError(f"manifest validation: {val_errors}")
    hints = {i["ue_material_hint"] for i in manifest["instances"]}
    if not any("/Game/EnvSandbox/" in h for h in hints):
        raise RuntimeError("ue_material_hint paths missing EnvSandbox prefix")
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "test.world.json")
        export.write_world_manifest(export_root, path)
        with open(path, encoding="utf-8") as f:
            side = json.load(f)
        assert side.get("format") == "surreal_arch_world_v1"
    print(f"  manifest instances={manifest.get('instance_count')} hism_groups={len(manifest.get('hism_groups', []))}")
    print("  export_contract: OK")
except Exception as e:
    print(f"  export_contract error: {e}")
    all_ok = False

print("\n--- Per-role FBX export ---")
try:
    if export_root is None:
        raise RuntimeError("no export_root for FBX tier")
    with tempfile.TemporaryDirectory() as td:
        fbx_paths = export.export_role_fbx_batches(bpy.context, export_root, out_dir=td)
        print(f"  fbx_batches={len(fbx_paths)} paths={[os.path.basename(p) for p in fbx_paths]}")
        if len(fbx_paths) < 2:
            print("  !! FAIL: expected at least 2 role FBX batches")
            all_ok = False
        else:
            for p in fbx_paths:
                if not os.path.isfile(p) or os.path.getsize(p) < 64:
                    print(f"  !! FAIL: invalid FBX {p}")
                    all_ok = False
                    break
            else:
                print("  fbx_export: OK")
except Exception as e:
    print(f"  fbx_export error: {e}")
    all_ok = False

print("\n--- World operators ---")
for op_id in ("plan_spawn_zen_roji", "export_world_ue"):
    ok = hasattr(bpy.ops.surreal_arch, op_id)
    print(f"  {op_id}: {ok}")
    if not ok:
        all_ok = False

if not all_ok:
    raise RuntimeError("World verify failed")

print("\n=== WORLD VERIFY OK ===")
