"""Nikki Wardrobe + Accessory Studio + Pattern Compendium + Photo Studio ΓÇö VIEW_3D panels."""

from __future__ import annotations

import bpy
import os
import sys
from mathutils import Vector

from .path_util import GENOME_FAMILY_ICONS, ensure_deploy_on_path
from .branding import N_PANEL_CATEGORY

_BAR_FULL = "\u2588"
_BAR_EMPTY = "\u2591"
_BAR_LENGTH = 12

_AXIS_LABELS = [
    ("genome_verticality", "Verticality", "\U0001f30b"),
    ("genome_symmetry", "Symmetry", "\u2696\ufe0f"),
    ("genome_ornament_density", "Ornament", "\u2728"),
    ("genome_structural_logic", "Structure", "\U0001f3d7"),
    ("genome_organic_growth", "Organic", "\U0001f33f"),
    ("genome_cosmic_influence", "Cosmic", "\U0001f4ab"),
]

_ATOM_ICON_MAP = {
    "torii_frame": "\U0001f3ef", "sakura_torii_frame": "\U0001f338",
    "sando_approach": "\U0001f30a", "kairo_cloister": "\U0001f3db",
    "karesansui_field": "\U0001fab4", "roji_path_segment": "\U0001f9f1",
    "tobiishi_scatter": "\U0001faa8", "tsukubai_station": "\U0001f6bd",
    "engawa_threshold": "\U0001f3e0", "bamboo_screen": "\U0001f332",
    "machiai_wait": "\U0001f3d8", "stone_bridge_span": "\U0001f309",
    "cherry_canopy_path": "\U0001f338", "stream_bank_edge": "\U0001f4a7",
    "goju_pagoda_tower": "\U0001f5fb", "tahoto_treasure_tower": "\U0001f3f0",
    "haiden_platform": "\U0001f3db", "honden_sanctuary": "\u26e9",
    "stone_lantern_post": "\U0001f3ee",
    "facade": "\U0001f3db", "nave": "\u26ea", "crossing": "\u267e",
    "transept": "\u2796", "altar": "\U0001f54a", "portal": "\U0001f3aa",
    "chapter": "\U0001f4da", "narthex": "\U0001f54a", "naos": "\u26ea", "dome": "\U0001f3e1",
}

VIBE_PRESETS = {
    "allegro_spire": {
        "icon": "\U0001f3d4\ufe0f", "label": "Allegro Spire",
        "desc": "Soaring upward \u2014 fast and grand, high verticality",
        "vals": (0.9, 0.4, 0.3, 0.7, 0.2, 0.3),
        "music": {"freq_a": 0.8, "freq_b": 1.6, "note_pattern": "EIGHTH", "tempo": 2.0},
    },
    "forte_garden": {
        "icon": "\U0001f33f", "label": "Forte Garden",
        "desc": "Lush and loud \u2014 nature overtaken, organic density",
        "vals": (0.4, 0.5, 0.8, 0.5, 0.9, 0.3),
        "music": {"freq_a": 0.4, "freq_b": 0.8, "note_pattern": "QUARTER", "tempo": 1.2},
    },
    "crystal_fugue": {
        "icon": "\U0001f48e", "label": "Crystal Fugue",
        "desc": "Structured precision \u2014 crystalline symmetry",
        "vals": (0.5, 0.9, 0.7, 0.8, 0.2, 0.6),
        "music": {"freq_a": 0.6, "freq_b": 1.2, "note_pattern": "SIXTEENTH", "tempo": 1.8},
    },
    "cosmic_lullaby": {
        "icon": "\U0001f30c", "label": "Cosmic Lullaby",
        "desc": "Dreamy and surreal \u2014 cosmic influence drifts",
        "vals": (0.6, 0.4, 0.4, 0.4, 0.6, 0.9),
        "music": {"freq_a": 0.3, "freq_b": 0.6, "note_pattern": "HALF", "tempo": 0.5},
    },
    "sacred_chant": {
        "icon": "\u26e9", "label": "Sacred Chant",
        "desc": "Balanced tradition \u2014 sacred geometry anchored",
        "vals": (0.7, 0.7, 0.5, 0.8, 0.3, 0.5),
        "music": {"freq_a": 0.5, "freq_b": 1.0, "note_pattern": "WHOLE", "tempo": 0.8},
    },
    "dramatic_crescendo": {
        "icon": "\U0001f3ad", "label": "Dramatic Crescendo",
        "desc": "Ornate drama \u2014 bold ornament swells",
        "vals": (0.6, 0.3, 0.9, 0.3, 0.5, 0.7),
        "music": {"freq_a": 0.7, "freq_b": 1.4, "note_pattern": "EIGHTH", "tempo": 1.5},
    },
    "starlight_melodia": {
        "icon": "\u2728", "label": "Starlight Melodia",
        "desc": "Pure magic \u2014 cosmic harmony at maximum",
        "vals": (1.0, 0.5, 0.5, 0.5, 0.5, 1.0),
        "music": {"freq_a": 2.0, "freq_b": 4.0, "note_pattern": "SIXTEENTH", "tempo": 3.0},
    },
}


def _stat_bar(value: float, length: int = _BAR_LENGTH) -> str:
    filled = max(0, min(int(round(value * length)), length))
    return _BAR_FULL * filled + _BAR_EMPTY * (length - filled)


def _family_icon(family: str) -> str:
    return GENOME_FAMILY_ICONS.get(family, "\U0001f52e")


def _atom_icon(atom_id: str) -> str:
    return _ATOM_ICON_MAP.get(atom_id, "\u25cf")


def _resolve_atom_kit(atom_id: str) -> str | None:
    ensure_deploy_on_path()
    try:
        from surreal_os.atoms import resolve_atom
        a = resolve_atom(atom_id)
        if a:
            return a.get("kit")
    except Exception:
        pass
    return None


def _rarity_from_seq_len(seq_len: int) -> tuple[str, str]:
    if seq_len >= 9:
        return "\u2b50\u2b50\u2b50\u2b50\u2b50", "Legendary"
    if seq_len >= 7:
        return "\u2b50\u2b50\u2b50\u2b50", "Epic"
    if seq_len >= 5:
        return "\u2b50\u2b50\u2b50", "Rare"
    if seq_len >= 3:
        return "\u2b50\u2b50", "Uncommon"
    return "\u2b50", "Common"


# ΓöÇΓöÇΓöÇ Property Group ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

def _update_accessory_toggles(self, context):
    """Push BoolVector accessory toggles to spawned Seq_/atom objects."""
    obj = getattr(self, "id_data", None)
    if obj is None or not hasattr(obj, "surreal_arch_props"):
        return
    gid = getattr(obj.surreal_arch_props, "style_genome_id", "") or ""
    seq = []
    if gid:
        try:
            ensure_deploy_on_path()
            from surreal_os import genome as os_genome

            g = os_genome.load_genome(gid)
            seq = list(g.get("sacred_sequence") or [])
        except Exception:
            seq = []
    _sync_accessory_visibility(context, seq, list(self.accessory_toggles))


