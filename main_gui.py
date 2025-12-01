# main_gui.py

import tkinter as tk
from tkinter import ttk, messagebox

from vent_functions import (
    TunnelVentInputs,
    compute_all,
    JET_AREA_MAP,
)
# :contentReference[oaicite:0]{index=0}


class JetFanTab(ttk.Frame):
    """
    First tab: 'Number of Jet Fan'
    - V_kmh: selectable from [10, 20, 30, 40, 50, 60, 70, 80] (Un computed from this)
    - Qtreq, Ar, Lr, Dr: user-editable variables
    - Un (computed), Vr (computed), rho, xi, lamb, Ae, eta: constants (shown but not editable)
    - jet_diameter: dropdown based on JET_AREA_MAP keys
    - high_efficiency: dropdown (High efficiency / Standard)
    """

    def __init__(self, parent, result_tab=None):
        super().__init__(parent)
        self.result_tab = result_tab
        self._build_variables()
        self._build_layout()

    # ----------------------------
    # 1) Variables for widgets
    # ----------------------------
    def _build_variables(self):
        # V_kmh as a selectable value (combobox)
        self.v_kmh_var = tk.DoubleVar(value=10.0)   # set to least selectable 10 km/h

        # Variables the user can change
        self.qtreq_var = tk.DoubleVar(value=0.0)    # least value
        self.imax_var = tk.DoubleVar(value=0.0)     # maximum traffic flow [PCU/hr·lane]
        self.road_type_var = tk.IntVar(value=1)     # road type (1 or 2)
        self.lanes_var = tk.IntVar(value=1)         # number of lanes
        self.target_year_var = tk.IntVar(value=2022)  # target year
        self.ar_var = tk.DoubleVar(value=1.0)       # least positive area to avoid divide-by-zero
        self.lr_var = tk.DoubleVar(value=1.0)       # least positive length
        self.dr_var = tk.DoubleVar(value=1.0)       # least positive diameter to avoid divide-by-zero

        # Constants (shown but read-only)
        self.un_var = tk.DoubleVar(value=2.78)      # computed Un (initially for V_kmh=10)
        self.rho_var = tk.DoubleVar(value=1.2)      # constant rho
        self.xi_var = tk.DoubleVar(value=0.99)      # constant xi
        self.lamb_var = tk.DoubleVar(value=0.025)   # constant lamb
        self.ae_var = tk.DoubleVar(value=1.0751)    # constant Ae
        self.eta_var = tk.DoubleVar(value=0.95)     # constant eta

        # jet_diameter from JET_AREA_MAP keys
        jet_keys = sorted(JET_AREA_MAP.keys())
        self.jet_choices = [str(k) for k in jet_keys]
        # set to smallest available diameter
        smallest_jet = self.jet_choices[0]
        self.jet_diameter_var = tk.StringVar(value=smallest_jet)

        # high_efficiency dropdown (we'll map to bool)
        self.high_eff_choices = [
            "High efficiency (30 m/s)",   # True
            "Standard (34 m/s)",          # False
        ]
        # keep the first option (least discharge speed: High efficiency 30 m/s)
        self.high_eff_var = tk.StringVar(value=self.high_eff_choices[0])

        # a small label to show result on this tab
        self.result_var = tk.StringVar(value="")

    # ----------------------------
    # 2) Layout / widgets
    # ----------------------------
    def _build_layout(self):
        pad = 4

        # Left column: main variables
        row = 0

        ttk.Label(self, text="Driving speed V_kmh (km/h):").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        v_kmh_cb = ttk.Combobox(
            self,
            textvariable=self.v_kmh_var,
            values=[10, 20, 30, 40, 50, 60, 70, 80],
            state="readonly",
            width=10,
        )
        v_kmh_cb.bind("<<ComboboxSelected>>", self._on_vkmh_changed)
        v_kmh_cb.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        ttk.Label(self, text="Required ventilation Qtreq (m³/s):").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        ttk.Entry(self, textvariable=self.qtreq_var, width=12).grid(
            row=row, column=1, sticky="w", padx=pad, pady=pad
        )
        row += 1

        ttk.Label(self, text="Max traffic flow Imax (PCU/hr·lane):").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        ttk.Entry(self, textvariable=self.imax_var, width=12).grid(
            row=row, column=1, sticky="w", padx=pad, pady=pad
        )
        row += 1

        ttk.Label(self, text="Road type:").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        road_type_cb = ttk.Combobox(
            self,
            textvariable=self.road_type_var,
            values=["1 - National Road/Expressway", "2 - Downtown"],
            state="readonly",
            width=20,
        )
        road_type_cb.current(0)
        road_type_cb.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        ttk.Label(self, text="Number of lanes:").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        ttk.Entry(self, textvariable=self.lanes_var, width=12).grid(
            row=row, column=1, sticky="w", padx=pad, pady=pad
        )
        row += 1

        ttk.Label(self, text="Target year:").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        year_cb = ttk.Combobox(
            self,
            textvariable=self.target_year_var,
            values=list(range(2025, 2051)),
            state="readonly",
            width=10,
        )
        year_cb.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        ttk.Label(self, text="Tunnel cross-sectional area Ar (m²):").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        ttk.Entry(self, textvariable=self.ar_var, width=12).grid(
            row=row, column=1, sticky="w", padx=pad, pady=pad
        )
        row += 1

        ttk.Label(self, text="Tunnel length Lr (m):").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        ttk.Entry(self, textvariable=self.lr_var, width=12).grid(
            row=row, column=1, sticky="w", padx=pad, pady=pad
        )
        row += 1

        ttk.Label(self, text="Representative diameter Dr (m):").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        ttk.Entry(self, textvariable=self.dr_var, width=12).grid(
            row=row, column=1, sticky="w", padx=pad, pady=pad
        )
        row += 1

        ttk.Label(self, text="Jet fan diameter Φ (mm):").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        jet_cb = ttk.Combobox(
            self,
            textvariable=self.jet_diameter_var,
            values=self.jet_choices,
            state="readonly",
            width=12,
        )
        jet_cb.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        ttk.Label(self, text="Jet fan type:").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        eff_cb = ttk.Combobox(
            self,
            textvariable=self.high_eff_var,
            values=self.high_eff_choices,
            state="readonly",
            width=22,
        )
        eff_cb.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        # Separator
        ttk.Separator(self, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky="ew", pady=(pad * 2, pad)
        )
        row += 1

        # Right column: constants, displayed read-only
        ttk.Label(self, text="Natural wind speed Un (m/s) [computed]:").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        un_entry = ttk.Entry(self, textvariable=self.un_var, width=12, state="readonly")
        un_entry.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        ttk.Label(self, text="Air density ρ (kg/m³):").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        rho_entry = ttk.Entry(self, textvariable=self.rho_var, width=12, state="readonly")
        rho_entry.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        ttk.Label(self, text="Entrance loss ξ:").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        xi_entry = ttk.Entry(self, textvariable=self.xi_var, width=12, state="readonly")
        xi_entry.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        ttk.Label(self, text="Friction loss λ:").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        lamb_entry = ttk.Entry(self, textvariable=self.lamb_var, width=12, state="readonly")
        lamb_entry.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        ttk.Label(self, text="Equivalent resistance area Ae (m²):").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        ae_entry = ttk.Entry(self, textvariable=self.ae_var, width=12, state="readonly")
        ae_entry.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        ttk.Label(self, text="Jet fan efficiency η:").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        eta_entry = ttk.Entry(self, textvariable=self.eta_var, width=12, state="readonly")
        eta_entry.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        # Compute button + small result
        ttk.Button(self, text="Compute jet fan number", command=self._on_compute).grid(
            row=row, column=0, columnspan=2, pady=(pad * 2, pad)
        )
        row += 1

        ttk.Label(self, textvariable=self.result_var, foreground="blue").grid(
            row=row, column=0, columnspan=2, pady=(pad, pad)
        )

        # Make columns expand a bit
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    # ----------------------------
    # 3) Data extraction + compute
    # ----------------------------
    def _build_inputs_object(self) -> TunnelVentInputs:
        """Build TunnelVentInputs from the widget variables."""
        # Map high_eff dropdown to bool
        high_eff_str = self.high_eff_var.get()
        high_eff_bool = high_eff_str.startswith("High")

        # Extract road_type from dropdown (parse first character)
        road_type_str = str(self.road_type_var.get())
        if road_type_str.startswith("1"):
            road_type = 1
        elif road_type_str.startswith("2"):
            road_type = 2
        else:
            road_type = int(self.road_type_var.get())

        return TunnelVentInputs(
            V_kmh=float(self.v_kmh_var.get()),
            Qtreq=float(self.qtreq_var.get()),
            Imax=float(self.imax_var.get()),
            road_type=road_type,
            lanes=int(self.lanes_var.get()),
            Ar=float(self.ar_var.get()),
            Lr=float(self.lr_var.get()),
            rho=float(self.rho_var.get()),
            xi=float(self.xi_var.get()),
            lamb=float(self.lamb_var.get()),
            Dr=float(self.dr_var.get()),
            Ae=float(self.ae_var.get()),
            jet_diameter=int(self.jet_diameter_var.get()),
            high_efficiency=high_eff_bool,
            eta=float(self.eta_var.get()),
        )

    def _on_vkmh_changed(self, event=None):
        """Update Un when V_kmh changes."""
        from vent_functions import compute_Un
        v_kmh = float(self.v_kmh_var.get())
        un_value = compute_Un(v_kmh)
        self.un_var.set(un_value)

    def _on_compute(self):
        """Callback for 'Compute jet fan number' button."""
        try:
            inp = self._build_inputs_object()
            results = compute_all(inp)

            # Show summary in this tab
            self.result_var.set(
                f"Z_raw = {results.Z_raw}, Applied jet fans Z = {results.Z_applied}"
            )

            # Send detailed results to result tab if available
            if self.result_tab:
                self.result_tab.display_results(inp, results)

        except Exception as e:
            messagebox.showerror("Error", str(e))


