"""UE editor startup: load Blender Live Link client and register menus."""
from __future__ import annotations

import importlib.util
import os
import sys

import pathlib

from envui.menu import register_envui_menus


_SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()
_OWNER = "BSGodFile_LiveLink"


def _py_path_prefix():
    project_python = str(_SCRIPT_DIR)
    return (
        f"import sys; import unreal; p=r'{project_python}'; "
        f"sys.path.insert(0,p) if p not in sys.path else None; "
        f"import livelink_unreal; "
    )


def _menu_command(py_body: str) -> str:
    return (
        _py_path_prefix()
        + "try:\n "
        + py_body
        + "\nexcept Exception as _ll_exc:\n "
        + " unreal.log_error('[LiveLink] Menu action failed: ' + str(_ll_exc))"
    )


def register_livelink_menus():
    """Register LiveLink menus."""
    from envui.menu import register_envui_menus

    register_envui_menus(owner=_OWNER)


if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))


def _load_livelink_module():
    for name in ("livelink_unreal.py", "livelink_unreal.pyc"):
        path = os.path.join(str(_SCRIPT_DIR), name)
        if not os.path.isfile(path):
            continue
        spec = importlib.util.spec_from_file_location("livelink_unreal", path)
        if not spec or not spec.loader:
            continue
        mod = importlib.util.module_from_spec(spec)
        sys.modules["livelink_unreal"] = mod
        spec.loader.exec_module(mod)
        mod.register_menus = register_livelink_menus
        return mod
    unreal.log_error(
        "[LiveLink] Missing Content/Python/livelink_unreal.py or .pyc — "
        "copy from your 3DRedbox purchase, restart UE"
    )
    return None


def _register_gmm() -> None:
    try:
        from gmm.ui.register import register_gmm_menus
        register_gmm_menus()
        unreal.log("[GMM] Grandmaster Melodia Melusina commands registered")
    except ImportError:
        unreal.log_warning("[GMM] gmm package not available — skipping registration")
    except Exception as e:
        unreal.log_warning(f"[GMM] Registration error (non-fatal): {e}")


def _register_osc_bridge() -> None:
    """Start the TD-UE OSC bridge on editor startup."""
    try:
        from osc_server import start_bridge
        if start_bridge(port=8000):
            unreal.log("[TD-Bridge] TouchDesigner OSC bridge started on port 8000")
        else:
            unreal.log_warning("[TD-Bridge] OSC bridge failed to start — OSC plugin may be disabled")
    except ImportError:
        unreal.log_warning("[TD-Bridge] osc_server.py not found — skipping OSC bridge")
    except Exception as e:
        unreal.log_warning(f"[TD-Bridge] OSC bridge error: {e}")


def startup() -> dict:
    """Initialize LiveLink module and register menus."""
    m = _load_livelink_module()
    if not m:
        return {"success": False}
    if hasattr(m, "startup"):
        unreal.log("Initializing LiveLink module...")
        m.startup()
    # Always re-register with sections + flattened entries (pyc menu can render empty)
    register_livelink_menus()
    _register_gmm()
    _register_osc_bridge()
    unreal.log(
        "[LiveLink] v3.1 loaded — LiveLink menu has Start/Stop/Status "
        "(no floating panel; start Blender server first)"
    )
    return {"success": True}


def shutdown() -> dict:
    """Shutdown LiveLink module."""
    m = _load_livelink_module()
    if m and hasattr(m, "shutdown"):
        unreal.log("Shutting down LiveLink module...")
        m.shutdown()
    return {"success": True}

if __name__ == '__main__':
    # Headless startup — run init, then return normally.
    # Do NOT call sys.exit() or raise SystemExit here.
    # When init_unreal.py runs as a UE startup script ANY exit kills the
    # Python executor, which prevents -ExecutePythonScript from running.
    try:
        result = startup()
        if not result.get("success", False):
            unreal.log_warning("[init_unreal] LiveLink startup skipped (no .pyc found)")
    except Exception as e:
        unreal.log_warning(f"[init_unreal] Startup error (non-fatal): {e}")