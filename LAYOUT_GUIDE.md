# Jet Fan Tab Visual Layout Guide

## UI Structure Diagram (Current Implementation)

```
┌─────────────────────────────────────────────────────────────────────┐
│  SHARED PARAMETERS SECTION                                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Driving speed, V_kmh [km/h]: [Dropdown: 10-80]                     │
│  Jet fan diameter, Φ [mm]: [Dropdown: from JET_AREA_MAP]            │
│                                                                       │
│  Jet fan type: [High efficiency (30 m/s) | Standard (34 m/s)]       │
│                                                                       │
├─────────────────────────────────────────────────────────────────────┤
│  DIRECTION-SPECIFIC CALCULATION COLUMNS                              │
├────────────────────────────────┬────────────────────────────────────┤
│                                │                                     │
│ Calculate number needed from   │ Calculate number needed from        │
│ {dir1_name} to {dir2_name}    │ {dir2_name} to {dir1_name}         │
│ ═════════════════════════════  │ ═════════════════════════════     │
│                                │                                     │
│ Required ventilation Qtreq:    │ Required ventilation Qtreq:        │
│ [Input Field] m³/s             │ [Input Field] m³/s                 │
│                                │                                     │
│ Number of lanes:               │ Number of lanes:                   │
│ [Input Field]                  │ [Input Field]                      │
│                                │                                     │
│ Tunnel cross-sectional Ar:     │ Tunnel cross-sectional Ar:         │
│ [RO] m²                        │ [RO] m²                            │
│                                │                                     │
│ Tunnel length Lr:              │ Tunnel length Lr:                  │
│ [RO] m                         │ [RO] m                             │
│                                │                                     │
│ Representative diameter Dr:    │ Representative diameter Dr:        │
│ [RO] m                         │ [RO] m                             │
│                                │                                     │
│ ─────────────────────────────  │ ─────────────────────────────     │
│                                │                                     │
│ Exact number of Jet Fans:      │ Exact number of Jet Fans:          │
│ [RESULT: blue bold]            │ [RESULT: blue bold]                │
│                                │                                     │
│ Approximated number required:  │ Approximated number required:      │
│ [RESULT: blue bold]            │ [RESULT: blue bold]                │
│                                │                                     │
├────────────────────────────────┴────────────────────────────────────┤
│  JET FAN CONSTANTS SECTION                                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Natural wind speed Un (m/s): [RO]    Driving speed Vt (m/s): [RO]  │
│  Air density ρ (kg/m³): [RO]          Entrance loss ξ: [RO]         │
│  Friction loss λ: [RO]                Equivalent resistance Ae: [RO] │
│  Jet fan efficiency η: [RO]                                          │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

Legend:
[Input Field] = Editable text field with numeric validation
[RO] = Read-only field (auto-synced from VentilationVolumeTab)
[RESULT] = Computed result (updated by Compute Summary button), displayed in blue bold
{dir1_name}, {dir2_name} = Dynamic labels from VentilationVolumeTab
```

## Variable Flow Map (Current Implementation)

