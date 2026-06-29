from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "output" / "diagnostics" / "cable_rod_long_test" / "calibrated_cable_rod_node_balance_72s_v2" / "run"
OUT_DIR = ROOT / "output" / "diagnostics" / "cable_rod_long_test" / "comparison" / "node_force_balance_72s_v2"


def norm(df: pd.DataFrame, y: str, z: str) -> pd.Series:
    return np.sqrt(df[y].to_numpy() ** 2 + df[z].to_numpy() ** 2)


def nearest_rows(df: pd.DataFrame, times: list[float], nodes: list[int]) -> pd.DataFrame:
    rows = []
    for target_time, node in zip(times, nodes):
        node_df = df[df["node"] == node].copy()
        idx = (node_df["time"] - target_time).abs().idxmin()
        rows.append(node_df.loc[idx])
    return pd.DataFrame(rows)


def add_force_metrics(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["acc_xz"] = norm(out, "acc_y", "acc_z")
    out["inertial_xz"] = norm(out, "inertial_y", "inertial_z")
    out["damping_xz"] = norm(out, "damping_resist_y", "damping_resist_z")
    out["gravity_xz"] = out["gravity_z"].abs()
    out["aero_ref_xz"] = norm(out, "aero_ref_y", "aero_ref_z")
    out["aero_delta_xz"] = norm(out, "aero_delta_y", "aero_delta_z")
    out["aero_current_xz"] = norm(out, "aero_current_y", "aero_current_z")
    out["element_internal_xz"] = norm(out, "element_internal_y", "element_internal_z")
    out["left_internal_xz"] = norm(out, "left_internal_y", "left_internal_z")
    out["right_internal_xz"] = norm(out, "right_internal_y", "right_internal_z")
    return out


def top_contributors(row: pd.Series) -> list[dict[str, float | str]]:
    items = [
        ("left_element_internal", float(row["left_internal_xz"])),
        ("right_element_internal", float(row["right_internal_xz"])),
        ("aero_current", float(row["aero_current_xz"])),
        ("aero_motion_delta", float(row["aero_delta_xz"])),
        ("gravity", float(row["gravity_xz"])),
        ("rayleigh_damping", float(row["damping_xz"])),
    ]
    return [
        {"component": name, "xz_norm_N": value}
        for name, value in sorted(items, key=lambda item: item[1], reverse=True)
    ]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    balance_path = RUN_DIR / "node_force_balance_log.csv"
    balance = pd.read_csv(balance_path)
    balance = add_force_metrics(balance)

    time_window = balance[(balance["time"] >= 60.0) & (balance["time"] <= 72.0)].copy()

    threshold_rows = {}
    for threshold in (50.0, 100.0, 200.0, 500.0, 1000.0):
        candidates = time_window[time_window["acc_xz"] > threshold]
        if len(candidates):
            row = candidates.sort_values(["time", "acc_xz"], ascending=[True, False]).iloc[0]
            threshold_rows[str(int(threshold))] = row.to_dict()

    focus_times = [63.1, 68.25, 68.8, 69.0333333333, 69.51895, 69.75]
    focus_nodes = [55, 52, 55, 50, 45, 49]
    focus = add_force_metrics(nearest_rows(balance, focus_times, focus_nodes))
    focus["contributors_ranked"] = focus.apply(top_contributors, axis=1)

    # Track node 52, where the first >100 m/s^2 acceleration was observed.
    node52 = time_window[time_window["node"] == 52].copy()
    sample_times = np.arange(66.0, 69.55, 0.25)
    sample_indices = [(node52["time"] - target).abs().idxmin() for target in sample_times]
    node52_samples = node52.loc[sample_indices].drop_duplicates(subset=["time"]).copy()

    # Find the largest internal-force jumps between adjacent records at each node.
    time_window = time_window.sort_values(["node", "time"])
    for col in ("element_internal_y", "element_internal_z", "aero_current_y", "aero_current_z", "acc_y", "acc_z"):
        time_window[f"d_{col}"] = time_window.groupby("node")[col].diff()
    time_window["d_internal_xz"] = np.sqrt(
        time_window["d_element_internal_y"].fillna(0).to_numpy() ** 2
        + time_window["d_element_internal_z"].fillna(0).to_numpy() ** 2
    )
    time_window["d_aero_xz"] = np.sqrt(
        time_window["d_aero_current_y"].fillna(0).to_numpy() ** 2
        + time_window["d_aero_current_z"].fillna(0).to_numpy() ** 2
    )
    top_internal_jumps = (
        time_window[(time_window["time"] >= 67.5) & (time_window["time"] <= 69.2)]
        .sort_values("d_internal_xz", ascending=False)
        .head(20)
    )

    summary = {
        "run_dir": str(RUN_DIR),
        "balance_rows": int(len(balance)),
        "time_min": float(balance["time"].min()),
        "time_max": float(balance["time"].max()),
        "threshold_first_rows": threshold_rows,
        "note": (
            "The OpenSees element force sign convention was not re-calibrated here; "
            "component magnitudes and adjacent element attribution are the primary diagnostic outputs."
        ),
    }
    (OUT_DIR / "node_force_balance_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    focus_cols = [
        "time",
        "node",
        "acc_y",
        "acc_z",
        "acc_xz",
        "inertial_y",
        "inertial_z",
        "inertial_xz",
        "aero_current_y",
        "aero_current_z",
        "aero_current_xz",
        "aero_delta_y",
        "aero_delta_z",
        "aero_delta_xz",
        "damping_resist_y",
        "damping_resist_z",
        "damping_xz",
        "left_element",
        "left_internal_y",
        "left_internal_z",
        "left_internal_xz",
        "right_element",
        "right_internal_y",
        "right_internal_z",
        "right_internal_xz",
        "element_internal_y",
        "element_internal_z",
        "element_internal_xz",
        "residual_y",
        "residual_z",
        "residual_xz_norm",
        "contributors_ranked",
    ]
    focus[focus_cols].to_csv(OUT_DIR / "focus_force_balance_events.csv", index=False)

    node52_cols = [
        "time",
        "acc_y",
        "acc_z",
        "acc_xz",
        "inertial_y",
        "inertial_z",
        "aero_current_y",
        "aero_current_z",
        "aero_delta_y",
        "aero_delta_z",
        "left_element",
        "left_internal_y",
        "left_internal_z",
        "right_element",
        "right_internal_y",
        "right_internal_z",
        "residual_y",
        "residual_z",
    ]
    node52_samples[node52_cols].to_csv(OUT_DIR / "node52_66_69p5s_samples.csv", index=False)

    jump_cols = [
        "time",
        "node",
        "acc_xz",
        "d_internal_xz",
        "d_aero_xz",
        "left_element",
        "right_element",
        "left_internal_y",
        "left_internal_z",
        "right_internal_y",
        "right_internal_z",
        "aero_current_y",
        "aero_current_z",
    ]
    top_internal_jumps[jump_cols].to_csv(OUT_DIR / "top_internal_force_jumps_67p5_69p2s.csv", index=False)

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(node52["time"], node52["inertial_xz"], label="inertial |m a|")
    ax.plot(node52["time"], node52["element_internal_xz"], label="element internal resultant")
    ax.plot(node52["time"], node52["aero_current_xz"], label="node aero current")
    ax.plot(node52["time"], node52["aero_delta_xz"], label="node aero motion delta")
    ax.plot(node52["time"], node52["damping_xz"], label="Rayleigh damping")
    ax.axvline(68.25, color="k", linestyle="--", linewidth=1, label="first >100 m/s2")
    ax.set_xlim(66.0, 69.5)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("force norm in y-z plane (N)")
    ax.set_title("Node 52 force-balance components")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "node52_force_balance_66_69p5s.png", dpi=200)
    plt.close(fig)

    event_plot = focus.copy()
    event_plot["event"] = event_plot.apply(lambda row: f"t={row['time']:.3f}s\nnode {int(row['node'])}", axis=1)
    components = [
        ("inertial_xz", "inertial"),
        ("element_internal_xz", "internal"),
        ("aero_current_xz", "aero current"),
        ("aero_delta_xz", "aero delta"),
        ("damping_xz", "damping"),
    ]
    x = np.arange(len(event_plot))
    width = 0.16
    fig, ax = plt.subplots(figsize=(12, 6))
    for idx, (col, label) in enumerate(components):
        ax.bar(x + (idx - 2) * width, event_plot[col].to_numpy(), width=width, label=label)
    ax.set_yscale("log")
    ax.set_ylabel("force norm in y-z plane (N, log scale)")
    ax.set_xticks(x)
    ax.set_xticklabels(event_plot["event"], rotation=0)
    ax.set_title("Force-balance component magnitude at key acceleration events")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "key_event_force_component_bars.png", dpi=200)
    plt.close(fig)

    print(f"Wrote node force-balance diagnostics to {OUT_DIR}")
    print(f"First threshold events: {list(threshold_rows.keys())}")
    print(focus[["time", "node", "acc_xz", "inertial_xz", "aero_current_xz", "aero_delta_xz", "left_internal_xz", "right_internal_xz", "residual_xz_norm"]])


if __name__ == "__main__":
    main()
