from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

from src.cable_analyser.geometry import CableGeometry


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "output" / "diagnostics" / "typical_incremental_quasi_steady_formal_no_stop"
CONFIG = CASE_DIR / "typical_L322P8_H10P48_U0P6_incremental_quasi_steady_formal_no_stop.yaml"
RUN_DIR = CASE_DIR / "run"
MONITOR_DIR = CASE_DIR / "point_monitoring"
FORCE_DIR = ROOT / "data" / "forces" / "FORCE_3" / "SIM1"
OUT_DIR = CASE_DIR / "analysis" / "after_40s_motion_force"


RHO = 1.293
B = 0.02862
TRIBUTARY = {
    26: 3.23479091521,
    51: 3.22800271433,
    76: 3.23425854844,
}
POINTS = [
    ("1/4 span", 26, MONITOR_DIR / "quarter_1_node_26_timeseries.csv"),
    ("midspan", 51, MONITOR_DIR / "midspan_node_51_timeseries.csv"),
    ("3/4 span", 76, MONITOR_DIR / "quarter_3_node_76_timeseries.csv"),
]


def point_power(arr: np.ndarray, node: int) -> dict[str, np.ndarray]:
    t = arr["time_s"]
    vx = arr["vel_transverse_x_mps"]
    vz = arr["vel_vertical_z_mps"]
    wx = arr["wind_x_mps"]
    wz = arr["wind_z_mps"]
    relx = wx - vx
    relz = wz - vz
    u_rel = np.sqrt(relx**2 + relz**2)
    ex = np.divide(relx, u_rel, out=np.zeros_like(u_rel), where=u_rel > 1e-12)
    ez = np.divide(relz, u_rel, out=np.zeros_like(u_rel), where=u_rel > 1e-12)
    q_area = 0.5 * RHO * u_rel**2 * (math.pi * B * TRIBUTARY[node] / 2.0)
    cd = arr["C_D"]
    cl = arr["C_L"]
    drag_x = q_area * cd * ex
    drag_z = q_area * cd * ez
    lift_x = -q_area * cl * ez
    lift_z = q_area * cl * ex
    cur_x = drag_x + lift_x
    cur_z = drag_z + lift_z
    h_drag = 1000.0 * np.loadtxt(FORCE_DIR / f"NODE_{node}_H_drag.txt", max_rows=len(t))
    h_lift = 1000.0 * np.loadtxt(FORCE_DIR / f"NODE_{node}_H_lift.txt", max_rows=len(t))
    v_drag = 1000.0 * np.loadtxt(FORCE_DIR / f"NODE_{node}_V_drag.txt", max_rows=len(t))
    v_lift = 1000.0 * np.loadtxt(FORCE_DIR / f"NODE_{node}_V_lift.txt", max_rows=len(t))
    ref_x = h_drag + v_lift
    ref_z = h_lift + v_drag
    return {
        "time": t,
        "speed": np.sqrt(vx**2 + vz**2),
        "disp": np.sqrt(arr["disp_transverse_x_m"] ** 2 + arr["disp_vertical_z_m"] ** 2),
        "u_rel": u_rel,
        "alpha": arr["alpha_lookup_deg_unclipped"],
        "p_current": cur_x * vx + cur_z * vz,
        "p_delta": (cur_x - ref_x) * vx + (cur_z - ref_z) * vz,
        "p_drag": drag_x * vx + drag_z * vz,
        "p_lift": lift_x * vx + lift_z * vz,
    }


def element_strain_series(cfg: dict) -> dict[str, np.ndarray]:
    geo = CableGeometry(cfg).generate()
    x0 = np.asarray(geo["x"], dtype=float)
    y0 = np.asarray(geo["y"], dtype=float)
    z0 = np.asarray(geo["z"], dtype=float)
    initial_lengths = np.asarray(geo["dx"], dtype=float)
    dyn = np.loadtxt(RUN_DIR / "Dynamic.out")
    time = dyn[:, 0]
    n_nodes = len(x0)
    disp = dyn[:, 1:].reshape((len(time), n_nodes, 3))
    x = x0[None, :] + disp[:, :, 0]
    y = y0[None, :] + disp[:, :, 1]
    z = z0[None, :] + disp[:, :, 2]
    lengths = np.sqrt(np.diff(x, axis=1) ** 2 + np.diff(y, axis=1) ** 2 + np.diff(z, axis=1) ** 2)
    strain = (lengths - initial_lengths[None, :]) / initial_lengths[None, :]
    idx = np.nanargmax(np.abs(strain), axis=1)
    max_abs = np.nanmax(np.abs(strain), axis=1)
    signed = strain[np.arange(len(time)), idx]
    return {
        "time": time,
        "max_abs_strain": max_abs,
        "signed_strain_at_max": signed,
        "element_at_max": idx + 1,
    }


