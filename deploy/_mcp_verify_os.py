"""Headless verify for Surreal Architecture OS layer.

Launch with --factory-startup:
  blender --background --factory-startup --python deploy/_mcp_verify_os.py
"""
import json
import os
import sys

import bpy

print("=== SURREAL OS VERIFY ===")

DEPLOY = os.path.dirname(os.path.abspath(__file__))
if DEPLOY not in sys.path:
    sys.path.insert(0, DEPLOY)

s = sys.modules.get("surreal_architecture_gen")
if s is None:
    if "surreal_architecture_gen" not in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_enable(module="surreal_architecture_gen")
    s = sys.modules.get("surreal_architecture_gen")
if s is None:
    print("  !! FAIL: surreal_architecture_gen not loaded")
    raise SystemExit(1)
if not getattr(s, "_surreal_patched", False):
    print("  !! FAIL: monolith patch (_surreal_patched) not applied")
    raise SystemExit(1)
print("  monolith: OK")

all_ok = True

print("\n--- Genome load ---")
from surreal_os import genome as os_genome

for gid in os_genome.list_genomes():
    try:
        g = os_genome.load_genome(gid)
        print(f"  {gid}: verticality={g.get('verticality')} graph={g.get('default_graph')}")
    except Exception as err:
        print(f"  !! FAIL {gid}: {err}")
        all_ok = False

print("\n--- Grammar graphs ---")
from surreal_os.grammar_loader import load_grammar_graph, merge_grammar_into_registry
from surreal_arch.greybox_graph import GRAPH_REGISTRY

merged = merge_grammar_into_registry(GRAPH_REGISTRY)
print(f"  merged_into_registry: {merged}")
for gid in ("ZEN_SHRINE_AXIS", "ZEN_SAKURA_WALK", "ZEN_SHRINE_COURTYARD", "ZEN_ROJI_PATH", "ZEN_KARESANSHUI_WALK", "ZEN_TEA_GARDEN", "CLOISTER", "SCIFI_AIRLOCK", "SCI_FI_DECK", "ROMANESQUE_CLOISTER", "VENETIAN_CANAL", "ROMANESQUE_APSE", "SCI_FI_DECK_EXPANSION", "ASIAN_CITY", "BRUTALIST_PLAZA", "ART_NOUVEAU", "MOORISH_COURTYARD"):
    if gid not in GRAPH_REGISTRY:
        print(f"  !! FAIL: {gid} not in GRAPH_REGISTRY")
        all_ok = False
    elif not GRAPH_REGISTRY[gid].get("os_grammar"):
        print(f"  !! FAIL: {gid} missing os_grammar flag")
        all_ok = False
    else:
        spec = GRAPH_REGISTRY[gid]["spec"]
        print(f"  {gid} modules={len(spec)} os_grammar=True")

print("\n--- Atoms + taxonomy ---")
from surreal_os import atoms, taxonomy, critique

kit_dispatch = getattr(s, "_KIT_DISPATCH", {})
missing_tax = taxonomy.validate_kit_dispatch(kit_dispatch)
if missing_tax:
    print(f"  !! FAIL missing taxonomy: {missing_tax}")
    all_ok = False
else:
    print("  taxonomy: all GB_ZEN_* kits registered")

zen_ok, zen_fails = critique.critique_all_zen_kits(kit_dispatch)
if not zen_ok:
    for line in zen_fails:
        print(f"  !! FAIL {line}")
    all_ok = False
else:
    print("  critique: all GB_ZEN_* pass")

print("\n--- Compose roles ---")
from surreal_os.rules_engine import load_compose_styles
from surreal_world.compose import resolve_compose_style

os_styles = load_compose_styles()
if "ZEN_SHRINE" not in os_styles:
    print("  !! FAIL: ZEN_SHRINE missing from compose_roles.json")
    all_ok = False
