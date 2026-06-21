"""Wire overhaul package into surreal_architecture_gen monolith."""

from __future__ import annotations

import bpy
import json
import os
import sys

_M = None
_EXTRA_CLASSES = []
_PATCHED = False


def _ensure_path():
    pkg = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(pkg)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    greybox_parent = os.path.dirname(parent)
    if greybox_parent not in sys.path:
        sys.path.insert(0, greybox_parent)


def _wire_trim_box_wrapper(monolith):
    """Re-apply after surreal_greybox.attach_all resets _gb_box each register."""
    from .trim_color_bake import resolve_trim_zone, tag_face_trim_attrs, tag_trim_geometry

    inner = getattr(monolith, "_gb_box_inner", None)
    current = monolith._gb_box
    if inner is None or current is inner:
        inner = current
        monolith._gb_box_inner = inner

    def _gb_box_trim_zones(tree, size, loc_xyz, x, y, label="level"):
        geom = inner(tree, size, loc_xyz, x, y, label)
        if geom is None:
            return None
        props = getattr(getattr(bpy.context, "active_object", None), "surreal_arch_props", None)
        zone = resolve_trim_zone(monolith, label, props)
        if zone is not None:
            return tag_trim_geometry(monolith, tree, geom, x, y, trim_value=zone)
        return tag_face_trim_attrs(monolith, tree, geom, x, y, zone_value=0.0, trim_flag=0.0)

    monolith._gb_box = _gb_box_trim_zones