class NikkiWardrobeProperties(bpy.types.PropertyGroup):
    show_stats: bpy.props.BoolProperty(
        name="Show All Stats", default=False,
        description="Expand to show all 6 personality axis values"
    )
    favorites_filter: bpy.props.BoolProperty(
        name="Favorites Only", default=False,
        description="Show only favorited patterns"
    )
    graph_spawned: bpy.props.StringProperty(
        name="Collected Graphs", default="",
        description="Comma-separated list of graph IDs that have been spawned"
    )
    accessory_toggles: bpy.props.BoolVectorProperty(
        size=16, default=tuple([True] * 16),
        description="Toggle each sacred sequence step on/off",
        update=_update_accessory_toggles,
    )
    accessory_preset: bpy.props.StringProperty(
        name="Accessory Preset", default="",
        description="Name of saved accessory loadout"
    )


# ΓöÇΓöÇΓöÇ Helpers ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

def _draw_sacred_sequence(layout, genome: dict, gid: str):
    seq = genome.get("sacred_sequence") or []
    if not seq:
        return
    box = layout.box()
    box.label(text="Sacred Path", icon="FORWARD")
    row = box.row(align=True)
    for i, atom_id in enumerate(seq):
        icon = _atom_icon(atom_id)
        kit = _resolve_atom_kit(atom_id)
        if kit:
            op = row.operator("surreal_arch.spawn_sequence_step", text=f"{icon}", depress=False)
            op.atom_id = atom_id
            op.genome_id = gid
        else:
            row.label(text=icon)
        if i < len(seq) - 1:
            row.label(text="\u2192")


def _draw_genome_card(layout, gid: str, genome: dict, meta: dict, active: bool = False):
    box = layout.box()
    fam = genome.get("family") or meta.get("family", "Other")
    icon = _family_icon(fam)
    seq = genome.get("sacred_sequence") or []
    stars, rarity_label = _rarity_from_seq_len(len(seq))

    header = box.row(align=True)
    header.label(text=f"{icon}  {gid}", icon="RNA")
    if active:
        header.label(text="ACTIVE", icon="CHECKMARK")

    sub = box.row(align=True)
    sub.scale_y = 0.8
    sub.label(text=f"{stars}  {fam}  \u00b7  {len(seq)} accessories")

    action_row = box.row(align=True)
    op_apply = action_row.operator("surreal_arch.select_style_genome", text="\u2728 Equip", icon="PLAY")
    op_apply.genome_id = gid
    op_spawn = action_row.operator("surreal_arch.spawn_genome_graph_full", text="\U0001f3ac Full Scene", icon="NODETREE")
    op_spawn.genome_id = gid

    _draw_sacred_sequence(box, genome, gid)

    stats_box = box.box()
    for attr, label, emoji in _AXIS_LABELS:
        val = float(genome.get(attr.replace("genome_", ""), genome.get(attr, 0.5)))
        row = stats_box.row(align=True)
        row.label(text=f"{emoji} {label}")
        row.label(text=f"{_stat_bar(val)}  {val:.2f}")

    graph = genome.get("default_graph") or meta.get("graph", "")
    if graph:
        info_row = box.row(align=True)
        info_row.label(text=f"Graph: {graph}", icon="NODETREE")


def _draw_compact_card(layout, gid: str, genome: dict, meta: dict, active: bool = False):
    col = layout.column(align=True)
    box = col.box()
    fam = genome.get("family") or meta.get("family", "Other")
    icon = _family_icon(fam)
    seq = genome.get("sacred_sequence") or []
    stars, _ = _rarity_from_seq_len(len(seq))
    graph = genome.get("default_graph") or meta.get("graph", "")
    header = box.row(align=True)
    header.label(text=f"{icon}")
    op_apply = box.operator("surreal_arch.select_style_genome", text=gid, depress=active)
    op_apply.genome_id = gid
    # Sacred sequence icons
    seq_row = box.row(align=True)
    seq_row.scale_y = 0.6
    for atom_id in seq[:5]:
        seq_row.label(text=_atom_icon(atom_id))
    if len(seq) > 5:
        seq_row.label(text=f"+{len(seq)-5}")
    # Rarity + graph
    sub = box.row(align=True)
    sub.scale_y = 0.7
    sub.label(text=f"{stars}")
    if graph:
        sub.label(text=f" {graph[:12]}")


# ΓöÇΓöÇΓöÇ Existing Operators ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

class SURREAL_ARCH_OT_spawn_sequence_step(bpy.types.Operator):
    bl_idname = "surreal_arch.spawn_sequence_step"
    bl_label = "Spawn Sequence Step"
    bl_options = {"REGISTER", "UNDO"}
    atom_id: bpy.props.StringProperty(default="")
    genome_id: bpy.props.StringProperty(default="")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        kit = _resolve_atom_kit(self.atom_id)
        if not kit:
            self.report({"WARNING"}, f"Atom {self.atom_id} has no kit mapping")
            return {"CANCELLED"}
        col = context.collection
        mesh = bpy.data.meshes.new(f"Seq_{self.atom_id}")
        obj = bpy.data.objects.new(f"Seq_{self.atom_id}", mesh)
        col.objects.link(obj)
        obj["surreal_atom_id"] = self.atom_id
        obj["surreal_genome_id"] = self.genome_id or ""
        props = obj.surreal_arch_props
        props.arch_type = kit
        if self.genome_id:
            ensure_deploy_on_path()
            try:
                from surreal_os import genome as os_genome
                os_genome.apply_genome(props, self.genome_id)
            except Exception:
                pass
        context.view_layer.objects.active = obj
        obj.select_set(True)
        try:
            bpy.ops.surreal_arch.generate()
        except Exception as exc:
            self.report({"ERROR"}, f"Generate failed: {exc}")
            return {"CANCELLED"}
        self.report({"INFO"}, f"Spawned {kit} ({self.atom_id})")
        return {"FINISHED"}


class SURREAL_ARCH_OT_spawn_genome_graph_full(bpy.types.Operator):
    bl_idname = "surreal_arch.spawn_genome_graph_full"
    bl_label = "Spawn Genome Graph"
    bl_options = {"REGISTER", "UNDO"}
    genome_id: bpy.props.StringProperty(default="")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mod = sys.modules.get("surreal_architecture_gen")
        if mod is None:
            self.report({"ERROR"}, "Surreal Architecture not loaded")
            return {"CANCELLED"}
        from .greybox_graph import GRAPH_REGISTRY, spawn_graph, resolve_graph_spacing
        obj = context.active_object
        gid = self.genome_id or "zen_shrine_axis"
        ensure_deploy_on_path()
        try:
            from surreal_os import genome as os_genome
            genome_data = os_genome.load_genome(gid)
            graph_id = genome_data.get("default_graph", "ZEN_SHRINE_AXIS")
            if obj and hasattr(obj, "surreal_arch_props"):
                os_genome.apply_genome(obj.surreal_arch_props, gid, monolith=mod)
            mod._active_style_genome = genome_data
        except Exception as err:
            self.report({"ERROR"}, f"Genome load: {err}")
            return {"CANCELLED"}
        meta = GRAPH_REGISTRY.get(graph_id)
        if not meta:
            self.report({"ERROR"}, f"Graph {graph_id} not in GRAPH_REGISTRY")
            return {"CANCELLED"}
        spacing = resolve_graph_spacing(context)
        objs = spawn_graph(context, mod, meta["spec"], spacing=spacing, graph_id=graph_id)
        self.report({"INFO"}, f"Spawned {len(objs)} modules ({graph_id})")
        return {"FINISHED"}


