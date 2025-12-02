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
# Ventilation Volume window and helper components
# ----------------------------
class SegmentsTableTransposed(ttk.Frame):
    """Placeholder for a segments table (direction-specific)."""
    def __init__(self, master, direction, segments, on_change, t, **kwargs):
        super().__init__(master, **kwargs)
        ttk.Label(self, text=f"Segments table ({direction})").pack(anchor="w", padx=4, pady=4)
        # Future: implement real editable segments table.


class TunnelGeometry(ttk.LabelFrame):
    """Geometry section with adjustable per-section inputs + Ar/Lp.

    Adds a transposed grid (rows: items; columns: Section 1..N) above the Ar/Lp inputs:
      - Tunnel gradient [%]
      - Tunnel length [m]
      - Number of lane(s) [N]

    Parameters:
      ar_var, lp_var: tk variables for Ar and Lp entries
      count_var: tk.IntVar controlling number of sections (columns)
      segments: list of dicts per section with keys: gradient, length, lanes
      on_segments_change: optional callback(direction, segments)
      on_ar_change, on_lp_change: callbacks for Ar/Lp changes
    """
    def __init__(self, master, ar_var, lp_var, count_var, segments, on_segments_change, on_ar_change, on_lp_change, t, **kwargs):
        super().__init__(master, text="Tunnel Geometry", **kwargs)

        self.count_var = count_var
        self.segments = segments
        self.on_segments_change = on_segments_change

        # Container for the transposed grid
        self.grid_frame = ttk.Frame(self)
        self.grid_frame.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=4, pady=(4, 8))

        # Build initial grid
        self._build_segments_grid()

        # Rebuild grid when section count changes
        self.count_var.trace_add("write", lambda *a: self._build_segments_grid())

        # Separator
        ttk.Separator(self, orient="horizontal").grid(row=1, column=0, columnspan=4, sticky="ew", pady=(2, 6))

        # Ar/Lp inputs
        ttk.Label(self, text="Tunnel Cross-Section Area [Ar]:").grid(row=2, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(self, textvariable=ar_var, width=10).grid(row=2, column=1, sticky="w", padx=4, pady=4)

        ttk.Label(self, text="Tunnel Perimeter [Lp]:").grid(row=3, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(self, textvariable=lp_var, width=10).grid(row=3, column=1, sticky="w", padx=4, pady=4)

        # Computed Dr = (4 * Ar) / Lp (read-only)
        self.dr_var = tk.DoubleVar(value=0.0)
        ttk.Label(self, text="Tunnel Representative Diameter [Dr] (m):").grid(row=4, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(self, textvariable=self.dr_var, width=14, state="readonly").grid(row=4, column=1, sticky="w", padx=4, pady=4)

        if on_ar_change is not None:
            ar_var.trace_add("write", lambda *args: on_ar_change(ar_var.get()))
        if on_lp_change is not None:
            lp_var.trace_add("write", lambda *args: on_lp_change(lp_var.get()))

        # Always recompute Dr when Ar or Lp changes
        ar_var.trace_add("write", lambda *args: self._recompute_dr(ar_var, lp_var))
        lp_var.trace_add("write", lambda *args: self._recompute_dr(ar_var, lp_var))

        # Initial Dr compute
        self._recompute_dr(ar_var, lp_var)

        # Keep label/entry columns anchored left; let a right filler stretch
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)

    def _recompute_dr(self, ar_var, lp_var):
        try:
            ar = float(ar_var.get())
        except Exception:
            ar = 0.0
        try:
            lp = float(lp_var.get())
        except Exception:
            lp = 0.0
        dr = (4.0 * ar / lp) if lp not in (0, 0.0) else 0.0
        self.dr_var.set(round(dr, 4))

    def _build_segments_grid(self):
        # Clear previous grid
        for w in self.grid_frame.winfo_children():
            w.destroy()

        n = self._safe_int(self.count_var.get(), 1)
        n = max(1, min(50, n))

        # Ensure segments storage size
        while len(self.segments) < n:
            self.segments.append({"gradient": 0.0, "length": 0.0, "lanes": 1})
        while len(self.segments) > n:
            self.segments.pop()

        header_style = {"padx": 6, "pady": 2}
        item_style = {"padx": 4, "pady": 2}

        # Header row: Item | Section 1 | Section 2 | ...
        ttk.Label(self.grid_frame, text="Item", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", **header_style)
        for i in range(n):
            ttk.Label(self.grid_frame, text=f"Sec. {i+1}", font=("Arial", 10, "bold")).grid(row=0, column=i+1, sticky="w", **header_style)

        # Rows: Gradient, Length, Lanes
        rows = [
            ("Tunnel gradient [%]", "gradient", tk.DoubleVar),
            ("Tunnel length [m]", "length", tk.DoubleVar),
            ("Number of lanes [N]", "lanes", tk.IntVar),
        ]

        # Keep strong refs to vars to prevent GC
        self._cell_vars = []

        for r_index, (label, key, VarType) in enumerate(rows, start=1):
            ttk.Label(self.grid_frame, text=label).grid(row=r_index, column=0, sticky="w", **item_style)
            row_vars = []
            for i in range(n):
                default = self.segments[i].get(key, 0 if key == "lanes" else 0.0)
                var = VarType(value=default)
                ent = ttk.Entry(self.grid_frame, textvariable=var, width=14)
                ent.grid(row=r_index, column=i+1, sticky="w", **item_style)

                # attach trace to update storage
                if key == "lanes":
                    var.trace_add("write", lambda *a, idx=i, v=var, k=key: self._update_segment(idx, k, self._sanitize_lanes(v.get())))
                else:
                    var.trace_add("write", lambda *a, idx=i, v=var, k=key: self._update_segment(idx, k, self._safe_float(v.get(), 0.0)))

                row_vars.append(var)
            self._cell_vars.append(row_vars)

        # Column weights: keep 'Item' fixed; let section columns stretch
        self.grid_frame.columnconfigure(0, weight=0)
        for c in range(1, n+1):
            self.grid_frame.columnconfigure(c, weight=1)

    def _update_segment(self, idx, key, value):
        if 0 <= idx < len(self.segments):
            self.segments[idx][key] = value
            if key == "lanes" and (not isinstance(value, int) or value < 1):
                self.segments[idx][key] = 1
        if callable(self.on_segments_change):
            try:
                self.on_segments_change("segments", self.segments)
            except Exception:
                pass

    @staticmethod
    def _safe_int(v, default=0):
        try:
            return int(v)
        except Exception:
            return default

    @staticmethod
    def _safe_float(v, default=0.0):
        try:
            return float(v)
        except Exception:
            return default

    @staticmethod
    def _sanitize_lanes(v):
        try:
            val = int(v)
        except Exception:
            val = 1
        return max(1, val)


class SummaryRow(ttk.Frame):
    """Displays provided stats and traffic dictionaries in two rows."""
    def __init__(self, master, stats, traffic, t, **kwargs):
        super().__init__(master, **kwargs)
        col = 0
        ttk.Label(self, text="Stats:", font=("Arial", 10, "bold")).grid(row=0, column=col, sticky="w", padx=4, pady=2)
        col += 1
        for key, value in stats.items():
            ttk.Label(self, text=f"{key}: {value}").grid(row=0, column=col, sticky="w", padx=4, pady=2)
            col += 1

        ttk.Label(self, text="Traffic:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", padx=4, pady=2)
        col = 1
        for key, value in traffic.items():
            ttk.Label(self, text=f"{key}: {value}").grid(row=1, column=col, sticky="w", padx=4, pady=2)
            col += 1


class VentilationVolumeWindow(tk.Toplevel):
    """Window implementing the 'Calculate Ventilation Volume' placeholder layout."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Calculate Ventilation Volume")
        self.geometry("900x600")

        # Translation-like dict
        t = {
            "dir1Title": "Masan → Jinju",
            "dir2Title": "Jinju → Masan",
            "numberOfSectionsLabel": "Number of sections",
            "averageElevationLabel": "Average elevation",
        }

        # State variables
        self.sectionCountMasanToJinju = tk.IntVar(value=10)
        self.sectionCountJinjuToMasan = tk.IntVar(value=10)
        self.avgElevationMasanToJinju = tk.DoubleVar(value=0.0)
        self.avgElevationJinjuToMasan = tk.DoubleVar(value=0.0)
        # Ventilation design speeds (80/100/120)
        self.designSpeedMasanToJinju = tk.IntVar(value=80)
        self.designSpeedJinjuToMasan = tk.IntVar(value=80)
        self.tunnelArMasanToJinju = tk.DoubleVar(value=0.0)
        self.tunnelLpMasanToJinju = tk.DoubleVar(value=0.0)
        self.tunnelArJinjuToMasan = tk.DoubleVar(value=0.0)
        self.tunnelLpJinjuToMasan = tk.DoubleVar(value=0.0)

        # Example data containers
        self.statsMasanToJinju = {"length_km": 0, "max_gradient": 0}
        self.statsJinjuToMasan = {"length_km": 0, "max_gradient": 0}
        self.trafficMasanToJinju = {"AADT": 0, "trucks_pct": 0}
        self.trafficJinjuToMasan = {"AADT": 0, "trucks_pct": 0}
        self.segmentsMasanToJinju = []
        self.segmentsJinjuToMasan = []

        def handleSectionCountChange(direction, value):
            try:
                v = int(value)
            except ValueError:
                return
            v = max(1, min(50, v))
            if direction == "MasanToJinju":
                self.sectionCountMasanToJinju.set(v)
            elif direction == "JinjuToMasan":
                self.sectionCountJinjuToMasan.set(v)

        # Geometry callbacks (placeholders)
        def onArChangeMasan(val):
            pass
        def onLpChangeMasan(val):
            pass
        def onArChangeJinju(val):
            pass
        def onLpChangeJinju(val):
            pass

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        card_padding = {"padx": 10, "pady": 10}

        # Direction 1 card
        card1 = ttk.Frame(main_frame, relief="raised", borderwidth=1)
        card1.pack(fill="x", **card_padding)
        header1 = ttk.Frame(card1)
        header1.pack(fill="x", pady=(0, 8))
        ttk.Label(header1, text=t["dir1Title"], font=("Arial", 14, "bold")).pack(side="left")
        controls1 = ttk.Frame(header1)
        controls1.pack(side="right")
        sections_group1 = ttk.Frame(controls1)
        sections_group1.pack(side="left", padx=8)
        ttk.Label(sections_group1, text=t["numberOfSectionsLabel"] + ":").pack(side="left")
        tk.Spinbox(
            sections_group1,
            from_=1,
            to=50,
            textvariable=self.sectionCountMasanToJinju,
            width=5,
            command=lambda: handleSectionCountChange("MasanToJinju", self.sectionCountMasanToJinju.get()),
        ).pack(side="left")
        elevation_group1 = ttk.Frame(controls1)
        elevation_group1.pack(side="left", padx=8)
        ttk.Label(elevation_group1, text=t["averageElevationLabel"] + ":").pack(side="left")
        ttk.Entry(elevation_group1, textvariable=self.avgElevationMasanToJinju, width=10).pack(side="left")

        # Ventilation Design Speed (80/100/120)
        speed_group1 = ttk.Frame(controls1)
        speed_group1.pack(side="left", padx=8)
        ttk.Label(speed_group1, text="Ventilation Design Speed:").pack(side="left")
        ttk.Combobox(
            speed_group1,
            textvariable=self.designSpeedMasanToJinju,
            values=[80, 100, 120],
            state="readonly",
            width=6,
        ).pack(side="left")
        SegmentsTableTransposed(card1, "MasanToJinju", self.segmentsMasanToJinju, None, t).pack(fill="x", pady=4)
        TunnelGeometry(
            card1,
            self.tunnelArMasanToJinju,
            self.tunnelLpMasanToJinju,
            self.sectionCountMasanToJinju,
            self.segmentsMasanToJinju,
            None,
            onArChangeMasan,
            onLpChangeMasan,
            t,
        ).pack(fill="x", pady=4)
        SummaryRow(card1, self.statsMasanToJinju, self.trafficMasanToJinju, t).pack(fill="x", pady=4)

        # Direction 2 card
        card2 = ttk.Frame(main_frame, relief="raised", borderwidth=1)
        card2.pack(fill="x", **card_padding)
        header2 = ttk.Frame(card2)
        header2.pack(fill="x", pady=(0, 8))
        ttk.Label(header2, text=t["dir2Title"], font=("Arial", 14, "bold")).pack(side="left")
        controls2 = ttk.Frame(header2)
        controls2.pack(side="right")
        sections_group2 = ttk.Frame(controls2)
        sections_group2.pack(side="left", padx=8)
        ttk.Label(sections_group2, text=t["numberOfSectionsLabel"] + ":").pack(side="left")
        tk.Spinbox(
            sections_group2,
            from_=1,
            to=50,
            textvariable=self.sectionCountJinjuToMasan,
            width=5,
            command=lambda: handleSectionCountChange("JinjuToMasan", self.sectionCountJinjuToMasan.get()),
        ).pack(side="left")
        elevation_group2 = ttk.Frame(controls2)
        elevation_group2.pack(side="left", padx=8)
        ttk.Label(elevation_group2, text=t["averageElevationLabel"] + ":").pack(side="left")
        ttk.Entry(elevation_group2, textvariable=self.avgElevationJinjuToMasan, width=10).pack(side="left")

        # Ventilation Design Speed (80/100/120)
        speed_group2 = ttk.Frame(controls2)
        speed_group2.pack(side="left", padx=8)
        ttk.Label(speed_group2, text="Ventilation Design Speed:").pack(side="left")
        ttk.Combobox(
            speed_group2,
            textvariable=self.designSpeedJinjuToMasan,
            values=[80, 100, 120],
            state="readonly",
            width=6,
        ).pack(side="left")
        SegmentsTableTransposed(card2, "JinjuToMasan", self.segmentsJinjuToMasan, None, t).pack(fill="x", pady=4)
        TunnelGeometry(
            card2,
            self.tunnelArJinjuToMasan,
            self.tunnelLpJinjuToMasan,
            self.sectionCountJinjuToMasan,
            self.segmentsJinjuToMasan,
            None,
            onArChangeJinju,
            onLpChangeJinju,
            t,
        ).pack(fill="x", pady=4)
        SummaryRow(card2, self.statsJinjuToMasan, self.trafficJinjuToMasan, t).pack(fill="x", pady=4)


# ----------------------------
# 4) Main menu window
# ----------------------------
class MainApp(tk.Tk):
    """Main menu to launch different ventilation calculation programs."""
    def __init__(self):
        super().__init__()
        self.title("BEC Computational System - Main Menu")
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

        # 1. Calculate Ventilation Volume (now placeholder)
        btn_volume = ttk.Button(
            menu_frame,
            text="1. Calculate Ventilation Volume",
            command=self._open_ventilation_volume,
            width=button_width
        )
        btn_volume.pack(pady=button_padding)

        # 2. Calculate Ventilation Capacity (Jet Fan)
        btn_jet_capacity = ttk.Button(
            menu_frame,
            text="2. Calculate Ventilation Capacity (Jet Fan)",
            command=self._open_jet_fan_calculator,
            width=button_width
        )
        btn_jet_capacity.pack(pady=button_padding)

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

    def _open_ventilation_volume(self):
        """Open the Ventilation Volume window."""
        VentilationVolumeWindow(self)

    def _coming_soon(self):
        """Placeholder for future modules."""
        messagebox.showinfo(
            "Coming Soon",
            "This module is under development and will be available in a future version."
        )


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