def patch_monolith(monolith):
    global _M, _PATCHED
    if _M is not monolith:
        _PATCHED = False
    _M = monolith
    first_patch = not _PATCHED
    _PATCHED = True

    _ensure_path()
    try:
        import surreal_greybox
        surreal_greybox.attach_all(monolith)
    except Exception as _gb_err:
        print(f"[Surreal Architecture] surreal_greybox attach skipped: {_gb_err}")

    from . import gothic_kit, greybox_offset, romanesque_kit, brutalist_kit, venetian_kit, scifi_kit, zen_kit
    from .kit_registration import register_kit

    if first_patch:
        monolith.build_gothic_portal = lambda t, p, bx=-1400: gothic_kit.build_gothic_portal(t, monolith, p, bx)
        monolith.build_gothic_bay = lambda t, p, bx=-1400: gothic_kit.build_gothic_bay(t, monolith, p, bx)
        monolith.build_gothic_buttress_kit = lambda t, p, bx=-1400: gothic_kit.build_gothic_buttress(t, monolith, p, bx)
        monolith.build_gothic_tracery_panel = lambda t, p, bx=-1400: gothic_kit.build_gothic_tracery_panel(t, monolith, p, bx)

        def _build_greybox_room_with_reveals(tree, props, base_x=-1400):
            W = getattr(props, "gb_width", 8.0)
            D = getattr(props, "gb_depth", 6.0)
            H = getattr(props, "gb_height", 3.5)
            t = getattr(props, "gb_wall_thick", 0.3)
            parts = monolith._gb_rect_room_shell(tree, props, W, D, H, t, base_x, 0)
            from .greybox_trim import gb_rect_room_window_reveals
            parts.extend(gb_rect_room_window_reveals(tree, monolith, props, base_x, W, D, H, t))
            return monolith._gb_join(tree, parts, base_x + 1600, 0)

        monolith.build_greybox_room = _build_greybox_room_with_reveals

        orig_picker_draw = monolith.SURREAL_ARCH_PT_arch_picker.draw

        def _picker_draw(self, context):
            from .ui import draw_arch_picker_filtered
            draw_arch_picker_filtered(self.layout, context, monolith, compact=False)

        monolith.SURREAL_ARCH_PT_arch_picker.draw = _picker_draw
        monolith.SURREAL_ARCH_PT_arch_picker.bl_order = 1
        monolith.SURREAL_ARCH_PT_arch_picker.bl_label = "Architecture Picker"

        def _level_draw(self, context):
            from .ui import draw_level_design
            draw_level_design(self.layout, context, monolith)

        monolith.SURREAL_ARCH_PT_level_design.draw = _level_draw

        _orig_generate = monolith.SURREAL_ARCH_OT_generate.execute

        def _generate_with_trim_reset(self, context):
            from .trim_color_bake import reset_trim_zones
            reset_trim_zones(monolith)
            return _orig_generate(self, context)

        monolith.SURREAL_ARCH_OT_generate.execute = _generate_with_trim_reset

    _wire_trim_box_wrapper(monolith)

    monolith.build_greybox_corridor_offset = lambda t, p, bx=-1400: greybox_offset.build_greybox_corridor_offset(
        t, monolith, p, bx
    )
    monolith.build_romanesque_arcade_bay = lambda t, p, bx=-1400: romanesque_kit.build_romanesque_arcade_bay(
        t, monolith, p, bx
    )
    monolith.build_brutalist_panel_wall = lambda t, p, bx=-1400: brutalist_kit.build_brutalist_panel_wall(
        t, monolith, p, bx
    )
    monolith.build_venetian_loggia_bay = lambda t, p, bx=-1400: venetian_kit.build_venetian_loggia_bay(
        t, monolith, p, bx
    )

    register_kit(
        monolith,
        "GB_SCIFI_PRESSURE_DOOR",
        scifi_kit.build_scifi_pressure_door,
        snap_fn=scifi_kit.compute_scifi_pressure_door_snaps,
        builder_attr="build_scifi_pressure_door",
        material_key="METAL",
    )
    register_kit(
        monolith,
        "GB_ROMANESQUE_APSE",
        romanesque_kit.build_romanesque_apse,
        snap_fn=lambda M, props, t: romanesque_kit.compute_romanesque_snap_points(M, props, t),
        builder_attr="build_romanesque_apse",
        material_key="STONE",
    )
    register_kit(
        monolith,
        "GB_ZEN_ROJI_STEP",
        zen_kit.build_zen_roji_step,
        snap_fn=zen_kit.compute_zen_kit_snaps,
        builder_attr="build_zen_roji_step",
        material_key="STONE",
    )
    register_kit(
        monolith,
        "GB_ZEN_TORII_GATE",
        zen_kit.build_zen_torii_gate,
        snap_fn=zen_kit.compute_zen_kit_snaps,
        builder_attr="build_zen_torii_gate",
        material_key="STONE",
    )
    register_kit(
        monolith,
        "GB_ZEN_TSUKUBAI",
        zen_kit.build_zen_tsukubai,
        snap_fn=zen_kit.compute_zen_kit_snaps,
        builder_attr="build_zen_tsukubai",
        material_key="STONE",
    )

    if not hasattr(monolith, "_gb_compute_snap_points_orig"):
        monolith._gb_compute_snap_points_orig = monolith._gb_compute_snap_points

    def _compute_snaps_extended(props):
        t = props.arch_type
        kit_snaps = getattr(monolith, "_KIT_SNAP_FN", {})
        if t in kit_snaps:
            fn = kit_snaps[t]
            try:
                return fn(monolith, props, t)
            except TypeError:
                return fn(monolith, props)
        if t.startswith("GB_GOTHIC_"):
            return gothic_kit.compute_gothic_snap_points(monolith, props, t)
        if t == "GB_CORRIDOR_OFFSET":
            return greybox_offset.compute_corridor_offset_snap_points(monolith, props)
        if t == "GB_ROMANESQUE_ARCADE":
            return romanesque_kit.compute_romanesque_snap_points(monolith, props, t)
        if t == "GB_ROMANESQUE_APSE":
            return romanesque_kit.compute_romanesque_snap_points(monolith, props, t)
        if t == "GB_BRUTALIST_PANEL_WALL":
            return brutalist_kit.compute_brutalist_snap_points(monolith, props)
        if t == "GB_VENETIAN_LOGGIA":
            return venetian_kit.compute_venetian_loggia_snap_points(monolith, props)
        if t.startswith("GB_ZEN_") or (t.startswith("ZEN_") and t not in ("ZEN_MOSS", "ZEN_RIPPLE", "ZEN_SAND", "ZEN_BAMBOO", "ZEN_PETALS", "ZEN_ORBIT", "ZEN_SMOKE", "ZEN_POND", "ZEN_TERRACE", "ZEN_GINKGO", "ZEN_RUNES", "ZEN_BONSAI")):
            return zen_kit.compute_zen_snaps(monolith, props, t)
        return monolith._gb_compute_snap_points_orig(props)

    monolith._gb_compute_snap_points = _compute_snaps_extended

    if not hasattr(monolith, "_gb_write_snap_points_orig"):
        monolith._gb_write_snap_points_orig = monolith._gb_write_snap_points

    def _write_snaps_extended(obj, props):
        monolith._gb_write_snap_points_orig(obj, props)
        from .snap_export import attach_trim_metadata
        attach_trim_metadata(obj, props, monolith)

    monolith._gb_write_snap_points = _write_snaps_extended

    from .catalog_dispatch import register_dispatch_entry, sync_catalog_dispatch

    register_dispatch_entry(
        monolith, "GB_CORRIDOR_OFFSET", "build_greybox_corridor_offset",
        snap_fn=greybox_offset.compute_corridor_offset_snap_points,
        material_key="STONE",
    )
    register_dispatch_entry(
        monolith, "GB_ROMANESQUE_ARCADE", "build_romanesque_arcade_bay",
        snap_fn=lambda M, props, t: romanesque_kit.compute_romanesque_snap_points(M, props, t),
        material_key="STONE",
    )
    register_dispatch_entry(
        monolith, "GB_BRUTALIST_PANEL_WALL", "build_brutalist_panel_wall",
        snap_fn=brutalist_kit.compute_brutalist_snap_points,
        material_key="STONE",
    )
    register_dispatch_entry(
        monolith, "GB_VENETIAN_LOGGIA", "build_venetian_loggia_bay",
        snap_fn=venetian_kit.compute_venetian_loggia_snap_points,
        material_key="MARBLE",
    )
    register_dispatch_entry(monolith, "GB_GOTHIC_PORTAL", "build_gothic_portal")
    register_dispatch_entry(monolith, "GB_GOTHIC_BAY", "build_gothic_bay")
    register_dispatch_entry(monolith, "GB_GOTHIC_BUTTRESS", "build_gothic_buttress_kit")
    register_dispatch_entry(monolith, "GB_GOTHIC_TRACERY_PANEL", "build_gothic_tracery_panel")

    sync_catalog_dispatch(monolith)

    try:
        from surreal_world.patch import patch_world

        patch_world(monolith)
    except Exception as _world_err:
        print(f"[Surreal Architecture] surreal_world patch skipped: {_world_err}")


