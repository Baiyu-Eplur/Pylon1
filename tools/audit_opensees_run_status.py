from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path
from typing import Any


TIME_SERIES_FILES = [
    "Dynamic.out",
    "Velocity.out",
    "Accel.out",
    "Reaction.out",
    "Static.out",
    "Element1.out",
]

ERROR_PATTERNS = [
    "failed to converge",
    "convergence",
    "failed",
    "WARNING",
    "ERROR",
    "NaN",
    "singular",
    "domainChange",
    "testNorm",
    "current Norm",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect OpenSees termination and monitoring status for one run directory.",
    )
    parser.add_argument("--output-dir", required=True, help="Directory containing OpenSees output files.")
    parser.add_argument("--dt", type=float, default=None, help="Nominal time step.")
    parser.add_argument("--npt", type=int, default=None, help="Nominal number of points.")
    parser.add_argument("--label", default=None, help="Human-readable case label.")
    parser.add_argument("--out-dir", default=None, help="Where to write audit files; defaults to output-dir/termination_audit.")
    return parser.parse_args()


def read_numeric_last(path: Path) -> dict[str, Any]:
    info: dict[str, Any] = {
        "file": path.name,
        "exists": path.exists(),
        "rows": 0,
        "columns_last": None,
        "last_time": None,
        "last_line": None,
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }
    if not path.exists() or path.stat().st_size == 0:
        return info

    last_line = None
    rows = 0
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped:
                continue
            rows += 1
            last_line = stripped

    info["rows"] = rows
    info["last_line"] = last_line
    if last_line:
        parts = last_line.split()
        info["columns_last"] = len(parts)
        try:
            info["last_time"] = float(parts[0])
        except ValueError:
            info["last_time"] = None
    return info


def read_realtime_state(path: Path) -> dict[str, Any]:
    info: dict[str, Any] = {"exists": path.exists(), "values": {}}
    if not path.exists():
        return info
    values: dict[str, Any] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        key, value = parts
        try:
            values[key] = float(value)
        except ValueError:
            values[key] = value
    info["values"] = values
    return info


def read_key_value_file(path: Path) -> dict[str, Any]:
    info: dict[str, Any] = {"exists": path.exists(), "values": {}}
    if not path.exists():
        return info
    values: dict[str, Any] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        key, value = parts
        try:
            values[key] = float(value)
        except ValueError:
            values[key] = value
    info["values"] = values
    return info


def read_damping(path: Path) -> dict[str, Any]:
    info: dict[str, Any] = {
        "exists": path.exists(),
        "rows": 0,
        "last_time": None,
        "min_xi_total": None,
        "max_xi_total": None,
        "negative_xi_rows": 0,
        "last_line": None,
    }
    if not path.exists() or path.stat().st_size == 0:
        return info

    min_xi = math.inf
    max_xi = -math.inf
    negative = 0
    rows = 0
    last_line = None
    last_time = None
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            parts = line.split()
            if len(parts) < 4:
                continue
            try:
                t = float(parts[0])
                xi = float(parts[3])
            except ValueError:
                continue
            rows += 1
            last_time = t
            last_line = line.strip()
            min_xi = min(min_xi, xi)
            max_xi = max(max_xi, xi)
            if xi < 0:
                negative += 1

    info.update(
        {
            "rows": rows,
            "last_time": last_time,
            "min_xi_total": None if math.isinf(min_xi) else min_xi,
            "max_xi_total": None if max_xi == -math.inf else max_xi,
            "negative_xi_rows": negative,
            "last_line": last_line,
        }
    )
    return info


def tail_text(path: Path, max_lines: int = 80) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[-max_lines:]


def collect_solver_logs(log_dir: Path) -> list[dict[str, Any]]:
    records = []
    if not log_dir.exists():
        return records
    for meta_path in sorted(log_dir.glob("*.meta.json")):
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        stdout_path = Path(meta.get("stdout_log", ""))
        stderr_path = Path(meta.get("stderr_log", ""))
        combined_tail = tail_text(stdout_path, 120) + tail_text(stderr_path, 120)
        matches = [
            line
            for line in combined_tail
            if any(pattern.lower() in line.lower() for pattern in ERROR_PATTERNS)
        ]
        records.append(
            {
                "meta_file": str(meta_path),
                "run_label": meta.get("run_label"),
                "return_code": meta.get("return_code"),
                "elapsed_seconds": meta.get("elapsed_seconds"),
                "started_at_utc": meta.get("started_at_utc"),
                "finished_at_utc": meta.get("finished_at_utc"),
                "stdout_log": meta.get("stdout_log"),
                "stderr_log": meta.get("stderr_log"),
                "diagnostic_lines_tail": matches[-40:],
                "stdout_tail": meta.get("stdout_tail", []),
                "stderr_tail": meta.get("stderr_tail", []),
            }
        )
    return records


def classify(report: dict[str, Any], target_duration: float | None, tolerance: float) -> str:
    status = report.get("analysis_status", {}).get("values", {}).get("STATUS")
    if status == "failed":
        return "tcl_analysis_failed"
    if status == "success":
        return "completed_to_target_duration"
    if any(item.get("return_code") not in (None, 0) for item in report["solver_logs"]):
        return "opensees_nonzero_exit"
    dynamic_time = report["time_series"].get("Dynamic.out", {}).get("last_time")
    realtime_time = report["realtime_state"].get("values", {}).get("TIME")
    observed = max([t for t in (dynamic_time, realtime_time) if isinstance(t, (int, float))], default=None)
    if target_duration is not None and observed is not None and observed < target_duration - tolerance:
        return "early_termination_or_incomplete_record"
    if target_duration is not None and observed is not None:
        return "completed_to_target_duration"
    return "unknown"


