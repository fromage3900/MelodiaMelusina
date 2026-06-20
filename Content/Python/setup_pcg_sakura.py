"""Sakura PCG Phase 0 + Phase 1 — greybox scatter kit + one stock ground-cover graph.

De-risked scope (see professional review):
  - Phase 0: verify materials, resolve greybox grass mesh, exclusion guide volumes
  - Phase 1: PCG_Sakura_GroundCover only (VolumeSampler → Transform → StaticMeshSpawner)
  - Phase 2/3 (petals, path flowers, PCGEx falloff) intentionally NOT built here

Run in-editor:
  py Content/Python/setup_pcg_sakura.py
  py Content/Python/setup_pcg_sakura.py --rebuild
  py Content/Python/setup_pcg_sakura.py --spawn-only
  py Content/Python/setup_pcg_sakura.py --graph-only

Headless:
  UnrealEditor-Cmd.exe BS_GodFile.uproject ^
    -ExecutePythonScript="G:/EnvironmentPortfolio/BS_GodFile/Content/Python/setup_pcg_sakura.py"
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pcg_sakura_standards as std
import pcg_sakura_validate_helpers as vh

try:
    import unreal
except ImportError:
    unreal = None  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = PROJECT_ROOT / "Saved" / "Audit" / "sakura_pcg_build.json"

ACTOR_PCG_VOLUME = "PCG_Sakura_GroundCover"
ACTOR_EXCLUDE_PREFIX = "PCG_Exclude_"


def _ensure_directory(path: str) -> None:
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def _clear_graph_nodes(graph) -> None:
    if hasattr(graph, "remove_nodes"):
        graph.remove_nodes()
        return
    for node in list(graph.get_nodes()):
        try:
            graph.remove_node(node)
        except Exception:
            pass


def _add_node(graph, settings_class_name: str, x: int, y: int):
    cls = getattr(unreal, settings_class_name, None)
    if cls is None:
        raise RuntimeError(f"PCG settings class missing: {settings_class_name}")
    node, settings = graph.add_node_of_type(cls)
    node.set_node_position(x, y)
    return node, settings


def _verify_materials() -> dict:
    checks = {}
    for label, path in (("grass", std.MI_GRASS), ("petals", std.MI_PETALS)):
        exists = unreal.EditorAssetLibrary.does_asset_exist(path)
        checks[label] = {"path": path, "exists": exists}
        if not exists:
            unreal.log_warning(f"[SakuraPCG] missing material {path} — run setup_sakura_instances.py")
    return checks


def _verify_grass_mesh() -> dict:
    mesh_path = std.resolve_mesh("grass")
    ok = mesh_path is not None
    if not ok:
        unreal.log_error("[SakuraPCG] no grass proxy mesh — import Greybox_Kit or use engine shapes")
    return {"path": mesh_path, "ok": ok}


def build_ground_cover_graph(*, force: bool = False) -> str:
    """Create or rebuild PCG_Sakura_GroundCover (stock nodes only)."""
    asset_path = std.GRAPH_GROUND_COVER
    _ensure_directory(std.PCG_ROOT)

    graph = None
    if not force and unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        graph = unreal.load_asset(asset_path)
    if graph is None:
        factory = unreal.PCGGraphFactory()
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        name = asset_path.rsplit("/", 1)[-1]
        graph = tools.create_asset(name, std.PCG_ROOT, unreal.PCGGraph, factory)
        if not graph:
            raise RuntimeError(f"failed to create PCG graph at {std.PCG_ROOT}")
    else:
        _clear_graph_nodes(graph)

    inp = graph.get_input_node()
    out = graph.get_output_node()
    inp.set_node_position(-600, 0)
    out.set_node_position(600, 0)

    sampler, sampler_settings = _add_node(graph, "PCGVolumeSamplerSettings", -400, 0)
    voxel = float(std.GROUND_VOXEL_CM)
    sampler_settings.set_editor_property("voxel_size", unreal.Vector(voxel, voxel, voxel))
    sampler_settings.set_editor_property("unbounded", False)

    xform, xform_settings = _add_node(graph, "PCGTransformPointsSettings", -100, 0)
    std.apply_grass_transform(xform_settings)

    spawner, spawner_settings = _add_node(graph, "PCGStaticMeshSpawnerSettings", 200, 0)
    if not std.configure_grass_spawner(spawner_settings, std.MI_GRASS):
        raise RuntimeError("grass spawner configuration failed — check mesh + material paths")

    graph.add_edge(inp, "In", sampler, "Volume")
    graph.add_edge(sampler, "Out", xform, "In")
    graph.add_edge(xform, "Out", spawner, "In")
    graph.add_edge(spawner, "Out", out, "Out")
    graph.set_editor_property("is_standalone_graph", True)

    unreal.EditorAssetLibrary.save_asset(asset_path, only_if_is_dirty=False)
    unreal.log(f"[SakuraPCG] graph saved: {asset_path}")
    return asset_path


def _set_actor_tag(actor, tag: str) -> None:
    try:
        tags = list(actor.tags)
        if tag not in tags:
            tags.append(tag)
            actor.tags = tags
    except Exception:
        pass


def _destroy_labeled(prefix: str) -> None:
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for actor in list(eas.get_all_level_actors()):
        label = actor.get_actor_label()
        if label == prefix or label.startswith(prefix):
            eas.destroy_actor(actor)


def _spawn_exclusion_guides() -> list[str]:
    """Visual exclusion boxes for path + pond — wire into graph in Phase 2."""
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    cube = "/Engine/BasicShapes/Cube.Cube"
    guides = [
        ("Path", (-700, -20, 8), (16, 3, 2)),
        ("Pond", (600, -400, 8), (8, 6, 2)),
        ("ToriiPad", (300, 0, 8), (8, 8, 2)),
    ]
    spawned: list[str] = []
    for suffix, loc, scale in guides:
        label = f"{ACTOR_EXCLUDE_PREFIX}{suffix}"
        actor = eas.spawn_actor_from_class(
            unreal.StaticMeshActor,
            unreal.Vector(*loc),
            unreal.Rotator(0, 0, 0),
        )
        if not actor:
            continue
        actor.set_actor_label(label)
        actor.set_actor_scale3d(unreal.Vector(*scale))
        _set_actor_tag(actor, std.TAG_EXCLUDE)
        comp = actor.static_mesh_component
        comp.set_static_mesh(unreal.load_asset(cube))
        comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        comp.set_visibility(False, True)
        spawned.append(label)
    return spawned


def _tag_ground_actor() -> bool:
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for actor in eas.get_all_level_actors():
        if actor.get_actor_label() == "Ground":
            _set_actor_tag(actor, std.TAG_GROUND)
            return True
    unreal.log_warning("[SakuraPCG] Ground actor not found — run setup_sakura_scene.py")
    return False


def spawn_level_pcg(*, generate: bool = True) -> dict:
    """Load L_SakuraPath, place PCGVolume + exclusion guides, optional generate."""
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    level_path = f"{std.LEVEL}.L_SakuraPath"
    if not unreal.EditorAssetLibrary.does_asset_exist(level_path):
        unreal.log_warning("[SakuraPCG] level missing — running setup_sakura_scene.build()")
        __import__("setup_sakura_scene").build()

    les.load_level(std.LEVEL)
    _destroy_labeled(ACTOR_PCG_VOLUME)
    _destroy_labeled(ACTOR_EXCLUDE_PREFIX)

    graph_path = std.GRAPH_GROUND_COVER
    if not unreal.EditorAssetLibrary.does_asset_exist(graph_path):
        build_ground_cover_graph(force=True)
    graph = unreal.load_asset(graph_path)
    if not graph:
        raise RuntimeError(f"PCG graph not loadable: {graph_path}")

    cx, cy, cz = std.PCG_VOLUME_CENTER
    sx, sy, sz = std.PCG_VOLUME_SCALE
    vol = eas.spawn_actor_from_class(
        unreal.PCGVolume,
        unreal.Vector(cx, cy, cz),
        unreal.Rotator(0, 0, 0),
    )
    if not vol:
        raise RuntimeError("failed to spawn PCGVolume")
    vol.set_actor_label(ACTOR_PCG_VOLUME)
    vol.set_actor_scale3d(unreal.Vector(sx, sy, sz))

    comp = vol.get_component_by_class(unreal.PCGComponent)
    comp.set_editor_property("graph", graph)
    comp.set_editor_property("seed", 4242)
    comp.set_editor_property("b_activated", True)

    exclusions = _spawn_exclusion_guides()
    ground_tagged = _tag_ground_actor()

    ism_count = 0
    gen_ok = False
    if generate:
        try:
            vh.generate_and_wait(comp, force=True, max_wait=60.0)
            gen_ok = True
            ism_count = vh.count_ism(vol)
        except Exception as exc:
            unreal.log_error(f"[SakuraPCG] generate failed: {exc}")

    les.save_current_level()
    return {
        "pcg_volume": ACTOR_PCG_VOLUME,
        "exclusion_guides": exclusions,
        "ground_tagged": ground_tagged,
        "generated": gen_ok,
        "ism_count": ism_count,
        "ism_valid": vh.within_bounds(
            ism_count, std.GROUND_COVER_ISM_MIN, std.GROUND_COVER_ISM_MAX
        ),
    }


def build_all(
    *,
    rebuild: bool = False,
    spawn: bool = True,
    graph_only: bool = False,
    spawn_only: bool = False,
) -> dict:
    if unreal is None:
        raise RuntimeError("setup_pcg_sakura.py must run inside Unreal Editor")

    try:
        unreal.AssetRegistryHelpers.get_asset_registry().search_all_assets(True)
    except Exception as exc:
        unreal.log_warning(f"[SakuraPCG] registry scan: {exc}")

    started = datetime.now(timezone.utc).isoformat()
    report: dict = {
        "timestamp": started,
        "phase": "0+1",
        "graphs_built": [],
        "materials": {},
        "grass_mesh": {},
        "level_spawn": {},
        "gates": {},
        "notes": [
            "Phase 2 (fallen petals) and Phase 3 (path flowers / PCGEx) not implemented.",
            "Exclusion guide actors are invisible placeholders — graph does not filter them yet.",
            "Disable dense NS_SakuraGroundPetals if PCG grass reads too busy.",
        ],
    }

    report["materials"] = _verify_materials()
    report["grass_mesh"] = _verify_grass_mesh()

    if spawn_only:
        report["level_spawn"] = spawn_level_pcg(generate=True)
    elif not graph_only:
        if rebuild or not unreal.EditorAssetLibrary.does_asset_exist(std.GRAPH_GROUND_COVER):
            report["graphs_built"].append(build_ground_cover_graph(force=True))
        else:
            unreal.log(f"[SakuraPCG] reusing graph {std.GRAPH_GROUND_COVER} (pass --rebuild)")
            report["graphs_built"].append(std.GRAPH_GROUND_COVER)
        if spawn:
            report["level_spawn"] = spawn_level_pcg(generate=True)
    else:
        report["graphs_built"].append(build_ground_cover_graph(force=rebuild))

    report["gates"] = {
        "grass_material_exists": report["materials"].get("grass", {}).get("exists", False),
        "grass_mesh_ok": report["grass_mesh"].get("ok", False),
        "graph_exists": unreal.EditorAssetLibrary.does_asset_exist(std.GRAPH_GROUND_COVER),
        "ism_valid": report.get("level_spawn", {}).get("ism_valid", False),
    }
    report["passed"] = all(
        [
            report["gates"]["grass_mesh_ok"],
            report["gates"]["graph_exists"],
            report["gates"].get("ism_valid") or not spawn,
        ]
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log(f"[SakuraPCG] audit -> {REPORT_PATH}")
    unreal.log(
        f"[SakuraPCG] done passed={report['passed']} "
        f"ism={report.get('level_spawn', {}).get('ism_count', 'n/a')}"
    )
    return report


def main() -> int:
    rebuild = "--rebuild" in sys.argv
    spawn_only = "--spawn-only" in sys.argv
    graph_only = "--graph-only" in sys.argv
    spawn = "--no-spawn" not in sys.argv

    if unreal is None:
        print("Run inside Unreal Editor: py Content/Python/setup_pcg_sakura.py")
        return 1

    report = build_all(
        rebuild=rebuild,
        spawn=spawn and not graph_only,
        graph_only=graph_only,
        spawn_only=spawn_only,
    )
    print(f"SAKURA_PCG passed={report['passed']}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