else:
    style = resolve_compose_style(s, "ZEN_SHRINE")
    print(f"  ZEN_SHRINE roles: {len(style)} keys")
    role_expect = {
        "sacred": "_lib_GB_ZEN_HONDEN",
        "corner_tower": "_lib_GB_ZEN_GOJU_PAGODA",
        "monument": "_lib_GB_ZEN_TAHOTO",
        "small": "_lib_GB_ZEN_LANTERN",
        "gate": "_lib_GB_ZEN_TORII_GATE",
    }
    for role, lib in role_expect.items():
        if style.get(role) != lib:
            print(f"  !! FAIL: {role} expected {lib} got {style.get(role)}")
            all_ok = False

s._active_style_genome = os_genome.load_genome("zen_shrine_sakura")
style_sakura = resolve_compose_style(s, "ZEN_SHRINE")
if style_sakura.get("gate") != "_lib_GB_ZEN_SAKURA_TORII":
    print(f"  !! FAIL: sakura genome gate override got {style_sakura.get('gate')}")
    all_ok = False
else:
    print("  genome compose_roles sakura: OK")
s._active_style_genome = None

print("\n--- Genome apply + graph spawn smoke ---")
mesh = bpy.data.meshes.new("_OSVerifyMesh")
obj = bpy.data.objects.new("_OSVerify", mesh)
bpy.context.collection.objects.link(obj)
props = obj.surreal_arch_props
os_genome.apply_genome(props, "zen_shrine_v1", monolith=s)
if props.style_genome_id != "zen_shrine_v1":
    print("  !! FAIL: style_genome_id not set")
    all_ok = False
else:
    print("  apply_genome: OK")

g = os_genome.load_genome("zen_shrine_v1")
if g.get("surreal_transform") != "axis_compression":
    print(f"  !! FAIL: zen_shrine_v1 surreal_transform={g.get('surreal_transform')}")
    all_ok = False
else:
    print("  zen_shrine_v1 axis_compression: OK")

ga = os_genome.load_genome("zen_shrine_axis")
if ga.get("grammar_id") != "ZEN_SHRINE_AXIS":
    print(f"  !! FAIL: zen_shrine_axis grammar_id={ga.get('grammar_id')}")
    all_ok = False
elif ga.get("surreal_transform") != "vertical_stretch":
    print(f"  !! FAIL: zen_shrine_axis surreal_transform={ga.get('surreal_transform')}")
    all_ok = False
elif len(ga.get("sacred_sequence") or []) < 6:
    print(f"  !! FAIL: zen_shrine_axis sacred_sequence short")
    all_ok = False
else:
    print("  zen_shrine_axis vertical_stretch: OK")

gs = os_genome.load_genome("zen_shrine_sakura")
if gs.get("torii_variant") != "sakura" or gs.get("default_graph") != "ZEN_SAKURA_WALK":
    print(f"  !! FAIL: zen_shrine_sakura variant/graph")
    all_ok = False
else:
    print("  zen_shrine_sakura sakura walk: OK")

gc = os_genome.load_genome("zen_shrine_courtyard")
if gc.get("default_graph") != "ZEN_SHRINE_COURTYARD":
    print(f"  !! FAIL: zen_shrine_courtyard graph={gc.get('default_graph')}")
    all_ok = False
else:
    print("  zen_shrine_courtyard: OK")

gr = os_genome.load_genome("zen_roji_path")
if gr.get("default_graph") != "ZEN_ROJI_PATH" or not gr.get("compose_roles"):
    print(f"  !! FAIL: zen_roji_path genome")
    all_ok = False
else:
    print("  zen_roji_path genome: OK")

gt = os_genome.load_genome("zen_tea_garden")
if gt.get("default_graph") != "ZEN_TEA_GARDEN":
    print(f"  !! FAIL: zen_tea_garden graph={gt.get('default_graph')}")
    all_ok = False
else:
    print("  zen_tea_garden genome: OK")

genome_ids = os_genome.list_genomes()
if len(genome_ids) < 19:
    print(f"  !! FAIL: expected >=19 genomes got {len(genome_ids)}")
    all_ok = False
else:
    print(f"  genome catalog: {len(genome_ids)} entries")

groups = getattr(s, "_STYLE_GENOME_GROUPS", {}) or {}
if not groups or sum(len(v) for v in groups.values()) < len(genome_ids):
    print(f"  !! FAIL: _STYLE_GENOME_GROUPS incomplete: {groups}")
    all_ok = False