def write_monitor_csv(
    path: Path,
    time_series: dict[str, Any],
    damping: dict[str, Any],
    realtime: dict[str, Any],
    analysis_status: dict[str, Any],
) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["category", "name", "exists", "rows", "last_time", "extra"])
        for name, info in time_series.items():
            writer.writerow([
                "time_series",
                name,
                info.get("exists"),
                info.get("rows"),
                info.get("last_time"),
                f"columns_last={info.get('columns_last')}; size_bytes={info.get('size_bytes')}",
            ])
        writer.writerow([
            "damping",
            "damping_change_log.txt",
            damping.get("exists"),
            damping.get("rows"),
            damping.get("last_time"),
            f"min_xi_total={damping.get('min_xi_total')}; negative_xi_rows={damping.get('negative_xi_rows')}",
        ])
        writer.writerow([
            "realtime",
            "realtime_state.txt",
            realtime.get("exists"),
            "",
            realtime.get("values", {}).get("TIME"),
            json.dumps(realtime.get("values", {}), ensure_ascii=False),
        ])
        writer.writerow([
            "tcl_status",
            "analysis_status.txt",
            analysis_status.get("exists"),
            "",
            analysis_status.get("values", {}).get("TIME"),
            json.dumps(analysis_status.get("values", {}), ensure_ascii=False),
        ])


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# OpenSees Termination Audit",
        "",
        f"- Label: `{report['label']}`",
        f"- Output directory: `{report['output_dir']}`",
        f"- Target duration: `{report.get('target_duration_s')}` s",
        f"- Classification: `{report['classification']}`",
        "",
        "## Time-Series Coverage",
        "",
        "| File | Exists | Rows | Last time | Last columns |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, info in report["time_series"].items():
        lines.append(
            f"| {name} | {info.get('exists')} | {info.get('rows')} | "
            f"{info.get('last_time')} | {info.get('columns_last')} |"
        )
    lines.extend(
        [
            "",
            "## Damping Log",
            "",
            f"- Exists: `{report['damping_log'].get('exists')}`",
            f"- Rows: `{report['damping_log'].get('rows')}`",
            f"- Last time: `{report['damping_log'].get('last_time')}`",
            f"- Min xi_total: `{report['damping_log'].get('min_xi_total')}`",
            f"- Negative xi rows: `{report['damping_log'].get('negative_xi_rows')}`",
            "",
            "## Realtime State",
            "",
        ]
    )
    for key, value in report["realtime_state"].get("values", {}).items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Tcl Analysis Status", ""])
    status_values = report.get("analysis_status", {}).get("values", {})
    if status_values:
        for key, value in status_values.items():
            lines.append(f"- `{key}`: `{value}`")
    else:
        lines.append("No `analysis_status.txt` file was found.")
    lines.extend(["", "## Solver Logs", ""])
    if not report["solver_logs"]:
        lines.append("No solver meta logs were found.")
    for item in report["solver_logs"]:
        lines.extend(
            [
                f"### {item.get('run_label')}",
                "",
                f"- Return code: `{item.get('return_code')}`",
                f"- Elapsed seconds: `{item.get('elapsed_seconds')}`",
                f"- stdout: `{item.get('stdout_log')}`",
                f"- stderr: `{item.get('stderr_log')}`",
                "",
                "Diagnostic tail lines:",
                "",
            ]
        )
        diagnostic = item.get("diagnostic_lines_tail") or []
        if diagnostic:
            lines.extend([f"- `{line}`" for line in diagnostic])
        else:
            lines.append("- None found in stdout/stderr tail.")
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    out_dir = Path(args.out_dir) if args.out_dir else output_dir / "termination_audit"
    out_dir.mkdir(parents=True, exist_ok=True)
    target_duration = args.dt * args.npt if args.dt is not None and args.npt is not None else None
    tolerance = max(args.dt or 0.0, 1e-9)

    time_series = {name: read_numeric_last(output_dir / name) for name in TIME_SERIES_FILES}
    damping = read_damping(output_dir / "damping_change_log.txt")
    realtime = read_realtime_state(output_dir / "realtime_state.txt")
    analysis_status = read_key_value_file(output_dir / "analysis_status.txt")
    solver_logs = collect_solver_logs(output_dir / "solver_logs")

    report: dict[str, Any] = {
        "label": args.label or output_dir.name,
        "output_dir": str(output_dir.resolve()),
        "target_duration_s": target_duration,
        "time_series": time_series,
        "damping_log": damping,
        "realtime_state": realtime,
        "analysis_status": analysis_status,
        "solver_logs": solver_logs,
    }
    report["classification"] = classify(report, target_duration, tolerance)

    report_json = out_dir / "opensees_termination_audit.json"
    report_md = out_dir / "opensees_termination_audit.md"
    monitor_csv = out_dir / "monitoring_file_summary.csv"

    report_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(report_md, report)
    write_monitor_csv(monitor_csv, time_series, damping, realtime, analysis_status)
    print(report_md)


if __name__ == "__main__":
    main()