class ResultsTab(ttk.Frame):
    """Tab to display detailed calculation results with formulas."""

    def __init__(self, parent):
        super().__init__(parent)
        self._build_layout()

    def _build_layout(self):
        # Create a scrollable text widget
        scroll_frame = ttk.Frame(self)
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side="right", fill="y")

        # Text widget for results
        self.text_widget = tk.Text(
            scroll_frame,
            wrap="word",
            yscrollcommand=scrollbar.set,
            font=("Courier New", 10),
            padx=10,
            pady=10
        )
        self.text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.text_widget.yview)

        # Configure tags for formatting
        self.text_widget.tag_configure("heading", font=("Courier New", 12, "bold"), foreground="#004080")
        self.text_widget.tag_configure("subheading", font=("Courier New", 10, "bold"), foreground="#006600")
        self.text_widget.tag_configure("formula", font=("Courier New", 9, "italic"), foreground="#800080")
        self.text_widget.tag_configure("result", font=("Courier New", 10, "bold"), foreground="#CC0000")

    def display_results(self, inp, results):
        """Display calculation results with formulas."""
        self.text_widget.config(state="normal")
        self.text_widget.delete(1.0, "end")

        # Header
        self._add_text("="*80 + "\n", "heading")
        self._add_text("TUNNEL VENTILATION CALCULATION RESULTS\n", "heading")
        self._add_text("="*80 + "\n\n", "heading")

        # Input parameters
        self._add_text("INPUT PARAMETERS\n", "subheading")
        self._add_text("-" * 80 + "\n")
        self._add_text(f"Driving speed V_kmh:              {inp.V_kmh} km/h\n")
        self._add_text(f"Required ventilation Qtreq:       {inp.Qtreq} m³/s\n")
        self._add_text(f"Natural wind speed Un (computed): {results.Un} m/s\n")
        self._add_text(f"Max traffic flow Imax:            {inp.Imax} PCU/hr·lane\n")
        self._add_text(f"Road type:                        {inp.road_type} ({'National Road/Expressway' if inp.road_type == 1 else 'Downtown'})\n")
        self._add_text(f"Number of lanes:                  {inp.lanes}\n")
        self._add_text(f"Tunnel cross-sectional area Ar:   {inp.Ar} m²\n")
        self._add_text(f"Tunnel length Lr:                 {inp.Lr} m\n")
        self._add_text(f"Air density ρ:                    {inp.rho} kg/m³\n")
        self._add_text(f"Entrance loss ξ:                  {inp.xi}\n")
        self._add_text(f"Friction loss λ:                  {inp.lamb}\n")
        self._add_text(f"Representative diameter Dr:       {inp.Dr} m\n")
        self._add_text(f"Equivalent resistance area Ae:    {inp.Ae} m²\n")
        self._add_text(f"Jet fan diameter Φ:               {inp.jet_diameter} mm\n")
        self._add_text(f"Jet fan type:                     {'High efficiency' if inp.high_efficiency else 'Standard'}\n")
        self._add_text(f"Jet fan efficiency η:             {inp.eta}\n\n")

        # Calculations
        self._add_text("CALCULATION STEPS\n", "subheading")
        self._add_text("="*80 + "\n\n")

        # 1. Vt
        self._add_text("1. Driving speed (Vt)\n", "subheading")
        self._add_text("   Formula: ", "formula")
        self._add_text("Vt = V_kmh / 3.6\n", "formula")
        self._add_text(f"   Calculation: Vt = {inp.V_kmh} / 3.6\n")
        self._add_text(f"   Result: ", "result")
        self._add_text(f"Vt = {results.Vt} m/s\n\n", "result")

        # 2. Vr
        self._add_text("2. Roadway wind speed (Vr)\n", "subheading")
        self._add_text("   Formula: ", "formula")
        self._add_text("Vr = Qtreq / Ar\n", "formula")
        self._add_text(f"   Calculation: Vr = {inp.Qtreq} / {inp.Ar}\n")
        self._add_text(f"   Result: ", "result")
        self._add_text(f"Vr = {results.Vr} m/s\n\n", "result")

        # 3. Un
        self._add_text("3. Natural wind speed (Un)\n", "subheading")
        self._add_text("   Formula: ", "formula")
        self._add_text("Un = Lookup from V_kmh table with interpolation\n", "formula")
        self._add_text(f"   V_kmh = {inp.V_kmh} km/h\n")
        self._add_text(f"   Result: ", "result")
        self._add_text(f"Un = {results.Un} m/s\n\n", "result")

        # 4. Aj
        self._add_text("4. Jet fan area (Aj)\n", "subheading")
        self._add_text("   Formula: ", "formula")
        self._add_text("Aj = Lookup from jet diameter map\n", "formula")
        self._add_text(f"   Jet diameter Φ = {inp.jet_diameter} mm\n")
        self._add_text(f"   Result: ", "result")
        self._add_text(f"Aj = {results.Aj} m²\n\n", "result")

        # 5. Vj
        self._add_text("5. Jet fan discharge speed (Vj)\n", "subheading")
        self._add_text("   Formula: ", "formula")
        self._add_text("Vj = 30 m/s (High efficiency) or 34 m/s (Standard)\n", "formula")
        self._add_text(f"   Type: {'High efficiency' if inp.high_efficiency else 'Standard'}\n")
        self._add_text(f"   Result: ", "result")
        self._add_text(f"Vj = {results.Vj} m/s\n\n", "result")

        # 6. n
        self._add_text("6. Number of vehicles in tunnel (n)\n", "subheading")
        self._add_text("   Formula: ", "formula")
        self._add_text("n = ROUND(traffic_volume × Lr / (3600 × Vt) + 0.4)\n", "formula")
        self._add_text(f"   Calculation: n = ROUND({inp.traffic_volume} × {inp.Lr} / (3600 × {results.Vt}) + 0.4)\n")
        self._add_text(f"   Result: ", "result")
        self._add_text(f"n = {results.n} vehicles\n\n", "result")

        # 7. Kj
        self._add_text("7. Jet fan pressure coefficient (Kj)\n", "subheading")
        self._add_text("   Formula: ", "formula")
        self._add_text("Kj = 0.99 (Vr<4), 0.92 (4≤Vr<8), 0.9 (Vr≥8)\n", "formula")
        self._add_text(f"   Vr = {results.Vr} m/s\n")
        self._add_text(f"   Result: ", "result")
        self._add_text(f"Kj = {results.Kj}\n\n", "result")

        # Common factor
        common_factor = (1 + inp.xi + inp.lamb * inp.Lr / inp.Dr) * inp.rho / 2.0
        self._add_text("Common factor for pressure calculations:\n", "subheading")
        self._add_text("   Formula: ", "formula")
        self._add_text("CF = (1 + ξ + λ × Lr / Dr) × ρ / 2 × (Qtreq/Ar)²\n", "formula")
        self._add_text(f"   Calculation: CF = (1 + {inp.xi} + {inp.lamb} × {inp.Lr} / {inp.Dr}) × {inp.rho} / 2 × ({inp.Qtreq}/{inp.Ar})²\n")
        self._add_text(f"   Result: ", "result")
        self._add_text(f"CF = {common_factor:.4f}\n\n", "result")

        # 8. Pr
        self._add_text("8. Roadway wind pressure loss (ΔPr)\n", "subheading")
        self._add_text("   Formula: ", "formula")
        self._add_text("ΔPr = CF\n", "formula")
        self._add_text(f"   Calculation: ΔPr = {common_factor:.4f}\n")
        self._add_text(f"   Result: ", "result")
        self._add_text(f"ΔPr = {results.Pr} Pa\n\n", "result")

        # 9. Pm
        self._add_text("9. Natural wind pressure loss (ΔPm)\n", "subheading")
        self._add_text("   Formula: ", "formula")
        self._add_text("ΔPm = CF × Un²\n", "formula")
        self._add_text(f"   Calculation: ΔPm = {common_factor:.4f} × {results.Un}²\n")
        self._add_text(f"   Result: ", "result")
        self._add_text(f"ΔPm = {results.Pm} Pa\n\n", "result")

        # 10. Pt
        self._add_text("10. Vehicle traffic pressure (ΔPt)\n", "subheading")
        self._add_text("   Formula: ", "formula")
        if results.Vt > results.Vr:
            self._add_text("ΔPt = (ρ/2) × (Ae/Ar) × n × (Vt-Vr)² (Vt>Vr)\n", "formula")
            self._add_text(f"   Calculation: ΔPt = ({inp.rho}/2) × ({inp.Ae}/{inp.Ar}) × {results.n} × ({results.Vt}-{results.Vr})²\n")
        else:
            self._add_text("ΔPt = -ρ/2 × Ae/Ar × n + (Vt-Vr)² (Vt<Vr)\n", "formula")
            self._add_text(f"   Calculation: ΔPt = -({inp.rho}/2) × ({inp.Ae}/{inp.Ar}) × {results.n} + ({results.Vt}-{results.Vr})²\n")
        self._add_text(f"   Result: ", "result")
        self._add_text(f"ΔPt = {results.Pt} Pa\n\n", "result")

        # 11. Pq
        self._add_text("11. Required pressure (ΔPq)\n", "subheading")
        self._add_text("    Formula: ", "formula")
        self._add_text("ΔPq = ΔPr + ΔPm - ΔPt\n", "formula")
        self._add_text(f"    Calculation: ΔPq = {results.Pr} + {results.Pm} - {results.Pt}\n")
        self._add_text(f"    Result: ", "result")
        self._add_text(f"ΔPq = {results.Pq} Pa\n\n", "result")

        # 12. Pj
        self._add_text("12. Jet fan pressure (ΔPj per fan)\n", "subheading")
        self._add_text("    Formula: ", "formula")
        self._add_text("ΔPj = Kj × ρ/2 × Vj² × (Aj/Ar) × (1 - Vr/Vj) × η\n", "formula")
        self._add_text(f"    Calculation: ΔPj = {results.Kj} × {inp.rho}/2 × {results.Vj}² × ({results.Aj}/{inp.Ar}) × (1 - {results.Vr}/{results.Vj}) × {inp.eta}\n")
        self._add_text(f"    Result: ", "result")
        self._add_text(f"ΔPj = {results.Pj} Pa\n\n", "result")

        # 13. Z_raw
        self._add_text("13. Required number of jet fans (Z_raw)\n", "subheading")
        self._add_text("    Formula: ", "formula")
        self._add_text("Z = ΔPq / ΔPj\n", "formula")
        self._add_text(f"    Calculation: Z = {results.Pq} / {results.Pj}\n")
        self._add_text(f"    Result: ", "result")
        self._add_text(f"Z_raw = {results.Z_raw}\n\n", "result")

        # 14. Z_applied
        self._add_text("14. Applied number of jet fans (Z_applied)\n", "subheading")
        self._add_text("    Formula: ", "formula")
        self._add_text("Z_applied = ROUND(Z_raw) if Z_raw > 0, else 0\n", "formula")
        self._add_text(f"    Calculation: Z_applied = ROUND({results.Z_raw})\n")
        self._add_text(f"    Result: ", "result")
        self._add_text(f"Z_applied = {results.Z_applied} fans\n\n", "result")

        # Final summary
        self._add_text("="*80 + "\n", "heading")
        self._add_text("FINAL RESULT\n", "heading")
        self._add_text("="*80 + "\n", "heading")
        self._add_text(f"Required jet fan count (calculated): {results.Z_raw}\n", "result")
        self._add_text(f"Applied jet fan count (rounded up): {results.Z_applied} fans\n\n", "result")

        self.text_widget.config(state="disabled")

    def _add_text(self, text, tag=None):
        """Helper to add text with optional tag."""
        if tag:
            self.text_widget.insert("end", text, tag)
        else:
            self.text_widget.insert("end", text)


