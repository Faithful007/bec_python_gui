# Jet Fan Tab Bidirectional Layout Refactoring

## Overview
Successfully restructured the **Number of Jet Fan** tab to support simultaneous bidirectional calculations with a two-column layout. Each column now independently calculates jet fan requirements for opposite tunnel directions.

## Key Changes

### 1. Variable Architecture Refactoring
**Previous Structure:** Single set of variables for one direction
```python
self.qtreq_var       # Single variable for required ventilation
self.lanes_var       # Single variable for number of lanes
self.ar_var          # Single variable for cross-sectional area
self.lr_var          # Single variable for tunnel length
self.dr_var          # Single variable for representative diameter
```

**New Structure:** Separate variable sets for each direction
```python
# Direction 1 (FROM→TO, MasanToJinju)
self.qtreq_dir1_var, self.lanes_dir1_var, self.ar_dir1_var, self.lr_dir1_var, self.dr_dir1_var
self.imax_dir1_var   # Capacity per lane for direction 1
self.exact_z_dir1_var, self.approx_z_dir1_var  # Results

# Direction 2 (TO→FROM, JinjuToMasan)
self.qtreq_dir2_var, self.lanes_dir2_var, self.ar_dir2_var, self.lr_dir2_var, self.dr_dir2_var
self.imax_dir2_var   # Capacity per lane for direction 2
self.exact_z_dir2_var, self.approx_z_dir2_var  # Results

# Shared across directions (not direction-specific)
self.v_kmh_var       # Driving speed (applies to both)
self.jet_diameter_var  # Jet diameter (applies to both)
self.high_eff_var    # Efficiency type (applies to both)
```

### 2. Layout Restructuring (_build_layout)
Reorganized from single-column to three-section layout:

**Section 1: Shared Parameters (Top)**
- Driving speed V_kmh (10-80 km/h dropdown)
- Jet fan diameter (from JET_AREA_MAP)
- Jet fan type (High efficiency 30 m/s / Standard 34 m/s)

**Section 2: Two-Column Direction-Specific Panels (Middle)**
- **Left Column:** "Calculate number needed from [DIR1] to [DIR2]"
  - Required ventilation Qtreq (editable)
  - Number of lanes (editable)
  - Tunnel cross-sectional area Ar (auto-synced from VentilationVolumeTab MasanToJinju)
  - Tunnel length Lr (auto-synced)
  - Representative diameter Dr (auto-synced)
  - Exact and Approximated jet fan requirements (computed results)

- **Right Column:** "Calculate number needed from [DIR2] to [DIR1]"
  - Same parameters but for opposite direction (JinjuToMasan)

**Section 3: Constants (Bottom)**
- Natural wind speed Un, Driving speed Vt
- Air density ρ, Entrance loss ξ
- Friction loss λ, Equivalent resistance Ae
- Jet fan efficiency η

### 3. Bidirectional Data Syncing (_wire_volume_sources)
Implemented separate sync functions for each tunnel direction:

**sync_dir1()** - Syncs FROM→TO (MasanToJinju) parameters:
- Traces: `tunnelGeometryMasanToJinju.avg_ar_var`, `avg_lp_var`, `dr_var`
- Traces: `totalLengthMasanToJinju_m`, `designSpeedMasanToJinju`
- Updates: `ar_dir1_var`, `lr_dir1_var`, `dr_dir1_var`, `imax_dir1_var`, `lanes_dir1_var`

**sync_dir2()** - Syncs TO→FROM (JinjuToMasan) parameters:
- Traces: `tunnelGeometryJinjuToMasan.avg_ar_var`, `avg_lp_var`, `dr_var`
- Traces: `totalLengthJinjuToMasan_m`, `designSpeedJinjuToMasan`
- Updates: `ar_dir2_var`, `lr_dir2_var`, `dr_dir2_var`, `imax_dir2_var`, `lanes_dir2_var`

Both sync functions trigger `_recompute_dynamic()` to update result displays.

### 4. Direction-Aware Input Building (_build_inputs_object)
Enhanced to support dual-direction computation:

```python
def _build_inputs_object(self, direction=1) -> TunnelVentInputs:
    # direction=1: Uses DIR1 variables (MasanToJinju)
    # direction=2: Uses DIR2 variables (JinjuToMasan)
    
    # Selects appropriate variable set based on direction
    if direction == 1:
        qtreq_var, lanes_var, ar_var, lr_var, dr_var, imax_var
        direction_str = "MasanToJinju"
    else:
        qtreq_var, lanes_var, ar_var, lr_var, dr_var, imax_var
        direction_str = "JinjuToMasan"
    
    # Builds TunnelVentInputs with correct parameters
```

### 5. Independent Computation (_on_compute)
Both directions computed simultaneously:
```python
# Compute Direction 1
inp_dir1 = self._build_inputs_object(direction=1)
results_dir1 = compute_all(inp_dir1)
self.exact_z_dir1_var.set(f"{results_dir1.Z_raw:.2f}")
self.approx_z_dir1_var.set(f"{results_dir1.Z_applied}")

# Compute Direction 2
inp_dir2 = self._build_inputs_object(direction=2)
results_dir2 = compute_all(inp_dir2)
self.exact_z_dir2_var.set(f"{results_dir2.Z_raw:.2f}")
self.approx_z_dir2_var.set(f"{results_dir2.Z_applied}")

# Send first direction to ResultsTab
if self.result_tab:
    self.result_tab.display_results(inp_dir1, results_dir1)
```

### 6. Dynamic Direction Labels
Direction labels ("FROM", "TO", etc.) are fetched from VentilationVolumeTab at layout build time:
```python
if self.volume_tab:
    dir1_name = self.volume_tab.dir1Name.get()
    dir2_name = self.volume_tab.dir2Name.get()
```

These names are used as column titles: "Calculate number needed from {dir1_name} to {dir2_name}"

## Architecture Benefits

1. **True Bidirectional Support:** Each column represents a complete calculation path with independent inputs and outputs
2. **Synchronized Geometry:** Both directions automatically pull from their respective tunnel geometry definitions
3. **Shared Configuration:** V_kmh, jet diameter, and efficiency settings apply to both directions simultaneously
4. **Clean Separation:** Direction-specific logic isolated in variables and methods (dir1/dir2 suffixes)
5. **Extensible Design:** Easy to add additional directions or modify computation per direction

## Data Flow

```
VentilationVolumeTab
├── tunnelGeometryMasanToJinju (avg_ar, avg_lp, dr)
│   └─→ sync_dir1() → JetFanTab (dir1 variables)
│
└── tunnelGeometryJinjuToMasan (avg_ar, avg_lp, dr)
    └─→ sync_dir2() → JetFanTab (dir2 variables)

JetFanTab
├── User Input (qtreq, lanes, shared parameters)
└── _on_compute()
    ├─→ _build_inputs_object(direction=1) → compute_all() → exact_z_dir1, approx_z_dir1
    └─→ _build_inputs_object(direction=2) → compute_all() → exact_z_dir2, approx_z_dir2
```

## Testing Recommendations

1. **Layout Test:** Verify both columns display side-by-side with proper titles
2. **Sync Test:** Change values in Ventilation Volume tab and confirm Ar/Lr/Dr update in both columns
3. **Computation Test:** Enter values in both columns and verify compute button produces different results for each
4. **Direction Labels:** Edit dir1Name/dir2Name in Ventilation Volume tab and verify column titles update
5. **Backward Compatibility:** Verify compute_and_publish() and ResultsTab integration still works

## Files Modified
- `main_gui.py` - JetFanTab class

## Code Structure Summary
| Component | Lines | Purpose |
|-----------|-------|---------|
| _build_variables() | 40-58 | Create all directional and shared variables |
| _build_layout() | 97-248 | Create three-section UI layout |
| _build_direction_column() | 249-341 | Create individual column frame |
| _build_inputs_object() | 355-410 | Build inputs for specified direction |
| _wire_volume_sources() | 452-539 | Sync both directions from volume_tab |
| _on_compute() | 424-445 | Compute both directions independently |
| _recompute_dynamic() | 447-452 | Clear result displays |