```
SHARED VARIABLES (both directions use same values):
├─ v_kmh_var .......................... Driving speed 10-80 km/h (ComboBox)
├─ jet_diameter_var ................... Jet fan diameter from JET_AREA_MAP (ComboBox)
├─ high_eff_var ....................... Efficiency type: "High efficiency (30 m/s)" or "Standard (34 m/s)"
└─ Constants (all RO):
   ├─ un_var = 2.5 .................... Natural wind speed (constant)
   ├─ vt_var .......................... Driving speed in m/s (updated when v_kmh changes via Vt_MAP)
   ├─ rho_var = 1.2 ................... Air density (constant)
   ├─ xi_var = 0.6 .................... Entrance loss (constant)
   ├─ lamb_var = 0.025 ................ Friction loss (constant)
   ├─ ae_var = 1.0751 ................. Equivalent resistance (constant)
   └─ eta_var = 0.95 .................. Jet fan efficiency (constant)

DIRECTION 1 (FROM→TO):
├─ Input Variables (Editable):
│  ├─ qtreq_dir1_var .................. User-editable required ventilation (m³/s)
│  └─ lanes_dir1_var .................. User-editable number of lanes
├─ Synced Variables (RO, from VentilationVolumeTab):
│  ├─ ar_dir1_var ..................... From tunnelGeometryFromToTo.avg_ar_var
│  ├─ lr_dir1_var ..................... From totalLengthFromToTo_m
│  ├─ dr_dir1_var ..................... From tunnelGeometryFromToTo.dr_var
│  └─ imax_dir1_var ................... From get_volume_summary("FromToTo").cap_per_lane
└─ Result Variables (updated on Compute button):
   ├─ exact_z_dir1_var ................ Format: f"{Z_raw:.2f}"
   └─ approx_z_dir1_var ............... Format: str(Z_applied)

DIRECTION 2 (TO→FROM):
├─ Input Variables (Editable):
│  ├─ qtreq_dir2_var .................. User-editable required ventilation (m³/s)
│  └─ lanes_dir2_var .................. User-editable number of lanes
├─ Synced Variables (RO, from VentilationVolumeTab):
│  ├─ ar_dir2_var ..................... From tunnelGeometryToToFrom.avg_ar_var
│  ├─ lr_dir2_var ..................... From totalLengthToToFrom_m
│  ├─ dr_dir2_var ..................... From tunnelGeometryToToFrom.dr_var
│  └─ imax_dir2_var ................... From get_volume_summary("ToToFrom").cap_per_lane
└─ Result Variables (updated on Compute button):
   ├─ exact_z_dir2_var ................ Format: f"{Z_raw:.2f}"
   └─ approx_z_dir2_var ............... Format: str(Z_applied)

Dynamic Label Updates:
├─ dir1_labelframe.config(text) ..... Updated by tracing dir1Name and dir2Name from VentilationVolumeTab
└─ dir2_labelframe.config(text) ..... Updated by tracing dir1Name and dir2Name from VentilationVolumeTab
```

## Synchronization Trigger Map (Current Implementation)

```
VentilationVolumeTab Changes → JetFanTab Automatic Sync:

DIRECTION 1 (FromToTo):
├─ tunnelGeometryFromToTo.avg_ar_var changes
│  └─ sync_dir1() triggered
│     └─ ar_dir1_var.set(new_value)
│        └─ _recompute_dynamic() clears results
├─ tunnelGeometryFromToTo.avg_lp_var changes
│  └─ sync_dir1() triggered
│     └─ (no direct effect on displayed values, monitored for consistency)
├─ tunnelGeometryFromToTo.dr_var changes
│  └─ sync_dir1() triggered
│     └─ dr_dir1_var.set(new_value)
│        └─ _recompute_dynamic() clears results
├─ totalLengthFromToTo_m changes
│  └─ sync_dir1() triggered
│     └─ lr_dir1_var.set(new_value)
│        └─ _recompute_dynamic() clears results
└─ designSpeedFromToTo changes
   └─ sync_dir1() triggered
      └─ imax_dir1_var.set(new_value)
         └─ _recompute_dynamic() clears results

DIRECTION 2 (ToToFrom):
├─ tunnelGeometryToToFrom.avg_ar_var changes
│  └─ sync_dir2() triggered
│     └─ ar_dir2_var.set(new_value)
│        └─ _recompute_dynamic() clears results
├─ tunnelGeometryToToFrom.avg_lp_var changes
│  └─ sync_dir2() triggered
│     └─ (no direct effect on displayed values, monitored for consistency)
├─ tunnelGeometryToToFrom.dr_var changes
│  └─ sync_dir2() triggered
│     └─ dr_dir2_var.set(new_value)
│        └─ _recompute_dynamic() clears results
├─ totalLengthToToFrom_m changes
│  └─ sync_dir2() triggered
│     └─ lr_dir2_var.set(new_value)
│        └─ _recompute_dynamic() clears results
└─ designSpeedToToFrom changes
   └─ sync_dir2() triggered
      └─ imax_dir2_var.set(new_value)
         └─ _recompute_dynamic() clears results

LABEL UPDATES (triggered by VentilationVolumeTab):
├─ dir1Name variable changes
│  └─ update_labels() triggered
│     └─ dir1_labelframe.config(text=f"Calculate number needed from {dir1_name} to {dir2_name}")
├─ dir2Name variable changes
│  └─ update_labels() triggered
│     └─ dir2_labelframe.config(text=f"Calculate number needed from {dir2_name} to {dir1_name}")
```

## Computation Sequence (Current Implementation)