elif groups.get("Zen", []) and groups.get("Gothic", []):
    print(f"  _STYLE_GENOME_GROUPS: {', '.join(f'{k}={len(v)}' for k, v in groups.items())}")
else:
    print(f"  !! FAIL: _STYLE_GENOME_GROUPS missing families: {groups}")
    all_ok = False

if not hasattr(s, "_STYLE_GENOMES") or len(s._STYLE_GENOMES) < 17:
    print("  !! FAIL: _STYLE_GENOMES not populated")
    all_ok = False
else:
    print("  _STYLE_GENOMES: OK")

meta = getattr(s, "_STYLE_GENOME_META", {}) or {}
if "zen_tea_garden" not in meta or meta["zen_tea_garden"].get("graph") != "ZEN_TEA_GARDEN":
    print(f"  !! FAIL: _STYLE_GENOME_META missing tea garden: {meta.get('zen_tea_garden')}")
    all_ok = False
else:
    print("  _STYLE_GENOME_META: OK")

from surreal_arch.greybox_graph import spawn_graph

bpy.context.view_layer.objects.active = obj
spec = GRAPH_REGISTRY["ZEN_SHRINE_AXIS"]["spec"]
try:
    objs = spawn_graph(bpy.context, s, spec[:3], spacing=8.0, graph_id="ZEN_SHRINE_AXIS")
    print(f"  spawn_graph partial: {len(objs)} objects")
    for o in objs:
        snaps = json.loads(o.get("surreal_snap_points", "[]")) if o.get("surreal_snap_points") else []
        if len(snaps) == 0:
            print(f"  !! FAIL: {o.name} has 0 snaps")
            all_ok = False
    asian_spec = GRAPH_REGISTRY["ASIAN_CITY"]["spec"]
    asian_objs = spawn_graph(bpy.context, s, asian_spec[:3], spacing=10.0, graph_id="ASIAN_CITY")
    print(f"  spawn_graph ASIAN_CITY partial: {len(asian_objs)} objects")
    if len(asian_objs) < 2:
        print(f"  !! FAIL: ASIAN_CITY spawn got {len(asian_objs)}")
        all_ok = False
    brutal_spec = GRAPH_REGISTRY["BRUTALIST_PLAZA"]["spec"]
    brutal_objs = spawn_graph(bpy.context, s, brutal_spec[:3], spacing=12.0, graph_id="BRUTALIST_PLAZA")
    print(f"  spawn_graph BRUTALIST_PLAZA partial: {len(brutal_objs)} objects")
    if len(brutal_objs) < 2:
        print(f"  !! FAIL: BRUTALIST_PLAZA spawn got {len(brutal_objs)}")
        all_ok = False
    art_spec = GRAPH_REGISTRY["ART_NOUVEAU"]["spec"]
    art_objs = spawn_graph(bpy.context, s, art_spec[:3], spacing=10.0, graph_id="ART_NOUVEAU")
    print(f"  spawn_graph ART_NOUVEAU partial: {len(art_objs)} objects")
    if len(art_objs) < 2:
        print(f"  !! FAIL: ART_NOUVEAU spawn got {len(art_objs)}")
        all_ok = False
    moor_spec = GRAPH_REGISTRY["MOORISH_COURTYARD"]["spec"]
    moor_objs = spawn_graph(bpy.context, s, moor_spec[:3], spacing=10.0, graph_id="MOORISH_COURTYARD")
    print(f"  spawn_graph MOORISH_COURTYARD partial: {len(moor_objs)} objects")
    if len(moor_objs) < 2:
        print(f"  !! FAIL: MOORISH_COURTYARD spawn got {len(moor_objs)}")
        all_ok = False
    from surreal_arch.research_presets import run_research_preset
    rp = run_research_preset(bpy.context, "gothic_cloister_graph", monolith=s)
    if rp.get("mode") != "graph" or rp.get("count", 0) < 3:
        print(f"  !! FAIL: research preset graph spawn: {rp}")
        all_ok = False
    else:
        print(f"  research_preset gothic_cloister_graph: {rp['count']} modules")
    rp2 = run_research_preset(bpy.context, "scifi_airlock_graph", monolith=s)
    if rp2.get("mode") != "graph" or rp2.get("count", 0) < 3:
        print(f"  !! FAIL: scifi_airlock_graph spawn: {rp2}")
        all_ok = False
    else:
        print(f"  research_preset scifi_airlock_graph: {rp2['count']} modules")