class SURREAL_ARCH_OT_spawn_graph_preset(bpy.types.Operator):
    bl_idname = "surreal_arch.spawn_graph_preset"
    bl_label = "Spawn Graph"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Spawn a pre-built module chain from the grammar graph library"
    graph_id: bpy.props.StringProperty(default="")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mod = sys.modules.get("surreal_architecture_gen")
        if mod is None:
            self.report({"ERROR"}, "Surreal Architecture not loaded")
            return {"CANCELLED"}
        from .greybox_graph import GRAPH_REGISTRY, spawn_graph, resolve_graph_spacing
        meta = GRAPH_REGISTRY.get(self.graph_id)
        if not meta:
            self.report({"ERROR"}, f"Graph {self.graph_id} not found")
            return {"CANCELLED"}
        spacing = resolve_graph_spacing(context)
        objs = spawn_graph(context, mod, meta["spec"], spacing=spacing, graph_id=self.graph_id)
        scene = context.scene
        spawned = set(g.strip() for g in getattr(scene, "graph_spawned_str", "").split(",") if g.strip())
        spawned.add(self.graph_id)
        scene.graph_spawned_str = ",".join(sorted(spawned))
        self.report({"INFO"}, f"Spawned {len(objs)} modules ({self.graph_id})")
        return {"FINISHED"}


class SURREAL_ARCH_OT_randomize_dna(bpy.types.Operator):
    bl_idname = "surreal_arch.randomize_dna"
    bl_label = "\u2728 Surprise Me!"
    bl_options = {"REGISTER", "UNDO"}
    seed: bpy.props.IntProperty(default=0, min=0, max=9999)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH" and hasattr(obj, "surreal_arch_props")

    def execute(self, context):
        import random
        props = context.active_object.surreal_arch_props
        axes = ["genome_verticality", "genome_symmetry", "genome_ornament_density",
                "genome_structural_logic", "genome_organic_growth", "genome_cosmic_influence"]
        rng = random.Random(self.seed or None)
        for attr in axes:
            setattr(props, attr, rng.uniform(0.0, 1.0))
        self.report({"INFO"}, f"\u2728 Surprise! DNA randomized (seed={self.seed})")
        return {"FINISHED"}


class SURREAL_ARCH_OT_morph_genome(bpy.types.Operator):
    bl_idname = "surreal_arch.morph_genome"
    bl_label = "Morph Genome"
    bl_options = {"REGISTER", "UNDO"}
    genome_a: bpy.props.StringProperty(default="")
    genome_b: bpy.props.StringProperty(default="")
    factor: bpy.props.FloatProperty(default=0.5, min=0.0, max=1.0, subtype="FACTOR")

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH" and hasattr(obj, "surreal_arch_props")

    def execute(self, context):
        ensure_deploy_on_path()
        try:
            from surreal_os import genome as os_genome
        except Exception as exc:
            self.report({"ERROR"}, f"surreal_os import: {exc}")
            return {"CANCELLED"}
        gid_a = self.genome_a or ""
        gid_b = self.genome_b or "zen_shrine_axis"
        try:
            ga = os_genome.load_genome(gid_a) if gid_a else {}
            gb = os_genome.load_genome(gid_b)
        except Exception as exc:
            self.report({"ERROR"}, f"Genome load: {exc}")
            return {"CANCELLED"}
        f = self.factor
        axes = [("genome_verticality", "verticality"), ("genome_symmetry", "symmetry"),
                ("genome_ornament_density", "ornament_density"),
                ("genome_structural_logic", "structural_logic"),
                ("genome_organic_growth", "organic_growth"),
                ("genome_cosmic_influence", "cosmic_influence")]
        props = context.active_object.surreal_arch_props
        for prop_attr, genome_key in axes:
            va = float(ga.get(genome_key, 0.5)) if ga else 0.5
            vb = float(gb.get(genome_key, 0.5))
            blended = va * (1 - f) + vb * f
            setattr(props, prop_attr, blended)
        props.style_genome_id = f"{gid_a or 'none'}->{gid_b}@f{f:.2f}"
        self.report({"INFO"}, f"Morphed {gid_a} -> {gid_b} at f={f:.2f}")
        return {"FINISHED"}


# ΓöÇΓöÇΓöÇ New Operators ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

class SURREAL_ARCH_OT_wardrobe_cycle(bpy.types.Operator):
    bl_idname = "surreal_arch.wardrobe_cycle"
    bl_label = "Cycle Outfit"
    bl_description = "Cycle to the next or previous genome in the current filter"
    bl_options = {"REGISTER", "UNDO"}
    direction: bpy.props.IntProperty(default=1, min=-1, max=1)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return bool(obj and obj.type == "MESH" and hasattr(obj, "surreal_arch_props"))

    def execute(self, context):
        mod = sys.modules.get("surreal_architecture_gen")
        if mod is None or not hasattr(mod, "_STYLE_GENOMES"):
            self.report({"ERROR"}, "Surreal Architecture not loaded")
            return {"CANCELLED"}
        ensure_deploy_on_path()
        try:
            from surreal_os import genome as os_genome
        except Exception:
            return {"CANCELLED"}
        genomes = mod._STYLE_GENOMES or []
        groups = getattr(mod, "_STYLE_GENOME_GROUPS", {}) or {}
        obj = context.active_object
        if not obj or not hasattr(obj, "surreal_arch_props"):
            self.report({"ERROR"}, "Select a SurrealArch mesh")
            return {"CANCELLED"}
        props = obj.surreal_arch_props
        active_gid = getattr(props, "style_genome_id", "")
        filter_fam = getattr(props, "genome_family_filter", "ALL")

        filtered = []
        for gid in genomes:
            if filter_fam != "ALL":
                try:
                    g = os_genome.load_genome(gid)
                    fam = os_genome.genome_family(g)
                except Exception:
                    continue
                if fam != filter_fam:
                    continue
            filtered.append(gid)

        if not filtered:
            self.report({"INFO"}, "No genomes match current filter")
            return {"CANCELLED"}

        try:
            idx = filtered.index(active_gid) if active_gid in filtered else -1
        except ValueError:
            idx = -1
        new_idx = (idx + self.direction) % len(filtered)
        new_gid = filtered[new_idx]
        try:
            g = os_genome.load_genome(new_gid)
            os_genome.apply_genome(props, new_gid)
        except Exception as exc:
            self.report({"ERROR"}, f"Could not load {new_gid}: {exc}")
            return {"CANCELLED"}
        mod._active_style_genome = g
        self.report({"INFO"}, f"\U0001f380 {new_gid}")
        return {"FINISHED"}


class SURREAL_ARCH_OT_toggle_stats(bpy.types.Operator):
    bl_idname = "surreal_arch.toggle_stats"
    bl_label = "Toggle Stats"
    bl_description = "Expand or collapse the full stat breakdown"

    def execute(self, context):
        obj = context.active_object
        if obj and hasattr(obj, "nikki_wardrobe"):
            obj.nikki_wardrobe.show_stats = not obj.nikki_wardrobe.show_stats
        return {"FINISHED"}


