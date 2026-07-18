"""
StackForge - Dynamic Analysis Module (Improved v2)
Better Natural Frequency using improved deflections
"""

import math


def rayleigh_natural_frequency(zone_weights: list, deflections_cm: list) -> dict:
    """
    Rayleigh method as per IS 6533 Part 2 Clause 8.3.1
    f = (1 / 2π) * sqrt( g * Σ(M·δ) / Σ(M·δ²) )
    """
    g = 981.0  # cm/s²

    sum_M_delta = 0.0
    sum_M_delta2 = 0.0

    for M, delta in zip(zone_weights, deflections_cm):
        sum_M_delta += M * delta
        sum_M_delta2 += M * (delta ** 2)

    if sum_M_delta2 < 1e-6:
        return {"frequency_hz": 1.0, "period_sec": 1.0}

    f = (1.0 / (2.0 * math.pi)) * math.sqrt(g * sum_M_delta / sum_M_delta2)
    T = 1.0 / f

    return {
        "frequency_hz": round(f, 4),
        "period_sec": round(T, 4),
        "sum_M_delta": round(sum_M_delta, 1),
        "sum_M_delta2": round(sum_M_delta2, 1)
    }


def estimate_deflections(zones: list, zone_weights: list) -> list:
    """
    Improved approximate deflections for Rayleigh method.
    Uses a realistic cantilever shape scaled to expected top deflection.
    """
    n = len(zones)
    total_height_m = sum(z["length"] for z in zones)
    total_height_cm = total_height_m * 100.0

    # Expected top deflection range for steel chimneys (H/200 to H/350)
    target_top_defl_cm = total_height_cm / 260.0

    deflections = []
    for i in range(n):
        # Normalized height from base (0 at base, 1 at top)
        height_from_top = sum(zones[j]["length"] for j in range(i+1))
        x = 1.0 - (height_from_top - zones[i]["length"]/2) / total_height_m
        x = max(min(x, 1.0), 0.0)

        # Cantilever-like shape (more realistic than simple x²)
        shape = x ** 1.8

        deflections.append(round(target_top_defl_cm * shape, 2))

    return deflections


def approximate_mode_shapes(num_zones: int) -> dict:
    """
    Approximate mode shapes normalized to 1.0 at the point of maximum amplitude.
    """
    shapes = {1: [], 2: [], 3: []}

    for i in range(num_zones):
        # x = 0 at top, 1 at base
        x = (i + 0.5) / num_zones

        # Mode 1
        y1 = (1 - x) ** 1.75

        # Mode 2
        y2 = math.sin(2.2 * math.pi * (1 - x) / 2.0) * (0.55 + 0.45 * (1 - x))

        # Mode 3
        y3 = math.sin(3.8 * math.pi * (1 - x) / 2.0) * (0.5 + 0.5 * (1 - x))

        shapes[1].append(y1)
        shapes[2].append(y2)
        shapes[3].append(y3)

    # Normalize
    for m in [1, 2, 3]:
        max_val = max(abs(v) for v in shapes[m]) or 1.0
        shapes[m] = [round(v / max_val, 4) for v in shapes[m]]

    return shapes


def critical_strouhal_velocity(top_od_m: float, natural_freq: float) -> float:
    """Vcr = 5 × Dt × f   (IS 6533 Annex A)"""
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
    # Deflections
    deflections = estimate_deflections(zones, zone_weights)

    # Natural Frequency
    freq_result = rayleigh_natural_frequency(zone_weights, deflections)

    # Mode shapes
    mode_shapes = approximate_mode_shapes(len(zones))

    # Across wind check
    from core.wind_loads import get_k2_factor
    total_height = sum(z["length"] for z in zones)
    K2_top = get_k2_factor(total_height, terrain_category)
    Vh = Vb * 0.90 * K2_top * 0.65

    across = check_across_wind(top_od_mm, freq_result["frequency_hz"], Vh)

    return {
        "natural_frequency": freq_result,
        "mode_shapes": mode_shapes,
        "deflections_used": deflections,
        "across_wind": across
    }