```
USER FLOW 1: Shared Parameter Change
────────────────────────────────────
User changes v_kmh_var (ComboBox) or jet_diameter_var or high_eff_var
│
├─ _on_vkmh_changed() called [if v_kmh changed]
│  ├─ un_var.set(2.5)
│  ├─ vt_var.set(Vt_MAP.get(int(v_kmh)))
│  └─ _recompute_dynamic()
│     ├─ exact_z_dir1_var.set("-")
│     ├─ approx_z_dir1_var.set("-")
│     ├─ exact_z_dir2_var.set("-")
│     └─ approx_z_dir2_var.set("-")
│
└─ Results cleared (no auto-compute; user must click "Compute Summary")


USER FLOW 2: Input Field Change
────────────────────────────────
User edits qtreq_dir1_var, lanes_dir1_var, qtreq_dir2_var, or lanes_dir2_var
│
└─ Trace triggers _recompute_dynamic()
   ├─ exact_z_dir1_var.set("-")
   ├─ approx_z_dir1_var.set("-")
   ├─ exact_z_dir2_var.set("-")
   └─ approx_z_dir2_var.set("-")


USER FLOW 3: "Compute Summary" Button Click (from MainWindow)
──────────────────────────────────────────────────────────────
User clicks "Compute Summary" button
│
└─ compute_and_publish() called
   │
   └─ _on_compute()
      │
      ├─ Direction 1 Computation:
      │  ├─ _build_inputs_object(direction=1)
      │  │  └─ Collects: v_kmh, qtreq_dir1, lanes_dir1, ar_dir1, lr_dir1, dr_dir1,
      │  │              rho, xi, lamb, Ae, jet_diameter, high_eff, eta, vehicle_hr_lane
      │  │              Returns TunnelVentInputs object
      │  ├─ compute_all(inp_dir1)
      │  │  └─ Returns TunnelVentResults with Z_raw and Z_applied
      │  ├─ exact_z_dir1_var.set(f"{results.Z_raw:.2f}")
      │  └─ approx_z_dir1_var.set(f"{results.Z_applied}")
      │
      ├─ Direction 2 Computation:
      │  ├─ _build_inputs_object(direction=2)
      │  │  └─ Collects: v_kmh, qtreq_dir2, lanes_dir2, ar_dir2, lr_dir2, dr_dir2,
      │  │              rho, xi, lamb, Ae, jet_diameter, high_eff, eta, vehicle_hr_lane
      │  │              Returns TunnelVentInputs object
      │  ├─ compute_all(inp_dir2)
      │  │  └─ Returns TunnelVentResults with Z_raw and Z_applied
      │  ├─ exact_z_dir2_var.set(f"{results.Z_raw:.2f}")
      │  └─ approx_z_dir2_var.set(f"{results.Z_applied}")
      │
      └─ result_tab.display_results_dual() called
         └─ Results Tab displays computed data for both directions


VOLUME TAB CHANGE FLOW
──────────────────────
VentilationVolumeTab geometry/capacity changes
│
├─ sync_dir1() or sync_dir2() triggered (via trace_add)
│  │
│  ├─ get_params_for_jet(direction) retrieves Ar, Lr_m, Dr
│  ├─ get_volume_summary(direction) retrieves cap_per_lane, lanes
│  ├─ Update direction-specific read-only variables
│  └─ _recompute_dynamic() clears results (results = "-")
│
└─ User must re-click "Compute Summary" to recompute with new geometry
```

## Column Independence (Current Implementation)

