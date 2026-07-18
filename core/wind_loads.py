"""
StackForge - Wind Loads Module (Improved)
"""

import math


def get_k2_factor(height_m: float, terrain_category: int = 3) -> float:
    tables = {
        1: [(10, 1.05), (15, 1.09), (20, 1.12), (30, 1.15), (50, 1.20), (100, 1.26), (150, 1.30)],
        2: [(10, 1.00), (15, 1.05), (20, 1.07), (30, 1.12), (50, 1.17), (100, 1.24), (150, 1.28)],
        3: [(10, 0.91), (15, 0.97), (20, 1.01), (30, 1.06), (50, 1.12), (100, 1.20), (150, 1.24)],
        4: [(10, 0.80), (15, 0.86), (20, 0.90), (30, 0.97), (50, 1.05), (100, 1.15), (150, 1.20)],
    }
    cat = min(max(terrain_category, 1), 4)
    rows = tables[cat]

    if height_m <= rows[0][0]:
        return rows[0][1]
    if height_m >= rows[-1][0]:
        return rows[-1][1]

    for i in range(1, len(rows)):
        h1, k1 = rows[i-1]
        h2, k2 = rows[i]
        if height_m <= h2:
            ratio = (height_m - h1) / (h2 - h1)
            return round(k1 + ratio * (k2 - k1), 3)
    return rows[-1][1]


def design_wind_speed(Vb: float, K1: float, K2: float, K3: float = 1.0, K4: float = 1.0) -> float:
    return Vb * K1 * K2 * K3 * K4


def design_wind_pressure(Vz: float) -> float:
    return 0.6 * (Vz ** 2)


def static_wind_load_on_zone(pressure_kg_m2: float, mean_od_mm: float, length_m: float, Cd: float = 0.7) -> float:
    diameter_m = mean_od_mm / 1000.0
    area = diameter_m * length_m
    return round(pressure_kg_m2 * Cd * area, 1)


def calculate_static_wind_loads(zones: list, Vb: float, K1: float = 0.90, K3: float = 1.0,
                                 K4: float = 1.0, terrain_category: int = 3, Cd: float = 0.70) -> list:
    results = []
    total_height = sum(z["length"] for z in zones)
    h_from_top = 0.0

    for zone in zones:
        mid_from_top = h_from_top + zone["length"] / 2.0
        mid_from_ground = total_height - mid_from_top

        K2 = get_k2_factor(mid_from_ground, terrain_category)
        Vz = design_wind_speed(Vb, K1, K2, K3, K4)
        pz = design_wind_pressure(Vz)
        load = static_wind_load_on_zone(pz, zone["mean_od"], zone["length"], Cd)

        results.append({
            "zone_no": zone["zone_no"],
            "height_mid": round(mid_from_ground, 2),
            "K2": K2,
            "Vz": round(Vz, 2),
            "pressure": round(pz, 1),
            "static_load": load
        })
        h_from_top += zone["length"]

    return results


def calculate_moments_from_loads(zones: list, loads: list) -> list:
    n = len(zones)
    moments = [0.0] * n
    cum_length = 0.0
    zone_bottom_from_top = []
    for z in zones:
        cum_length += z["length"]
        zone_bottom_from_top.append(cum_length)

    for i in range(n):
        M = 0.0
        for j in range(i + 1):
            centre_j = sum(zones[k]["length"] for k in range(j)) + zones[j]["length"] / 2.0
            lever = zone_bottom_from_top[i] - centre_j
            if lever > 0:
                M += loads[j] * lever
        moments[i] = round(M, 1)
    return moments


def approximate_mode_shape(zone_index: int, total_zones: int, mode: int = 1) -> float:
    x = 1.0 - (zone_index + 0.5) / total_zones
    if mode == 1:
        return x ** 1.7
    elif mode == 2:
        return math.sin(2.3 * math.pi * x / 2) * (0.55 + 0.45 * x)
    else:
        return math.sin(3.9 * math.pi * x / 2) * (0.45 + 0.55 * x)


