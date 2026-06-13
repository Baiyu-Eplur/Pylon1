from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml


ROOT = Path(__file__).resolve().parents[1]
POINTS = [
    ("quarter_1", "1/4 span", 26),
    ("midspan", "Midspan", 51),
    ("quarter_3", "3/4 span", 76),
]


def load_vector(path: Path) -> np.ndarray:
    data = np.loadtxt(path)
    return np.asarray(data, dtype=float)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot wind-force histories at the monitored cable points.")
    parser.add_argument("--config", required=True, help="YAML config for the run.")
    parser.add_argument("--output-dir", required=True, help="Directory for PNG/CSV outputs.")
    parser.add_argument("--duration", type=float, default=None, help="Optional maximum plotted time in seconds.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = Path(args.config)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    cfg = yaml.safe_load(config.read_text(encoding="utf-8"))

    force_dir = ROOT / cfg["paths"]["forces_dir"] / cfg["time_history"]["folder_1"][0] / cfg["time_history"]["folder_2"][0]
    dt = float(cfg["time_history"]["dt"])
    npt = int(cfg["time_history"]["npt"])
    max_points = npt if args.duration is None else min(npt, int(round(args.duration / dt)) + 1)

    rows: list[dict[str, float | str | int]] = []
    data: dict[str, dict[str, np.ndarray]] = {}
    for key, label, node in POINTS:
        h_drag = 1000.0 * load_vector(force_dir / f"NODE_{node}_H_drag.txt")[:max_points]
        h_lift = 1000.0 * load_vector(force_dir / f"NODE_{node}_H_lift.txt")[:max_points]
        v_drag = 1000.0 * load_vector(force_dir / f"NODE_{node}_V_drag.txt")[:max_points]
        v_lift = 1000.0 * load_vector(force_dir / f"NODE_{node}_V_lift.txt")[:max_points]
        n = min(len(h_drag), len(h_lift), len(v_drag), len(v_lift), max_points)
        time = np.arange(n, dtype=float) * dt
        h_drag = h_drag[:n]
        h_lift = h_lift[:n]
        v_drag = v_drag[:n]
        v_lift = v_lift[:n]
        fy = h_drag + v_lift
        fz = h_lift + v_drag
        f_abs = np.sqrt(fy**2 + fz**2)
        data[label] = {
            "time": time,
            "h_drag": h_drag,
            "h_lift": h_lift,
            "v_drag": v_drag,
            "v_lift": v_lift,
            "fy": fy,
            "fz": fz,
            "f_abs": f_abs,
        }
        rows.append({
            "point": label,
            "node": node,
            "time_end_s": float(time[-1]),
            "mean_Fy_N": float(np.mean(fy)),
            "std_Fy_N": float(np.std(fy)),
            "min_Fy_N": float(np.min(fy)),
            "max_Fy_N": float(np.max(fy)),
            "mean_Fz_N": float(np.mean(fz)),
            "std_Fz_N": float(np.std(fz)),
            "min_Fz_N": float(np.min(fz)),
            "max_Fz_N": float(np.max(fz)),
            "max_abs_force_N": float(np.max(f_abs)),
        })

    csv_path = out / "point_wind_force_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    colors = {
        "1/4 span": "#2E6FBB",
        "Midspan": "#B84A62",
        "3/4 span": "#27856A",
    }

    fig, axes = plt.subplots(2, 1, figsize=(12, 7.5), dpi=170, sharex=True)
    for label, item in data.items():
        axes[0].plot(item["time"], item["fy"], lw=0.85, color=colors[label], label=label)
        axes[1].plot(item["time"], item["fz"], lw=0.85, color=colors[label], label=label)
    axes[0].set_title("Applied precomputed wind-force components at monitored points")
    axes[0].set_ylabel("Fy = H_drag + V_lift (N)")
    axes[1].set_ylabel("Fz = H_lift + V_drag (N)")
    axes[1].set_xlabel("time (s)")
    for ax in axes:
        ax.grid(True, alpha=0.25)
        ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(out / "point_wind_force_yz.png")
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(13.5, 8.5), dpi=170, sharex=True)
    component_names = [
        ("h_drag", "H_drag file contribution (N)"),
        ("h_lift", "H_lift file contribution (N)"),
        ("v_drag", "V_drag file contribution (N)"),
        ("v_lift", "V_lift file contribution (N)"),
    ]
    for ax, (key, title) in zip(axes.ravel(), component_names):
        for label, item in data.items():
            ax.plot(item["time"], item[key], lw=0.75, color=colors[label], label=label)
        ax.set_title(title)
        ax.grid(True, alpha=0.25)
    axes[1, 0].set_xlabel("time (s)")
    axes[1, 1].set_xlabel("time (s)")
    axes[0, 0].set_ylabel("force (N)")
    axes[1, 0].set_ylabel("force (N)")
    axes[0, 0].legend(loc="best")
    fig.tight_layout()
    fig.savefig(out / "point_wind_force_raw_components.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 5.8), dpi=170)
    for label, item in data.items():
        ax.plot(item["time"], item["f_abs"], lw=0.9, color=colors[label], label=label)
    ax.set_title("Resultant precomputed wind-force magnitude at monitored points")
    ax.set_ylabel("|F_yz| (N)")
    ax.set_xlabel("time (s)")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(out / "point_wind_force_magnitude.png")
    plt.close(fig)

    print(csv_path)
    print(out / "point_wind_force_yz.png")
    print(out / "point_wind_force_raw_components.png")
    print(out / "point_wind_force_magnitude.png")


if __name__ == "__main__":
    main()
