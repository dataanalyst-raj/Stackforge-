"""
StackForge - Flange Design Module
Based on the logic reverse-engineered from Dynastac + Brownell & Young
"""

import math
from utils.constants import (
    ALLOW_FLANGE_PLATE, ALLOW_BOLT_TENSION,
    MIN_BOLT_PITCH_FACTOR, MAX_BOLT_PITCH_FACTOR
)


# Standard bolt data: (size, root_area_mm2, across_flats_mm)
BOLT_DATA = {
    "M20": {"root_area": 245, "across_flats": 30, "dia": 20},
    "M24": {"root_area": 353, "across_flats": 36, "dia": 24},
    "M27": {"root_area": 459, "across_flats": 41, "dia": 27},
    "M30": {"root_area": 561, "across_flats": 46, "dia": 30},
    "M33": {"root_area": 694, "across_flats": 50, "dia": 33},
    "M36": {"root_area": 817, "across_flats": 55, "dia": 36},
}


def get_gamma_factors(b_over_l: float) -> tuple:
    """
    γ1 and γ2 from Brownell & Young Table 10.6 style.
    Interpolated values.
    """
    table = [
        (1.0, 0.565, 0.135),
        (1.2, 0.350, 0.115),
        (1.4, 0.211, 0.085),
        (1.6, 0.125, 0.057),
        (1.8, 0.073, 0.037),
        (2.0, 0.042, 0.023),
        (3.0, 0.010, 0.008),
    ]

    if b_over_l <= 1.0:
        return 0.565, 0.135
    if b_over_l >= 3.0:
        return 0.010, 0.008

    for i in range(1, len(table)):
        x1, g1_1, g2_1 = table[i-1]
        x2, g1_2, g2_2 = table[i]
        if b_over_l <= x2:
            r = (b_over_l - x1) / (x2 - x1)
            g1 = g1_1 + r * (g1_2 - g1_1)
            g2 = g2_1 + r * (g2_2 - g2_1)
            return round(g1, 3), round(g2, 3)

    return 0.042, 0.023


def calculate_bolt_force(M_kgm: float, N: int, PCD_mm: float, weight_above_kg: float) -> float:
    """
    F_bolt = 4M / (N × PCD) − P/N
    M in kg-m, PCD in mm → consistent units
    """
    M_kgcm = M_kgm * 100.0
    PCD_cm = PCD_mm / 10.0

    if N <= 0 or PCD_cm <= 0:
        return 0.0

    F = (4.0 * M_kgcm) / (N * PCD_cm) - (weight_above_kg / N)
    return max(F, 0.0)


def suggest_bolt_count(PCD_mm: float, bolt_dia_mm: float,
                       min_factor: float = 2.9, max_factor: float = 5.0) -> int:
    """
    Suggest number of bolts based on spacing rules.
    Min pitch = min_factor × d, Max pitch = max_factor × d
    """
    circumference = math.pi * PCD_mm
    min_pitch = min_factor * bolt_dia_mm
    max_pitch = max_factor * bolt_dia_mm

    # Start with a reasonable number and adjust
    n_min = math.ceil(circumference / max_pitch)
    n_max = math.floor(circumference / min_pitch)

    # Prefer a multiple of 4 for symmetry
    n = max(n_min, 8)
    while n % 4 != 0:
        n += 1
    if n > n_max:
        n = n_max if n_max >= 8 else n_min

    return max(n, 8)


