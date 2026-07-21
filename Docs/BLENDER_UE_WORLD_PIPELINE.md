# Blender 5.1 ΓåÆ UE 5.8 World Pipeline Verification

## Pipeline Overview

The `surreal_architecture_gen.py` addon (v2.131.0) generates procedural architecture and exports via `.world.json` manifest for HISM import into UE.

## Export Path

**Blender Side:**
- `deploy/surreal_architecture_gen.py` ΓåÆ `deploy/surreal_world/export.py`
- Exports: `{WorldRoot}.world.json` with transform matrices

**UE Side:**
- `Content/Python/import_world_manifest.py` (WIA ownership)
- Consumes: JSON ΓåÆ `PCGGraph` with HISM spawner nodes

## Verification Script

Run this in Blender to test the pipeline:

```python
# In Blender 5.1 Python console:
import bpy
import sys
sys.path.append("//deploy")  # Add project path
from surreal_architecture_gen import STRUCTURES, BUILDERS

# Generate a test structure (Relativity Room)
for key in ["RoseWindow_8Petal", "Quatrefoil_Arch", "Spiral_Staircase"]:
    spec = STRUCTURES.get(key)
    if spec:
        result = _bake_structure(spec)
        print(f"{key}: {result}")
```

## Known Integration Points

| Blender Output | UE Material Target |
|----------------|-------------------|
| `SurrealArch_Stone` | `MI_Show_StoneCliff` |
| `SurrealArch_Marble` | `MI_Trimsheet_HeavyWear` |
| `SurrealArch_Gold` | `MI_Zen_Karesansui` |
| `SurrealArch_Stained` | Custom for Baroque/Grotto |

## Coordinate Transformation

- **Blender**: Z-Up, meters, -Y forward
- **UE 5.8**: Left-handed Z-Up, centimeters

Transform in `import_world_manifest.py`:
```python
# Scale: meters ΓåÆ cm
transform.location *= 100.0

# Rotation: Blender ΓåÆ UE conversion
# Use Matrix4x4 transform + handedness correction
```

## Verification Steps (Manual)

1. **Blender Generation Test**
   - Launch Blender 5.1
   - Run addon, generate any structure
   - Check `Saved/Export/{StructureName}.world.json`

2. **UE Import Test**
   - Launch UE 5.8 with `-unattended`
   - Run `py Content/Python/import_world_manifest.py {path_to_json}`
   - Check output in `Saved/Audit/world_import.json`

3. **HISM Verification**
   - Open generated level
   - Verify instances spawned correctly
   - Check ISM count vs expected

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| No JSON output | Check Blender console for errors |
| HISM not spawning | Verify terrain mesh at origin |
| Materials missing | Check ROLE_UE_HINTS mapping |
| Scale wrong | MetersΓåÆcm conversion may have been skipped |

## Status

- **Addon Version**: v2.131.0 (confirmed newer than June 4 backup)
- **Export Path**: `deploy/surreal_world/export.py` exists
- **Import Path**: `Content/Python/import_world_manifest.py` needs verification
- **Ornamental Meshes**: 15 meshes ready, graphs created (`build_pcg_ornamental.py`)
