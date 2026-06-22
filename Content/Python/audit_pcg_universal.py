"""Audit universal PCG graphs and smoke-test greybox preset.

  python Content/Python/audit_pcg_universal.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pcg_portfolio_standards as std

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT = PROJECT_ROOT / "Saved" / "Audit" / "pcg_universal_audit.json"
UE_CMD = Path(r"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe")
UPROJECT = PROJECT_ROOT / "BS_GodFile.uproject"

EXPECTED_GRAPHS = (
    std.GRAPH_FOLIAGE,
    std.GRAPH_ROCK,
    std.GRAPH_EXCLUSION,
    std.GRAPH_WALL,
    std.GRAPH_GREYBOX_MINIMAL,
    std.GRAPH_GREYBOX_STANDARD,
)


def _audit_in_ue() -> dict:
    import unreal

    graphs = {}
    for path in EXPECTED_GRAPHS:
        exists = unreal.EditorAssetLibrary.does_asset_exist(path)
        node_count = 0
        if exists:
            g = unreal.load_asset(path)
            if g and hasattr(g, "get_nodes"):
                node_count = len(list(g.get_nodes() or []))
        graphs[path] = {"exists": exists, "node_count": node_count}

    build_path = PROJECT_ROOT / "Saved" / "Audit" / "pcg_universal_build.json"
    build = {}
    if build_path.exists():
        try:
            build = json.loads(build_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "graphs": graphs,
        "all_exist": all(g["exists"] for g in graphs.values()),
        "build_passed": build.get("passed"),
        "clean": all(g["exists"] for g in graphs.values()) and build.get("passed", False),
    }


def main() -> int:
    try:
        import unreal  # noqa: F401
        report = _audit_in_ue()
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"PCG_UNIVERSAL_AUDIT clean={report['clean']} -> {REPORT}")
        return 0
    except ImportError:
        if not UE_CMD.exists():
            return 1
        cmd = [
            str(UE_CMD), str(UPROJECT),
            f"-ExecutePythonScript={(PROJECT_ROOT / 'Content/Python/audit_pcg_universal.py').as_posix()}",
            "-stdout", "-unattended", "-nullrhi", "-DisablePlugins=Monolith",
        ]
        return subprocess.run(cmd, cwd=str(PROJECT_ROOT)).returncode


if __name__ == "__main__":
    raise SystemExit(main())