def calculate_dynamic_wind_loads(zones: list, zone_weights: list, static_loads_hmw: list,
                                  natural_freq: float, Vb: float, damping: float = 0.02) -> list:
    n = len(zones)
    T = 1.0 / max(natural_freq, 0.05)
    xi = T * Vb / 1200.0

    if xi <= 0.02:
        dyn_coeff = 2.40
    elif xi <= 0.04:
        dyn_coeff = 2.40 + (xi - 0.02) / 0.02 * 0.50
    else:
        dyn_coeff = 2.90 + min(xi - 0.04, 0.06) * 3.0

    nu = 0.70
    Y = [approximate_mode_shape(i, n, 1) for i in range(n)]
    max_y = max(abs(y) for y in Y) or 1.0
    Y = [y / max_y for y in Y]
    mk = [0.65 + 0.025 * i for i in range(n)]

    sum_num = 0.0
    sum_den = 0.0
    for i in range(n):
        Pst = static_loads_hmw[i] if i < len(static_loads_hmw) else 50
        M = zone_weights[i] if i < len(zone_weights) else 500
        sum_num += Y[i] * Pst * mk[i]
        sum_den += (Y[i] ** 2) * M

    ratio = sum_num / max(sum_den, 1.0)
    results = []
    for i in range(n):
        eta = Y[i] * ratio
        M = zone_weights[i] if i < len(zone_weights) else 500
        Pdyn = abs(M * dyn_coeff * eta * nu)
        results.append({
            "zone_no": zones[i]["zone_no"],
            "Y": round(Y[i], 4),
            "dynamic_load": round(Pdyn, 1)
        })
    return results


def calculate_gust_factor(height_m: float, natural_freq: float, Vb: float,
                           avg_breadth_m: float, damping: float = 0.02,
                           terrain_category: int = 3) -> dict:
    K2_top = get_k2_factor(height_m, terrain_category)
    Vh = Vb * 0.90 * K2_top * 0.67
    gfr = 1.70
    B = 0.78
    phi = 0.0
    S = 0.15
    E = 0.047
    SE_beta = (S * E) / max(damping, 0.015)
    G = 1 + gfr * math.sqrt(B * (1 + phi)**2 + SE_beta)
    return {"G": round(G, 3), "Vh": round(Vh, 2), "gfr": gfr, "B": B, "SE_beta": round(SE_beta, 3)}


def calculate_all_wind_loads(zones: list, zone_weights: list, Vb: float, natural_freq: float,
                              K1: float = 0.90, K3: float = 1.0, K4: float = 1.0,
                              terrain_category: int = 3, Cd: float = 0.70,
                              damping: float = 0.02) -> dict:
    static_results = calculate_static_wind_loads(zones, Vb, K1, K3, K4, terrain_category, Cd)
    static_loads = [r["static_load"] for r in static_results]
    hmw_static = [round(s * 0.42, 1) for s in static_loads]

    dynamic_results = calculate_dynamic_wind_loads(zones, zone_weights, hmw_static, natural_freq, Vb, damping)
    dynamic_loads = [r["dynamic_load"] for r in dynamic_results]

    total_height = sum(z["length"] for z in zones)
    avg_breadth = sum(z["mean_od"] for z in zones) / max(len(zones), 1) / 1000.0
    gf = calculate_gust_factor(total_height, natural_freq, Vb, avg_breadth, damping, terrain_category)
    gust_loads = [round(h * gf["G"], 1) for h in hmw_static]

    moments_gust = calculate_moments_from_loads(zones, gust_loads)
    moments_static = calculate_moments_from_loads(zones, static_loads)
    moments_dyn = calculate_moments_from_loads(zones, [h + d for h, d in zip(hmw_static, dynamic_loads)])
    governing_moments = [max(moments_gust[i], moments_static[i], moments_dyn[i]) for i in range(len(zones))]

    combined = []
    for i, zone in enumerate(zones):
        combined.append({
            "zone_no": zone["zone_no"],
            "static_3sec": static_loads[i],
            "hmw_static": hmw_static[i],
            "dynamic": dynamic_loads[i],
            "hmw_plus_dynamic": round(hmw_static[i] + dynamic_loads[i], 1),
            "gust": gust_loads[i],
            "moment": governing_moments[i],
            "Y_mode1": dynamic_results[i]["Y"]
        })

    return {
        "zones": combined,
        "gust_factor": gf,
        "static_details": static_results,
        "moments": governing_moments
    }
