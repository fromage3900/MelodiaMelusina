# Material Library Improvement - Implementation Tasks

## Task Overview

This document outlines the implementation tasks for the Material Library Improvement project. Tasks are organized by priority and dependency order.

## Task Dependency Graph

```
Phase 1 (Critical)          Phase 2 (High)           Phase 3 (Medium)
┌─────────────────┐         ┌─────────────────┐      ┌─────────────────┐
│ T1: Layer Fix   │────────►│ T3: Water Expand│      │ T5: Cleanup     │
└────────┬────────┘         └────────┬────────┘      └────────┬────────┘
         │                           │                        │
         ▼                           ▼                        ▼
┌─────────────────┐         ┌─────────────────┐      ┌─────────────────┐
│ T2: Nikki Fix   │────────►│ T4: Params Std  │      │ T6: BSDF Valid  │
└─────────────────┘         └─────────────────┘      └─────────────────┘
```

---

## Phase 1: Critical Fixes

### Task 1: Fix Universal Master Layering System - Implementation Guide

## Overview
Fix the layering system so LayerA, LayerB, and LayerC can be enabled simultaneously without canceling each other out. The current implementation uses dependent blending (A→B→C) instead of independent weighted blending.

## Implementation Steps

### Step 1.1: Add Layer Activation Switches

**Location:** `Content/Python/setup_master_universal.py`, after `layer_c_metallic_blend` definition (~line 380)

```python
# ---- Layer Activation Switches (independent per layer) ----
layer_a_active = static_switch(m, "bLayerA_Active", "Layers", -2100, 3800, default=True)
layer_b_active = static_switch(m, "bLayerB_Active", "Layers", -2100, 3900, default=False)
layer_c_active = static_switch(m, "bLayerC_Active", "Layers", -2100, 4000, default=False)
```

**Purpose:** Create independent switches that allow each layer to be active without affecting others.

---

### Step 1.2: Add Helper Functions

**Location:** `Content/Python/setup_master_universal.py`, after `sat1()` function (~line 350)

```python
def add3(m, a, b, c, tag: str, x: int, y: int):
    """Add three values together via nested Add nodes."""
    ab = lib.create_expression(m, unreal.MaterialExpressionAdd, x, y)
    wire(f"{tag}_abA", a, ab, "A")
    wire(f"{tag}_abB", b, ab, "B")
    abc = lib.create_expression(m, unreal.MaterialExpressionAdd, x + 160, y)
    wire(f"{tag}_abcA", ab, abc, "A")
    wire(f"{tag}_abcB", c, abc, "B")
    return abc


def div2(m, a, b, tag: str, x: int, y: int):
    """Divide a by b."""
    e = lib.create_expression(m, unreal.MaterialExpressionDivide, x, y)
    wire(f"{tag}_A", a, e, "A")
    wire(f"{tag}_B", b, e, "B")
    return e
```

**Purpose:** Helper functions for weighted blending calculations.

---

### Step 1.3: Implement Weighted Layer Blending

**Location:** `Content/Python/setup_master_universal.py`, replace the layer blending section (~lines 830-920)

**Replace the existing layer blending logic with weighted blend approach:**

