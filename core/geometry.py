"""
StackForge - Geometry Module (Improved)
Accurate shell zoning matching Dynastac style
"""

from utils.constants import FLARE_FACTOR_UNLINED, FLARE_FACTOR_LINED


def calculate_flare_height(total_height: float, top_id_mm: float, is_lined: bool = False) -> float:
    """
    Flare Height = MAX( H/3 , H - factor × ID_top/1000 )
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
    Generate shell zones in Dynastac style.

    - Cylindrical portion first (constant diameter)
    - Then conical (flare) portion with linearly increasing diameter
    - Practical zone lengths (usually 4–7 m)
    - Returns list of zone dictionaries
    """
    zones = []
    zone_no = 1

    cylindrical_height = max(total_height - flare_height, 0.0)

    # -------------------------------------------------------
    # 1. Cylindrical Portion
    # -------------------------------------------------------
    if cylindrical_height > 0.05:
        remaining = cylindrical_height
        while remaining > 0.05:
            # Prefer preferred_zone_length, but avoid very short last zone
            if remaining <= preferred_zone_length + 1.5:
                length = remaining
            else:
                length = preferred_zone_length

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

    # -------------------------------------------------------
    # 2. Conical (Flare) Portion
    # -------------------------------------------------------
    if flare_height > 0.05:
        remaining = flare_height
        current_top_od = top_od
        od_increase_per_meter = (bottom_od - top_od) / flare_height

        while remaining > 0.05:
            if remaining <= preferred_zone_length + 1.5:
                length = remaining
            else:
                length = preferred_zone_length

            bottom_od_zone = current_top_od + od_increase_per_meter * length

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
    Corroded section properties for thin cylindrical shell.
    Area in cm², Z in cm³, I in cm⁴
    """
    D = od_mm / 10.0          # cm
    t = thickness_mm / 10.0   # cm

    area = 3.14159265 * D * t
    I = 3.14159265 * (D ** 3) * t / 8.0
    Z = 2.0 * I / D

    return {
        "area_cm2": round(area, 2),
        "I_cm4": round(I, 1),
        "Z_cm3": round(Z, 1)
    }


def print_zone_summary(zones: list) -> str:
    """Helper to display zones cleanly"""
    lines = []
    lines.append(f"{'Zone':<6} {'Portion':<12} {'Length':>8} {'Top OD':>10} {'Bottom OD':>10} {'Mean OD':>10}")
    lines.append("-" * 60)
    for z in zones:
        lines.append(
            f"{z['zone_no']:<6} {z['portion']:<12} {z['length']:>8.2f} "
            f"{z['top_od']:>10.1f} {z['bottom_od']:>10.1f} {z['mean_od']:>10.1f}"
        )
    return "\n".join(lines)
