from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = ROOT / "output" / "diagnostics" / "cable_rod_long_test"
CASES = {
    "current_tension_only": OUT_ROOT / "current_tension_only" / "run",
    "calibrated_cable_rod": OUT_ROOT / "calibrated_cable_rod" / "run",
    "regularized_tension_only": OUT_ROOT / "regularized_tension_only" / "run",
}
OUT = OUT_ROOT / "comparison"
N_NODES = 101


def read_status(run: Path) -> dict[str, str]:
    path = run / "analysis_status.txt"
    if not path.exists():
        return {"STATUS": "missing", "MESSAGE": "external_timeout_or_missing_status"}
    values: dict[str, str] = {}
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
    data = np.genfromtxt(path, names=True, delimiter=",", encoding=None)
    if data.shape == ():
        data = np.array([data], dtype=data.dtype)
    return data


def load_space(path: Path) -> np.ndarray | None:
    if not path.exists() or path.stat().st_size == 0:
        return None
    data = np.genfromtxt(path, names=True)
    if data.shape == ():
        data = np.array([data], dtype=data.dtype)
    return data


def first_time(time: np.ndarray, mask: np.ndarray) -> float | None:
    idx = np.flatnonzero(mask)
    if idx.size == 0:
        return None
    return float(time[int(idx[0])])