```python
# Layer activation weights for weighted blend
# Each layer contributes based on: active switch * weight
eps = lib.create_expression(m, unreal.MaterialExpressionConstant, -600, 1200)
eps.set_editor_property("r", 0.001)

active_count = lib.create_expression(m, unreal.MaterialExpressionAdd, -600, 1200)
wire("acA", layer_a_active, active_count, "A")
wire("acB", layer_b_active, active_count, "B")
active_count2 = lib.create_expression(m, unreal.MaterialExpressionAdd, -440, 1200)
wire("ac2A", active_count, active_count2, "A")
wire("ac2B", layer_c_active, active_count2, "B")
active_safe = lib.create_expression(m, unreal.MaterialExpressionAdd, -280, 1200)
wire("safeA", active_count2, active_safe, "A")
wire("safeB", eps, active_safe, "B")  # Add epsilon to avoid division by zero

# Layer A weighted output (always active by default)
layer_a_alpha = lib.create_expression(m, unreal.MaterialExpressionMultiply, -800, 1200)
wire("laA_active", layer_a_active, layer_a_alpha, "A")
wire("laA_const", const1(m, -1000, 1200, 1.0), layer_a_alpha, "B")
weight_a = div2(m, layer_a_alpha, active_safe, -280, 1200)

# Layer B weighted output
color_alpha_ab = mul2(m, blend_alpha_ab, layer_color_blend, "layAB_color_alpha", 720, 520)
# ... (existing alpha calculations for layer B)
layer_b_alpha = lib.create_expression(m, unreal.MaterialExpressionMultiply, -800, 1320)
wire("lbB_active", layer_b_active, layer_b_alpha, "A")
wire("lbB_alpha", blend_alpha_ab, layer_b_alpha, "B")
weight_b = div2(m, layer_b_alpha, active_safe, -280, 1320)

# Layer C weighted output
# ... (existing alpha calculations for layer C)
layer_c_alpha = lib.create_expression(m, unreal.MaterialExpressionMultiply, -800, 1440)
wire("lcC_active", layer_c_active, layer_c_alpha, "A")
wire("lcC_alpha", blend_alpha_c, layer_c_alpha, "B")
weight_c = div2(m, layer_c_alpha, active_safe, -280, 1440)

# Apply texture weights
alb_a_w = mul2(m, alb_a, layer_a_weight, "alb_a_w", -120, 1200)
alb_b_w = mul2(m, alb_b_s, layer_b_weight, "alb_b_w", -120, 1320)
alb_c_w = mul2(m, alb_c_s, layer_c_weight, "alb_c_w", -120, 1440)

# Weighted average: sum(weight * value)
alb_blend = add3(m,
    mul2(m, alb_a_w, weight_a, "alb_wa", 40, 1200),
    mul2(m, alb_b_w, weight_b, "alb_wb", 40, 1320),
    mul2(m, alb_c_w, weight_c, "alb_wc", 40, 1440),
    200, 1200
)
# Repeat for nrm_blend, orm_blend, hgt_blend, rough_blend, metal_blend
```

**Purpose:** Implement weighted blending where each active layer contributes proportionally to the final output.

---

### Step 1.4: Update tex_eff Calculation

**Location:** `Content/Python/setup_master_universal.py`, after weighted blend section

```python
# Weighted texture blending for hybrid
active_count_for_tex = div2(m, add3(m, layer_a_active, layer_b_active, layer_c_active, 40, 1200), 
                            const1(m, -200, 1200, 3.0), -40, 1200)

tex_a_eff = mul2(m, layer_a_weight, layer_a_active, "tex_a_eff", -200, 120)
tex_b_eff = mul2(m, layer_b_weight, layer_b_active, "tex_b_eff", -200, 240)
tex_c_eff = mul2(m, layer_c_weight, layer_c_active, "tex_c_eff", -200, 360)

tex_eff = add3(m, tex_a_eff, tex_b_eff, tex_c_eff, "tex_eff", -40, 180)
```

**Purpose:** Calculate texture influence based on active layers and their weights.

---

## Testing Checklist

- [ ] Run `python Content/Python/setup_master_universal.py --force`
- [ ] Verify all 27 existing instances compile without errors
- [ ] Test layer combinations in Material Editor:
  - [ ] LayerA only (bLayerA_Active=True, others=False)
  - [ ] LayerB only (bLayerB_Active=True, others=False)
  - [ ] LayerA + LayerB (both True)
  - [ ] LayerA + LayerB + LayerC (all True)
- [ ] Verify per-instance texture editing still works
- [ ] Check no loss of texture quality

---

## Rollback Plan

If issues occur:
1. Restore from git: `git restore Content/Python/setup_master_universal.py`
2. Rebuild instances: `python Content/Python/setup_universal_instances.py`

---

### Task 2: Fix Nikki MF on Landscape Master

**Priority:** High  
**Estimated Effort:** 3-4 hours  
**Dependencies:** Task 1 (recommended to fix masters in order)

**Description:** Fix Nikki material function chain compatibility with landscape geometry by adding proper UV scaling and normal space handling.

**Sub-Tasks:**

- [ ] **T2.1:** Add Nikki UV Scale parameter
  - Add `NikkiUVScale` scalar parameter (default: 0.001, range: 0.0001-0.01)
  - Group: "Nikki"
  - File: `Content/Python/setup_landscape_height_blend.py`

- [ ] **T2.2:** Modify UV input for Nikki MF chain
  - Scale `layer_uv` by `NikkiUVScale` before passing to sparkle
  - Update lines 700-750 in setup_landscape_height_blend.py

