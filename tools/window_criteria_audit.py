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


def load_damping_rows(path: Path) -> tuple[np.ndarray, np.ndarray] | tuple[None, None]:
    if not path.exists() or path.stat().st_size == 0:
        return None, None
    data = np.loadtxt(path)
    if data.ndim == 1:
        data = data[np.newaxis, :]
    return data[:, 0], data[:, 3]


def safe_ratio(num: float, den: float) -> float | None:
    if abs(den) <= 1.0e-12:
        return None
    return num / den


def occupancy(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    values = [bool(row[key]) for row in rows]
    return {
        "windows_true": int(sum(values)),
        "windows_total": int(len(values)),
        "window_fraction": float(np.mean(values)) if values else 0.0,
    }


def build_window_audit(
    config_path: Path,
    *,
    window_s: float,
    step_s: float,
    negative_fraction_threshold: float,
    min_negative_xi_threshold: float,
    growth_late_over_prev: float,
    growth_late_over_baseline: float,
    large_response_fraction_of_sag: float,
    clearance_limit_m: float,
) -> dict[str, Any]:
    cfg = load_config(config_path)
    geo = CableGeometry(cfg).generate()
    output_dir = ROOT / cfg["paths"]["output_dir"]
    n_nodes = len(geo["x"])
    dt = float(cfg["time_history"]["dt"])

    dynamic_raw = load_output_matrix(output_dir / "Dynamic.out")
    if dynamic_raw is None:
        raise FileNotFoundError(output_dir / "Dynamic.out")
    disp_data = dynamic_raw
    if disp_data.shape[1] == 3 * n_nodes + 1:
        time = disp_data[:, 0]
        disp_data = disp_data[:, 1:]
    else:
        time = np.arange(disp_data.shape[0], dtype=float) * dt
    if disp_data.shape[1] != 3 * n_nodes:
        raise ValueError(
            f"Dynamic.out has {disp_data.shape[1]} displacement columns; expected {3 * n_nodes}"
        )

    y = disp_data[:, 1::3]
    z = disp_data[:, 2::3]
    resultant = np.sqrt(y**2 + z**2)
    global_resultant = np.max(resultant, axis=1)
    clearance = compute_clearance(y, z, geo["z"])
    global_min_clearance = np.min(clearance, axis=1)

    damping_time, damping_xi = load_damping_rows(output_dir / "damping_change_log.txt")

    sag = float(cfg["geometry"].get("Sag", cfg["geometry"].get("H", 0.0)))
    large_response_threshold_m = large_response_fraction_of_sag * sag
    duration = float(time[-1] - time[0] + dt)
    starts = np.arange(float(time[0]), float(time[-1]) - window_s + dt, step_s)

    rows: list[dict[str, Any]] = []
    previous_p95: float | None = None
    baseline_p95: float | None = None

    for idx, start in enumerate(starts):
        end = float(start + window_s)
        mask = (time >= start) & (time < end)
        if not np.any(mask):
            continue
        series = global_resultant[mask]
        p95 = float(np.percentile(series, 95))
        max_disp = float(np.max(series))
        min_clearance = float(np.min(global_min_clearance[mask]))
        if baseline_p95 is None:
            baseline_p95 = p95

        if damping_time is not None and damping_xi is not None:
            dmask = (damping_time >= start) & (damping_time < end)
            if np.any(dmask):
                xi_window = damping_xi[dmask]
                neg_fraction = float(np.mean(xi_window < 0.0))
                min_xi = float(np.min(xi_window))
            else:
                neg_fraction = 0.0
                min_xi = None
        else:
            neg_fraction = 0.0
            min_xi = None

        late_over_prev = safe_ratio(p95, previous_p95) if previous_p95 is not None else None
        late_over_baseline = safe_ratio(p95, baseline_p95) if baseline_p95 is not None else None

        c2 = bool(
            neg_fraction >= negative_fraction_threshold
            and min_xi is not None
            and min_xi < min_negative_xi_threshold
        )
        c4 = bool(
            late_over_prev is not None
            and late_over_baseline is not None
            and late_over_prev >= growth_late_over_prev
            and late_over_baseline >= growth_late_over_baseline
        )
        c6 = bool(p95 >= large_response_threshold_m)
        c7 = bool(min_clearance < clearance_limit_m)
        c2_c4 = bool(c2 and c4)

        rows.append(
            {
                "window_index": idx,
                "start_s": float(start),
                "end_s": end,
                "global_disp_p95_m": p95,
                "global_disp_max_m": max_disp,
                "min_clearance_m": min_clearance,
                "negative_damping_fraction": neg_fraction,
                "min_xi": min_xi,
                "late_over_previous_window": late_over_prev,
                "late_over_baseline_window": late_over_baseline,
                "C2_sustained_negative_damping": c2,
                "C4_response_growth": c4,
                "C6_large_response": c6,
                "C7_clearance_limit": c7,
                "C2_and_C4_confirmed_window": c2_c4,
            }
        )
        previous_p95 = p95

    summary = {
        "C2_sustained_negative_damping": occupancy(rows, "C2_sustained_negative_damping"),
        "C4_response_growth": occupancy(rows, "C4_response_growth"),
        "C6_large_response": occupancy(rows, "C6_large_response"),
        "C7_clearance_limit": occupancy(rows, "C7_clearance_limit"),
        "C2_and_C4_confirmed_window": occupancy(rows, "C2_and_C4_confirmed_window"),
    }
    return {
        "config": str(config_path.relative_to(ROOT)),
        "output_dir": str(output_dir.relative_to(ROOT)),
        "duration_s": duration,
        "dt_s": dt,
        "window_s": window_s,
        "step_s": step_s,
        "n_windows": len(rows),
        "thresholds": {
            "C2_negative_fraction_threshold": negative_fraction_threshold,
            "C2_min_xi_threshold": min_negative_xi_threshold,
            "C4_late_over_previous_window": growth_late_over_prev,
            "C4_late_over_baseline_window": growth_late_over_baseline,
            "C6_large_response_fraction_of_sag": large_response_fraction_of_sag,
            "C6_large_response_threshold_m": large_response_threshold_m,
            "C7_clearance_limit_m": clearance_limit_m,
        },
        "summary": summary,
        "windows": rows,
    }


def write_markdown(audit: dict[str, Any], path: Path) -> None:
    lines = [
        "# Window Criteria Audit",
        "",
        f"Config: `{audit['config']}`",
        f"Output dir: `{audit['output_dir']}`",
        f"Duration: `{audit['duration_s']:.6g}` s",
        f"Window/step: `{audit['window_s']}` / `{audit['step_s']}` s",
        f"Windows: `{audit['n_windows']}`",
        "",
        "## Thresholds",
        "",
    ]
    for key, value in audit["thresholds"].items():
        lines.append(f"- {key}: `{value}`")
    lines += [
        "",
        "## Occupancy Summary",
        "",
        "| Criterion | Windows true | Windows total | Fraction |",
        "|---|---:|---:|---:|",
    ]
    for key, value in audit["summary"].items():
        lines.append(
            f"| {key} | {value['windows_true']} | {value['windows_total']} | "
            f"{value['window_fraction']:.3f} |"
        )
    lines += [
        "",
        "## Window Table",
        "",
        "| i | start | end | p95 disp | max disp | neg damping frac | min xi | prev growth | baseline growth | C2 | C4 | C6 | C7 | C2&C4 |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|",
    ]
    for row in audit["windows"]:
        min_xi = row["min_xi"]
        prev = row["late_over_previous_window"]
        base = row["late_over_baseline_window"]
        lines.append(
            f"| {row['window_index']} | {row['start_s']:.1f} | {row['end_s']:.1f} | "
            f"{row['global_disp_p95_m']:.3f} | {row['global_disp_max_m']:.3f} | "
            f"{row['negative_damping_fraction']:.3f} | "
            f"{min_xi:.4f}" if min_xi is not None else "| None"
        )
        tail = (
            f" | {prev:.3f}" if prev is not None else " | None"
        ) + (
            f" | {base:.3f}" if base is not None else " | None"
        ) + (
            f" | {'yes' if row['C2_sustained_negative_damping'] else 'no'}"
            f" | {'yes' if row['C4_response_growth'] else 'no'}"
            f" | {'yes' if row['C6_large_response'] else 'no'}"
            f" | {'yes' if row['C7_clearance_limit'] else 'no'}"
            f" | {'yes' if row['C2_and_C4_confirmed_window'] else 'no'} |"
        )
        lines[-1] += tail
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--window-s", type=float, default=20.0)
    parser.add_argument("--step-s", type=float, default=10.0)
    parser.add_argument("--negative-fraction-threshold", type=float, default=0.005)
    parser.add_argument("--min-negative-xi-threshold", type=float, default=-1.0e-4)
    parser.add_argument("--growth-late-over-prev", type=float, default=1.20)
    parser.add_argument("--growth-late-over-baseline", type=float, default=1.50)
    parser.add_argument("--large-response-fraction-of-sag", type=float, default=0.10)
    parser.add_argument("--clearance-limit-m", type=float, default=0.0)
    args = parser.parse_args()

    audit = build_window_audit(
        (ROOT / args.config).resolve(),
        window_s=args.window_s,
        step_s=args.step_s,
        negative_fraction_threshold=args.negative_fraction_threshold,
        min_negative_xi_threshold=args.min_negative_xi_threshold,
        growth_late_over_prev=args.growth_late_over_prev,
        growth_late_over_baseline=args.growth_late_over_baseline,
        large_response_fraction_of_sag=args.large_response_fraction_of_sag,
        clearance_limit_m=args.clearance_limit_m,
    )
    out_dir = (ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "window_criteria_audit.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    write_markdown(audit, out_dir / "window_criteria_audit.md")
    print(f"Wrote {out_dir / 'window_criteria_audit.md'}")


if __name__ == "__main__":
    main()
