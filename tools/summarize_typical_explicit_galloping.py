from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


RUN = Path("output/diagnostics/typical_explicit_galloping/run")
OUT = Path("output/diagnostics/typical_explicit_galloping/analysis")


def load_table(path: Path) -> np.ndarray:
    data = np.loadtxt(path)
    if data.ndim == 1:
        data = data[np.newaxis, :]
    return data


def envelope(path: Path) -> tuple[np.ndarray, np.ndarray]:
    data = load_table(path)
    t = data[:, 0]
    y = data[:, 1:]
    env = np.nanmax(np.abs(y), axis=1)
    return t, env


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    t_disp, disp_env = envelope(RUN / "Dynamic.out")
    t_vel, vel_env = envelope(RUN / "Velocity.out")
    t_acc, acc_env = envelope(RUN / "Accel.out")

    force = load_table(RUN / "explicit_aero_damping_force_log.txt")
    damping = load_table(RUN / "damping_change_log.txt")
    summary = json.loads((RUN / "strong_response_diagnosis" / "strong_response_summary.json").read_text(encoding="utf-8"))

    stats = {
        "last_time_s": float(t_disp[-1]),
        "target_time_s": 204.8,
        "progress_percent": float(t_disp[-1] / 204.8 * 100.0),
        "max_disp_m": float(np.nanmax(disp_env)),
        "max_vel_mps": float(np.nanmax(vel_env)),
        "max_acc_mps2": float(np.nanmax(acc_env)),
        "force_log_rows": int(force.shape[0]),
        "max_total_explicit_force_N": float(np.nanmax(force[:, 1])),
        "max_element_explicit_force_N": float(np.nanmax(force[:, 2])),
        "min_xi_total": float(np.nanmin(damping[:, 3])),
        "negative_xi_fraction_log_rows": float(np.mean(damping[:, 3] < 0.0)),
        "duplicate_time_fraction": float(summary["time_repetition"]["duplicate_time_fraction"]),
        "max_duplicate_count": int(summary["time_repetition"]["max_duplicate_count"]),
    }
    (OUT / "typical_explicit_galloping_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")

    plt.figure(figsize=(10, 6))
    plt.plot(t_disp, disp_env, label="displacement envelope (m)")
    plt.plot(t_vel, vel_env, label="velocity envelope (m/s)")
    plt.yscale("log")
    plt.xlabel("time (s)")
    plt.ylabel("log envelope")
    plt.title("Typical explicit galloping response envelopes")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "response_envelopes_log.png", dpi=180)
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.plot(force[:, 0], force[:, 1], label="total |F_aero,damp| (N)")
    plt.plot(force[:, 0], force[:, 2], label="max element |F_aero,damp| (N)")
    plt.yscale("symlog", linthresh=1.0)
    plt.xlabel("time (s)")
    plt.ylabel("force (N), symlog")
    plt.title("Explicit aerodynamic damping force")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "explicit_force_log.png", dpi=180)
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.scatter(damping[:, 0], damping[:, 3], s=2, alpha=0.25)
    plt.axhline(0.0, color="black", linewidth=1)
    plt.xlabel("time (s)")
    plt.ylabel("xi_total")
    plt.title("Time-resolved total damping indicator")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT / "xi_total_scatter.png", dpi=180)
    plt.close()

    # strong_response_windows.csv is written with header by the diagnosis tool.
    import csv

    win_rows = []
    with (RUN / "strong_response_diagnosis" / "strong_response_windows.csv").open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            win_rows.append(row)

    md = [
        "# Typical Explicit Galloping Analysis",
        "",
        "## Run",
        "",
        "- Geometry: L = 322.8 m, Sag = 10.48 m.",
        "- Wind/force input: FORCE_3 / SIM1.",
        "- Time step target: dt = 0.05 s, npt = 4096, target = 204.8 s.",
        "- Active mechanism: global structural Rayleigh damping plus explicit velocity-dependent aerodynamic damping force, scale = 1.0.",
        "",
        "## Key Numbers",
        "",
        f"- Last recorded time: `{stats['last_time_s']:.6f} s` ({stats['progress_percent']:.2f}% of target).",
        f"- Max displacement envelope: `{stats['max_disp_m']:.6g} m`.",
        f"- Max velocity envelope: `{stats['max_vel_mps']:.6g} m/s`.",
        f"- Max acceleration envelope: `{stats['max_acc_mps2']:.6g} m/s^2`.",
        f"- Max total explicit aerodynamic damping force: `{stats['max_total_explicit_force_N']:.6g} N`.",
        f"- Min recorded xi_total: `{stats['min_xi_total']:.6g}`.",
        f"- Negative xi_total fraction in damping log rows: `{stats['negative_xi_fraction_log_rows']:.3f}`.",
        f"- Duplicate-time fraction: `{stats['duplicate_time_fraction']:.3f}`; max duplicate count: `{stats['max_duplicate_count']}`.",
        "",
        "## Window Progression",
        "",
        "| Window (s) | p95 disp | growth vs base | xi min | xi negative fraction | p95 velocity | max acceleration |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in win_rows[-8:]:
        md.append(
            "| {t0}-{t1} | {p95} | {growth_base_p95} | {xi_min} | {xi_negative_fraction} | {vel_p95} | {acc_max} |".format(
                t0=row["t0"],
                t1=row["t1"],
                p95=row["p95"],
                growth_base_p95=row["growth_base_p95"],
                xi_min=row["xi_min"],
                xi_negative_fraction=row["xi_negative_fraction"],
                vel_p95=row["vel_p95"],
                acc_max=row["acc_max"],
            )
        )
    md.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Galloping mechanism is active: negative total damping appears early and persists in substantial time-window fractions.",
            "- The explicit aerodynamic damping force is nonzero and grows with the response, which confirms that the galloping energy-transfer mechanism enters the time-domain equation.",
            "- The excessive response is still present, but now it is consistent with active aerodynamic negative damping rather than an unexplained structural-only instability.",
            "- The run did not reach 204.8 s. It was externally interrupted at 20 minutes after the response entered a severe nonlinear/substepping state near 72.28 s.",
            "",
            "## Figures",
            "",
            "- `response_envelopes_log.png`",
            "- `explicit_force_log.png`",
            "- `xi_total_scatter.png`",
        ]
    )
    (OUT / "typical_explicit_galloping_analysis.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(OUT / "typical_explicit_galloping_analysis.md")


if __name__ == "__main__":
    main()