- [ ] **T2.3:** Fix normal space handling
  - Verify `PixelNormalWS` is used for rim lighting calculations
  - Ensure MF_NikkiRimGlow receives world-space normal
  - Update normal input to MF_NikkiIridescenceSheen

- [ ] **T2.4:** Adjust default parameters for landscape
  - Modify `RimWidth` default for terrain scale (1.0 → 0.5)
  - Adjust `SparkleThreshold` for larger UV range

- [ ] **T2.5:** Test performance on landscape
  - Apply Nikki effects to test landscape
  - Profile frame time before/after
  - Verify < 2ms overhead

- [ ] **T2.6:** Update landscape instances
  - Rebuild landscape master with `--force`
  - Test all 12 landscape instances
  - Verify visual output in SakuraGarden scene

**Acceptance Criteria:**
- [ ] MF_NikkiSparkle produces correct sparkle pattern on landscape
- [ ] MF_NikkiRimGlow calculates proper rim lighting on terrain
- [ ] Performance overhead < 2ms when Nikki chain is active
- [ ] All 12 landscape instances compile and display correctly

**Commands:**
```bash
# Rebuild landscape master
python Content/Python/setup_landscape_height_blend.py --force

# Performance test
# Open L_SakuraPath.umap and profile with Nikki effects enabled
```

---

## Phase 2: Medium Priority

### Task 3: Expand Water Master

**Priority:** Medium  
**Estimated Effort:** 5-6 hours  
**Dependencies:** Task 1, Task 2 (recommended)

**Description:** Expand `M_Water_Master_Grand_v6` with depth, shoreline, and surface effects while maintaining concise instances.

**Sub-Tasks:**

- [ ] **T3.1:** Add Depth parameter group
  - Add `DepthColorGradient` vector parameter
  - Add `DepthOpacityFalloff` scalar parameter (0.0-1.0)
  - Add `UnderwaterTint` vector parameter
  - Implement depth-based color gradient logic
  - File: `Content/Python/setup_master_water.py` or new `expand_grand_water.py`

- [ ] **T3.2:** Add Shoreline parameter group
  - Add `ShorelineFadeDistance` scalar parameter (50-500)
  - Add `FoamColor` vector parameter
  - Implement UV-based shoreline fade
  - Add static switch `bUseShorelineUV`

- [ ] **T3.3:** Add Surface parameter group
  - Add `CausticSpeed` scalar parameter (0.0-1.0)
  - Add `RippleIntensity` scalar parameter (0.0-1.0)
  - Add `RippleScale` scalar parameter (0.01-0.2)
  - Add `SpecularBoost` scalar parameter (0.5-2.0)
  - Implement animated caustics

- [ ] **T3.4:** Create new instance presets
  - MI_GrandWater_LagoonClear (tropical clear)
  - MI_GrandWater_MysticalPool (high magical)
  - MI_GrandWater_Rapids (fast flow, foam)
  - MI_GrandWater_TropicalOcean (gradient depth)

- [ ] **T3.5:** Update existing instances
  - Add new parameters to existing 8 instances
  - Set appropriate defaults for each water type
  - Verify backward compatibility

- [ ] **T3.6:** Test all water instances
  - Verify all 12+ instances compile
  - Test visual output for each instance
  - Verify depth/shoreline/surface effects work

**Acceptance Criteria:**
- [ ] Water master has 3 new parameter groups (Depth, Shoreline, Surface)
- [ ] All 12+ water instances compile and display correctly
- [ ] Depth effects create visible underwater gradient
- [ ] Shoreline effects create visible foam and fade
- [ ] Surface effects animate caustics and ripples

**Commands:**
```bash
# Expand water master
python Content/Python/setup_master_water.py

# Verify instances
# Check /Game/EnvSandbox/Materials/Instances/Water/
```

---

### Task 4: Parameter Standardization

**Priority:** Low  
**Estimated Effort:** 3-4 hours  
**Dependencies:** Task 1, Task 2, Task 3

**Description:** Standardize parameter naming across all masters for consistency and artist-friendliness.

**Sub-Tasks:**

- [ ] **T4.1:** Audit existing parameter names
  - Extract all parameters from Universal master
  - Extract all parameters from Landscape master
  - Extract all parameters from Water master
  - Create parameter inventory document

- [ ] **T4.2:** Create naming convention document
  - Document layer naming pattern: `Layer{A/B/C}_{Property}`
  - Document texture naming pattern: `{Purpose}Map`
  - Document scalar/vector naming patterns
  - Document group naming conventions

