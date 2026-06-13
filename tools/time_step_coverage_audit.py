from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cable_analyser.config_loader import load_config
from cable_analyser.geometry import CableGeometry
from cable_analyser.postprocess import compute_clearance

from dynamic_response_audit import load_output_matrix


def count_data_rows(path: Path) -> int:
    if not path.exists() or path.stat().st_size == 0:
        return 0
    count = 0
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                count += 1
    return count


def load_displacement_time_series(config_path: Path, max_records: int | None = None) -> dict[str, Any]:
    cfg = load_config(config_path)
    geo = CableGeometry(cfg).generate()
    output_dir = ROOT / cfg["paths"]["output_dir"]
    n_nodes = len(geo["x"])
    dt = float(cfg["time_history"]["dt"])

    dynamic_path = output_dir / "Dynamic.out"
    raw_dynamic_rows = count_data_rows(dynamic_path)
    dynamic_raw = load_output_matrix(dynamic_path, max_rows=max_records)
    if dynamic_raw is None:
        raise FileNotFoundError(output_dir / "Dynamic.out")
    truncated_to_records = None
    if max_records is not None and max_records > 0 and raw_dynamic_rows > max_records:
        truncated_to_records = int(max_records)
    if dynamic_raw.shape[1] == 3 * n_nodes + 1:
        time = dynamic_raw[:, 0]
        disp_data = dynamic_raw[:, 1:]
    else:
        time = np.arange(dynamic_raw.shape[0], dtype=float) * dt
        disp_data = dynamic_raw
    if disp_data.shape[1] != 3 * n_nodes:
        raise ValueError(
            f"Dynamic.out has {disp_data.shape[1]} displacement columns; expected {3 * n_nodes}"
        )

    y = disp_data[:, 1::3]
    z = disp_data[:, 2::3]
    resultant = np.sqrt(y**2 + z**2)
    clearance = compute_clearance(y, z, geo["z"])

    accel_raw = load_output_matrix(output_dir / "Accel.out", max_rows=max_records)
    max_accel = None
    if accel_raw is not None:
        accel_data = accel_raw[:, 1:] if accel_raw.shape[1] == 3 * n_nodes + 1 else accel_raw
        if accel_data.shape[1] == 3 * n_nodes:
            ay = accel_data[:, 1::3]
            az = accel_data[:, 2::3]
            max_accel = np.max(np.sqrt(ay**2 + az**2), axis=1)

    return {
        "cfg": cfg,
        "geo": geo,
        "output_dir": output_dir,
        "time": time,
        "dt": dt,
        "raw_dynamic_rows": raw_dynamic_rows,
        "truncated_to_records": truncated_to_records,
        "global_disp": np.max(resultant, axis=1),
        "min_clearance": np.min(clearance, axis=1),
        "max_accel": max_accel,
    }


def aggregate_damping_by_time(path: Path, time: np.ndarray) -> dict[str, np.ndarray]:
    neg_fraction = np.zeros(len(time), dtype=float)
    min_xi = np.full(len(time), np.nan, dtype=float)
    mean_xi = np.full(len(time), np.nan, dtype=float)
    sample_count = np.zeros(len(time), dtype=int)

    if not path.exists() or path.stat().st_size == 0:
        return {
            "negative_fraction": neg_fraction,
            "min_xi": min_xi,
            "mean_xi": mean_xi,
            "sample_count": sample_count,
        }

    data = np.loadtxt(path)
    if data.ndim == 1:
        data = data[np.newaxis, :]
    damping_time = data[:, 0]
    xi = data[:, 3]
    rounded_dynamic = np.round(time, 8)
    index_by_time = {float(value): idx for idx, value in enumerate(rounded_dynamic)}

    groups: dict[float, list[float]] = {}
    for t_value, xi_value in zip(damping_time, xi):
        key = float(np.round(t_value, 8))
        groups.setdefault(key, []).append(float(xi_value))

    for key, values in groups.items():
        idx = index_by_time.get(key)
        if idx is None:
            continue
        arr = np.asarray(values, dtype=float)
        sample_count[idx] = int(len(arr))
        neg_fraction[idx] = float(np.mean(arr < 0.0))
        min_xi[idx] = float(np.min(arr))
        mean_xi[idx] = float(np.mean(arr))

    return {
        "negative_fraction": neg_fraction,
        "min_xi": min_xi,
        "mean_xi": mean_xi,
        "sample_count": sample_count,
    }


