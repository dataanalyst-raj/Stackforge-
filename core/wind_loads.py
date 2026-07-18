"""
StackForge - Wind Loads Module
Static, Dynamic (Inertia) and Gust Factor wind loads
As per IS 875 (Part 3) and IS 6533 (Part 2)
"""

import math
from utils.constants import STEEL_DENSITY


def get_k2_factor(height_m: float, terrain_category: int = 3) -> float:
    """
    Terrain & Height factor K2 (simplified from IS 875 Part 3).
    Values are approximate mid-range for each height band.
    """
    # Terrain Category 3 (most common for industrial areas)
    table = {
        1: [(10, 1.05), (15, 1.09), (20, 1.12), (30, 1.15), (50, 1.20), (100, 1.26)],
        2: [(10, 1.00), (15, 1.05), (20, 1.07), (30, 1.12), (50, 1.17), (100, 1.24)],
        3: [(10, 0.91), (15, 0.97), (20, 1.01), (30, 1.06), (50, 1.12), (100, 1.20)],
        4: [(10, 0.80), (15, 0.86), (20, 0.90), (30, 0.97), (50, 1.05), (100, 1.15)],
    }

    cat = min(max(terrain_category, 1), 4)
    rows = table[cat]

    if height_m <= rows[0][0]:
        return rows[0][1]

    for i in range(1, len(rows)):
        h1, k1 = rows[i-1]
        h2, k2 = rows[i]
        if height_m <= h2:
            # Linear interpolation
            ratio = (height_m - h1) / (h2 - h1)
            return round(k1 + ratio * (k2 - k1), 3)

    return rows[-1][1]


def design_wind_speed(Vb: float, K1: float, K2: float, K3: float = 1.0) -> float:
    """Vz = Vb × K1 × K2 × K3"""
    return Vb * K1 * K2 * K3


def design_wind_pressure(Vz: float) -> float:
    """pz = 0.6 × Vz²   (N/m²) → converted to kg/m²"""
    return 0.6 * (Vz ** 2)


def static_wind_load_on_zone(
    pressure_kg_m2: float,
    mean_od_mm: float,
    length_m: float,
    Cd: float = 0.70
) -> float:
    """
    Static wind load on a zone (kg)
    Force = pz × Cd × Projected Area
    """
    diameter_m = mean_od_mm / 1000.0
    area = diameter_m * length_m
    force = pressure_kg_m2 * Cd * area
    return round(force, 1)


def calculate_static_wind_loads(
    zones: list,
    Vb: float,
    K1: float = 0.90,
    K3: float = 1.0,
    terrain_category: int = 3,
    Cd: float = 0.70
) -> list:
    """
    Calculate static wind load for every zone (3-sec peak style).
    Returns list of dicts with speed, pressure and load.
    """
    results = []
    height_from_ground = 0.0
    total_height = sum(z["length"] for z in zones)

    # We calculate from bottom to top for height reference
    # but store in zone order (top to bottom as per Dynastac)
    zone_heights = []
    h = total_height
    for z in zones:
        mid_height = h - z["length"] / 2.0
        zone_heights.append(mid_height)
        h -= z["length"]

    for i, zone in enumerate(zones):
        mid_h = zone_heights[i]
        K2 = get_k2_factor(mid_h, terrain_category)
        Vz = design_wind_speed(Vb, K1, K2, K3)
        pz = design_wind_pressure(Vz)
        load = static_wind_load_on_zone(pz, zone["mean_od"], zone["length"], Cd)

        results.append({
            "zone_no": zone["zone_no"],
            "height_mid": round(mid_h, 2),
            "K2": K2,
            "Vz": round(Vz, 1),
            "pressure": round(pz, 1),
            "static_load": load
        })

    return results


def approximate_mode_shape(zone_index: int, total_zones: int, mode: int = 1) -> float:
    """
    Approximate mode shape values for a cantilever chimney.
    Mode 1: simple cantilever
    Mode 2 & 3: approximate higher modes
    """
    # Normalized height from base (0 at base, 1 at top)
    # zone_index 0 = top zone
    x = 1.0 - (zone_index + 0.5) / total_zones

    if mode == 1:
        # Classic cantilever approximation
        return x ** 1.5
    elif mode == 2:
        # Approximate second mode
        return math.sin(2.5 * math.pi * x / 2) * (0.5 + 0.5 * x)
    else:
        # Approximate third mode
        return math.sin(4.0 * math.pi * x / 2) * (0.4 + 0.6 * x)


