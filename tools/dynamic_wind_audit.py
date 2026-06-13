from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cable_analyser.config_loader import load_config
from cable_analyser.geometry import CableGeometry


def load_vector(path: Path, max_points: int | None = None) -> np.ndarray:
    data = np.loadtxt(path, max_rows=max_points)
    return np.atleast_1d(data).astype(float)


def one_sided_psd(x: np.ndarray, dt: float) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray(x, dtype=float)
    x = x - np.mean(x)
    n = len(x)
    freq = np.fft.rfftfreq(n, dt)
    fft = np.fft.rfft(x)
    psd = (dt / n) * np.abs(fft) ** 2
    if n > 1:
        psd[1:-1] *= 2.0
    return freq, psd


def kaimal_psd(freq: np.ndarray, mean_u: float, height: float, u_star: float) -> np.ndarray:
    # Common longitudinal Kaimal form used for atmospheric boundary layer checks.
    # f*S(f)/u_*^2 = 200*n / (1 + 50*n)^(5/3), n = f*z/U
    n = np.maximum(freq * height / max(mean_u, 1e-12), 1e-12)
    return (u_star**2 / np.maximum(freq, 1e-12)) * (200.0 * n) / (1.0 + 50.0 * n) ** (5.0 / 3.0)


def spectral_log_rmse(freq: np.ndarray, psd: np.ndarray, target: np.ndarray) -> float:
    mask = (freq > 0.01) & np.isfinite(psd) & np.isfinite(target) & (psd > 0) & (target > 0)
    if mask.sum() < 10:
        return float("nan")
    return float(np.sqrt(np.mean((np.log10(psd[mask]) - np.log10(target[mask])) ** 2)))


def mag_squared_coherence(x: np.ndarray, y: np.ndarray, dt: float, segment_length: int = 4096) -> tuple[np.ndarray, np.ndarray]:
    n = min(len(x), len(y))
    x = x[:n] - np.mean(x[:n])
    y = y[:n] - np.mean(y[:n])
    if n < segment_length:
        segment_length = n
    step = segment_length // 2
    window = np.hanning(segment_length)
    sxx = syy = sxy = None
    count = 0
    for start in range(0, n - segment_length + 1, step):
        xs = x[start:start + segment_length] * window
        ys = y[start:start + segment_length] * window
        fx = np.fft.rfft(xs)
        fy = np.fft.rfft(ys)
        cur_sxx = fx * np.conj(fx)
        cur_syy = fy * np.conj(fy)
        cur_sxy = fx * np.conj(fy)
        if sxx is None:
            sxx = cur_sxx
            syy = cur_syy
            sxy = cur_sxy
        else:
            sxx += cur_sxx
            syy += cur_syy
            sxy += cur_sxy
        count += 1
    if count == 0:
        return np.array([]), np.array([])
    sxx = sxx / count
    syy = syy / count
    sxy = sxy / count
    coh = np.abs(sxy) ** 2 / np.maximum(np.real(sxx * syy), 1e-30)
    freq = np.fft.rfftfreq(segment_length, dt)
    return freq, np.real(coh)


def summarize_vector(v: np.ndarray) -> dict:
    return {
        "n": int(len(v)),
        "mean": float(np.mean(v)),
        "std": float(np.std(v, ddof=1)) if len(v) > 1 else 0.0,
        "min": float(np.min(v)),
        "max": float(np.max(v)),
    }


