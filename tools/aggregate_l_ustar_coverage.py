from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


CORE_CRITERIA = [
    "C2_sustained_negative_damping",
    "C4_rolling_response_growth",
    "C6_large_response",
    "C2_and_C4",
]


def load_manifest_cases(paths: list[Path]) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}
    for path in paths:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        for case in manifest["cases"]:
            label = case["case_label"]
            cases[label] = {
                "case_label": label,
                "L_m": float(case["L_m"]),
                "Sag_m": float(case["Sag_m"]),
                "u_star": float(case["u_star"]),
                "seed": int(case["seed"]),
                "config_path": case["config_path"],
                "output_dir": case["output_dir"],
                "completed": bool(case.get("executed") and not case.get("failed")),
                "failed": bool(case.get("failed") or not case.get("executed")),
                "returncode": case.get("returncode"),
            }
    return cases


def read_case_audits(audit_root: Path, cases: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for audit_path in sorted(audit_root.glob("*/time_step_coverage_audit.json")):
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        label = audit_path.parent.name
        meta = cases[label]
        row: dict[str, Any] = {
            **meta,
            "audit_path": str(audit_path.relative_to(ROOT)),
            "steps": int(audit["steps"]),
            "duration_s": float(audit["duration_s"]),
            "raw_dynamic_rows": int(audit.get("raw_dynamic_rows", audit["steps"])),
            "truncated_to_records": audit.get("truncated_to_records"),
        }
        for criterion in audit["summary"]:
            summary = audit["summary"][criterion]
            row[f"{criterion}__coverage"] = float(summary["coverage_fraction"])
            row[f"{criterion}__time_true_s"] = float(summary["time_true_s"])
            row[f"{criterion}__longest_s"] = float(summary["longest_continuous_true_s"])
        rows.append(row)
    return rows


def mean(values: list[float]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


def stdev(values: list[float]) -> float:
    return float(statistics.stdev(values)) if len(values) > 1 else 0.0


def sem(values: list[float]) -> float:
    return stdev(values) / (len(values) ** 0.5) if len(values) > 1 else 0.0


def summarize(cases: dict[str, dict[str, Any]], case_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    all_l = sorted({case["L_m"] for case in cases.values()})
    all_u = sorted({case["u_star"] for case in cases.values()})
    rows: list[dict[str, Any]] = []
    for l_value in all_l:
        for u_star in all_u:
            planned = [
                case for case in cases.values()
                if case["L_m"] == l_value and case["u_star"] == u_star
            ]
            completed = [
                row for row in case_rows
                if row["L_m"] == l_value and row["u_star"] == u_star
            ]
            failed = [
                case for case in planned
                if case["failed"]
            ]
            sag_values = sorted({case["Sag_m"] for case in planned})
            row: dict[str, Any] = {
                "L_m": l_value,
                "Sag_m": sag_values[0] if sag_values else 0.0,
                "u_star": u_star,
                "planned_n": len(planned),
                "completed_n": len(completed),
                "failed_n": len(failed),
                "failed_fraction": float(len(failed) / len(planned)) if planned else 0.0,
            }
            for criterion in CORE_CRITERIA:
                values = [float(item[f"{criterion}__coverage"]) for item in completed]
                value_mean = mean(values)
                value_sem = sem(values)
                ci95 = 1.96 * value_sem
                row[f"{criterion}__mean_coverage"] = value_mean
                row[f"{criterion}__std_coverage"] = stdev(values)
                row[f"{criterion}__sem_coverage"] = value_sem
                row[f"{criterion}__ci95_low_coverage"] = max(0.0, value_mean - ci95)
                row[f"{criterion}__ci95_high_coverage"] = min(1.0, value_mean + ci95)
                row[f"{criterion}__min_coverage"] = min(values) if values else 0.0
                row[f"{criterion}__max_coverage"] = max(values) if values else 0.0
            rows.append(row)
    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float) -> str:
    return f"{100.0 * value:.2f}%"


def write_markdown(summary_rows: list[dict[str, Any]], failed_rows: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "# L-u_star Time-Step Coverage Summary",
        "",
        "Sag rule: `parabolic_tension`, i.e. `H(L) = w L^2 / (8 T0)` using Zebra self-weight and 15% RTS pretension.",
        "",
        "## Geometry",
        "",
        "| L (m) | H/Sag (m) | H/L |",
        "|---:|---:|---:|",
    ]
    for l_value in sorted({row["L_m"] for row in summary_rows}):
        row = next(item for item in summary_rows if item["L_m"] == l_value)
        lines.append(f"| {l_value:.1f} | {row['Sag_m']:.4f} | {row['Sag_m']/l_value:.4f} |")

    lines += [
        "",
        "## Core Mean Coverage And Failure Rate",
        "",
        "| L | u_star | completed/planned | failed rate | C2 | C4 | C6 | C2&C4 |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['L_m']:.1f} | {row['u_star']:.2f} | "
            f"{row['completed_n']}/{row['planned_n']} | {fmt(row['failed_fraction'])} | "
            f"{fmt(row['C2_sustained_negative_damping__mean_coverage'])} | "
            f"{fmt(row['C4_rolling_response_growth__mean_coverage'])} | "
            f"{fmt(row['C6_large_response__mean_coverage'])} | "
            f"{fmt(row['C2_and_C4__mean_coverage'])} |"
        )

    lines += [
        "",
        "## C4/C6/C2&C4 Approximate 95% CI",
        "",
        "| L | u_star | C4 mean [95% CI] | C6 mean [95% CI] | C2&C4 mean [95% CI] |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['L_m']:.1f} | {row['u_star']:.2f} | "
            f"{fmt(row['C4_rolling_response_growth__mean_coverage'])} "
            f"[{fmt(row['C4_rolling_response_growth__ci95_low_coverage'])}, {fmt(row['C4_rolling_response_growth__ci95_high_coverage'])}] | "
            f"{fmt(row['C6_large_response__mean_coverage'])} "
            f"[{fmt(row['C6_large_response__ci95_low_coverage'])}, {fmt(row['C6_large_response__ci95_high_coverage'])}] | "
            f"{fmt(row['C2_and_C4__mean_coverage'])} "
            f"[{fmt(row['C2_and_C4__ci95_low_coverage'])}, {fmt(row['C2_and_C4__ci95_high_coverage'])}] |"
        )

    lines += [
        "",
        "## Failed Or Non-Normal Cases",
        "",
        "| case | L | u_star | seed | returncode |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in failed_rows:
        lines.append(
            f"| {row['case_label']} | {row['L_m']:.1f} | {row['u_star']:.2f} | {row['seed']} | {row.get('returncode', '')} |"
        )
    lines += [
        "",
        "## Notes",
        "",
        "- Coverage is averaged only over completed runs.",
        "- Failed/non-normal runs are retained as a separate instability indicator.",
        "- Approximate 95% CI uses completed-run SEM; with small `n`, treat it as descriptive.",
        "- All audits use `--max-records 4096` to avoid adaptive substep-density bias.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def svg_plot(summary_rows: list[dict[str, Any]], criterion: str, out_path: Path, title: str) -> None:
    width, height = 920, 560
    ml, mr, mt, mb = 80, 40, 54, 70
    plot_w = width - ml - mr
    plot_h = height - mt - mb
    l_values = sorted({row["L_m"] for row in summary_rows})
    u_values = sorted({row["u_star"] for row in summary_rows})
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd"]
    y_max = max(
        [row[f"{criterion}__ci95_high_coverage"] for row in summary_rows] + [0.01]
    )
    y_max = min(1.0, max(0.1, y_max * 1.08))

    def sx(u_star: float) -> float:
        return ml + (u_star - min(u_values)) / (max(u_values) - min(u_values)) * plot_w

    def sy(value: float) -> float:
        return mt + (1.0 - value / y_max) * plot_h

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{ml}" y="30" font-family="Arial" font-size="18" font-weight="bold" fill="#213547">{title}</text>',
        f'<line x1="{ml}" y1="{mt + plot_h}" x2="{ml + plot_w}" y2="{mt + plot_h}" stroke="#333"/>',
        f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt + plot_h}" stroke="#333"/>',
    ]
    for i in range(0, 6):
        y = y_max * i / 5
        py = sy(y)
        lines.append(f'<line x1="{ml}" y1="{py:.2f}" x2="{ml + plot_w}" y2="{py:.2f}" stroke="#e6e9ef"/>')
        lines.append(f'<text x="{ml-10}" y="{py+4:.2f}" text-anchor="end" font-family="Arial" font-size="11" fill="#555">{100*y:.0f}%</text>')
    for u in u_values:
        x = sx(u)
        lines.append(f'<text x="{x:.2f}" y="{mt+plot_h+25}" text-anchor="middle" font-family="Arial" font-size="12" fill="#555">{u:.2f}</text>')
    lines.append(f'<text x="{ml+plot_w/2}" y="{height-18}" text-anchor="middle" font-family="Arial" font-size="13" fill="#555">u_star (m/s)</text>')

    for idx, l_value in enumerate(l_values):
        color = colors[idx % len(colors)]
        rows = [row for row in summary_rows if row["L_m"] == l_value]
        rows.sort(key=lambda row: row["u_star"])
        points = []
        for row in rows:
            x = sx(row["u_star"])
            mean = row[f"{criterion}__mean_coverage"]
            lo = row[f"{criterion}__ci95_low_coverage"]
            hi = row[f"{criterion}__ci95_high_coverage"]
            y = sy(mean)
            points.append(f"{x:.2f},{y:.2f}")
            lines.append(f'<line x1="{x:.2f}" y1="{sy(hi):.2f}" x2="{x:.2f}" y2="{sy(lo):.2f}" stroke="{color}" stroke-width="1.2" opacity="0.55"/>')
            lines.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.5" fill="{color}"/>')
        lines.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2"/>')
        lines.append(f'<text x="{width-mr-120}" y="{mt + 18*idx}" font-family="Arial" font-size="12" fill="{color}">L={l_value:.0f} m</text>')
    lines.append("</svg>")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def svg_metric_plot(summary_rows: list[dict[str, Any]], metric: str, out_path: Path, title: str) -> None:
    width, height = 920, 560
    ml, mr, mt, mb = 80, 40, 54, 70
    plot_w = width - ml - mr
    plot_h = height - mt - mb
    l_values = sorted({row["L_m"] for row in summary_rows})
    u_values = sorted({row["u_star"] for row in summary_rows})
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd"]
    y_max = max([row[metric] for row in summary_rows] + [0.01])
    y_max = min(1.0, max(0.1, y_max * 1.08))

    def sx(u_star: float) -> float:
        return ml + (u_star - min(u_values)) / (max(u_values) - min(u_values)) * plot_w

    def sy(value: float) -> float:
        return mt + (1.0 - value / y_max) * plot_h

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{ml}" y="30" font-family="Arial" font-size="18" font-weight="bold" fill="#213547">{title}</text>',
        f'<line x1="{ml}" y1="{mt + plot_h}" x2="{ml + plot_w}" y2="{mt + plot_h}" stroke="#333"/>',
        f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt + plot_h}" stroke="#333"/>',
    ]
    for i in range(0, 6):
        y = y_max * i / 5
        py = sy(y)
        lines.append(f'<line x1="{ml}" y1="{py:.2f}" x2="{ml + plot_w}" y2="{py:.2f}" stroke="#e6e9ef"/>')
        lines.append(f'<text x="{ml-10}" y="{py+4:.2f}" text-anchor="end" font-family="Arial" font-size="11" fill="#555">{100*y:.0f}%</text>')
    for u in u_values:
        x = sx(u)
        lines.append(f'<text x="{x:.2f}" y="{mt+plot_h+25}" text-anchor="middle" font-family="Arial" font-size="12" fill="#555">{u:.2f}</text>')
    lines.append(f'<text x="{ml+plot_w/2}" y="{height-18}" text-anchor="middle" font-family="Arial" font-size="13" fill="#555">u_star (m/s)</text>')

    for idx, l_value in enumerate(l_values):
        color = colors[idx % len(colors)]
        rows = [row for row in summary_rows if row["L_m"] == l_value]
        rows.sort(key=lambda row: row["u_star"])
        points = []
        for row in rows:
            x = sx(row["u_star"])
            y = sy(row[metric])
            points.append(f"{x:.2f},{y:.2f}")
            lines.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.5" fill="{color}"/>')
        lines.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2"/>')
        lines.append(f'<text x="{width-mr-120}" y="{mt + 18*idx}" font-family="Arial" font-size="12" fill="{color}">L={l_value:.0f} m</text>')
    lines.append("</svg>")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-root", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--manifest", action="append", required=True)
    args = parser.parse_args()

    out_dir = (ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_paths = [(ROOT / item).resolve() for item in args.manifest]
    cases = load_manifest_cases(manifest_paths)
    case_rows = read_case_audits((ROOT / args.audit_root).resolve(), cases)
    failed_rows = [case for case in cases.values() if case["failed"]]
    summary_rows = summarize(cases, case_rows)

    write_csv(case_rows, out_dir / "case_coverage.csv")
    write_csv(summary_rows, out_dir / "l_ustar_coverage_summary.csv")
    write_csv(failed_rows, out_dir / "failed_cases.csv")
    (out_dir / "l_ustar_coverage_summary.json").write_text(
        json.dumps(
            {"cases": case_rows, "summary": summary_rows, "failed_cases": failed_rows},
            indent=2,
        ),
        encoding="utf-8",
    )
    write_markdown(summary_rows, failed_rows, out_dir / "l_ustar_coverage_summary.md")
    svg_plot(summary_rows, "C2_sustained_negative_damping", out_dir / "C2_coverage_by_L.svg", "C2 negative damping coverage")
    svg_plot(summary_rows, "C4_rolling_response_growth", out_dir / "C4_coverage_by_L.svg", "C4 response growth coverage")
    svg_plot(summary_rows, "C6_large_response", out_dir / "C6_coverage_by_L.svg", "C6 large response coverage")
    svg_plot(summary_rows, "C2_and_C4", out_dir / "C2C4_coverage_by_L.svg", "C2&C4 strict marker coverage")
    svg_metric_plot(summary_rows, "failed_fraction", out_dir / "failed_fraction_by_L.svg", "Failed/non-normal fraction")
    print(f"Wrote {out_dir / 'l_ustar_coverage_summary.md'}")


if __name__ == "__main__":
    main()
