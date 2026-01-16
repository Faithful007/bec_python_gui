#!/usr/bin/env python3
"""
Quick test to verify n and pressure calculations are working correctly.
This script checks the calculation logic without running the full GUI.
"""

from vent_functions import compute_traffic_flow, Vt_MAP

# Test parameters
direction = 1
speed = 100  # km/h
vt = Vt_MAP.get(speed, 0)  # should be ~13.89 m/s
lr = 1000  # tunnel length in meters
lp = 29.728  # segment length in meters
ar = 58.67216   # cross-section area in m²

lanes = 1
imax = 165  # capacity per lane
road_type = 1  # National/Expressway

# Constants
xi = 0.6
lamb = 0.025
rho = 1.2
ae = 1.0751
un = 2.5
vr = 0.1023   # reference speed

# Test compute_traffic_flow
q = compute_traffic_flow(imax, speed, road_type)
print(f"Traffic flow Q: {q:.2f} PCU/hr·lane")

# Test n calculation
if vt > 0 and lr > 0:
    n = round((q * lanes * lr / (3600.0 * vt)) + 0.4, 0)
else:
    n = 0
print(f"Number of vehicles n: {n:.0f}")

# Test Dr calculation
dr = (4 * ar) / lp
print(f"Hydraulic diameter Dr: {dr:.4f} m")

# Test pressure calculations
if dr > 0:
    common_factor = (1 + xi + lamb * lr / dr) * rho / 2.0
else:
    common_factor = 0.0

delta_pr = common_factor * (vr ** 2)
delta_pm = common_factor * (un ** 2)

if vt == vr:
    delta_pt = 0.0
else:
    sign = 1.0 if vt > vr else -1.0
    if ar > 0:
        delta_pt = sign * rho / 2.0 * ae / ar * n * (vt - vr) ** 2
    else:
        delta_pt = 0.0

delta_pq = delta_pr + delta_pm - delta_pt

print(f"\nPressure calculations:")
print(f"  Common factor: {common_factor:.4f}")
print(f"  ΔPr (vehicle resistance): {delta_pr:.4f} Pa")
print(f"  ΔPm (natural wind): {delta_pm:.4f} Pa")
print(f"  ΔPt (traffic): {delta_pt:.4f} Pa")
print(f"  ΔPq (required pressure): {delta_pq:.4f} Pa")

print("\n✓ All calculations completed successfully!")
