"""Architecturally researched quick-launch presets (v2.65)."""

from __future__ import annotations

import bpy

RESEARCH_PRESETS = {
    "romanesque_cloister_arcade": {
        "label": "Romanesque Cloister Arcade",
        "description": "Round arches on colonettes, barrel vault segment, snap at bay ends",
        "research_ref": "Cistercian cloister typology — paired colonettes + semicircular arch + quadripartite vault rhythm",
        "props": dict(
            arch_type="GB_ROMANESQUE_ARCADE",
            gb_width=3.2,
            gb_height=4.2,
            gb_wall_thick=0.35,
            gb_leg_thick=0.18,
            gb_trim_mode="RECESS",
            gb_trim_recess=0.06,
            gb_corridor_ceiling="FULL",
            material_choice="STONE",
            unit_size=3.2,
        ),
    },
    "brutalist_pilotis_hall": {
        "label": "Brutalist Pilotis Hall",
        "description": "Column grid + slab, offset recess panels for trim sheets",
        "research_ref": "Le Corbusier pilotis + béton brut — structural grid with deep panel recesses",
        "props": dict(
            arch_type="GREYBOX_PILLAR_HALL",
            gb_cols_x=4,
            gb_cols_y=3,
            gb_spacing=4.0,
            gb_height=3.6,
            gb_wall_thick=0.45,
            gb_leg_thick=0.55,
            gb_trim_mode="RECESS",
            gb_trim_recess=0.08,
            gb_wainscot_height=0.0,
            gb_baseboard_height=0.15,
            material_choice="STONE",
            unit_size=4.0,
        ),
    },
    "venetian_loggia_bay": {
        "label": "Venetian Loggia Bay",
        "description": "Bifora rhythm + cornice shelf — Palazzo piano nobile reference",
        "research_ref": "Venetian Gothic bifora + loggia cornice (Boscarino et al. façade analysis)",
        "props": dict(
            arch_type="GB_VENETIAN_LOGGIA",
            gb_width=3.0,
            gb_height=4.8,
            gb_wall_thick=0.35,
            gb_window_sill=1.0,
            gb_window_height=2.6,
            bifora_lights=2,
            gb_trim_mode="RECESS",
            gb_trim_recess=0.05,
            material_choice="MARBLE",
            unit_size=3.0,
        ),
    },
    "romanesque_apse_choir": {
        "label": "Romanesque Choir + Apse",
        "description": "Semicircular apse recess with barrel vault — choir terminus",
        "research_ref": "Cistercian choir apse typology — semicircular shell + barrel vault cap",
        "props": dict(
            arch_type="GB_ROMANESQUE_APSE",
            gb_width=4.0,
            gb_depth=3.5,
            gb_height=4.5,
            gb_wall_thick=0.35,
            gb_leg_thick=0.18,
            gb_trim_mode="RECESS",
            gb_trim_recess=0.06,
            gb_corridor_ceiling="FULL",
            material_choice="STONE",
            unit_size=4.0,
        ),
    },
    "scifi_pressure_door_airlock": {
        "label": "Sci-Fi Pressure Door Airlock",
        "description": "Gasket recess, frame offset, MUST_CONNECT door snap",
        "research_ref": "Industrial airlock gasket recess + pressure-frame offset for modular sci-fi corridors",
        "props": dict(
            arch_type="GB_SCIFI_PRESSURE_DOOR",
            gb_length=3.5,
            gb_corridor_profile="DOUBLE",
            gb_height=3.2,
            gb_wall_thick=0.35,
            gb_door_width=1.2,
            gb_door_height=2.35,
            gb_trim_mode="RECESS",
            gb_trim_recess=0.1,
            gb_frame=True,
            material_choice="METAL",
            unit_size=3.5,
        ),
    },
    "zen_roji_step": {
        "label": "Zen Roji Dew Path",
        "description": "Flat slab + raised edge stones — roji approach segment with path snaps",
        "research_ref": "Roji dew-path typology — stepping stones flanking central slab (tea garden entry)",
        "props": dict(
            arch_type="GB_ZEN_ROJI_STEP",
            gb_length=4.5,
            gb_width=1.8,
            gb_wall_thick=0.12,
            gb_trim_mode="RECESS",
            gb_trim_recess=0.04,
            material_choice="STONE",
            unit_size=2.0,
        ),
    },
    "zen_torii_gate_modular": {
        "label": "Zen Torii Gate (Greybox)",
        "description": "Hashira posts, nuki tie beam, kasagi lintel — MUST_CONNECT path snaps",
        "research_ref": "Shinto torii typology — hashira / nuki / kasagi modular kit for shrine entry",
        "props": dict(
            arch_type="GB_ZEN_TORII_GATE",
            torii_width=3.6,
            torii_height=4.2,
            torii_post_radius=0.18,
            gb_wall_thick=0.2,
            gb_trim_mode="RECESS",
            gb_trim_recess=0.05,
            material_choice="STONE",
            unit_size=3.6,
        ),
    },
    "zen_tsukubai_basin": {
        "label": "Zen Tsukubai Basin",
        "description": "Stone pad with recess bowl + surround flagstones — ritual hand-wash station",
        "research_ref": "Tsukubai chōzubachi typology — basin recess + flagstone surround for roji tea path",
        "props": dict(
            arch_type="GB_ZEN_TSUKUBAI",
            gb_width=1.6,
            gb_depth=1.6,
            gb_height=0.45,
            gb_wall_thick=0.14,
            gb_trim_mode="RECESS",
            gb_trim_recess=0.06,
            material_choice="STONE",
            unit_size=2.0,
        ),
    },
}


def apply_research_preset(props, preset_id):
    spec = RESEARCH_PRESETS.get(preset_id)
    if not spec:
        raise KeyError(preset_id)
    for key, val in spec["props"].items():
        if hasattr(props, key):
            setattr(props, key, val)
    return spec


def register_research_preset_operators(monolith):
    classes = []
    for preset_id, spec in RESEARCH_PRESETS.items():
        op_id = f"surreal_arch.preset_research_{preset_id}"

        def _make_execute(pid=preset_id):
            def execute(self, context):
                obj = context.active_object
                if not obj or not hasattr(obj, "surreal_arch_props"):
                    self.report({"WARNING"}, "Select a mesh with Surreal Architecture")
                    return {"CANCELLED"}
                apply_research_preset(obj.surreal_arch_props, pid)
                return bpy.ops.surreal_arch.generate()

            return execute

        cls_name = f"SURREAL_ARCH_OT_preset_research_{preset_id}"
        cls = type(
            cls_name,
            (bpy.types.Operator,),
            {
                "bl_idname": op_id,
                "bl_label": spec["label"],
                "bl_description": spec.get("description", ""),
                "bl_options": {"REGISTER", "UNDO"},
                "execute": _make_execute(preset_id),
                "poll": classmethod(
                    lambda c, ctx: ctx.active_object and ctx.active_object.type == "MESH"
                ),
            },
        )
        classes.append(cls)
    return classes
