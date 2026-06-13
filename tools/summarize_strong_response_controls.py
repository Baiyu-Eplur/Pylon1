"""Summarize strong-response diagnostic control cases."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path("output/diagnostics/strong_response_controls")
CASES = [
    ("A_dcl_scale_1_no_rad_conversion", "A: dCL scale = 1, no rad conversion"),
    ("B_dcl_rad_scale_delta_cap_minus2", "B: dCL rad scale, Delta_D >= -2"),
    ("C_no_aero_damping_update", "C: aerodynamic damping update disabled"),
]


def read_status(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            data[parts[0]] = parts[1]
    return data


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def as_float(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def main() -> None:
    rows = []
    for case_id, label in CASES:
        run_dir = ROOT / "runs" / case_id
        status = read_status(run_dir / "analysis_status.txt")
        audit = read_json(run_dir / "termination_audit" / "opensees_termination_audit.json")
        summary = read_json(run_dir / "strong_response_diagnosis" / "strong_response_summary.json")
        damping = audit.get("damping_log", {}) if isinstance(audit, dict) else {}
        repetition = summary.get("time_repetition", {}) if isinstance(summary, dict) else {}
        last_windows = summary.get("last_windows", []) if isinstance(summary, dict) else []
        onset_window = next(
            (
                w
                for w in last_windows
                if as_float(w.get("t0"), -1) >= 135.0 and as_float(w.get("t1"), -1) <= 140.1
            ),
            {},
        )
        rows.append(
            {
                "case_id": case_id,
                "label": label,
                "status": status.get("STATUS", ""),
                "message": status.get("MESSAGE", ""),
                "last_time_s": as_float(status.get("TIME")),
                "progress_percent": as_float(status.get("PROGRESS")),
                "analyze_return_code": as_float(status.get("ANALYZE_RETURN_CODE")),
                "factor": as_float(status.get("FACTOR")),
                "min_factor": as_float(status.get("MIN_FACTOR")),
                "disp_max_m": summary.get("disp_max"),
                "vel_max_mps": summary.get("vel_max"),
                "acc_max_mps2": summary.get("acc_max"),
                "duplicate_time_fraction": repetition.get("duplicate_time_fraction"),
                "max_duplicate_count": repetition.get("max_duplicate_count"),
                "damping_rows": damping.get("rows"),
                "min_xi_total": damping.get("min_xi_total"),
                "negative_xi_rows": damping.get("negative_xi_rows"),
                "onset_135_140_p95_disp_m": onset_window.get("p95"),
                "onset_135_140_vel_p95_mps": onset_window.get("vel_p95"),
                "onset_135_140_acc_p95_mps2": onset_window.get("acc_p95"),
                "onset_135_140_xi_negative_fraction": onset_window.get("xi_negative_fraction"),
            }
        )

    out_csv = ROOT / "control_comparison.csv"
    out_md = ROOT / "control_comparison.md"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as fid:
        writer = csv.DictWriter(fid, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    headers = list(rows[0])
    lines = [
        "# Strong Response Control Comparison",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join("" if row[h] is None else str(row[h]) for h in headers) + " |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- All three diagnostic controls stopped at the same dynamic time, 160.43890698784924 s, with OpenSees analyze return code -3 and the same adaptive factor floor condition.",
            "- The global displacement, velocity, and acceleration envelopes are identical across the three controls to the reported precision.",
            "- Case A has no negative damping rows; Case C disables aerodynamic damping updates entirely. Therefore, this particular strong-response path is not caused solely by the Den Hartog derivative scaling or by negative aerodynamic damping in `Damping_shifter.tcl`.",
            "- The next diagnostic priority is to check whether the external wind-force histories, dynamic load application, or structural/integrator configuration imposes the same forcing path independent of damping changes.",
        ]
    )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out_csv)
    print(out_md)


if __name__ == "__main__":
    main()
