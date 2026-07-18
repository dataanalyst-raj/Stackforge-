"""
StackForge - Geometry Module
Handles shell geometry, zoning and flare height calculation
"""

from utils.constants import FLARE_FACTOR_UNLINED, FLARE_FACTOR_LINED


def calculate_flare_height(total_height: float, top_id_mm: float, is_lined: bool = False) -> float:
    """
    Calculate suggested Flare Height.

    Formula:
        Flare Height = MAX( H/3 , H - factor * ID_top/1000 )

    factor = 20 (Unlined), 25 (Lined)
    """
    factor = FLARE_FACTOR_LINED if is_lined else FLARE_FACTOR_UNLINED

    option1 = total_height / 3.0
    option2 = total_height - factor * (top_id_mm / 1000.0)

    return max(option1, option2)


def generate_shell_zones(
    total_height: float,
    flare_height: float,
    top_od: float,
    bottom_od: float,
    preferred_zone_length: float = 6.0
) -> list:
    """
    Generate shell zones (Cylindrical + Conical portions).

    Returns list of zone dictionaries:
    [
        {
            "zone_no": 1,
            "portion": "Cylindrical" or "Conical",
            "length": m,
            "top_od": mm,
            "bottom_od": mm,
            "mean_od": mm
        },
        ...
    ]
    """
    zones = []
    zone_no = 1

    cylindrical_height = total_height - flare_height

    # ----- Cylindrical Portion -----
    if cylindrical_height > 0.1:
        remaining = cylindrical_height
        while remaining > 0.1:
            length = min(preferred_zone_length, remaining)
            # Avoid very short last zone
            if remaining - length < 1.5 and remaining - length > 0.1:
                length = remaining

            zones.append({
                "zone_no": zone_no,
                "portion": "Cylindrical",
                "length": round(length, 2),
                "top_od": round(top_od, 1),
                "bottom_od": round(top_od, 1),
                "mean_od": round(top_od, 1)
            })
            zone_no += 1
            remaining -= length

    # ----- Conical (Flare) Portion -----
    if flare_height > 0.1:
        remaining = flare_height
        current_top_od = top_od
        od_increase_per_m = (bottom_od - top_od) / flare_height

        while remaining > 0.1:
            length = min(preferred_zone_length, remaining)
            if remaining - length < 1.5 and remaining - length > 0.1:
                length = remaining

            bottom_od_zone = current_top_od + od_increase_per_m * length

            zones.append({
                "zone_no": zone_no,
                "portion": "Conical",
                "length": round(length, 2),
                "top_od": round(current_top_od, 1),
                "bottom_od": round(bottom_od_zone, 1),
                "mean_od": round((current_top_od + bottom_od_zone) / 2.0, 1)
            })

            current_top_od = bottom_od_zone
            zone_no += 1
            remaining -= length

    return zones


def get_section_properties(od_mm: float, thickness_mm: float) -> dict:
    """
    Calculate corroded section properties for a thin cylindrical shell.
    Returns Area (cm²) and Section Modulus Z (cm³)
    """
    D = od_mm / 10.0          # cm
    t = thickness_mm / 10.0   # cm

    # Thin wall approximation
    area = 3.1416 * D * t                    # cm²
    I = 3.1416 * D**3 * t / 8.0              # cm⁴
    Z = 2.0 * I / D                          # cm³

    return {
        "area_cm2": round(area, 1),
        "I_cm4": round(I, 1),
        "Z_cm3": round(Z, 1)
    }
