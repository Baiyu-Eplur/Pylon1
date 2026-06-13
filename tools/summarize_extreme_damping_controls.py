"""Summarize baseline and extreme damping diagnostic controls."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


CASES = [
    (
        "C_no_aero_damping_update",
        "C baseline: xi=0.01, aero damping disabled",
        Path("output/diagnostics/strong_response_controls/runs/C_no_aero_damping_update"),
        0.01,
    ),
    (
        "D0_zero_global_rayleigh_xi0",
        "D0: xi=0.0, aero damping disabled",
        Path("output/diagnostics/extreme_damping_controls/runs/D0_zero_global_rayleigh_xi0"),
        0.0,
    ),
    (
        "D1_high_global_rayleigh_xi0p50",
        "D1: xi=0.5, aero damping disabled",
        Path("output/diagnostics/extreme_damping_controls/runs/D1_high_global_rayleigh_xi0p50"),
        0.5,
    ),
]

OUT_DIR = Path("output/diagnostics/extreme_damping_controls")


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


def sha256(path: Path) -> str:
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as fid:
        for block in iter(lambda: fid.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def as_float(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def main() -> None:
    rows = []
    for case_id, label, run_dir, xi in CASES:
        status = read_status(run_dir / "analysis_status.txt")
        audit = read_json(run_dir / "termination_audit" / "opensees_termination_audit.json")
        summary = read_json(run_dir / "strong_response_diagnosis" / "strong_response_summary.json")
        solver_logs = audit.get("solver_logs", []) if isinstance(audit, dict) else []
        th_return_code = ""
        th_elapsed = ""
        for log in solver_logs:
            if str(log.get("run_label", "")).endswith("_time_history"):
                th_return_code = log.get("return_code", "")
                th_elapsed = log.get("elapsed_seconds", "")
        rows.append(
            {
                "case_id": case_id,
                "label": label,
                "xi": xi,
                "status": status.get("STATUS", "missing"),
                "message": status.get("MESSAGE", ""),
                "classification": audit.get("classification", ""),
                "last_time_s": summary.get("last_time"),
                "progress_percent": as_float(status.get("PROGRESS")),
                "analyze_return_code": as_float(status.get("ANALYZE_RETURN_CODE")),
                "opensees_return_code": th_return_code,
                "time_history_elapsed_s": th_elapsed,
                "disp_max_m": summary.get("disp_max"),
                "vel_max_mps": summary.get("vel_max"),
                "acc_max_mps2": summary.get("acc_max"),
                "dynamic_sha256": sha256(run_dir / "Dynamic.out"),
                "velocity_sha256": sha256(run_dir / "Velocity.out"),
                "accel_sha256": sha256(run_dir / "Accel.out"),
            }
        )

    out_csv = OUT_DIR / "extreme_damping_comparison.csv"
    out_md = OUT_DIR / "extreme_damping_comparison.md"
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with out_csv.open("w", newline="", encoding="utf-8") as fid:
        writer = csv.DictWriter(fid, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    headers = list(rows[0])
    lines = [
        "# Extreme Damping Control Comparison",
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
            "- Changing structural/global damping changes the OpenSees main response histories; the dynamic output hashes are different across C/D0/D1.",
            "- With zero damping, the run becomes more numerically difficult and exits abnormally at about 154.325 s without Tcl `analysis_status.txt`.",
            "- With intentionally high damping (`xi=0.5`), the run reaches 204.8 s successfully and the displacement/velocity/acceleration envelopes are strongly suppressed.",
            "- Therefore the earlier A/B/C equality does not mean OpenSees ignores damping in general. It means the tested aerodynamic-damping update variants did not alter the effective global response path for that case.",
        ]
    )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out_csv)
    print(out_md)


if __name__ == "__main__":
    main()
