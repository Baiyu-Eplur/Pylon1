from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = ROOT / "output" / "diagnostics" / "cable_rod_long_test" / "calibrated_cable_rod" / "run"
DEFAULT_OUT = ROOT / "output" / "diagnostics" / "cable_rod_long_test" / "comparison" / "calibrated_cable_rod_collapse_cause"

N_NODES = 101
KEY_NODES = {
    "quarter": 26,
    "midspan": 51,
    "three_quarter": 76,
}
KEY_ELEMENTS = {
    "quarter": 25,
    "midspan_left": 50,
    "midspan_right": 51,
    "three_quarter": 75,
}


def read_node_history(path: Path, prefix: str) -> pd.DataFrame:
    raw = pd.read_csv(path, sep=r"\s+", header=None, engine="python")
    cols = ["time"]
    for node in range(1, N_NODES + 1):
        cols.extend([f"{prefix}x_{node}", f"{prefix}y_{node}", f"{prefix}z_{node}"])
    raw.columns = cols
    return raw


def nearest_rows(df: pd.DataFrame, times: list[float], time_col: str = "time") -> dict[str, dict]:
    rows: dict[str, dict] = {}
    tvals = df[time_col].to_numpy(dtype=float)
    for t in times:
        idx = int(np.argmin(np.abs(tvals - t)))
        rows[f"{t:.6f}"] = df.iloc[idx].to_dict()
    return rows


def first_threshold(df: pd.DataFrame, col: str, threshold: float, op: str = "abs_gt") -> float | None:
    data = df[col].to_numpy(dtype=float)
    if op == "abs_gt":
        mask = np.abs(data) >= threshold
    elif op == "gt":
        mask = data >= threshold
    elif op == "lt":
        mask = data <= threshold
    else:
        raise ValueError(op)
    if not mask.any():
        return None
    return float(df.iloc[int(np.argmax(mask))]["time"])


