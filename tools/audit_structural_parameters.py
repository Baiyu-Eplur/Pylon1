from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def audit(config_path: Path) -> dict:
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    geom = cfg["geometry"]
    mat = cfg["material"]
    ana = cfg["analysis"]

    dia = float(mat["Dia"])
    area = math.pi * dia**2 / 4.0
    in_plane_i = math.pi * dia**4 / 64.0
    polar_j = 2.0 * in_plane_i
    e = float(mat["E"])
    g = float(mat["G"])
    ea = e * area
    ei = e * in_plane_i
    gj = g * polar_j

    if mat.get("self_weight_N_per_m") is not None:
        w = float(mat["self_weight_N_per_m"])
        weight_source = "material.self_weight_N_per_m"
    else:
        rho_material = float(mat["ro"])
        w = area * rho_material * 9.80665
        weight_source = "Area * ro * g"

    mass_per_m = w / 9.80665
    l = float(geom["L"])
    sag = float(geom["Sag"])
    pretension = float(ana["pretension_load"])
    parabolic_horizontal_tension = w * l**2 / (8.0 * sag) if sag > 0 else None
    pretension_to_parabolic_ratio = (
        pretension / parabolic_horizontal_tension
        if parabolic_horizontal_tension and parabolic_horizontal_tension != 0
        else None
    )
    rated = mat.get("rated_strength_N")
    rated_ratio = pretension / float(rated) if rated else None

    return {
        "config": str(config_path),
        "geometry": {
            "L_m": l,
            "Sag_m": sag,
            "discretisation_m": float(geom["discretisation"]),
            "sag_to_span_ratio": sag / l,
        },
        "material": {
            "conductor_name": mat.get("conductor_name"),
            "Dia_m": dia,
            "E_Pa": e,
            "G_Pa": g,
            "self_weight_N_per_m": w,
            "self_weight_source": weight_source,
            "mass_per_m_kg": mass_per_m,
            "rated_strength_N": rated,
        },
        "section": {
            "Area_m2": area,
            "I_m4": in_plane_i,
            "J_m4": polar_j,
            "EA_N": ea,
            "EI_Nm2": ei,
            "GJ_Nm2": gj,
        },
        "initial_tension": {
            "pretension_load_N": pretension,
            "pretension_ratio_to_rated_strength": rated_ratio,
            "parabolic_horizontal_tension_from_wLH_N": parabolic_horizontal_tension,
            "pretension_ratio_to_parabolic_tension": pretension_to_parabolic_ratio,
            "pretension_strain": pretension / ea if ea != 0 else None,
        },
        "loads": {
            "total_self_weight_N": w * l,
            "vertical_load_multiplier": float(ana["multiplier_vertical_load"]),
            "mass_multiplier": float(ana["multiplier_mass"]),
        },
        "model_flags": {
            "fiber_section": int(ana["fiber_section"]),
            "structural_model": ana.get("structural_model"),
            "initial_state_route": ana.get("initial_state_route"),
            "assume_initial_equilibrium": ana.get("assume_initial_equilibrium"),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default=(
            ROOT
            / "output"
            / "diagnostics"
            / "c4_structural_model_comparison_200s"
            / "tension_only"
            / "tension_only.yaml"
        ),
        type=Path,
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = audit(args.config)
    out_path = args.output
    if out_path is None:
        out_path = (
            ROOT
            / "output"
            / "diagnostics"
            / "cable_rod_long_test"
            / "parameter_audit"
            / "structural_parameter_audit.json"
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
