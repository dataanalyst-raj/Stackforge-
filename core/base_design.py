"""
StackForge - Base Chair Design Module
Foundation Bolts, Base Plate, Compression Plate, Gussets
"""

import math
from utils.constants import ALLOW_BASE_PLATE, ALLOW_BOLT_TENSION


def calculate_foundation_bolt_force(M_kgm: float, N: int, Db_mm: float) -> float:
    """
    Pb = 4M / (N × Db)
    """
    M_kgcm = M_kgm * 100.0
    Db_cm = Db_mm / 10.0
    if N <= 0 or Db_cm <= 0:
        return 0.0
    return (4.0 * M_kgcm) / (N * Db_cm)


def suggest_foundation_bolts(
    moment_kgm: float,
    base_od_mm: float,
    min_bolts: int = 12
) -> dict:
    """
    Suggest number and size of foundation bolts.
    """
    # Bolt circle ≈ 0.85 × Base OD (typical)
    Db = base_od_mm * 0.85

    # Try different bolt counts (multiple of 4)
    best = None
    for N in range(max(min_bolts, 12), 49, 4):
        Pb = calculate_foundation_bolt_force(moment_kgm, N, Db)
        # Required root area
        area_req = (Pb * 10) / (ALLOW_BOLT_TENSION * 0.8)  # mm² with margin

        if area_req < 245:
            size = "M20"
        elif area_req < 353:
            size = "M24"
        elif area_req < 459:
            size = "M27"
        elif area_req < 561:
            size = "M30"
        elif area_req < 694:
            size = "M33"
        elif area_req < 817:
            size = "M36"
        else:
            size = "M42"

        best = {
            "num_bolts": N,
            "bolt_size": size,
            "bolt_circle": round(Db, 1),
            "bolt_force": round(Pb, 1),
            "required_area": round(area_req, 1)
        }
        # Prefer reasonable spacing
        pitch = math.pi * Db / N
        if 80 < pitch < 280:
            break

    return best or {
        "num_bolts": 16,
        "bolt_size": "M30",
        "bolt_circle": round(Db, 1),
        "bolt_force": 0,
        "required_area": 0
    }


def base_plate_thickness(
    l_mm: float,
    b_mm: float,
    fc_kgcm2: float,
    allow_stress: float = ALLOW_BASE_PLATE
) -> dict:
    """
    Base plate thickness using l/b ratio method (Brownell Table 10.3 style).
    """
    l = l_mm / 10.0  # cm
    b = b_mm / 10.0  # cm
    ratio = l / max(b, 0.1)

    # Approximate coefficient Cx (free edge) for l/b ≈ 0.7
    if ratio <= 0.67:
        Cx = 0.05
    elif ratio <= 1.0:
        Cx = 0.055 + (ratio - 0.67) * 0.12
    else:
        Cx = 0.10 + min(ratio - 1.0, 1.0) * 0.03

    M_max = Cx * fc_kgcm2 * (b ** 2)  # kg-cm / cm

    t_req = math.sqrt(6.0 * M_max / allow_stress)  # cm
    t_mm = t_req * 10.0

    return {
        "l_mm": l_mm,
        "b_mm": b_mm,
        "l_over_b": round(ratio, 3),
        "M_max": round(M_max, 1),
        "t_required_mm": round(t_mm, 1),
        "t_practical_mm": math.ceil(t_mm / 2) * 2  # even mm
    }


def gusset_check(
    load_kg: float,
    thickness_mm: float,
    height_mm: float,
    corrosion_mm: float = 1.0
) -> dict:
    """
    Simple gusset check as per IS 800 (compression + slenderness).
    """
    t_corr = max(thickness_mm - corrosion_mm, 1.0)
    # ry ≈ t / sqrt(12) for rectangular strip
    ry = t_corr / math.sqrt(12)
    slenderness = height_mm / max(ry, 0.1)

    # Approximate allowable (IS 800 Table 5.1 style)
    if slenderness <= 50:
        fa = 150
    elif slenderness <= 100:
        fa = 140 - (slenderness - 50) * 0.6
    elif slenderness <= 150:
        fa = 110 - (slenderness - 100) * 0.7
    else:
        fa = 50

    area = t_corr * 100  # assume 100 mm effective width
    stress = (load_kg / max(area, 1)) * 10  # rough kg/cm²

    return {
        "thickness": thickness_mm,
        "height": height_mm,
        "slenderness": round(slenderness, 1),
        "induced_stress": round(stress, 1),
        "allowable_stress": round(fa, 1),
        "status": "OK" if stress < fa else "Increase thickness"
    }


def design_base_chair(
    base_moment_kgm: float,
    base_shear_kg: float,
    total_weight_kg: float,
    skirt_od_mm: float,
    base_plate_width_mm: float = 300,
    num_bolts_preference: int = 0
) -> dict:
    """
    Complete Base Chair design.
    """
    base_od = skirt_od_mm + 2 * base_plate_width_mm

    # 1. Foundation bolts
    bolts = suggest_foundation_bolts(base_moment_kgm, base_od)
    if num_bolts_preference >= 12:
        bolts["num_bolts"] = num_bolts_preference
        bolts["bolt_force"] = round(
            calculate_foundation_bolt_force(
                base_moment_kgm, num_bolts_preference, bolts["bolt_circle"]
            ), 1
        )

    # 2. Base plate
    l = base_plate_width_mm
    b = math.pi * bolts["bolt_circle"] / bolts["num_bolts"]  # gusset spacing
    # Approximate concrete stress
    fc = 20.0  # kg/cm² typical
    plate = base_plate_thickness(l, b, fc)

    # 3. Gussets
    load_per_gusset = bolts["bolt_force"]
    gusset = gusset_check(load_per_gusset, thickness_mm=10, height_mm=350)

    # 4. Compression plate (simplified)
    comp_thk = max(plate["t_practical_mm"] - 4, 16)

    return {
        "base_od": round(base_od, 1),
        "skirt_od": round(skirt_od_mm, 1),
        "base_plate_width": base_plate_width_mm,
        "bolts": bolts,
        "base_plate": plate,
        "compression_plate_thk": comp_thk,
        "gusset": gusset,
        "total_weight_on_base": round(total_weight_kg, 1),
        "base_moment": base_moment_kgm,
        "base_shear": base_shear_kg
    }