def xz_max(mat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    time = mat[:, 0]
    xyz = mat[:, 1:].reshape(mat.shape[0], N_NODES, 3)
    mag = np.linalg.norm(xyz[:, :, [0, 2]], axis=2)
    return time, np.max(mag, axis=1)


def summarize_case(run: Path) -> dict:
    status = read_status(run)
    summary: dict = {"status": status, "events": {}, "peaks": {}}
    dyn = load_matrix(run / "Dynamic.out")
    vel = load_matrix(run / "Velocity.out")
    acc = load_matrix(run / "Accel.out")
    ten = load_csv(run / "element_strain_tension_summary_log.csv")
    force = load_space(run / "incremental_quasi_steady_aero_force_log.txt")
    power = load_csv(run / "incremental_qs_node_power_log.csv")

    if dyn is not None:
        t, y = xz_max(dyn)
        summary["peaks"]["max_disp_m"] = float(np.max(y))
        summary["peaks"]["max_disp_time_s"] = float(t[int(np.argmax(y))])
        summary["events"]["disp_0p5m"] = first_time(t, y >= 0.5)
        summary["events"]["disp_1m"] = first_time(t, y >= 1.0)
        summary["events"]["disp_2m"] = first_time(t, y >= 2.0)
        summary["time_end_displacement_s"] = float(t[-1])
    if vel is not None:
        t, y = xz_max(vel)
        summary["peaks"]["max_vel_mps"] = float(np.max(y))
        summary["peaks"]["max_vel_time_s"] = float(t[int(np.argmax(y))])
        summary["events"]["vel_1mps"] = first_time(t, y >= 1.0)
        summary["events"]["vel_5mps"] = first_time(t, y >= 5.0)
    if acc is not None:
        t, y = xz_max(acc)
        summary["peaks"]["max_acc_mps2"] = float(np.max(y))
        summary["peaks"]["max_acc_time_s"] = float(t[int(np.argmax(y))])
        summary["events"]["acc_100mps2"] = first_time(t, y >= 100.0)
    if ten is not None:
        t = np.asarray(ten["time"], dtype=float)
        min_tension = np.asarray(ten["min_estimated_tension_N"], dtype=float)
        max_tension = np.asarray(ten["max_abs_tension_N"], dtype=float)
        strain = np.asarray(ten["max_abs_strain"], dtype=float)
        slack = np.asarray(ten["slack_element_count"], dtype=float)
        summary["time_end_tension_log_s"] = float(t[-1])
        summary["peaks"]["min_tension_N"] = float(np.min(min_tension))
        summary["peaks"]["min_tension_time_s"] = float(t[int(np.argmin(min_tension))])
        summary["peaks"]["max_abs_tension_N"] = float(np.max(max_tension))
        summary["peaks"]["max_abs_tension_time_s"] = float(t[int(np.argmax(max_tension))])
        summary["peaks"]["max_abs_strain"] = float(np.max(strain))
        summary["peaks"]["max_abs_strain_time_s"] = float(t[int(np.argmax(strain))])
        summary["peaks"]["max_slack_count"] = int(np.max(slack))
        summary["events"]["negative_tension"] = first_time(t, min_tension < 0.0)
        summary["events"]["low_tension_1kN"] = first_time(t, min_tension <= 1000.0)
        summary["events"]["slack_count_gt0"] = first_time(t, slack > 0.0)
        summary["events"]["strain_0p001"] = first_time(t, strain >= 1.0e-3)
        summary["events"]["strain_0p01"] = first_time(t, strain >= 1.0e-2)
        summary["events"]["tension_abs_100kN"] = first_time(t, max_tension >= 100.0e3)
        summary["events"]["tension_abs_500kN"] = first_time(t, max_tension >= 500.0e3)
    if force is not None:
        t = np.asarray(force["time"], dtype=float)
        total_delta = np.asarray(force["total_abs_delta_force"], dtype=float)
        alpha = np.abs(np.asarray(force["max_alpha_current_deg"], dtype=float))
        clipped = np.asarray(force["clipped_count"], dtype=float)
        delta_power = np.asarray(force["total_delta_power"], dtype=float)
        summary["time_end_force_log_s"] = float(t[-1])
        summary["peaks"]["max_total_abs_delta_force_N"] = float(np.max(total_delta))
        summary["peaks"]["max_total_abs_delta_force_time_s"] = float(t[int(np.argmax(total_delta))])
        summary["peaks"]["max_abs_alpha_deg"] = float(np.max(alpha))
        summary["peaks"]["max_abs_alpha_time_s"] = float(t[int(np.argmax(alpha))])
        summary["peaks"]["max_clipped_count"] = int(np.max(clipped))
        summary["peaks"]["max_total_delta_power_W"] = float(np.max(delta_power))
        summary["peaks"]["min_total_delta_power_W"] = float(np.min(delta_power))
        summary["events"]["delta_force_500N"] = first_time(t, total_delta >= 500.0)
        summary["events"]["delta_force_1000N"] = first_time(t, total_delta >= 1000.0)
        summary["events"]["alpha_30deg"] = first_time(t, alpha >= 30.0)
        summary["events"]["alpha_60deg"] = first_time(t, alpha >= 60.0)
        summary["events"]["alpha_clipping"] = first_time(t, clipped > 0.0)
        summary["events"]["delta_power_abs_1000W"] = first_time(t, np.abs(delta_power) >= 1000.0)
        summary["events"]["delta_power_abs_10000W"] = first_time(t, np.abs(delta_power) >= 10000.0)
    if power is not None:
        t = np.asarray(power["time"], dtype=float)
        p = np.asarray(power["delta_power"], dtype=float)
        unique_t = np.unique(t)
        max_abs = np.array([np.max(np.abs(p[t == time])) for time in unique_t])
        summary["peaks"]["max_abs_node_delta_power_W"] = float(np.max(max_abs))
        summary["peaks"]["max_abs_node_delta_power_time_s"] = float(unique_t[int(np.argmax(max_abs))])
        summary["events"]["node_delta_power_abs_100W"] = first_time(unique_t, max_abs >= 100.0)
        summary["events"]["node_delta_power_abs_1000W"] = first_time(unique_t, max_abs >= 1000.0)

    ordered = [(k, v) for k, v in summary["events"].items() if v is not None]
    ordered.sort(key=lambda item: item[1])
    summary["ordered_events"] = ordered
    return summary


def plot_summary(summary: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(4, 1, figsize=(11, 10), sharex=True)
    for label, run in CASES.items():
        dyn = load_matrix(run / "Dynamic.out")
        ten = load_csv(run / "element_strain_tension_summary_log.csv")
        force = load_space(run / "incremental_quasi_steady_aero_force_log.txt")
        if dyn is not None:
            t, y = xz_max(dyn)
            axes[0].plot(t, y, label=label)
        if ten is not None:
            axes[1].plot(ten["time"], ten["min_estimated_tension_N"] / 1000.0, label=label)
            axes[2].plot(ten["time"], ten["max_abs_strain"], label=label)
        if force is not None:
            axes[3].plot(force["time"], force["max_alpha_current_deg"], label=label)
    axes[0].set_ylabel("max disp (m)")
    axes[1].set_ylabel("min tension (kN)")
    axes[1].axhline(0, color="black", lw=0.8)
    axes[2].set_ylabel("max strain")
    axes[3].set_ylabel("max alpha (deg)")
    axes[3].set_xlabel("time (s)")
    for ax in axes:
        ax.grid(True, alpha=0.25)
        ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "cable_rod_long_test_core_comparison.png", dpi=180)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {label: summarize_case(run) for label, run in CASES.items()}
    (OUT / "cable_rod_long_test_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    for label, item in summary.items():
        lines = [f"# {label}", "", "## Status", "```json", json.dumps(item["status"], indent=2), "```", "", "## Ordered events"]
        for event, t in item.get("ordered_events", []):
            lines.append(f"- {event}: {t:.6f} s")
        (OUT / f"{label}_events.md").write_text("\n".join(lines), encoding="utf-8")
    plot_summary(summary)
    print(OUT / "cable_rod_long_test_summary.json")
    print(OUT / "cable_rod_long_test_core_comparison.png")


if __name__ == "__main__":
    main()
