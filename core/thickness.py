"""
StackForge - Shell Thickness Module
Iterative thickness calculation as per IS 6533 (Part 2)
"""

from utils.constants import FY_IS2062, MIN_SHELL_THICKNESS


def get_temperature_coefficient(temperature: float) -> float:
    """
    Temperature coefficient Kt as per IS 6533 Part 2 Clause 7.8.1
    Approximate values used in practice.
    """
    if temperature <= 50:
        return 1.00
    elif temperature <= 100:
        return 0.97
    elif temperature <= 150:
        return 0.93
    elif temperature <= 200:
        return 0.87
    elif temperature <= 250:
        return 0.80
    elif temperature <= 300:
        return 0.75
    elif temperature <= 350:
        return 0.70
    else:
        return 0.65


def get_factor_B(D_over_t: float) -> float:
    """
    Factor B from IS 6533 Annex C (simplified interpolation).
    Used for allowable compressive stress.
    """
    if D_over_t <= 60:
        return 1.00
    elif D_over_t <= 80:
        return 1.00
    elif D_over_t <= 100:
        return 0.98
    elif D_over_t <= 120:
        return 0.95
    elif D_over_t <= 140:
        return 0.92
    elif D_over_t <= 160:
        return 0.88
    elif D_over_t <= 180:
        return 0.84
    elif D_over_t <= 200:
        return 0.80
    elif D_over_t <= 220:
        return 0.76
    elif D_over_t <= 240:
        return 0.72
    elif D_over_t <= 260:
        return 0.68
    elif D_over_t <= 280:
        return 0.64
    elif D_over_t <= 300:
        return 0.60
    else:
        return 0.55


def get_factor_A(he_over_D: float) -> float:
    """
    Factor A from IS 6533 (simplified).
    For most practical chimneys He/D < 21 → A = 1.0
    """
    if he_over_D <= 21:
        return 1.00
    elif he_over_D <= 25:
        return 0.95
    else:
        return 0.90


def calculate_allowable_stress(fy: float, Kt: float, A: float, B: float) -> float:
    """
    Allowable compressive stress as per IS 6533:
    σ_allow = 0.5 * fy * Kt * A * B
    """
    return 0.5 * fy * Kt * A * B


def iterate_thickness(
    diameter_mm: float,
    axial_force_kg: float,
    moment_kgm: float,
    he_over_D: float,
    temperature: float,
    corrosion_mm: float = 3.0,
    fy: float = FY_IS2062,
    max_iterations: int = 15
) -> dict:
    """
    Iterative calculation of required shell thickness.

    Formula:
        t = W / (σ_allow * π * D) + 4M / (σ_allow * π * D²) + Corrosion

    Returns dictionary with results.
    """
    D_cm = diameter_mm / 10.0
    M_kgcm = moment_kgm * 100.0
    Kt = get_temperature_coefficient(temperature)
    A = get_factor_A(he_over_D)

    # Start with a trial thickness
    t_corroded = 5.0  # mm

    for i in range(max_iterations):
        D_over_t = diameter_mm / max(t_corroded, 1.0)
        B = get_factor_B(D_over_t)
        sigma_allow = calculate_allowable_stress(fy, Kt, A, B)

        if sigma_allow <= 0:
            sigma_allow = 500.0

        # Stress-required thickness (corroded)
        term1 = axial_force_kg / (sigma_allow * 3.1416 * D_cm)
        term2 = 4.0 * M_kgcm / (sigma_allow * 3.1416 * D_cm**2)
        t_required = (term1 + term2) * 10.0  # convert cm → mm

        # Next trial
        t_next = t_required

        # Convergence check
        if abs(t_next - t_corroded) < 0.05:
            t_corroded = t_next
            break

        t_corroded = 0.5 * (t_corroded + t_next)  # damping for stability

    # Final values
    D_over_t = diameter_mm / max(t_corroded, 1.0)
    B = get_factor_B(D_over_t)
    sigma_allow = calculate_allowable_stress(fy, Kt, A, B)

    required_nominal = t_corroded + corrosion_mm
    code_minimum = max(MIN_SHELL_THICKNESS, diameter_mm / 500.0)

    # Practical plate thickness (round up to common sizes)
    practical = round_to_practical_thickness(max(required_nominal, code_minimum))

    return {
        "corroded_thickness": round(t_corroded, 2),
        "required_nominal": round(required_nominal, 2),
        "code_minimum": round(code_minimum, 2),
        "practical_thickness": practical,
        "sigma_allow": round(sigma_allow, 1),
        "Kt": Kt,
        "A": A,
        "B": round(B, 3),
        "D_over_t": round(D_over_t, 1)
    }


def round_to_practical_thickness(t_mm: float) -> float:
    """
    Round up to next practical plate thickness.
    Common available thicknesses: 6, 8, 10, 12, 14, 16, 18, 20, 22, 25 mm
    """
    standard = [6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 30, 32, 36, 40]

    for s in standard:
        if s >= t_mm - 0.05:
            return float(s)

    return round(t_mm + 2, 0)


def design_shell_thicknesses(
    zones: list,
    axial_forces: list,
    moments: list,
    temperature: float,
    corrosion_mm: float = 3.0
) -> list:
    """
    Design thickness for all zones.

    zones: list from generate_shell_zones()
    axial_forces: list of Dead+Imposed force at each section (kg)
    moments: list of governing BM at each section (kg-m)

    Returns updated zones with thickness information.
    """
    results = []
    cumulative_height = 0.0

    for i, zone in enumerate(zones):
        cumulative_height += zone["length"]
        he = cumulative_height  # approximate effective height from top
        D = zone["mean_od"]
        he_over_D = (he * 1000) / D if D > 0 else 10

        W = axial_forces[i] if i < len(axial_forces) else 5000
        M = moments[i] if i < len(moments) else 10000

        thk = iterate_thickness(
            diameter_mm=D,
            axial_force_kg=W,
            moment_kgm=M,
            he_over_D=he_over_D,
            temperature=temperature,
            corrosion_mm=corrosion_mm
        )

        zone_result = zone.copy()
        zone_result.update(thk)
        results.append(zone_result)

    return results
