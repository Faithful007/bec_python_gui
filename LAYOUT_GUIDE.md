# Jet Fan Tab Visual Layout Guide

## UI Structure Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│  SHARED PARAMETERS SECTION                                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Driving speed V_kmh: [Dropdown: 10-80]  Jet fan diameter: [mmm]    │
│  Jet fan type: [High efficiency | Standard]                          │
│                                                                       │
├─────────────────────────────────────────────────────────────────────┤
│  DIRECTION-SPECIFIC CALCULATION COLUMNS                              │
├────────────────────────────────┬────────────────────────────────────┤
│                                │                                     │
│ FROM→TO Direction (Column 1)   │ TO→FROM Direction (Column 2)       │
│ ═════════════════════════════  │ ═════════════════════════════     │
│                                │                                     │
│ Required ventilation Qtreq:    │ Required ventilation Qtreq:        │
│ [Input Field] m³/s             │ [Input Field] m³/s                 │
│                                │                                     │
│ Number of lanes:               │ Number of lanes:                   │
│ [Input Field]                  │ [Input Field]                      │
│                                │                                     │
│ Tunnel Ar (m²):                │ Tunnel Ar (m²):                    │
│ [Synced from Vol Tab] RO        │ [Synced from Vol Tab] RO           │
│                                │                                     │
│ Tunnel length Lr (m):          │ Tunnel length Lr (m):              │
│ [Synced from Vol Tab] RO        │ [Synced from Vol Tab] RO           │
│                                │                                     │
│ Rep. diameter Dr (m):          │ Rep. diameter Dr (m):              │
│ [Synced from Vol Tab] RO        │ [Synced from Vol Tab] RO           │
│                                │                                     │
│ ─────────────────────────────  │ ─────────────────────────────     │
│                                │                                     │
│ Exact Jet Fans needed: [RESULT]│ Exact Jet Fans needed: [RESULT]    │
│ Approx. needed:        [RESULT]│ Approx. needed:        [RESULT]    │
│                                │                                     │
├────────────────────────────────┴────────────────────────────────────┤
│  JET FAN CONSTANTS SECTION                                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Un (m/s): [RO]         Vt (m/s): [RO]                              │
│  ρ (kg/m³): [RO]        ξ: [RO]                                     │
│  λ: [RO]                Ae (m²): [RO]                               │
│  η: [RO]                                                             │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

Legend:
[Input Field] = Editable text field
[RO] = Read-only field (auto-synced from VentilationVolumeTab)
[RESULT] = Computed result (updated by Compute Summary button)
```

## Variable Flow Map

```
SHARED VARIABLES (both directions use same values):
├─ v_kmh_var ........... Driving speed 10-80 km/h
├─ jet_diameter_var .... Jet fan diameter from dropdown
├─ high_eff_var ........ Efficiency type (High/Standard)
└─ un_var, vt_var, rho_var, xi_var, lamb_var, ae_var, eta_var ... Constants

DIRECTION 1 (FROM→TO, MasanToJinju):
├─ Input Variables:
│  ├─ qtreq_dir1_var ... User-editable required ventilation
│  └─ lanes_dir1_var ... User-editable number of lanes
├─ Synced Variables:
│  ├─ ar_dir1_var ....... From tunnelGeometryMasanToJinju.avg_ar_var
│  ├─ lr_dir1_var ....... From totalLengthMasanToJinju_m
│  ├─ dr_dir1_var ....... From tunnelGeometryMasanToJinju.dr_var
│  └─ imax_dir1_var .... From get_volume_summary("MasanToJinju")
└─ Result Variables:
   ├─ exact_z_dir1_var .. Z_raw formatted to 2 decimals
   └─ approx_z_dir1_var . Z_applied formatted as integer

DIRECTION 2 (TO→FROM, JinjuToMasan):
├─ Input Variables:
│  ├─ qtreq_dir2_var ... User-editable required ventilation
│  └─ lanes_dir2_var ... User-editable number of lanes
├─ Synced Variables:
│  ├─ ar_dir2_var ....... From tunnelGeometryJinjuToMasan.avg_ar_var
│  ├─ lr_dir2_var ....... From totalLengthJinjuToMasan_m
│  ├─ dr_dir2_var ....... From tunnelGeometryJinjuToMasan.dr_var
│  └─ imax_dir2_var .... From get_volume_summary("JinjuToMasan")
└─ Result Variables:
   ├─ exact_z_dir2_var .. Z_raw formatted to 2 decimals
   └─ approx_z_dir2_var . Z_applied formatted as integer
