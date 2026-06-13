from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "output" / "diagnostics" / "typical_incremental_qs_mapping_fixed_power_strain"
RUN = CASE / "run"
OUT = CASE / "analysis" / "onset_root_cause_69s"

START = 68.5
END = 70.2
SNAPSHOTS = [69.45, 69.50, 69.55, 69.60, 69.65, 69.70, 69.75]
RATED_STRAIN = 0.0029714372583237586


def load_force() -> np.ndarray:
    return np.genfromtxt(RUN / "incremental_quasi_steady_aero_force_log.txt", names=True)


def load_strain_summary() -> np.ndarray:
    return np.genfromtxt(RUN / "element_strain_tension_summary_log.csv", delimiter=",", names=True)


def nearest_time(values: np.ndarray, target: float) -> float:
    return float(values[np.argmin(np.abs(values - target))])


def subset_node_power(start: float, end: float) -> tuple[list[str], list[dict[str, float]]]:
    path = RUN / "incremental_qs_node_power_log.csv"
    rows: list[dict[str, float]] = []
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        for row in reader:
            t = float(row["time"])
            if start <= t <= end:
                rows.append({k: float(v) for k, v in row.items()})
            elif t > end and rows:
                break
    return fieldnames, rows


def subset_element_log(start: float, end: float) -> tuple[list[str], list[dict[str, float]]]:
    path = RUN / "element_strain_tension_log.csv"
    rows: list[dict[str, float]] = []
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        for row in reader:
            t = float(row["time"])
            if start <= t <= end:
                rows.append({k: float(v) for k, v in row.items()})
            elif t > end and rows:
                break
    return fieldnames, rows


def load_matrix(path: Path) -> np.ndarray:
    data = np.loadtxt(path)
    return data[np.newaxis, :] if data.ndim == 1 else data


def node_cols(node_id: int) -> tuple[int, int, int]:
    start = 1 + (node_id - 1) * 3
    return start, start + 1, start + 2


def state_at_nodes(time_target: float, node_ids: list[int]) -> dict[int, dict[str, float]]:
    dyn = load_matrix(RUN / "Dynamic.out")
    vel = load_matrix(RUN / "Velocity.out")
    accel = load_matrix(RUN / "Accel.out")
    idx = int(np.argmin(np.abs(dyn[:, 0] - time_target)))
    out: dict[int, dict[str, float]] = {}
    for node in node_ids:
        c1, c2, c3 = node_cols(node)
        out[node] = {
            "time": float(dyn[idx, 0]),
            "disp_dof1": float(dyn[idx, c1]),
            "disp_dof2": float(dyn[idx, c2]),
            "disp_dof3": float(dyn[idx, c3]),
            "vel_dof1": float(vel[idx, c1]),
            "vel_dof2": float(vel[idx, c2]),
            "vel_dof3": float(vel[idx, c3]),
            "accel_dof1": float(accel[idx, c1]),
            "accel_dof2": float(accel[idx, c2]),
            "accel_dof3": float(accel[idx, c3]),
        }
    return out


def first_force_events(force: np.ndarray, strain: np.ndarray) -> dict[str, float | None]:
    def first(field: str, threshold: float) -> float | None:
        mask = force[field] >= threshold
        return float(force["time"][np.argmax(mask)]) if np.any(mask) else None

    def first_s(field: str, threshold: float) -> float | None:
        mask = strain[field] >= threshold
        return float(strain["time"][np.argmax(mask)]) if np.any(mask) else None

    return {
        "alpha_over_table": first("max_alpha_current_deg", 29.9),
        "clipped_count_positive": first("clipped_count", 1.0),
        "Delta_F_over_1000N": first("Delta_F_motion", 1000.0),
        "Delta_F_over_1500N": first("Delta_F_motion", 1500.0),
        "total_delta_power_positive": first("total_delta_power", 0.0),
        "total_delta_power_over_10kW": first("total_delta_power", 10000.0),
        "strain_over_0p001": first_s("max_abs_strain", 0.001),
        "strain_over_0p002": first_s("max_abs_strain", 0.002),
        "strain_over_rated": first_s("max_abs_strain", RATED_STRAIN),
    }


