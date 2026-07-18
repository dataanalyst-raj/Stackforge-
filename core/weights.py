"""
StackForge - Weights Module (Improved)
More accurate zone-wise weights matching Dynastac style
"""

from utils.constants import STEEL_DENSITY


def calculate_shell_weight(mean_od_mm: float, length_m: float, thickness_mm: float,
                           density: float = STEEL_DENSITY) -> float:
    """
    Shell weight (uncorroded) = π × D × L × t × density
    """
    D = mean_od_mm / 1000.0
    t = thickness_mm / 1000.0
    volume = 3.14159265 * D * t * length_m
    return round(volume * density, 1)


def calculate_platform_weight(shell_od_mm: float, platform_width_mm: float = 900,
                              sweep_deg: float = 360, self_weight: float = 160) -> float:
    """
    Platform weight based on floor area.
    Effective OD = Shell OD + Platform Width
    """
    Deff = (shell_od_mm + platform_width_mm) / 1000.0
    width = platform_width_mm / 1000.0
    arc_length = 3.14159265 * Deff * (sweep_deg / 360.0)
    area = arc_length * width
    return round(area * self_weight, 1)


def calculate_ladder_weight(length_m: float, weight_per_m: float = 50.0) -> float:
    return round(length_m * weight_per_m, 1)


def calculate_strake_weight(mean_od_mm: float, length_m: float,
                            thickness_mm: float = 6.0, density: float = STEEL_DENSITY) -> float:
    """
    Approximate helical strake weight (top portion only)
    """
    D = mean_od_mm / 1000.0
    t = thickness_mm / 1000.0
    # Practical approximation used in many designs
    volume = 3.14159265 * D * t * length_m * 0.16
    return round(volume * density, 1)


def calculate_zone_weights(
    zones: list,
    thicknesses: list,
    platform_elevations: list = None,
    platform_width_mm: float = 900,
    platform_self_weight: float = 160,
    ladder_weight_per_m: float = 50.0,
    provide_strakes: bool = False,
    strake_thickness: float = 6.0,
    misc_weight: float = 1200.0,
    contingency: float = 500.0
) -> dict:
    """
    Calculate complete zone-wise and total weights.
    """
    if platform_elevations is None:
        platform_elevations = []

    zone_results = []
    total_shell = 0.0
    total_platform = 0.0
    total_ladder = 0.0
    total_strakes = 0.0

    total_height = sum(z["length"] for z in zones)
    height_from_base = total_height

    for i, zone in enumerate(zones):
        length = zone["length"]
        mean_od = zone["mean_od"]
        thk = thicknesses[i] if i < len(thicknesses) else 10.0

        # Shell
        shell_wt = calculate_shell_weight(mean_od, length, thk)
        total_shell += shell_wt

        # Ladder (full height)
        ladder_wt = calculate_ladder_weight(length, ladder_weight_per_m)
        total_ladder += ladder_wt

        # Strakes (usually provided on upper 1/3 to 1/2)
        strake_wt = 0.0
        if provide_strakes and height_from_base > total_height * 0.55:
            strake_wt = calculate_strake_weight(mean_od, length, strake_thickness)
            total_strakes += strake_wt

        # Platforms
        platform_wt = 0.0
        zone_top = height_from_base
        zone_bottom = height_from_base - length

        for elev in platform_elevations:
            if zone_bottom <= elev <= zone_top:
                platform_wt += calculate_platform_weight(
                    mean_od, platform_width_mm, 360, platform_self_weight
                )
        total_platform += platform_wt

        zone_total = shell_wt + platform_wt + ladder_wt + strake_wt

        zone_results.append({
            "zone_no": zone["zone_no"],
            "portion": zone["portion"],
            "length": length,
            "mean_od": mean_od,
            "thickness": thk,
            "shell_weight": shell_wt,
            "platform_weight": round(platform_wt, 1),
            "ladder_weight": ladder_wt,
            "strake_weight": strake_wt,
            "zone_total": round(zone_total, 1)
        })

        height_from_base -= length

    # Add misc + contingency to the bottom zone
    if zone_results:
        zone_results[-1]["zone_total"] += misc_weight + contingency
        zone_results[-1]["zone_total"] = round(zone_results[-1]["zone_total"], 1)

    grand_total = total_shell + total_platform + total_ladder + total_strakes + misc_weight + contingency

    return {
        "zones": zone_results,
        "summary": {
            "shell_weight": round(total_shell, 1),
            "platform_weight": round(total_platform, 1),
            "ladder_weight": round(total_ladder, 1),
            "strake_weight": round(total_strakes, 1),
            "misc_weight": round(misc_weight, 1),
            "contingency": round(contingency, 1),
            "grand_total": round(grand_total, 1)
        }
    }


def get_cumulative_weights(zone_weights: list) -> list:
    """
    Cumulative weight from top (for axial force calculation)
    """
    cumulative = []
    running = 0.0
    for zone in zone_weights:
        running += zone["zone_total"]
        cumulative.append(round(running, 1))
    return cumulative
