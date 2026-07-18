"""
StackForge - Weights Module
Calculates shell weights, platform weights, ladder, strakes and total weights
"""

from utils.constants import STEEL_DENSITY


def calculate_shell_weight(
    mean_od_mm: float,
    length_m: float,
    thickness_mm: float,
    density: float = STEEL_DENSITY
) -> float:
    """
    Calculate weight of a cylindrical / conical shell zone.

    Weight (kg) = π × D_mean × L × t × density
    (all dimensions converted to metres)
    """
    D = mean_od_mm / 1000.0          # m
    t = thickness_mm / 1000.0        # m
    L = length_m

    volume = 3.1416 * D * t * L      # m³
    weight = volume * density        # kg

    return round(weight, 1)


def calculate_platform_weight(
    diameter_mm: float,
    platform_width_mm: float = 900,
    sweep_angle_deg: float = 360,
    self_weight_kg_m2: float = 160
) -> float:
    """
    Calculate platform weight.

    Effective diameter = Shell OD + Platform Width
    Arc length = π × Deff × (sweep/360)
    Area ≈ Arc length × Platform Width
    Weight = Area × self_weight
    """
    Deff = (diameter_mm + platform_width_mm) / 1000.0   # m
    width = platform_width_mm / 1000.0                  # m

    arc_length = 3.1416 * Deff * (sweep_angle_deg / 360.0)
    area = arc_length * width                           # m²
    weight = area * self_weight_kg_m2

    return round(weight, 1)


def calculate_ladder_weight(
    height_m: float,
    weight_per_m: float = 45.0
) -> float:
    """Ladder weight = height × weight per metre"""
    return round(height_m * weight_per_m, 1)


def calculate_strake_weight(
    mean_od_mm: float,
    length_m: float,
    thickness_mm: float = 6.0,
    density: float = STEEL_DENSITY
) -> float:
    """
    Approximate weight of helical strakes.
    Simplified as additional surface area.
    """
    # Rough approximation used in practice
    D = mean_od_mm / 1000.0
    t = thickness_mm / 1000.0
    # Assume strakes add roughly 15-20% extra surface in the top portion
    volume = 3.1416 * D * t * length_m * 0.18
    return round(volume * density, 1)


def calculate_zone_weights(
    zones: list,
    thicknesses: list,
    platform_elevations: list = None,
    platform_width_mm: float = 900,
    platform_self_weight: float = 160,
    ladder_weight_per_m: float = 45.0,
    provide_strakes: bool = False,
    strake_thickness: float = 6.0,
    misc_weight: float = 0.0,
    contingency: float = 0.0
) -> dict:
    """
    Calculate complete weight breakdown for all zones.

    Parameters:
        zones: list from generate_shell_zones()
        thicknesses: list of nominal thicknesses (mm) for each zone
        platform_elevations: list of elevations from base (m) where platforms are located

    Returns:
        Dictionary containing zone-wise and total weights.
    """
    if platform_elevations is None:
        platform_elevations = []

    zone_results = []
    total_shell = 0.0
    total_platform = 0.0
    total_ladder = 0.0
    total_strakes = 0.0

    cumulative_height_from_base = 0.0
    total_height = sum(z["length"] for z in zones)

    for i, zone in enumerate(zones):
        length = zone["length"]
        mean_od = zone["mean_od"]
        thk = thicknesses[i] if i < len(thicknesses) else 10.0

        # Shell weight
        shell_wt = calculate_shell_weight(mean_od, length, thk)
        total_shell += shell_wt

        # Ladder (distributed along height)
        ladder_wt = calculate_ladder_weight(length, ladder_weight_per_m)
        total_ladder += ladder_wt

        # Strakes (usually only on upper portion)
        strake_wt = 0.0
        if provide_strakes and cumulative_height_from_base + length > total_height * 0.6:
            strake_wt = calculate_strake_weight(mean_od, length, strake_thickness)
            total_strakes += strake_wt

        # Platforms (check if any platform lies in this zone)
        platform_wt = 0.0
        zone_bottom = cumulative_height_from_base
        zone_top = cumulative_height_from_base + length

        for elev in platform_elevations:
            if zone_bottom <= elev <= zone_top:
                platform_wt += calculate_platform_weight(
                    mean_od, platform_width_mm, 360, platform_self_weight
                )

        total_platform += platform_wt

        zone_results.append({
            "zone_no": zone["zone_no"],
            "portion": zone["portion"],
            "length": length,
            "mean_od": mean_od,
            "thickness": thk,
            "shell_weight": shell_wt,
            "platform_weight": platform_wt,
            "ladder_weight": ladder_wt,
            "strake_weight": strake_wt,
            "zone_total": round(shell_wt + platform_wt + ladder_wt + strake_wt, 1)
        })

        cumulative_height_from_base += length

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
    Return cumulative weight from top for each section
    (used for axial force in stress calculations).
    """
    cumulative = []
    running = 0.0

    for zone in zone_weights:
        running += zone["zone_total"]
        cumulative.append(round(running, 1))

    return cumulative
