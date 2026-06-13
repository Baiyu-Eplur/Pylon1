from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path("output/diagnostics/damping_writeback_matrix")
RUNS = ROOT / "runs"
CASES = [
    ("E1", "E1_global0_element_structural", "global=0; element=xi_structural"),
    ("E2", "E2_global_structural_record_only", "global=xi_structural; element=record_only"),
    ("E3", "E3_global0_element_total", "global=0; element=xi_structural+xi_aero(t)"),
    ("E4", "E4_global_structural_element_aero", "global=xi_structural; element=xi_aero(t)"),
]


def sha256(path: Path) -> str:
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_summary(run: Path) -> dict:
    path = run / "strong_response_diagnosis" / "strong_response_summary.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_status(run: Path) -> dict:
    status = {}
    path = run / "analysis_status.txt"
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                status[parts[0]] = parts[1]
        return status

    audit = run / "termination_audit" / "opensees_termination_audit.md"
    if audit.exists():
        text = audit.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"Classification: `([^`]+)`", text)
        if m:
            status["MESSAGE"] = m.group(1)
        m = re.search(r"Dynamic\.out \| True \| \d+ \| ([0-9.]+)", text)
        if m:
            status["TIME"] = m.group(1)
    return status


def read_damping_log_stats(run: Path) -> dict:
    audit = run / "termination_audit" / "opensees_termination_audit.md"
    out = {}
    if not audit.exists():
        return out
    text = audit.read_text(encoding="utf-8", errors="replace")
    patterns = {
        "damping_log_exists": r"Exists: `([^`]+)`",
        "damping_log_rows": r"Rows: `([^`]+)`",
        "damping_xi_min": r"Min xi_total: `([^`]+)`",
        "damping_negative_rows": r"Negative xi rows: `([^`]+)`",
    }
    # Limit the search to the damping section to avoid matching the time-series rows.
    section = text.split("## Damping Log", 1)[-1].split("## Realtime State", 1)[0]
    for key, pattern in patterns.items():
        m = re.search(pattern, section)
        if m:
            out[key] = m.group(1)
    return out


def fmt(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    for case_id, folder, meaning in CASES:
        run = RUNS / folder
        summary = read_summary(run)
        status = read_status(run)
        damping = read_damping_log_stats(run)
        rows.append(
            {
                "case": case_id,
                "folder": folder,
                "meaning": meaning,
                "termination": status.get("MESSAGE", status.get("STATUS", "")),
                "analysis_return_code": status.get("ANALYZE_RETURN_CODE", ""),
                "last_time_s": status.get("TIME", summary.get("last_time", "")),
                "disp_max_m": summary.get("disp_max", ""),
                "vel_max_mps": summary.get("vel_max", ""),
                "acc_max_mps2": summary.get("acc_max", ""),
                "damping_log_rows": damping.get("damping_log_rows", ""),
                "damping_xi_min": damping.get("damping_xi_min", ""),
                "damping_negative_rows": damping.get("damping_negative_rows", ""),
                "dynamic_sha256": sha256(run / "Dynamic.out"),
                "velocity_sha256": sha256(run / "Velocity.out"),
                "accel_sha256": sha256(run / "Accel.out"),
            }
        )

    csv_path = ROOT / "damping_writeback_matrix_comparison.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    md_path = ROOT / "damping_writeback_matrix_comparison.md"
    lines = [
        "# Damping writeback matrix comparison",
        "",
        "| Case | Configuration | Termination | t_last (s) | disp_max (m) | vel_max (m/s) | acc_max (m/s^2) | Dynamic hash group |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    hash_groups: dict[str, str] = {}
    for row in rows:
        digest = row["dynamic_sha256"]
        if digest not in hash_groups:
            hash_groups[digest] = chr(ord("A") + len(hash_groups))
        lines.append(
            "| {case} | {meaning} | {termination} | {last_time_s} | {disp_max_m} | "
            "{vel_max_mps} | {acc_max_mps2} | {group} |".format(
                case=row["case"],
                meaning=row["meaning"],
                termination=row["termination"],
                last_time_s=fmt(float(row["last_time_s"]) if row["last_time_s"] != "" else ""),
                disp_max_m=fmt(row["disp_max_m"]),
                vel_max_mps=fmt(row["vel_max_mps"]),
                acc_max_mps2=fmt(row["acc_max_mps2"]),
                group=hash_groups[digest],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- E1 and E3 share the same Dynamic/Velocity/Accel hash group if element writeback does not affect the solved response when global Rayleigh damping is zero.",
            "- E2 and E4 share the same Dynamic/Velocity/Accel hash group if aerodynamic-only element writeback does not perturb the solved response when global structural Rayleigh damping is active.",
            "- A difference between the global=0 group and the global=xi_structural group indicates that the global Rayleigh damping channel is active and controls the structural damping response.",
            "",
            f"CSV: `{csv_path}`",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(md_path)


if __name__ == "__main__":
    main()