class SURREAL_ARCH_OT_toggle_graph_favorite(bpy.types.Operator):
    bl_idname = "surreal_arch.toggle_graph_favorite"
    bl_label = "Toggle Favorite"
    bl_description = "Star or unstar this pattern in your compendium"
    graph_id: bpy.props.StringProperty(default="")

    def execute(self, context):
        scene = context.scene
        current = getattr(scene, "graph_favorites_str", "")
        favs = set(g.strip() for g in current.split(",") if g.strip())
        if self.graph_id in favs:
            favs.discard(self.graph_id)
        else:
            favs.add(self.graph_id)
        scene.graph_favorites_str = ",".join(sorted(favs))
        return {"FINISHED"}


def _sync_accessory_visibility(context, seq, toggles):
    """Set hide_viewport/hide_render on objects tagged with surreal_atom_id matching seq indices."""
    seq = list(seq or [])
    for obj in bpy.data.objects:
        atom_id = obj.get("surreal_atom_id", "")
        idx = None
        if atom_id and atom_id in seq:
            idx = seq.index(atom_id)
        elif obj.name.startswith("Seq_") and seq:
            # Seq_<atom_id> fallback from spawn_sequence_step
            tail = obj.name[4:]
            if tail in seq:
                idx = seq.index(tail)
        if idx is None:
            continue
        visible = toggles[idx] if idx < len(toggles) else True
        obj.hide_viewport = not visible
        obj.hide_render = not visible


class SURREAL_ARCH_OT_accessory_toggle_all(bpy.types.Operator):
    bl_idname = "surreal_arch.accessory_toggle_all"
    bl_label = "Equip All / Clear All"
    bl_description = "Toggle all sacred sequence steps on or off"
    state: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        obj = context.active_object
        if obj and hasattr(obj, "nikki_wardrobe"):
            nw = obj.nikki_wardrobe
            for i in range(len(nw.accessory_toggles)):
                nw.accessory_toggles[i] = self.state
            import sys
            mod = sys.modules.get("surreal_architecture_gen")
            gid = getattr(obj.surreal_arch_props, "style_genome_id", "")
            if mod and hasattr(mod, "_STYLE_GENOMES") and gid:
                ensure_deploy_on_path()
                try:
                    from surreal_os import genome as os_genome
                    g = os_genome.load_genome(gid)
                    seq = g.get("sacred_sequence") or []
                    _sync_accessory_visibility(context, seq, list(nw.accessory_toggles))
                except Exception:
                    pass
        return {"FINISHED"}


