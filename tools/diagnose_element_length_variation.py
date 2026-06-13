from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import yaml

from src.cable_analyser.geometry import CableGeometry


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "output" / "diagnostics" / "typical_incremental_quasi_steady_formal_no_stop"
CONFIG = CASE_DIR / "typical_L322P8_H10P48_U0P6_incremental_quasi_steady_formal_no_stop.yaml"
RUN_DIR = CASE_DIR / "run"
OUT_DIR = CASE_DIR / "analysis"


def main() -> None:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    geo = CableGeometry(cfg).generate()
    x0 = np.asarray(geo["x"], dtype=float)
    y0 = np.asarray(geo["y"], dtype=float)
    z0 = np.asarray(geo["z"], dtype=float)
    initial_lengths = np.asarray(geo["dx"], dtype=float)

    dyn = np.loadtxt(RUN_DIR / "Dynamic.out")
    time = dyn[:, 0]
    values = dyn[:, 1:]
    n_nodes = len(x0)
    disp = values.reshape((len(time), n_nodes, 3))
    x = x0[None, :] + disp[:, :, 0]
    y = y0[None, :] + disp[:, :, 1]
    z = z0[None, :] + disp[:, :, 2]
    lengths = np.sqrt(np.diff(x, axis=1) ** 2 + np.diff(y, axis=1) ** 2 + np.diff(z, axis=1) ** 2)
    strain = (lengths - initial_lengths[None, :]) / initial_lengths[None, :]

    windows = [(0, 40), (40, 50), (50, 58), (58, 65), (65, 75), (75, float(time[-1]) + 1e-9)]
    window_rows = []
    for start, end in windows:
        mask = (time >= start) & (time < end)
        if not np.any(mask):
            continue
        s = strain[mask]
        idx = np.unravel_index(np.nanargmax(np.abs(s)), s.shape)
        row = {
            "window_s": [start, end],
            "max_abs_strain": float(np.nanmax(np.abs(s))),
            "mean_abs_strain": float(np.nanmean(np.abs(s))),
            "p95_abs_strain": float(np.nanpercentile(np.abs(s), 95)),
            "element_at_max_1based": int(idx[1] + 1),
            "time_at_max_s": float(time[mask][idx[0]]),
            "length_change_at_max_m": float((lengths[mask][idx] - initial_lengths[idx[1]])),
        }
        window_rows.append(row)

    summary = {
        "case_dir": str(CASE_DIR),
        "n_time_steps": int(len(time)),
        "n_elements": int(len(initial_lengths)),
        "initial_length_min_m": float(np.min(initial_lengths)),
        "initial_length_max_m": float(np.max(initial_lengths)),
        "global_max_abs_strain": float(np.nanmax(np.abs(strain))),
        "global_mean_abs_strain": float(np.nanmean(np.abs(strain))),
        "global_p95_abs_strain": float(np.nanpercentile(np.abs(strain), 95)),
        "window_rows": window_rows,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_json = OUT_DIR / "element_length_variation_summary.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    out_csv = OUT_DIR / "element_length_variation_windows.csv"
    with out_csv.open("w", encoding="utf-8") as f:
        f.write("window_start_s,window_end_s,max_abs_strain,mean_abs_strain,p95_abs_strain,element_at_max_1based,time_at_max_s,length_change_at_max_m\n")
        for row in window_rows:
            f.write(
                "{},{},{:.12g},{:.12g},{:.12g},{},{:.12g},{:.12g}\n".format(
                    row["window_s"][0],
                    row["window_s"][1],
                    row["max_abs_strain"],
                    row["mean_abs_strain"],
                    row["p95_abs_strain"],
                    row["element_at_max_1based"],
                    row["time_at_max_s"],
                    row["length_change_at_max_m"],
                )
            )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
