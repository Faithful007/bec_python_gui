"""
traffic_estimation_module.py

Pure Python translation of src/modules/trafficEstimation/TrafficEstimationLogic.js.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional
import math

from traffic_calculations import (
    TrafficInput,
    TrafficResult,
    compute_estimated_traffic,
    VEHICLE_KEYS
)
from traffic_data_io import (
    TrafficRow,
    parse_csv,
    export_to_csv,
    build_pdf_html,
    open_pdf_preview_in_browser
)


@dataclass
class TrafficBatch:
    """
    One set of inputs, plus computed result and associated metadata.
    """
    year: int = 0
    inputs: Optional[TrafficInput] = None
    result: Optional[TrafficResult] = None
    direction: str = ""


class TrafficEstimationLogic:
    """
    Manages a batch of traffic estimation records for a single direction.
    """

    def __init__(self, direction: str = ""):
        self.direction = direction
        self.batch: List[TrafficBatch] = []

    def import_csv_data(self, csv_text: str) -> None:
        """
        Parse CSV text and populate self.batch with computed results.
        """
        rows = parse_csv(csv_text)
        self.batch.clear()

        for row in rows:
            # Build TrafficInput
            t_input = TrafficInput(
                passenger_aadt=(row.passengerGasoline or 0) + (row.passengerDiesel or 0),
                bus_small=row.busSmall or 0,
                bus_large=row.busLarge or 0,
                truck_small=row.truckSmall or 0,
                truck_medium=row.truckMedium or 0,
                truck_large=row.truckLarge or 0,
                truck_special=row.truckSpecial or 0,
            )
            result = compute_estimated_traffic(t_input)
            entry = TrafficBatch(
                year=row.year,
                inputs=t_input,
                result=result,
                direction=self.direction,
            )
            self.batch.append(entry)

    def add_manual_entry(
        self,
        year: int,
        passenger_aadt: float,
        bus_small: float,
        bus_large: float,
        truck_small: float,
        truck_medium: float,
        truck_large: float,
        truck_special: float,
        # Optional tunnel parameters for pressure calculation
        Qtreq: float = 0.0,
        Ar: float = 0.0,
        Lr: float = 0.0,
        Dr: float = 0.0,
        rho: float = 1.2,
        xi: float = 0.6,
        lamb: float = 0.025,
        Ae: float = 1.0751,
        Vt: float = 0.0,
        lanes: int = 1,
        vehicle_hr_lane: float = 0.0,
    ) -> TrafficResult:
        """
        Manually add a single entry and compute its result.
        If tunnel parameters are provided, also compute pressure values.
        """
        from traffic_calculations import compute_pressure_values
        
        t_input = TrafficInput(
            passenger_aadt=passenger_aadt,
            bus_small=bus_small,
            bus_large=bus_large,
            truck_small=truck_small,
            truck_medium=truck_medium,
            truck_large=truck_large,
            truck_special=truck_special,
        )
        result = compute_estimated_traffic(t_input)
        
        # Compute pressure values if tunnel parameters are provided
        if Qtreq > 0 and Ar > 0 and Lr > 0:
            result = compute_pressure_values(
                result=result,
                Qtreq=Qtreq,
                Ar=Ar,
                Lr=Lr,
                Dr=Dr,
                rho=rho,
                xi=xi,
                lamb=lamb,
                Ae=Ae,
                Vt=Vt,
                lanes=lanes,
                vehicle_hr_lane=vehicle_hr_lane,
            )
        
        entry = TrafficBatch(
            year=year,
            inputs=t_input,
            result=result,
            direction=self.direction,
        )
        self.batch.append(entry)
        return result

    def get_batch_data(self) -> List[Dict[str, Any]]:
        """
        Return a list of dict suitable for CSV export or PDF generation.
        """
        out: List[Dict[str, Any]] = []
        for entry in self.batch:
            if not entry.result:
                continue
            res = entry.result
            inp = entry.inputs or TrafficInput()
            out.append(
                {
                    "year": entry.year,
                    "direction": entry.direction,
                    "passengerGasoline": res.counts.get("passengerGasoline", 0),
                    "passengerDiesel": res.counts.get("passengerDiesel", 0),
                    "busSmall": inp.bus_small,
                    "busLarge": inp.bus_large,
                    "truckSmall": inp.truck_small,
                    "truckMedium": inp.truck_medium,
                    "truckLarge": inp.truck_large,
                    "truckSpecial": inp.truck_special,
                    "totalAadt": res.total_aadt,
                    "heavyVehicleMixPt": res.heavy_vehicle_mix_pt,
                    "mixPercents": res.mix_percents,
                    "delta_Pr": res.delta_Pr,
                    "delta_Pm": res.delta_Pm,
                    "delta_Pt": res.delta_Pt,
                    "delta_Pq": res.delta_Pq,
                }
            )
        return out

    def export_csv(self) -> str:
        """
        Return CSV string for this batch.
        """
        data = self.get_batch_data()
        return export_to_csv(data, direction=self.direction)

    def export_pdf_html(self, title: str = "Traffic Estimation Results") -> str:
        """
        Return HTML suitable for PDF printing.
        """
        data = self.get_batch_data()
        return build_pdf_html(data, title=title)

    def open_pdf_preview(self, title: str = "Traffic Estimation Results") -> str:
        """
        Open browser preview for printing to PDF.
        """
        data = self.get_batch_data()
        return open_pdf_preview_in_browser(data, title=title)

    def clear_batch(self) -> None:
        """
        Clear all entries.
        """
        self.batch.clear()

    def get_latest_result(self) -> Optional[TrafficResult]:
        """
        Return the result from the most recent entry, if any.
        """
        if not self.batch:
            return None
        return self.batch[-1].result