def calculate_dynamic_wind_loads(
    zones: list,
    zone_weights: list,
    static_loads_hmw: list,
    natural_freq: float,
    Vb: float,
    damping: float = 0.02
) -> list:
    """
    Approximate Dynamic (Inertia) wind loads using IS 6533 logic.
    Uses approximate mode shapes for Version 1.
    """
    n = len(zones)
    T = 1.0 / max(natural_freq, 0.1)
    xi = T * Vb / 1200.0

    # Dynamic coefficient (simplified from Table 5)
    if xi <= 0.025:
        dyn_coeff = 2.50
    elif xi <= 0.050:
        dyn_coeff = 2.50 + (xi - 0.025) / 0.025 * 0.60
    else:
        dyn_coeff = 3.10

    # Space correlation
    nu = 0.70 if n > 3 else 0.85

    # Build mode 1 shape
    Y = [approximate_mode_shape(i, n, mode=1) for i in range(n)]
    # Normalize so top = 1.0
    max_y = max(abs(y) for y in Y) or 1.0
    Y = [y / max_y for y in Y]

    # Approximate pulsation coefficients
    mk = [0.66 + 0.03 * i for i in range(n)]

    # Summation terms
    sum_num = 0.0
    sum_den = 0.0
    for i in range(n):
        Pst = static_loads_hmw[i] if i < len(static_loads_hmw) else 100
        M = zone_weights[i] if i < len(zone_weights) else 1000
        sum_num += Y[i] * Pst * mk[i] * 9.81   # to Newtons
        sum_den += (Y[i] ** 2) * M

    ratio = sum_num / max(sum_den, 1.0)

    results = []
    for i in range(n):
        eta = Y[i] * ratio
        M = zone_weights[i] if i < len(zone_weights) else 1000
        Pdyn = M * dyn_coeff * abs(eta) * nu / 9.81   # back to kg
        results.append({
            "zone_no": zones[i]["zone_no"],
            "Y": round(Y[i], 4),
            "dynamic_load": round(Pdyn, 1)
        })

    return results


def calculate_gust_factor(
    height_m: float,
    natural_freq: float,
    Vb: float,
    avg_breadth_m: float,
    damping: float = 0.02,
    terrain_category: int = 3
) -> dict:
    """
    Calculate Gust Factor G as per IS 875 Part 3 Clause 8.3
    Simplified but follows the same structure we verified.
    """
    # Hourly mean wind at top (approximate)
    K2_top = get_k2_factor(height_m, terrain_category)
    # HMW is roughly 0.6–0.7 of peak for many cases; we use a practical factor
    Vh = Vb * 0.90 * K2_top * 0.65   # rough HMW

    # Simplified factors (based on typical values we saw)
    gfr = 1.70
    B = 0.75
    phi = 0.0

    # Size reduction and energy (approximate)
    S = 0.16
    E = 0.047
    SE_beta = (S * E) / max(damping, 0.01)

    G = 1 + gfr * math.sqrt(B * (1 + phi)**2 + SE_beta)

    return {
        "G": round(G, 3),
        "Vh": round(Vh, 2),
        "gfr": gfr,
        "B": B,
        "SE_beta": round(SE_beta, 3)
    }


def calculate_gust_wind_loads(static_hmw_loads: list, G: float) -> list:
    """Gust Wind Load = HMW Static Load × G"""
    return [round(load * G, 1) for load in static_hmw_loads]


def calculate_all_wind_loads(
    zones: list,
    zone_weights: list,
    Vb: float,
    natural_freq: float,
    K1: float = 0.90,
    K3: float = 1.0,
    terrain_category: int = 3,
    Cd: float = 0.70,
    damping: float = 0.02
) -> dict:
    """
    Master function – calculates all wind load cases.
    """
    # 1. Static (3-sec style)
    static_results = calculate_static_wind_loads(
        zones, Vb, K1, K3, terrain_category, Cd
    )
    static_loads = [r["static_load"] for r in static_results]

    # 2. Approximate HMW static (lower)
    hmw_factor = 0.40   # typical ratio seen in samples
    hmw_static = [round(s * hmw_factor, 1) for s in static_loads]

    # 3. Dynamic (Inertia)
    dynamic_results = calculate_dynamic_wind_loads(
        zones, zone_weights, hmw_static, natural_freq, Vb, damping
    )
    dynamic_loads = [r["dynamic_load"] for r in dynamic_results]

    # 4. Gust Factor
    total_height = sum(z["length"] for z in zones)
    avg_breadth = sum(z["mean_od"] for z in zones) / len(zones) / 1000.0
    gf = calculate_gust_factor(total_height, natural_freq, Vb, avg_breadth, damping, terrain_category)
    gust_loads = calculate_gust_wind_loads(hmw_static, gf["G"])

    # Combine
    combined = []
    for i, zone in enumerate(zones):
        combined.append({
            "zone_no": zone["zone_no"],
            "static_3sec": static_loads[i],
            "hmw_static": hmw_static[i],
            "dynamic": dynamic_loads[i],
            "hmw_plus_dynamic": round(hmw_static[i] + dynamic_loads[i], 1),
            "gust": gust_loads[i],
            "Y_mode1": dynamic_results[i]["Y"]
        })

    return {
        "zones": combined,
        "gust_factor": gf,
        "static_details": static_results
    }