def summarize_by_time(node_rows: list[dict[str, float]]) -> dict[float, dict[str, float]]:
    by_time: dict[float, list[dict[str, float]]] = defaultdict(list)
    for row in node_rows:
        by_time[row["time"]].append(row)
    summary = {}
    for t, rows in by_time.items():
        delta_power = np.array([r["delta_power"] for r in rows])
        lift_power = np.array([r["lift_power"] for r in rows])
        drag_power = np.array([r["drag_power"] for r in rows])
        delta_abs = np.array([
            math.sqrt(r["delta_fx"] ** 2 + r["delta_fy"] ** 2 + r["delta_fz"] ** 2)
            for r in rows
        ])
        summary[t] = {
            "clipped_count": float(sum(1 for r in rows if r["clipped"] > 0.5)),
            "max_alpha": float(max(r["alpha_deg"] for r in rows)),
            "sum_delta_power": float(np.sum(delta_power)),
            "sum_positive_delta_power": float(np.sum(delta_power[delta_power > 0])),
            "sum_negative_delta_power": float(np.sum(delta_power[delta_power < 0])),
            "sum_lift_power": float(np.sum(lift_power)),
            "sum_drag_power": float(np.sum(drag_power)),
            "max_delta_abs": float(np.max(delta_abs)),
            "node_max_delta_abs": float(rows[int(np.argmax(delta_abs))]["node"]),
            "max_positive_delta_power": float(np.max(delta_power)),
            "node_max_positive_delta_power": float(rows[int(np.argmax(delta_power))]["node"]),
            "max_lift_power": float(np.max(lift_power)),
            "node_max_lift_power": float(rows[int(np.argmax(lift_power))]["node"]),
        }
    return summary


def top_rows_at_snapshot(node_rows: list[dict[str, float]], snapshot: float) -> dict[str, object]:
    times = np.array(sorted({r["time"] for r in node_rows}))
    t = nearest_time(times, snapshot)
    rows = [r for r in node_rows if r["time"] == t]
    for r in rows:
        r["delta_abs"] = math.sqrt(r["delta_fx"] ** 2 + r["delta_fy"] ** 2 + r["delta_fz"] ** 2)
    clipped = [r for r in rows if r["clipped"] > 0.5]
    top_delta = sorted(rows, key=lambda r: r["delta_abs"], reverse=True)[:8]
    top_positive_power = sorted(rows, key=lambda r: r["delta_power"], reverse=True)[:8]
    top_alpha = sorted(rows, key=lambda r: r["alpha_deg"], reverse=True)[:8]
    return {
        "requested_time": snapshot,
        "actual_time": t,
        "clipped_nodes": [int(r["node"]) for r in clipped],
        "top_delta_abs": slim_node_rows(top_delta),
        "top_positive_delta_power": slim_node_rows(top_positive_power),
        "top_alpha": slim_node_rows(top_alpha),
    }


def slim_node_rows(rows: list[dict[str, float]]) -> list[dict[str, float | int]]:
    keys = [
        "node",
        "delta_abs",
        "delta_power",
        "current_power",
        "drag_power",
        "lift_power",
        "U_rel",
        "alpha_deg",
        "alpha_lookup_deg",
        "CD",
        "CL",
        "clipped",
        "vy",
        "vz",
    ]
    out = []
    for row in rows:
        item = {}
        for key in keys:
            if key in row:
                item[key] = int(row[key]) if key in {"node", "clipped"} else float(row[key])
        out.append(item)
    return out


def top_elements_at_snapshot(elem_rows: list[dict[str, float]], snapshot: float) -> dict[str, object]:
    times = np.array(sorted({r["time"] for r in elem_rows}))
    t = nearest_time(times, snapshot)
    rows = [r for r in elem_rows if r["time"] == t]
    top = sorted(rows, key=lambda r: abs(r["strain"]), reverse=True)[:10]
    return {
        "requested_time": snapshot,
        "actual_time": t,
        "top_abs_strain": [
            {
                "element": int(r["element"]),
                "strain": float(r["strain"]),
                "initial_length": float(r["initial_length"]),
                "current_length": float(r["current_length"]),
                "delta_tension_N": float(r["delta_tension_N"]),
                "estimated_total_tension_N": float(r["estimated_total_tension_N"]),
            }
            for r in top
        ],
    }


