"""Interactive tutorial system for Melodia Studio addon."""

from __future__ import annotations

import bpy

from .branding import N_PANEL_CATEGORY

TUTORIAL_STEPS = [
    {
        "id": "welcome",
        "title": "Welcome to Melodia Studio",
        "content": "Procedural architecture generator with Style Genomes, Grammar Graphs, Melusina rig control, LiveLink, and UE5 export.",
        "target": "VIEW_3D",
        "icon": "PLUGIN",
    },
    {
        "id": "dna",
        "title": "Style Genome DNA",
        "content": "6 personality sliders control architecture: Verticality, Symmetry, Ornament, Structure, Organic, Cosmic.",
        "target": "surreal_arch_props",
        "icon": "RNA",
    },
    {
        "id": "starlight",
        "title": "Starlight Quick-Swap",
        "content": "Press Shift+G to open the Starlight popup ΓÇö cycle through Nikki-inspired outfits inspired by Melodia's rhythm.",
        "target": "SURREAL_ARCH_PT_genome_carousel",
        "icon": "DECORATE_ANIMATE",
    },
    {
        "id": "graphs",
        "title": "Grammar Graph Presets",
        "content": "Pre-built module chains for rapid level design. Each graph spawns multiple pieces with auto-snap alignment.",
        "target": "SURREAL_ARCH_PT_grammar_graph_browser",
        "icon": "NODETREE",
    },
    {
        "id": "export",
        "title": "Export Pipeline",
        "content": "Bake trim attributes, export snap JSON, capture photos, and send to Unreal via LiveLink or MCP.",
        "target": "SURREAL_ARCH_PT_livelink",
        "icon": "EXPORT",
    },
]

# State stored in WindowManager for persistence across sessions
WM_PROP = "melodia_studio_show_tutorial"
WM_STEP = "melodia_studio_tutorial_step"


def _ensure_props(context):
    wm = context.window_manager
    if WM_PROP not in wm:
        wm[WM_PROP] = True
    if WM_STEP not in wm:
        wm[WM_STEP] = 0


def is_dismissed(context):
    _ensure_props(context)
    return not context.window_manager[WM_PROP]


def current_step(context):
    _ensure_props(context)
    return context.window_manager[WM_STEP]


def reset_tutorial(context):
    _ensure_props(context)
    context.window_manager[WM_PROP] = True
    context.window_manager[WM_STEP] = 0


def next_step(context):
    _ensure_props(context)
    step = min(context.window_manager[WM_STEP] + 1, len(TUTORIAL_STEPS) - 1)
    context.window_manager[WM_STEP] = step


def prev_step(context):
    _ensure_props(context)
    step = max(context.window_manager[WM_STEP] - 1, 0)
    context.window_manager[WM_STEP] = step


def dismiss_tutorial(context):
    _ensure_props(context)
    context.window_manager[WM_PROP] = False


class SURREAL_ARCH_OT_tutorial_next(bpy.types.Operator):
    bl_idname = "surreal_arch.tutorial_next"
    bl_label = "Next"
    bl_options = {"REGISTER"}

    def execute(self, context):
        next_step(context)
        return {"FINISHED"}


class SURREAL_ARCH_OT_tutorial_prev(bpy.types.Operator):
    bl_idname = "surreal_arch.tutorial_prev"
    bl_label = "Previous"
    bl_options = {"REGISTER"}

    def execute(self, context):
        prev_step(context)
        return {"FINISHED"}


class SURREAL_ARCH_OT_tutorial_dismiss(bpy.types.Operator):
    bl_idname = "surreal_arch.tutorial_dismiss"
    bl_label = "Don't show again"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        dismiss_tutorial(context)
        return {"FINISHED"}


class SURREAL_ARCH_OT_tutorial_reset(bpy.types.Operator):
    bl_idname = "surreal_arch.tutorial_reset"
    bl_label = "Reset Tutorial"
    bl_options = {"REGISTER"}

    def execute(self, context):
        reset_tutorial(context)
        return {"FINISHED"}


class SURREAL_ARCH_PT_tutorial_overlay(bpy.types.Panel):
    bl_label = "Tutorial"
    bl_idname = "SURREAL_ARCH_PT_tutorial_overlay"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = N_PANEL_CATEGORY
    bl_parent_id = "SURREAL_ARCH_PT_genome_carousel"
    bl_order = 99
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        if is_dismissed(context):
            return False
        # Visible whenever tutorial is active; parent carousel is always shown
        return True

    def draw(self, context):
        layout = self.layout
        if is_dismissed(context):
            return

        idx = current_step(context)
        step = TUTORIAL_STEPS[idx]

        box = layout.box()
        header = box.row(align=True)
        header.label(text=step["title"], icon=step.get("icon", "INFO"))

        box.label(text=step["content"])

        nav = box.row(align=True)
        if idx > 0:
            nav.operator("surreal_arch.tutorial_prev", text="ΓùÇ", icon="TRIA_LEFT")
        nav.label(text=f"Step {idx + 1}/{len(TUTORIAL_STEPS)}")
        if idx < len(TUTORIAL_STEPS) - 1:
            nav.operator("surreal_arch.tutorial_next", text="Γû╢", icon="TRIA_RIGHT")

        done = box.row(align=True)
        done.operator("surreal_arch.tutorial_dismiss", text="Hide forever", icon="X")
        done.operator("surreal_arch.tutorial_reset", text="Reset", icon="FILE_REFRESH")


def register_tutorial_classes():
    """Return tutorial classes for integration to register once (do not register here)."""
    return [
        SURREAL_ARCH_OT_tutorial_next,
        SURREAL_ARCH_OT_tutorial_prev,
        SURREAL_ARCH_OT_tutorial_dismiss,
        SURREAL_ARCH_OT_tutorial_reset,
        SURREAL_ARCH_PT_tutorial_overlay,
    ]


def unregister_tutorial_classes(_classes):
    for cls in reversed(_classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