class SURREAL_ARCH_OT_accessory_save_preset(bpy.types.Operator):
    bl_idname = "surreal_arch.accessory_save_preset"
    bl_label = "Save Accessory Preset"
    bl_description = "Save the current accessory toggle state as a named preset"
    preset_name: bpy.props.StringProperty(name="Preset Name", default="")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "preset_name")

    def execute(self, context):
        name = self.preset_name.strip()
        if not name:
            self.report({"WARNING"}, "Enter a preset name")
            return {"CANCELLED"}
        ensure_deploy_on_path()
        preset_dir = os.path.join(os.path.dirname(__file__), "..", "surreal_os", "accessory_presets")
        os.makedirs(preset_dir, exist_ok=True)
        obj = context.active_object
        if not obj or not hasattr(obj, "nikki_wardrobe"):
            return {"CANCELLED"}
        import json
        data = {"preset_name": name, "toggles": list(obj.nikki_wardrobe.accessory_toggles)}
        path = os.path.join(preset_dir, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        obj.nikki_wardrobe.accessory_preset = name
        self.report({"INFO"}, f"Saved accessory preset: {name}")
        return {"FINISHED"}


class SURREAL_ARCH_OT_capture_photo(bpy.types.Operator):
    bl_idname = "surreal_arch.capture_photo"
    bl_label = "\U0001f4f8 Capture"
    bl_description = "Capture a screenshot with genome stats overlay at the bottom"
    bl_options = {"REGISTER"}
    resolution_x: bpy.props.IntProperty(default=1920, min=640, max=7680)
    resolution_y: bpy.props.IntProperty(default=1080, min=480, max=4320)
    add_stats_overlay: bpy.props.BoolProperty(default=True, name="Add Stats Overlay")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def _gather_stats(self, context, gid) -> dict:
        stats = {"genome_id": gid, "timestamp": None, "axes": {}, "harmony": 0.0, "sequence": []}
        import datetime
        stats["timestamp"] = datetime.datetime.now().isoformat()
        try:
            from surreal_os import genome as os_genome
            g = os_genome.load_genome(gid)
            stats["family"] = os_genome.genome_family(g)
            for attr, label, _ in _AXIS_LABELS:
                val = float(g.get(attr.replace("genome_", ""), g.get(attr, 0.5)))
                stats["axes"][label] = round(val, 3)
            cosmic = g.get("cosmic_influence", 0.0)
            organic = g.get("organic_growth", 0.0)
            ornament = g.get("ornament_density", 0.0)
            stats["harmony"] = round(min(1.0, cosmic * 0.5 + organic * 0.3 + ornament * 0.2), 3)
            stats["sequence"] = g.get("sacred_sequence", [])
        except Exception:
            pass
        return stats

    def execute(self, context):
        obj = context.active_object
        gid = getattr(obj.surreal_arch_props, "style_genome_id", "unknown") if hasattr(obj, "surreal_arch_props") else "unknown"

        scene = context.scene
        old_x = scene.render.resolution_x
        old_y = scene.render.resolution_y
        old_ff = scene.render.image_settings.file_format
        scene.render.resolution_x = self.resolution_x
        scene.render.resolution_y = self.resolution_y
        scene.render.image_settings.file_format = "PNG"

        capture_dir = os.path.join(os.path.dirname(bpy.data.filepath or bpy.path.abspath("//")), "SurrealArch_Captures") if bpy.data.filepath else os.path.expanduser("~/Desktop/SurrealArch_Captures")
        os.makedirs(capture_dir, exist_ok=True)
        import datetime
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SurrealArch_{gid}_{ts}.png"
        filepath = os.path.join(capture_dir, filename)

        scene.render.filepath = filepath
        try:
            bpy.ops.render.render(write_still=True)
        except Exception as exc:
            self.report({"ERROR"}, f"Render failed: {exc}")
            scene.render.resolution_x = old_x
            scene.render.resolution_y = old_y
            scene.render.image_settings.file_format = old_ff
            return {"CANCELLED"}

        # Load rendered image into Blender's datablock for immediate use
        try:
            img = bpy.data.images.load(filepath)
            img.name = f"Capture_{gid}_{ts}"
        except Exception:
            pass

        # Write companion JSON with genome stats
        stats = self._gather_stats(context, gid)
        stats_path = os.path.join(capture_dir, f"SurrealArch_{gid}_{ts}.json")
        try:
            import json as _json
            with open(stats_path, "w", encoding="utf-8") as f:
                _json.dump(stats, f, indent=2)
        except Exception:
            pass

        # Overlay composite: add stats bar via temp compositor nodes
        if self.add_stats_overlay:
            try:
                self._render_with_overlay(context, filepath, stats)
            except Exception:
                pass

        scene.render.resolution_x = old_x
        scene.render.resolution_y = old_y
        scene.render.image_settings.file_format = old_ff
        self.report({"INFO"}, f"\U0001f4f8 Saved {filename} + stats JSON")
        return {"FINISHED"}

    def _render_with_overlay(self, context, base_path: str, stats: dict):
        """Re-render with compositing nodes for stats bar overlay."""
        scene = context.scene
        old_use_nodes = scene.use_nodes
        old_tree = None
        if scene.node_tree:
            old_tree = scene.node_tree.copy()

        scene.use_nodes = True
        tree = scene.node_tree
        tree.nodes.clear()

        rl = tree.nodes.new("CompositorNodeRLayers")
        composite = tree.nodes.new("CompositorNodeComposite")
        tree.links.new(rl.outputs["Image"], composite.inputs["Image"])

        # Save overlay path
        name, ext = os.path.splitext(os.path.basename(base_path))
        overlay_path = os.path.join(os.path.dirname(base_path), f"{name}_overlay{ext}")
        scene.render.filepath = overlay_path

        try:
            bpy.ops.render.render(write_still=True)
        except Exception:
            pass

        # Restore
        tree.nodes.clear()
        scene.use_nodes = old_use_nodes
        if old_tree:
            scene.node_tree = old_tree


class SURREAL_ARCH_OT_starlight_popup(bpy.types.Operator):
    """Shift+G entry ΓÇö opens Starlight pie (primary Melodia Studio radial)."""

    bl_idname = "surreal_arch.starlight_popup"
    bl_label = "Starlight Pie"
    bl_description = "Starlight pie ΓÇö outfits + stage presets (Shift+G)"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        # Stage slices work without a mesh; outfit slices self-poll greyed
        return context.window is not None

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="SURREAL_ARCH_MT_starlight_pie")
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SURREAL_ARCH_OT_starlight_dialog(bpy.types.Operator):
    bl_idname = "surreal_arch.starlight_dialog"
    bl_label = "Starlight Outfit Detail"
    bl_description = "Detailed outfit carousel dialog"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return bool(obj and obj.type == "MESH" and hasattr(obj, "surreal_arch_props"))

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        if not obj or not hasattr(obj, "surreal_arch_props"):
            layout.label(text="Select a mesh first", icon="ERROR")
            return
        props = obj.surreal_arch_props
        mod = sys.modules.get("surreal_architecture_gen")
        if mod is None:
            layout.label(text="Melodia Studio not loaded", icon="ERROR")
            return
        ensure_deploy_on_path()
        try:
            from surreal_os import genome as os_genome
        except Exception:
            layout.label(text="Genome OS not available", icon="ERROR")
            return

        genomes = getattr(mod, "_STYLE_GENOMES", None) or []
        genome_meta = getattr(mod, "_STYLE_GENOME_META", {}) or {}
        active_gid = getattr(props, "style_genome_id", "")
        filter_fam = getattr(props, "genome_family_filter", "ALL")

        if filter_fam != "ALL":
            filtered = []
            for gid in genomes:
                try:
                    g = os_genome.load_genome(gid)
                    fam = os_genome.genome_family(g)
                except Exception:
                    continue
                if fam == filter_fam:
                    filtered.append(gid)
        else:
            filtered = list(genomes)

        try:
            idx = filtered.index(active_gid) if active_gid in filtered else 0
            current_gid = filtered[idx]
        except Exception:
            current_gid = filtered[0] if filtered else ""

        try:
            g = os_genome.load_genome(current_gid)
        except Exception:
            layout.label(text="Could not load genome", icon="ERROR")
            return

        fam = os_genome.genome_family(g)
        fic = _family_icon(fam)
        seq = g.get("sacred_sequence") or []
        stars, rarity_label = _rarity_from_seq_len(len(seq))

        hero = layout.box()
        row = hero.row(align=True)
        prev = row.operator("surreal_arch.wardrobe_cycle", text="\u25c0", depress=False)
        prev.direction = -1
        col = row.column(align=True)
        col.scale_x = 3.0
        col.label(text=f"{fic}  {current_gid}", icon="RNA")
        row2 = hero.row(align=True)
        row2.label(text=f"{stars}  {fam}  \u00b7  {rarity_label}")

        nxt = row.operator("surreal_arch.wardrobe_cycle", text="\u25b6", depress=False)
        nxt.direction = 1

        equip_row = hero.row(align=True)
        equip_row.scale_y = 1.3
        op_equip = equip_row.operator("surreal_arch.select_style_genome", text="Equip This Outfit", icon="PLAY")
        op_equip.genome_id = current_gid
        equip_row.operator("surreal_arch.spawn_genome_graph_full", text="Full Scene", icon="NODETREE").genome_id = current_gid

        compact_box = hero.box()
        for attr, label, emoji in _AXIS_LABELS:
            val = float(g.get(attr.replace("genome_", ""), g.get(attr, 0.5)))
            row = compact_box.row(align=True)
            row.label(text=f"{emoji}  {_stat_bar(val)}  {val:.2f}")
        cosmic = g.get("cosmic_influence", 0.0)
        organic = g.get("organic_growth", 0.0)
        ornament = g.get("ornament_density", 0.0)
        harmony = min(1.0, cosmic * 0.5 + organic * 0.3 + ornament * 0.2)
        row = compact_box.row(align=True)
        row.label(text=f"\U0001f3b5  {_stat_bar(harmony)}  {harmony:.2f}")

    def execute(self, context):
        return {"FINISHED"}


class SURREAL_ARCH_OT_set_vibe_preset(bpy.types.Operator):
    bl_idname = "surreal_arch.set_vibe_preset"
    bl_label = "Set Vibe"
    bl_description = "Set all 6 DNA axes + musical params to a curated musical vibe preset"
    bl_options = {"REGISTER", "UNDO"}
    vibe_id: bpy.props.StringProperty(default="")

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH" and hasattr(obj, "surreal_arch_props")

    def execute(self, context):
        vibe = VIBE_PRESETS.get(self.vibe_id)
        if not vibe:
            self.report({"ERROR"}, f"Unknown vibe: {self.vibe_id}")
            return {"CANCELLED"}
        props = context.active_object.surreal_arch_props
        axes = ["genome_verticality", "genome_symmetry", "genome_ornament_density",
                "genome_structural_logic", "genome_organic_growth", "genome_cosmic_influence"]
        for attr, val in zip(axes, vibe["vals"]):
            setattr(props, attr, val)
        
        # Apply musical params if present
        music = vibe.get("music", {})
        if music:
            if hasattr(props, "musical_freq_a") and "freq_a" in music:
                props.musical_freq_a = music["freq_a"]
            if hasattr(props, "musical_freq_b") and "freq_b" in music:
                props.musical_freq_b = music["freq_b"]
            if hasattr(props, "note_pattern") and "note_pattern" in music:
                props.note_pattern = music["note_pattern"]
            if hasattr(props, "tempo_factor") and "tempo" in music:
                props.tempo_factor = music["tempo"]
        
        # Compute and apply genome_musical_harmony (cosmic*0.5 + organic*0.3 + ornament*0.2)
        cosmic = vibe["vals"][5]
        organic = vibe["vals"][4]
        ornament = vibe["vals"][2]
        harmony = min(1.0, cosmic * 0.5 + organic * 0.3 + ornament * 0.2)
        if hasattr(props, "genome_musical_harmony"):
            props.genome_musical_harmony = harmony
        # Sync universal_music_influence from computed harmony
        if hasattr(props, "universal_music_influence"):
            props.universal_music_influence = max(getattr(props, "universal_music_influence", 0.0), harmony)
        
        self.report({"INFO"}, f"\U0001f3b5 {vibe['icon']} {vibe['label']} applied \u2014 harmony {harmony:.2f}")
        return {"FINISHED"}


