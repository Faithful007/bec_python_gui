# main_gui.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

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

    def __init__(self, parent, result_tab=None, volume_tab=None):
        super().__init__(parent)
        self.result_tab = result_tab
        self.volume_tab = volume_tab
        self._build_variables()
        self._build_layout()
        self._wire_volume_sources()
        self._recompute_dynamic()

    # ----------------------------
    # 1) Variables for widgets
    # ----------------------------
    def _build_variables(self):
        # V_kmh as a selectable value (combobox)
        self.v_kmh_var = tk.DoubleVar(value=10.0)   # set to least selectable 10 km/h

        # Variables the user can change
        self.qtreq_var = tk.DoubleVar(value=0.0)    # least value
        self.lanes_var = tk.IntVar(value=1)         # number of lanes
        self.ar_var = tk.DoubleVar(value=1.0)       # least positive area to avoid divide-by-zero
        self.lr_var = tk.DoubleVar(value=1.0)       # total tunnel length (will be sourced)
        self.dr_var = tk.DoubleVar(value=1.0)       # least positive diameter to avoid divide-by-zero

        # Constants (shown but read-only)
        self.un_var = tk.DoubleVar(value=2.5)       # Un is constant for Jet Fan calc
        # Vt (m/s) from Vt_MAP using V_kmh; displayed as a constant here
        from vent_functions import Vt_MAP
        initial_key = int(self.v_kmh_var.get())
        self.vt_var = tk.DoubleVar(value=Vt_MAP.get(initial_key, Vt_MAP.get(10)))
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

        # dynamic labels for exact/approx results
        self.exact_z_var = tk.StringVar(value="-")
        self.approx_z_var = tk.StringVar(value="-")

        # Hidden variable for Imax (capacity per lane) sourced from Volume tab
        self.imax_var = tk.DoubleVar(value=0.0)

    # ----------------------------
    # 2) Layout / widgets
    # ----------------------------
    def _build_layout(self):
        # Create a container frame with padding
        container = ttk.Frame(self, padding="20 20 20 20")
        container.pack(fill="both", expand=True)
        
        pad = 6

        # Left column: main variables
        row = 0

        ttk.Label(container, text="Driving speed V_kmh (km/h):").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        v_kmh_cb = ttk.Combobox(
            container,
            textvariable=self.v_kmh_var,
            values=[10, 20, 30, 40, 50, 60, 70, 80],
            state="readonly",
            width=10,
        )
        v_kmh_cb.bind("<<ComboboxSelected>>", self._on_vkmh_changed)
        v_kmh_cb.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        ttk.Label(container, text="Required ventilation Qtreq (m³/s):").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        ttk.Entry(container, textvariable=self.qtreq_var, width=12).grid(
            row=row, column=1, sticky="w", padx=pad, pady=pad
        )
        row += 1

        ttk.Label(container, text="Number of lanes:").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        ttk.Entry(container, textvariable=self.lanes_var, width=12).grid(
            row=row, column=1, sticky="w", padx=pad, pady=pad
        )
        row += 1


        ttk.Label(container, text="Tunnel cross-sectional area Ar (m²):").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        ttk.Entry(container, textvariable=self.ar_var, width=12, state="readonly").grid(
            row=row, column=1, sticky="w", padx=pad, pady=pad
        )
        row += 1

        ttk.Label(container, text="Tunnel length Lr (m):").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        ttk.Entry(container, textvariable=self.lr_var, width=12, state="readonly").grid(
            row=row, column=1, sticky="w", padx=pad, pady=pad
        )
        row += 1

        ttk.Label(container, text="Representative diameter Dr (m):").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        ttk.Entry(container, textvariable=self.dr_var, width=12, state="readonly").grid(
            row=row, column=1, sticky="w", padx=pad, pady=pad
        )
        row += 1

        ttk.Label(container, text="Jet fan diameter Φ (mm):").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        jet_cb = ttk.Combobox(
            container,
            textvariable=self.jet_diameter_var,
            values=self.jet_choices,
            state="readonly",
            width=12,
        )
        jet_cb.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        ttk.Label(container, text="Jet fan type:").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        eff_cb = ttk.Combobox(
            container,
            textvariable=self.high_eff_var,
            values=self.high_eff_choices,
            state="readonly",
            width=22,
        )
        eff_cb.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        # Separator
        ttk.Separator(container, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky="ew", pady=(pad * 3, pad * 2)
        )
        row += 1

        # Right column: constants, displayed read-only
        ttk.Label(container, text="Natural wind speed Un (m/s) [computed]:").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        un_entry = ttk.Entry(container, textvariable=self.un_var, width=12, state="readonly")
        un_entry.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        ttk.Label(container, text="Driving speed Vt (m/s) [from map]:").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        vt_entry = ttk.Entry(container, textvariable=self.vt_var, width=12, state="readonly")
        vt_entry.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        ttk.Label(container, text="Air density ρ (kg/m³):").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        rho_entry = ttk.Entry(container, textvariable=self.rho_var, width=12, state="readonly")
        rho_entry.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        ttk.Label(container, text="Entrance loss ξ:").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        xi_entry = ttk.Entry(container, textvariable=self.xi_var, width=12, state="readonly")
        xi_entry.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        ttk.Label(container, text="Friction loss λ:").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        lamb_entry = ttk.Entry(container, textvariable=self.lamb_var, width=12, state="readonly")
        lamb_entry.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        ttk.Label(container, text="Equivalent resistance area Ae (m²):").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        ae_entry = ttk.Entry(container, textvariable=self.ae_var, width=12, state="readonly")
        ae_entry.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        ttk.Label(container, text="Jet fan efficiency η:").grid(
            row=row, column=0, sticky="e", padx=pad, pady=pad
        )
        eta_entry = ttk.Entry(container, textvariable=self.eta_var, width=12, state="readonly")
        eta_entry.grid(row=row, column=1, sticky="w", padx=pad, pady=pad)
        row += 1

        # Dynamic results labels
        ttk.Label(container, text="Exact number of Jet Fan Require =").grid(
            row=row, column=0, sticky="e", padx=pad, pady=(pad, 0)
        )
        ttk.Label(container, textvariable=self.exact_z_var, foreground="#004080").grid(
            row=row, column=1, sticky="w", padx=pad, pady=(pad, 0)
        )
        row += 1
        ttk.Label(container, text="Approximated Number of Jet Fan Require =").grid(
            row=row, column=0, sticky="e", padx=pad, pady=(0, pad)
        )
        ttk.Label(container, textvariable=self.approx_z_var, foreground="#004080").grid(
            row=row, column=1, sticky="w", padx=pad, pady=(0, pad)
        )

        # Make columns expand a bit
        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)

        # Traces for dynamic recompute
        # Traces update constants only; jet fan count computed on Summary click
        for var in [self.v_kmh_var, self.qtreq_var, self.lanes_var, self.rho_var, self.xi_var, self.lamb_var, self.ae_var, self.eta_var, self.jet_diameter_var, self.high_eff_var]:
            try:
                var.trace_add("write", lambda *a: self._recompute_dynamic())
            except Exception:
                pass

    # ----------------------------
    # 3) Data extraction + compute
    # ----------------------------
    def _build_inputs_object(self) -> TunnelVentInputs:
        """Build TunnelVentInputs from the widget variables."""
        # Map high_eff dropdown to bool
        high_eff_str = self.high_eff_var.get()
        high_eff_bool = high_eff_str.startswith("High")

        return TunnelVentInputs(
            V_kmh=float(self.v_kmh_var.get()),
            Qtreq=float(self.qtreq_var.get()),
            Imax=float(self.imax_var.get()),
            road_type=1,
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
        """Driving speed change: Un remains constant (2.5)."""
        self.un_var.set(2.5)
        # Update Vt based on map
        try:
            from vent_functions import Vt_MAP
            key = int(self.v_kmh_var.get())
            self.vt_var.set(Vt_MAP.get(key, Vt_MAP.get(10)))
        except Exception:
            pass
        self._recompute_dynamic()

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

    def _recompute_dynamic(self):
        # Do not compute jet fan count dynamically; only update constants
        self.exact_z_var.set("-")
        self.approx_z_var.set("-")
        self.result_var.set("")

    def _wire_volume_sources(self):
        if not self.volume_tab:
            return
        # Sync Ar, Lr, Dr from VentilationVolumeTab (Masan→Jinju by default)
        def sync(*_):
            try:
                params = self.volume_tab.get_params_for_jet(direction="MasanToJinju")
                volsum = self.volume_tab.get_volume_summary(direction="MasanToJinju")
                # Geometry
                self.ar_var.set(params.get("Ar", self.ar_var.get()))
                self.lr_var.set(params.get("Lr_m", self.lr_var.get()))
                self.dr_var.set(params.get("Dr", self.dr_var.get()))
                # Capacity and lanes (Imax is capacity per lane from volume tab)
                self.imax_var.set(volsum.get("cap_per_lane", self.imax_var.get()))
                # Default lanes from volume summary if available
                lanes_from_volume = volsum.get("lanes")
                if isinstance(lanes_from_volume, int) and lanes_from_volume >= 1:
                    self.lanes_var.set(lanes_from_volume)
                self._recompute_dynamic()
            except Exception:
                pass
        # Trace on Ar/Lp/total length vars
        try:
            self.volume_tab.tunnelArMasanToJinju.trace_add("write", sync)
            self.volume_tab.tunnelLpMasanToJinju.trace_add("write", sync)
            self.volume_tab.totalLengthMasanToJinju_m.trace_add("write", sync)
            # Also trace design speed to refresh capacity per lane (Imax)
            self.volume_tab.designSpeedMasanToJinju.trace_add("write", sync)
        except Exception:
            pass
        # Initial sync
        sync()

    def compute_and_publish(self):
        """Compute jet fan numbers and publish to the Results tab."""
        try:
            inp = self._build_inputs_object()
            results = compute_all(inp)
            self.exact_z_var.set(f"{results.Z_raw:.3f}")
            self.approx_z_var.set(f"{results.Z_applied}")
            if self.result_tab:
                self.result_tab.display_results(inp, results)
            return inp, results
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return None, None


class ResultsTab(ttk.Frame):
    """Tab to display detailed calculation results with formulas."""

    def __init__(self, parent):
        super().__init__(parent)
        self._build_layout()

    def _build_layout(self):
        # Create a scrollable text widget
        scroll_frame = ttk.Frame(self, padding="10 10 10 10")
        scroll_frame.pack(fill="both", expand=True)

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
        # Imax and road type inputs removed from UI; omitted from display
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
        self._add_text("Vt = Vt_MAP[V_kmh] (lookup)\n", "formula")
        self._add_text(f"   Selected V_kmh = {inp.V_kmh} km/h\n")
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
        self._add_text("Un = 2.5 (constant for Jet Fan calc)\n", "formula")
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
        self._add_text("n = ROUND(Q × lanes × Lr / (3600 × Vt) + 0.4)\n", "formula")
        self._add_text(f"   where Q is traffic flow computed from Imax = {inp.Imax} PCU/hr·lane\n")
        self._add_text(f"   Calculation: n = ROUND(Q × {inp.lanes} × {inp.Lr} / (3600 × {results.Vt}) + 0.4)\n")
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
        self._add_text("CF = (1 + ξ + λ × Lr / Dr) × ρ / 2\n", "formula")
        self._add_text(f"   Calculation: CF = (1 + {inp.xi} + {inp.lamb} × {inp.Lr} / {inp.Dr}) × {inp.rho} / 2\n")
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

    def append_volume_summary(self, volume_infos):
        """Append ventilation volume summaries. volume_infos: list of dicts."""
        self.text_widget.config(state="normal")
        self._add_text("\n" + "-"*80 + "\n", "heading")
        self._add_text("VENTILATION VOLUME SUMMARY\n", "heading")
        self._add_text("-"*80 + "\n\n")
        for info in volume_infos:
            self._add_text(f"Direction: {info.get('direction','')}\n", "subheading")
            self._add_text(f"Design speed: {info.get('design_speed', '')} km/h\n")
            self._add_text(f"Length: {info.get('length_km', info.get('Lr_m',0)/1000):.3f} km\n")
            self._add_text(f"Max gradient: {info.get('max_gradient', 0)} %\n")
            self._add_text(f"Lanes: {info.get('lanes', 1)}\n")
            self._add_text(f"Capacity per lane: {info.get('cap_per_lane', 0)} PCU/hr\n")
            self._add_text(f"Total capacity: {info.get('total_capacity', 0)} PCU/hr\n")
            self._add_text(f"Ar: {info.get('Ar', 0)} m², Lp: {info.get('Lp', 0)} m, Dr: {info.get('Dr', 0):.4f} m\n\n")
        self.text_widget.config(state="disabled")
    
    def append_traffic_summary(self, traffic_logic_masan_jinju, traffic_logic_jinju_masan):
        """Append traffic estimation summary for both directions."""
        self.text_widget.config(state="normal")
        self._add_text("\n" + "-"*80 + "\n", "heading")
        self._add_text("ESTIMATED TRAFFIC VOLUME SUMMARY\n", "heading")
        self._add_text("-"*80 + "\n\n")
        
        # Display Direction 1 (dynamically get names from parent)
        dir1_name = "Masan"
        dir2_name = "Jinju"
        try:
            # Try to get dynamic names from volume tab
            if hasattr(self.master, 'volume_tab'):
                dir1_name = self.master.volume_tab.dir1Name.get()
                dir2_name = self.master.volume_tab.dir2Name.get()
        except:
            pass
        self._add_text(f"Direction: {dir1_name} → {dir2_name}\n", "subheading")
        self._add_text("-"*60 + "\n")
        if not traffic_logic_masan_jinju.batch:
            self._add_text("No traffic data computed.\n\n")
        else:
            for entry in traffic_logic_masan_jinju.batch:
                if not entry.result:
                    continue
                res = entry.result
                inp = entry.inputs
                
                self._add_text(f"Year: {entry.year}\n", "subheading")
                self._add_text(f"  Passenger Vehicles:       {inp.passenger_aadt:,.0f}\n")
                self._add_text(f"    - Gasoline (60%):       {res.counts.get('passengerGasoline', 0):,.0f}\n")
                self._add_text(f"    - Diesel (40%):         {res.counts.get('passengerDiesel', 0):,.0f}\n")
                self._add_text(f"  Bus Small:                {inp.bus_small:,.0f}\n")
                self._add_text(f"  Bus Large:                {inp.bus_large:,.0f}\n")
                self._add_text(f"  Truck Small:              {inp.truck_small:,.0f}\n")
                self._add_text(f"  Truck Medium:             {inp.truck_medium:,.0f}\n")
                self._add_text(f"  Truck Large:              {inp.truck_large:,.0f}\n")
                self._add_text(f"  Truck Special:            {inp.truck_special:,.0f}\n")
                self._add_text(f"  Total AADT:               ", "result")
                self._add_text(f"{res.total_aadt:,.0f}\n", "result")
                self._add_text(f"  Heavy Vehicle Mix:        ", "result")
                self._add_text(f"{res.heavy_vehicle_mix_pt:.2f}%\n\n", "result")
        
        # Display Jinju → Masan
        self._add_text(f"\nDirection: {dir2_name} → {dir1_name}\n", "subheading")
        self._add_text("-"*60 + "\n")
        if not traffic_logic_jinju_masan.batch:
            self._add_text("No traffic data computed.\n\n")
        else:
            for entry in traffic_logic_jinju_masan.batch:
                if not entry.result:
                    continue
                res = entry.result
                inp = entry.inputs
                
                self._add_text(f"Year: {entry.year}\n", "subheading")
                self._add_text(f"  Passenger Vehicles:       {inp.passenger_aadt:,.0f}\n")
                self._add_text(f"    - Gasoline (60%):       {res.counts.get('passengerGasoline', 0):,.0f}\n")
                self._add_text(f"    - Diesel (40%):         {res.counts.get('passengerDiesel', 0):,.0f}\n")
                self._add_text(f"  Bus Small:                {inp.bus_small:,.0f}\n")
                self._add_text(f"  Bus Large:                {inp.bus_large:,.0f}\n")
                self._add_text(f"  Truck Small:              {inp.truck_small:,.0f}\n")
                self._add_text(f"  Truck Medium:             {inp.truck_medium:,.0f}\n")
                self._add_text(f"  Truck Large:              {inp.truck_large:,.0f}\n")
                self._add_text(f"  Truck Special:            {inp.truck_special:,.0f}\n")
                self._add_text(f"  Total AADT:               ", "result")
                self._add_text(f"{res.total_aadt:,.0f}\n", "result")
                self._add_text(f"  Heavy Vehicle Mix:        ", "result")
                self._add_text(f"{res.heavy_vehicle_mix_pt:.2f}%\n\n", "result")
        
        self.text_widget.config(state="disabled")


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
    """Displays provided stats and traffic dictionaries in two rows and allows refresh."""
    def __init__(self, master, stats, traffic, t, **kwargs):
        super().__init__(master, **kwargs)
        self._stats = stats
        self._traffic = traffic
        self._stat_labels = {}
        self._traffic_labels = {}

        col = 0
        ttk.Label(self, text="Stats:", font=("Arial", 10, "bold")).grid(row=0, column=col, sticky="w", padx=4, pady=2)
        col += 1
        for key, value in self._stats.items():
            lbl = ttk.Label(self, text=f"{key}: {value}")
            lbl.grid(row=0, column=col, sticky="w", padx=4, pady=2)
            self._stat_labels[key] = lbl
            col += 1

        ttk.Label(self, text="Traffic:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", padx=4, pady=2)
        col = 1
        for key, value in self._traffic.items():
            lbl = ttk.Label(self, text=f"{key}: {value}")
            lbl.grid(row=1, column=col, sticky="w", padx=4, pady=2)
            self._traffic_labels[key] = lbl
            col += 1

    def set_data(self, stats=None, traffic=None):
        if stats is not None:
            self._stats.update(stats)
            for key, value in stats.items():
                if key in self._stat_labels:
                    self._stat_labels[key].configure(text=f"{key}: {value}")
        if traffic is not None:
            self._traffic.update(traffic)
            for key, value in traffic.items():
                if key in self._traffic_labels:
                    self._traffic_labels[key].configure(text=f"{key}: {value}")


class VentilationVolumeTab(ttk.Frame):
    """Tab for Calculate Ventilation Volume functionality."""
    def __init__(self, parent):
        super().__init__(parent)
        self._build_interface()

    def _build_interface(self):
        # Speed capacity per lane table (PCU/hr·lane)
        self.SPEED_CAPACITY_TABLE = {80: 2000, 100: 2200, 120: 2300}

        # Direction name variables (editable)
        self.dir1Name = tk.StringVar(value="FROM")
        self.dir2Name = tk.StringVar(value="TO")

        # Translation-like dict
        t = {
            "dir1Title": self.dir1Name,
            "dir2Title": self.dir2Name,
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
        # Total length by direction (m)
        self.totalLengthMasanToJinju_m = tk.DoubleVar(value=0.0)
        self.totalLengthJinjuToMasan_m = tk.DoubleVar(value=0.0)
        
        # Road type for traffic flow calculation (1=National/Expressway, 2=Downtown)
        self.roadTypeMasanToJinju = tk.StringVar(value="1 - National/Expressway (K=150)")
        self.roadTypeJinjuToMasan = tk.StringVar(value="1 - National/Expressway (K=150)")

        # Example data containers
        self.statsMasanToJinju = {"length_km": 0.0, "max_gradient": 0.0, "lanes": 1, "cap_per_lane": 0, "total_capacity": 0}
        self.statsJinjuToMasan = {"length_km": 0.0, "max_gradient": 0.0, "lanes": 1, "cap_per_lane": 0, "total_capacity": 0}
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
                self._update_summary("MasanToJinju")
            elif direction == "JinjuToMasan":
                self.sectionCountJinjuToMasan.set(v)
                self._update_summary("JinjuToMasan")

        # Geometry callbacks (placeholders)
        def onArChangeMasan(val):
            pass
        def onLpChangeMasan(val):
            pass
        def onArChangeJinju(val):
            pass
        def onLpChangeJinju(val):
            pass

        # Create scrollable frame
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        card_padding = {"padx": 15, "pady": 10}

        # Direction 1 card
        card1 = ttk.Frame(scrollable_frame, relief="raised", borderwidth=1, padding="10 10 10 10")
        card1.pack(fill="x", **card_padding)
        header1 = ttk.Frame(card1)
        header1.pack(fill="x", pady=(0, 10))
        
        # Editable direction name
        dir_name_frame1 = ttk.Frame(header1)
        dir_name_frame1.pack(side="left", padx=(0, 10))
        ttk.Entry(dir_name_frame1, textvariable=self.dir1Name, width=15, font=("Arial", 14, "bold")).pack(side="left", padx=(0, 5))
        ttk.Label(dir_name_frame1, text="→", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 5))
        ttk.Entry(dir_name_frame1, textvariable=self.dir2Name, width=15, font=("Arial", 14, "bold")).pack(side="left")
        controls1 = ttk.Frame(header1)
        controls1.pack(side="right", padx=(10, 0))
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
        SegmentsTableTransposed(card1, "MasanToJinju", self.segmentsMasanToJinju, lambda *_: self._update_summary("MasanToJinju"), t).pack(fill="x", pady=4)
        TunnelGeometry(
            card1,
            self.tunnelArMasanToJinju,
            self.tunnelLpMasanToJinju,
            self.sectionCountMasanToJinju,
            self.segmentsMasanToJinju,
            lambda *a: self._update_summary("MasanToJinju"),
            onArChangeMasan,
            onLpChangeMasan,
            t,
        ).pack(fill="x", pady=4)
        self.summaryRowMasanToJinju = SummaryRow(card1, self.statsMasanToJinju, self.trafficMasanToJinju, t)
        self.summaryRowMasanToJinju.pack(fill="x", pady=4)

        # Direction 2 card
        card2 = ttk.Frame(scrollable_frame, relief="raised", borderwidth=1, padding="10 10 10 10")
        card2.pack(fill="x", **card_padding)
        header2 = ttk.Frame(card2)
        header2.pack(fill="x", pady=(0, 10))
        
        # Editable direction name (reverse order)
        dir_name_frame2 = ttk.Frame(header2)
        dir_name_frame2.pack(side="left", padx=(0, 10))
        ttk.Entry(dir_name_frame2, textvariable=self.dir2Name, width=15, font=("Arial", 14, "bold")).pack(side="left", padx=(0, 5))
        ttk.Label(dir_name_frame2, text="→", font=("Arial", 14, "bold")).pack(side="left", padx=(0, 5))
        ttk.Entry(dir_name_frame2, textvariable=self.dir1Name, width=15, font=("Arial", 14, "bold")).pack(side="left")
        controls2 = ttk.Frame(header2)
        controls2.pack(side="right", padx=(10, 0))
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
        SegmentsTableTransposed(card2, "JinjuToMasan", self.segmentsJinjuToMasan, lambda *_: self._update_summary("JinjuToMasan"), t).pack(fill="x", pady=4)
        TunnelGeometry(
            card2,
            self.tunnelArJinjuToMasan,
            self.tunnelLpJinjuToMasan,
            self.sectionCountJinjuToMasan,
            self.segmentsJinjuToMasan,
            lambda *a: self._update_summary("JinjuToMasan"),
            onArChangeJinju,
            onLpChangeJinju,
            t,
        ).pack(fill="x", pady=4)
        self.summaryRowJinjuToMasan = SummaryRow(card2, self.statsJinjuToMasan, self.trafficJinjuToMasan, t)
        self.summaryRowJinjuToMasan.pack(fill="x", pady=4)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Store references to traffic card frames for later updates
        self.traffic_card1_frame = None
        self.traffic_card2_frame = None
        
        # Trace design speed changes to refresh summary
        self.designSpeedMasanToJinju.trace_add("write", lambda *a: self._update_summary("MasanToJinju"))
        self.designSpeedJinjuToMasan.trace_add("write", lambda *a: self._update_summary("JinjuToMasan"))

        # Trace direction name changes to update traffic panel labels
        self.dir1Name.trace_add("write", lambda *a: self._update_traffic_labels())
        self.dir2Name.trace_add("write", lambda *a: self._update_traffic_labels())

        # Initial compute
        self._update_summary("MasanToJinju")
        self._update_summary("JinjuToMasan")

        # Add traffic estimation panel after direction cards
        self._add_traffic_estimation_panel(scrollable_frame)

    def _update_summary(self, direction):
        if direction == "MasanToJinju":
            segments = self.segmentsMasanToJinju
            design_speed = int(self.designSpeedMasanToJinju.get())
            stats = self.statsMasanToJinju
            row = self.summaryRowMasanToJinju
            count = int(self.sectionCountMasanToJinju.get())
        else:
            segments = self.segmentsJinjuToMasan
            design_speed = int(self.designSpeedJinjuToMasan.get())
            stats = self.statsJinjuToMasan
            row = self.summaryRowJinjuToMasan
            count = int(self.sectionCountJinjuToMasan.get())

        # Ensure segment list has desired size
        while len(segments) < max(1, count):
            segments.append({"gradient": 0.0, "length": 0.0, "lanes": 1})
        if len(segments) > count:
            segments[:] = segments[:count]

        total_length_m = sum(float(s.get("length", 0.0) or 0.0) for s in segments)
        max_gradient = max(float(s.get("gradient", 0.0) or 0.0) for s in segments) if segments else 0.0
        max_lanes = max(int(s.get("lanes", 1) or 1) for s in segments) if segments else 1

        cap_per_lane = self.SPEED_CAPACITY_TABLE.get(design_speed, 2000)
        total_capacity = cap_per_lane * max_lanes

        stats_update = {
            "length_km": round(total_length_m / 1000.0, 3),
            "max_gradient": round(max_gradient, 2),
            "lanes": max_lanes,
            "cap_per_lane": cap_per_lane,
            "total_capacity": total_capacity,
        }

        stats.update(stats_update)
        row.set_data(stats=stats_update)
        # update total length variable for external consumers
        if direction == "MasanToJinju":
            self.totalLengthMasanToJinju_m.set(total_length_m)
        else:
            self.totalLengthJinjuToMasan_m.set(total_length_m)

    def get_params_for_jet(self, direction="MasanToJinju"):
        if direction == "MasanToJinju":
            Ar = float(self.tunnelArMasanToJinju.get())
            Lp = float(self.tunnelLpMasanToJinju.get())
            Lr_m = float(self.totalLengthMasanToJinju_m.get())
        else:
            Ar = float(self.tunnelArJinjuToMasan.get())
            Lp = float(self.tunnelLpJinjuToMasan.get())
            Lr_m = float(self.totalLengthJinjuToMasan_m.get())
        Dr = (4.0 * Ar / Lp) if Lp not in (0, 0.0) else 0.0
        return {"Ar": Ar, "Lp": Lp, "Lr_m": Lr_m, "Dr": Dr}

    def get_volume_summary(self, direction="MasanToJinju"):
        if direction == "MasanToJinju":
            stats = dict(self.statsMasanToJinju)
            design_speed = int(self.designSpeedMasanToJinju.get())
            params = self.get_params_for_jet(direction)
            dir_label = f"{self.dir1Name.get()} → {self.dir2Name.get()}"
        else:
            stats = dict(self.statsJinjuToMasan)
            design_speed = int(self.designSpeedJinjuToMasan.get())
            params = self.get_params_for_jet(direction)
            dir_label = f"{self.dir2Name.get()} → {self.dir1Name.get()}"
        stats.update({
            "direction": dir_label,
            "design_speed": design_speed,
            "Ar": params["Ar"],
            "Lp": params["Lp"],
            "Dr": params["Dr"],
            "Lr_m": params["Lr_m"],
        })
        return stats

    def _update_traffic_labels(self):
        """Update traffic panel labels when direction names change."""
        dir1_name = self.dir1Name.get()
        dir2_name = self.dir2Name.get()
        
        # Update traffic card labels if they exist
        if hasattr(self, 'traffic_card1_label'):
            self.traffic_card1_label.config(text=f"{dir1_name} → {dir2_name}")
        if hasattr(self, 'traffic_card2_label'):
            self.traffic_card2_label.config(text=f"{dir2_name} → {dir1_name}")
        
        # Update logic direction labels
        if hasattr(self, 'traffic_logic_masan_jinju'):
            self.traffic_logic_masan_jinju.direction = f"{dir1_name} → {dir2_name}"
        if hasattr(self, 'traffic_logic_jinju_masan'):
            self.traffic_logic_jinju_masan.direction = f"{dir2_name} → {dir1_name}"

    def _add_traffic_estimation_panel(self, parent):
        """Add traffic estimation module panels for both directions."""
        from traffic_estimation_module import TrafficEstimationLogic

        # Get dynamic direction names
        dir1_name = self.dir1Name.get()
        dir2_name = self.dir2Name.get()
        
        # Initialize traffic estimation logic for both directions
        self.traffic_logic_masan_jinju = TrafficEstimationLogic(direction=f"{dir1_name} → {dir2_name}")
        self.traffic_logic_jinju_masan = TrafficEstimationLogic(direction=f"{dir2_name} → {dir1_name}")
        self.traffic_rows_masan_jinju = []
        self.traffic_rows_jinju_masan = []

        # Create Direction 1 card
        self._create_direction_traffic_card(
            parent, 
            f"{dir1_name} → {dir2_name}", 
            "masan_jinju",
            self.traffic_logic_masan_jinju,
            self.traffic_rows_masan_jinju
        )

        # Create Direction 2 card
        self._create_direction_traffic_card(
            parent, 
            f"{dir2_name} → {dir1_name}", 
            "jinju_masan",
            self.traffic_logic_jinju_masan,
            self.traffic_rows_jinju_masan
        )

    def _create_direction_traffic_card(self, parent, direction_title, direction_key, traffic_logic, traffic_rows_list):
        """Create a traffic estimation card for a specific direction."""
        # Create card for traffic estimation
        traffic_card = ttk.Frame(parent, relief="raised", borderwidth=1, padding="10 10 10 10")
        traffic_card.pack(fill="x", padx=15, pady=10)

        # Header
        header = ttk.Frame(traffic_card)
        header.pack(fill="x", pady=(0, 10))
        
        # Main title
        ttk.Label(header, text="Estimated Traffic Volume", font=("Arial", 14, "bold")).pack(anchor="w")
        
        # Direction label (editable via parent variables)
        header_label = ttk.Label(header, text=f"{direction_title}", font=("Arial", 12))
        header_label.pack(anchor="w", pady=(2, 0))
        
        # Store reference to label for updates
        if direction_key == "masan_jinju":
            self.traffic_card1_label = header_label
        else:
            self.traffic_card2_label = header_label

        # Input frame for AADT values
        input_frame = ttk.LabelFrame(traffic_card, text="AADT Input (Annual Average Daily Traffic)", padding="10 10 10 10")
        input_frame.pack(fill="x", pady=5)

        # Create scrollable frame for rows
        canvas = tk.Canvas(input_frame, height=200)
        scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=canvas.yview)
        traffic_rows_frame = ttk.Frame(canvas)

        traffic_rows_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=traffic_rows_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Store references based on direction
        if direction_key == "masan_jinju":
            self.traffic_rows_frame_masan_jinju = traffic_rows_frame
        else:
            self.traffic_rows_frame_jinju_masan = traffic_rows_frame

        # Header row with column labels
        header_labels = ["Year", "Passenger Vehicles", "Bus Small", "Bus Large", "Truck Small", "Truck Medium", "Truck Large", "Truck Special", "Action"]
        for col, label in enumerate(header_labels):
            ttk.Label(traffic_rows_frame, text=label, font=("Arial", 9, "bold")).grid(row=0, column=col, padx=5, pady=5, sticky="w")

        # Add Row button
        add_row_btn_frame = ttk.Frame(traffic_card)
        add_row_btn_frame.pack(fill="x", pady=5)
        ttk.Button(add_row_btn_frame, text="+ Add Row", command=lambda: self._add_traffic_row(direction_key)).pack(side="left", padx=5)

        # Add first row by default
        self._add_traffic_row(direction_key)

        # Buttons frame
        button_frame = ttk.Frame(traffic_card)
        button_frame.pack(fill="x", pady=5)

        ttk.Button(button_frame, text="Import CSV", command=lambda: self._import_traffic_csv(direction_key)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Compute All", command=lambda: self._compute_all_traffic(direction_key)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Export CSV", command=lambda: self._export_traffic_csv(direction_key)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Export PDF", command=lambda: self._export_traffic_pdf(direction_key)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear All", command=lambda: self._clear_traffic(direction_key)).pack(side="left", padx=5)

        # Traffic Density Table (collapsible)
        density_frame = ttk.Frame(traffic_card)
        density_frame.pack(fill="x", pady=5)
        
        # Control row with toggle button and road type selector
        density_control_frame = ttk.Frame(density_frame)
        density_control_frame.pack(fill="x", padx=5, pady=2)
        
        # Toggle button for density table
        density_visible = tk.BooleanVar(value=False)
        toggle_btn = ttk.Button(
            density_control_frame, 
            text="▶ Show Traffic Density Table",
            command=lambda: self._toggle_density_table(direction_key, density_visible, toggle_btn, density_table_frame)
        )
        toggle_btn.pack(side="left", padx=(0, 10))
        
        # Road Type selector next to toggle button
        ttk.Label(density_control_frame, text="Road Type:").pack(side="left", padx=(0, 5))
        road_type_var = self.roadTypeMasanToJinju if direction_key == "masan_jinju" else self.roadTypeJinjuToMasan
        road_type_combo = ttk.Combobox(
            density_control_frame,
            textvariable=road_type_var,
            values=["1 - National/Expressway (K=150)", "2 - Downtown (K=165)"],
            state="readonly",
            width=25,
        )
        road_type_combo.pack(side="left")
        
        # Trace road type changes to auto-update table if visible
        def on_road_type_change(*args):
            if density_visible.get():
                self._populate_density_table(direction_key)
        road_type_var.trace_add("write", on_road_type_change)
        
        # Collapsible density table frame
        density_table_frame = ttk.Frame(density_frame)
        # Don't pack initially (hidden by default)
        
        # Create table with headers
        headers = ["Speed\n(km/h)", "Flow Q\n(PCU/hr·lane)", "Density k\n(PCU/km·lane)", "K_lim-1", "k/K_lim-1"]
        for col, header in enumerate(headers):
            ttk.Label(density_table_frame, text=header, font=("Arial", 9, "bold"), borderwidth=1, relief="solid", padding=5).grid(row=0, column=col, sticky="nsew")
        
        # Store reference to populate later
        if direction_key == "masan_jinju":
            self.density_table_frame_masan_jinju = density_table_frame
            self.density_visible_masan_jinju = density_visible
        else:
            self.density_table_frame_jinju_masan = density_table_frame
            self.density_visible_jinju_masan = density_visible

        # Results frame
        results_frame = ttk.LabelFrame(traffic_card, text="Traffic Estimation Results", padding="10 10 10 10")
        results_frame.pack(fill="both", expand=True, pady=5)

        # Results text widget
        result_scroll = ttk.Scrollbar(results_frame)
        result_scroll.pack(side="right", fill="y")

        traffic_result_text = tk.Text(results_frame, wrap="word", height=10, yscrollcommand=result_scroll.set, font=("Courier New", 9))
        traffic_result_text.pack(side="left", fill="both", expand=True)
        result_scroll.config(command=traffic_result_text.yview)

        # Store text widget reference
        if direction_key == "masan_jinju":
            self.traffic_result_text_masan_jinju = traffic_result_text
        else:
            self.traffic_result_text_jinju_masan = traffic_result_text

    def _toggle_density_table(self, direction_key, visible_var, toggle_btn, table_frame):
        """Toggle visibility of traffic density table."""
        is_visible = visible_var.get()
        
        if is_visible:
            # Hide table
            table_frame.pack_forget()
            toggle_btn.config(text="▶ Show Traffic Density Table")
            visible_var.set(False)
        else:
            # Show and populate table
            table_frame.pack(fill="x", pady=5)
            toggle_btn.config(text="▼ Hide Traffic Density Table")
            visible_var.set(True)
            self._populate_density_table(direction_key)

    def _populate_density_table(self, direction_key):
        """Populate the traffic density table with current parameters."""
        from vent_functions import build_traffic_density_table
        
        # Get table frame
        if direction_key == "masan_jinju":
            table_frame = self.density_table_frame_masan_jinju
            design_speed = int(self.designSpeedMasanToJinju.get())
        else:
            table_frame = self.density_table_frame_jinju_masan
            design_speed = int(self.designSpeedJinjuToMasan.get())
        
        # Get current parameters from volume summary
        volume_summary = self.get_volume_summary(direction="MasanToJinju" if direction_key == "masan_jinju" else "JinjuToMasan")
        Imax = volume_summary.get("cap_per_lane", 2000)
        
        # Get road_type from user selection (extract integer from string like "1 - National/...")
        if direction_key == "masan_jinju":
            road_type_str = str(self.roadTypeMasanToJinju.get())
        else:
            road_type_str = str(self.roadTypeJinjuToMasan.get())
        
        # Parse the integer from the string (handle both "1" and "1 - National/...")
        try:
            road_type = int(road_type_str.split()[0]) if ' ' in road_type_str else int(road_type_str)
        except (ValueError, AttributeError):
            road_type = 1  # Default to National/Expressway
        
        # Build density table
        density_rows = build_traffic_density_table(Imax, road_type)
        
        # Clear existing data rows (keep header row 0)
        for widget in table_frame.grid_slaves():
            row = widget.grid_info().get('row', 0)
            if row > 0:
                widget.destroy()
        
        # Populate data rows
        for idx, row_data in enumerate(density_rows, start=1):
            ttk.Label(table_frame, text=f"{row_data.speed_kmh:.0f}", borderwidth=1, relief="solid", padding=5).grid(row=idx, column=0, sticky="nsew")
            ttk.Label(table_frame, text=f"{row_data.flow_pcu_per_hr_lane}", borderwidth=1, relief="solid", padding=5).grid(row=idx, column=1, sticky="nsew")
            ttk.Label(table_frame, text=f"{row_data.density_pcu_per_km_lane:.3f}", borderwidth=1, relief="solid", padding=5).grid(row=idx, column=2, sticky="nsew")
            ttk.Label(table_frame, text=f"{row_data.k_lim1:.3f}", borderwidth=1, relief="solid", padding=5).grid(row=idx, column=3, sticky="nsew")
            ttk.Label(table_frame, text=f"{row_data.density_to_limit_ratio:.3f}", borderwidth=1, relief="solid", padding=5).grid(row=idx, column=4, sticky="nsew")

    def _add_traffic_row(self, direction_key):
        """Add a new row for traffic input."""
        rows_frame = self.traffic_rows_frame_masan_jinju if direction_key == "masan_jinju" else self.traffic_rows_frame_jinju_masan
        rows_list = self.traffic_rows_masan_jinju if direction_key == "masan_jinju" else self.traffic_rows_jinju_masan
        
        row_num = len(rows_list) + 1
        
        # Create variables for this row
        row_vars = {
            'year': tk.IntVar(value=2024),
            'passenger_vehicles': tk.DoubleVar(value=0.0),
            'bus_small': tk.DoubleVar(value=0.0),
            'bus_large': tk.DoubleVar(value=0.0),
            'truck_small': tk.DoubleVar(value=0.0),
            'truck_medium': tk.DoubleVar(value=0.0),
            'truck_large': tk.DoubleVar(value=0.0),
            'truck_special': tk.DoubleVar(value=0.0),
        }
        
        # Create entries
        entries = []
        entry_year = ttk.Entry(rows_frame, textvariable=row_vars['year'], width=8)
        entry_year.grid(row=row_num, column=0, padx=5, pady=2)
        entries.append(entry_year)
        
        entry_pv = ttk.Entry(rows_frame, textvariable=row_vars['passenger_vehicles'], width=10)
        entry_pv.grid(row=row_num, column=1, padx=5, pady=2)
        entries.append(entry_pv)
        
        entry_bs = ttk.Entry(rows_frame, textvariable=row_vars['bus_small'], width=10)
        entry_bs.grid(row=row_num, column=2, padx=5, pady=2)
        entries.append(entry_bs)
        
        entry_bl = ttk.Entry(rows_frame, textvariable=row_vars['bus_large'], width=10)
        entry_bl.grid(row=row_num, column=3, padx=5, pady=2)
        entries.append(entry_bl)
        
        entry_ts = ttk.Entry(rows_frame, textvariable=row_vars['truck_small'], width=10)
        entry_ts.grid(row=row_num, column=4, padx=5, pady=2)
        entries.append(entry_ts)
        
        entry_tm = ttk.Entry(rows_frame, textvariable=row_vars['truck_medium'], width=10)
        entry_tm.grid(row=row_num, column=5, padx=5, pady=2)
        entries.append(entry_tm)
        
        entry_tl = ttk.Entry(rows_frame, textvariable=row_vars['truck_large'], width=10)
        entry_tl.grid(row=row_num, column=6, padx=5, pady=2)
        entries.append(entry_tl)
        
        entry_tsp = ttk.Entry(rows_frame, textvariable=row_vars['truck_special'], width=10)
        entry_tsp.grid(row=row_num, column=7, padx=5, pady=2)
        entries.append(entry_tsp)
        
        # Bind paste functionality to all entries
        for entry in entries:
            entry.bind('<Control-v>', lambda e, rv=row_vars, dk=direction_key: self._handle_paste(e, rv, dk))
            entry.bind('<Button-3>', lambda e, rv=row_vars, dk=direction_key: self._show_paste_menu(e, rv, dk))
        
        # Delete button
        delete_btn = ttk.Button(rows_frame, text="Delete", command=lambda: self._delete_traffic_row(row_num - 1, direction_key))
        delete_btn.grid(row=row_num, column=8, padx=5, pady=2)
        
        rows_list.append({'vars': row_vars, 'widgets': entries, 'delete_btn': delete_btn})
    
    def _handle_paste(self, event, row_vars, direction_key):
        """Handle paste event from clipboard (Ctrl+V)."""
        try:
            # Get clipboard content
            clipboard_text = self.clipboard_get()
            
            # Determine which field has focus
            focused_widget = event.widget
            field_keys = ['year', 'passenger_vehicles', 'bus_small', 'bus_large', 
                          'truck_small', 'truck_medium', 'truck_large', 'truck_special']
            
            # Find starting column based on focused widget
            start_col = 0
            for i, key in enumerate(field_keys):
                if str(row_vars[key]) in str(focused_widget.cget('textvariable')):
                    start_col = i
                    break
            
            # Parse clipboard data (try tab first, then comma)
            values = []
            if '\t' in clipboard_text:
                values = clipboard_text.strip().split('\t')
            elif ',' in clipboard_text:
                values = clipboard_text.strip().split(',')
            else:
                values = clipboard_text.strip().split()
            
            # Fill values starting from focused column
            for i, value in enumerate(values):
                col_index = start_col + i
                if col_index >= len(field_keys):
                    break
                
                try:
                    clean_value = value.strip().replace(',', '')
                    if col_index == 0:  # Year field
                        row_vars[field_keys[col_index]].set(int(clean_value))
                    else:  # Numeric fields
                        row_vars[field_keys[col_index]].set(float(clean_value))
                except (ValueError, tk.TclError):
                    continue
            
            return 'break'  # Prevent default paste behavior
        except tk.TclError:
            pass  # Clipboard empty or unavailable
        except Exception as e:
            messagebox.showerror("Paste Error", f"Error pasting data: {str(e)}")
        return 'break'
    
    def _show_paste_menu(self, event, row_vars, direction_key):
        """Show right-click context menu for paste."""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Paste Row Data", command=lambda: self._handle_paste(event, row_vars, direction_key))
        menu.post(event.x_root, event.y_root)
    
    def _delete_traffic_row(self, index, direction_key):
        """Delete a traffic row."""
        rows_frame = self.traffic_rows_frame_masan_jinju if direction_key == "masan_jinju" else self.traffic_rows_frame_jinju_masan
        rows_list = self.traffic_rows_masan_jinju if direction_key == "masan_jinju" else self.traffic_rows_jinju_masan
        
        if len(rows_list) <= 1:
            messagebox.showwarning("Cannot Delete", "At least one row must remain.")
            return
        
        # Destroy widgets for this row
        for widget in rows_frame.grid_slaves(row=index + 1):
            widget.destroy()
        
        # Remove from list
        rows_list.pop(index)
        
        # Rebuild the grid to fix row numbers
        self._rebuild_traffic_grid(direction_key)
    
    def _rebuild_traffic_grid(self, direction_key):
        """Rebuild the traffic input grid after deletion."""
        rows_frame = self.traffic_rows_frame_masan_jinju if direction_key == "masan_jinju" else self.traffic_rows_frame_jinju_masan
        rows_list = self.traffic_rows_masan_jinju if direction_key == "masan_jinju" else self.traffic_rows_jinju_masan
        
        # Clear all widgets except header
        for widget in rows_frame.grid_slaves():
            row = widget.grid_info().get('row', 0)
            if row > 0:
                widget.destroy()
        
        # Recreate rows
        temp_rows = rows_list[:]
        rows_list.clear()
        
        for row_data in temp_rows:
            row_num = len(rows_list) + 1
            vars_dict = row_data['vars']
            
            ttk.Entry(rows_frame, textvariable=vars_dict['year'], width=8).grid(row=row_num, column=0, padx=5, pady=2)
            ttk.Entry(rows_frame, textvariable=vars_dict['passenger_vehicles'], width=10).grid(row=row_num, column=1, padx=5, pady=2)
            ttk.Entry(rows_frame, textvariable=vars_dict['bus_small'], width=10).grid(row=row_num, column=2, padx=5, pady=2)
            ttk.Entry(rows_frame, textvariable=vars_dict['bus_large'], width=10).grid(row=row_num, column=3, padx=5, pady=2)
            ttk.Entry(rows_frame, textvariable=vars_dict['truck_small'], width=10).grid(row=row_num, column=4, padx=5, pady=2)
            ttk.Entry(rows_frame, textvariable=vars_dict['truck_medium'], width=10).grid(row=row_num, column=5, padx=5, pady=2)
            ttk.Entry(rows_frame, textvariable=vars_dict['truck_large'], width=10).grid(row=row_num, column=6, padx=5, pady=2)
            ttk.Entry(rows_frame, textvariable=vars_dict['truck_special'], width=10).grid(row=row_num, column=7, padx=5, pady=2)
            
            delete_btn = ttk.Button(rows_frame, text="Delete", command=lambda idx=len(rows_list): self._delete_traffic_row(idx, direction_key))
            delete_btn.grid(row=row_num, column=8, padx=5, pady=2)
            
            rows_list.append({'vars': vars_dict, 'widgets': [], 'delete_btn': delete_btn})

    def _import_traffic_csv(self, direction_key):
        """Import traffic data from CSV."""
        traffic_logic = self.traffic_logic_masan_jinju if direction_key == "masan_jinju" else self.traffic_logic_jinju_masan
        
        filename = filedialog.askopenfilename(
            title="Import Traffic CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filename:
            return
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                csv_text = f.read()
            traffic_logic.import_csv_data(csv_text)
            self._display_traffic_results(direction_key)
            messagebox.showinfo("Success", f"Imported {len(traffic_logic.batch)} traffic records")
        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    def _compute_all_traffic(self, direction_key):
        """Compute traffic estimation for all rows."""
        traffic_logic = self.traffic_logic_masan_jinju if direction_key == "masan_jinju" else self.traffic_logic_jinju_masan
        rows_list = self.traffic_rows_masan_jinju if direction_key == "masan_jinju" else self.traffic_rows_jinju_masan
        
        try:
            # Clear previous batch
            traffic_logic.clear_batch()
            
            for row_data in rows_list:
                vars_dict = row_data['vars']
                year = int(vars_dict['year'].get())
                passenger_vehicles = float(vars_dict['passenger_vehicles'].get())
                bus_small = float(vars_dict['bus_small'].get())
                bus_large = float(vars_dict['bus_large'].get())
                truck_small = float(vars_dict['truck_small'].get())
                truck_medium = float(vars_dict['truck_medium'].get())
                truck_large = float(vars_dict['truck_large'].get())
                truck_special = float(vars_dict['truck_special'].get())
                
                # Calculate passenger split: 60% Gasoline, 40% Diesel
                passenger_gasoline = passenger_vehicles * 0.60
                passenger_diesel = passenger_vehicles * 0.40
                passenger_aadt = passenger_vehicles
                
                result = traffic_logic.add_manual_entry(
                    year=year,
                    passenger_aadt=passenger_aadt,
                    bus_small=bus_small,
                    bus_large=bus_large,
                    truck_small=truck_small,
                    truck_medium=truck_medium,
                    truck_large=truck_large,
                    truck_special=truck_special,
                )
            
            self._display_traffic_results(direction_key)
            messagebox.showinfo("Success", f"Computed {len(rows_list)} traffic entries")
        except Exception as e:
            messagebox.showerror("Computation Error", str(e))

    def _export_traffic_csv(self, direction_key):
        """Export traffic data to CSV."""
        traffic_logic = self.traffic_logic_masan_jinju if direction_key == "masan_jinju" else self.traffic_logic_jinju_masan
        
        if not traffic_logic.batch:
            messagebox.showwarning("No Data", "No traffic data to export")
            return
        filename = filedialog.asksaveasfilename(
            title="Export Traffic CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filename:
            return
        try:
            csv_content = traffic_logic.export_csv()
            from traffic_data_io import save_csv_to_file
            save_csv_to_file(csv_content, filename)
            messagebox.showinfo("Success", f"Exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _export_traffic_pdf(self, direction_key):
        """Export traffic data to PDF (via HTML browser preview)."""
        traffic_logic = self.traffic_logic_masan_jinju if direction_key == "masan_jinju" else self.traffic_logic_jinju_masan
        
        if not traffic_logic.batch:
            messagebox.showwarning("No Data", "No traffic data to export")
            return
        try:
            filename = traffic_logic.open_pdf_preview(title="Traffic Estimation Results")
            messagebox.showinfo("Success", f"PDF preview opened: {filename}\nUse browser Print to save as PDF")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _clear_traffic(self, direction_key):
        """Clear all traffic estimation data."""
        traffic_logic = self.traffic_logic_masan_jinju if direction_key == "masan_jinju" else self.traffic_logic_jinju_masan
        text_widget = self.traffic_result_text_masan_jinju if direction_key == "masan_jinju" else self.traffic_result_text_jinju_masan
        rows_frame = self.traffic_rows_frame_masan_jinju if direction_key == "masan_jinju" else self.traffic_rows_frame_jinju_masan
        rows_list = self.traffic_rows_masan_jinju if direction_key == "masan_jinju" else self.traffic_rows_jinju_masan
        
        traffic_logic.clear_batch()
        text_widget.delete(1.0, "end")
        text_widget.insert("end", "Traffic data cleared.\n")
        
        # Clear all rows and add one fresh row
        for row_data in rows_list:
            for widget in rows_frame.grid_slaves():
                if widget.grid_info().get('row', 0) > 0:
                    widget.destroy()
        rows_list.clear()
        self._add_traffic_row(direction_key)

    def _display_traffic_results(self, direction_key):
        """Display traffic estimation results in the text widget."""
        traffic_logic = self.traffic_logic_masan_jinju if direction_key == "masan_jinju" else self.traffic_logic_jinju_masan
        text_widget = self.traffic_result_text_masan_jinju if direction_key == "masan_jinju" else self.traffic_result_text_jinju_masan
        
        text_widget.delete(1.0, "end")
        if not traffic_logic.batch:
            text_widget.insert("end", "No traffic data.\n")
            return

        text_widget.insert("end", "="*80 + "\n")
        text_widget.insert("end", "ESTIMATED TRAFFIC VOLUME RESULTS\n")
        text_widget.insert("end", "="*80 + "\n\n")

        for entry in traffic_logic.batch:
            if not entry.result:
                continue
            res = entry.result
            inp = entry.inputs

            text_widget.insert("end", f"Year: {entry.year}\n")
            text_widget.insert("end", f"Direction: {entry.direction}\n")
            text_widget.insert("end", "-"*60 + "\n")
            text_widget.insert("end", f"  Passenger Vehicles: {inp.passenger_aadt:,.0f}\n")
            text_widget.insert("end", f"    - Gasoline (60%): {res.counts.get('passengerGasoline', 0):,.0f}\n")
            text_widget.insert("end", f"    - Diesel (40%):   {res.counts.get('passengerDiesel', 0):,.0f}\n")
            text_widget.insert("end", f"  Bus Small:          {inp.bus_small:,.0f}\n")
            text_widget.insert("end", f"  Bus Large:          {inp.bus_large:,.0f}\n")
            text_widget.insert("end", f"  Truck Small:        {inp.truck_small:,.0f}\n")
            text_widget.insert("end", f"  Truck Medium:       {inp.truck_medium:,.0f}\n")
            text_widget.insert("end", f"  Truck Large:        {inp.truck_large:,.0f}\n")
            text_widget.insert("end", f"  Truck Special:      {inp.truck_special:,.0f}\n")
            text_widget.insert("end", f"\n  Total AADT:         {res.total_aadt:,.0f}\n")
            text_widget.insert("end", f"  Heavy Vehicle Mix:  {res.heavy_vehicle_mix_pt:.2f}%\n")
            text_widget.insert("end", "\n  Mix Percentages:\n")
            for key, val in res.mix_percents.items():
                text_widget.insert("end", f"    {key}: {val:.2f}%\n")
            text_widget.insert("end", "\n")


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
    """Main application with tabbed interface."""
    def __init__(self):
        super().__init__()
        self.title("BEC Computational System - Main Menu")
        self.geometry("750x800")
        
        self._build_interface()

    def _build_interface(self):
        # Title
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=10)
        
        # Center the titles
        center_titles = ttk.Frame(title_frame)
        center_titles.pack(expand=True)
        title_label = ttk.Label(center_titles, text="BEC Computational System", font=("Arial", 16, "bold"), foreground="#004080")
        title_label.pack()
        subtitle_label = ttk.Label(center_titles, text="Use the tab below for appropriate calculations", font=("Arial", 10), foreground="#666666")
        subtitle_label.pack(pady=2)

        # Compute Summary button positioned absolutely on the right
        self.compute_btn = ttk.Button(title_frame, text="Compute Summary", command=self._compute_summary)
        self.compute_btn.place(relx=1.0, rely=0.5, anchor="e", x=-10)

        # Separator
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20, pady=5)

        # Create notebook for tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Create result tab first
        result_tab = ResultsTab(notebook)

        # First tab: Calculate Ventilation Volume
        self.ventilation_volume_tab = VentilationVolumeTab(notebook)
        notebook.add(self.ventilation_volume_tab, text="Calculate Ventilation Volume")

        # Second tab: Number of Jet Fan (pass result_tab and volume_tab references)
        self.jet_fan_tab = JetFanTab(notebook, result_tab=result_tab, volume_tab=self.ventilation_volume_tab)
        notebook.add(self.jet_fan_tab, text="Number of Jet Fan")

        # Results tab
        self.results_tab = result_tab
        notebook.add(self.results_tab, text="Results (summary)")

    def _compute_summary(self):
        # Compute Jet Fan results and publish
        inp, results = self.jet_fan_tab.compute_and_publish()
        # Append Ventilation Volume summaries for both directions
        infos = [
            self.ventilation_volume_tab.get_volume_summary("MasanToJinju"),
            self.ventilation_volume_tab.get_volume_summary("JinjuToMasan"),
        ]
        self.results_tab.append_volume_summary(infos)
        # Append Traffic Estimation summary for both directions
        self.results_tab.append_traffic_summary(
            self.ventilation_volume_tab.traffic_logic_masan_jinju,
            self.ventilation_volume_tab.traffic_logic_jinju_masan
        )


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