except Exception as err:
    print(f"  !! FAIL spawn_graph: {err}")
    all_ok = False

print("\n--- Research preset graph audit ---")
from surreal_arch.research_presets import audit_graph_presets, audit_grammar_enums, RESEARCH_PRESETS

graph_preset_ids = [pid for pid, spec in RESEARCH_PRESETS.items() if spec.get("graph_id")]
audit_errs = audit_graph_presets(GRAPH_REGISTRY)
if audit_errs:
    for line in audit_errs:
        print(f"  !! FAIL {line}")
    all_ok = False
elif len(graph_preset_ids) < 19:
    print(f"  !! FAIL: expected >=19 graph research presets got {len(graph_preset_ids)}")
    all_ok = False
else:
    print(f"  graph_research_presets: {len(graph_preset_ids)} OK")

enum_errs = audit_grammar_enums(GRAPH_REGISTRY)
if enum_errs:
    for line in enum_errs:
        print(f"  !! FAIL {line}")
    all_ok = False
else:
    print("  grammar_enum_audit: OK")

print("\n--- Surreal transform ---")
from surreal_os.rules_engine import get_transform, apply_surreal_transform

xf = get_transform("axis_compression")
if not xf:
    print("  !! FAIL: axis_compression missing")
    all_ok = False
elif "BRUTALIST_PLAZA" not in (xf.get("applies_to") or []):
    print("  !! FAIL: axis_compression missing BRUTALIST_PLAZA")
    all_ok = False
else:
    print(f"  axis_compression type={xf.get('type')} BRUTALIST_PLAZA: OK")

xf2 = get_transform("vertical_stretch")
if not xf2:
    print("  !! FAIL: vertical_stretch missing")
    all_ok = False
else:
    print(f"  vertical_stretch type={xf2.get('type')}")

xf3 = get_transform("recursive_interior")
if not xf3 or "CLOISTER" not in (xf3.get("applies_to") or []):
    print(f"  !! FAIL: recursive_interior CLOISTER apply: {xf3}")
    all_ok = False
elif "ASIAN_CITY" not in (xf3.get("applies_to") or []):
    print("  !! FAIL: recursive_interior missing ASIAN_CITY")
    all_ok = False
else:
    print("  recursive_interior CLOISTER + ASIAN_CITY: OK")

gothic = os_genome.load_genome("gothic_cloister_v1")
if os_genome.genome_family(gothic) != "Gothic":
    print(f"  !! FAIL: genome_family gothic={os_genome.genome_family(gothic)}")
    all_ok = False
elif gothic.get("surreal_transform") != "recursive_interior":
    print(f"  !! FAIL: gothic_cloister_v1 transform={gothic.get('surreal_transform')}")
    all_ok = False
else:
    print("  gothic_cloister_v1 + genome_family: OK")

scifi = os_genome.load_genome("scifi_airlock_v1")
if scifi.get("default_graph") != "SCIFI_AIRLOCK":
    print(f"  !! FAIL: scifi_airlock_v1 graph={scifi.get('default_graph')}")
    all_ok = False
else:
    print("  scifi_airlock_v1: OK")

rom = os_genome.load_genome("romanesque_cloister_v1")
ven = os_genome.load_genome("venetian_canal_v1")
if rom.get("grammar_id") != "ROMANESQUE_CLOISTER" or ven.get("grammar_id") != "VENETIAN_CANAL":
    print("  !! FAIL: romanesque/venetian genome grammar_id")
    all_ok = False
else:
    print("  romanesque_cloister_v1 + venetian_canal_v1: OK")

s._active_style_genome = os_genome.load_genome("romanesque_apse_v1")
wc = resolve_compose_style(s, "WESTERN_CASTLE")
if wc.get("sacred") != "_lib_CHAPEL":
    print(f"  !! FAIL: romanesque_apse sacred override got {wc.get('sacred')}")
    all_ok = False
