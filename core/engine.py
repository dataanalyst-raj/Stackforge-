"""
StackForge - Master Calculation Engine (Stage 1 Improved)
"""

from core.geometry import calculate_flare_height, generate_shell_zones
from core.thickness import design_shell_thicknesses
from core.weights import calculate_zone_weights, get_cumulative_weights
from core.wind_loads import calculate_all_wind_loads
from core.dynamic_analysis import run_dynamic_analysis
from core.earthquake import run_earthquake_analysis
from core.flange_design import design_all_flanges
from core.base_design import design_base_chair
from core.shell_stress import run_shell_stress_analysis


def run_complete_design(inputs: dict) -> dict:
    # --------------------------------------------------
    # 1. Geometry
    # --------------------------------------------------
    H = inputs["total_height"]
    top_id = inputs["top_id"]
    is_lined = inputs["is_lined"]
    bottom_od = inputs["bottom_od"]
    corrosion = inputs.get("int_corrosion", 3.0)

    # Approximate top OD (will be refined later with actual thickness)
    top_od = top_id + 2 * (corrosion + 4)

    if inputs.get("flare_height", 0) > 0.5:
        flare_height = inputs["flare_height"]
    else:
        flare_height = calculate_flare_height(H, top_id, is_lined)

    zones = generate_shell_zones(
        total_height=H,
        flare_height=flare_height,
        top_od=top_od,
        bottom_od=bottom_od,
        preferred_zone_length=6.0
    )

    if not zones:
        return {"error": "Could not generate shell zones. Check geometry inputs."}

    # --------------------------------------------------
    # 2. Trial thicknesses + Weights
    # --------------------------------------------------
    trial_thk = []
    for i, z in enumerate(zones):
        # Simple increasing thickness towards bottom
        thk = 6.0 + i * 1.5
        if thk < 6: thk = 6.0
        if thk > 16: thk = 16.0
        trial_thk.append(thk)

    # Platform elevations (simple distribution)
    platform_elevs = []
    n_plat = inputs.get("num_platforms", 0)
    for i in range(n_plat):
        elev = H * (0.93 - i * 0.35)
        if elev > 4:
            platform_elevs.append(elev)

    weight_data = calculate_zone_weights(
        zones=zones,
        thicknesses=trial_thk,
        platform_elevations=platform_elevs,
        platform_width_mm=inputs.get("platform_width", 900),
        provide_strakes=inputs.get("strakes", False)
    )

    zone_weights = [z["zone_total"] for z in weight_data["zones"]]
    cumulative_weights = get_cumulative_weights(weight_data["zones"])

    # --------------------------------------------------
    # 3. Dynamic Analysis
    # --------------------------------------------------
    terrain_cat = 2 if "2" in str(inputs.get("terrain", "3")) else 3

    dynamic = run_dynamic_analysis(
        zones=zones,
        zone_weights=zone_weights,
        top_od_mm=top_od,
        Vb=inputs["wind_speed"],
        terrain_category=terrain_cat
    )

    nat_freq = dynamic["natural_frequency"]["frequency_hz"]
    mode_shapes = dynamic["mode_shapes"]

    # --------------------------------------------------
    # 4. Wind Loads + Proper Moments
    # --------------------------------------------------
    wind = calculate_all_wind_loads(
        zones=zones,
        zone_weights=zone_weights,
        Vb=inputs["wind_speed"],
        natural_freq=nat_freq,
        K1=0.90,
        terrain_category=terrain_cat
    )

    governing_moments = wind.get("moments", [5000 * (i+1) for i in range(len(zones))])

    # --------------------------------------------------
    # 5. Earthquake
    # --------------------------------------------------
    earthquake = run_earthquake_analysis(
        zones=zones,
        zone_weights=zone_weights,
        mode_shapes=mode_shapes,
        natural_period=dynamic["natural_frequency"]["period_sec"],
        seismic_zone=inputs.get("seismic_zone", "Zone 3"),
        importance=inputs.get("importance", 1.5)
    )

    # --------------------------------------------------
    # 6. Shell Thickness Design
    # --------------------------------------------------
    thickness_results = design_shell_thicknesses(
        zones=zones,
        axial_forces=cumulative_weights,
        moments=governing_moments,
        temperature=inputs.get("temperature", 250),
        corrosion_mm=corrosion
    )

    final_thicknesses = [t["practical_thickness"] for t in thickness_results]

    # Recalculate weights with final thicknesses
    weight_data = calculate_zone_weights(
        zones=zones,
        thicknesses=final_thicknesses,
        platform_elevations=platform_elevs,
        platform_width_mm=inputs.get("platform_width", 900),
        provide_strakes=inputs.get("strakes", False)
    )
    zone_weights = [z["zone_total"] for z in weight_data["zones"]]
    cumulative_weights = get_cumulative_weights(weight_data["zones"])

    # --------------------------------------------------
    # 7. Shell Stress
    # --------------------------------------------------
    stress_results = run_shell_stress_analysis(
        zones=zones,
        thicknesses=final_thicknesses,
        axial_forces=cumulative_weights,
        moments=governing_moments,
        temperature=inputs.get("temperature", 250),
        corrosion_mm=corrosion
    )

    # --------------------------------------------------
    # 8. Flanges
    # --------------------------------------------------
    flanges = design_all_flanges(
        zones=zones,
        moments=governing_moments,
        cumulative_weights=cumulative_weights,
        min_bolt_size=inputs.get("min_bolt", "M24"),
        min_flange_thk=inputs.get("min_flange_thk", 12.0)
    )

    # --------------------------------------------------
    # 9. Base Chair
    # --------------------------------------------------
    base_moment = governing_moments[-1] if governing_moments else 80000
    base_shear = sum(w.get("gust", 0) for w in wind["zones"])
    total_wt = weight_data["summary"]["grand_total"]

    base = design_base_chair(
        base_moment_kgm=base_moment,
        base_shear_kg=base_shear,
        total_weight_kg=total_wt,
        skirt_od_mm=bottom_od,
        base_plate_width_mm=inputs.get("base_plate_width", 300)
    )

    # --------------------------------------------------
    # 10. Final Results
    # --------------------------------------------------
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
