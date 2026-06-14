from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = ROOT / "output" / "diagnostics" / "c4_structural_model_comparison_200s"
CASES = {
    "tension-only": OUT_ROOT / "tension_only" / "run",
    "bidirectional axial": OUT_ROOT / "bidirectional_axial" / "run",
}
OUT = OUT_ROOT / "comparison"
N_NODES = 101
MONITOR_NODES = {
    "1/4 span": 26,
    "midspan": 51,
    "3/4 span": 76,
}


def read_status(run: Path) -> dict[str, str]:
    path = run / "analysis_status.txt"
    values: dict[str, str] = {}
    if not path.exists():
        return {"STATUS": "missing", "MESSAGE": "analysis_status.txt missing"}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            values[parts[0]] = parts[1]
    return values


def load_matrix(path: Path) -> np.ndarray | None:
    if not path.exists() or path.stat().st_size == 0:
        return None
    data = np.loadtxt(path)
    if data.ndim == 1:
        data = data[np.newaxis, :]
    return data


def load_csv(path: Path) -> np.ndarray | None:
    if not path.exists() or path.stat().st_size == 0:
        return None
    data = np.genfromtxt(path, names=True, delimiter=",", dtype=None, encoding=None)
    if data.shape == ():
        data = np.array([data], dtype=data.dtype)
    return data


def load_space_table(path: Path) -> np.ndarray | None:
    if not path.exists() or path.stat().st_size == 0:
        return None
    data = np.genfromtxt(path, names=True)
    if data.shape == ():
        data = np.array([data], dtype=data.dtype)
    return data


def node_component(mat: np.ndarray, node_id: int, dof: int) -> np.ndarray:
    col = 1 + (node_id - 1) * 3 + dof
    return mat[:, col]


def max_xz_norm(mat: np.ndarray) -> float:
    xyz = mat[:, 1:].reshape(mat.shape[0], N_NODES, 3)
    return float(np.max(np.linalg.norm(xyz[:, :, [0, 2]], axis=2)))


def summarize_case(run: Path) -> dict[str, float | int | str | None]:
    status = read_status(run)
    dyn = load_matrix(run / "Dynamic.out")
    vel = load_matrix(run / "Velocity.out")
    acc = load_matrix(run / "Accel.out")
    ten = load_csv(run / "element_strain_tension_summary_log.csv")
    force = load_space_table(run / "incremental_quasi_steady_aero_force_log.txt")

    summary: dict[str, float | int | str | None] = {
        "status": status.get("STATUS"),
        "message": status.get("MESSAGE"),
        "analysis_time_s": float(status["TIME"]) if "TIME" in status else None,
        "analyze_return_code": status.get("ANALYZE_RETURN_CODE"),
    }

    if dyn is not None:
        summary["time_end_displacement_s"] = float(dyn[-1, 0])
        summary["max_xz_displacement_m"] = max_xz_norm(dyn)
        for label, node_id in MONITOR_NODES.items():
            summary[f"{label}_max_abs_x_disp_m"] = float(np.max(np.abs(node_component(dyn, node_id, 0))))
            summary[f"{label}_max_abs_z_disp_m"] = float(np.max(np.abs(node_component(dyn, node_id, 2))))
    if vel is not None:
        summary["max_xz_velocity_mps"] = max_xz_norm(vel)
    if acc is not None:
        summary["max_xz_acceleration_mps2"] = max_xz_norm(acc)
    if ten is not None:
        min_tension = np.asarray(ten["min_estimated_tension_N"], dtype=float)
        max_abs_tension = np.asarray(ten["max_abs_tension_N"], dtype=float)
        max_abs_strain = np.asarray(ten["max_abs_strain"], dtype=float)
        ten_time = np.asarray(ten["time"], dtype=float)
        neg_mask = min_tension < 0.0
        summary["time_end_tension_log_s"] = float(ten_time[-1])
        summary["min_estimated_tension_N"] = float(np.min(min_tension))
        summary["min_estimated_tension_time_s"] = float(ten_time[int(np.argmin(min_tension))])
        summary["max_abs_tension_N"] = float(np.max(max_abs_tension))
        summary["max_abs_tension_time_s"] = float(ten_time[int(np.argmax(max_abs_tension))])
        summary["max_abs_strain"] = float(np.max(max_abs_strain))
        summary["negative_tension_logged_rows"] = int(np.sum(neg_mask))
        summary["first_negative_tension_time_s"] = float(ten_time[np.argmax(neg_mask)]) if np.any(neg_mask) else None
    if force is not None:
        summary["time_end_force_log_s"] = float(np.asarray(force["time"], dtype=float)[-1])
        summary["max_total_abs_delta_force_N"] = float(np.max(force["total_abs_delta_force"]))
        summary["max_abs_delta_force_N"] = float(np.max(force["max_abs_delta_force"]))
        summary["max_abs_alpha_current_deg"] = float(np.max(np.abs(force["max_alpha_current_deg"])))
        summary["max_clipped_count"] = int(np.max(force["clipped_count"]))
        summary["max_total_delta_power_W"] = float(np.max(force["total_delta_power"]))
        summary["min_total_delta_power_W"] = float(np.min(force["total_delta_power"]))
    return summary