- [ ] **T4.3:** Update parameter names in scripts
  - Update `setup_master_universal.py`
  - Update `setup_landscape_height_blend.py`
  - Update `setup_master_water.py`
  - Preserve backward compatibility with aliases

- [ ] **T4.4:** Regenerate materials
  - Run all setup scripts with `--force`
  - Verify all instances still work
  - Update instance presets with new names

**Acceptance Criteria:**
- [ ] All layer parameters follow `Layer{A/B/C}_*` pattern
- [ ] All texture parameters follow `*Map` suffix pattern
- [ ] All masters use consistent group names
- [ ] Naming convention document created

---

## Phase 3: Cleanup and Validation

### Task 5: Material Library Cleanup

**Priority:** Medium  
**Estimated Effort:** 2-3 hours  
**Dependencies:** Task 1, Task 2, Task 3 (all material changes complete)

**Description:** Clean up deprecated materials, orphan textures, and Melodia path references.

**Sub-Tasks:**

- [ ] **T5.1:** Run material library audit
  - Execute `python Content/Python/audit_material_library.py`
  - Review audit report in `Saved/Audit/material_library_audit.json`
  - Identify orphan textures and Melodia references

- [ ] **T5.2:** Create migration script
  - Create `migrate_material_paths.py`
  - Implement Melodia → EnvSandbox path replacement
  - Add dry-run mode for safety
  - Add backup mechanism

- [ ] **T5.3:** Execute migration
  - Run migration script in dry-run mode
  - Review planned changes
  - Execute migration with backup
  - Verify migrated assets

- [ ] **T5.4:** Handle orphan textures
  - Preserve textures in `SDF/Textures/` (intentional placeholders)
  - Delete confirmed orphan textures (outside SDF)
  - Reassign textures with partial refs

- [ ] **T5.5:** Clean up redirectors
  - Run `fix_migration_redirectors.py`
  - Delete stale redirector assets
  - Verify no broken references

- [ ] **T5.6:** Generate cleanup report
  - Document all deleted assets
  - Document all migrated paths
  - Create summary of changes

**Acceptance Criteria:**
- [ ] Audit shows < 5 orphan textures
- [ ] Audit shows < 50 Melodia/_PROJECT references
- [ ] All migrated assets compile and display correctly
- [ ] Cleanup report generated in `Saved/Audit/`

**Commands:**
```bash
# Run audit
python Content/Python/audit_material_library.py

# Create migration script (if not exists)
# Then run migration
python Content/Python/migrate_material_paths.py --dry-run
python Content/Python/migrate_material_paths.py

# Fix redirectors
python Content/Python/fix_migration_redirectors.py
```

---

### Task 6: Substrate Toon BSDF Validation

**Priority:** High  
**Estimated Effort:** 2 hours  
**Dependencies:** Task 1, Task 2, Task 3 (all masters complete)

**Description:** Validate that all masters have correct Substrate Toon BSDF wiring.

**Sub-Tasks:**

- [ ] **T6.1:** Create validation script
  - Create `validate_substrate_bsdf.py`
  - Check for SubstrateToonBSDF nodes
  - Verify BaseColor, Normal, Roughness connections
  - Verify Front Material output
  - Generate JSON report

- [ ] **T6.2:** Run validation on all masters
  - Validate M_Master_Toon_Universal
  - Validate M_Master_Toon_Landscape_HeightBlend
  - Validate M_Water_Master_Grand_v6
  - Validate M_Master_Impressionist_Toon
  - Validate M_Master_Impressionist_Toon_Landscape

- [ ] **T6.3:** Fix any wiring issues
  - If validation fails, review BSDF connections in Material Editor
  - Fix pin connections manually or via script
  - Re-run validation

- [ ] **T6.4:** Generate validation report
  - Create report in `Saved/Audit/bsdf_validation.json`
  - Include pass/fail status for each master
  - Document any issues found and fixed

**Acceptance Criteria:**
- [ ] Validation script created and executable
- [ ] All masters pass BSDF validation (100% pass rate)
- [ ] Validation report generated
- [ ] No legacy BaseColor-only output paths remain

**Commands:**
```bash
# Create and run validation script
python Content/Python/validate_substrate_bsdf.py

# Check report
# Saved/Audit/bsdf_validation.json
```

---

## Execution Order

