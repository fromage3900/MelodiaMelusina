"""Missing subgraph builders ΓÇö SG_Triplanar, SG_Flow_Generator, SG_Spherical_Projection.

Part of Phase 2 of SURREAL_PBR_REDESIGN.md.
Generates .ptex files in MaterialMaker/Subgraphs/ via JSON manipulation (no MM required).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

SUBS_DIR = Path(r"G:\EnvironmentPortfolio\BS_GodFile\Tools\MaterialMaker\Subgraphs")


def _write_ptex(name: str, nodes: list[dict], connections: list[dict]) -> Path:
    """Write a minimal .ptex graph file via JSON."""
    SUBS_DIR.mkdir(parents=True, exist_ok=True)
    path = SUBS_DIR / name
    graph = {
        "connections": connections,
        "nodes": nodes,
        "parameters": [],
    }
    path.write_text(json.dumps(graph, indent=2))
    return path


def build_sg_triplanar() -> Path:
    """SG_Triplanar: World-space triplanar projection with blend control.

    Inputs:  UV, WorldNormal, BlendSharpness
    Outputs: TriplanarUV, TriplanarMask
    """
    nodes = [
        {
            "name": "comment_lane_input",
            "type": "comment_lane",
            "params": {"label": "Input"}
        },
        {
            "name": "comment_lane_proj",
            "type": "comment_lane",
            "params": {"label": "Triplanar Projection"}
        },
        {
            "name": "comment_lane_output",
            "type": "comment_lane",
            "params": {"label": "Output"}
        },
        {
            "name": "input_uv",
            "type": "remote",
            "params": {"name": "UV", "type": "vec2", "default": [0, 0]}
        },
        {
            "name": "input_normal",
            "type": "remote",
            "params": {"name": "WorldNormal", "type": "vec3", "default": [0, 0, 1]}
        },
        {
            "name": "input_blend",
            "type": "remote",
            "params": {"name": "BlendSharpness", "type": "float", "default": 4.0, "min": 0.1, "max": 16.0}
        },
        {
            "name": "blend_node",
            "type": "blend",
            "params": {}
        },
        {
            "name": "output_uv",
            "type": "output",
            "params": {"name": "TriplanarUV", "type": "vec2"}
        },
        {
            "name": "output_mask",
            "type": "output",
            "params": {"name": "TriplanarMask", "type": "float"}
        },
    ]
    connections = [
        {"from": "input_uv", "from_port": 0, "to": "blend_node", "to_port": 0},
        {"from": "input_normal", "from_port": 0, "to": "blend_node", "to_port": 1},
        {"from": "input_blend", "from_port": 0, "to": "blend_node", "to_port": 2},
        {"from": "blend_node", "from_port": 0, "to": "output_uv", "to_port": 0},
        {"from": "blend_node", "from_port": 1, "to": "output_mask", "to_port": 0},
    ]
    return _write_ptex("SG_Triplanar.ptex", nodes, connections)


def build_sg_flow_generator() -> Path:
    """SG_Flow_Generator: Directional flow map generation.

    Inputs:  UV, FlowDirection, FlowSpeed, FlowIntensity
    Outputs: FlowUV, FlowMask
    """
    nodes = [
        {
            "name": "comment_lane_input",
            "type": "comment_lane",
            "params": {"label": "Input"}
        },
        {
            "name": "comment_lane_flow",
            "type": "comment_lane",
            "params": {"label": "Flow Generation"}
        },
        {
            "name": "input_uv",
            "type": "remote",
            "params": {"name": "UV", "type": "vec2", "default": [0, 0]}
        },
        {
            "name": "input_dir",
            "type": "remote",
            "params": {"name": "FlowDirection", "type": "vec2", "default": [1, 0]}
        },
        {
            "name": "input_speed",
            "type": "remote",
            "params": {"name": "FlowSpeed", "type": "float", "default": 1.0, "min": 0.0, "max": 10.0}
        },
        {
            "name": "input_intensity",
            "type": "remote",
            "params": {"name": "FlowIntensity", "type": "float", "default": 0.5, "min": 0.0, "max": 1.0}
        },
        {
            "name": "flow_gen",
            "type": "flow",
            "params": {}
        },
        {
            "name": "output_uv",
            "type": "output",
            "params": {"name": "FlowUV", "type": "vec2"}
        },
        {
            "name": "output_mask",
            "type": "output",
            "params": {"name": "FlowMask", "type": "float"}
        },
    ]
    connections = [
        {"from": "input_uv", "from_port": 0, "to": "flow_gen", "to_port": 0},
        {"from": "input_dir", "from_port": 0, "to": "flow_gen", "to_port": 1},
        {"from": "input_speed", "from_port": 0, "to": "flow_gen", "to_port": 2},
        {"from": "input_intensity", "from_port": 0, "to": "flow_gen", "to_port": 3},
        {"from": "flow_gen", "from_port": 0, "to": "output_uv", "to_port": 0},
        {"from": "flow_gen", "from_port": 1, "to": "output_mask", "to_port": 0},
    ]
    return _write_ptex("SG_Flow_Generator.ptex", nodes, connections)


def build_sg_spherical_projection() -> Path:
    """SG_Spherical_Projection: Equirectangular/spherical UV projection.

    Inputs:  WorldPos, SphereCenter, SphereRadius
    Outputs: SphericalUV, SphericalMask
    """
    nodes = [
        {
            "name": "comment_lane_input",
            "type": "comment_lane",
            "params": {"label": "Input"}
        },
        {
            "name": "comment_lane_sphere",
            "type": "comment_lane",
            "params": {"label": "Spherical Projection"}
        },
        {
            "name": "input_pos",
            "type": "remote",
            "params": {"name": "WorldPos", "type": "vec3", "default": [0, 0, 0]}
        },
        {
            "name": "input_center",
            "type": "remote",
            "params": {"name": "SphereCenter", "type": "vec3", "default": [0, 0, 0]}
        },
        {
            "name": "input_radius",
            "type": "remote",
            "params": {"name": "SphereRadius", "type": "float", "default": 100.0, "min": 1.0, "max": 10000.0}
        },
        {
            "name": "sphere_proj",
            "type": "spherical",
            "params": {}
        },
        {
            "name": "output_uv",
            "type": "output",
            "params": {"name": "SphericalUV", "type": "vec2"}
        },
        {
            "name": "output_mask",
            "type": "output",
            "params": {"name": "SphericalMask", "type": "float"}
        },
    ]
    connections = [
        {"from": "input_pos", "from_port": 0, "to": "sphere_proj", "to_port": 0},
        {"from": "input_center", "from_port": 0, "to": "sphere_proj", "to_port": 1},
        {"from": "input_radius", "from_port": 0, "to": "sphere_proj", "to_port": 2},
        {"from": "sphere_proj", "from_port": 0, "to": "output_uv", "to_port": 0},
        {"from": "sphere_proj", "from_port": 1, "to": "output_mask", "to_port": 0},
    ]
    return _write_ptex("SG_Spherical_Projection.ptex", nodes, connections)


def build_all_subgraphs():
    """Build all 3 missing subgraphs."""
    results = []
    for builder, name in [
        (build_sg_triplanar, "SG_Triplanar.ptex"),
        (build_sg_flow_generator, "SG_Flow_Generator.ptex"),
        (build_sg_spherical_projection, "SG_Spherical_Projection.ptex"),
    ]:
        path = builder()
        results.append(str(path))
        print(f"  Γ£ô {path}")
    return results


if __name__ == "__main__":
    build_all_subgraphs()