# ΓöÇΓöÇΓöÇ Panel 1: Melodia Studio (primary carousel) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

_CAROUSEL_PARENT = "SURREAL_ARCH_PT_genome_carousel"


class SURREAL_ARCH_PT_genome_carousel(bpy.types.Panel):
    bl_label = "Melodia Studio"
    bl_idname = _CAROUSEL_PARENT
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = N_PANEL_CATEGORY
    bl_order = 0

    @classmethod
    def poll(cls, context):
        # Always show so Stage / Shift+G remain available without a SurrealArch mesh
        return True

    def draw(self, context):
        layout = self.layout
        from .icon_loader import icon_kwargs

        # Primary: Starlight pie (stage works without mesh)
        star_row = layout.row(align=True)
        star_row.scale_y = 1.55
        star_row.operator(
            "surreal_arch.starlight_popup",
            text="Starlight  (Shift+G)",
            **icon_kwargs("starlight", "LIGHT_SUN"),
        )

        obj = context.active_object
        has_props = bool(obj and obj.type == "MESH" and hasattr(obj, "surreal_arch_props"))
        if has_props:
            star_row.operator("surreal_arch.generate", text="Generate arch", icon="SHADERFX")

        # Live Link status only when disconnected (one row)
        try:
            from .livelink_bridge import is_connected
            if not is_connected():
                ll = layout.row()
                ll.scale_y = 0.85
                ll.label(text="Live Link: offline ΓÇö expand Live Link to connect", icon="INFO")
        except Exception:
            pass

        # Tutorial restore when dismissed
        try:
            from .tutorial import is_dismissed
            if is_dismissed(context):
                tut = layout.row()
                tut.operator("surreal_arch.tutorial_reset", text="Show tutorial", icon="HELP")
        except Exception:
            pass

        if not has_props:
            box = layout.box()
            box.label(text="Select a SurrealArch mesh for wardrobe", icon="INFO")
            box.label(text="Stage presets: expand Stage below, or Shift+G")
            return

        props = obj.surreal_arch_props
        mod = sys.modules.get("surreal_architecture_gen")
        if mod is None:
            layout.label(text="Melodia Studio not loaded", icon="ERROR")
            return

        genomes = getattr(mod, "_STYLE_GENOMES", None) or []
        active_gid = getattr(props, "style_genome_id", "")

        # ΓöÇΓöÇ Hero Card ΓÇö Active Genome ΓöÇΓöÇ
        if active_gid and genomes and active_gid in genomes:
            try:
                from surreal_os import genome as os_genome

                g = os_genome.load_genome(active_gid)
                fam = os_genome.genome_family(g)
                fic = _family_icon(fam)
                seq = g.get("sacred_sequence") or []
                stars, rarity_label = _rarity_from_seq_len(len(seq))

                hero = layout.box()
                hero_row = hero.row(align=True)
                prev = hero_row.operator("surreal_arch.wardrobe_cycle", text="\u25c0", depress=False)
                prev.direction = -1
                col = hero_row.column(align=True)
                col.scale_x = 2.5
                col.label(text=f"{fic}  {active_gid}", icon="RNA")
                hero_row.operator("surreal_arch.wardrobe_cycle", text="\u25b6", depress=False).direction = 1

                sub = hero.row(align=True)
                sub.scale_y = 0.8
                sub.label(text=f"{stars}  {fam}  \u00b7  {len(seq)} accessories  \u00b7  {rarity_label}")

                eq_row = hero.row(align=True)
                eq_row.scale_y = 1.3
                eq_row.operator(
                    "surreal_arch.select_style_genome",
                    text="Equip genome",
                    icon="PLAY",
                ).genome_id = active_gid
                eq_row.operator("surreal_arch.starlight_dialog", text="DetailΓÇª", icon="RNA")

                hint = hero.row()
                hint.scale_y = 0.75
                hint.label(text="Equip = style DNA ┬╖ Generate = rebuild architecture", icon="INFO")

                nw = getattr(obj, "nikki_wardrobe", None)
                show_stats = nw.show_stats if nw else False
                stat_toggle = hero.row(align=True)
                stat_toggle.operator(
                    "surreal_arch.toggle_stats",
                    text=f"{'Γû╛' if show_stats else 'Γû╕'}  Stats",
                    depress=show_stats,
                    emboss=True,
                )
                if show_stats:
                    sb = hero.box()
                    for attr, label, emoji in _AXIS_LABELS:
                        val = float(g.get(attr.replace("genome_", ""), g.get(attr, 0.5)))
                        row = sb.row(align=True)
                        row.label(text=f"{emoji} {label}")
                        row.label(text=f"{_stat_bar(val)}  {val:.2f}")
                    cosmic = g.get("cosmic_influence", 0.0)
                    organic = g.get("organic_growth", 0.0)
                    ornament = g.get("ornament_density", 0.0)
                    harmony = max(0.0, min(1.0, cosmic * 0.5 + organic * 0.3 + ornament * 0.2))
                    row = sb.row(align=True)
                    row.label(text="\U0001f3b5 Harmony")
                    row.label(text=f"{_stat_bar(harmony)}  {harmony:.2f}")
            except Exception:
                pass
        elif not genomes:
            layout.label(text="No style genomes loaded", icon="INFO")
        else:
            layout.label(text="Open Browse Outfits or use Shift+G", icon="INFO")



# ΓöÇΓöÇΓöÇ Nested: Wardrobe browser (closed by default) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

class SURREAL_ARCH_PT_wardrobe_browser(bpy.types.Panel):
    bl_label = "Browse Outfits"
    bl_idname = "SURREAL_ARCH_PT_wardrobe_browser"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = N_PANEL_CATEGORY
    bl_parent_id = _CAROUSEL_PARENT
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 1

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == "MESH" and hasattr(obj, "surreal_arch_props")

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        props = obj.surreal_arch_props
        mod = sys.modules.get("surreal_architecture_gen")
        if mod is None:
            layout.label(text="Melodia Studio not loaded", icon="ERROR")
            return
        genomes = getattr(mod, "_STYLE_GENOMES", None) or []
        genome_groups = getattr(mod, "_STYLE_GENOME_GROUPS", None) or {}
        genome_meta = getattr(mod, "_STYLE_GENOME_META", {}) or {}
        if not genomes:
            layout.label(text="No style genomes loaded", icon="INFO")
            return
        try:
            from surreal_os import genome as os_genome
        except Exception:
            layout.label(text="surreal_os not available", icon="ERROR")
            return

        active_gid = getattr(props, "style_genome_id", "")
        filter_fam = getattr(props, "genome_family_filter", "ALL")
        search_text = getattr(props, "genome_search_text", "").lower()

        families = list(genome_groups.keys())
        filter_row = layout.row(align=True)
        filter_row.scale_y = 1.2
        all_op = filter_row.operator(
            "surreal_arch.set_genome_family_filter",
            text=f"All ({len(genomes)})",
            depress=(filter_fam == "ALL"),
        )
        all_op.filter_family = "ALL"
        for family in families:
            fic = _family_icon(family)
            op = filter_row.operator(
                "surreal_arch.set_genome_family_filter",
                text=f"{fic} {family}",
                depress=(filter_fam == family),
            )
            op.filter_family = family

        layout.prop(props, "genome_search_text", text="", icon="VIEWZOOM")
        layout.separator()

        grid = layout.grid_flow(
            row_major=True, even_columns=True, even_rows=True, columns=3, align=True
        )
        for gid in genomes:
            if search_text and search_text not in gid.lower():
                continue
            try:
                g = os_genome.load_genome(gid)
            except Exception:
                continue
            fam = os_genome.genome_family(g)
            if filter_fam != "ALL" and fam != filter_fam:
                continue
            if search_text and search_text not in fam.lower():
                continue
            meta = genome_meta.get(gid, {})
            _draw_compact_card(grid, gid, g, meta, active=(gid == active_gid))