class JetFanCalculatorWindow(tk.Toplevel):
    """Separate window for Jet Fan calculations."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Jet Fan Calculator")
        self.geometry("800x700")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # Create result tab first
        result_tab = ResultsTab(notebook)

        # First tab: Number of Jet Fan (pass result_tab reference)
        jet_fan_tab = JetFanTab(notebook, result_tab=result_tab)
        notebook.add(jet_fan_tab, text="Number of Jet Fan")

        # Results tab
        notebook.add(result_tab, text="Results (summary)")


# ----------------------------
# 4) Main menu window
# ----------------------------
class MainApp(tk.Tk):
    """Main menu to launch different ventilation calculation programs."""
    def __init__(self):
        super().__init__()
        self.title("Tunnel Ventilation System - Main Menu")
        self.geometry("600x400")
        
        self._build_menu()

    def _build_menu(self):
        # Title
        title_frame = ttk.Frame(self)
        title_frame.pack(pady=20)
        
        title_label = ttk.Label(
            title_frame,
            text="BEC Computational System",
            font=("Arial", 18, "bold"),
            foreground="#004080"
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Select a calculation module",
            font=("Arial", 11),
            foreground="#666666"
        )
        subtitle_label.pack(pady=5)

        # Separator
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20, pady=10)

        # Menu buttons frame
        menu_frame = ttk.Frame(self)
        menu_frame.pack(pady=20, padx=40, fill="both", expand=True)

        # Button style configuration
        button_width = 40
        button_padding = 10

        # 1. Jet Fan Calculator
        btn_jet_fan = ttk.Button(
            menu_frame,
            text="1. Jet Fan Calculator",
            command=self._open_jet_fan_calculator,
            width=button_width
        )
        btn_jet_fan.pack(pady=button_padding)

        # 2. Ventilation Shaft Calculator (placeholder)
        btn_shaft = ttk.Button(
            menu_frame,
            text="2. Ventilation Shaft Calculator (Coming Soon)",
            command=self._coming_soon,
            width=button_width,
            state="disabled"
        )
        btn_shaft.pack(pady=button_padding)

        # 3. Emergency Ventilation (placeholder)
        btn_emergency = ttk.Button(
            menu_frame,
            text="3. Emergency Ventilation Calculator (Coming Soon)",
            command=self._coming_soon,
            width=button_width,
            state="disabled"
        )
        btn_emergency.pack(pady=button_padding)

        # 4. Pressure Analysis (placeholder)
        btn_pressure = ttk.Button(
            menu_frame,
            text="4. Pressure Analysis (Coming Soon)",
            command=self._coming_soon,
            width=button_width,
            state="disabled"
        )
        btn_pressure.pack(pady=button_padding)

        # 5. Air Quality Analysis (placeholder)
        btn_air_quality = ttk.Button(
            menu_frame,
            text="5. Air Quality Analysis (Coming Soon)",
            command=self._coming_soon,
            width=button_width,
            state="disabled"
        )
        btn_air_quality.pack(pady=button_padding)

        # Separator
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20, pady=20)

        # Exit button
        btn_exit = ttk.Button(
            self,
            text="Exit",
            command=self.quit,
            width=15
        )
        btn_exit.pack(pady=10)

    def _open_jet_fan_calculator(self):
        """Open the Jet Fan Calculator window."""
        JetFanCalculatorWindow(self)

    def _coming_soon(self):
        """Placeholder for future modules."""
        messagebox.showinfo(
            "Coming Soon",
            "This module is under development and will be available in a future version."
        )


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
