from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CASES = {
    "C4 tension-only": ROOT / "output" / "diagnostics" / "typical_incremental_qs_c4_static_balance" / "run",
    "C4 bidirectional axial": ROOT / "output" / "diagnostics" / "typical_incremental_qs_c4_bidirectional_axial" / "run",
}
OUT = ROOT / "output" / "diagnostics" / "typical_incremental_qs_c4_bidirectional_axial" / "comparison"
N_NODES = 101
MONITOR_NODES = {
    "1/4 span": 26,
    "midspan": 51,
    "3/4 span": 76,
}


def load_table(path: Path) -> np.ndarray:
    return np.genfromtxt(path, names=True, delimiter=",", dtype=None, encoding=None)


def load_matrix(path: Path) -> np.ndarray:
    return np.loadtxt(path)


def node_component(mat: np.ndarray, node_id: int, dof: int) -> np.ndarray:
    col = 1 + (node_id - 1) * 3 + dof
    return mat[:, col]


def summarize_case(run: Path) -> dict[str, float | int | str | None]:
    dyn = load_matrix(run / "Dynamic.out")
    vel = load_matrix(run / "Velocity.out")
    acc = load_matrix(run / "Accel.out")
    ten = load_table(run / "element_strain_tension_summary_log.csv")
    force = np.genfromtxt(run / "incremental_quasi_steady_aero_force_log.txt", names=True)

    disp_xyz = dyn[:, 1:].reshape(dyn.shape[0], N_NODES, 3)
    vel_xyz = vel[:, 1:].reshape(vel.shape[0], N_NODES, 3)
    acc_xyz = acc[:, 1:].reshape(acc.shape[0], N_NODES, 3)
    disp_mag = np.linalg.norm(disp_xyz[:, :, [0, 2]], axis=2)
    vel_mag = np.linalg.norm(vel_xyz[:, :, [0, 2]], axis=2)
    acc_mag = np.linalg.norm(acc_xyz[:, :, [0, 2]], axis=2)

    min_tension = np.asarray(ten["min_estimated_tension_N"], dtype=float)
    max_abs_tension = np.asarray(ten["max_abs_tension_N"], dtype=float)
    max_abs_strain = np.asarray(ten["max_abs_strain"], dtype=float)
    ten_time = np.asarray(ten["time"], dtype=float)
    neg_mask = min_tension < 0.0

    summary: dict[str, float | int | str | None] = {
        "status": read_status(run),
        "time_end_displacement_s": float(dyn[-1, 0]),
        "time_end_tension_log_s": float(ten_time[-1]),
        "max_xz_displacement_m": float(np.max(disp_mag)),
        "max_xz_velocity_mps": float(np.max(vel_mag)),
        "max_xz_acceleration_mps2": float(np.max(acc_mag)),
        "min_estimated_tension_N": float(np.min(min_tension)),
        "min_estimated_tension_time_s": float(ten_time[int(np.argmin(min_tension))]),
        "max_abs_tension_N": float(np.max(max_abs_tension)),
        "max_abs_tension_time_s": float(ten_time[int(np.argmax(max_abs_tension))]),
        "max_abs_strain": float(np.max(max_abs_strain)),
        "negative_tension_logged_rows": int(np.sum(neg_mask)),
        "first_negative_tension_time_s": float(ten_time[np.argmax(neg_mask)]) if np.any(neg_mask) else None,
        "max_total_abs_delta_force_N": float(np.max(force["total_abs_delta_force"])),
        "max_abs_delta_force_N": float(np.max(force["max_abs_delta_force"])),
        "max_abs_alpha_current_deg": float(np.max(np.abs(force["max_alpha_current_deg"]))),
        "max_clipped_count": int(np.max(force["clipped_count"])),
        "max_total_delta_power_W": float(np.max(force["total_delta_power"])),
        "min_total_delta_power_W": float(np.min(force["total_delta_power"])),
    }
    for label, node_id in MONITOR_NODES.items():
        summary[f"{label}_max_abs_x_disp_m"] = float(np.max(np.abs(node_component(dyn, node_id, 0))))
        summary[f"{label}_max_abs_z_disp_m"] = float(np.max(np.abs(node_component(dyn, node_id, 2))))
    return summary


def read_status(run: Path) -> str:
    path = run / "analysis_status.txt"
    if not path.exists():
        return "missing"
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            values[parts[0]] = parts[1]
    return f"{values.get('STATUS', 'unknown')} / {values.get('MESSAGE', 'unknown')}"


def plot_comparison() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    colors = {
        "C4 tension-only": "#2b6e4a",
        "C4 bidirectional axial": "#9a4f20",
    }

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for label, run in CASES.items():
        ten = load_table(run / "element_strain_tension_summary_log.csv")
        axes[0].plot(ten["time"], ten["min_estimated_tension_N"] / 1000.0, label=label, color=colors[label])
        axes[1].plot(ten["time"], ten["max_abs_tension_N"] / 1000.0, label=label, color=colors[label])
        axes[2].plot(ten["time"], ten["max_abs_strain"], label=label, color=colors[label])
    axes[0].axhline(0, color="black", lw=0.8)
    axes[0].set_ylabel("min tension (kN)")
    axes[1].set_ylabel("max |tension| (kN)")
    axes[2].set_ylabel("max |strain|")
    axes[2].set_xlabel("time (s)")
    for ax in axes:
        ax.grid(True, alpha=0.25)
        ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "c4_tension_strain_comparison.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(3, 2, figsize=(11, 8), sharex=True)
    for row, (point, node_id) in enumerate(MONITOR_NODES.items()):
        for label, run in CASES.items():
            dyn = load_matrix(run / "Dynamic.out")
            axes[row, 0].plot(dyn[:, 0], node_component(dyn, node_id, 0), label=label, color=colors[label], lw=1)
            axes[row, 1].plot(dyn[:, 0], node_component(dyn, node_id, 2), label=label, color=colors[label], lw=1)
        axes[row, 0].set_ylabel(f"{point}\nx disp (m)")
        axes[row, 1].set_ylabel("z disp (m)")
        axes[row, 0].grid(True, alpha=0.25)
        axes[row, 1].grid(True, alpha=0.25)
    axes[0, 0].legend()
    axes[0, 1].legend()
    axes[-1, 0].set_xlabel("time (s)")
    axes[-1, 1].set_xlabel("time (s)")
    fig.tight_layout()
    fig.savefig(OUT / "c4_monitor_displacement_comparison.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    for label, run in CASES.items():
        force = np.genfromtxt(run / "incremental_quasi_steady_aero_force_log.txt", names=True)
        axes[0].plot(force["time"], force["total_abs_delta_force"], label=label, color=colors[label])
        axes[1].plot(force["time"], force["total_delta_power"], label=label, color=colors[label])
    axes[0].set_ylabel("total |Delta F| (N)")
    axes[1].set_ylabel("Delta F dot v (W)")
    axes[1].set_xlabel("time (s)")
    for ax in axes:
        ax.grid(True, alpha=0.25)
        ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "c4_incremental_force_power_comparison.png", dpi=180)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {label: summarize_case(run) for label, run in CASES.items()}
    (OUT / "c4_bidirectional_axial_comparison_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    plot_comparison()
    print(OUT / "c4_bidirectional_axial_comparison_summary.json")
    print(OUT / "c4_tension_strain_comparison.png")
    print(OUT / "c4_monitor_displacement_comparison.png")
    print(OUT / "c4_incremental_force_power_comparison.png")


if __name__ == "__main__":
    main()
