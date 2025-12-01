# vent_functions.py
from dataclasses import dataclass
import math

# ---- 1. Data models ----

@dataclass
class TunnelVentInputs:
    # INPUTS (Un computed from V_kmh, traffic_volume computed from Imax)
    V_kmh: float          # 1. 주행속도 (km/h)
    Qtreq: float          # 2. 소요환기량 Qtreq (m3/s)
    Imax: float           # 3. 최대교통량 [PCU/hr·lane]
    road_type: int        # 4. 도로종류 (1=국도/고속도로, 2=도심지)
    lanes: int            # 5. 차로수
    Ar: float             # 6. 터널단면적 Ar (m2)
    Lr: float             # 7. 터널길이 Lr (m)
    rho: float            # 8. 공기밀도 ρ (kg/m3)
    xi: float             # 9. 입구손실계수 ξ
    lamb: float           # 10. 마찰손실계수 λ
    Dr: float             # 11. 대표직경 Dr (m)
    Ae: float             # 12. 등가저항면적 Ae (m2)
    jet_diameter: int     # 13. 젯트팬 직경 Φ (mm, e.g. 1030)
    high_efficiency: bool # 14. 고효율형 여부 (True→30 m/s, False→34 m/s)
    eta: float            # 15. 분류효율 η

@dataclass
class TunnelVentResults:
    Vt: float
    Vr: float
    Un: float
    Aj: float
    Vj: float
    n: int
    Kj: float
    Pr: float
    Pm: float
    Pt: float
    Pq: float
    Pj: float
    Z_raw: float
    Z_applied: int


# ---- 2. Constant lookup tables ----

JET_AREA_MAP = {
    630: 0.27,
    710: 0.396,
    1030: 0.83,
    1250: 1.227,
    1530: 1.83
}

# Un values corresponding to V_kmh
UN_MAP = {
    10: 2.78,
    20: 5.56,
    30: 8.33,
    40: 11.11,
    50: 13.89,
    60: 16.67,
    70: 19.44,
    80: 22.22
}

# Allowed speeds for traffic flow calculation
SPEED_OPTIONS_KMH = (10, 20, 30, 40, 50, 60, 70, 80)


# ---- 3. Traffic flow calculation functions ----

def compute_traffic_flow(Imax: float, speed_kmh: float, road_type: int) -> int:
    """
    교통량 Q [PCU/hr·lane] for a given speed.
    
    road_type:
        1 → 국도/고속도로
        2 → 도심지
    """
    I = float(Imax)
    V = float(speed_kmh)

    if I <= 0 or V <= 0:
        return 0

    if road_type == 1:
        K = 150.0  # 국도/고속도로
    elif road_type == 2:
        K = 165.0  # 도심지
    else:
        raise ValueError("road_type must be 1 (국도/고속도로) or 2 (도심지).")

    numerator = K * I
    denominator = K * V + I * (1.0 - V / 60.0) ** 2

    q = numerator / denominator  # PCU/hr·lane
    return int(round(q))         # same as Excel ROUND(…,0)


def compute_traffic_density(Imax: float, speed_kmh: float, road_type: int) -> float:
    """
    교통밀도 k [PCU/km·lane]
    k = Q / V
    """
    flow = compute_traffic_flow(Imax, speed_kmh, road_type)
    V = float(speed_kmh)
    if V <= 0:
        return 0.0
    k = flow / V
    return round(k, 3)  # 3 decimal places


# ---- 4. Small functions for each quantity ----

def compute_Un(V_kmh: float) -> float:
    """자연풍속 Un from V_kmh lookup table with interpolation"""
    if V_kmh in UN_MAP:
        return UN_MAP[V_kmh]
    
    # Linear interpolation for values between table entries
    sorted_keys = sorted(UN_MAP.keys())
    if V_kmh < sorted_keys[0]:
        return UN_MAP[sorted_keys[0]]
    if V_kmh > sorted_keys[-1]:
        return UN_MAP[sorted_keys[-1]]
    
    # Find bracketing values
    for i in range(len(sorted_keys) - 1):
        if sorted_keys[i] <= V_kmh <= sorted_keys[i + 1]:
            x1, x2 = sorted_keys[i], sorted_keys[i + 1]
            y1, y2 = UN_MAP[x1], UN_MAP[x2]
            # Linear interpolation
            return round(y1 + (y2 - y1) * (V_kmh - x1) / (x2 - x1), 4)
    
    return UN_MAP[sorted_keys[0]]  # fallback


def compute_Vt(inp: TunnelVentInputs) -> float:
    """주행속도(m/s) Vt = ROUND(V_kmh/3.6, 2)"""
    return round(inp.V_kmh / 3.6, 2)


def compute_Vr(inp: TunnelVentInputs) -> float:
    """차도내풍속 Vr = ROUND(Qtreq / Ar, 4)"""
    return round(inp.Qtreq / inp.Ar, 4)