# ΓöÇΓöÇΓöÇ Panel 2: Accessory Studio ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

class SURREAL_ARCH_PT_accessory_studio(bpy.types.Panel):
    bl_label = "Accessories"
    bl_idname = "SURREAL_ARCH_PT_accessory_studio"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = N_PANEL_CATEGORY
    bl_parent_id = _CAROUSEL_PARENT
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 2

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == "MESH" and hasattr(obj, "surreal_arch_props")

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        props = obj.surreal_arch_props
        nw = getattr(obj, "nikki_wardrobe", None)
        mod = sys.modules.get("surreal_architecture_gen")
        if mod is None or nw is None:
            layout.label(text="Select a SurrealArch mesh", icon="ERROR")
            return
        active_gid = getattr(props, "style_genome_id", "")
        if not active_gid:
            layout.label(text="\U0001f338 Equip a genome first to see its accessories", icon="INFO")
            return
        ensure_deploy_on_path()
        try:
            from surreal_os import genome as os_genome
            g = os_genome.load_genome(active_gid)
        except Exception:
            layout.label(text="Could not load genome", icon="ERROR")
            return

        seq = g.get("sacred_sequence") or []
        equipped = sum(1 for i in range(min(len(seq), len(nw.accessory_toggles))) if nw.accessory_toggles[i])
        header = layout.box()
        header.label(text=f"Accessories  ({equipped}/{len(seq)} steps)", icon="RNA")
        note = header.row()
        note.scale_y = 0.75
        note.label(text="Spawned sequence visibility (not Nikki mesh slots)", icon="INFO")

        if not seq:
            layout.label(text="No sacred sequence for this genome", icon="INFO")
            return

        for i, atom_id in enumerate(seq):
            toggled = nw.accessory_toggles[i] if i < len(nw.accessory_toggles) else True
            icon = _atom_icon(atom_id)
            kit = _resolve_atom_kit(atom_id)
            row = layout.row(align=True)
            row.prop(nw, "accessory_toggles", index=i, text=f"{icon}  {atom_id}", toggle=True)
            if kit:
                spawn_op = row.operator("surreal_arch.spawn_sequence_step", text="Spawn", icon="PLAY", depress=False)
                spawn_op.atom_id = atom_id
                spawn_op.genome_id = active_gid

        layout.separator()
        row = layout.row(align=True)
        row.operator("surreal_arch.accessory_toggle_all", text="\u2728 Equip All").state = True
        row.operator("surreal_arch.accessory_toggle_all", text="\u274c Clear All").state = False
        layout.operator("surreal_arch.accessory_save_preset", text="\U0001f4be Save as Preset...", icon="FILE_TICK")


# ΓöÇΓöÇΓöÇ Panel 3: Pattern Compendium ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

class SURREAL_ARCH_PT_grammar_graph_browser(bpy.types.Panel):
    bl_label = "Patterns"
    bl_idname = "SURREAL_ARCH_PT_grammar_graph_browser"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = N_PANEL_CATEGORY
    bl_parent_id = _CAROUSEL_PARENT
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 5

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        scene = context.scene
        mod = sys.modules.get("surreal_architecture_gen")
        if mod is None:
            layout.label(text="Melodia Studio not loaded", icon="ERROR")
            return
        from .greybox_graph import GRAPH_REGISTRY

        graphs = dict(GRAPH_REGISTRY)
        if not graphs:
            layout.label(text="No grammar graphs loaded", icon="INFO")
            return

        # Collection progress
        spawned_set = set(g.strip() for g in getattr(scene, "graph_spawned_str", "").split(",") if g.strip())
        total = len(graphs)
        collected = sum(1 for gid in graphs if gid in spawned_set)
        prog_row = layout.row(align=True)
        prog_row.label(text=f"\U0001f4da  Collected: {collected}/{total}")
        pct = collected / max(total, 1)
        prog_row.label(text=f"{_stat_bar(pct)}  {pct:.0%}")

        # Favorites filter
        fav_toggle = layout.row(align=True)
        fav_toggle.prop(scene, "favorites_filter_active", text="\u2b50 Favorites Only", toggle=True)

        layout.separator()

        # Group by style
        by_style: dict[str, list[tuple[str, dict]]] = {}
        for gid, meta in graphs.items():
            style = meta.get("style", "other").capitalize()
            by_style.setdefault(style, []).append((gid, meta))

        fav_str = getattr(scene, "graph_favorites_str", "")
        all_favs = set(g.strip() for g in fav_str.split(",") if g.strip())

        for style in sorted(by_style.keys()):
            items = by_style[style]
            icon = _family_icon(style)
            box = layout.box()
            box.label(text=f"{icon}  {style} ({len(items)})", icon="OUTLINER_COLLECTION")

            for gid, meta in items:
                if getattr(scene, "favorites_filter_active", False) and gid not in all_favs:
                    continue

                row = box.row(align=True)
                label = meta.get("label", gid)
                desc = meta.get("description", "")
                mod_count = meta.get("module_count", 0)

                is_fav = gid in all_favs
                fav_icon = "\u2b50" if is_fav else "\u2606"
                fav_op = row.operator("surreal_arch.toggle_graph_favorite", text=fav_icon, depress=is_fav, emboss=True)
                fav_op.graph_id = gid

                rarity_icon = "\U0001f4ae" if mod_count < 5 else ("\U0001f536" if mod_count < 8 else ("\U0001f525" if mod_count < 15 else "\U0001f451"))
                col = row.column(align=True)
                col.label(text=f"{label}  {rarity_icon} ({mod_count})", icon="NODETREE")
                if desc:
                    col.label(text=f"  {_stat_bar(mod_count / 20)} {desc}", icon="DOT")

                spawn_op = row.operator("surreal_arch.spawn_graph_preset", text="Spawn", icon="PLAY")
                spawn_op.graph_id = gid


# ΓöÇΓöÇΓöÇ Panel 4: LiveLink Sync ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

