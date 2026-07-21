"""Blender MCP Server ΓÇö HTTP JSON API on port 9317 for remote agent control."""

from __future__ import annotations

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any

import bpy

_PORT = 9317
_SERVER: HTTPServer | None = None
_THREAD: threading.Thread | None = None


class _MCPHandler(BaseHTTPRequestHandler):
    """Minimal HTTP JSON handler ΓÇö exposes genome/graph/style endpoints."""

    def log_message(self, fmt, *args):
        pass

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def do_GET(self):
        if self.path == "/api/ping":
            return self._send_json({"ok": True, "service": "blender_mcp", "port": _PORT})
        if self.path == "/api/status":
            return self._send_json(_get_status())
        if self.path == "/api/genomes":
            return self._send_json(_list_genomes())
        if self.path == "/api/smoke":
            return self._send_json(_run_smoke())
        self._send_json({"error": "not_found"}, 404)

    def do_POST(self):
        body = self._read_body()
        if self.path == "/api/smoke":
            return self._send_json(_run_smoke(body))
        if self.path == "/api/genomes/apply":
            return self._send_json(_apply_genome(body))
        if self.path == "/api/genomes/randomize":
            return self._send_json(_randomize_dna(body))
        if self.path == "/api/graph/spawn":
            return self._send_json(_spawn_graph(body))
        if self.path == "/api/graph/spawn_step":
            return self._send_json(_spawn_step(body))
        self._send_json({"error": "not_found"}, 404)


def _get_status() -> dict:
    obj = bpy.context.active_object
    if not obj or not hasattr(obj, "surreal_arch_props"):
        return {"ok": True, "active_object": None}
    props = obj.surreal_arch_props
    return {
        "ok": True,
        "active_object": obj.name,
        "arch_type": props.arch_type,
        "genome_id": getattr(props, "style_genome_id", ""),
        "genome_verticality": props.genome_verticality,
        "genome_symmetry": props.genome_symmetry,
        "genome_ornament_density": props.genome_ornament_density,
        "genome_structural_logic": props.genome_structural_logic,
        "genome_organic_growth": props.genome_organic_growth,
        "genome_cosmic_influence": props.genome_cosmic_influence,
    }


def _list_genomes() -> dict:
    import sys
    mod = sys.modules.get("surreal_architecture_gen")
    if mod is None:
        return {"ok": False, "error": "surreal_architecture_gen not loaded", "genomes": []}
    genomes = getattr(mod, "_STYLE_GENOMES", None) or []
    meta = getattr(mod, "_STYLE_GENOME_META", {}) or {}
    groups = getattr(mod, "_STYLE_GENOME_GROUPS", {}) or {}
    items = []
    for gid in genomes:
        m = meta.get(gid, {})
        items.append({
            "id": gid,
            "family": m.get("family", "Unknown"),
            "graph": m.get("graph", ""),
            "transform": m.get("transform", "none"),
        })
    return {"ok": True, "total": len(items), "genomes": items, "groups": groups}


def _apply_genome(body: dict) -> dict:
    gid = body.get("genome_id", "")
    if not gid:
        return {"ok": False, "error": "genome_id required"}
    from .path_util import ensure_deploy_on_path
    ensure_deploy_on_path()
    try:
        from surreal_os import genome as os_genome
    except Exception as exc:
        return {"ok": False, "error": f"surreal_os import: {exc}"}
    obj = bpy.context.active_object
    if not obj or not hasattr(obj, "surreal_arch_props"):
        return {"ok": False, "error": "No active mesh object"}
    props = obj.surreal_arch_props
    import sys
    mod = sys.modules.get("surreal_architecture_gen")
    try:
        os_genome.apply_genome(props, gid, monolith=mod)
        if mod:
            mod._active_style_genome = os_genome.load_genome(gid)
        bpy.context.view_layer.objects.active = obj
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": True, "genome_id": gid}