```
Column 1 (FROM→TO, Direction 1)        Column 2 (TO→FROM, Direction 2)
├─ Shared Controls:                    ├─ Shared Controls:
│  ├─ V_kmh = 50                       │  ├─ V_kmh = 50 (SAME)
│  ├─ Jet diameter = 315               │  ├─ Jet diameter = 315 (SAME)
│  └─ Jet fan type = High eff          │  └─ Jet fan type = High eff (SAME)
│                                       │
├─ Direction-Specific Inputs:          ├─ Direction-Specific Inputs:
│  ├─ Qtreq_dir1 = 100                 │  ├─ Qtreq_dir2 = 150
│  └─ Lanes_dir1 = 2                   │  └─ Lanes_dir2 = 3
│                                       │
├─ Synced Read-Only Variables:         ├─ Synced Read-Only Variables:
│  ├─ Ar_dir1 = 45.6 (from Vol Tab)    │  ├─ Ar_dir2 = 45.6 (from Vol Tab)
│  ├─ Lr_dir1 = 5000 (from Vol Tab)    │  ├─ Lr_dir2 = 5000 (from Vol Tab)
│  └─ Dr_dir1 = 4.2 (from Vol Tab)     │  └─ Dr_dir2 = 4.2 (from Vol Tab)
│                                       │
│ _build_inputs_object(1)               │ _build_inputs_object(2)
│ compute_all(inp_dir1)                 │ compute_all(inp_dir2)
│ ↓                                     │ ↓
├─ Results (Direction 1):               ├─ Results (Direction 2):
│  ├─ Z_raw_1 = 12.34                   │  ├─ Z_raw_2 = 18.56
│  └─ Z_applied_1 = 13                  │  └─ Z_applied_2 = 19
│                                       │

NOTE: Even though shared controls (V_kmh, jet diameter, type) and synced
      read-only values (Ar, Lr, Dr) are IDENTICAL for both directions,
      the results differ because Qtreq_dir1 ≠ Qtreq_dir2 and Lanes_dir1 ≠ Lanes_dir2.
      Each direction computes independently using its own input values.
```

## Layout Tree Structure (Current Implementation)

```
JetFanTab (ttk.Frame)
│
└─ main_container (ttk.Frame, padding="20 20 20 20")
   │
   ├─ top_frame (ttk.LabelFrame "Shared Parameters", padding="10 10 10 10")
   │  ├─ Row 0, Col 0-1: Driving speed V_kmh (ComboBox: 10-80)
   │  ├─ Row 0, Col 2-3: Jet fan diameter Φ (ComboBox: from JET_AREA_MAP)
   │  ├─ Row 1, Col 0-3 (colspan): Jet fan type (ComboBox: High/Standard)
   │  │
   │  └─ Column Config: [weight 0, 1, 0, 1]
   │
   ├─ columns_frame (ttk.Frame, fill="both", expand=True)
   │  │
   │  ├─ Column 0: col_frame (ttk.LabelFrame "Calculate number needed from {dir1} to {dir2}")
   │  │  │
   │  │  ├─ Row 0: Required ventilation Qtreq (Entry, input)
   │  │  ├─ Row 1: Number of lanes (Entry, input)
   │  │  ├─ Row 2: Tunnel cross-sectional Ar (Entry, RO)
   │  │  ├─ Row 3: Tunnel length Lr (Entry, RO)
   │  │  ├─ Row 4: Representative diameter Dr (Entry, RO)
   │  │  ├─ Row 5: Separator (horizontal line)
   │  │  ├─ Row 6: Exact number of Jet Fans (Label, blue bold result)
   │  │  ├─ Row 7: Approximated number (Label, blue bold result)
   │  │  │
   │  │  └─ Column Config: [weight 0, 1]
   │  │
   │  └─ Column 1: col_frame (ttk.LabelFrame "Calculate number needed from {dir2} to {dir1}")
   │     │
   │     ├─ Row 0: Required ventilation Qtreq (Entry, input)
   │     ├─ Row 1: Number of lanes (Entry, input)
   │     ├─ Row 2: Tunnel cross-sectional Ar (Entry, RO)
   │     ├─ Row 3: Tunnel length Lr (Entry, RO)
   │     ├─ Row 4: Representative diameter Dr (Entry, RO)
   │     ├─ Row 5: Separator (horizontal line)
   │     ├─ Row 6: Exact number of Jet Fans (Label, blue bold result)
   │     ├─ Row 7: Approximated number (Label, blue bold result)
   │     │
   │     └─ Column Config: [weight 0, 1]
   │
   └─ bottom_frame (ttk.LabelFrame "Jet Fan Constants", padding="10 10 10 10")
      │
      ├─ Row 0: Natural wind speed Un (Entry, RO) | Driving speed Vt (Entry, RO)
      ├─ Row 1: Air density ρ (Entry, RO) | Entrance loss ξ (Entry, RO)
      ├─ Row 2: Friction loss λ (Entry, RO) | Equivalent resistance Ae (Entry, RO)
      ├─ Row 3: Jet fan efficiency η (Entry, RO)
      │
      └─ Column Config: [weight 0, 1, 0, 1]
```