def build_audit(config_path: Path, support_height: float, z0: float, kappa: float, max_points: int | None) -> dict:
    cfg = load_config(config_path)
    geo = CableGeometry(cfg).generate()
    n_nodes = len(geo["x"])
    dt = float(cfg["time_history"]["dt"])
    expected_npt = int(cfg["time_history"]["npt"])
    wind_dir = ROOT / cfg["paths"]["wind_dir"]
    force_case = ROOT / cfg["paths"]["forces_dir"] / cfg["time_history"]["folder_1"][0] / cfg["time_history"]["folder_2"][0]
    time_path = ROOT / "data" / "aero_coeffs" / "time.txt"
    time = load_vector(time_path, max_points=max_points)
    if len(time) > 1:
        time_dt_median = float(np.median(np.diff(time)))
    else:
        time_dt_median = float("nan")

    node_ids = list(range(1, n_nodes + 1))
    mean_h = []
    std_h = []
    mean_v = []
    std_v = []
    heights = []
    lengths = []
    psd_checks = []
    force_checks = []

    sample_nodes = sorted(set([1, max(1, n_nodes // 4), max(1, n_nodes // 2 + 1), max(1, 3 * n_nodes // 4), n_nodes]))

    for node_id in node_ids:
        wh = load_vector(wind_dir / f"NODE_{node_id}_wind_H.txt", max_points=max_points)
        wv = load_vector(wind_dir / f"NODE_{node_id}_wind_V.txt", max_points=max_points)
        lengths.append(len(wh))
        mean_h.append(float(np.mean(wh)))
        std_h.append(float(np.std(wh, ddof=1)))
        mean_v.append(float(np.mean(wv)))
        std_v.append(float(np.std(wv, ddof=1)))
        heights.append(float(support_height + geo["z"][node_id - 1]))

        if node_id in sample_nodes:
            u_star = mean_h[-1] * kappa / math.log(max(heights[-1], z0 * 1.01) / z0)
            freq, psd = one_sided_psd(wh, dt)
            target = kaimal_psd(freq, mean_h[-1], heights[-1], u_star)
            psd_checks.append(
                {
                    "node": node_id,
                    "height_m": heights[-1],
                    "mean_H_mps": mean_h[-1],
                    "std_H_mps": std_h[-1],
                    "inferred_u_star_mps": u_star,
                    "kaimal_log10_psd_rmse": spectral_log_rmse(freq, psd, target),
                }
            )

        h_drag_path = force_case / f"NODE_{node_id}_H_drag.txt"
        if h_drag_path.exists():
            h_drag = load_vector(h_drag_path, max_points=max_points)
            corr = float(np.corrcoef(wh[: len(h_drag)] ** 2, h_drag[: len(wh)])[0, 1])
            force_checks.append(
                {
                    "node": node_id,
                    "H_drag_n": int(len(h_drag)),
                    "H_drag_mean_file_units": float(np.mean(h_drag)),
                    "H_drag_std_file_units": float(np.std(h_drag, ddof=1)),
                    "corr_H_drag_with_wind_H_squared": corr,
                }
            )

    mean_h_arr = np.array(mean_h)
    heights_arr = np.array(heights)
    u_star_nodes = mean_h_arr * kappa / np.log(np.maximum(heights_arr, z0 * 1.01) / z0)

    coherence_checks = []
    for pair in [(1, n_nodes // 2 + 1), (1, n_nodes), (n_nodes // 2 + 1, n_nodes)]:
        a, b = pair
        xa = load_vector(wind_dir / f"NODE_{a}_wind_H.txt", max_points=max_points)
        xb = load_vector(wind_dir / f"NODE_{b}_wind_H.txt", max_points=max_points)
        freq, coh = mag_squared_coherence(xa, xb, dt)
        if len(freq):
            band = (freq >= 0.02) & (freq <= 1.0)
            coherence_checks.append(
                {
                    "node_pair": [a, b],
                    "spanwise_distance_m": float(abs(geo["x"][b - 1] - geo["x"][a - 1])),
                    "mean_coherence_0p02_to_1Hz": float(np.mean(coh[band])) if band.any() else float("nan"),
                    "coherence_at_0p1Hz": float(coh[np.argmin(np.abs(freq - 0.1))]),
                    "coherence_at_0p5Hz": float(coh[np.argmin(np.abs(freq - 0.5))]),
                }
            )

    return {
        "config": str(config_path.relative_to(ROOT)),
        "support_height_m": support_height,
        "roughness_z0_m": z0,
        "kappa": kappa,
        "dt_config_s": dt,
        "npt_config": expected_npt,
        "time_file": {
            "path": str(time_path.relative_to(ROOT)),
            "n": int(len(time)),
            "dt_median_s": time_dt_median,
            "duration_s": float(time[-1] - time[0] + time_dt_median) if len(time) > 1 else 0.0,
            "matches_config_dt": bool(abs(time_dt_median - dt) < 1e-12),
            "matches_config_npt": bool(len(time) == expected_npt),
        },
        "wind_profile": {
            "nodes": n_nodes,
            "file_lengths_unique": sorted(set(lengths)),
            "mean_H_summary_mps": summarize_vector(mean_h_arr),
            "std_H_summary_mps": summarize_vector(np.array(std_h)),
            "mean_V_summary_mps": summarize_vector(np.array(mean_v)),
            "inferred_u_star_summary_mps": summarize_vector(u_star_nodes),
            "height_range_m": [float(np.min(heights_arr)), float(np.max(heights_arr))],
        },
        "psd_checks": psd_checks,
        "coherence_checks": coherence_checks,
        "force_checks_sample": [
            item for item in force_checks if item["node"] in sample_nodes
        ],
    }


def write_markdown(audit: dict, path: Path) -> None:
    time = audit["time_file"]
    wp = audit["wind_profile"]
    lines = [
        "# Dynamic Wind Response Audit",
        "",
        f"Config: `{audit['config']}`",
        "",
        "## Time Base",
        "",
        f"- Config dt/npt: `{audit['dt_config_s']}` s / `{audit['npt_config']}`",
        f"- Time file rows: `{time['n']}`",
        f"- Time file median dt: `{time['dt_median_s']}` s",
        f"- Duration: `{time['duration_s']}` s",
        f"- Matches config dt: `{time['matches_config_dt']}`",
        f"- Matches config npt: `{time['matches_config_npt']}`",
        "",
        "## Wind Profile",
        "",
        f"- Node count: `{wp['nodes']}`",
        f"- Unique wind-file lengths: `{wp['file_lengths_unique']}`",
        f"- Height range: `{wp['height_range_m']}` m",
        f"- Mean horizontal wind summary (m/s): `{wp['mean_H_summary_mps']}`",
        f"- Horizontal turbulence std summary (m/s): `{wp['std_H_summary_mps']}`",
        f"- Mean vertical wind summary (m/s): `{wp['mean_V_summary_mps']}`",
        f"- Inferred friction velocity summary (m/s): `{wp['inferred_u_star_summary_mps']}`",
        "",
        "## Kaimal PSD Spot Checks",
        "",
    ]
    for item in audit["psd_checks"]:
        lines.append(
            f"- Node `{item['node']}`: height `{item['height_m']:.3f}` m, "
            f"mean H `{item['mean_H_mps']:.3f}` m/s, "
            f"u* `{item['inferred_u_star_mps']:.4f}` m/s, "
            f"log10 PSD RMSE `{item['kaimal_log10_psd_rmse']:.4f}`"
        )
    lines.extend(["", "## Davenport-Like Coherence Spot Checks", ""])
    for item in audit["coherence_checks"]:
        lines.append(
            f"- Nodes `{item['node_pair']}` distance `{item['spanwise_distance_m']:.3f}` m: "
            f"mean coherence 0.02-1 Hz `{item['mean_coherence_0p02_to_1Hz']:.4f}`, "
            f"coh@0.1 Hz `{item['coherence_at_0p1Hz']:.4f}`, "
            f"coh@0.5 Hz `{item['coherence_at_0p5Hz']:.4f}`"
        )
    lines.extend(["", "## Force/Wind Consistency Spot Checks", ""])
    for item in audit["force_checks_sample"]:
        lines.append(
            f"- Node `{item['node']}` H_drag rows `{item['H_drag_n']}`, "
            f"mean `{item['H_drag_mean_file_units']:.6g}`, "
            f"corr(H_drag, wind_H^2) `{item['corr_H_drag_with_wind_H_squared']:.4f}`"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/timur_baseline.yaml")
    parser.add_argument("--out-dir", default="output/wind_audit/timur_baseline")
    parser.add_argument("--support-height", type=float, default=49.4)
    parser.add_argument("--roughness-z0", type=float, default=0.05)
    parser.add_argument("--kappa", type=float, default=0.387)
    parser.add_argument("--max-points", type=int, default=0)
    args = parser.parse_args()

    max_points = args.max_points if args.max_points > 0 else None
    config_path = (ROOT / args.config).resolve()
    out_dir = (ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    audit = build_audit(
        config_path=config_path,
        support_height=args.support_height,
        z0=args.roughness_z0,
        kappa=args.kappa,
        max_points=max_points,
    )
    (out_dir / "dynamic_wind_audit.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    write_markdown(audit, out_dir / "dynamic_wind_audit.md")
    print(f"Wrote {out_dir / 'dynamic_wind_audit.md'}")


if __name__ == "__main__":
    main()
