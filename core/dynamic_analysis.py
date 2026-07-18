"""
StackForge - Dynamic Analysis Module (Improved)
Natural Frequency (Rayleigh with better deflections), Mode Shapes, Across-Wind
"""

import math


def rayleigh_natural_frequency(zone_weights: list, deflections_cm: list) -> dict:
    """
    Rayleigh method - IS 6533 Part 2 Clause 8.3.1
    f = (1/2π) * sqrt( g * Σ(M·x) / Σ(M·x²) )
    """
    g = 981.0  # cm/s²

    sum_Mx = 0.0
    sum_Mx2 = 0.0

    for M, x in zip(zone_weights, deflections_cm):
        sum_Mx += M * x
        sum_Mx2 += M * (x ** 2)

    if sum_Mx2 <= 1e-6:
        return {"frequency_hz": 1.0, "period_sec": 1.0, "sum_Mx": 0, "sum_Mx2": 0}

    f = (1.0 / (2.0 * math.pi)) * math.sqrt(g * sum_Mx / sum_Mx2)
    T = 1.0 / f

    return {
        "frequency_hz": round(f, 4),
        "period_sec": round(T, 4),
        "sum_Mx": round(sum_Mx, 1),
        "sum_Mx2": round(sum_Mx2, 1)
    }


def estimate_deflections_moment_area(zones: list, zone_weights: list, E: float = 2.1e6) -> list:
    """
    Improved deflection estimate using approximate Moment-Area approach.
    """
    n = len(zones)
    total_height = sum(z["length"] for z in zones)

    I_list = []
    for z in zones:
        D = z["mean_od"] / 10.0   # cm
        t = 1.0
        I = math.pi * (D ** 3) * t / 8.0
        I_list.append(max(I, 100.0))

    shears = []
    moments = []
    V = 0.0
    M = 0.0
    for i in range(n):
        V += zone_weights[i]
        shears.append(V)
        M += zone_weights[i] * (zones[i]["length"] * 100 / 2.0) + (shears[i-1] if i > 0 else 0) * (zones[i]["length"] * 100)
        moments.append(M)

    slopes = [0.0] * n
    deflections = [0.0] * n

    theta = 0.0
    y = 0.0
    for i in range(n-1, -1, -1):
        L = zones[i]["length"] * 100
        EI = E * I_list[i]
        M_avg = moments[i]
        d_theta = M_avg * L / EI
        d_y = theta * L + 0.5 * d_theta * L
        theta += d_theta
        y += d_y
        deflections[i] = y

    top_defl = deflections[0] if deflections[0] > 0 else 1.0
    target_top = (total_height * 100) / 280.0
    scale = target_top / top_defl

    deflections = [max(d * scale, 0.05) for d in deflections]
    return [round(d, 2) for d in deflections]


def approximate_mode_shapes(num_zones: int) -> dict:
    shapes = {1: [], 2: [], 3: []}
    for i in range(num_zones):
        x = (i + 0.5) / num_zones

        y1 = (1 - x) ** 1.75
        y2 = math.sin(2.25 * math.pi * (1 - x) / 2) * (0.6 + 0.4 * (1 - x))
        y3 = math.sin(3.9 * math.pi * (1 - x) / 2) * (0.5 + 0.5 * (1 - x))

        shapes[1].append(y1)
        shapes[2].append(y2)
        shapes[3].append(y3)

    for m in [1, 2, 3]:
        max_abs = max(abs(v) for v in shapes[m]) or 1.0
        shapes[m] = [round(v / max_abs, 4) for v in shapes[m]]
    return shapes


def critical_strouhal_velocity(top_od_m: float, natural_freq: float) -> float:
    return 5.0 * top_od_m * natural_freq


def check_across_wind(top_od_mm: float, natural_freq: float, Vh_hmw: float) -> dict:
    Dt = top_od_mm / 1000.0
    Vcr = critical_strouhal_velocity(Dt, natural_freq)
    lower = 0.33 * Vh_hmw
    upper = 0.80 * Vh_hmw
    in_danger = lower <= Vcr <= upper

    return {
        "Vcr": round(Vcr, 2),
        "Vh": round(Vh_hmw, 2),
        "dangerous_range_lower": round(lower, 2),
        "dangerous_range_upper": round(upper, 2),
        "in_dangerous_range": in_danger,
        "strakes_required": in_danger,
        "conclusion": "Helical strakes are required" if in_danger else "Helical strakes are not required"
    }


def run_dynamic_analysis(zones: list, zone_weights: list, top_od_mm: float,
                          Vb: float, terrain_category: int = 3) -> dict:
    deflections = estimate_deflections_moment_area(zones, zone_weights)
    freq_result = rayleigh_natural_frequency(zone_weights, deflections)
    mode_shapes = approximate_mode_shapes(len(zones))

    from core.wind_loads import get_k2_factor
    K2_top = get_k2_factor(sum(z["length"] for z in zones), terrain_category)
    Vh = Vb * 0.90 * K2_top * 0.67

    across = check_across_wind(top_od_mm, freq_result["frequency_hz"], Vh)

    return {
        "natural_frequency": freq_result,
        "mode_shapes": mode_shapes,
        "deflections_used": deflections,
        "across_wind": across
    }
