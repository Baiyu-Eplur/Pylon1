from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output" / "diagnostics" / "cable_rod_long_test" / "comparison" / "path_load_sensitivity_results"

CASES = {
    "baseline_dt0p05": ROOT
    / "output"
    / "diagnostics"
    / "cable_rod_long_test"
    / "calibrated_cable_rod_node_balance_72s_v2"
    / "run",
    "temporal_interp_dt0p025": ROOT
    / "output"
    / "diagnostics"
    / "cable_rod_long_test"
    / "path_load_sensitivity"
    / "temporal_interp_dt0p025_72s"
    / "run",
    "spatial_smooth5_dt0p05": ROOT
    / "output"
    / "diagnostics"
    / "cable_rod_long_test"
    / "path_load_sensitivity"
    / "spatial_smooth5_dt0p05_72s"
    / "run",
}


def add_metrics(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["acc_xz"] = np.sqrt(out["acc_y"].to_numpy() ** 2 + out["acc_z"].to_numpy() ** 2)
    out["inertial_xz"] = np.sqrt(out["inertial_y"].to_numpy() ** 2 + out["inertial_z"].to_numpy() ** 2)
    out["aero_current_xz"] = np.sqrt(out["aero_current_y"].to_numpy() ** 2 + out["aero_current_z"].to_numpy() ** 2)
    out["aero_delta_xz"] = np.sqrt(out["aero_delta_y"].to_numpy() ** 2 + out["aero_delta_z"].to_numpy() ** 2)
    out["internal_xz"] = np.sqrt(out["element_internal_y"].to_numpy() ** 2 + out["element_internal_z"].to_numpy() ** 2)
    out["left_internal_xz"] = np.sqrt(out["left_internal_y"].to_numpy() ** 2 + out["left_internal_z"].to_numpy() ** 2)
    out["right_internal_xz"] = np.sqrt(out["right_internal_y"].to_numpy() ** 2 + out["right_internal_z"].to_numpy() ** 2)
    return out


def read_status(run: Path) -> dict[str, str]:
    path = run / "analysis_status.txt"
    if not path.exists():
        return {}
    out = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            out[parts[0]] = parts[1]
    return out


def read_matrix(path: Path, nodes: int = 101) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    raw = np.loadtxt(path)
    time = raw[:, 0]
    data = raw[:, 1:].reshape(raw.shape[0], nodes, 3)
    return time, data[:, :, 1], data[:, :, 2]


def first_threshold(df: pd.DataFrame, col: str, threshold: float) -> dict[str, float | int | None]:
    hit = df[df[col] > threshold]
    if hit.empty:
        return {"time": None, "node": None, "value": None}
    row = hit.sort_values(["time", col], ascending=[True, False]).iloc[0]
    return {"time": float(row["time"]), "node": int(row["node"]), "value": float(row[col])}


def summarize_case(name: str, run: Path) -> tuple[dict[str, object], pd.DataFrame]:
    bal = add_metrics(pd.read_csv(run / "node_force_balance_log.csv"))
    status = read_status(run)
    dyn_t, uy, uz = read_matrix(run / "Dynamic.out")
    acc_t, ay, az = read_matrix(run / "Accel.out")
    disp_xz = np.sqrt(uy**2 + uz**2)
    acc_xz = np.sqrt(ay**2 + az**2)

    tension = pd.read_csv(run / "element_strain_tension_summary_log.csv")
    force = pd.read_csv(run / "incremental_quasi_steady_aero_force_log.txt", sep=r"\s+")

    onset = bal[(bal["time"] >= 68.0) & (bal["time"] <= 69.1)]
    node52 = bal[bal["node"] == 52]
    near_6825 = node52.iloc[(node52["time"] - 68.25).abs().argsort()[:1]].iloc[0]

    summary: dict[str, object] = {
        "case": name,
        "run_dir": str(run),
        "status": status,
        "max_disp_xz_m": float(np.nanmax(disp_xz)),
        "max_acc_xz_mps2": float(np.nanmax(acc_xz)),
        "first_acc_gt_50": first_threshold(bal, "acc_xz", 50.0),
        "first_acc_gt_100": first_threshold(bal, "acc_xz", 100.0),
        "first_acc_gt_200": first_threshold(bal, "acc_xz", 200.0),
        "onset_68_69p1_max_acc_xz": float(onset["acc_xz"].max()),
        "onset_68_69p1_max_internal_xz_N": float(onset["internal_xz"].max()),
        "onset_68_69p1_max_aero_current_xz_N": float(onset["aero_current_xz"].max()),
        "onset_68_69p1_max_aero_delta_xz_N": float(onset["aero_delta_xz"].max()),
        "onset_68_69p1_median_residual_xz_N": float(onset["residual_xz_norm"].median()),
        "node52_near_68p25": {
            "time": float(near_6825["time"]),
            "acc_xz": float(near_6825["acc_xz"]),
            "internal_xz_N": float(near_6825["internal_xz"]),
            "aero_current_xz_N": float(near_6825["aero_current_xz"]),
            "aero_delta_xz_N": float(near_6825["aero_delta_xz"]),
            "left_element": int(near_6825["left_element"]),
            "left_internal_xz_N": float(near_6825["left_internal_xz"]),
            "right_element": int(near_6825["right_element"]),
            "right_internal_xz_N": float(near_6825["right_internal_xz"]),
            "residual_xz_N": float(near_6825["residual_xz_norm"]),
        },
        "max_abs_strain": float(tension["max_abs_strain"].max()),
        "min_estimated_tension_N": float(tension["min_estimated_tension_N"].min()),
        "max_abs_tension_N": float(tension["max_abs_tension_N"].max()),
        "max_delta_force_motion_N": float(force["Delta_F_motion"].max()),
        "max_total_delta_power_W": float(force["total_delta_power"].max()),
        "max_alpha_current_deg": float(force["max_alpha_current_deg"].max()),
        "max_clipped_count": int(force["clipped_count"].max()),
    }

    focus = bal[(bal["node"].isin([45, 49, 50, 52, 55])) & (bal["time"].between(66.0, 70.0))].copy()
    focus["case"] = name
    return summary, focus


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries = []
    focus_frames = []
    for name, run in CASES.items():
        summary, focus = summarize_case(name, run)
        summaries.append(summary)
        focus_frames.append(focus)

    (OUT_DIR / "path_load_sensitivity_summary.json").write_text(
        json.dumps(summaries, indent=2), encoding="utf-8"
    )

    flat_rows = []
    for s in summaries:
        row = {
            "case": s["case"],
            "max_disp_xz_m": s["max_disp_xz_m"],
            "max_acc_xz_mps2": s["max_acc_xz_mps2"],
            "first_acc_gt_100_time": s["first_acc_gt_100"]["time"],
            "first_acc_gt_100_node": s["first_acc_gt_100"]["node"],
            "onset_68_69p1_max_acc_xz": s["onset_68_69p1_max_acc_xz"],
            "onset_68_69p1_max_internal_xz_N": s["onset_68_69p1_max_internal_xz_N"],
            "onset_68_69p1_max_aero_current_xz_N": s["onset_68_69p1_max_aero_current_xz_N"],
            "node52_68p25_acc_xz": s["node52_near_68p25"]["acc_xz"],
            "node52_68p25_internal_xz_N": s["node52_near_68p25"]["internal_xz_N"],
            "node52_68p25_aero_current_xz_N": s["node52_near_68p25"]["aero_current_xz_N"],
            "max_delta_force_motion_N": s["max_delta_force_motion_N"],
            "max_total_delta_power_W": s["max_total_delta_power_W"],
            "max_alpha_current_deg": s["max_alpha_current_deg"],
            "max_clipped_count": s["max_clipped_count"],
        }
        flat_rows.append(row)
    flat = pd.DataFrame(flat_rows)
    flat.to_csv(OUT_DIR / "path_load_sensitivity_summary.csv", index=False)

    focus_all = pd.concat(focus_frames, ignore_index=True)
    focus_all.to_csv(OUT_DIR / "focus_nodes_66_70s_force_balance.csv", index=False)

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    for name in CASES:
        data = focus_all[(focus_all["case"] == name) & (focus_all["node"] == 52)]
        axes[0].plot(data["time"], data["acc_xz"], label=name)
        axes[1].plot(data["time"], data["internal_xz"], label=name)
        axes[2].plot(data["time"], data["aero_current_xz"], label=name)
    axes[0].set_ylabel("node 52 acc x-z (m/s2)")
    axes[1].set_ylabel("node 52 internal x-z (N)")
    axes[2].set_ylabel("node 52 aero x-z (N)")
    axes[2].set_xlabel("time (s)")
    for ax in axes:
        ax.axvspan(68.0, 69.1, color="tab:red", alpha=0.10)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        ax.set_xlim(66.0, 70.0)
    fig.suptitle("Sensitivity comparison at node 52")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "node52_sensitivity_comparison.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 5))
    x = np.arange(len(flat))
    width = 0.24
    ax.bar(x - width, flat["onset_68_69p1_max_internal_xz_N"], width=width, label="max internal resultant")
    ax.bar(x, flat["onset_68_69p1_max_aero_current_xz_N"], width=width, label="max aero current")
    ax.bar(x + width, flat["onset_68_69p1_max_acc_xz"], width=width, label="max acc x-z")
    ax.set_xticks(x)
    ax.set_xticklabels(flat["case"], rotation=12, ha="right")
    ax.set_yscale("log")
    ax.set_ylabel("68-69.1 s window metric (log scale)")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "onset_window_sensitivity_bars.png", dpi=200)
    plt.close(fig)

    print(flat.to_string(index=False))
    print(f"Wrote sensitivity comparison to {OUT_DIR}")


if __name__ == "__main__":
    main()