def compute_Aj(inp: TunnelVentInputs) -> float:
    """젯트팬 면적 Aj : Φ 값에 따른 lookup"""
    if inp.jet_diameter not in JET_AREA_MAP:
        raise ValueError(f"Unsupported jet fan diameter Φ={inp.jet_diameter}")
    return JET_AREA_MAP[inp.jet_diameter]


def compute_Vj(inp: TunnelVentInputs) -> float:
    """젯트팬 토출속도 Vj = IF(high_efficiency, 30, 34)"""
    return 30.0 if inp.high_efficiency else 34.0


def compute_n(inp: TunnelVentInputs, Vt: float) -> int:
    """
    터널내 자동차 수 n = ROUND(Q * lanes * Lr / (V * 1000) + 0.4, 0)
    where Q is computed from traffic flow model
    """
    # Calculate traffic flow Q [PCU/hr·lane]
    Q = compute_traffic_flow(inp.Imax, inp.V_kmh, inp.road_type)
    
    # Total vehicles in tunnel: Q * lanes * Lr / (V * 1000)
    # Lr is in meters, V is in km/h, so divide by 1000 to convert
    if inp.V_kmh <= 0:
        return 0
    
    n = Q * inp.lanes * inp.Lr / (inp.V_kmh * 1000.0)
    return round(n + 0.4)


def compute_Kj(Vr: float) -> float:
    """제트팬 승압계수 Kj = IF(Vr<4,0.99, IF(Vr<8,0.92,0.9))"""
    if Vr < 4:
        return 0.99
    elif Vr < 8:
        return 0.92
    return 0.9


def compute_common_factor(inp: TunnelVentInputs) -> float:
    """공통계수 (1+ξ+λ*Lr/Dr) * ρ / 2"""
    return (1 + inp.xi + inp.lamb * (inp.Lr / inp.Dr)) * inp.rho / 2.0 


def compute_Pr(inp: TunnelVentInputs, Vr: float) -> float:
    """ΔPr = common_factor"""
    cf = compute_common_factor(inp)
    return round(cf * (Vr ** 2), 4)


def compute_Pm(inp: TunnelVentInputs, Un: float) -> float:
    """ΔPm = common_factor * Un^2"""
    cf = compute_common_factor(inp)
    return round(cf * (Un ** 2), 4)


def compute_Pt(inp: TunnelVentInputs, Vt: float, Vr: float, n: int) -> float:
    """
    ΔPt = sign(Vt−Vr) × ρ/2 × (Ae/Ar) × n × (Vt−Vr)^2
    where sign(Vt−Vr) = +1 if Vt>Vr, -1 if Vt<Vr.
    """
    if Vt == Vr:
        return 0.0

    sign = 1.0 if Vt > Vr else -1.0
    base = inp.rho / 2.0 * inp.Ae / inp.Ar * n * (Vt - Vr) ** 2
    return round(sign * base, 4)


def compute_Pq(Pr: float, Pm: float, Pt: float) -> float:
    """ΔPq = Pr + Pm - Pt"""
    return round(Pr + Pm - Pt, 4)


def compute_Pj(inp: TunnelVentInputs, Vr: float, Aj: float, Vj: float, Kj: float) -> float:
    """
    ΔPj = Kj * ρ/2 * Vj^2 * Aj/Ar * (1 - Vr/Vj) * η
    """
    return round(Kj * (inp.rho / 2.0) * Vj ** 2 * Aj / inp.Ar * (1 - Vr / Vj) * inp.eta, 4)


def compute_Z_raw(Pq: float, Pj: float) -> float:
    """소요 젯트팬 수 Z = ROUND(Pq / Pj, 2)"""
    if Pj == 0:
        return math.inf
    return round(Pq / Pj, 2)


def compute_Z_applied(Z_raw: float) -> int:
    """적용 수량 Z대 = IF(Z<0,0, ROUND(Z,0))"""
    if Z_raw <= 0 or math.isinf(Z_raw):
        return 0
    return round(Z_raw)


# ---- 4. Helper that runs everything ----

def compute_all(inp: TunnelVentInputs) -> TunnelVentResults:
    Vt = compute_Vt(inp)
    Vr = compute_Vr(inp)
    Un = compute_Un(inp.V_kmh)
    Aj = compute_Aj(inp)
    Vj = compute_Vj(inp)
    n = compute_n(inp, Vt)
    Kj = compute_Kj(Vr)
    Pr = compute_Pr(inp, Vr)
    Pm = compute_Pm(inp, Un)
    Pt = compute_Pt(inp, Vt, Vr, n)
    Pq = compute_Pq(Pr, Pm, Pt)
    Pj = compute_Pj(inp, Vr, Aj, Vj, Kj)
    Z_raw = compute_Z_raw(Pq, Pj)
    Z_applied = compute_Z_applied(Z_raw)

    return TunnelVentResults(
        Vt=Vt, Vr=Vr, Un=Un, Aj=Aj, Vj=Vj, n=n, Kj=Kj,
        Pr=Pr, Pm=Pm, Pt=Pt, Pq=Pq, Pj=Pj,
        Z_raw=Z_raw, Z_applied=Z_applied
    )
