"""Bridge from SurrealArch to the Blender LiveLink addon for Unreal Engine sync."""

from __future__ import annotations

import bpy
import json
import socket
import struct
import os
import sys
import tempfile
import threading
import time

# ΓöÇΓöÇΓöÇ Try to import from installed LiveLink addon ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

_LIVELINK_AVAILABLE = False
_LIVELINK_IMPORT_ERR = None

def _try_import_livelink():
    global _LIVELINK_AVAILABLE, _LIVELINK_IMPORT_ERR
    if _LIVELINK_AVAILABLE:
        return True
    try:
        # Try direct import if addon is installed in Blender
        import live_link_unreal
        _LIVELINK_AVAILABLE = True
        return True
    except ImportError:
        pass
    # Try loading from Tools/BlenderLiveLink path
    try:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # deploy/
        ll_path = os.path.join(base, '..', 'Tools', 'BlenderLiveLink')
        if os.path.isdir(ll_path) and ll_path not in sys.path:
            sys.path.insert(0, ll_path)
            import live_link_unreal
            _LIVELINK_AVAILABLE = True
            return True
    except (ImportError, NameError):
        pass
    _LIVELINK_IMPORT_ERR = "LiveLink addon not installed (Tools/BlenderLiveLink/)"
    return False


# ΓöÇΓöÇΓöÇ Standalone socket helpers (fallback if LiveLink addon not found) ΓöÇ

_LINK_HOST = "127.0.0.1"
_LINK_PORT = 9876
_link_socket = None
_link_connected = False

def _send_message(sock, msg_type, data):
    try:
        message = json.dumps({"type": msg_type, "data": data})
        encoded = message.encode('utf-8')
        sock.sendall(struct.pack('!I', len(encoded)) + encoded)
        return True
    except Exception:
        return False


def ensure_livelink():
    """Ensure LiveLink bridge is available. Returns True if ready."""
    return _try_import_livelink()


def is_connected():
    """Check if LiveLink socket is currently connected."""
    if _LIVELINK_AVAILABLE:
        try:
            from live_link_unreal import _state
            return _state.is_connected
        except Exception:
            pass
    return _link_connected


def get_status():
    """Get connection status string."""
    if _LIVELINK_AVAILABLE:
        try:
            from live_link_unreal import _state
            return _state.status_message
        except Exception:
            pass
    return "Connected (standalone)" if _link_connected else "Disconnected"


def get_port():
    return _LINK_PORT


# ΓöÇΓöÇΓöÇ Import LiveLink functions ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

def start_server():
    """Start LiveLink server. Returns dict with ok/port."""
    if _try_import_livelink():
        try:
            from live_link_unreal import start_server as _ll_start
            return _ll_start()
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
    # Standalone fallback
    global _link_socket, _link_connected
    try:
        _link_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _link_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _link_socket.bind((_LINK_HOST, _LINK_PORT))
        _link_socket.listen(1)
        _link_socket.settimeout(1.0)
        _link_connected = True
        return {"ok": True, "port": _LINK_PORT}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def stop_server():
    """Stop LiveLink server."""
    if _LIVELINK_AVAILABLE:
        try:
            from live_link_unreal import stop_server as _ll_stop
            return _ll_stop()
        except Exception:
            pass
    global _link_socket, _link_connected
    if _link_socket:
        try:
            _link_socket.close()
        except Exception:
            pass
        _link_socket = None
    _link_connected = False


# ΓöÇΓöÇΓöÇ High-level send wrappers ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

def send_to_unreal(msg_type, data):
    """Send a typed JSON message to Unreal Engine over LiveLink socket."""
    if _LIVELINK_AVAILABLE:
        try:
            from live_link_unreal import _state, send_message
            if _state.is_connected and _state.client_socket:
                return send_message(_state.client_socket, msg_type, data)
        except Exception:
            pass
    return False


def send_scene_to_unreal(is_live=False):
    """Send full scene to Unreal via LiveLink."""
    if _try_import_livelink():
        try:
            from live_link_unreal import do_send_scene
            return do_send_scene(is_live=is_live)
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
    return {"ok": False, "error": "LiveLink addon not available"}


def send_selected_to_unreal():
    """Send selected objects to Unreal via LiveLink."""
    if _try_import_livelink():
        try:
            from live_link_unreal import do_send_selected
            return do_send_selected()
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
    return {"ok": False, "error": "LiveLink addon not available"}


# ΓöÇΓöÇΓöÇ Melusina Outfit Swap ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

def send_melusina_outfit(context):
    """Send current genome/style as an outfit packet to Unreal.

    Returns dict with 'ok' and 'outfit_id' on success.
    """
    obj = context.active_object
    if not obj or not hasattr(obj, "surreal_arch_props"):
        return {"ok": False, "error": "No active SurrealArch object"}
    props = obj.surreal_arch_props
    gid = getattr(props, "style_genome_id", "unknown")
    try:
        from surreal_os import genome as os_genome
        g = os_genome.load_genome(gid)
    except Exception as exc:
        return {"ok": False, "error": f"Genome load: {exc}"}

    fam = os_genome.genome_family(g)
    seq = g.get("sacred_sequence", [])
    cosmic = g.get("cosmic_influence", 0.0)
    organic = g.get("organic_growth", 0.0)
    ornament = g.get("ornament_density", 0.0)
    harmony = min(1.0, cosmic * 0.5 + organic * 0.3 + ornament * 0.2)
    graph_id = g.get("default_graph", "")

    outfit = {
        "genome_id": gid,
        "family": fam,
        "axes": {
            "verticality": g.get("verticality", 0.5),
            "symmetry": g.get("symmetry", 0.5),
            "ornament_density": ornament,
            "structural_logic": g.get("structural_logic", 0.5),
            "organic_growth": organic,
            "cosmic_influence": cosmic,
        },
        "harmony": round(harmony, 3),
        "sacred_sequence": seq,
        "default_graph": graph_id,
        "timestamp": time.time(),
    }

    ok = send_to_unreal("MELUSINA_OUTFIT", outfit)
    if not ok:
        return {"ok": False, "error": "Send failed ΓÇö LiveLink not connected"}
    return {"ok": True, "outfit_id": gid, "data": outfit}
