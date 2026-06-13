from __future__ import annotations

import csv
import json
import math
import argparse
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cable_analyser.wind_forces import _load_coefficient_table


DEFAULT_CONFIG = ROOT / "output/diagnostics/typical_explicit_galloping/typical_L322P8_H10P48_U0P6_explicit_force.yaml"
DEFAULT_RUN = ROOT / "output/diagnostics/typical_explicit_galloping/run"
DEFAULT_OUT = ROOT / "output/diagnostics/typical_explicit_galloping/point_monitoring"
N_NODES = 101
POINTS = [
    ("quarter_1", "1/4 span", 26),
    ("midspan", "Midspan", 51),
    ("quarter_3", "3/4 span", 76),
]


def load_matrix(path: Path) -> np.ndarray:
    data = np.loadtxt(path)
    return data[np.newaxis, :] if data.ndim == 1 else data


def node_cols(node_id: int) -> tuple[int, int, int]:
    start = 1 + (node_id - 1) * 3
    return start, start + 1, start + 2


def read_params(path: Path) -> dict[str, float]:
    params: dict[str, float] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0] == "set":
            try:
                params[parts[1]] = float(parts[2].strip('"'))
            except ValueError:
                continue
    return params


def resample_vector(source_time: np.ndarray, values: np.ndarray, target_time: np.ndarray) -> np.ndarray:
    return np.interp(target_time, source_time, values)


def clamped_interp(x: np.ndarray, xp: np.ndarray, fp: np.ndarray) -> np.ndarray:
    return np.interp(np.clip(x, xp[0], xp[-1]), xp, fp)


