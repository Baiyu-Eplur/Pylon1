from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cable_analyser.config_loader import load_config
from cable_analyser.geometry import CableGeometry


def _rmse(a: np.ndarray, b: np.ndarray) -> float:
    if np.isnan(b).any():
        return -1.0
    return float(np.sqrt(np.mean((a - b) ** 2)))


def _shape_references(x: np.ndarray, L: float, sag: float) -> dict[str, np.ndarray]:
    parabola = 4 * sag / L**2 * x**2 - 4 * sag / L * x

    x_mid = L / 2
    broken = np.empty_like(x)
    for i, xi in enumerate(x):
        if xi <= x_mid:
            broken[i] = -sag * xi / x_mid
        else:
            broken[i] = -sag * (L - xi) / x_mid

    x1 = x - L / 2
    if sag <= 0:
        catenary = np.full_like(x, np.nan)
    else:
        def sag_from_a(a: float) -> float:
            return a * (math.cosh(L / (2 * a)) - 1)

        high = max(L**2 / (8 * sag), L, 1.0)
        while sag_from_a(high) > sag:
            high *= 2.0
        low = high / 2.0
        while sag_from_a(low) < sag:
            low /= 2.0
        for _ in range(80):
            mid = (low + high) / 2.0
            if sag_from_a(mid) > sag:
                low = mid
            else:
                high = mid
        a = (low + high) / 2.0
        catenary_raw = a * np.cosh(x1 / a)
        catenary = catenary_raw - np.max(catenary_raw)

    return {
        "parabolic": parabola,
        "catenary": catenary,
        "broken_line": broken,
    }


def _file_count(path: Path, pattern: str) -> int:
    return len(list(path.glob(pattern))) if path.exists() else 0


def build_audit(config_path: Path) -> dict:
    cfg = load_config(config_path)

    geo = CableGeometry(cfg)
    result = geo.generate()
    x = result["x"]
    z = result["z"]
    L = float(cfg["geometry"]["L"])
    sag = float(cfg["geometry"]["Sag"])
    disc = float(cfg["geometry"]["discretisation"])
    n_nodes = len(x)
    n_elements = n_nodes - 1

    refs = _shape_references(x, L, sag)
    shape_errors = {name: _rmse(z, ref) for name, ref in refs.items()}
    finite_shape_errors = {k: v for k, v in shape_errors.items() if v >= 0}
    best_shape = min(finite_shape_errors, key=finite_shape_errors.get)

    output_dir = ROOT / cfg["paths"]["output_dir"]
    modal_path = output_dir / "modal_simple.out"
    first_frequency_hz = None
    rayleigh_alpha = None
    if modal_path.exists():
        data = np.loadtxt(modal_path)
        if data.ndim == 1:
            data = data[np.newaxis, :]
        first_frequency_hz = float(data[0, 1])
        xi = float(cfg["damping"]["xi"])
        rayleigh_alpha = 2.0 * xi * 2.0 * math.pi * first_frequency_hz

    force_root = ROOT / cfg["paths"]["forces_dir"]
    force_checks = []
    for f1 in cfg["time_history"]["folder_1"]:
        for f2 in cfg["time_history"]["folder_2"]:
            case_dir = force_root / f1 / f2
            expected_per_component = n_nodes
            force_checks.append(
                {
                    "case": f"{f1}/{f2}",
                    "path": str(case_dir.relative_to(ROOT)),
                    "exists": case_dir.exists(),
                    "expected_files_total": 4 * n_nodes,
                    "H_drag": _file_count(case_dir, "NODE_*_H_drag.txt"),
                    "H_lift": _file_count(case_dir, "NODE_*_H_lift.txt"),
                    "V_drag": _file_count(case_dir, "NODE_*_V_drag.txt"),
                    "V_lift": _file_count(case_dir, "NODE_*_V_lift.txt"),
                    "expected_per_component": expected_per_component,
                }
            )

    wind_dir = ROOT / cfg["paths"]["wind_dir"]
    wind_check = {
        "path": str(wind_dir.relative_to(ROOT)),
        "exists": wind_dir.exists(),
        "expected_wind_H_files": n_nodes,
        "expected_wind_V_files": n_nodes,
        "wind_H": _file_count(wind_dir, "NODE_*_wind_H.txt"),
        "wind_V": _file_count(wind_dir, "NODE_*_wind_V.txt"),
    }

    return {
        "config": str(config_path.relative_to(ROOT)),
        "geometry": {
            "configured_type": int(cfg["geometry"]["type"]),
            "L_m": L,
            "Sag_m": sag,
            "sag_to_span": sag / L,
            "discretisation_m": disc,
            "n_nodes": n_nodes,
            "n_elements": n_elements,
            "best_shape_match": best_shape,
            "shape_rmse_m": shape_errors,
            "z_min_m": float(np.min(z)),
            "z_max_m": float(np.max(z)),
            "total_arc_length_m": float(np.sum(result["dx"])),
        },
        "section_and_mass": {
            "Dia_m": float(cfg["material"]["Dia"]),
            "Area_m2": float(result["Area"]),
            "In_m4": float(result["In"]),
            "Io_m4": float(result["Io"]),
            "self_weight_N_per_m": float(result["self_weight"]),
            "self_weight_source": result["self_weight_source"],
            "total_mass_kg": float(np.sum(result["MN"])),
            "min_node_mass_kg": float(np.min(result["MN"])),
            "max_node_mass_kg": float(np.max(result["MN"])),
        },
        "damping": {
            "model": cfg["damping"]["model"],
            "xi": float(cfg["damping"]["xi"]),
            "modal_simple_out_exists": modal_path.exists(),
            "first_frequency_hz": first_frequency_hz,
            "rayleigh_mass_alpha_if_available": rayleigh_alpha,
            "note": "OpenSees full C/K matrices are not exported by the current workflow.",
        },
        "input_data_checks": {
            "force_cases": force_checks,
            "wind": wind_check,
        },
    }


