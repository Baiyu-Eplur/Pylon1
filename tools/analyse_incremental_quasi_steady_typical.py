from __future__ import annotations

import json
import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "output" / "diagnostics" / "typical_incremental_quasi_steady_no_stop"
RUN = CASE / "run"
OUT = CASE / "analysis"
OLD_EXPLICIT = ROOT / "output" / "diagnostics" / "typical_explicit_no_stop" / "run"
FULL_QS = ROOT / "output" / "diagnostics" / "typical_quasi_steady_no_stop" / "run"


def load_table(path: Path, ncols: int | None = None) -> np.ndarray:
    if not path.exists() or path.stat().st_size == 0:
        return np.empty((0, ncols or 0))
    rows: list[list[float]] = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            if ncols is not None and len(parts) < ncols:
                continue
            try:
                values = [float(x) for x in parts[: ncols or len(parts)]]
            except ValueError:
                continue
            rows.append(values)
    if not rows:
        return np.empty((0, ncols or 0))
    return np.asarray(rows, dtype=float)


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.edgecolor": "#AAB2BF",
            "axes.labelcolor": "#222831",
            "xtick.color": "#222831",
            "ytick.color": "#222831",
            "grid.color": "#D8DEE8",
            "grid.linewidth": 0.65,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def save_force_decomposition(data: np.ndarray, path: Path) -> None:
    t = data[:, 0]
    labels = [
        ("F_original", data[:, 1], "#2E6FBB"),
        ("F_reference", data[:, 2], "#8C6BB1"),
        ("F_current", data[:, 3], "#C46A2B"),
        ("Delta_F_motion", data[:, 4], "#27856A"),
        ("total_abs_delta_force", data[:, 5], "#B84A62"),
    ]
    fig, axes = plt.subplots(2, 1, figsize=(11.5, 7.2), sharex=True)
    for label, y, color in labels:
        axes[0].plot(t, y, lw=1.15, label=label, color=color)
    axes[0].set_ylabel("Total absolute force (N)")
    axes[0].set_title("Incremental quasi-steady aerodynamic force decomposition", weight="bold")
    axes[0].grid(True)
    axes[0].legend(ncol=3, fontsize=8)

    for label, y, color in labels:
        axes[1].plot(t, y, lw=1.0, label=label, color=color)
    axes[1].set_yscale("symlog", linthresh=1.0)
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Force (N, symlog)")
    axes[1].grid(True, which="both")
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)


def save_ratio_plot(data: np.ndarray, path: Path) -> None:
    t = data[:, 0]
    f_original = np.maximum(np.abs(data[:, 1]), 1.0e-12)
    ratio_current = data[:, 3] / f_original
    ratio_delta = data[:, 5] / f_original
    max_delta = data[:, 6]
    fig, axes = plt.subplots(2, 1, figsize=(11.5, 6.8), sharex=True)
    axes[0].plot(t, ratio_current, lw=1.1, label="F_current / F_original", color="#C46A2B")
    axes[0].plot(t, ratio_delta, lw=1.1, label="total_abs_delta_force / F_original", color="#B84A62")
    axes[0].axhline(1.0, color="#444444", lw=0.8, ls="--")
    axes[0].set_ylabel("Force ratio")
    axes[0].set_title("Motion-correction size relative to original force", weight="bold")
    axes[0].grid(True)
    axes[0].legend(fontsize=8)
    axes[1].plot(t, max_delta, lw=1.0, color="#27856A")
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Max element delta force (N)")
    axes[1].grid(True)
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)


def save_branch_comparison(data: np.ndarray, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    ax.plot(data[:, 0], data[:, 5], lw=1.05, label="incremental: total_abs_delta_force", color="#B84A62")
    old = load_table(OLD_EXPLICIT / "explicit_aero_damping_force_log.txt", 4)
    if old.size:
        ax.plot(old[:, 0], old[:, 1], lw=0.95, label="old explicit equivalent damping: total_abs_force", color="#2E6FBB", alpha=0.85)
    qs = load_table(FULL_QS / "quasi_steady_aero_force_log.txt", 7)
    if qs.size:
        ax.plot(qs[:, 0], qs[:, 1], lw=0.95, label="full quasi-steady replacement: total_abs_force", color="#27856A", alpha=0.85)
    ax.set_yscale("symlog", linthresh=1.0)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Force diagnostic (N, symlog)")
    ax.set_title("Aerodynamic-force branch comparison", weight="bold")
    ax.grid(True, which="both")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)


