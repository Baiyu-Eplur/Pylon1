from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "output" / "diagnostics" / "c4_structural_model_comparison_200s" / "tension_only" / "run"
OUT = ROOT / "output" / "diagnostics" / "c4_structural_model_comparison_200s" / "comparison" / "tension_only_failure_mechanism"
N_NODES = 101
WINDOWS = {
    "pre_onset_86_88": (86.0, 88.0),
    "onset_88_91": (88.0, 91.0),
    "post_onset_91_96": (91.0, 96.0),
    "late_110_130": (110.0, 130.0),
}


def load_matrix(path: Path) -> np.ndarray:
    data = np.loadtxt(path)
    if data.ndim == 1:
        data = data[np.newaxis, :]
    return data


def load_csv(path: Path) -> np.ndarray:
    data = np.genfromtxt(path, names=True, delimiter=",", encoding=None)
    if data.shape == ():
        data = np.array([data], dtype=data.dtype)
    return data


def load_space(path: Path) -> np.ndarray:
    data = np.genfromtxt(path, names=True)
    if data.shape == ():
        data = np.array([data], dtype=data.dtype)
    return data


def reshape_nodes(mat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return mat[:, 0], mat[:, 1:].reshape(mat.shape[0], N_NODES, 3)


def nearest_rows(table: np.ndarray, time_name: str, t0: float, half_width: float = 0.03) -> np.ndarray:
    t = np.asarray(table[time_name], dtype=float)
    return table[np.abs(t - t0) <= half_width]


def top_nodes_at_time(table: np.ndarray, t0: float, value_name: str, n: int = 10) -> list[dict]:
    rows = nearest_rows(table, "time", t0, half_width=0.03)
    if rows.size == 0:
        return []
    vals = np.asarray(rows[value_name], dtype=float)
    order = np.argsort(np.abs(vals))[::-1][:n]
    out = []
    for idx in order:
        row = rows[idx]
        item = {"time": float(row["time"]), "node": int(row["node"]), value_name: float(row[value_name])}
        for key in ("delta_fx", "delta_fy", "delta_fz", "vx", "vy", "vz", "alpha_deg", "clipped"):
            if key in rows.dtype.names:
                item[key] = float(row[key]) if key != "clipped" else int(row[key])
        out.append(item)
    return out


def summarize_windows(
    dyn: np.ndarray,
    vel: np.ndarray,
    acc: np.ndarray,
    ten_summary: np.ndarray,
    force: np.ndarray,
) -> dict:
    dt, dxyz = reshape_nodes(dyn)
    vt, vxyz = reshape_nodes(vel)
    at, axyz = reshape_nodes(acc)
    dmag = np.linalg.norm(dxyz[:, :, [0, 2]], axis=2)
    vmag = np.linalg.norm(vxyz[:, :, [0, 2]], axis=2)
    amag = np.linalg.norm(axyz[:, :, [0, 2]], axis=2)
    out = {}
    for name, (t0, t1) in WINDOWS.items():
        dmask = (dt >= t0) & (dt <= t1)
        vmask = (vt >= t0) & (vt <= t1)
        amask = (at >= t0) & (at <= t1)
        ten_t = np.asarray(ten_summary["time"], dtype=float)
        f_t = np.asarray(force["time"], dtype=float)
        tmask = (ten_t >= t0) & (ten_t <= t1)
        fmask = (f_t >= t0) & (f_t <= t1)
        out[name] = {
            "time_range": [t0, t1],
            "max_disp_m": float(np.max(dmag[dmask])) if np.any(dmask) else None,
            "max_vel_mps": float(np.max(vmag[vmask])) if np.any(vmask) else None,
            "max_acc_mps2": float(np.max(amag[amask])) if np.any(amask) else None,
            "max_abs_strain": float(np.max(ten_summary["max_abs_strain"][tmask])) if np.any(tmask) else None,
            "max_abs_tension_N": float(np.max(ten_summary["max_abs_tension_N"][tmask])) if np.any(tmask) else None,
            "min_tension_N": float(np.min(ten_summary["min_estimated_tension_N"][tmask])) if np.any(tmask) else None,
            "max_slack_count": int(np.max(ten_summary["slack_element_count"][tmask])) if np.any(tmask) else None,
            "max_total_abs_delta_force_N": float(np.max(force["total_abs_delta_force"][fmask])) if np.any(fmask) else None,
            "max_alpha_deg": float(np.max(np.abs(force["max_alpha_current_deg"][fmask]))) if np.any(fmask) else None,
            "max_clipped_count": int(np.max(force["clipped_count"][fmask])) if np.any(fmask) else None,
            "max_total_delta_power_W": float(np.max(force["total_delta_power"][fmask])) if np.any(fmask) else None,
            "min_total_delta_power_W": float(np.min(force["total_delta_power"][fmask])) if np.any(fmask) else None,
        }
    return out


def event_context() -> dict:
    dyn = load_matrix(RUN / "Dynamic.out")
    vel = load_matrix(RUN / "Velocity.out")
    acc = load_matrix(RUN / "Accel.out")
    ten = load_csv(RUN / "element_strain_tension_summary_log.csv")
    elem = load_csv(RUN / "element_strain_tension_log.csv")
    force = load_space(RUN / "incremental_quasi_steady_aero_force_log.txt")
    node_power = load_csv(RUN / "incremental_qs_node_power_log.csv")

    events = {
        "first_acc_100": 88.35,
        "first_vel_1": 89.35,
        "first_slack": 89.73664031101754,
        "force_500": 89.86782761150748,
        "force_1000": 90.2152782049681,
        "first_alpha_clip": 90.45577503970993,
        "alpha_60": 91.35915405496358,
    }
    summary: dict = {
        "event_times_s": events,
        "windows": summarize_windows(dyn, vel, acc, ten, force),
    }

    # Element rows around the first slack event.
    rows = nearest_rows(elem, "time", events["first_slack"], half_width=0.001)
    slack_rows = rows[np.asarray(rows["estimated_total_tension_N"], dtype=float) <= 0.0]
    summary["first_slack_rows"] = [
        {
            "time": float(r["time"]),
            "element": int(r["element"]),
            "initial_length": float(r["initial_length"]),
            "current_length": float(r["current_length"]),
            "strain": float(r["strain"]),
            "raw_elastic_tension_N": float(r["raw_elastic_tension_N"]),
            "estimated_total_tension_N": float(r["estimated_total_tension_N"]),
        }
        for r in slack_rows
    ]

    # Pre-slack minimum tension rows.
    pre_rows = elem[(np.asarray(elem["time"], dtype=float) >= 88.0) & (np.asarray(elem["time"], dtype=float) <= events["first_slack"])]
    order = np.argsort(np.asarray(pre_rows["raw_elastic_tension_N"], dtype=float))[:20]
    summary["lowest_raw_tension_before_first_slack"] = [
        {
            "time": float(pre_rows[i]["time"]),
            "element": int(pre_rows[i]["element"]),
            "strain": float(pre_rows[i]["strain"]),
            "raw_elastic_tension_N": float(pre_rows[i]["raw_elastic_tension_N"]),
            "estimated_total_tension_N": float(pre_rows[i]["estimated_total_tension_N"]),
        }
        for i in order
    ]

    for label, t0 in events.items():
        summary[f"top_delta_power_nodes_at_{label}"] = top_nodes_at_time(
            node_power, t0, "delta_power", n=8
        )

    return summary


def plot_local_timeseries() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ten = load_csv(RUN / "element_strain_tension_summary_log.csv")
    force = load_space(RUN / "incremental_quasi_steady_aero_force_log.txt")
    dyn = load_matrix(RUN / "Dynamic.out")
    vel = load_matrix(RUN / "Velocity.out")
    acc = load_matrix(RUN / "Accel.out")
    dt, dxyz = reshape_nodes(dyn)
    vt, vxyz = reshape_nodes(vel)
    at, axyz = reshape_nodes(acc)
    dmag = np.max(np.linalg.norm(dxyz[:, :, [0, 2]], axis=2), axis=1)
    vmag = np.max(np.linalg.norm(vxyz[:, :, [0, 2]], axis=2), axis=1)
    amag = np.max(np.linalg.norm(axyz[:, :, [0, 2]], axis=2), axis=1)

    fig, axes = plt.subplots(6, 1, figsize=(11, 12), sharex=True)
    axes[0].plot(dt, dmag)
    axes[0].set_ylabel("max disp (m)")
    axes[1].plot(vt, vmag)
    axes[1].set_ylabel("max vel (m/s)")
    axes[2].plot(at, amag)
    axes[2].set_ylabel("max acc (m/s2)")
    axes[3].plot(ten["time"], ten["slack_element_count"], label="slack count")
    axes[3].set_ylabel("slack count")
    axes[4].plot(force["time"], force["total_abs_delta_force"], label="|Delta F|")
    axes[4].set_ylabel("|Delta F| (N)")
    axes[5].plot(force["time"], force["max_alpha_current_deg"], label="alpha")
    axes[5].plot(force["time"], force["clipped_count"], label="clipped count")
    axes[5].set_ylabel("alpha / clipped")
    axes[5].set_xlabel("time (s)")
    for ax in axes:
        ax.set_xlim(86, 94)
        ax.grid(True, alpha=0.25)
        ax.axvline(88.35, color="#777777", lw=0.8, ls="--")
        ax.axvline(89.73664031101754, color="#a85", lw=0.8, ls="--")
        ax.axvline(90.45577503970993, color="#a33", lw=0.8, ls="--")
    axes[5].legend()
    fig.tight_layout()
    fig.savefig(OUT / "tension_only_86_94_onset_chain.png", dpi=180)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summary = event_context()
    (OUT / "tension_only_failure_mechanism_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    plot_local_timeseries()
    print(OUT / "tension_only_failure_mechanism_summary.json")
    print(OUT / "tension_only_86_94_onset_chain.png")


if __name__ == "__main__":
    main()