def make_plot(force: np.ndarray, strain: np.ndarray, node_summary: dict[float, dict[str, float]], out: Path) -> None:
    times = np.array(sorted(node_summary))
    node_sum_delta = np.array([node_summary[t]["sum_delta_power"] for t in times])
    node_sum_pos = np.array([node_summary[t]["sum_positive_delta_power"] for t in times])
    node_clip = np.array([node_summary[t]["clipped_count"] for t in times])
    mask_f = (force["time"] >= START) & (force["time"] <= END)
    mask_s = (strain["time"] >= START) & (strain["time"] <= END)
    fig, axes = plt.subplots(6, 1, figsize=(11, 13.5), sharex=True)
    axes[0].plot(force["time"][mask_f], force["Delta_F_motion"][mask_f], label="|Delta F|", lw=0.9)
    axes[0].plot(force["time"][mask_f], force["F_current"][mask_f], label="F_current", lw=0.9)
    axes[0].legend()
    axes[0].set_ylabel("force (N)")
    axes[1].plot(force["time"][mask_f], force["max_alpha_current_deg"][mask_f], lw=0.9)
    axes[1].axhline(29.9, color="black", ls="--", lw=0.8)
    axes[1].set_ylabel("max alpha")
    axes[2].plot(force["time"][mask_f], force["total_delta_power"][mask_f], label="global delta power", lw=0.9)
    axes[2].plot(times, node_sum_delta, label="node-summed delta power", lw=0.6, alpha=0.6)
    axes[2].plot(times, node_sum_pos, label="positive-node contribution", lw=0.8)
    axes[2].axhline(0.0, color="black", lw=0.8)
    axes[2].set_ylabel("power (W)")
    axes[2].legend()
    axes[3].plot(force["time"][mask_f], force["total_drag_power"][mask_f], label="drag", lw=0.8)
    axes[3].plot(force["time"][mask_f], force["total_lift_power"][mask_f], label="lift", lw=0.8)
    axes[3].axhline(0.0, color="black", lw=0.8)
    axes[3].set_ylabel("power (W)")
    axes[3].legend()
    axes[4].plot(strain["time"][mask_s], strain["max_abs_strain"][mask_s], color="#8B2E2E", lw=0.9)
    axes[4].axhline(RATED_STRAIN, color="black", ls="--", lw=0.8)
    axes[4].set_ylabel("max strain")
    axes[5].plot(force["time"][mask_f], force["clipped_count"][mask_f], label="force log clipped", lw=0.9)
    axes[5].plot(times, node_clip, label="node log clipped", lw=0.6, alpha=0.6)
    axes[5].set_ylabel("clipped nodes")
    axes[5].set_xlabel("time (s)")
    axes[5].legend()
    for ax in axes:
        ax.grid(True, color="#D8DEE8", lw=0.6)
    fig.tight_layout()
    fig.savefig(out / "onset_68p5_70p2_chain.png", dpi=180)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    force = load_force()
    strain = load_strain_summary()
    _, node_rows = subset_node_power(START, END)
    _, elem_rows = subset_element_log(START, END)
    node_summary = summarize_by_time(node_rows)

    snapshots = [top_rows_at_snapshot(node_rows, s) for s in SNAPSHOTS]
    elem_snaps = [top_elements_at_snapshot(elem_rows, s) for s in SNAPSHOTS]
    important_nodes = sorted(
        {
            int(r["node"])
            for snap in snapshots
            for group in ("top_delta_abs", "top_positive_delta_power", "top_alpha")
            for r in snap[group]
        }
    )
    states = {
        str(s): state_at_nodes(s, important_nodes)
        for s in [69.50, 69.70, 69.75]
    }
    result = {
        "case": str(CASE),
        "interval": [START, END],
        "events": first_force_events(force, strain),
        "snapshots": snapshots,
        "element_snapshots": elem_snaps,
        "important_node_states": states,
    }
    (OUT / "onset_root_cause_trace.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    make_plot(force, strain, node_summary, OUT)
    print(json.dumps(result["events"], indent=2))
    print(OUT / "onset_root_cause_trace.json")


if __name__ == "__main__":
    main()
