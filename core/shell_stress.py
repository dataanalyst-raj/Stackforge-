"""
StackForge - Shell Stress Analysis Module
Combined stress check as per IS 6533 (Part 2)
"""

from core.thickness import (
    get_temperature_coefficient,
    get_factor_A,
    get_factor_B,
    calculate_allowable_stress
)
from core.geometry import get_section_properties
from utils.constants import FY_IS2062


def calculate_section_stress(
    diameter_mm: float,
    thickness_mm: float,
    axial_force_kg: float,
    moment_kgm: float,
    he_over_D: float,
    temperature: float,
    fy: float = FY_IS2062
) -> dict:
    """
    Calculate compressive, bending and total stress for one section.
    """
    # Section properties (corroded thickness should be passed)
    props = get_section_properties(diameter_mm, thickness_mm)
    area = props["area_cm2"]
    Z = props["Z_cm3"]

    # Stresses
    sigma_c = axial_force_kg / max(area, 1.0)                  # kg/cm²
    sigma_b = (moment_kgm * 100.0) / max(Z, 1.0)               # kg/cm²
    sigma_total = sigma_c + sigma_b

    # Allowable
    Kt = get_temperature_coefficient(temperature)
    A = get_factor_A(he_over_D)
    D_over_t = diameter_mm / max(thickness_mm, 1.0)
    B = get_factor_B(D_over_t)
    sigma_allow = calculate_allowable_stress(fy, Kt, A, B)

    utilization = sigma_total / max(sigma_allow, 1.0)
    status = "OK" if sigma_total <= sigma_allow else "FAIL"

    return {
        "diameter": round(diameter_mm, 1),
        "thickness": round(thickness_mm, 1),
        "area": area,
        "Z": Z,
        "axial_force": round(axial_force_kg, 1),
        "moment": round(moment_kgm, 1),
        "sigma_c": round(sigma_c, 1),
        "sigma_b": round(sigma_b, 1),
        "sigma_total": round(sigma_total, 1),
        "sigma_allow": round(sigma_allow, 1),
        "utilization": round(utilization * 100, 1),
        "status": status,
        "Kt": Kt,
        "A": A,
        "B": round(B, 3)
    }


def run_shell_stress_analysis(
    zones: list,
    thicknesses: list,
    axial_forces: list,
    moments: list,
    temperature: float,
    corrosion_mm: float = 3.0
) -> list:
    """
    Run combined stress check for all sections.

    thicknesses : nominal thicknesses
    axial_forces : Dead + Imposed at each section (from top)
    moments : governing bending moment at each section
    """
    results = []
    cumulative_height = 0.0

    for i, zone in enumerate(zones):
        cumulative_height += zone["length"]
        D = zone["mean_od"]
        t_nominal = thicknesses[i] if i < len(thicknesses) else 10.0
        t_corroded = max(t_nominal - corrosion_mm, 1.0)

        he = cumulative_height
        he_over_D = (he * 1000.0) / D if D > 0 else 10.0

        W = axial_forces[i] if i < len(axial_forces) else 5000
        M = moments[i] if i < len(moments) else 10000

        stress = calculate_section_stress(
            diameter_mm=D,
            thickness_mm=t_corroded,
            axial_force_kg=W,
            moment_kgm=M,
            he_over_D=he_over_D,
            temperature=temperature
        )

        stress["zone_no"] = zone["zone_no"]
        stress["portion"] = zone["portion"]
        stress["nominal_thickness"] = t_nominal
        results.append(stress)

    return results