def register_overhaul(monolith):
    _ensure_path()
    patch_monolith(monolith)
    from .ui import make_view3d_panels
    from .greybox_graph import register_graph_operators
    from .greybox_overlay import enable_overlay
    from .research_presets import register_research_preset_operators
    from .asset_browser import register_asset_ops
    from .catalog_enum import register_catalog_enum_ops
    from .workflow_polls import patch_workflow_polls

    patch_workflow_polls(monolith)

    global _EXTRA_CLASSES
    _EXTRA_CLASSES = list(make_view3d_panels(monolith))
    _EXTRA_CLASSES.extend(list(register_graph_operators(monolith)))
    _EXTRA_CLASSES.extend(register_research_preset_operators(monolith))
    _EXTRA_CLASSES.extend(register_asset_ops(monolith))
    _EXTRA_CLASSES.extend(register_catalog_enum_ops(monolith))

    try:
        from surreal_world.patch import register_world_operators

        _EXTRA_CLASSES.extend(register_world_operators(monolith))
    except Exception as _wo_err:
        print(f"[Surreal Architecture] world operators skipped: {_wo_err}")

    class SURREAL_ARCH_OT_export_snap_json(bpy.types.Operator):
        bl_idname = "surreal_arch.export_snap_json"
        bl_label = "Export Snap JSON"
        bl_options = {"REGISTER"}

        filepath: bpy.props.StringProperty(subtype="FILE_PATH")

        def execute(self, context):
            obj = context.active_object
            if not obj or "surreal_snap_points" not in obj:
                self.report({"ERROR"}, "No snap metadata on active object")
                return {"CANCELLED"}
            path = self.filepath or bpy.path.abspath("//snap_points.json")
            from .snap_export import build_ue_export_payload
            payload = build_ue_export_payload(obj, monolith)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            self.report({"INFO"}, f"Wrote UE snap JSON ({len(payload.get('trim_groups', []))} trim groups)")
            return {"FINISHED"}

        def invoke(self, context, event):
            context.window_manager.fileselect_add(self)
            return {"RUNNING_MODAL"}

    class SURREAL_ARCH_OT_toggle_snap_overlay(bpy.types.Operator):
        bl_idname = "surreal_arch.toggle_snap_overlay"
        bl_label = "Toggle Snap Overlay"
        bl_options = {"REGISTER"}

        def execute(self, context):
            from .greybox_overlay import _handler, disable_overlay, enable_overlay
            if _handler is None:
                enable_overlay()
                self.report({"INFO"}, "Snap overlay ON")
            else:
                disable_overlay()
                self.report({"INFO"}, "Snap overlay OFF")
            return {"FINISHED"}

    class SURREAL_ARCH_OT_bake_trim_attributes(bpy.types.Operator):
        bl_idname = "surreal_arch.bake_trim_attributes"
        bl_label = "Bake Trim Attributes"
        bl_options = {"REGISTER", "UNDO"}

        @classmethod
        def poll(cls, context):
            obj = context.active_object
            return obj and obj.type == "MESH" and hasattr(obj, "surreal_arch_props")

        def execute(self, context):
            obj = context.active_object
            from .trim_bake import apply_trim_bake
            if apply_trim_bake(obj, obj.surreal_arch_props, monolith):
                self.report({"INFO"}, "Trim vertex colors + face attribute written")
                return {"FINISHED"}
            self.report({"WARNING"}, "No trim groups for active arch type")
            return {"CANCELLED"}

    _EXTRA_CLASSES.extend([
        SURREAL_ARCH_OT_export_snap_json,
        SURREAL_ARCH_OT_toggle_snap_overlay,
        SURREAL_ARCH_OT_bake_trim_attributes,
    ])
    for cls in _EXTRA_CLASSES:
        try:
            bpy.utils.register_class(cls)
        except RuntimeError:
            # Blender may retain registered classes across hot reload/disable-enable cycles.
            # Treat as idempotent for nap-loop stability.
            pass
    enable_overlay()


def unregister_overhaul():
    from .greybox_overlay import disable_overlay
    disable_overlay()
    global _EXTRA_CLASSES
    for cls in reversed(_EXTRA_CLASSES):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
    _EXTRA_CLASSES = []
