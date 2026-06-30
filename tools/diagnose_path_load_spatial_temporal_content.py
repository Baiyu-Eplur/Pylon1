from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "output" / "diagnostics" / "cable_rod_long_test" / "calibrated_cable_rod_node_balance_72s_v2" / "run"
FORCE_DIR = ROOT / "data" / "forces" / "FORCE_3" / "SIM1"
OUT_DIR = ROOT / "output" / "diagnostics" / "cable_rod_long_test" / "comparison" / "path_load_spatial_temporal_diagnostic"

DT = 0.05
NODES = 101
TARGET_SECONDS = 72.0
N_STEPS = int(TARGET_SECONDS / DT) + 1


def load_node_vector(node: int, suffix: str, n: int = N_STEPS) -> np.ndarray:
    path = FORCE_DIR / f"NODE_{node}_{suffix}.txt"
    return np.loadtxt(path, max_rows=n)


def load_path_force_matrix() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    fy = []
    fz = []
    wind_h = []
    wind_v = []
    for node in range(1, NODES + 1):
        h_drag = load_node_vector(node, "H_drag")
        h_lift = load_node_vector(node, "H_lift")
        v_drag = load_node_vector(node, "V_drag")
        v_lift = load_node_vector(node, "V_lift")
        # OpenSees applies these kN-equivalent files with factor 1000.
        fy.append(1000.0 * (h_drag + v_lift))
        fz.append(1000.0 * (h_lift + v_drag))
        wind_h.append(load_node_vector(node, "wind_H"))
        wind_v.append(load_node_vector(node, "wind_V"))
    return np.asarray(fy).T, np.asarray(fz).T, np.asarray(wind_h).T, np.asarray(wind_v).T