def rolling_p95(series: np.ndarray, points: int) -> np.ndarray:
    result = np.full(len(series), np.nan, dtype=float)
    if points <= 1:
        return series.astype(float)
    for idx in range(points - 1, len(series)):
        result[idx] = float(np.percentile(series[idx - points + 1:idx + 1], 95))
    return result


def longest_true_run_seconds(mask: np.ndarray, dt: float) -> float:
    longest = 0
    current = 0
    for value in mask:
        if bool(value):
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return float(longest * dt)


def summarize_mask(mask: np.ndarray, dt: float) -> dict[str, Any]:
    mask = np.asarray(mask, dtype=bool)
    true_steps = int(np.sum(mask))
    total_steps = int(len(mask))
    return {
        "steps_true": true_steps,
        "steps_total": total_steps,
        "time_true_s": float(true_steps * dt),
        "total_time_s": float(total_steps * dt),
        "coverage_fraction": float(true_steps / total_steps) if total_steps else 0.0,
        "longest_continuous_true_s": longest_true_run_seconds(mask, dt),
    }


def build_audit(
    config_path: Path,
    *,
    c2_element_negative_fraction: float,
    c2_min_xi_threshold: float,
    c4_window_s: float,
    c4_growth_over_previous: float,
    c4_growth_over_baseline: float,
    c6_displacement_fraction_of_sag: float,
    c7_clearance_limit_m: float,
    acceleration_limit: float | None,
    max_records: int | None,
) -> dict[str, Any]:
    data = load_displacement_time_series(config_path, max_records=max_records)
    cfg = data["cfg"]
    output_dir = data["output_dir"]
    time = data["time"]
    dt = float(data["dt"])
    sag = float(cfg["geometry"].get("Sag", 0.0))
    global_disp = data["global_disp"]
    min_clearance = data["min_clearance"]
    max_accel = data["max_accel"]

    damping = aggregate_damping_by_time(output_dir / "damping_change_log.txt", time)
    valid_damping = damping["sample_count"] > 0
    c2 = (
        valid_damping
        & (damping["negative_fraction"] >= c2_element_negative_fraction)
        & (np.nan_to_num(damping["min_xi"], nan=0.0) < c2_min_xi_threshold)
    )

    c4_points = max(2, int(round(c4_window_s / dt)))
    p95 = rolling_p95(global_disp, c4_points)
    previous = np.roll(p95, c4_points)
    previous[:c4_points] = np.nan
    baseline = p95[c4_points - 1] if len(p95) >= c4_points else np.nan
    c4 = (
        np.isfinite(p95)
        & np.isfinite(previous)
        & (previous > 1.0e-12)
        & np.isfinite(baseline)
        & (baseline > 1.0e-12)
        & ((p95 / previous) >= c4_growth_over_previous)
        & ((p95 / baseline) >= c4_growth_over_baseline)
    )

    c6_limit = c6_displacement_fraction_of_sag * sag
    c6 = global_disp >= c6_limit
    c7 = min_clearance < c7_clearance_limit_m
    c2_c4 = c2 & c4

    masks = {
        "C2_sustained_negative_damping": c2,
        "C4_rolling_response_growth": c4,
        "C6_large_response": c6,
        "C7_clearance_limit": c7,
        "C2_and_C4": c2_c4,
    }
    if acceleration_limit is not None and max_accel is not None:
        masks["C5_acceleration_limit"] = max_accel >= acceleration_limit

    summary = {key: summarize_mask(value, dt) for key, value in masks.items()}
    rows = []
    for idx, t_value in enumerate(time):
        row = {
            "step": int(idx),
            "time_s": float(t_value),
            "global_disp_m": float(global_disp[idx]),
            "min_clearance_m": float(min_clearance[idx]),
            "damping_sample_count": int(damping["sample_count"][idx]),
            "negative_element_fraction": float(damping["negative_fraction"][idx]),
            "min_xi": None if np.isnan(damping["min_xi"][idx]) else float(damping["min_xi"][idx]),
            "rolling_disp_p95_m": None if np.isnan(p95[idx]) else float(p95[idx]),
        }
        if max_accel is not None:
            row["max_accel_mps2"] = float(max_accel[idx])
        for key, mask in masks.items():
            row[key] = bool(mask[idx])
        rows.append(row)

    return {
        "config": str(config_path.relative_to(ROOT)),
        "output_dir": str(output_dir.relative_to(ROOT)),
        "dt_s": dt,
        "steps": int(len(time)),
        "duration_s": float(len(time) * dt),
        "raw_dynamic_rows": int(data["raw_dynamic_rows"]),
        "truncated_to_records": data["truncated_to_records"],
        "thresholds": {
            "C2_element_negative_fraction": c2_element_negative_fraction,
            "C2_min_xi_threshold": c2_min_xi_threshold,
            "C4_window_s": c4_window_s,
            "C4_growth_over_previous_window": c4_growth_over_previous,
            "C4_growth_over_baseline_window": c4_growth_over_baseline,
            "C6_displacement_fraction_of_sag": c6_displacement_fraction_of_sag,
            "C6_displacement_limit_m": c6_limit,
            "C7_clearance_limit_m": c7_clearance_limit_m,
            "C5_acceleration_limit_mps2": acceleration_limit,
        },
        "summary": summary,
        "time_steps": rows,
    }


