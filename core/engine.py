"""
StackForge - Master Calculation Engine
Orchestrates all design modules and returns complete results
"""

from core.geometry import (
    calculate_flare_height,
    generate_shell_zones,
    get_section_properties
)
from core.thickness import design_shell_thicknesses, iterate_thickness
from core.weights import calculate_zone_weights, get_cumulative_weights
from core.wind_loads import calculate_all_wind_loads
from core.dynamic_analysis import run_dynamic_analysis
from core.earthquake import run_earthquake_analysis
from core.flange_design import design_all_flanges
from core.base_design import design_base_chair
from core.shell_stress import run_shell_stress_analysis


def run_complete_design(inputs: dict) -> dict:
    """
    Master function – runs the complete chimney design.

    Parameters
    ----------
    inputs : dict
        Dictionary of all user inputs (from InputPanel.get_all_inputs())

    Returns
    -------
    dict
        Complete design results ready for display and reporting.
    """

    # ------------------------------------------------------------------
    # 1. Basic Geometry
    # ------------------------------------------------------------------
    H = inputs["total_height"]
    top_id = inputs["top_id"]
    is_lined = inputs["is_lined"]
    bottom_od = inputs["bottom_od"]
    top_od = top_id + 2 * 6   # approximate initial top OD (will be refined)

    # Flare height
    if inputs.get("flare_height", 0) > 0.5:
        flare_height = inputs["flare_height"]
    else:
        flare_height = calculate_flare_height(H, top_id, is_lined)

    # Generate zones
    zones = generate_shell_zones(
        total_height=H,
        flare_height=flare_height,
        top_od=top_od,
        bottom_od=bottom_od,
        preferred_zone_length=6.0
    )

    if not zones:
        return {"error": "Could not generate shell zones. Check geometry inputs."}

    # ------------------------------------------------------------------
    # 2. Preliminary Weights (assume trial thicknesses)
    # ------------------------------------------------------------------
    trial_thicknesses = [10.0] * len(zones)
    # Increase thickness towards bottom
    for i in range(len(trial_thicknesses)):
        trial_thicknesses[i] = 8.0 + i * 1.5

    platform_elevs = []
    if inputs.get("num_platforms", 0) > 0:
        # Simple distribution of platforms
        n_plat = inputs["num_platforms"]
        for i in range(n_plat):
            elev = H * (0.9 - i * 0.35)
            if elev > 2:
                platform_elevs.append(elev)

    weight_data = calculate_zone_weights(
        zones=zones,
        thicknesses=trial_thicknesses,
        platform_elevations=platform_elevs,
        platform_width_mm=inputs.get("platform_width", 900),
        provide_strakes=inputs.get("strakes", False)
    )

    zone_weights = [z["zone_total"] for z in weight_data["zones"]]
    cumulative_weights = get_cumulative_weights(weight_data["zones"])

    # ------------------------------------------------------------------
    # 3. Dynamic Analysis (Frequency + Mode Shapes)
    # ------------------------------------------------------------------
    dynamic = run_dynamic_analysis(
        zones=zones,
        zone_weights=zone_weights,
        top_od_mm=top_od,
        Vb=inputs["wind_speed"],
        terrain_category=3
    )

    nat_freq = dynamic["natural_frequency"]["frequency_hz"]
    mode_shapes = dynamic["mode_shapes"]

    # ------------------------------------------------------------------
    # 4. Wind Loads
    # ------------------------------------------------------------------
    wind = calculate_all_wind_loads(
        zones=zones,
        zone_weights=zone_weights,
        Vb=inputs["wind_speed"],
        natural_freq=nat_freq,
        K1=0.90,
        terrain_category=3
    )

    # Governing moments (simplified – use gust loads for now)
    # In a full version we would integrate loads to get proper BM
    # Here we create approximate moments increasing towards base
    n = len(zones)
    approx_moments = []
    total_shear = sum(w["gust"] for w in wind["zones"])
    for i in range(n):
        # Rough moment accumulation
        lever = sum(zones[j]["length"] for j in range(i, n)) * 0.55
        M = total_shear * lever * (i + 1) / n
        approx_moments.append(round(M, 1))

    # ------------------------------------------------------------------
    # 5. Earthquake
    # ------------------------------------------------------------------
    earthquake = run_earthquake_analysis(
        zones=zones,
        zone_weights=zone_weights,
        mode_shapes=mode_shapes,
        natural_period=dynamic["natural_frequency"]["period_sec"],
        seismic_zone=inputs.get("seismic_zone", "Zone 4"),
        importance=inputs.get("importance", 1.5)
    )

    # ------------------------------------------------------------------
    # 6. Shell Thickness Design (iterative)
    # ------------------------------------------------------------------
    thickness_results = design_shell_thicknesses(
        zones=zones,
        axial_forces=cumulative_weights,
        moments=approx_moments,
        temperature=inputs.get("temperature", 250),
        corrosion_mm=inputs.get("int_corrosion", 3.0)
    )

    final_thicknesses = [t["practical_thickness"] for t in thickness_results]

    # Re-calculate weights with final thicknesses
    weight_data = calculate_zone_weights(
        zones=zones,
        thicknesses=final_thicknesses,
        platform_elevations=platform_elevs,
        platform_width_mm=inputs.get("platform_width", 900),
        provide_strakes=inputs.get("strakes", False)
    )
    zone_weights = [z["zone_total"] for z in weight_data["zones"]]
    cumulative_weights = get_cumulative_weights(weight_data["zones"])

    # ------------------------------------------------------------------
    # 7. Shell Stress Check
    # ------------------------------------------------------------------
    stress_results = run_shell_stress_analysis(
        zones=zones,
        thicknesses=final_thicknesses,
        axial_forces=cumulative_weights,
        moments=approx_moments,
        temperature=inputs.get("temperature", 250),
        corrosion_mm=inputs.get("int_corrosion", 3.0)
    )

    # ------------------------------------------------------------------
    # 8. Flange Design
    # ------------------------------------------------------------------
    flanges = design_all_flanges(
        zones=zones,
        moments=approx_moments,
        cumulative_weights=cumulative_weights,
        min_bolt_size=inputs.get("min_bolt", "M24"),
        min_flange_thk=inputs.get("min_flange_thk", 12.0)
    )

    # ------------------------------------------------------------------
    # 9. Base Chair Design
    # ------------------------------------------------------------------
    base_moment = approx_moments[-1] if approx_moments else 50000
    base_shear = sum(w["gust"] for w in wind["zones"])
    total_wt = weight_data["summary"]["grand_total"]

    base = design_base_chair(
        base_moment_kgm=base_moment,
        base_shear_kg=base_shear,
        total_weight_kg=total_wt,
        skirt_od_mm=bottom_od,
        base_plate_width_mm=inputs.get("base_plate_width", 300)
    )

    # ------------------------------------------------------------------
    # 10. Compile Final Results
    # ------------------------------------------------------------------
    return {
        "inputs": inputs,
        "geometry": {
            "total_height": H,
            "flare_height": round(flare_height, 2),
            "top_od": top_od,
            "bottom_od": bottom_od,
            "zones": zones
        },
        "thicknesses": thickness_results,
        "weights": weight_data,
        "dynamic": dynamic,
        "wind": wind,
        "earthquake": earthquake,
        "stress": stress_results,
        "flanges": flanges,
        "base": base,
        "summary": {
            "natural_frequency": nat_freq,
            "period": dynamic["natural_frequency"]["period_sec"],
            "total_weight": total_wt,
            "base_moment": base_moment,
            "base_shear": round(base_shear, 1),
            "strakes_required": dynamic["across_wind"]["strakes_required"],
            "max_utilization": max((s["utilization"] for s in stress_results), default=0)
        }
    }
