"""
StackForge - Dynamic Analysis Module
Natural Frequency (Rayleigh), Mode Shapes, Across-Wind (Vortex Shedding)
As per IS 6533 (Part 2) Clause 8.3 and Annex A
"""

import math


def rayleigh_natural_frequency(zone_weights: list, deflections_cm: list) -> dict:
    """
    Calculate fundamental natural frequency using Rayleigh method.
    IS 6533 Part 2 Clause 8.3.1

    f = (1 / 2π) * sqrt( g * Σ(M·x) / Σ(M·x²) )

    zone_weights : list of masses (kg)
    deflections_cm : list of deflections (cm) under self-weight (or assumed shape)
    """
    g = 9.81  # m/s²

    sum_Mx = 0.0
    sum_Mx2 = 0.0

    for M, x_cm in zip(zone_weights, deflections_cm):
        x = x_cm / 100.0  # convert to metres
        sum_Mx += M * x
        sum_Mx2 += M * (x ** 2)

    if sum_Mx2 <= 0:
        return {"frequency_hz": 1.0, "period_sec": 1.0}

    f = (1.0 / (2.0 * math.pi)) * math.sqrt(g * sum_Mx / sum_Mx2)
    T = 1.0 / f

    return {
        "frequency_hz": round(f, 5),
        "period_sec": round(T, 5),
        "sum_Mx": round(sum_Mx, 2),
        "sum_Mx2": round(sum_Mx2, 2)
    }


def estimate_deflections_for_rayleigh(
    zones: list,
    zone_weights: list,
    E: float = 2.1e6
) -> list:
    """
    Rough estimate of lateral deflections for Rayleigh method
    when a full structural analysis is not yet available.
    Uses a simplified cantilever approximation.
    """
    total_height = sum(z["length"] for z in zones)
    n = len(zones)
    deflections = []

    # Approximate top deflection (cm) – typical range  H/200 to H/300
    top_defl_cm = (total_height * 100) / 250.0

    for i in range(n):
        # Normalized height from base
        height_from_top = sum(zones[j]["length"] for j in range(i + 1))
        x_norm = 1.0 - (height_from_top - zones[i]["length"] / 2) / total_height
        # Cantilever-like shape
        defl = top_defl_cm * (x_norm ** 2)
        deflections.append(round(max(defl, 0.05), 2))

    return deflections


def approximate_mode_shapes(num_zones: int) -> dict:
    """
    Generate approximate mode shape ordinates for Mode 1, 2 and 3.
    Values are normalized so that the maximum absolute value = 1.0
    """
    shapes = {1: [], 2: [], 3: []}

    for i in range(num_zones):
        # x = 0 at top, 1 at base (we reverse later for consistency with Dynastac top-first)
        x = (i + 0.5) / num_zones          # 0 at top → 1 at base

        # Mode 1 – cantilever
        y1 = (1 - x) ** 1.8

        # Mode 2 – one node
        y2 = math.sin(2.2 * math.pi * (1 - x) / 2) * (0.6 + 0.4 * (1 - x))

        # Mode 3 – two nodes
        y3 = math.sin(3.8 * math.pi * (1 - x) / 2) * (0.5 + 0.5 * (1 - x))

        shapes[1].append(y1)
        shapes[2].append(y2)
        shapes[3].append(y3)

    # Normalize each mode
    for m in [1, 2, 3]:
        max_abs = max(abs(v) for v in shapes[m]) or 1.0
        shapes[m] = [round(v / max_abs, 4) for v in shapes[m]]

    return shapes


def critical_strouhal_velocity(top_od_m: float, natural_freq: float) -> float:
    """
    Critical wind speed for vortex shedding.
    Vcr = 5 × Dt × f    (IS 6533 Annex A, Amendment)
    """
    return 5.0 * top_od_m * natural_freq


def check_across_wind(
    top_od_mm: float,
    natural_freq: float,
    Vh_hmw: float
) -> dict:
    """
    Across-the-wind (Vortex Shedding) check as per IS 6533 Clause 8.4.1
    """
    Dt = top_od_mm / 1000.0
    Vcr = critical_strouhal_velocity(Dt, natural_freq)

    lower = 0.33 * Vh_hmw
    upper = 0.80 * Vh_hmw

    in_danger_zone = lower <= Vcr <= upper
    strakes_required = in_danger_zone

    return {
        "Vcr": round(Vcr, 2),
        "Vh": round(Vh_hmw, 2),
        "dangerous_range_lower": round(lower, 2),
        "dangerous_range_upper": round(upper, 2),
        "in_dangerous_range": in_danger_zone,
        "strakes_required": strakes_required,
        "conclusion": "Helical strakes are required" if strakes_required
                      else "Helical strakes are not required"
    }


def run_dynamic_analysis(
    zones: list,
    zone_weights: list,
    top_od_mm: float,
    Vb: float,
    terrain_category: int = 3
) -> dict:
    """
    Master function for dynamic analysis.
    """
    # 1. Estimate deflections and calculate natural frequency
    deflections = estimate_deflections_for_rayleigh(zones, zone_weights)
    freq_result = rayleigh_natural_frequency(zone_weights, deflections)

    # 2. Mode shapes
    mode_shapes = approximate_mode_shapes(len(zones))

    # 3. Approximate HMW at top for across-wind check
    from core.wind_loads import get_k2_factor
    K2_top = get_k2_factor(sum(z["length"] for z in zones), terrain_category)
    Vh = Vb * 0.90 * K2_top * 0.65

    # 4. Across-wind check
    across = check_across_wind(top_od_mm, freq_result["frequency_hz"], Vh)

    return {
        "natural_frequency": freq_result,
        "mode_shapes": mode_shapes,
        "deflections_used": deflections,
        "across_wind": across
    }