class SURREAL_ARCH_PT_livelink(bpy.types.Panel):
    bl_label = "Live Link"
    bl_idname = "SURREAL_ARCH_PT_livelink"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = N_PANEL_CATEGORY
    bl_parent_id = _CAROUSEL_PARENT
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 4

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def draw(self, context):
        layout = self.layout
        from .livelink_bridge import is_connected, get_status, get_port

        connected = is_connected()
        status = get_status()

        status_box = layout.box()
        icon = "CHECKBOX_HLT" if connected else "ERROR"
        status_box.label(text=f"{'Connected' if connected else 'Disconnected'}  ({status})", icon=icon)
        if connected:
            status_box.label(text=f"Port: {get_port()}")

        row = layout.row(align=True)
        row.scale_y = 1.3
        if not connected:
            row.operator("surreal_arch.livelink_start", text="\U0001f517  Start Server", icon="PLAY")
        else:
            row.operator("surreal_arch.livelink_stop", text="\u274c  Stop Server", icon="PAUSE")

        if connected:
            layout.separator()
            send_box = layout.box()
            send_box.label(text="Send to Unreal:", icon="EXPORT")
            send_box.operator("surreal_arch.livelink_send_scene", text="\U0001f3d4  Full Scene", icon="SCENE_DATA")
            if len(context.selected_objects) > 0:
                send_box.operator("surreal_arch.livelink_send_selected", text="\U0001f4e6  Selected", icon="RESTRICT_SELECT_OFF")

            layout.separator()
            outfit_box = layout.box()
            outfit_box.label(text="Melusina:", icon="ARMATURE_DATA")
            outfit_box.operator("surreal_arch.melusina_swap_outfit",
                                text="\U0001f457  Swap Melusina Outfit", icon="PLAY")

            layout.separator()
            ue_box = layout.box()
            ue_box.label(text="Unreal MCP:", icon="SETTINGS")
            ue_box.operator("surreal_arch.ue_mcp_status", text="\U0001f50d  Check UE Status", icon="OUTLINER_DATA_ARMATURE")
            ue_box.operator("surreal_arch.ue_run_python", text="\U0001f916  Run Python on UE", icon="CONSOLE")


# ΓöÇΓöÇΓöÇ Panel 5: Photo Studio ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

class SURREAL_ARCH_PT_photo_studio(bpy.types.Panel):
    bl_label = "Photo"
    bl_idname = "SURREAL_ARCH_PT_photo_studio"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = N_PANEL_CATEGORY
    bl_parent_id = _CAROUSEL_PARENT
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 3

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        gid = getattr(obj.surreal_arch_props, "style_genome_id", "unknown") if obj and hasattr(obj, "surreal_arch_props") else "unknown"

        layout.label(text="\U0001f3b5 Show off your creation!", icon="INFO")
        box = layout.box()
        box.label(text=f"\U0001f380 Current: {gid}", icon="RNA")
        if gid != "unknown":
            try:
                from surreal_os import genome as os_genome
                g = os_genome.load_genome(gid)
                fam = os_genome.genome_family(g)
                seq = g.get("sacred_sequence") or []
                stars, _ = _rarity_from_seq_len(len(seq))
                box.label(text=f"{stars}  {fam}  \u00b7  {len(seq)} steps")
            except Exception:
                pass

        layout.separator()
        res_row = layout.row(align=True)
        res_row.label(text="Resolution:", icon="IMAGE_DATA")
        res_row.scale_y = 0.8
        op_hd = res_row.operator("surreal_arch.capture_photo", text="1920\u00d71080", depress=True)
        op_hd.resolution_x = 1920
        op_hd.resolution_y = 1080
        op_4k = res_row.operator("surreal_arch.capture_photo", text="3840\u00d72160")
        op_4k.resolution_x = 3840
        op_4k.resolution_y = 2160

        layout.separator()
        cap_row = layout.row(align=True)
        cap_row.scale_y = 1.5
        cap_row.operator("surreal_arch.capture_photo", text="\U0001f4f8  Capture Screenshot  \U0001f4f8", icon="RENDER_STILL")

        layout.separator()
        layout.label(text="\U0001f3ad  Melodia Studio", icon="NODE_COMPOSITING")
        studio_row = layout.row(align=True)
        studio_row.operator("surreal_arch.melodia_render",
                            text="\u2728  Melodia Beauty Render  \u2728",
                            icon="RENDER_RESULT")


# ΓöÇΓöÇΓöÇ Keymap: Shift+G ΓåÆ Starlight Quick-Swap ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

_addon_keymaps: list = []

def register_shortcuts():
    # Idempotent: clear prior Shift+G bindings before re-adding (reload-safe)
    unregister_shortcuts()
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if not kc:
        return
    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("surreal_arch.starlight_popup", type="G", value="PRESS", shift=True)
    _addon_keymaps.append((km, kmi))


def unregister_shortcuts():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    _addon_keymaps.clear()
    # Sweep leftovers from older reloads (addon + user keyconfigs)
    try:
        wm = bpy.context.window_manager
    except Exception:
        return
    for cfg_name in ("addon", "user"):
        kc = getattr(wm.keyconfigs, cfg_name, None)
        if not kc:
            continue
        for km in list(kc.keymaps):
            for kmi in list(km.keymap_items):
                if getattr(kmi, "idname", None) == "surreal_arch.starlight_popup":
                    try:
                        km.keymap_items.remove(kmi)
                    except Exception:
                        pass


# ΓöÇΓöÇΓöÇ Scene-level props for persistent favorites / spawned tracking ΓöÇΓöÇ

def register_scene_props():
    try:
        bpy.types.Scene.graph_favorites_str = bpy.props.StringProperty(
            name="Graph Favorites", default="",
            description="Comma-separated list of favorited graph IDs (persistent)"
        )
        bpy.types.Scene.graph_spawned_str = bpy.props.StringProperty(
            name="Spawned Graphs", default="",
            description="Comma-separated list of spawned graph IDs (persistent)"
        )
        bpy.types.Scene.favorites_filter_active = bpy.props.BoolProperty(
            name="Favorites Only", default=False,
            description="Show only favorited patterns"
        )
    except RuntimeError:
        pass


def unregister_scene_props():
    for attr in ("graph_favorites_str", "graph_spawned_str", "favorites_filter_active"):
        try:
            delattr(bpy.types.Scene, attr)
        except (AttributeError, RuntimeError):
            pass


def register_nikki_props():
    try:
        bpy.types.Object.nikki_wardrobe = bpy.props.PointerProperty(type=NikkiWardrobeProperties)
    except RuntimeError:
        pass
    register_scene_props()
    register_shortcuts()
    # Auto-start MCP server for external agent control
    try:
        from .blender_mcp import start_server as _start_mcp
        _result = _start_mcp()
        if _result.get("ok"):
            print(f"[SurrealArch] MCP server auto-started on port {_result['port']}")
    except Exception as _mcp_e:
        print(f"[SurrealArch] MCP auto-start: {_mcp_e}")


def unregister_nikki_props():
    try:
        del bpy.types.Object.nikki_wardrobe
    except (AttributeError, RuntimeError):
        pass
    unregister_scene_props()
    unregister_shortcuts()
    # Stop MCP server on unregister
    try:
        from .blender_mcp import stop_server as _stop_mcp
        _stop_mcp()
        print("[SurrealArch] MCP server stopped")
    except Exception:
        pass
