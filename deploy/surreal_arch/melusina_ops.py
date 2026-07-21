"""Melusina ops: LiveLink connection, outfit swap, Melodia render, MCP bridge."""

from __future__ import annotations

import bpy
import os
import sys
import time

from .path_util import ensure_deploy_on_path
from .livelink_bridge import (
    ensure_livelink, is_connected, get_status, get_port,
    start_server, stop_server,
    send_scene_to_unreal, send_selected_to_unreal, send_melusina_outfit,
    send_to_unreal,
)


# ΓöÇΓöÇΓöÇ LiveLink Connection ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

class SURREAL_ARCH_OT_livelink_start(bpy.types.Operator):
    bl_idname = "surreal_arch.livelink_start"
    bl_label = "Connect LiveLink"
    bl_description = "Start LiveLink server on port 9876 and wait for Unreal connection"
    bl_options = {"REGISTER"}

    def execute(self, context):
        result = start_server()
        if result.get("ok"):
            self.report({"INFO"}, f"LiveLink server on port {result['port']}")
        else:
            self.report({"ERROR"}, f"LiveLink start: {result.get('error', '?')}")
        return {"FINISHED"}


class SURREAL_ARCH_OT_livelink_stop(bpy.types.Operator):
    bl_idname = "surreal_arch.livelink_stop"
    bl_label = "Disconnect LiveLink"
    bl_description = "Stop the LiveLink server"
    bl_options = {"REGISTER"}

    def execute(self, context):
        stop_server()
        self.report({"INFO"}, "LiveLink server stopped")
        return {"FINISHED"}


class SURREAL_ARCH_OT_livelink_send_scene(bpy.types.Operator):
    bl_idname = "surreal_arch.livelink_send_scene"
    bl_label = "Send Scene to Unreal"
    bl_description = "Export and send the full Blender scene to Unreal via LiveLink"
    bl_options = {"REGISTER"}

    def execute(self, context):
        if not is_connected():
            self.report({"ERROR"}, "LiveLink not connected ΓÇö start server first")
            return {"CANCELLED"}
        result = send_scene_to_unreal()
        if isinstance(result, dict) and not result.get("ok", True):
            self.report({"ERROR"}, result.get("error", "Send failed"))
            return {"CANCELLED"}
        self.report({"INFO"}, "Scene sent to Unreal")
        return {"FINISHED"}


class SURREAL_ARCH_OT_livelink_send_selected(bpy.types.Operator):
    bl_idname = "surreal_arch.livelink_send_selected"
    bl_label = "Send Selected to Unreal"
    bl_description = "Export and send selected objects to Unreal via LiveLink"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        if not is_connected():
            self.report({"ERROR"}, "LiveLink not connected ΓÇö start server first")
            return {"CANCELLED"}
        result = send_selected_to_unreal()
        if isinstance(result, dict) and not result.get("ok", True):
            self.report({"ERROR"}, result.get("error", "Send failed"))
            return {"CANCELLED"}
        self.report({"INFO"}, "Selected sent to Unreal")
        return {"FINISHED"}


# ΓöÇΓöÇΓöÇ Melusina Outfit Swap ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

class SURREAL_ARCH_OT_melusina_swap_outfit(bpy.types.Operator):
    bl_idname = "surreal_arch.melusina_swap_outfit"
    bl_label = "Swap Melusina Outfit"
    bl_description = "Send current genome outfit config to Unreal via LiveLink"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and hasattr(obj, "surreal_arch_props")

    def execute(self, context):
        if not is_connected():
            self.report({"ERROR"}, "LiveLink not connected ΓÇö start server first")
            return {"CANCELLED"}
        result = send_melusina_outfit(context)
        if not result.get("ok"):
            self.report({"ERROR"}, result.get("error", "Outfit swap failed"))
            return {"CANCELLED"}
        gid = result.get("outfit_id", "?")
        harmony = result.get("data", {}).get("harmony", 0)
        self.report({"INFO"}, f"Outfit '{gid}' sent to Unreal (harmony {harmony:.2f})")
        return {"FINISHED"}


# ΓöÇΓöÇΓöÇ Melodia Beauty Render ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

class SURREAL_ARCH_OT_melodia_render(bpy.types.Operator):
    bl_idname = "surreal_arch.melodia_render"
    bl_label = "Melodia Beauty Render"
    bl_description = "Apply void/iri world + Nikki rim lights and render a beauty shot"
    bl_options = {"REGISTER"}

    output_path: bpy.props.StringProperty(
        name="Output Path",
        default=os.path.join(os.path.dirname(bpy.data.filepath or "//") if bpy.data.filepath else "//", "renders", "melodia_beauty.png"),
        subtype="FILE_PATH",
    )

    def _setup_world(self, context):
        # HARD STOP 2026-07-14: do not nodes.clear() W_MelodiaStudio ΓÇö that stomped Melusina lookdev.
        self.report(
            {"ERROR"},
            "Refused: world rebuild disabled (MELUSINA_SHADER_AGENT_STOP). Artist owns shading.",
        )
        return False

    def execute(self, context):
        self.report(
            {"ERROR"},
            "Melusina portrait/world operator disabled after repeated shader reverts. Do not use.",
        )
        return {"CANCELLED"}


# ΓöÇΓöÇΓöÇ Bidirectional MCP ΓÇö call UE Monolith from Blender ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

class SURREAL_ARCH_OT_ue_mcp_status(bpy.types.Operator):
    bl_idname = "surreal_arch.ue_mcp_status"
    bl_label = "Check UE MCP Status"
    bl_description = "Query Unreal Engine Monolith MCP server (port 9316) for status"
    bl_options = {"REGISTER"}

    def execute(self, context):
        import urllib.request
        import json as _json
        try:
            req = urllib.request.Request("http://127.0.0.1:9316/api/status", method="GET")
            resp = urllib.request.urlopen(req, timeout=3)
            data = _json.loads(resp.read())
            self.report({"INFO"}, f"UE MCP: {data.get('status', 'ok')}")
        except Exception as exc:
            self.report({"ERROR"}, f"UE MCP unreachable: {exc}")
        return {"FINISHED"}


class SURREAL_ARCH_OT_ue_run_python(bpy.types.Operator):
    bl_idname = "surreal_arch.ue_run_python"
    bl_label = "Run Python on UE"
    bl_description = "Execute a Python snippet on Unreal Engine via Monolith MCP"
    bl_options = {"REGISTER"}
    code: bpy.props.StringProperty(
        name="Python Code", default="print('Hello from Blender!')",
        description="Python code to execute on UE",
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        self.layout.prop(self, "code", text="")

    def execute(self, context):
        import urllib.request
        import json as _json
        payload = _json.dumps({
            "namespace": "editor",
            "action": "run_python",
            "params": {"command": self.code, "mode": "execute_statement"},
        }).encode()
        try:
            req = urllib.request.Request(
                "http://127.0.0.1:9316", data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            resp = urllib.request.urlopen(req, timeout=5)
            result = _json.loads(resp.read())
            self.report({"INFO"}, f"UE result: {str(result)[:120]}")
        except Exception as exc:
            self.report({"ERROR"}, f"UE MCP call failed: {exc}")
        return {"FINISHED"}