def design_flange(
    shell_od_mm: float,
    moment_kgm: float,
    weight_above_kg: float,
    min_bolt_size: str = "M24",
    min_flange_thk: float = 12.0,
    corrosion_flange: float = 1.5,
    corrosion_bolt: float = 1.0
) -> dict:
    """
    Complete flange design for one section.
    """
    # 1. Geometry
    # PCD ≈ shell OD + 50 to 60 mm (typical edge distance)
    bolt_dia = BOLT_DATA.get(min_bolt_size, BOLT_DATA["M24"])["dia"]
    edge = max(50.0, 1.7 * bolt_dia)

    PCD = shell_od_mm + 2 * edge
    flange_od = PCD + 2 * edge
    flange_id = shell_od_mm - 2.0   # slightly inside shell

    # 2. Bolt count from spacing
    N = suggest_bolt_count(PCD, bolt_dia)

    # 3. Bolt force
    F_bolt = calculate_bolt_force(moment_kgm, N, PCD, weight_above_kg)

    # 4. Check / upgrade bolt size if needed
    root_area = BOLT_DATA[min_bolt_size]["root_area"]
    # Corroded area approximation
    corroded_area = root_area * ((bolt_dia - 2*corrosion_bolt)/bolt_dia)**2
    stress = (F_bolt * 10) / max(corroded_area, 1)   # kg/cm² approx

    bolt_size = min_bolt_size
    if stress > ALLOW_BOLT_TENSION * 0.85:
        # Try next larger bolt
        sizes = list(BOLT_DATA.keys())
        idx = sizes.index(min_bolt_size) if min_bolt_size in sizes else 0
        if idx + 1 < len(sizes):
            bolt_size = sizes[idx + 1]
            bolt_dia = BOLT_DATA[bolt_size]["dia"]
            N = suggest_bolt_count(PCD, bolt_dia)
            F_bolt = calculate_bolt_force(moment_kgm, N, PCD, weight_above_kg)

    # 5. Flange plate thickness (simplified Brownell style)
    b = math.pi * PCD / N          # spacing
    a = (flange_od - flange_id) / 2.0
    b_over_a = b / max(a, 1.0)

    g1, g2 = get_gamma_factors(b_over_a)

    # Approximate moment in plate (simplified)
    # Using a practical form close to what we verified
    e = BOLT_DATA[bolt_size]["across_flats"] / 2.0
    mu = 0.30

    # Simplified My (Eq 10.40 style)
    if e > 0 and a > 0:
        My = (F_bolt / (4 * math.pi)) * ((1 + mu) * math.log(max(2 * a / (math.pi * e), 1.01)) + (1 - g1))
    else:
        My = F_bolt * 0.15

    My = abs(My)

    # Required thickness from bending
    # σ = 6M / t²  → t = sqrt(6M / σ_allow)
    t_req = math.sqrt(6.0 * My / ALLOW_FLANGE_PLATE) * 10  # to mm
    t_corroded = t_req
    t_nominal = max(t_corroded + corrosion_flange, min_flange_thk)

    # Round to practical thickness
    practical = [12, 14, 16, 18, 20, 22, 25, 28, 30]
    t_final = next((p for p in practical if p >= t_nominal - 0.1), 16)

    # 6. Weight of flange pair (approx)
    area = math.pi / 4 * ((flange_od/1000)**2 - (flange_id/1000)**2)
    weight_pair = area * (t_final/1000) * 7850 * 2

    return {
        "shell_od": round(shell_od_mm, 1),
        "flange_od": round(flange_od, 1),
        "flange_id": round(flange_id, 1),
        "thickness": t_final,
        "bolt_size": bolt_size,
        "PCD": round(PCD, 1),
        "num_bolts": N,
        "bolt_force": round(F_bolt, 1),
        "bolt_stress": round(stress, 1),
        "plate_My": round(My, 1),
        "weight_pair": round(weight_pair, 1),
        "status": "OK" if stress < ALLOW_BOLT_TENSION else "Check Bolt"
    }


def design_all_flanges(
    zones: list,
    moments: list,
    cumulative_weights: list,
    min_bolt_size: str = "M24",
    min_flange_thk: float = 12.0
) -> list:
    """
    Design flanges at each section boundary.
    """
    flanges = []
    for i, zone in enumerate(zones):
        M = moments[i] if i < len(moments) else 10000
        W = cumulative_weights[i] if i < len(cumulative_weights) else 5000
        shell_od = zone["bottom_od"] if i == len(zones)-1 else zone["mean_od"]

        fl = design_flange(
            shell_od_mm=shell_od,
            moment_kgm=M,
            weight_above_kg=W,
            min_bolt_size=min_bolt_size,
            min_flange_thk=min_flange_thk
        )
        fl["section"] = i + 1
        flanges.append(fl)

    return flanges