def plot_tension() -> None:
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for label, run in CASES.items():
        ten = load_csv(run / "element_strain_tension_summary_log.csv")
        if ten is None:
            continue
        axes[0].plot(ten["time"], ten["min_estimated_tension_N"] / 1000.0, label=label)
        axes[1].plot(ten["time"], ten["max_abs_tension_N"] / 1000.0, label=label)
        axes[2].plot(ten["time"], ten["max_abs_strain"], label=label)
    axes[0].axhline(0, color="black", lw=0.8)
    axes[0].set_ylabel("min tension (kN)")
    axes[1].set_ylabel("max |tension| (kN)")
    axes[2].set_ylabel("max |strain|")
    axes[2].set_xlabel("time (s)")
    for ax in axes:
        ax.grid(True, alpha=0.25)
        ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "c4_200s_tension_strain_comparison.png", dpi=180)
    plt.close(fig)


def plot_monitor_displacement() -> None:
    fig, axes = plt.subplots(3, 2, figsize=(11, 8), sharex=True)
    for row, (point, node_id) in enumerate(MONITOR_NODES.items()):
        for label, run in CASES.items():
            dyn = load_matrix(run / "Dynamic.out")
            if dyn is None:
                continue
            axes[row, 0].plot(dyn[:, 0], node_component(dyn, node_id, 0), label=label, lw=1)
            axes[row, 1].plot(dyn[:, 0], node_component(dyn, node_id, 2), label=label, lw=1)
        axes[row, 0].set_ylabel(f"{point}\nx disp (m)")
        axes[row, 1].set_ylabel("z disp (m)")
        axes[row, 0].grid(True, alpha=0.25)
        axes[row, 1].grid(True, alpha=0.25)
    axes[0, 0].legend()
    axes[0, 1].legend()
    axes[-1, 0].set_xlabel("time (s)")
    axes[-1, 1].set_xlabel("time (s)")
    fig.tight_layout()
    fig.savefig(OUT / "c4_200s_monitor_displacement_comparison.png", dpi=180)
    plt.close(fig)


def plot_force_power() -> None:
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    for label, run in CASES.items():
        force = load_space_table(run / "incremental_quasi_steady_aero_force_log.txt")
        if force is None:
            continue
        axes[0].plot(force["time"], force["total_abs_delta_force"], label=label)
        axes[1].plot(force["time"], force["total_delta_power"], label=label)
        axes[2].plot(force["time"], force["max_alpha_current_deg"], label=label)
    axes[0].set_ylabel("total |Delta F| (N)")
    axes[1].set_ylabel("Delta F dot v (W)")
    axes[2].set_ylabel("max alpha (deg)")
    axes[2].set_xlabel("time (s)")
    for ax in axes:
        ax.grid(True, alpha=0.25)
        ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "c4_200s_incremental_force_power_comparison.png", dpi=180)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {label: summarize_case(run) for label, run in CASES.items()}
    (OUT / "c4_200s_structural_model_comparison_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    plot_tension()
    plot_monitor_displacement()
    plot_force_power()
    print(OUT / "c4_200s_structural_model_comparison_summary.json")
    print(OUT / "c4_200s_tension_strain_comparison.png")
    print(OUT / "c4_200s_monitor_displacement_comparison.png")
    print(OUT / "c4_200s_incremental_force_power_comparison.png")


if __name__ == "__main__":
    main()