### Recommended Sequence:
1. **T1: Layer Fix** (Critical, no dependencies)
2. **T2: Nikki Fix** (High, depends on T1 for workflow)
3. **T6: BSDF Validation** (High, verify T1 and T2)
4. **T3: Water Expansion** (Medium, depends on T1/T2)
5. **T4: Parameter Standardization** (Low, depends on all material changes)
6. **T5: Library Cleanup** (Medium, depends on all material changes)

### Parallel Execution Possible:
- T1 and T2 can run in parallel (different files)
- T4 and T5 can run in parallel after T1/T2/T3

---

## Progress Tracking

| Task | Status | Start Date | End Date | Notes |
|------|--------|------------|----------|-------|
| T1: Layer Fix | Not Started | - | - | Critical priority |
| T2: Nikki Fix | Not Started | - | - | High priority |
| T3: Water Expand | Not Started | - | - | Medium priority |
| T4: Params Std | Not Started | - | - | Low priority |
| T5: Cleanup | Not Started | - | - | Medium priority |
| T6: BSDF Valid | Not Started | - | - | High priority |

---

## Notes

- All tasks should be tested in a separate branch before merging to main
- Backup project before running `--force` rebuilds
- Document any deviations from this plan
- Update this document as tasks progress
---

## Task 2: Fix Nikki MF on Landscape Master - Implementation Guide

### Overview
Fix Nikki material function chain (MF_NikkiDreamGrade, MF_NikkiRimGlow, MF_NikkiSparkle, MF_NikkiIridescenceSheen) compatibility with landscape geometry.

### Problem
- Landscape uses `LandscapeLayerCoords` for UV (much larger scale than character UV)
- Nikki MF functions were designed for character-scale UV
- Normal mapping uses world-space normals for landscapes (vs tangent-space for characters)

### Implementation Steps

#### Step 2.1: Add Nikki UV Scale Parameter

**Location:** `Content/Python/setup_landscape_height_blend.py`, after existing Nikki parameters (~line 700)

```python
nikki_uv_scale = lib.scalar_param(m, "NikkiUVScale", "Nikki", 0.001, px, py + 4200)
nikki_uv_scaled = lib.create_expression(m, unreal.MaterialExpressionMultiply, x, y)
lib.connect(layer_uv, "", nikki_uv_scaled, "A")
lib.connect(nikki_uv_scale, "", nikki_uv_scaled, "B")
```

**Default Value:** 0.001 (compensates for landscape UV scale being ~1000x larger)

#### Step 2.2: Update Sparkle UV Input

**Location:** `Content/Python/setup_landscape_height_blend.py`, where sparkle is called (~line 720)

**Before:**
```python
lib.connect(layer_uv, "", sparkle, "UV")
```

**After:**
```python
lib.connect(nikki_uv_scaled, "", sparkle, "UV")
```

#### Step 2.3: Fix Normal Space Handling

**Location:** `Content/Python/setup_landscape_height_blend.py`, where normal inputs are connected

**Before:**
```python
lib.connect(nrm_final, "", irid_mf, "Normal")
```

**After:**
```python
pixel_normal = lib.create_expression(m, unreal.MaterialExpressionPixelNormalWS, x, y)
lib.connect(pixel_normal, "", irid_mf, "Normal")
```

#### Step 2.4: Adjust Default Parameters

**Add these parameter defaults:**
- `NikkiUVScale`: 0.001 (default)
- `RimWidth`: 0.5 (adjust for landscape scale)
- `SparkleThreshold`: 0.42 (keep, works well with scaled UV)

### Testing Checklist

- [ ] Rebuild landscape master: `python Content/Python/setup_landscape_height_blend.py --force`
- [ ] Open L_SakuraPath.umap
- [ ] Enable Nikki effects on test landscape material
- [ ] Verify sparkle pattern appears correctly
- [ ] Verify rim lighting works on terrain
- [ ] Profile frame time (< 2ms overhead)

---

## Task 3: Water Master Expansion - Implementation Guide

### Overview
Expand `M_Water_Master_Grand_v6` with depth, shoreline, and surface effects.

### New Parameter Groups

#### Depth Group
| Parameter | Type | Default | Range | Purpose |
|-----------|------|---------|-------|---------|
| DepthColorGradient | Vector | (0.0, 0.1, 0.2, 1.0) | Color gradient from shallow to deep |
| DepthOpacityFalloff | Scalar | 0.5 | 0.0-1.0 | Controls depth-based opacity transition |
| UnderwaterTint | Vector | (0.02, 0.08, 0.15, 1.0) | Color for deep underwater areas |

