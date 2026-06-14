from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = ROOT / "output" / "diagnostics" / "c4_structural_model_comparison_200s"
CASES = {
    "tension_only": OUT_ROOT / "tension_only" / "run",
    "bidirectional_axial": OUT_ROOT / "bidirectional_axial" / "run",
}
OUT = OUT_ROOT / "comparison" / "abnormal_onset"
N_NODES = 101


THRESHOLDS = {
    "disp_0p5m": 0.5,
    "disp_1m": 1.0,
    "disp_2m": 2.0,
    "vel_1mps": 1.0,
    "vel_5mps": 5.0,
    "acc_100mps2": 100.0,
    "strain_0p001": 1.0e-3,
    "strain_0p005": 5.0e-3,
    "strain_0p01": 1.0e-2,
    "tension_abs_100kN": 100.0e3,
    "tension_abs_500kN": 500.0e3,
    "delta_force_500N": 500.0,
    "delta_force_1000N": 1000.0,
    "delta_power_abs_1000W": 1000.0,
    "delta_power_abs_10000W": 10000.0,
    "alpha_30deg": 30.0,
    "alpha_60deg": 60.0,
}


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


def first_time(time: np.ndarray, mask: np.ndarray) -> float | None:
    idx = np.flatnonzero(mask)
    if idx.size == 0:
        return None
    return float(time[int(idx[0])])


