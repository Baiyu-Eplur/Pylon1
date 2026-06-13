from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import numpy as np


ROOT = Path("output/diagnostics/explicit_aero_force_validation")
RUNS = ROOT / "runs"
CASES = [
    ("F0", "F0_record_only_no_explicit_force", "disabled", 1.0),
    ("F1", "F1_explicit_force_scale0", "enabled", 0.0),
    ("F2", "F2_explicit_force_scale1", "enabled", 1.0),
    ("F3", "F3_explicit_force_scale10", "enabled", 10.0),
]


def sha256(path: Path) -> str:
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_table(path: Path) -> np.ndarray | None:
    if not path.exists() or path.stat().st_size == 0:
        return None
    data = np.loadtxt(path)
    if data.ndim == 1:
        data = data[np.newaxis, :]
    return data


def response_stats(run: Path) -> dict[str, float | int | str]:
    out: dict[str, float | int | str] = {}
    for filename, key in [
        ("Dynamic.out", "disp"),
        ("Velocity.out", "vel"),
        ("Accel.out", "acc"),
    ]:
        data = load_table(run / filename)
        out[f"{key}_rows"] = 0 if data is None else int(data.shape[0])
        out[f"{key}_last_time"] = "" if data is None else float(data[-1, 0])
        out[f"{key}_max_abs"] = "" if data is None else float(np.nanmax(np.abs(data[:, 1:])))
    return out


def force_stats(run: Path) -> dict[str, float | int | str]:
    data = load_table(run / "explicit_aero_damping_force_log.txt")
    if data is None:
        return {
            "force_rows": 0,
            "force_last_time": "",
            "force_total_abs_max": "",
            "force_element_abs_max": "",
            "force_scale_logged": "",
        }
    return {
        "force_rows": int(data.shape[0]),
        "force_last_time": float(data[-1, 0]),
        "force_total_abs_max": float(np.nanmax(data[:, 1])),
        "force_element_abs_max": float(np.nanmax(data[:, 2])),
        "force_scale_logged": float(data[-1, 3]),
    }


def status(run: Path) -> str:
    path = run / "analysis_status.txt"
    if not path.exists():
        return "no_analysis_status"
    values = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            values[parts[0]] = parts[1]
    return values.get("MESSAGE", values.get("STATUS", "unknown"))


def fmt(value: object) -> str:
    if value == "":
        return ""
    if isinstance(value, float):
        return f"{value:.8g}"
    return str(value)


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    for case, folder, enabled, scale in CASES:
        run = RUNS / folder
        row = {
            "case": case,
            "folder": folder,
            "explicit_force": enabled,
            "scale": scale,
            "termination": status(run),
            "dynamic_sha256": sha256(run / "Dynamic.out"),
            "velocity_sha256": sha256(run / "Velocity.out"),
            "accel_sha256": sha256(run / "Accel.out"),
        }
        row.update(response_stats(run))
        row.update(force_stats(run))
        rows.append(row)

    csv_path = ROOT / "explicit_aero_force_validation_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    hash_groups: dict[str, str] = {}
    md_path = ROOT / "explicit_aero_force_validation_summary.md"
    lines = [
        "# Explicit Aerodynamic Damping Force Validation",
        "",
        "| Case | Explicit force | Scale | Termination | Last response time (s) | Max disp abs (m) | Max vel abs (m/s) | Max acc abs (m/s^2) | Max total explicit force (N) | Dynamic hash group |",
        "|---|---|---:|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        digest = str(row["dynamic_sha256"])
        if digest not in hash_groups:
            hash_groups[digest] = chr(ord("A") + len(hash_groups))
        lines.append(
            "| {case} | {explicit_force} | {scale} | {termination} | {disp_last_time} | "
            "{disp_max_abs} | {vel_max_abs} | {acc_max_abs} | {force_total_abs_max} | {group} |".format(
                case=row["case"],
                explicit_force=row["explicit_force"],
                scale=fmt(row["scale"]),
                termination=row["termination"],
                disp_last_time=fmt(row["disp_last_time"]),
                disp_max_abs=fmt(row["disp_max_abs"]),
                vel_max_abs=fmt(row["vel_max_abs"]),
                acc_max_abs=fmt(row["acc_max_abs"]),
                force_total_abs_max=fmt(row["force_total_abs_max"]),
                group=hash_groups[digest],
            )
        )
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "- F1 is the null-force check. The explicit-force callback is active, but the logged force is zero because scale = 0.",
            "- F2 is the physical-scale explicit aerodynamic damping force. It must have a nonzero force log and a different response hash from F0/F1.",
            "- F3 is an amplified sensitivity check. It is not a production setting; it verifies that the explicit force channel can strongly feed back into the nonlinear time-domain solution.",
            "",
            f"CSV: `{csv_path}`",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(md_path)


if __name__ == "__main__":
    main()