elif os_styles.get("WESTERN_CASTLE", {}).get("gate") != "_lib_GATEHOUSE":
    print("  !! FAIL: WESTERN_CASTLE compose_roles missing")
    all_ok = False
else:
    print("  WESTERN_CASTLE + genome compose_roles: OK")
s._active_style_genome = None

asian = os_genome.load_genome("asian_city_v1")
if asian.get("compose_style") != "ASIAN_CITY" or os_genome.genome_family(asian) != "Asian":
    print(f"  !! FAIL: asian_city_v1 compose/family={asian.get('compose_style')}")
    all_ok = False
elif asian.get("grammar_id") != "ASIAN_CITY":
    print(f"  !! FAIL: asian_city_v1 grammar={asian.get('grammar_id')}")
    all_ok = False
elif os_styles.get("ASIAN_CITY", {}).get("gate") != "_lib_CN_PAILOU":
    print("  !! FAIL: ASIAN_CITY compose_roles missing")
    all_ok = False
else:
    print("  asian_city_v1 + ASIAN_CITY compose_roles: OK")

asian_r = os_genome.load_genome("asian_city_recursive_v1")
if asian_r.get("surreal_transform") != "recursive_interior" or asian_r.get("grammar_id") != "ASIAN_CITY":
    print(f"  !! FAIL: asian_city_recursive_v1 transform/grammar")
    all_ok = False
else:
    print("  asian_city_recursive_v1: OK")

brut = os_genome.load_genome("brutalist_plaza_v1")
if brut.get("surreal_transform") != "axis_compression" or os_genome.genome_family(brut) != "Brutalist":
    print(f"  !! FAIL: brutalist_plaza_v1 transform/family")
    all_ok = False
elif brut.get("grammar_id") != "BRUTALIST_PLAZA":
    print(f"  !! FAIL: brutalist_plaza_v1 grammar={brut.get('grammar_id')}")
    all_ok = False
else:
    print("  brutalist_plaza_v1: OK")

wc = os_genome.load_genome("western_castle_v1")
if wc.get("compose_style") != "WESTERN_CASTLE" or os_genome.genome_family(wc) != "Western":
    print(f"  !! FAIL: western_castle_v1 compose/family")
    all_ok = False
elif wc.get("grammar_id") != "CLOISTER":
    print(f"  !! FAIL: western_castle_v1 grammar={wc.get('grammar_id')}")
    all_ok = False
else:
    print("  western_castle_v1: OK")

an = os_genome.load_genome("art_nouveau_v1")
if an.get("compose_style") != "ART_NOUVEAU" or os_genome.genome_family(an) != "ArtNouveau":
    print(f"  !! FAIL: art_nouveau_v1 compose/family")
    all_ok = False
elif an.get("grammar_id") != "ART_NOUVEAU":
    print(f"  !! FAIL: art_nouveau_v1 grammar={an.get('grammar_id')}")
    all_ok = False
elif os_styles.get("ART_NOUVEAU", {}).get("gate") != "_lib_OGEE_ARCH":
    print("  !! FAIL: ART_NOUVEAU compose_roles missing")
    all_ok = False
else:
    print("  art_nouveau_v1 + ART_NOUVEAU compose_roles: OK")

mc = os_genome.load_genome("moorish_courtyard_v1")
if mc.get("compose_style") != "MOORISH_COURTYARD" or os_genome.genome_family(mc) != "Moorish":
    print(f"  !! FAIL: moorish_courtyard_v1 compose/family")
    all_ok = False
elif mc.get("grammar_id") != "MOORISH_COURTYARD":
    print(f"  !! FAIL: moorish_courtyard_v1 grammar={mc.get('grammar_id')}")
    all_ok = False
elif os_styles.get("MOORISH_COURTYARD", {}).get("gate") != "_lib_ARCHWAY_ADV":
    print("  !! FAIL: MOORISH_COURTYARD compose_roles missing")
    all_ok = False
else:
    print("  moorish_courtyard_v1 + MOORISH_COURTYARD compose_roles: OK")

if all_ok:
    print("\n=== OS VERIFY OK ===")
else:
    print("\n=== OS VERIFY FAILED ===")
    raise SystemExit(1)