def load_response(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    raw = np.loadtxt(path)
    time = raw[:, 0]
    data = raw[:, 1:].reshape(raw.shape[0], NODES, 3)
    return time, data[:, :, 1], data[:, :, 2]


def spatial_spectrum_fraction(field: np.ndarray, cut_index: int) -> np.ndarray:
    demeaned = field - field.mean(axis=1, keepdims=True)
    spec = np.abs(np.fft.rfft(demeaned, axis=1)) ** 2
    total = spec[:, 1:].sum(axis=1)
    high = spec[:, cut_index:].sum(axis=1)
    return np.divide(high, total, out=np.zeros_like(high), where=total > 0)


def temporal_high_frequency_fraction(series: np.ndarray, dt: float, f_cut: float) -> float:
    x = series - np.mean(series)
    spec = np.abs(np.fft.rfft(x)) ** 2
    freqs = np.fft.rfftfreq(len(x), dt)
    total = spec[1:].sum()
    if total <= 0:
        return 0.0
    return float(spec[freqs >= f_cut].sum() / total)


def adjacent_corr(field: np.ndarray) -> np.ndarray:
    corrs = []
    for i in range(field.shape[1] - 1):
        a = field[:, i] - field[:, i].mean()
        b = field[:, i + 1] - field[:, i + 1].mean()
        den = np.sqrt(np.sum(a * a) * np.sum(b * b))
        corrs.append(float(np.sum(a * b) / den) if den > 0 else np.nan)
    return np.asarray(corrs)


def adjacent_diff_ratio(field: np.ndarray) -> np.ndarray:
    rms_field = np.sqrt(np.mean((field - field.mean(axis=1, keepdims=True)) ** 2, axis=1))
    rms_diff = np.sqrt(np.mean(np.diff(field, axis=1) ** 2, axis=1))
    return np.divide(rms_diff, rms_field, out=np.zeros_like(rms_diff), where=rms_field > 0)


def summarize_time_window(name: str, time: np.ndarray, values: np.ndarray) -> dict[str, float]:
    windows = {
        "0_60": (0.0, 60.0),
        "66_69p5": (66.0, 69.5),
        "68_69p1": (68.0, 69.1),
    }
    out: dict[str, float] = {}
    for suffix, (a, b) in windows.items():
        mask = (time >= a) & (time <= b)
        if mask.any():
            out[f"{name}_{suffix}_mean"] = float(np.nanmean(values[mask]))
            out[f"{name}_{suffix}_max"] = float(np.nanmax(values[mask]))
    return out


def find_local_max_times(time: np.ndarray, values: np.ndarray, top_n: int = 10) -> list[dict[str, float]]:
    idx = np.argsort(values)[-top_n:][::-1]
    return [{"time": float(time[i]), "value": float(values[i])} for i in idx]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    time = np.arange(N_STEPS) * DT
    fy, fz, wind_h, wind_v = load_path_force_matrix()
    resp_time, uy, uz = load_response(RUN_DIR / "Dynamic.out")
    _, ay, az = load_response(RUN_DIR / "Accel.out")

    response_time = resp_time
    # Force files start at t=0; OpenSees output starts after first successful step.
    force_for_response = slice(1, 1 + len(response_time))

    force_metrics = {
        "fy_spatial_high_k_gt_12": spatial_spectrum_fraction(fy, 13),
        "fz_spatial_high_k_gt_12": spatial_spectrum_fraction(fz, 13),
        "fy_spatial_high_k_gt_25": spatial_spectrum_fraction(fy, 26),
        "fz_spatial_high_k_gt_25": spatial_spectrum_fraction(fz, 26),
        "fy_adjacent_diff_ratio": adjacent_diff_ratio(fy),
        "fz_adjacent_diff_ratio": adjacent_diff_ratio(fz),
        "wind_h_adjacent_diff_ratio": adjacent_diff_ratio(wind_h),
        "wind_v_adjacent_diff_ratio": adjacent_diff_ratio(wind_v),
    }

    resp_metrics = {
        "uy_spatial_high_k_gt_12": spatial_spectrum_fraction(uy, 13),
        "uz_spatial_high_k_gt_12": spatial_spectrum_fraction(uz, 13),
        "ay_spatial_high_k_gt_12": spatial_spectrum_fraction(ay, 13),
        "az_spatial_high_k_gt_12": spatial_spectrum_fraction(az, 13),
        "ay_adjacent_diff_ratio": adjacent_diff_ratio(ay),
        "az_adjacent_diff_ratio": adjacent_diff_ratio(az),
    }

    summary: dict[str, object] = {
        "force_dir": str(FORCE_DIR),
        "run_dir": str(RUN_DIR),
        "dt": DT,
        "nodes": NODES,
        "duration_s": TARGET_SECONDS,
        "modal_simple": (RUN_DIR / "modal_simple.out").read_text(encoding="utf-8").strip(),
        "adjacent_correlation": {
            "fy_mean": float(np.nanmean(adjacent_corr(fy))),
            "fy_min": float(np.nanmin(adjacent_corr(fy))),
            "fz_mean": float(np.nanmean(adjacent_corr(fz))),
            "fz_min": float(np.nanmin(adjacent_corr(fz))),
            "wind_h_mean": float(np.nanmean(adjacent_corr(wind_h))),
            "wind_h_min": float(np.nanmin(adjacent_corr(wind_h))),
            "wind_v_mean": float(np.nanmean(adjacent_corr(wind_v))),
            "wind_v_min": float(np.nanmin(adjacent_corr(wind_v))),
        },
        "temporal_high_frequency_fraction_gt_2Hz": {},
        "metrics": {},
        "top_times": {},
        "interpretation_flags": {},
    }

    for label, matrix in {
        "fy_node52": fy[:, 51],
        "fz_node52": fz[:, 51],
        "fy_midspan_mean": fy[:, 45:56].mean(axis=1),
        "fz_midspan_mean": fz[:, 45:56].mean(axis=1),
        "wind_h_node52": wind_h[:, 51],
        "wind_v_node52": wind_v[:, 51],
    }.items():
        summary["temporal_high_frequency_fraction_gt_2Hz"][label] = temporal_high_frequency_fraction(matrix, DT, 2.0)

    for name, values in force_metrics.items():
        summary["metrics"].update(summarize_time_window(name, time, values))
        summary["top_times"][name] = find_local_max_times(time, values, 6)

    for name, values in resp_metrics.items():
        summary["metrics"].update(summarize_time_window(name, response_time, values))
        summary["top_times"][name] = find_local_max_times(response_time, values, 6)

    # Correlate force roughness with acceleration roughness at the actual
    # OpenSees output times. The solver can reduce the increment after onset,
    # so the response record is not guaranteed to have the same length as the
    # original Path-load sampling grid.
    fy_diff = np.interp(response_time, time, force_metrics["fy_adjacent_diff_ratio"])
    fz_diff = np.interp(response_time, time, force_metrics["fz_adjacent_diff_ratio"])
    ay_diff = resp_metrics["ay_adjacent_diff_ratio"]
    az_diff = resp_metrics["az_adjacent_diff_ratio"]
    summary["roughness_correlations"] = {
        "fy_diff_vs_ay_diff": float(np.corrcoef(fy_diff, ay_diff)[0, 1]),
        "fz_diff_vs_az_diff": float(np.corrcoef(fz_diff, az_diff)[0, 1]),
        "fy_diff_vs_az_diff": float(np.corrcoef(fy_diff, az_diff)[0, 1]),
        "fz_diff_vs_ay_diff": float(np.corrcoef(fz_diff, ay_diff)[0, 1]),
    }

    summary["interpretation_flags"] = {
        "force_adjacent_corr_low": bool(summary["adjacent_correlation"]["fy_min"] < 0.3 or summary["adjacent_correlation"]["fz_min"] < 0.3),
        "force_high_spatial_content_near_onset": bool(
            summary["metrics"]["fy_spatial_high_k_gt_12_68_69p1_mean"] > 0.05
            or summary["metrics"]["fz_spatial_high_k_gt_12_68_69p1_mean"] > 0.05
        ),
        "response_high_spatial_content_grows_near_onset": bool(
            summary["metrics"]["ay_spatial_high_k_gt_12_68_69p1_mean"]
            > max(1.5 * summary["metrics"]["ay_spatial_high_k_gt_12_0_60_mean"], 1.0e-6)
            or summary["metrics"]["az_spatial_high_k_gt_12_68_69p1_mean"]
            > max(1.5 * summary["metrics"]["az_spatial_high_k_gt_12_0_60_mean"], 1.0e-6)
        ),
    }

    (OUT_DIR / "path_load_spatial_temporal_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    metric_df = pd.DataFrame({"time": time, **force_metrics})
    metric_df.to_csv(OUT_DIR / "force_spatial_temporal_metrics.csv", index=False)
    resp_df = pd.DataFrame({"time": response_time, **resp_metrics})
    resp_df.to_csv(OUT_DIR / "response_spatial_metrics.csv", index=False)

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=False)
    axes[0].plot(time, force_metrics["fy_adjacent_diff_ratio"], label="Fy adjacent-diff ratio")
    axes[0].plot(time, force_metrics["fz_adjacent_diff_ratio"], label="Fz adjacent-diff ratio")
    axes[0].axvspan(68.0, 69.1, color="tab:red", alpha=0.12, label="onset window")
    axes[0].set_ylabel("roughness ratio")
    axes[0].set_xlim(0, 72)
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=9)

    axes[1].plot(time, force_metrics["fy_spatial_high_k_gt_12"], label="Fy high-k fraction")
    axes[1].plot(time, force_metrics["fz_spatial_high_k_gt_12"], label="Fz high-k fraction")
    axes[1].axvspan(68.0, 69.1, color="tab:red", alpha=0.12)
    axes[1].set_ylabel("spatial PSD fraction")
    axes[1].set_xlim(0, 72)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=9)

    axes[2].plot(response_time, resp_metrics["ay_adjacent_diff_ratio"], label="ay adjacent-diff ratio")
    axes[2].plot(response_time, resp_metrics["az_adjacent_diff_ratio"], label="az adjacent-diff ratio")
    axes[2].axvspan(68.0, 69.1, color="tab:red", alpha=0.12)
    axes[2].set_xlabel("time (s)")
    axes[2].set_ylabel("response roughness")
    axes[2].set_xlim(0, 72)
    axes[2].grid(True, alpha=0.3)
    axes[2].legend(fontsize=9)
    fig.suptitle("Path-load and response spatial roughness diagnostics")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "path_load_response_roughness_timeseries.png", dpi=200)
    plt.close(fig)

    nodes = np.arange(1, NODES + 1)
    idx68 = int(round(68.25 / DT))
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    for offset, alpha in [(-2, 0.35), (-1, 0.55), (0, 0.9), (1, 0.55), (2, 0.35)]:
        i = idx68 + offset
        axes[0].plot(nodes, fy[i], alpha=alpha, label=f"t={time[i]:.2f}s")
        axes[1].plot(nodes, fz[i], alpha=alpha, label=f"t={time[i]:.2f}s")
    axes[0].set_ylabel("Fy Path load (N)")
    axes[1].set_ylabel("Fz Path load (N)")
    axes[1].set_xlabel("node")
    for ax in axes:
        ax.grid(True, alpha=0.3)
        ax.legend(ncol=5, fontsize=8)
        ax.axvline(52, color="k", linestyle="--", linewidth=1)
    fig.suptitle("Spatial Path-load profiles around 68.25 s")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "path_load_spatial_profiles_around_68p25s.png", dpi=200)
    plt.close(fig)

    print(json.dumps(summary["interpretation_flags"], indent=2))
    print(json.dumps(summary["roughness_correlations"], indent=2))
    print(f"Wrote diagnostics to {OUT_DIR}")


if __name__ == "__main__":
    main()