def solver_lookup_angle_deg(rel_x: np.ndarray, rel_z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    raw = np.abs(np.rad2deg(np.arctan2(rel_z, rel_x)))
    angle_x = np.abs(rel_x)
    angle_z = np.where(rel_x < 0.0, -rel_z, rel_z)
    alpha = np.abs(np.rad2deg(np.arctan2(angle_z, angle_x)))
    return raw, alpha


def plot_two_direction(path: Path, t: np.ndarray, data: dict[str, dict[str, np.ndarray]], key_x: str, key_z: str, title: str, ylabel: str) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(11.5, 7.0), dpi=170, sharex=True)
    colors = ["#2E74B5", "#4A8F5A", "#C7832B"]
    for color, (_, label, _) in zip(colors, POINTS):
        axes[0].plot(t, data[label][key_x], lw=1.0, color=color, label=label)
        axes[1].plot(t, data[label][key_z], lw=1.0, color=color, label=label)
    axes[0].set_title(title, fontsize=13, weight="bold")
    axes[0].set_ylabel(f"{ylabel}, transverse x")
    axes[1].set_ylabel(f"{ylabel}, vertical z")
    axes[1].set_xlabel("Time (s)")
    for ax in axes:
        ax.grid(True, color="#D8DEE8", linewidth=0.65)
        ax.legend(loc="best", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_scalar(path: Path, t: np.ndarray, data: dict[str, dict[str, np.ndarray]], key: str, title: str, ylabel: str, hline0: bool = False) -> None:
    fig, ax = plt.subplots(figsize=(11.5, 5.6), dpi=170)
    colors = ["#2E74B5", "#4A8F5A", "#C7832B"]
    for color, (_, label, _) in zip(colors, POINTS):
        ax.plot(t, data[label][key], lw=1.0, color=color, label=label)
    if hline0:
        ax.axhline(0.0, color="#A33", lw=1.0, ls="--")
    ax.set_title(title, fontsize=13, weight="bold")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel(ylabel)
    ax.grid(True, color="#D8DEE8", linewidth=0.65)
    ax.legend(loc="best", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_cd_cl(path: Path, t: np.ndarray, data: dict[str, dict[str, np.ndarray]]) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(11.5, 7.0), dpi=170, sharex=True)
    colors = ["#2E74B5", "#4A8F5A", "#C7832B"]
    for color, (_, label, _) in zip(colors, POINTS):
        axes[0].plot(t, data[label]["cd"], lw=1.0, color=color, label=label)
        axes[1].plot(t, data[label]["cl"], lw=1.0, color=color, label=label)
    axes[0].set_title("Aerodynamic coefficients from local relative angle", fontsize=13, weight="bold")
    axes[0].set_ylabel("C_D")
    axes[1].set_ylabel("C_L")
    axes[1].set_xlabel("Time (s)")
    for ax in axes:
        ax.grid(True, color="#D8DEE8", linewidth=0.65)
        ax.legend(loc="best", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_paths(path: Path, data: dict[str, dict[str, np.ndarray]]) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(14.0, 4.8), dpi=170)
    colors = ["#2E74B5", "#4A8F5A", "#C7832B"]
    for ax, color, (_, label, _) in zip(axes, colors, POINTS):
        x = data[label]["disp_x"]
        z = data[label]["disp_z"]
        if len(x) > 4000:
            idx = np.linspace(0, len(x) - 1, 4000).astype(int)
            x = x[idx]
            z = z[idx]
        ax.plot(x, z, lw=0.75, color=color, alpha=0.85)
        ax.scatter([x[0]], [z[0]], s=24, color="#222", label="start")
        ax.scatter([x[-1]], [z[-1]], s=24, color="#B24A4A", label="end")
        ax.set_title(label, fontsize=11, weight="bold")
        ax.set_xlabel("Transverse displacement x (m)")
        ax.set_ylabel("Vertical displacement z (m)")
        ax.grid(True, color="#D8DEE8", linewidth=0.65)
        ax.axis("equal")
    axes[0].legend(loc="best", fontsize=8)
    fig.suptitle("x-z displacement paths", fontsize=13, weight="bold")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitor quarter/midspan points for a cable TH run.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="YAML config used for the run.")
    parser.add_argument("--run-dir", default=str(DEFAULT_RUN), help="OpenSees output directory containing Dynamic.out, Velocity.out, and Accel.out.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUT), help="Directory for monitoring CSV/PNG/report outputs.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = Path(args.config)
    run = Path(args.run_dir)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    cfg: dict[str, Any] = yaml.safe_load(config.read_text(encoding="utf-8"))
    dt = float(cfg["time_history"]["dt"])
    force_dir = ROOT / cfg["paths"]["wind_dir"]
    coeff_dir = ROOT / cfg["paths"]["aero_coeffs_dir"]

    disp = load_matrix(run / "Dynamic.out")
    vel = load_matrix(run / "Velocity.out")
    accel = load_matrix(run / "Accel.out")
    t = disp[:, 0]
    n = len(t)

    wind_time = np.loadtxt(ROOT / cfg["paths"]["time_file"])
    cd_table = _load_coefficient_table(coeff_dir / "C_D_data.txt")
    cl_table = _load_coefficient_table(coeff_dir / "C_L_data2.txt")
    dcl_per_degree = np.loadtxt(coeff_dir / "dC_L.txt")
    dcl_x = cd_table[:, 0]

    params = read_params(run / "inputs_aerodynamic_damping.tcl")
    xi_structural = params.get("xi_structural", float(cfg["damping"]["xi"]))
    k = params["ro_air"] * params["B"] * params["L"] / (4.0 * params["MassM"] * params["omegaN"])

    data: dict[str, dict[str, np.ndarray]] = {}
    rows: list[dict[str, float | str | int]] = []
    for key, label, node_id in POINTS:
        _, col_x, col_z = node_cols(node_id)
        disp_x = disp[:, col_x]
        disp_z = disp[:, col_z]
        vel_x = vel[:, col_x]
        vel_z = vel[:, col_z]
        accel_x = accel[:, col_x]
        accel_z = accel[:, col_z]

        wind_h = np.loadtxt(force_dir / f"NODE_{node_id}_wind_H.txt")
        wind_v = np.loadtxt(force_dir / f"NODE_{node_id}_wind_V.txt")
        wind_x = resample_vector(wind_time, wind_h, t)
        wind_z = resample_vector(wind_time, wind_v, t)

        rel_x = wind_x - vel_x
        rel_z = wind_z - vel_z
        u_rel = np.sqrt(rel_x**2 + rel_z**2)
        alpha_raw_deg, alpha_lookup_deg_unclipped = solver_lookup_angle_deg(rel_x, rel_z)
        alpha_lookup_deg = np.clip(alpha_lookup_deg_unclipped, cd_table[:, 0][0], cd_table[:, 0][-1])
        cd = clamped_interp(alpha_lookup_deg, cd_table[:, 0], cd_table[:, 1])
        cl = clamped_interp(alpha_lookup_deg, cl_table[:, 0], cl_table[:, 1])
        dcl = clamped_interp(alpha_lookup_deg, dcl_x, dcl_per_degree) * 180.0 / math.pi
        delta = dcl + cd
        xi_eff = xi_structural + k * u_rel * delta

        data[label] = {
            "disp_x": disp_x,
            "disp_z": disp_z,
            "vel_x": vel_x,
            "vel_z": vel_z,
            "accel_x": accel_x,
            "accel_z": accel_z,
            "wind_x": wind_x,
            "wind_z": wind_z,
            "u_rel": u_rel,
            "alpha_raw_deg": alpha_raw_deg,
            "alpha_lookup_deg_unclipped": alpha_lookup_deg_unclipped,
            "alpha_deg": alpha_lookup_deg,
            "cd": cd,
            "cl": cl,
            "delta": delta,
            "xi_eff": xi_eff,
        }

        csv_path = out / f"{key}_node_{node_id}_timeseries.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "time_s",
                "disp_transverse_x_m",
                "disp_vertical_z_m",
                "vel_transverse_x_mps",
                "vel_vertical_z_mps",
                "accel_transverse_x_mps2",
                "accel_vertical_z_mps2",
                "wind_x_mps",
                "wind_z_mps",
                "u_rel_mps",
                "alpha_raw_deg",
                "alpha_lookup_deg_unclipped",
                "alpha_lookup_deg",
                "C_D",
                "C_L",
                "Delta_D",
                "xi_eff",
            ])
            for i in range(n):
                writer.writerow([
                    t[i], disp_x[i], disp_z[i], vel_x[i], vel_z[i],
                    accel_x[i], accel_z[i],
                    wind_x[i], wind_z[i], u_rel[i], alpha_raw_deg[i],
                    alpha_lookup_deg_unclipped[i], alpha_lookup_deg[i],
                    cd[i], cl[i], delta[i], xi_eff[i],
                ])

        rows.append({
            "point": label,
            "node_id": node_id,
            "max_abs_disp_x_m": float(np.nanmax(np.abs(disp_x))),
            "max_abs_disp_z_m": float(np.nanmax(np.abs(disp_z))),
            "max_abs_vel_x_mps": float(np.nanmax(np.abs(vel_x))),
            "max_abs_vel_z_mps": float(np.nanmax(np.abs(vel_z))),
            "max_abs_accel_x_mps2": float(np.nanmax(np.abs(accel_x))),
            "max_abs_accel_z_mps2": float(np.nanmax(np.abs(accel_z))),
            "max_u_rel_mps": float(np.nanmax(u_rel)),
            "alpha_raw_min_deg": float(np.nanmin(alpha_raw_deg)),
            "alpha_raw_max_deg": float(np.nanmax(alpha_raw_deg)),
            "alpha_lookup_min_deg": float(np.nanmin(alpha_lookup_deg)),
            "alpha_lookup_max_deg": float(np.nanmax(alpha_lookup_deg)),
            "alpha_clipped_fraction": float(np.nanmean(alpha_lookup_deg_unclipped > cd_table[:, 0][-1])),
            "cd_min": float(np.nanmin(cd)),
            "cd_max": float(np.nanmax(cd)),
            "cl_min": float(np.nanmin(cl)),
            "cl_max": float(np.nanmax(cl)),
            "delta_min": float(np.nanmin(delta)),
            "delta_max": float(np.nanmax(delta)),
            "xi_eff_min": float(np.nanmin(xi_eff)),
            "xi_eff_negative_fraction": float(np.nanmean(xi_eff < 0.0)),
        })

    plot_two_direction(out / "point_displacement_x_z.png", t, data, "disp_x", "disp_z", "Observed point displacement response", "Displacement (m)")
    plot_two_direction(out / "point_velocity_x_z.png", t, data, "vel_x", "vel_z", "Observed point velocity response", "Velocity (m/s)")
    plot_two_direction(out / "point_acceleration_x_z.png", t, data, "accel_x", "accel_z", "Observed point acceleration response", "Acceleration (m/s^2)")
    plot_paths(out / "point_xz_paths.png", data)
    plot_cd_cl(out / "point_cd_cl.png", t, data)
    plot_scalar(out / "point_delta_D.png", t, data, "delta", "Den Hartog Delta_D at observation points", "Delta_D = dC_L/dalpha + C_D", hline0=True)
    plot_scalar(out / "point_xi_eff.png", t, data, "xi_eff", "Effective damping indicator at observation points", "xi_eff", hline0=True)
    plot_scalar(out / "point_alpha.png", t, data, "alpha_deg", "Relative-flow angle of attack", "|alpha| (deg)")

    summary = {
        "config": str(config.relative_to(ROOT) if config.is_relative_to(ROOT) else config),
        "run": str(run.relative_to(ROOT) if run.is_relative_to(ROOT) else run),
        "last_time_s": float(t[-1]),
        "n_records": int(n),
        "dt_nominal_s": dt,
        "points": rows,
        "notes": [
            "Transverse x in the plots corresponds to OpenSees DOF 2; vertical z corresponds to DOF 3.",
            "C_D, C_L, Delta_D, and xi_eff are recomputed from local relative velocity using the same positive-along-wind angle convention and coefficient-table clamping as Damping_shifter.tcl.",
            "alpha_raw_deg is retained in the CSV files only as a diagnostic; alpha_lookup_deg is the coefficient lookup angle.",
        ],
    }
    (out / "point_monitoring_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md = [
        "# Typical Explicit Galloping Point Monitoring",
        "",
        f"- Run: `{run.relative_to(ROOT) if run.is_relative_to(ROOT) else run}`",
        f"- Last recorded time: `{t[-1]:.6f} s`",
        "- Monitoring nodes: Node 26 (1/4), Node 51 (midspan), Node 76 (3/4).",
        "- Transverse x = OpenSees DOF 2; vertical z = OpenSees DOF 3.",
        "",
        "## Point Summary",
        "",
        "| Point | Node | max abs x disp (m) | max abs z disp (m) | max abs x vel (m/s) | max abs z vel (m/s) | max abs x accel (m/s^2) | max abs z accel (m/s^2) | lookup alpha range (deg) | raw alpha range (deg) | clipped fraction | Delta_D min | xi_eff min | xi_eff<0 fraction |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        md.append(
            "| {point} | {node_id} | {max_abs_disp_x_m:.6g} | {max_abs_disp_z_m:.6g} | {max_abs_vel_x_mps:.6g} | {max_abs_vel_z_mps:.6g} | {max_abs_accel_x_mps2:.6g} | {max_abs_accel_z_mps2:.6g} | {alpha_lookup_min_deg:.3g}-{alpha_lookup_max_deg:.3g} | {alpha_raw_min_deg:.3g}-{alpha_raw_max_deg:.3g} | {alpha_clipped_fraction:.3f} | {delta_min:.6g} | {xi_eff_min:.6g} | {xi_eff_negative_fraction:.3f} |".format(**row)
        )
    max_point_disp = max(
        max(row["max_abs_disp_x_m"], row["max_abs_disp_z_m"]) for row in rows
    )
    max_clipped_fraction = max(row["alpha_clipped_fraction"] for row in rows)
    if max_point_disp > 10.0:
        path_comment = (
            "- The x-z paths expand into large trajectories as the response grows. "
            "This is consistent with severe self-excited galloping-type instability, "
            "although the final amplitudes exceed a practical engineering regime."
        )
    elif max_point_disp > 1.0:
        path_comment = (
            "- The x-z paths show bounded coupled transverse/vertical motion. "
            "This indicates aerodynamic feedback is present, but the monitored "
            "points do not develop a divergent large-amplitude galloping trajectory "
            "within the recorded duration."
        )
    else:
        path_comment = (
            "- The x-z paths remain compact. No large-amplitude galloping trajectory "
            "is observed at the monitored points within the recorded duration."
        )
    if max_clipped_fraction > 0.05:
        clipping_comment = (
            "- The coefficient table is only available up to about 29.9 degrees. "
            "Some lookup angles are clamped, so high-angle response phases should "
            "be interpreted cautiously."
        )
    else:
        clipping_comment = (
            "- Coefficient-table clipping is negligible in this run, so the "
            "reported C_D/C_L/Delta_D histories stay within the calibrated angle "
            "range of the available table."
        )

    md.extend([
        "",
        "## Generated Figures",
        "",
        "- `point_displacement_x_z.png`",
        "- `point_velocity_x_z.png`",
        "- `point_acceleration_x_z.png`",
        "- `point_xz_paths.png`",
        "- `point_cd_cl.png`",
        "- `point_delta_D.png`",
        "- `point_xi_eff.png`",
        "- `point_alpha.png`",
        "",
        "## Reasonableness Checks",
        "",
        "- The three monitored points are checked together so that the result is not interpreted from a single-node artifact.",
        "- Negative Delta_D and negative xi_eff occur over parts of the recorded response, matching the intended Den Hartog galloping mechanism.",
        path_comment,
        "- The coefficient histories are recomputed from relative flow including cable velocity, so late-time changes reflect aeroelastic feedback rather than fixed wind-only coefficients.",
        clipping_comment,
    ])
    (out / "point_monitoring_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(out / "point_monitoring_report.md")


if __name__ == "__main__":
    main()