def _randomize_dna(body: dict) -> dict:
    import random
    obj = bpy.context.active_object
    if not obj or not hasattr(obj, "surreal_arch_props"):
        return {"ok": False, "error": "No active mesh object"}
    props = obj.surreal_arch_props
    axes = [
        "genome_verticality", "genome_symmetry", "genome_ornament_density",
        "genome_structural_logic", "genome_organic_growth", "genome_cosmic_influence",
    ]
    seed = body.get("seed", random.randint(0, 9999))
    rng = random.Random(seed)
    for attr in axes:
        setattr(props, attr, rng.uniform(0.0, 1.0))
    return {"ok": True, "seed": seed, "values": {a: getattr(props, a) for a in axes}}


def _spawn_graph(body: dict) -> dict:
    gid = body.get("genome_id", "")
    if not gid:
        return {"ok": False, "error": "genome_id required"}
    import sys
    mod = sys.modules.get("surreal_architecture_gen")
    if mod is None:
        return {"ok": False, "error": "surreal_architecture_gen not loaded"}
    from .greybox_graph import GRAPH_REGISTRY, spawn_graph, resolve_graph_spacing
    from .path_util import ensure_deploy_on_path
    ensure_deploy_on_path()
    try:
        from surreal_os import genome as os_genome
        genome_data = os_genome.load_genome(gid)
        graph_id = genome_data.get("default_graph", "ZEN_SHRINE_AXIS")
    except Exception as exc:
        return {"ok": False, "error": f"genome load: {exc}"}
    meta = GRAPH_REGISTRY.get(graph_id)
    if not meta:
        return {"ok": False, "error": f"Graph {graph_id} not found"}
    obj = bpy.context.active_object
    if obj and hasattr(obj, "surreal_arch_props"):
        os_genome.apply_genome(obj.surreal_arch_props, gid, monolith=mod)
    spacing = resolve_graph_spacing(bpy.context)
    objs = spawn_graph(bpy.context, mod, meta["spec"], spacing=spacing, graph_id=graph_id)
    return {"ok": True, "graph_id": graph_id, "modules_spawned": len(objs)}


def _spawn_step(body: dict) -> dict:
    atom_id = body.get("atom_id", "")
    gid = body.get("genome_id", "")
    if not atom_id:
        return {"ok": False, "error": "atom_id required"}
    from .path_util import ensure_deploy_on_path
    ensure_deploy_on_path()
    try:
        from surreal_os.atoms import resolve_atom
        a = resolve_atom(atom_id)
        kit = a.get("kit") if a else None
    except Exception:
        kit = None
    if not kit:
        return {"ok": False, "error": f"No kit mapping for atom {atom_id}"}
    col = bpy.context.collection
    mesh = bpy.data.meshes.new(f"Seq_{atom_id}")
    obj = bpy.data.objects.new(f"Seq_{atom_id}", mesh)
    col.objects.link(obj)
    props = obj.surreal_arch_props
    props.arch_type = kit
    if gid:
        try:
            from surreal_os import genome as os_genome
            os_genome.apply_genome(props, gid)
        except Exception:
            pass
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    try:
        bpy.ops.surreal_arch.generate()
    except Exception as exc:
        return {"ok": False, "error": f"generate failed: {exc}"}
    return {"ok": True, "atom_id": atom_id, "kit": kit}


def _run_smoke(body: dict | None = None) -> dict:
    """PGA-callable smoke: register ΓåÆ greybox+kit ΓåÆ snap assert."""
    from .path_util import ensure_deploy_on_path

    ensure_deploy_on_path()
    try:
        from .smoke_harness import run_smoke

        report_path = None
        if isinstance(body, dict) and body.get("report_path"):
            from pathlib import Path

            report_path = Path(body["report_path"])
        return run_smoke(report_path=report_path)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def start_server(port: int = _PORT):
    """Idempotent: re-calling while running returns ok with already_running."""
    global _SERVER, _THREAD, _PORT
    if _SERVER is not None:
        return {"ok": True, "port": _PORT, "already_running": True}
    _PORT = port
    _SERVER = HTTPServer(("0.0.0.0", port), _MCPHandler)
    _THREAD = threading.Thread(target=_SERVER.serve_forever, daemon=True)
    _THREAD.start()
    return {"ok": True, "port": port, "already_running": False}


def stop_server():
    global _SERVER, _THREAD
    if _SERVER:
        _SERVER.shutdown()
        _SERVER.server_close()
        _SERVER = None
        _THREAD = None
    return {"ok": True}
