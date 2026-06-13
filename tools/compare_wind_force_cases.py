from __future__ import annotations

import argparse
import json
import math
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


def load_vector(path: Path, max_points: int | None = None) -> np.ndarray:
    return np.atleast_1d(np.loadtxt(path, max_rows=max_points)).astype(float)


def one_sided_psd(x: np.ndarray, dt: float) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray(x, dtype=float) - float(np.mean(x))
    n = len(x)
    freq = np.fft.rfftfreq(n, dt)
    fft = np.fft.rfft(x)
    psd = (dt / n) * np.abs(fft) ** 2
    if n > 1:
        psd[1:-1] *= 2.0
    return freq, psd


def spectral_log_rmse(a: np.ndarray, b: np.ndarray) -> float:
    mask = np.isfinite(a) & np.isfinite(b) & (a > 0) & (b > 0)
    if int(mask.sum()) < 10:
        return float("nan")
    return float(np.sqrt(np.mean((np.log10(a[mask]) - np.log10(b[mask])) ** 2)))


def mag_squared_coherence(
    x: np.ndarray,
    y: np.ndarray,
    dt: float,
    segment_length: int = 1024,
) -> tuple[np.ndarray, np.ndarray]:
    n = min(len(x), len(y))
    x = x[:n] - np.mean(x[:n])
    y = y[:n] - np.mean(y[:n])
    if n < 32:
        return np.array([]), np.array([])
    segment_length = min(segment_length, n)
    step = max(1, segment_length // 2)
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
            sxx, syy, sxy = cur_sxx, cur_syy, cur_sxy
        else:
            sxx += cur_sxx
            syy += cur_syy
            sxy += cur_sxy
        count += 1
    if count == 0:
        return np.array([]), np.array([])
    coh = np.abs(sxy / count) ** 2 / np.maximum(
        np.real((sxx / count) * (syy / count)),
        1e-30,
    )
    return np.fft.rfftfreq(segment_length, dt), np.real(coh)


def summary(v: np.ndarray) -> dict[str, float | int]:
    return {
        "n": int(len(v)),
        "mean": float(np.mean(v)),
        "std": float(np.std(v, ddof=1)) if len(v) > 1 else 0.0,
        "min": float(np.min(v)),
        "max": float(np.max(v)),
    }


def rel_diff(new: float, base: float) -> float:
    return float((new - base) / base) if abs(base) > 1e-15 else float("nan")


def compare_component(
    base_dir: Path,
    new_dir: Path,
    node_ids: list[int],
    suffix: str,
    max_points: int | None,
) -> dict[str, Any]:
    rows = []
    for node_id in node_ids:
        base = load_vector(base_dir / f"NODE_{node_id}_{suffix}.txt", max_points=max_points)
        new = load_vector(new_dir / f"NODE_{node_id}_{suffix}.txt", max_points=max_points)
        n = min(len(base), len(new))
        base = base[:n]
        new = new[:n]
        base_mean = float(np.mean(base))
        new_mean = float(np.mean(new))
        base_std = float(np.std(base, ddof=1))
        new_std = float(np.std(new, ddof=1))
        corr = float(np.corrcoef(base, new)[0, 1]) if n > 2 else float("nan")
        rows.append(
            {
                "node": node_id,
                "n": int(n),
                "base_mean": base_mean,
                "new_mean": new_mean,
                "mean_rel_diff": rel_diff(new_mean, base_mean),
                "base_std": base_std,
                "new_std": new_std,
                "std_rel_diff": rel_diff(new_std, base_std),
                "corr_same_node": corr,
            }
        )
    return {
        "suffix": suffix,
        "rows": rows,
        "mean_rel_diff_abs_avg": float(np.mean([abs(r["mean_rel_diff"]) for r in rows])),
        "std_rel_diff_abs_avg": float(np.mean([abs(r["std_rel_diff"]) for r in rows])),
    }


def compare_cases(
    config_path: Path,
    base_force: str,
    base_sim: str,
    base_wind_dir: str,
    new_force: str,
    new_sim: str,
    new_wind_dir: str,
    max_points: int | None,
    support_elevation: float,
    kappa: float,
    z0: float,
) -> dict[str, Any]:
    cfg = load_config(config_path)
    geo = CableGeometry(cfg).generate()
    n_nodes = len(geo["x"])
    dt = float(cfg["time_history"]["dt"])
    base_force_dir = ROOT / cfg["paths"]["forces_dir"] / base_force / base_sim
    new_force_dir = ROOT / cfg["paths"]["forces_dir"] / new_force / new_sim
    base_wind = ROOT / base_wind_dir
    new_wind = ROOT / new_wind_dir
    sample_nodes = sorted(set([1, max(1, n_nodes // 4), n_nodes // 2 + 1, max(1, 3 * n_nodes // 4), n_nodes]))

    wind_rows = []
    psd_rows = []
    inferred_base = []
    inferred_new = []
    for node_id in sample_nodes:
        wh_base = load_vector(base_wind / f"NODE_{node_id}_wind_H.txt", max_points=max_points)
        wh_new = load_vector(new_wind / f"NODE_{node_id}_wind_H.txt", max_points=max_points)
        wv_base = load_vector(base_wind / f"NODE_{node_id}_wind_V.txt", max_points=max_points)
        wv_new = load_vector(new_wind / f"NODE_{node_id}_wind_V.txt", max_points=max_points)
        n = min(len(wh_base), len(wh_new))
        wh_base = wh_base[:n]
        wh_new = wh_new[:n]
        wv_base = wv_base[:n]
        wv_new = wv_new[:n]
        height = support_elevation + float(geo["z"][node_id - 1])
        ustar_base = float(np.mean(wh_base)) * kappa / math.log(height / z0)
        ustar_new = float(np.mean(wh_new)) * kappa / math.log(height / z0)
        inferred_base.append(ustar_base)
        inferred_new.append(ustar_new)
        wind_rows.append(
            {
                "node": node_id,
                "height_m": height,
                "H_mean_base": float(np.mean(wh_base)),
                "H_mean_new": float(np.mean(wh_new)),
                "H_mean_rel_diff": rel_diff(float(np.mean(wh_new)), float(np.mean(wh_base))),
                "H_std_base": float(np.std(wh_base, ddof=1)),
                "H_std_new": float(np.std(wh_new, ddof=1)),
                "H_std_rel_diff": rel_diff(float(np.std(wh_new, ddof=1)), float(np.std(wh_base, ddof=1))),
                "V_mean_base": float(np.mean(wv_base)),
                "V_mean_new": float(np.mean(wv_new)),
                "V_std_base": float(np.std(wv_base, ddof=1)),
                "V_std_new": float(np.std(wv_new, ddof=1)),
                "inferred_u_star_base": ustar_base,
                "inferred_u_star_new": ustar_new,
            }
        )
        freq_base, psd_base = one_sided_psd(wh_base, dt)
        freq_new, psd_new = one_sided_psd(wh_new, dt)
        n_freq = min(len(freq_base), len(freq_new))
        band = (freq_base[:n_freq] >= 0.02) & (freq_base[:n_freq] <= 2.0)
        psd_rows.append(
            {
                "node": node_id,
                "H_psd_log10_rmse_0p02_to_2Hz": spectral_log_rmse(psd_new[:n_freq][band], psd_base[:n_freq][band]),
            }
        )

    coherence_rows = []
    for a, b in [(1, n_nodes // 2 + 1), (1, n_nodes), (n_nodes // 2 + 1, n_nodes)]:
        base_a = load_vector(base_wind / f"NODE_{a}_wind_H.txt", max_points=max_points)
        base_b = load_vector(base_wind / f"NODE_{b}_wind_H.txt", max_points=max_points)
        new_a = load_vector(new_wind / f"NODE_{a}_wind_H.txt", max_points=max_points)
        new_b = load_vector(new_wind / f"NODE_{b}_wind_H.txt", max_points=max_points)
        fb, cb = mag_squared_coherence(base_a, base_b, dt)
        fn, cn = mag_squared_coherence(new_a, new_b, dt)
        n_freq = min(len(fb), len(fn))
        if n_freq:
            band = (fb[:n_freq] >= 0.02) & (fb[:n_freq] <= 1.0)
            coherence_rows.append(
                {
                    "pair": [a, b],
                    "base_mean_0p02_to_1Hz": float(np.mean(cb[:n_freq][band])) if np.any(band) else float("nan"),
                    "new_mean_0p02_to_1Hz": float(np.mean(cn[:n_freq][band])) if np.any(band) else float("nan"),
                }
            )

    component_rows = [
        compare_component(base_force_dir, new_force_dir, sample_nodes, suffix, max_points)
        for suffix in ("H_drag", "H_lift", "V_drag", "V_lift")
    ]
    return {
        "config": str(config_path.relative_to(ROOT)),
        "base": {
            "force_dir": str(base_force_dir.relative_to(ROOT)),
            "wind_dir": base_wind_dir,
        },
        "new": {
            "force_dir": str(new_force_dir.relative_to(ROOT)),
            "wind_dir": new_wind_dir,
        },
        "max_points": max_points,
        "sample_nodes": sample_nodes,
        "inferred_u_star_base": summary(np.array(inferred_base)),
        "inferred_u_star_new": summary(np.array(inferred_new)),
        "wind_rows": wind_rows,
        "psd_rows": psd_rows,
        "coherence_rows": coherence_rows,
        "force_component_rows": component_rows,
    }


def write_markdown(result: dict[str, Any], path: Path) -> None:
    lines = [
        "# Wind/Force Case Comparison",
        "",
        f"Config: `{result['config']}`",
        f"Base force dir: `{result['base']['force_dir']}`",
        f"New force dir: `{result['new']['force_dir']}`",
        f"Max points per file: `{result['max_points']}`",
        "",
        "## Inferred u_star",
        "",
        f"- Base: `{result['inferred_u_star_base']}`",
        f"- New: `{result['inferred_u_star_new']}`",
        "",
        "## Wind Samples",
        "",
        "| Node | H mean base | H mean new | H mean rel diff | H std base | H std new | H std rel diff |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["wind_rows"]:
        lines.append(
            f"| {row['node']} | {row['H_mean_base']:.6g} | {row['H_mean_new']:.6g} | "
            f"{row['H_mean_rel_diff']:.3%} | {row['H_std_base']:.6g} | "
            f"{row['H_std_new']:.6g} | {row['H_std_rel_diff']:.3%} |"
        )
    lines.extend(["", "## PSD Samples", "", "| Node | H PSD log10 RMSE 0.02-2 Hz |", "|---:|---:|"])
    for row in result["psd_rows"]:
        lines.append(f"| {row['node']} | {row['H_psd_log10_rmse_0p02_to_2Hz']:.6g} |")
    lines.extend(["", "## Coherence Samples", "", "| Pair | Base mean | New mean |", "|---|---:|---:|"])
    for row in result["coherence_rows"]:
        lines.append(f"| {row['pair']} | {row['base_mean_0p02_to_1Hz']:.6g} | {row['new_mean_0p02_to_1Hz']:.6g} |")
    lines.extend(["", "## Force Components", ""])
    for comp in result["force_component_rows"]:
        lines.append(f"### {comp['suffix']}")
        lines.append("")
        lines.append(f"- Mean abs relative difference average: `{comp['mean_rel_diff_abs_avg']:.6g}`")
        lines.append(f"- Std abs relative difference average: `{comp['std_rel_diff_abs_avg']:.6g}`")
        lines.append("")
        lines.append("| Node | Mean base | Mean new | Mean rel diff | Std base | Std new | Std rel diff | Corr |")
        lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|")
        for row in comp["rows"]:
            lines.append(
                f"| {row['node']} | {row['base_mean']:.6g} | {row['new_mean']:.6g} | "
                f"{row['mean_rel_diff']:.3%} | {row['base_std']:.6g} | {row['new_std']:.6g} | "
                f"{row['std_rel_diff']:.3%} | {row['corr_same_node']:.4g} |"
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare two wind/force cases statistically.")
    parser.add_argument("--config", default="config/timur_baseline.yaml")
    parser.add_argument("--base-force", default="FORCE_3")
    parser.add_argument("--base-sim", default="SIM1")
    parser.add_argument("--base-wind-dir", default="data/wind/SIM1")
    parser.add_argument("--new-force", required=True)
    parser.add_argument("--new-sim", required=True)
    parser.add_argument("--new-wind-dir", required=True)
    parser.add_argument("--max-points", type=int)
    parser.add_argument("--support-elevation", type=float, default=49.4)
    parser.add_argument("--kappa", type=float, default=0.387)
    parser.add_argument("--z0", type=float, default=0.05)
    parser.add_argument("--out-dir", default="output/wind_case_comparison")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    result = compare_cases(
        ROOT / args.config,
        args.base_force,
        args.base_sim,
        args.base_wind_dir,
        args.new_force,
        args.new_sim,
        args.new_wind_dir,
        args.max_points,
        args.support_elevation,
        args.kappa,
        args.z0,
    )
    (out_dir / "wind_force_case_comparison.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_markdown(result, out_dir / "wind_force_case_comparison.md")
    print(f"Wrote {out_dir / 'wind_force_case_comparison.md'}")


if __name__ == "__main__":
    main()