def moving_mean(x: np.ndarray, n: int = 20) -> np.ndarray:
    if len(x) < n:
        return x
    kernel = np.ones(n) / n
    return np.convolve(x, kernel, mode="same")


def main() -> None:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    force_log = np.loadtxt(RUN_DIR / "incremental_quasi_steady_aero_force_log.txt", skiprows=1)
    strain = element_strain_series(cfg)
    point_data = [(name, node, point_power(np.genfromtxt(path, delimiter=",", names=True), node)) for name, node, path in POINTS]

    mask_force = force_log[:, 0] >= 40
    mask_strain = strain["time"] >= 40

    fig, axes = plt.subplots(5, 1, figsize=(11, 12), sharex=True)
    axes[0].plot(force_log[mask_force, 0], force_log[mask_force, 4], lw=0.9, label="total |Delta F|")
    axes[0].plot(force_log[mask_force, 0], force_log[mask_force, 3], lw=0.9, label="F_current")
    axes[0].set_ylabel("force sum (N)")
    axes[0].legend(loc="upper left")

    axes[1].plot(force_log[mask_force, 0], force_log[mask_force, 9], lw=0.9, label="max alpha")
    axes[1].axhline(29.9, color="black", lw=0.8, ls="--", label="table limit")
    axes[1].set_ylabel("alpha (deg)")
    axes[1].legend(loc="upper left")

    axes[2].plot(strain["time"][mask_strain], strain["max_abs_strain"][mask_strain], lw=0.9, color="#8B2E2E")
    axes[2].axhline(cfg["material"]["rated_strength_N"] / (cfg["material"]["E"] * math.pi * cfg["material"]["Dia"] ** 2 / 4.0), color="black", lw=0.8, ls="--", label="rated strain")
    axes[2].set_ylabel("max |strain|")
    axes[2].legend(loc="upper left")

    for name, _node, data in point_data:
        mask = data["time"] >= 40
        axes[3].plot(data["time"][mask], data["speed"][mask], lw=0.9, label=name)
    axes[3].set_ylabel("point speed (m/s)")
    axes[3].legend(loc="upper left")

    for name, _node, data in point_data:
        mask = data["time"] >= 40
        axes[4].plot(data["time"][mask], moving_mean(data["p_delta"][mask], 30), lw=0.9, label=name)
    axes[4].axhline(0.0, color="black", lw=0.8)
    axes[4].set_ylabel("Delta F . v (W)")
    axes[4].set_xlabel("time (s)")
    axes[4].legend(loc="upper left")

    for ax in axes:
        ax.grid(True, color="#D8DEE8", linewidth=0.6)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "after_40s_force_motion_strain_overview.png", dpi=180)
    plt.close(fig)

    summaries = []
    windows = [(40, 50), (50, 58), (58, 65), (65, 75), (75, float(force_log[-1, 0]))]
    for start, end in windows:
        fmask = (force_log[:, 0] >= start) & (force_log[:, 0] < end)
        smask = (strain["time"] >= start) & (strain["time"] < end)
        row = {
            "window_s": [start, end],
            "delta_force_mean_N": float(np.mean(force_log[fmask, 4])),
            "delta_force_max_N": float(np.max(force_log[fmask, 4])),
            "max_alpha_max_deg": float(np.max(force_log[fmask, 9])),
            "max_abs_strain": float(np.max(strain["max_abs_strain"][smask])),
        }
        for name, _node, data in point_data:
            pmask = (data["time"] >= start) & (data["time"] < end)
            key = name.replace("/", "_").replace(" ", "_")
            row[f"{key}_speed_max_mps"] = float(np.max(data["speed"][pmask]))
            row[f"{key}_p_delta_mean_W"] = float(np.mean(data["p_delta"][pmask]))
            row[f"{key}_p_delta_positive_fraction"] = float(np.mean(data["p_delta"][pmask] > 0))
        summaries.append(row)

    (OUT_DIR / "after_40s_summary.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    print(json.dumps({"out_dir": str(OUT_DIR), "summaries": summaries}, indent=2))


if __name__ == "__main__":
    main()