## Color & Typography (Current Implementation)

```
Field Types & Styling:
├─ Input Fields (ttk.Entry)
│  ├─ Background: Default (light/white)
│  ├─ Editable: Yes
│  ├─ Font: Default ttk.Entry font
│  ├─ Validation: Numeric validation (digits, decimal, minus sign)
│  ├─ Focus behaviors:
│  │  ├─ FocusIn: Clear entry on click
│  │  └─ FocusOut: Set to "0" if empty
│  └─ Examples: Qtreq, Lanes
│
├─ Read-Only Fields (ttk.Entry, state="readonly")
│  ├─ Background: Gray
│  ├─ Editable: No
│  ├─ Font: Default ttk.Entry font
│  └─ Examples: Ar, Lr, Dr, all Constants (Un, Vt, ρ, ξ, λ, Ae, η)
│
├─ Result Labels (ttk.Label)
│  ├─ Foreground Color: #004080 (dark blue)
│  ├─ Font: Arial 11 Bold
│  ├─ Content Format:
│  │  ├─ exact_z: f"{Z_raw:.2f}" (2 decimal places)
│  │  └─ approx_z: str(Z_applied) (integer)
│  └─ Examples: Exact number of Jet Fans, Approximated number
│
└─ Section Headers (ttk.LabelFrame, text property)
   ├─ Font: Default bold (ttk.LabelFrame default)
   ├─ Sections:
   │  ├─ "Shared Parameters"
   │  ├─ "Calculate number needed from {dir1_name} to {dir2_name}"
   │  ├─ "Calculate number needed from {dir2_name} to {dir1_name}"
   │  └─ "Jet Fan Constants"
   └─ Dynamic: Labels updated when VentilationVolumeTab direction names change

Spacing:
├─ Internal padding (pad variable): 6 pixels (used in grid pady/padx)
├─ Section separation: pad * 3 = 18 pixels (vertical padding between sections)
├─ Column horizontal padding: 6 pixels
└─ Main container padding: 20 pixels on all sides
```

## Implementation Status & Key Features

### Actual Implementation Details:

**Numeric Validation:**
- All input fields (Qtreq, Lanes) use `NumericValidator.validate_numeric()`
- Allows: digits (0-9), decimal point (.), minus sign (-)
- FocusIn: Clears field value for clean data entry
- FocusOut: Defaults to "0" if field is left empty

**Dynamic Direction Labels:**
- Column headers dynamically updated from `VentilationVolumeTab.dir1Name` and `dir2Name`
- LabelFrame titles: "Calculate number needed from {dir1_name} to {dir2_name}"
- Updated in real-time via trace_add on volume tab variables

**Shared Parameters Behavior:**
- V_kmh selection triggers `_on_vkmh_changed()`
  - Un remains constant at 2.5 m/s
  - Vt updates via `Vt_MAP` lookup
  - Results are cleared (reset to "-")
- Jet diameter dropdown: values populated from `JET_AREA_MAP.keys()`
- Jet fan type: "High efficiency (30 m/s)" or "Standard (34 m/s)"

**Computation:**
- Results cleared on any parameter change (dynamic triggers)
- Explicit computation only on "Compute Summary" button click from MainWindow
- `_on_compute()` computes both directions independently
- Results sent to ResultTab via `display_results_dual()`

**Synchronization with VentilationVolumeTab:**
- Automatic syncing of Ar, Lr, Dr, and lane defaults
- 100ms delayed initial sync to ensure VentilationVolumeTab is ready
- Direction names automatically update column titles
- Capacity (Imax) synced to support vehicle-hour-lane calculations

**Result Formatting:**
- Exact number: Two decimal places (e.g., "12.34")
- Approximated number: Integer value (e.g., "13")
- Both displayed in blue bold (Arial 11)

### Visual Design Goals:

- **Symmetric two-column layout** emphasizes dual-direction nature of tunnel ventilation
- **Clear section separation** (Shared Parameters → Direction Columns → Constants) improves readability
- **Color coding (blue results)** draws attention to computed values
- **LabelFrames group related parameters** together logically
- **Dynamic labels** adapt to user-defined direction names from VentilationVolumeTab
- **Read-only fields** prevent accidental changes to synced geometry parameters
- **Numeric validation** ensures data integrity in input fields
- **Responsive design** with weighted columns for flexible layout