def add_key_node_norms(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    out = df[["time"]].copy()
    for label, node in KEY_NODES.items():
        x = df[f"{prefix}x_{node}"].to_numpy(float)
        z = df[f"{prefix}z_{node}"].to_numpy(float)
        out[f"{label}_{prefix}xz_norm"] = np.sqrt(x * x + z * z)
        out[f"{label}_{prefix}x"] = x
        out[f"{label}_{prefix}z"] = z
    out[f"max_{prefix}xz_norm"] = out[[f"{k}_{prefix}xz_norm" for k in KEY_NODES]].max(axis=1)
    return out


def load_status(run_dir: Path) -> dict[str, str]:
    path = run_dir / "analysis_status.txt"
    if not path.exists():
        return {"STATUS": "missing"}
    status: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            status[parts[0]] = parts[1]
    return status


def key_node_aero_summary(node_power: pd.DataFrame) -> dict[str, dict]:
    summary: dict[str, dict] = {}
    for label, node in KEY_NODES.items():
        sub = node_power[node_power["node"] == node].copy()
        if sub.empty:
            continue
        sub["delta_force_norm"] = np.sqrt(
            sub["delta_fx"] ** 2 + sub["delta_fy"] ** 2 + sub["delta_fz"] ** 2
        )
        summary[label] = {
            "node": node,
            "max_U_rel": float(sub["U_rel"].max()),
            "max_U_rel_time": float(sub.loc[sub["U_rel"].idxmax(), "time"]),
            "max_abs_alpha_deg": float(sub["alpha_deg"].abs().max()),
            "max_abs_alpha_time": float(sub.loc[sub["alpha_deg"].abs().idxmax(), "time"]),
            "first_clipped": first_threshold(sub, "clipped", 0.5, "gt"),
            "max_delta_force_N": float(sub["delta_force_norm"].max()),
            "max_delta_force_time": float(sub.loc[sub["delta_force_norm"].idxmax(), "time"]),
            "max_abs_delta_power_W": float(sub["delta_power"].abs().max()),
            "max_abs_delta_power_time": float(sub.loc[sub["delta_power"].abs().idxmax(), "time"]),
        }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", default=str(DEFAULT_RUN))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    dyn = read_node_history(run_dir / "Dynamic.out", "u")
    vel = read_node_history(run_dir / "Velocity.out", "v")
    acc = read_node_history(run_dir / "Accel.out", "a")
    disp_key = add_key_node_norms(dyn, "u")
    vel_key = add_key_node_norms(vel, "v")
    acc_key = add_key_node_norms(acc, "a")

    aero_total = pd.read_csv(run_dir / "incremental_quasi_steady_aero_force_log.txt", sep=r"\s+", engine="python")
    node_power = pd.read_csv(run_dir / "incremental_qs_node_power_log.csv")
    elem_summary = pd.read_csv(run_dir / "element_strain_tension_summary_log.csv")
    elem_log = pd.read_csv(run_dir / "element_strain_tension_log.csv")

    node_power["delta_force_norm"] = np.sqrt(
        node_power["delta_fx"] ** 2 + node_power["delta_fy"] ** 2 + node_power["delta_fz"] ** 2
    )

    t_fail = float(load_status(run_dir).get("TIME", dyn["time"].max()))
    landmarks = [
        68.3,
        69.51895049845076,
        69.86118860198653,
        70.1704551021575,
        92.70132890318229,
        97.40647966018898,
        107.7392460761126,
        107.811040145845,
        t_fail,
    ]

    events = {
        "status": load_status(run_dir),
        "time_end_displacement_s": float(dyn["time"].max()),
        "time_end_aero_s": float(aero_total["time"].max()),
        "time_end_element_s": float(elem_summary["time"].max()),
        "first_motion_acc_100mps2": first_threshold(acc_key, "max_axz_norm", 100.0),
        "first_motion_vel_1mps": first_threshold(vel_key, "max_vxz_norm", 1.0),
        "first_aero_delta_force_500N": first_threshold(aero_total, "total_abs_delta_force", 500.0, "gt"),
        "first_aero_alpha_clipping": first_threshold(aero_total, "clipped_count", 0.5, "gt"),
        "first_negative_tension": first_threshold(elem_summary, "min_estimated_tension_N", 0.0, "lt"),
        "first_strain_0p001": first_threshold(elem_summary, "max_abs_strain", 0.001, "gt"),
        "first_strain_0p01": first_threshold(elem_summary, "max_abs_strain", 0.01, "gt"),
        "first_tension_500kN": first_threshold(elem_summary, "max_abs_tension_N", 500000.0, "gt"),
        "first_aero_power_1000W": first_threshold(aero_total, "total_delta_power", 1000.0),
        "first_aero_power_10000W": first_threshold(aero_total, "total_delta_power", 10000.0),
        "key_node_aero": key_node_aero_summary(node_power),
    }

    max_rows = {
        "max_displacement_key_nodes": disp_key.loc[disp_key["max_uxz_norm"].idxmax()].to_dict(),
        "max_velocity_key_nodes": vel_key.loc[vel_key["max_vxz_norm"].idxmax()].to_dict(),
        "max_acceleration_key_nodes": acc_key.loc[acc_key["max_axz_norm"].idxmax()].to_dict(),
        "max_total_abs_delta_force": aero_total.loc[aero_total["total_abs_delta_force"].idxmax()].to_dict(),
        "max_abs_total_delta_power": aero_total.loc[aero_total["total_delta_power"].abs().idxmax()].to_dict(),
        "max_abs_strain": elem_summary.loc[elem_summary["max_abs_strain"].idxmax()].to_dict(),
        "min_tension": elem_summary.loc[elem_summary["min_estimated_tension_N"].idxmin()].to_dict(),
        "max_abs_tension": elem_summary.loc[elem_summary["max_abs_tension_N"].idxmax()].to_dict(),
    }

    key_element_windows: dict[str, list[dict]] = {}
    window = elem_log[(elem_log["time"] >= 68.0) & (elem_log["time"] <= 108.052)].copy()
    for label, elem in KEY_ELEMENTS.items():
        sub = window[window["element"] == elem]
        key_element_windows[label] = [
            {
                "time": float(row["time"]),
                "strain": float(row["strain"]),
                "estimated_tension_N": float(row["estimated_total_tension_N"]),
                "raw_elastic_tension_N": float(row["raw_elastic_tension_N"]),
                "is_slack": int(row["is_slack"]),
            }
            for _, row in sub.tail(20).iterrows()
        ]

    n_align = min(len(disp_key), len(vel_key), len(acc_key))
    merged_key = pd.concat(
        [
            disp_key.iloc[:n_align].reset_index(drop=True),
            vel_key.iloc[:n_align].drop(columns=["time"]).reset_index(drop=True),
            acc_key.iloc[:n_align].drop(columns=["time"]).reset_index(drop=True),
        ],
        axis=1,
    )
    snapshots = {
        "key_motion": nearest_rows(merged_key, landmarks),
        "aero_total": nearest_rows(aero_total, landmarks),
        "element_summary": nearest_rows(elem_summary, landmarks),
    }

    result = {
        "run_dir": str(run_dir),
        "events": events,
        "maxima": max_rows,
        "snapshots": snapshots,
        "key_element_tail_68_to_failure": key_element_windows,
        "monitoring_completeness": {
            "has_displacement": (run_dir / "Dynamic.out").exists(),
            "has_velocity": (run_dir / "Velocity.out").exists(),
            "has_acceleration": (run_dir / "Accel.out").exists(),
            "has_support_reaction": (run_dir / "SupportReactions.out").exists(),
            "has_element_summary": (run_dir / "element_strain_tension_summary_log.csv").exists(),
            "has_element_log": (run_dir / "element_strain_tension_log.csv").exists(),
            "has_aero_total_force": (run_dir / "incremental_quasi_steady_aero_force_log.txt").exists(),
            "has_node_aero_force_alpha_urel": (run_dir / "incremental_qs_node_power_log.csv").exists(),
            "has_node_free_stream_wind": {"wind_y", "wind_z", "U_wind"}.issubset(set(node_power.columns)),
            "has_node_reference_alpha": "ref_alpha_deg" in node_power.columns,
            "has_node_relative_flow_components": {"rel_y", "rel_z"}.issubset(set(node_power.columns)),
            "has_effective_damping": (run_dir / "damping_change_log.txt").exists(),
            "has_solver_status": (run_dir / "analysis_status.txt").exists(),
            "note": (
                "The expanded monitoring run stores free-stream wind components, U_wind, "
                "relative wind components, U_rel, alpha, CD/CL, reference/current/delta "
                "aerodynamic forces, and power per logged node/time row."
            ),
        },
    }

    (out_dir / "calibrated_cable_rod_collapse_cause_summary.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )

    fig, axes = plt.subplots(5, 1, figsize=(14, 15), sharex=True)
    axes[0].plot(disp_key["time"], disp_key["max_uxz_norm"], label="key-node max displacement")
    axes[0].set_ylabel("disp (m)")
    axes[1].plot(vel_key["time"], vel_key["max_vxz_norm"], label="key-node max velocity", color="tab:orange")
    axes[1].set_ylabel("vel (m/s)")
    axes[2].plot(aero_total["time"], aero_total["max_alpha_current_deg"], label="max alpha", color="tab:green")
    axes[2].plot(aero_total["time"], aero_total["clipped_count"], label="clipped count", color="tab:red", alpha=0.6)
    axes[2].set_ylabel("alpha/count")
    axes[2].legend(loc="upper left")
    axes[3].plot(aero_total["time"], aero_total["total_abs_delta_force"], label="total |delta F|", color="tab:purple")
    axes[3].set_ylabel("delta F (N)")
    axes[4].plot(elem_summary["time"], elem_summary["min_estimated_tension_N"] / 1000, label="min tension", color="tab:brown")
    axes[4].plot(elem_summary["time"], elem_summary["max_abs_tension_N"] / 1000, label="max |tension|", color="tab:gray")
    axes[4].set_ylabel("tension (kN)")
    axes[4].set_xlabel("time (s)")
    for ax in axes:
        ax.axvline(t_fail, color="black", linestyle="--", linewidth=1)
        ax.grid(True, alpha=0.25)
    axes[4].legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(out_dir / "calibrated_cable_rod_collapse_cause_timeline.png", dpi=180)
    plt.close(fig)

    md = [
        "# Calibrated Cable/Rod Collapse Cause Analysis",
        "",
        f"Run directory: `{run_dir}`",
        "",
        "## Monitoring Completeness",
    ]
    for key, value in result["monitoring_completeness"].items():
        md.append(f"- `{key}`: {value}")
    md.extend(
        [
            "",
            "## Ordered Critical Events",
        ]
    )
    ordered = []
    for key, value in events.items():
        if key in {"status", "key_node_aero"} or value is None:
            continue
        if isinstance(value, (int, float)):
            ordered.append((key, float(value)))
    for key, value in sorted(ordered, key=lambda kv: kv[1]):
        md.append(f"- `{key}`: `{value:.6f} s`")
    md.extend(
        [
            "",
            "## Key Interpretation",
            "",
            "- The earliest clear warning is key-node acceleration growth around `68.3 s`, before large displacement.",
            "- Incremental aerodynamic force and alpha clipping appear at about `69.519 s`, before the first recorded negative/low tension at `69.861 s`.",
            "- Large displacement follows after this aerodynamic/kinematic transition, not before it.",
            "- The final OpenSees failure at `108.051751 s` occurs after high velocity, severe alpha clipping, large aerodynamic power oscillation, and large axial force/strain amplification.",
            "- Therefore the direct failure is a nonlinear convergence failure in an already severe coupled aero-structural state.",
            "- The likely root issue is that the current beam/rod branch plus large-angle quasi-steady aerodynamics permits a post-taut-cable state outside the validated galloping regime: large relative velocity drives alpha to the coefficient clipping range, while the structural branch allows large compression/tension excursions.",
        ]
    )
    (out_dir / "calibrated_cable_rod_collapse_cause.md").write_text("\n".join(md), encoding="utf-8")

    print(out_dir / "calibrated_cable_rod_collapse_cause_summary.json")
    print(out_dir / "calibrated_cable_rod_collapse_cause_timeline.png")


if __name__ == "__main__":
    main()
