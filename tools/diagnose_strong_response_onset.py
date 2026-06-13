from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diagnose when and how a strong response starts.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--n-nodes", type=int, default=101)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--window", type=float, default=5.0)
    return parser.parse_args()


def load_matrix(path: Path) -> np.ndarray:
    if not path.exists() or path.stat().st_size == 0:
        return np.empty((0, 0))
    return np.loadtxt(path)


def load_damping(path: Path) -> np.ndarray:
    rows = []
    if not path.exists():
        return np.empty((0, 4))
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            parts = line.split()
            if len(parts) < 4:
                continue
            try:
                rows.append([float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3])])
            except ValueError:
                continue
    return np.asarray(rows, dtype=float) if rows else np.empty((0, 4))


def node_resultant(data: np.ndarray, n_nodes: int) -> tuple[np.ndarray, np.ndarray]:
    if data.size == 0:
        return np.array([]), np.array([])
    time = data[:, 0]
    vals = data[:, 1:]
    n_cols = vals.shape[1]
    if n_cols >= n_nodes * 3:
        vals = vals[:, : n_nodes * 3].reshape((-1, n_nodes, 3))
        y = vals[:, :, 1]
        z = vals[:, :, 2]
    elif n_cols >= n_nodes * 2:
        vals = vals[:, : n_nodes * 2].reshape((-1, n_nodes, 2))
        y = vals[:, :, 0]
        z = vals[:, :, 1]
    else:
        raise ValueError(f"Cannot infer nodal y/z columns from {n_cols} columns")
    envelope = np.nanmax(np.sqrt(y * y + z * z), axis=1)
    return time, envelope


def rolling_metrics(time: np.ndarray, values: np.ndarray, window: float) -> list[dict]:
    if len(time) == 0:
        return []
    start = float(np.nanmin(time))
    end = float(np.nanmax(time))
    rows = []
    t0 = start
    while t0 < end:
        t1 = t0 + window
        mask = (time >= t0) & (time < t1)
        if np.any(mask):
            segment = values[mask]
            rows.append(
                {
                    "t0": t0,
                    "t1": t1,
                    "n": int(np.sum(mask)),
                    "max": float(np.nanmax(segment)),
                    "p95": float(np.nanpercentile(segment, 95)),
                    "rms": float(np.sqrt(np.nanmean(segment * segment))),
                }
            )
        t0 = t1
    for idx, row in enumerate(rows):
        if idx == 0:
            row["growth_prev_p95"] = None
            row["growth_base_p95"] = 1.0
        else:
            prev = rows[idx - 1]["p95"]
            base = rows[0]["p95"]
            row["growth_prev_p95"] = None if prev == 0 else row["p95"] / prev
            row["growth_base_p95"] = None if base == 0 else row["p95"] / base
    return rows


def damping_windows(damping: np.ndarray, windows: list[dict]) -> None:
    if damping.size == 0:
        for row in windows:
            row.update({"xi_min": None, "xi_negative_fraction": None, "xi_rows": 0})
        return
    t = damping[:, 0]
    xi = damping[:, 3]
    for row in windows:
        mask = (t >= row["t0"]) & (t < row["t1"])
        if not np.any(mask):
            row.update({"xi_min": None, "xi_negative_fraction": None, "xi_rows": 0})
            continue
        xi_seg = xi[mask]
        row.update(
            {
                "xi_min": float(np.nanmin(xi_seg)),
                "xi_negative_fraction": float(np.mean(xi_seg < 0.0)),
                "xi_rows": int(np.sum(mask)),
            }
        )


def repeated_time_stats(time: np.ndarray) -> dict:
    if len(time) == 0:
        return {}
    unique, counts = np.unique(np.round(time, 9), return_counts=True)
    repeated = counts[counts > 1]
    return {
        "n_rows": int(len(time)),
        "n_unique_time": int(len(unique)),
        "max_duplicate_count": int(np.max(repeated)) if repeated.size else 1,
        "duplicate_time_fraction": float(np.sum(counts[counts > 1]) / len(time)),
    }


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    out_dir = Path(args.out_dir) if args.out_dir else output_dir / "strong_response_diagnosis"
    out_dir.mkdir(parents=True, exist_ok=True)

    dyn = load_matrix(output_dir / "Dynamic.out")
    vel = load_matrix(output_dir / "Velocity.out")
    acc = load_matrix(output_dir / "Accel.out")
    damping = load_damping(output_dir / "damping_change_log.txt")

    t_disp, disp_env = node_resultant(dyn, args.n_nodes)
    t_vel, vel_env = node_resultant(vel, args.n_nodes)
    t_acc, acc_env = node_resultant(acc, args.n_nodes)

    rows = rolling_metrics(t_disp, disp_env, args.window)
    vel_rows = rolling_metrics(t_vel, vel_env, args.window)
    acc_rows = rolling_metrics(t_acc, acc_env, args.window)
    damping_windows(damping, rows)

    for i, row in enumerate(rows):
        if i < len(vel_rows):
            row["vel_p95"] = vel_rows[i]["p95"]
            row["vel_max"] = vel_rows[i]["max"]
        if i < len(acc_rows):
            row["acc_p95"] = acc_rows[i]["p95"]
            row["acc_max"] = acc_rows[i]["max"]

    onset_candidates = [
        row
        for row in rows
        if (row.get("growth_prev_p95") is not None and row["growth_prev_p95"] >= 1.2)
        or (row.get("growth_base_p95") is not None and row["growth_base_p95"] >= 1.5)
        or (row.get("xi_negative_fraction") is not None and row["xi_negative_fraction"] >= 0.25)
    ]

    summary = {
        "output_dir": str(output_dir.resolve()),
        "last_time": float(t_disp[-1]) if len(t_disp) else None,
        "disp_max": float(np.nanmax(disp_env)) if len(disp_env) else None,
        "vel_max": float(np.nanmax(vel_env)) if len(vel_env) else None,
        "acc_max": float(np.nanmax(acc_env)) if len(acc_env) else None,
        "first_onset_candidate": onset_candidates[0] if onset_candidates else None,
        "last_windows": rows[-8:],
        "time_repetition": repeated_time_stats(t_disp),
    }

    with (out_dir / "strong_response_windows.csv").open("w", newline="", encoding="utf-8") as fh:
        if rows:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    (out_dir / "strong_response_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    md = [
        "# Strong Response Onset Diagnosis",
        "",
        f"- Output directory: `{summary['output_dir']}`",
        f"- Last dynamic time: `{summary['last_time']}` s",
        f"- Max displacement envelope: `{summary['disp_max']}`",
        f"- Max velocity envelope: `{summary['vel_max']}`",
        f"- Max acceleration envelope: `{summary['acc_max']}`",
        f"- Time repetition: `{summary['time_repetition']}`",
        "",
        "## First Onset Candidate",
        "",
        f"`{summary['first_onset_candidate']}`",
        "",
        "## Last Windows",
        "",
    ]
    for row in summary["last_windows"]:
        md.append(f"- `{row}`")
    (out_dir / "strong_response_diagnosis.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(out_dir / "strong_response_diagnosis.md")


if __name__ == "__main__":
    main()