#### Shoreline Group
| Parameter | Type | Default | Range | Purpose |
|-----------|------|---------|-------|---------|
| bUseShorelineUV | Switch | False | - | Enable UV-based shoreline fade |
| ShorelineFadeDistance | Scalar | 200.0 | 50-500 | Distance over which shoreline fades |
| FoamColor | Vector | (1.0, 1.0, 1.0, 1.0) | Color of shoreline foam |

#### Surface Group
| Parameter | Type | Default | Range | Purpose |
|-----------|------|---------|-------|---------|
| CausticSpeed | Scalar | 0.15 | 0.0-1.0 | Animation speed of caustics |
| RippleIntensity | Scalar | 0.0 | 0.0-1.0 | Strength of ripple animation |
| RippleScale | Scalar | 0.05 | 0.01-0.2 | Scale of ripple patterns |
| SpecularBoost | Scalar | 1.0 | 0.5-2.0 | Specular highlight intensity |

### Implementation Steps

#### Step 3.1: Add Depth Parameters

**Location:** `Content/Python/setup_master_water.py`, in the build() function

```python
# Depth group
depth_color_grad = lib.vector_param(m, "DepthColorGradient", "Depth", (0.0, 0.1, 0.2, 1.0), x, y)
depth_opacity_falloff = lib.scalar_param(m, "DepthOpacityFalloff", "Depth", 0.5, x, y)
underwater_tint = lib.vector_param(m, "UnderwaterTint", "Depth", (0.02, 0.08, 0.15, 1.0), x, y)

# Depth-based color gradient
depth_factor = lib.create_expression(m, unreal.MaterialExpressionDepthFade, x, y)
lib.connect(depth_fade_distance, "", depth_factor, "FadeDistance")
depth_color = lerp3(m, water_color_shallow, water_color_deep, depth_factor, "depth_col", x, y)
underwater_color = lerp3(m, depth_color, underwater_tint, depth_opacity_falloff, "underwater", x, y)
```

#### Step 3.2: Add Shoreline Parameters

```python
# Shoreline group
shoreline_fade_dist = lib.scalar_param(m, "ShorelineFadeDistance", "Shoreline", 200.0, x, y)
foam_color = lib.vector_param(m, "FoamColor", "Shoreline", (1.0, 1.0, 1.0, 1.0), x, y)

# UV-based shoreline fade
shore_uv = lib.create_expression(m, unreal.MaterialExpressionTextureCoordinate, x, y)
shore_v = mask_channel(m, shore_uv, "g", "shore_v", x, y)
shore_fade = lib.create_expression(m, unreal.MaterialExpressionSmoothStep, x, y)
lib.connect(shore_v, "", shore_fade, "Value")
lib.connect(const1(m, x-200, y, 0.3), "", shore_fade, "Edge0")
lib.connect(const1(m, x-200, y+100, 0.7), "", shore_fade, "Edge1")
```

#### Step 3.3: Add Surface Parameters

```python
# Surface group
caustic_speed = lib.scalar_param(m, "CausticSpeed", "Surface", 0.15, x, y)
ripple_intensity = lib.scalar_param(m, "RippleIntensity", "Surface", 0.0, x, y)
ripple_scale = lib.scalar_param(m, "RippleScale", "Surface", 0.05, x, y)
specular_boost = lib.scalar_param(m, "SpecularBoost", "Surface", 1.0, x, y)

# Animated caustics
time_node = lib.create_expression(m, unreal.MaterialExpressionTime, x, y)
caustic_time = mul2(m, time_node, caustic_speed, "caustic_t", x, y)
```

### Testing Checklist

- [ ] All 12+ water instances compile
- [ ] Test depth effects: shallow vs deep water colors
- [ ] Test shoreline effects: foam and fade transitions
- [ ] Test surface effects: caustics animation, ripples
- [ ] Verify performance (< 1ms overhead)

---

## Summary

This implementation plan provides detailed step-by-step instructions for:

1. **Layering Fix:** Independent layer activation with weighted blending
2. **Nikki Landscape Fix:** UV scaling and normal space conversion
3. **Water Expansion:** Depth, shoreline, and surface parameter groups

Each task includes specific code snippets, locations, and testing checklists for verification.