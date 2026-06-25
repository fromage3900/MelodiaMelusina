"""Load L_SakuraPath and run portfolio metadata + render exporters (needs RHI).

  UnrealEditor-Cmd.exe BS_GodFile.uproject ^
    -ExecutePythonScript="G:/EnvironmentPortfolio/BS_GodFile/Content/Python/run_portfolio_capture.py"
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT = PROJECT_ROOT / "Saved" / "Audit" / "portfolio_capture.json"
LEVEL = "/Game/EnvSandbox/Levels/L_SakuraPath"
UE_CMD = Path(r"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe")
UPROJECT = PROJECT_ROOT / "BS_GodFile.uproject"


def run_capture() -> dict:
    import unreal

    time.sleep(15)
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if les and unreal.EditorAssetLibrary.does_asset_exist(f"{LEVEL}.L_SakuraPath"):
        les.load_level(LEVEL)
        time.sleep(3)

    import portfolio_output_layout as layout
    import render_exporter as renders
    import scene_metadata_exporter as metadata

    layout.ensure_portfolio_layout()
    meta_path = metadata.write_scene_metadata()
    render_result = renders.export_renders()
    layout.organize_portfolio_outputs()

    return {
        "ok": True,
        "level": LEVEL,
        "metadata": str(meta_path),
        "renders": render_result,
    }


def main() -> int:
    try:
        import unreal  # noqa: F401
        result = run_capture()
        report = {"timestamp": datetime.now(timezone.utc).isoformat(), **result}
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"PORTFOLIO_CAPTURE ok -> {REPORT}")
        return 0
    except ImportError:
        if not UE_CMD.exists():
            print(f"ERROR: {UE_CMD}")
            return 1
        log = PROJECT_ROOT / "Saved" / "Logs" / "portfolio_capture.log"
        cmd = [
            str(UE_CMD),
            str(UPROJECT),
            f"-ExecutePythonScript={(PROJECT_ROOT / 'Content/Python/run_portfolio_capture.py').as_posix()}",
            "-stdout",
            "-unattended",
            "-nosplash",
            "-DisablePlugins=Monolith",
            f"-log={log}",
        ]
        print(f"Launching portfolio capture (RHI) -> {log}")
        return subprocess.run(cmd, cwd=str(PROJECT_ROOT)).returncode


if __name__ == "__main__":
    raise SystemExit(main())