```

## Synchronization Trigger Map

```
VentilationVolumeTab Changes:
│
├─ tunnelGeometryMasanToJinju.avg_ar_var changes
│  └─ TRACE: sync_dir1() triggered
│     └─ ar_dir1_var.set(new_value)
│        └─ _recompute_dynamic() clears results
│
├─ tunnelGeometryMasanToJinju.avg_lp_var changes
│  └─ TRACE: sync_dir1() triggered
│     └─ (no direct effect on displayed values)
│
├─ tunnelGeometryMasanToJinju.dr_var changes
│  └─ TRACE: sync_dir1() triggered
│     └─ dr_dir1_var.set(new_value)
│        └─ _recompute_dynamic() clears results
│
├─ totalLengthMasanToJinju_m changes
│  └─ TRACE: sync_dir1() triggered
│     └─ lr_dir1_var.set(new_value)
│        └─ _recompute_dynamic() clears results
│
├─ designSpeedMasanToJinju changes
│  └─ TRACE: sync_dir1() triggered
│     └─ imax_dir1_var.set(new_value)
│        └─ _recompute_dynamic() clears results
│
└─ [Same pattern for Direction 2 with JinjuToMasan]
```

## Computation Sequence

```
User clicks "Compute Summary" button
│
├─ compute_summary() called (from main window)
│  │
│  └─ jet_fan_tab.compute_and_publish()
│     │
│     └─ _on_compute()
│        │
│        ├─ Direction 1 Computation:
│        │  ├─ _build_inputs_object(direction=1)
│        │  │  └─ Collects: v_kmh, qtreq_dir1, lanes_dir1, ar_dir1, lr_dir1, dr_dir1, etc.
│        │  ├─ compute_all(inp_dir1)
│        │  │  └─ Returns TunnelVentResults with Z_raw and Z_applied
│        │  └─ exact_z_dir1_var.set(f"{results.Z_raw:.2f}")
│        │     approx_z_dir1_var.set(f"{results.Z_applied}")
│        │
│        └─ Direction 2 Computation:
│           ├─ _build_inputs_object(direction=2)
│           │  └─ Collects: v_kmh, qtreq_dir2, lanes_dir2, ar_dir2, lr_dir2, dr_dir2, etc.
│           ├─ compute_all(inp_dir2)
│           │  └─ Returns TunnelVentResults with Z_raw and Z_applied
│           └─ exact_z_dir2_var.set(f"{results.Z_raw:.2f}")
│              approx_z_dir2_var.set(f"{results.Z_applied}")
│
└─ Results Tab displays Direction 1 data
```

## Column Independence

```
Column 1 (DIR1)                  Column 2 (DIR2)
├─ Qtreq_dir1 = 100            ├─ Qtreq_dir2 = 150
├─ Lanes_dir1 = 2              ├─ Lanes_dir2 = 3
├─ Ar_dir1 = 45.6 (synced)     ├─ Ar_dir2 = 45.6 (synced)
├─ Lr_dir1 = 5000 (synced)     ├─ Lr_dir2 = 5000 (synced)
├─ Dr_dir1 = 4.2 (synced)      ├─ Dr_dir2 = 4.2 (synced)
│                               │
│ compute_all(inp_dir1)         │ compute_all(inp_dir2)
│ ↓                              │ ↓
├─ Z_raw_1 = 12.34            ├─ Z_raw_2 = 18.56
└─ Z_applied_1 = 13           └─ Z_applied_2 = 19

Note: Even though Ar, Lr, Dr are same (from same tunnel),
      results differ because Qtreq and lanes are different
```

## Layout Tree Structure

```
JetFanTab (main frame)
│
└─ main_container (ttk.Frame with padding 20)
   │
   ├─ top_frame (ttk.LabelFrame "Shared Parameters")
   │  ├─ Row 0: V_kmh + jet_diameter
   │  └─ Row 1: high_eff (spans columns)
   │
   ├─ columns_frame (ttk.Frame)
   │  ├─ Column 0: col_frame (ttk.LabelFrame "FROM→TO")
   │  │  ├─ qtreq input
   │  │  ├─ lanes input
   │  │  ├─ ar readonly
   │  │  ├─ lr readonly
   │  │  ├─ dr readonly
   │  │  ├─ separator
   │  │  ├─ exact_z result
   │  │  └─ approx_z result
   │  │
   │  └─ Column 1: col_frame (ttk.LabelFrame "TO→FROM")
   │     ├─ qtreq input
   │     ├─ lanes input
   │     ├─ ar readonly
   │     ├─ lr readonly
   │     ├─ dr readonly
   │     ├─ separator
   │     ├─ exact_z result
   │     └─ approx_z result
   │
   └─ bottom_frame (ttk.LabelFrame "Jet Fan Constants")
      ├─ Row 0: Un + Vt
      ├─ Row 1: ρ + ξ
      ├─ Row 2: λ + Ae
      └─ Row 3: η
```

## Color & Typography

```
Field Types:
├─ [Input Fields] ................. White background, editable
├─ [Readonly Fields] .............. Gray background, non-editable
├─ [Result Labels] ................ Blue text (#004080), bold, font size 11
└─ [Section Headers] .............. Bold, LabelFrame titles

Spacing:
├─ Internal padding (pad variable): 6 pixels
├─ Top section to middle: 18 pixels (pad * 3)
├─ Middle to bottom: 18 pixels (pad * 3)
└─ Column padding: 6 pixels horizontal
```

---

**Visual Design Goals:**
- Symmetric two-column layout emphasizes dual-direction nature
- Clear section separation improves readability
- Color coding (blue results) draws attention to computed values
- LabelFrames group related parameters together

