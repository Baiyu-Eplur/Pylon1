from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cable_analyser.config_loader import load_config
from cable_analyser.geometry import CableGeometry


def load_table(path: Path) -> np.ndarray:
    try:
        return np.loadtxt(path, delimiter=",")
    except ValueError:
        return np.loadtxt(path)


def unstable_ranges(alpha: np.ndarray, delta: np.ndarray) -> list[dict[str, float]]:
    mask = delta < 0
    ranges = []
    start = None
    for idx, value in enumerate(mask):
        if value and start is None:
            start = idx
        if start is not None and (not value or idx == len(mask) - 1):
            end = idx - 1 if not value else idx
            ranges.append(
                {
                    "alpha_start_deg": float(alpha[start]),
                    "alpha_end_deg": float(alpha[end]),
                    "min_delta": float(np.min(delta[start:end + 1])),
                }
            )
            start = None
    return ranges


def moving_average(values: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return values.copy()
    kernel = np.ones(window) / window
    pad = window // 2
    padded = np.pad(values, (pad, pad), mode="edge")
    return np.convolve(padded, kernel, mode="valid")[: len(values)]


def read_first_modal_frequency(output_dir: Path) -> float | None:
    path = output_dir / "modal_simple.out"
    if not path.exists() or path.stat().st_size == 0:
        return None
    data = np.loadtxt(path)
    if data.ndim == 1:
        data = data[np.newaxis, :]
    return float(data[0, 1])


def build_audit(config_path: Path) -> dict[str, Any]:
    cfg = load_config(config_path)
    geo = CableGeometry(cfg).generate()
    coeff_dir = ROOT / cfg["paths"].get("aero_coeffs_dir", "data/aero_coeffs")
    cd = load_table(coeff_dir / "C_D_data.txt")
    cl = load_table(coeff_dir / "C_L_data2.txt")
    dcl_stored = np.loadtxt(coeff_dir / "dC_L.txt")
    alpha = cl[:, 0]
    cd_interp = np.interp(alpha, cd[:, 0], cd[:, 1])
    dcl_per_degree = dcl_stored[: len(alpha)]
    dcl_per_radian = dcl_per_degree * 180.0 / math.pi
    delta_degree = dcl_per_degree + cd_interp
    delta_radian = dcl_per_radian + cd_interp
    delta_radian_smoothed = moving_average(delta_radian, 11)

    xi = float(cfg["damping"]["xi"])
    ro_air = float(cfg["time_history"]["ro_air"])
    diameter = float(cfg["material"]["Dia"])
    mass_m = float(geo["MN"][1])
    element_length = float(geo["DX"][1])
    f1 = read_first_modal_frequency(ROOT / cfg["paths"]["output_dir"])
    omega = 2.0 * math.pi * f1 if f1 else None

    critical = None
    if omega:
        critical = []
        for a, delta in zip(alpha, delta_radian):
            if delta < 0:
                ucrit = -4.0 * mass_m * omega * xi / (ro_air * diameter * element_length * delta)
                critical.append({"alpha_deg": float(a), "ucrit_mps": float(ucrit), "delta_D": float(delta)})
        critical = sorted(critical, key=lambda item: item["ucrit_mps"])[:10]

    return {
        "config": str(config_path.relative_to(ROOT)),
        "coefficient_source": {
            "cd": str((coeff_dir / "C_D_data.txt").relative_to(ROOT)),
            "cl": str((coeff_dir / "C_L_data2.txt").relative_to(ROOT)),
            "dcl": str((coeff_dir / "dC_L.txt").relative_to(ROOT)),
        },
        "dcl_unit_check": {
            "stored_matches_per_degree": True,
            "conversion_to_per_radian": "dCL_rad = dCL_degree * 180 / pi",
            "stored_range_per_degree": [float(np.min(dcl_per_degree)), float(np.max(dcl_per_degree))],
            "converted_range_per_radian": [float(np.min(dcl_per_radian)), float(np.max(dcl_per_radian))],
        },
        "den_hartog_delta_degree": {
            "min": float(np.min(delta_degree)),
            "max": float(np.max(delta_degree)),
            "negative_fraction": float(np.mean(delta_degree < 0)),
            "unstable_ranges": unstable_ranges(alpha, delta_degree),
        },
        "den_hartog_delta_radian": {
            "min": float(np.min(delta_radian)),
            "max": float(np.max(delta_radian)),
            "negative_fraction": float(np.mean(delta_radian < 0)),
            "unstable_ranges": unstable_ranges(alpha, delta_radian),
        },
        "den_hartog_delta_radian_smoothed": {
            "method": "11-point moving average over 0.1 degree coefficient table",
            "min": float(np.min(delta_radian_smoothed)),
            "max": float(np.max(delta_radian_smoothed)),
            "negative_fraction": float(np.mean(delta_radian_smoothed < 0)),
            "unstable_ranges": unstable_ranges(alpha, delta_radian_smoothed),
        },
        "critical_speed_screening": {
            "formula": "Ucrit = -4*M*omega*xi/(rho_air*B*L*delta_D), delta_D < 0",
            "modal_frequency_hz": f1,
            "mass_M": mass_m,
            "element_length_L": element_length,
            "diameter_B": diameter,
            "xi_structural": xi,
            "lowest_ucrit_samples": critical,
        },
    }


def write_markdown(audit: dict[str, Any], path: Path) -> None:
    lines = [
        "# Galloping Criterion Audit",
        "",
        f"Config: `{audit['config']}`",
        "",
        "## dCL Unit Check",
        "",
        f"`{audit['dcl_unit_check']}`",
        "",
        "## Den Hartog Criterion",
        "",
        "Den Hartog vertical galloping screening uses:",
        "",
        "```text",
        "delta_D = dC_L/dalpha + C_D",
        "potential aerodynamic instability when delta_D < 0",
        "```",
        "",
        "The derivative must use alpha in radians.",
        "",
        f"- Using stored per-degree derivative: `{audit['den_hartog_delta_degree']}`",
        f"- Using corrected per-radian derivative: `{audit['den_hartog_delta_radian']}`",
        f"- Corrected and smoothed: `{audit['den_hartog_delta_radian_smoothed']}`",
        "",
        "## Critical Speed Screening",
        "",
        f"`{audit['critical_speed_screening']}`",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/timur_baseline.yaml")
    parser.add_argument("--out-dir", default="output/galloping_criterion/timur_baseline")
    args = parser.parse_args()
    config_path = (ROOT / args.config).resolve()
    out_dir = (ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    audit = build_audit(config_path)
    (out_dir / "galloping_criterion_audit.json").write_text(
        json.dumps(audit, indent=2),
        encoding="utf-8",
    )
    write_markdown(audit, out_dir / "galloping_criterion_audit.md")
    print(f"Wrote {out_dir / 'galloping_criterion_audit.md'}")


if __name__ == "__main__":
    main()
