"""
StackForge - Earthquake Module
As per IS 1893
"""

import math


# Zone Factor Fo (IS 1893)
ZONE_FACTOR = {
    "Zone 2": 0.10,
    "Zone 3": 0.16,
    "Zone 4": 0.24,
    "Zone 5": 0.36,
}

# Approximate Sa/g from response spectrum (5% damping, medium soil)
# Simplified for practical use
def get_sa_by_period(T: float) -> float:
    """
    Approximate spectral acceleration coefficient Sa/g
    for medium soil (Type II) – 5% damping.
    """
    if T <= 0.10:
        return 1.0 + 15.0 * T
    elif T <= 0.55:
        return 2.50
    elif T <= 4.00:
        return 1.36 / T
    else:
        return 0.34


def design_seismic_coefficient(
    T: float,
    zone: str = "Zone 4",
    importance: float = 1.5,
    beta: float = 1.5,
    performance_K: float = 1.0
) -> float:
    """
    αh = K × β × I × Fo × (Sa/g)

    This is the form we verified against Dynastac.
    """
    Fo = ZONE_FACTOR.get(zone, 0.24)
    Sa = get_sa_by_period(T)

    ah = performance_K * beta * importance * Fo * Sa
    return round(ah, 4)


def modal_participation_factor(weights: list, mode_shape: list) -> float:
    """
    Cr = Σ(W × Y) / Σ(W × Y²)
    """
    sum_WY = 0.0
    sum_WY2 = 0.0

    for W, Y in zip(weights, mode_shape):
        sum_WY += W * Y
        sum_WY2 += W * (Y ** 2)

    if abs(sum_WY2) < 1e-6:
        return 0.0

    return round(sum_WY / sum_WY2, 4)


def calculate_seismic_loads(
    zones: list,
    zone_weights: list,
    mode_shapes: dict,
    periods: dict,
    zone: str = "Zone 4",
    importance: float = 1.5,
    beta: float = 1.5,
    performance_K: float = 1.0
) -> dict:
    """
    Calculate design seismic coefficients and approximate
    horizontal forces for Mode 1, 2 and 3.
    """
    results = {"modes": {}, "zone_forces": []}

    for mode in [1, 2, 3]:
        T = periods.get(mode, 1.0)
        Y = mode_shapes.get(mode, [1.0] * len(zones))
        ah = design_seismic_coefficient(T, zone, importance, beta, performance_K)
        Cr = modal_participation_factor(zone_weights, Y)

        results["modes"][mode] = {
            "period": round(T, 4),
            "Sa_g": round(get_sa_by_period(T), 3),
            "ah": ah,
            "participation_factor": Cr
        }

    # Approximate lateral force distribution for Mode 1 (most important)
    Y1 = mode_shapes.get(1, [1.0] * len(zones))
    ah1 = results["modes"][1]["ah"]
    Cr1 = results["modes"][1]["participation_factor"]

    total_weight = sum(zone_weights)
    base_shear = ah1 * total_weight * abs(Cr1) * 0.6   # practical reduction factor

    # Distribute force proportional to W × Y
    WY = [w * y for w, y in zip(zone_weights, Y1)]
    sum_WY = sum(abs(v) for v in WY) or 1.0

    zone_forces = []
    for i, zone in enumerate(zones):
        force = base_shear * (abs(WY[i]) / sum_WY)
        zone_forces.append({
            "zone_no": zone["zone_no"],
            "weight": zone_weights[i],
            "Y": Y1[i],
            "force": round(force, 1)
        })

    results["base_shear"] = round(base_shear, 1)
    results["zone_forces"] = zone_forces

    return results


def run_earthquake_analysis(
    zones: list,
    zone_weights: list,
    mode_shapes: dict,
    natural_period: float,
    seismic_zone: str = "Zone 4",
    importance: float = 1.5
) -> dict:
    """
    Master function for earthquake analysis.
    """
    # Approximate higher mode periods
    periods = {
        1: natural_period,
        2: natural_period / 3.3,
        3: natural_period / 8.5
    }

    return calculate_seismic_loads(
        zones=zones,
        zone_weights=zone_weights,
        mode_shapes=mode_shapes,
        periods=periods,
        zone=seismic_zone,
        importance=importance
    )