def xz_norm(mat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    time = mat[:, 0]
    xyz = mat[:, 1:].reshape(mat.shape[0], N_NODES, 3)
    mag = np.linalg.norm(xyz[:, :, [0, 2]], axis=2)
    return time, np.max(mag, axis=1)


def summarize_case(name: str, run: Path) -> dict:
    summary: dict = {"status": read_status(run), "events": {}, "peaks": {}}

    dyn = load_matrix(run / "Dynamic.out")
    vel = load_matrix(run / "Velocity.out")
    acc = load_matrix(run / "Accel.out")
    ten = load_csv(run / "element_strain_tension_summary_log.csv")
    elem = load_csv(run / "element_strain_tension_log.csv")
    force = load_space(run / "incremental_quasi_steady_aero_force_log.txt")
    power = load_csv(run / "incremental_qs_node_power_log.csv")

    if dyn is not None:
        t, v = xz_norm(dyn)
        summary["peaks"]["disp_max_m"] = float(np.max(v))
        summary["peaks"]["disp_max_time_s"] = float(t[int(np.argmax(v))])
        for key, thr in [("disp_0p5m", 0.5), ("disp_1m", 1.0), ("disp_2m", 2.0)]:
            summary["events"][key] = first_time(t, v >= thr)
    if vel is not None:
        t, v = xz_norm(vel)
        summary["peaks"]["vel_max_mps"] = float(np.max(v))
        summary["peaks"]["vel_max_time_s"] = float(t[int(np.argmax(v))])
        for key, thr in [("vel_1mps", 1.0), ("vel_5mps", 5.0)]:
            summary["events"][key] = first_time(t, v >= thr)
    if acc is not None:
        t, v = xz_norm(acc)
        summary["peaks"]["acc_max_mps2"] = float(np.max(v))
        summary["peaks"]["acc_max_time_s"] = float(t[int(np.argmax(v))])
        summary["events"]["acc_100mps2"] = first_time(t, v >= 100.0)
    if ten is not None:
        t = np.asarray(ten["time"], dtype=float)
        min_tension = np.asarray(ten["min_estimated_tension_N"], dtype=float)
        max_abs_tension = np.asarray(ten["max_abs_tension_N"], dtype=float)
        max_strain = np.asarray(ten["max_abs_strain"], dtype=float)
        slack = np.asarray(ten["slack_element_count"], dtype=float)
        summary["peaks"]["min_tension_N"] = float(np.min(min_tension))
        summary["peaks"]["min_tension_time_s"] = float(t[int(np.argmin(min_tension))])
        summary["peaks"]["max_abs_tension_N"] = float(np.max(max_abs_tension))
        summary["peaks"]["max_abs_tension_time_s"] = float(t[int(np.argmax(max_abs_tension))])
        summary["peaks"]["max_abs_strain"] = float(np.max(max_strain))
        summary["peaks"]["max_abs_strain_time_s"] = float(t[int(np.argmax(max_strain))])
        summary["peaks"]["max_slack_count"] = int(np.max(slack))
        summary["events"]["negative_tension"] = first_time(t, min_tension < 0.0)
        summary["events"]["slack_count_gt0"] = first_time(t, slack > 0.0)
        for key, thr in [
            ("strain_0p001", 1.0e-3),
            ("strain_0p005", 5.0e-3),
            ("strain_0p01", 1.0e-2),
        ]:
            summary["events"][key] = first_time(t, max_strain >= thr)
        for key, thr in [
            ("tension_abs_100kN", 100.0e3),
            ("tension_abs_500kN", 500.0e3),
        ]:
            summary["events"][key] = first_time(t, max_abs_tension >= thr)
    if force is not None:
        t = np.asarray(force["time"], dtype=float)
        total_delta = np.asarray(force["total_abs_delta_force"], dtype=float)
        max_alpha = np.abs(np.asarray(force["max_alpha_current_deg"], dtype=float))
        clipped = np.asarray(force["clipped_count"], dtype=float)
        delta_power = np.asarray(force["total_delta_power"], dtype=float)
        summary["peaks"]["max_total_abs_delta_force_N"] = float(np.max(total_delta))
        summary["peaks"]["max_total_abs_delta_force_time_s"] = float(t[int(np.argmax(total_delta))])
        summary["peaks"]["max_abs_alpha_deg"] = float(np.max(max_alpha))
        summary["peaks"]["max_abs_alpha_time_s"] = float(t[int(np.argmax(max_alpha))])
        summary["peaks"]["max_clipped_count"] = int(np.max(clipped))
        summary["peaks"]["max_total_delta_power_W"] = float(np.max(delta_power))
        summary["peaks"]["min_total_delta_power_W"] = float(np.min(delta_power))
        for key, thr in [
            ("delta_force_500N", 500.0),
            ("delta_force_1000N", 1000.0),
        ]:
            summary["events"][key] = first_time(t, total_delta >= thr)
        for key, thr in [("alpha_30deg", 30.0), ("alpha_60deg", 60.0)]:
            summary["events"][key] = first_time(t, max_alpha >= thr)
        summary["events"]["alpha_clipping"] = first_time(t, clipped > 0.0)
        for key, thr in [
            ("delta_power_abs_1000W", 1000.0),
            ("delta_power_abs_10000W", 10000.0),
        ]:
            summary["events"][key] = first_time(t, np.abs(delta_power) >= thr)
    if power is not None:
        t = np.asarray(power["time"], dtype=float)
        node_power = np.asarray(power["delta_power"], dtype=float)
        # CSV is long-form; aggregate per recorded time.
        unique_t = np.unique(t)
        max_abs_per_t = np.array([np.max(np.abs(node_power[t == tt])) for tt in unique_t])
        summary["peaks"]["max_abs_node_delta_power_W"] = float(np.max(max_abs_per_t))
        summary["peaks"]["max_abs_node_delta_power_time_s"] = float(unique_t[int(np.argmax(max_abs_per_t))])
        summary["events"]["node_delta_power_abs_100W"] = first_time(unique_t, max_abs_per_t >= 100.0)
        summary["events"]["node_delta_power_abs_1000W"] = first_time(unique_t, max_abs_per_t >= 1000.0)
    if elem is not None:
        # Element-level first rows for root-cause inspection.
        t = np.asarray(elem["time"], dtype=float)
        est = np.asarray(elem["estimated_total_tension_N"], dtype=float)
        strain = np.asarray(elem["strain"], dtype=float)
        neg_idx = np.flatnonzero(est < 0.0)
        if neg_idx.size:
            rows = []
            for idx in neg_idx[:10]:
                rows.append({
                    "time": float(t[idx]),
                    "element": int(elem["element"][idx]),
                    "strain": float(strain[idx]),
                    "estimated_total_tension_N": float(est[idx]),
                })
            summary["first_negative_element_rows"] = rows
        slack_idx = np.flatnonzero(est == 0.0)
        if slack_idx.size:
            rows = []
            for idx in slack_idx[:10]:
                rows.append({
                    "time": float(t[idx]),
                    "element": int(elem["element"][idx]),
                    "strain": float(strain[idx]),
                    "estimated_total_tension_N": float(est[idx]),
                })
            summary["first_slack_element_rows"] = rows

    ordered = [
        (k, v) for k, v in summary["events"].items()
        if v is not None
    ]
    ordered.sort(key=lambda item: item[1])
    summary["ordered_events"] = ordered
    return summary


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {name: summarize_case(name, run) for name, run in CASES.items()}
    out_path = OUT / "abnormal_onset_summary.json"
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    for name, item in summary.items():
        lines = [f"# {name}", "", "## Ordered events"]
        for key, value in item["ordered_events"]:
            lines.append(f"- {key}: {value:.6f} s")
        lines.extend(["", "## Status", "```json", json.dumps(item["status"], indent=2), "```"])
        (OUT / f"{name}_abnormal_onset.md").write_text("\n".join(lines), encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
