from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "output" / "diagnostics" / "typical_incremental_qs_mapping_fixed_power_strain"
RUN = CASE / "run"
FORCE_DIR = ROOT / "data" / "forces" / "FORCE_3" / "SIM1"
OUT = CASE / "analysis" / "onset_root_cause_69s"


def load_force_log() -> np.ndarray:
    return np.genfromtxt(RUN / "incremental_quasi_steady_aero_force_log.txt", names=True)


def original_total_abs_at_time(t: float, dt: float = 0.05, n_nodes: int = 101) -> float:
    # Mirrors OpenSees Path time-series linear interpolation more closely than
    # indexing by adaptive solver increment.
    total = 0.0
    for node in range(1, n_nodes + 1):
        h_drag = np.loadtxt(FORCE_DIR / f"NODE_{node}_H_drag.txt")
        h_lift = np.loadtxt(FORCE_DIR / f"NODE_{node}_H_lift.txt")
        v_drag = np.loadtxt(FORCE_DIR / f"NODE_{node}_V_drag.txt")
        v_lift = np.loadtxt(FORCE_DIR / f"NODE_{node}_V_lift.txt")
        x = np.arange(len(h_drag), dtype=float) * dt
        hd = float(np.interp(t, x, h_drag)) * 1000.0
        hl = float(np.interp(t, x, h_lift)) * 1000.0
        vd = float(np.interp(t, x, v_drag)) * 1000.0
        vl = float(np.interp(t, x, v_lift)) * 1000.0
        fy = hd + vl
        fz = hl + vd
        total += float(np.hypot(fy, fz))
    return total


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    log = load_force_log()
    sample_times = [40.0, 58.0, 65.0, 69.45, 69.51330692520463, 69.65545123364667, 69.74924193572579]
    rows = []
    for target in sample_times:
        idx = int(np.argmin(np.abs(log["time"] - target)))
        t = float(log["time"][idx])
        logged = float(log["F_reference"][idx])
        correct = original_total_abs_at_time(t)
        rows.append(
            {
                "target_time_s": target,
                "log_time_s": t,
                "logged_F_reference_N": logged,
                "correct_time_F_reference_N": correct,
                "difference_N": logged - correct,
                "ratio_logged_over_correct": logged / correct if abs(correct) > 1e-12 else None,
            }
        )
    (OUT / "time_series_alignment_check.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
