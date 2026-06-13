from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "output" / "diagnostics" / "typical_incremental_qs_mapping_fixed_power_strain"
RUN = CASE / "run"
OUT = CASE / "analysis" / "trigger_40_65"


def load_force_log() -> np.ndarray:
    return np.genfromtxt(RUN / "incremental_quasi_steady_aero_force_log.txt", names=True)


def load_summary_log() -> np.ndarray:
    return np.genfromtxt(RUN / "element_strain_tension_summary_log.csv", delimiter=",", names=True)


def load_node_power_subset(start: float = 40.0, end: float = 65.0) -> np.ndarray:
    path = RUN / "incremental_qs_node_power_log.csv"
    rows = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        header = f.readline().strip().split(",")
        for line in f:
            parts = line.strip().split(",")
            if len(parts) != len(header):
                continue
            t = float(parts[0])
            if start <= t <= end:
                rows.append([float(x) for x in parts])
    dtype = [(name, float) for name in header]
    arr = np.zeros(len(rows), dtype=dtype)
    for i, row in enumerate(rows):
        for name, value in zip(header, row):
            arr[name][i] = value
    return arr


def first_time(force: np.ndarray, field: str, threshold: float, above: bool = True) -> float | None:
    values = force[field]
    mask = values >= threshold if above else values <= threshold
    if not np.any(mask):
        return None
    return float(force["time"][np.argmax(mask)])


def window_stats(force: np.ndarray, strain: np.ndarray, node: np.ndarray) -> list[dict[str, float | list[float]]]:
    windows = [(40, 50), (50, 58), (58, 65), (65, 75), (75, min(float(force["time"][-1]), 96.0))]
    rows = []
    for start, end in windows:
        fm = (force["time"] >= start) & (force["time"] < end)
        sm = (strain["time"] >= start) & (strain["time"] < end)
        nm = (node["time"] >= start) & (node["time"] < end)
        if not np.any(fm):
            continue
        row = {
            "window_s": [start, end],
            "F_current_mean_N": float(np.mean(force["F_current"][fm])),
            "Delta_F_motion_mean_N": float(np.mean(force["Delta_F_motion"][fm])),
            "max_alpha_max_deg": float(np.max(force["max_alpha_current_deg"][fm])),
            "clipped_count_max": float(np.max(force["clipped_count"][fm])),
            "baseline_mismatch_mean_N": float(np.mean(force["baseline_mismatch_abs"][fm])),
            "baseline_mismatch_max_N": float(np.max(force["baseline_mismatch_abs"][fm])),
            "total_delta_power_mean_W": float(np.mean(force["total_delta_power"][fm])),
            "total_delta_power_positive_fraction": float(np.mean(force["total_delta_power"][fm] > 0.0)),
            "total_drag_power_mean_W": float(np.mean(force["total_drag_power"][fm])),
            "total_lift_power_mean_W": float(np.mean(force["total_lift_power"][fm])),
        }
        if np.any(sm):
            row["max_abs_strain"] = float(np.max(strain["max_abs_strain"][sm]))
            row["max_abs_tension_N"] = float(np.max(strain["max_abs_tension_N"][sm]))
        if np.any(nm):
            row["node_delta_power_mean_W"] = float(np.mean(node["delta_power"][nm]))
            row["node_delta_power_positive_fraction"] = float(np.mean(node["delta_power"][nm] > 0.0))
            row["node_baseline_mismatch_max_N"] = float(np.max(node["baseline_mismatch_abs"][nm]))
        rows.append(row)
    return rows


def make_plot(force: np.ndarray, strain: np.ndarray, path: Path) -> None:
    mask = (force["time"] >= 40) & (force["time"] <= 65)
    smask = (strain["time"] >= 40) & (strain["time"] <= 65)
    fig, axes = plt.subplots(5, 1, figsize=(11, 12), sharex=True)
    axes[0].plot(force["time"][mask], force["F_current"][mask], label="F_current", lw=1.0)
    axes[0].plot(force["time"][mask], force["Delta_F_motion"][mask], label="|Delta F| sum", lw=1.0)
    axes[0].set_ylabel("force (N)")
    axes[0].legend()
    axes[1].plot(force["time"][mask], force["max_alpha_current_deg"][mask], lw=1.0)
    axes[1].axhline(29.9, color="black", ls="--", lw=0.8)
    axes[1].set_ylabel("max alpha (deg)")
    axes[2].plot(force["time"][mask], force["total_delta_power"][mask], label="Delta F . v", lw=0.9)
    axes[2].plot(force["time"][mask], force["total_drag_power"][mask], label="drag power", lw=0.8)
    axes[2].plot(force["time"][mask], force["total_lift_power"][mask], label="lift power", lw=0.8)
    axes[2].axhline(0.0, color="black", lw=0.8)
    axes[2].set_ylabel("global power (W)")
    axes[2].legend()
    axes[3].plot(strain["time"][smask], strain["max_abs_strain"][smask], color="#8B2E2E", lw=1.0)
    axes[3].axhline(0.0029714372583237586, color="black", ls="--", lw=0.8, label="rated strain")
    axes[3].set_ylabel("max strain")
    axes[3].legend()
    axes[4].plot(force["time"][mask], force["baseline_mismatch_abs"][mask], lw=1.0)
    axes[4].set_ylabel("baseline mismatch (N)")
    axes[4].set_xlabel("time (s)")
    for ax in axes:
        ax.grid(True, color="#D8DEE8", lw=0.6)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    force = load_force_log()
    strain = load_summary_log()
    node = load_node_power_subset(40.0, 75.0)
    rows = window_stats(force, strain, node)
    events = {
        "last_force_log_time_s": float(force["time"][-1]),
        "first_alpha_over_table_s": first_time(force, "max_alpha_current_deg", 29.9),
        "first_delta_force_over_1500N_s": first_time(force, "Delta_F_motion", 1500.0),
        "first_delta_power_positive_over_10kW_s": first_time(force, "total_delta_power", 10000.0),
        "first_max_strain_over_rated_s": first_time(strain, "max_abs_strain", 0.0029714372583237586),
        "first_max_strain_over_0p002_s": first_time(strain, "max_abs_strain", 0.002),
        "baseline_mismatch_abs_max_N": float(np.max(force["baseline_mismatch_abs"])),
        "baseline_mismatch_abs_mean_N": float(np.mean(force["baseline_mismatch_abs"])),
    }
    result = {"events": events, "windows": rows}
    (OUT / "trigger_40_65_summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    make_plot(force, strain, OUT / "trigger_40_65_overview.png")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