def write_markdown(audit: dict, path: Path) -> None:
    g = audit["geometry"]
    s = audit["section_and_mass"]
    d = audit["damping"]
    lines = [
        "# Model Sanity Audit",
        "",
        f"Config: `{audit['config']}`",
        "",
        "## Geometry",
        "",
        f"- Configured geometry type: `{g['configured_type']}`",
        f"- Span L: `{g['L_m']}` m",
        f"- Sag: `{g['Sag_m']}` m",
        f"- Sag/span: `{g['sag_to_span']:.6g}`",
        f"- Nodes/elements: `{g['n_nodes']}` / `{g['n_elements']}`",
        f"- Best shape match from generated nodes: `{g['best_shape_match']}`",
        f"- Shape RMSE (m, -1 means not applicable): `{g['shape_rmse_m']}`",
        f"- Arc length: `{g['total_arc_length_m']:.6g}` m",
        "",
        "## Section And Mass",
        "",
        f"- Diameter: `{s['Dia_m']}` m",
        f"- Area: `{s['Area_m2']:.8e}` m2",
        f"- In: `{s['In_m4']:.8e}` m4",
        f"- Io: `{s['Io_m4']:.8e}` m4",
        f"- Self weight: `{s['self_weight_N_per_m']:.6g}` N/m",
        f"- Self weight source: `{s['self_weight_source']}`",
        f"- Total nodal mass: `{s['total_mass_kg']:.6g}` kg",
        "",
        "## Damping",
        "",
        f"- Model: `{d['model']}`",
        f"- Structural xi: `{d['xi']}`",
        f"- `modal_simple.out` exists: `{d['modal_simple_out_exists']}`",
        f"- First frequency: `{d['first_frequency_hz']}` Hz",
        f"- Rayleigh mass alpha if available: `{d['rayleigh_mass_alpha_if_available']}`",
        f"- Note: {d['note']}",
        "",
        "## Input Data Checks",
        "",
    ]
    for case in audit["input_data_checks"]["force_cases"]:
        lines.extend(
            [
                f"### Force Case `{case['case']}`",
                "",
                f"- Path exists: `{case['exists']}` (`{case['path']}`)",
                f"- Expected per component: `{case['expected_per_component']}`",
                f"- H_drag/H_lift/V_drag/V_lift: `{case['H_drag']}` / `{case['H_lift']}` / `{case['V_drag']}` / `{case['V_lift']}`",
                "",
            ]
        )
    wind = audit["input_data_checks"]["wind"]
    lines.extend(
        [
            "### Wind Velocity Data",
            "",
            f"- Path exists: `{wind['exists']}` (`{wind['path']}`)",
            f"- Expected H/V files: `{wind['expected_wind_H_files']}` / `{wind['expected_wind_V_files']}`",
            f"- Found H/V files: `{wind['wind_H']}` / `{wind['wind_V']}`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/default_config.yaml")
    parser.add_argument("--out-dir", default="output/model_audit")
    args = parser.parse_args()

    config_path = (ROOT / args.config).resolve()
    out_dir = (ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    audit = build_audit(config_path)
    (out_dir / "model_sanity_audit.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    write_markdown(audit, out_dir / "model_sanity_audit.md")
    print(f"Wrote {out_dir / 'model_sanity_audit.md'}")


if __name__ == "__main__":
    main()