def write_markdown(audit: dict[str, Any], path: Path) -> None:
    lines = [
        "# Time-Step Coverage Audit",
        "",
        f"Config: `{audit['config']}`",
        f"Output dir: `{audit['output_dir']}`",
        f"dt: `{audit['dt_s']}` s",
        f"Steps/duration: `{audit['steps']}` / `{audit['duration_s']}` s",
        f"Raw Dynamic.out rows: `{audit['raw_dynamic_rows']}`; truncated_to_records: `{audit['truncated_to_records']}`",
        "",
        "## Thresholds",
        "",
    ]
    for key, value in audit["thresholds"].items():
        lines.append(f"- {key}: `{value}`")
    lines += [
        "",
        "## Coverage Summary",
        "",
        "| Criterion | Problem steps | Total steps | Problem time (s) | Coverage | Longest continuous (s) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for key, value in audit["summary"].items():
        lines.append(
            f"| {key} | {value['steps_true']} | {value['steps_total']} | "
            f"{value['time_true_s']:.3f} | {value['coverage_fraction']:.4f} | "
            f"{value['longest_continuous_true_s']:.3f} |"
        )
    lines += [
        "",
        "## Notes",
        "",
        "- Coverage is counted directly in model time steps.",
        "- With `dt = 0.05 s`, 20 s of exceedance equals 400 problem steps.",
        "- C4 is assigned to time steps through a rolling p95 response-growth limit, because growth is not an instantaneous scalar.",
        "- C2 aggregates all available element damping values at the same time stamp.",
        "- If `truncated_to_records` is not null, the audit used a fixed target record window to avoid adaptive substep density bias.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--c2-element-negative-fraction", type=float, default=0.05)
    parser.add_argument("--c2-min-xi-threshold", type=float, default=-1.0e-4)
    parser.add_argument("--c4-window-s", type=float, default=20.0)
    parser.add_argument("--c4-growth-over-previous", type=float, default=1.20)
    parser.add_argument("--c4-growth-over-baseline", type=float, default=1.50)
    parser.add_argument("--c6-displacement-fraction-of-sag", type=float, default=0.10)
    parser.add_argument("--c7-clearance-limit-m", type=float, default=0.0)
    parser.add_argument("--acceleration-limit", type=float, default=None)
    parser.add_argument("--max-records", type=int, default=None)
    args = parser.parse_args()

    audit = build_audit(
        (ROOT / args.config).resolve(),
        c2_element_negative_fraction=args.c2_element_negative_fraction,
        c2_min_xi_threshold=args.c2_min_xi_threshold,
        c4_window_s=args.c4_window_s,
        c4_growth_over_previous=args.c4_growth_over_previous,
        c4_growth_over_baseline=args.c4_growth_over_baseline,
        c6_displacement_fraction_of_sag=args.c6_displacement_fraction_of_sag,
        c7_clearance_limit_m=args.c7_clearance_limit_m,
        acceleration_limit=args.acceleration_limit,
        max_records=args.max_records,
    )
    out_dir = (ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "time_step_coverage_audit.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    write_markdown(audit, out_dir / "time_step_coverage_audit.md")
    print(f"Wrote {out_dir / 'time_step_coverage_audit.md'}")


if __name__ == "__main__":
    main()
