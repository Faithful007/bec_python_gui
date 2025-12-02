"""
traffic_calculations.py

Pure Python translation of src/modules/trafficEstimation/calculations.js
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List


# Excel logic: passenger cars split 60% gasoline / 40% diesel
PASSENGER_SPLIT: Dict[str, float] = {
    "gasoline": 0.6,
    "diesel": 0.4,
}

# Order aligned with Excel columns (C..J) – same as VEHICLE_KEYS in JS
VEHICLE_KEYS: List[str] = [
    "passengerGasoline",  # C
    "passengerDiesel",    # D
    "busSmall",           # E
    "busLarge",           # F
    "truckSmall",         # G
    "truckMedium",        # H
    "truckLarge",         # I
    "truckSpecial",       # J
]


@dataclass
class TrafficInput:
    """
    Input for compute_estimated_traffic, mirroring the JS object.
    All values are AADT (vehicles/day).
    """
    passenger_aadt: float = 0.0
    bus_small: float = 0.0
    bus_large: float = 0.0
    truck_small: float = 0.0
    truck_medium: float = 0.0
    truck_large: float = 0.0
    truck_special: float = 0.0


@dataclass
class TrafficResult:
    """
    Output of compute_estimated_traffic.
    """
    counts: Dict[str, float]
    total_aadt: float
    mix_percents: Dict[str, float]
    mix_percent_sum: float
    heavy_vehicle_mix_pt: float


def compute_estimated_traffic(params: TrafficInput) -> TrafficResult:
    """
    Compute estimated daily traffic (추정교통량 / 정교통량),
    translated from computeEstimatedTraffic in calculations.js.

    :param params: TrafficInput with AADT values.
    :return: TrafficResult
    """
    passenger_aadt = float(params.passenger_aadt or 0.0)
    bus_small = float(params.bus_small or 0.0)
    bus_large = float(params.bus_large or 0.0)
    truck_small = float(params.truck_small or 0.0)
    truck_medium = float(params.truck_medium or 0.0)
    truck_large = float(params.truck_large or 0.0)
    truck_special = float(params.truck_special or 0.0)

    # 1) Counts (row 38 / 55 equivalents)
    counts: Dict[str, float] = {
        "passengerGasoline": passenger_aadt * PASSENGER_SPLIT["gasoline"],
        "passengerDiesel": passenger_aadt * PASSENGER_SPLIT["diesel"],
        "busSmall": bus_small,
        "busLarge": bus_large,
        "truckSmall": truck_small,
        "truckMedium": truck_medium,
        "truckLarge": truck_large,
        "truckSpecial": truck_special,
    }

    # 2) Total AADT (K38 / K55)
    total_aadt = 0.0
    for key in VEHICLE_KEYS:
        v = counts.get(key, 0.0)
        total_aadt += float(v or 0.0)

    # 3) Mix ratios (%) per vehicle type
    mix_percents: Dict[str, float] = {}
    if total_aadt > 0:
        for key in VEHICLE_KEYS:
            v = float(counts.get(key, 0.0) or 0.0)
            mix_percents[key] = round((v / total_aadt) * 100.0, 2)
    else:
        for key in VEHICLE_KEYS:
            mix_percents[key] = 0.0

    # 4) Heavy-vehicle mix Pt = F39 + H39 + I39 + J39
    heavy_vehicle_mix_pt = round(
        (mix_percents.get("busLarge", 0.0)
         + mix_percents.get("truckMedium", 0.0)
         + mix_percents.get("truckLarge", 0.0)
         + mix_percents.get("truckSpecial", 0.0)),
        2,
    )

    # 5) Sum of mix (%) – for check (should be ~100)
    mix_percent_sum = 0.0
    for key in VEHICLE_KEYS:
        mix_percent_sum += mix_percents.get(key, 0.0)

    return TrafficResult(
        counts=counts,
        total_aadt=total_aadt,
        mix_percents=mix_percents,
        mix_percent_sum=mix_percent_sum,
        heavy_vehicle_mix_pt=heavy_vehicle_mix_pt,
    )