def summarize(data: np.ndarray) -> dict[str, float | int]:
    names = [
        "time_s",
        "F_original",
        "F_reference",
        "F_current",
        "Delta_F_motion",
        "total_abs_delta_force",
        "max_abs_delta_force",
        "scale",
        "max_alpha_reference_deg",
        "max_alpha_current_deg",
        "clipped_count",
        "node_count",
        "total_delta_power",
        "total_current_power",
        "total_drag_power",
        "total_lift_power",
        "baseline_mismatch_abs",
        "max_baseline_mismatch_abs",
    ]
    summary: dict[str, float | int] = {
        "records": int(data.shape[0]),
        "last_time_s": float(data[-1, 0]),
    }
    for idx, name in enumerate(names[1 : min(len(names), data.shape[1])], start=1):
        summary[f"{name}_min"] = float(np.nanmin(data[:, idx]))
        summary[f"{name}_max"] = float(np.nanmax(data[:, idx]))
        summary[f"{name}_mean"] = float(np.nanmean(data[:, idx]))
    summary["max_delta_over_original"] = float(
        np.nanmax(data[:, 5] / np.maximum(np.abs(data[:, 1]), 1.0e-12))
    )
    summary["final_delta_over_original"] = float(data[-1, 5] / max(abs(data[-1, 1]), 1.0e-12))
    summary["current_angle_clipped_fraction"] = float(np.nanmean(data[:, 10] > 0.0))
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyse incremental quasi-steady force diagnostics.")
    parser.add_argument("--case-dir", default=str(CASE), help="Case directory containing run/")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    case = Path(args.case_dir)
    run = case / "run"
    out = case / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    configure_style()
    data = load_table(run / "incremental_quasi_steady_aero_force_log.txt")
    if data.size == 0:
        raise SystemExit("No incremental_quasi_steady_aero_force_log.txt rows found.")

    save_force_decomposition(data, out / "incremental_force_decomposition.png")
    save_ratio_plot(data, out / "incremental_motion_correction_ratio.png")
    save_branch_comparison(data, out / "aero_force_branch_comparison.png")

    summary = summarize(data)
    (out / "incremental_force_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# Incremental Quasi-Steady Typical Diagnostic",
        "",
        f"- Records in incremental force log: `{summary['records']}`",
        f"- Last recorded time: `{summary['last_time_s']:.6f} s`",
        f"- F_original range: `{summary['F_original_min']:.6g}` to `{summary['F_original_max']:.6g}` N",
        f"- F_reference range: `{summary['F_reference_min']:.6g}` to `{summary['F_reference_max']:.6g}` N",
        f"- F_current range: `{summary['F_current_min']:.6g}` to `{summary['F_current_max']:.6g}` N",
        f"- total_abs_delta_force range: `{summary['total_abs_delta_force_min']:.6g}` to `{summary['total_abs_delta_force_max']:.6g}` N",
        f"- Max total_abs_delta_force / F_original: `{summary['max_delta_over_original']:.6g}`",
        f"- Final total_abs_delta_force / F_original: `{summary['final_delta_over_original']:.6g}`",
        f"- Current-angle clipped row fraction: `{summary['current_angle_clipped_fraction']:.3f}`",
        "",
        "## Interpretation",
        "",
        "- In this branch the original Path wind loads remain active. The Tcl branch applies only `F_current - F_reference`.",
        "- `F_original` is the nodal absolute total of the original force files after the OpenSees `1000` factor.",
        "- `F_reference`, `F_current`, and `total_abs_delta_force` are element-integrated quasi-steady absolute totals.",
        "- If `total_abs_delta_force` remains comparable to or smaller than `F_original`, the motion correction is physically moderate. If it rapidly exceeds `F_original` by orders of magnitude, the force feedback is likely over-injecting energy.",
        "",
        "## Figures",
        "",
        "- `incremental_force_decomposition.png`",
        "- `incremental_motion_correction_ratio.png`",
        "- `aero_force_branch_comparison.png`",
    ]
    (out / "incremental_force_diagnostic_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out / "incremental_force_diagnostic_report.md")


if __name__ == "__main__":
    main()
