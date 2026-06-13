from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def load_csv(path: Path) -> np.ndarray:
    return np.genfromtxt(path, delimiter=",", names=True, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize a tension-only cable diagnostic run.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    run = Path(args.run_dir)
    out = Path(args.output_dir) if args.output_dir else run / "tension_only_summary"
    out.mkdir(parents=True, exist_ok=True)

    tension = load_csv(run / "element_strain_tension_summary_log.csv")
    force = np.genfromtxt(run / "incremental_quasi_steady_aero_force_log.txt", names=True, encoding="utf-8")

    min_tension_idx = int(np.argmin(tension["min_estimated_tension_N"]))
    max_tension_idx = int(np.argmax(tension["max_abs_tension_N"]))
    max_strain_idx = int(np.argmax(tension["max_abs_strain"]))
    slack_count_total = int(np.sum(tension["slack_element_count"]))

    after_69 = tension[tension["time"] >= 69.0]
    if after_69.size:
        min_after_69 = float(np.min(after_69["min_estimated_tension_N"]))
        max_after_69 = float(np.max(after_69["max_abs_tension_N"]))
        slack_after_69 = int(np.sum(after_69["slack_element_count"]))
    else:
        min_after_69 = float("nan")
        max_after_69 = float("nan")
        slack_after_69 = 0

    summary = {
        "time_end_s": float(np.max(tension["time"])),
        "min_estimated_tension_N": float(tension["min_estimated_tension_N"][min_tension_idx]),
        "min_estimated_tension_time_s": float(tension["time"][min_tension_idx]),
        "max_abs_tension_N": float(tension["max_abs_tension_N"][max_tension_idx]),
        "max_abs_tension_time_s": float(tension["time"][max_tension_idx]),
        "max_abs_strain": float(tension["max_abs_strain"][max_strain_idx]),
        "max_abs_strain_time_s": float(tension["time"][max_strain_idx]),
        "slack_log_count_total": slack_count_total,
        "min_estimated_tension_after_69s_N": min_after_69,
        "max_abs_tension_after_69s_N": max_after_69,
        "slack_log_count_after_69s": slack_after_69,
        "force_log_time_end_s": float(np.max(force["time"])),
        "max_total_abs_delta_force_N": float(np.max(force["total_abs_delta_force"])),
        "max_total_abs_delta_force_time_s": float(force["time"][int(np.argmax(force["total_abs_delta_force"]))]),
        "max_alpha_current_deg": float(np.max(force["max_alpha_current_deg"])),
        "max_alpha_current_time_s": float(force["time"][int(np.argmax(force["max_alpha_current_deg"]))]),
        "max_clipped_count": int(np.max(force["clipped_count"])),
    }

    (out / "tension_only_run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    fig, axes = plt.subplots(3, 1, figsize=(12, 9), dpi=170, sharex=True)
    axes[0].plot(tension["time"], tension["min_estimated_tension_N"] / 1000.0, lw=1.0, color="#2B6E4A")
    axes[0].axhline(0.0, color="#8B2E2E", lw=0.9, ls="--")
    axes[0].set_ylabel("min tension (kN)")
    axes[0].set_title("Tension-only cable diagnostic")
    axes[1].plot(tension["time"], tension["max_abs_tension_N"] / 1000.0, lw=1.0, color="#304E7A")
    axes[1].set_ylabel("max tension (kN)")
    axes[2].plot(tension["time"], tension["slack_element_count"], lw=1.0, color="#9A6A16")
    axes[2].set_ylabel("slack elements")
    axes[2].set_xlabel("time (s)")
    for ax in axes:
        ax.grid(True, alpha=0.25)
        ax.axvspan(69.0, 70.0, color="#B84A62", alpha=0.12)
    fig.tight_layout()
    fig.savefig(out / "tension_only_tension_slack_summary.png")
    plt.close(fig)

    fig, axes = plt.subplots(3, 1, figsize=(12, 9), dpi=170, sharex=True)
    axes[0].plot(force["time"], force["total_abs_delta_force"], lw=1.0, label="total |Delta F|", color="#B84A62")
    axes[0].plot(force["time"], force["F_current"], lw=0.9, label="F_current", color="#304E7A")
    axes[0].set_ylabel("force (N)")
    axes[0].legend(loc="best")
    axes[1].plot(force["time"], force["total_delta_power"], lw=1.0, color="#7A3F98")
    axes[1].axhline(0.0, color="#333333", lw=0.8)
    axes[1].set_ylabel("Delta F dot v (W)")
    axes[2].plot(force["time"], force["max_alpha_current_deg"], lw=1.0, color="#9A6A16")
    axes[2].set_ylabel("max alpha (deg)")
    axes[2].set_xlabel("time (s)")
    for ax in axes:
        ax.grid(True, alpha=0.25)
        ax.axvspan(69.0, 70.0, color="#B84A62", alpha=0.12)
    fig.tight_layout()
    fig.savefig(out / "tension_only_force_power_alpha_summary.png")
    plt.close(fig)

    print(out / "tension_only_run_summary.json")
    print(out / "tension_only_tension_slack_summary.png")
    print(out / "tension_only_force_power_alpha_summary.png")


if __name__ == "__main__":
    main()
