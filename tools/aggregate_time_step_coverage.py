from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cable_analyser.config_loader import load_config


def case_label_from_audit_dir(path: Path) -> str:
    return path.name


def parse_extra_failed(value: str) -> dict[str, Any]:
    parts = value.split(":")
    if len(parts) < 3:
        raise ValueError("--extra-failed-case must be LABEL:USTAR:SEED[:NOTE]")
    return {
        "case_label": parts[0],
        "u_star": float(parts[1]),
        "seed": int(parts[2]),
        "status": "failed",
        "note": ":".join(parts[3:]) if len(parts) > 3 else "extra failed case",
    }


def load_manifest_cases(manifest_paths: list[Path]) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}
    for manifest_path in manifest_paths:
        if not manifest_path.exists():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for case in manifest.get("cases", []):
            label = case.get("case_label")
            if not label:
                continue
            status = "completed" if case.get("executed") and not case.get("failed") else "failed"
            cases[label] = {
                "case_label": label,
                "u_star": float(case.get("u_star")),
                "seed": int(case.get("seed")),
                "L_m": float(case.get("L_m")),
                "Sag_m": float(case.get("Sag_m")),
                "config_path": case.get("config_path"),
                "output_dir": case.get("output_dir"),
                "status": status,
                "returncode": case.get("returncode"),
                "note": "manifest",
            }
    return cases


def metadata_from_audit(audit: dict[str, Any], label: str) -> dict[str, Any]:
    cfg = load_config(ROOT / audit["config"])
    wind = cfg.get("wind", {})
    wind_generation = cfg.get("wind_generation", {})
    label_match = re.search(r"_U(?P<u>\d+)P(?P<frac>\d+)_SEED(?P<seed>\d+)", label)
    label_u_star = None
    label_seed = None
    if label_match:
        label_u_star = float(f"{int(label_match.group('u'))}.{label_match.group('frac')}")
        label_seed = int(label_match.group("seed"))
    return {
        "case_label": label,
        "u_star": float(wind_generation.get("u_star", wind.get("u_star", label_u_star or 0.0))),
        "seed": int(wind_generation.get("seed", wind.get("seed", label_seed or -1))),
        "L_m": float(cfg["geometry"].get("L")),
        "Sag_m": float(cfg["geometry"].get("Sag")),
        "config_path": audit["config"],
        "output_dir": audit["output_dir"],
        "status": "completed",
        "returncode": None,
        "note": "audit",
    }


def read_case_audits(audit_root: Path, manifest_cases: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for audit_path in sorted(audit_root.glob("*/time_step_coverage_audit.json")):
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        label = case_label_from_audit_dir(audit_path.parent)
        meta = manifest_cases.get(label) or metadata_from_audit(audit, label)
        row: dict[str, Any] = {
            **meta,
            "audit_path": str(audit_path.relative_to(ROOT)),
            "steps": int(audit["steps"]),
            "duration_s": float(audit["duration_s"]),
        }
        for criterion, summary in audit["summary"].items():
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


def summarize_by_ustar(case_rows: list[dict[str, Any]], failed_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    criteria = sorted(
        {
            key.removesuffix("__coverage")
            for row in case_rows
            for key in row
            if key.endswith("__coverage")
        }
    )
    u_values = sorted({float(row["u_star"]) for row in case_rows + failed_rows})
    summary_rows: list[dict[str, Any]] = []
    for u_star in u_values:
        completed = [row for row in case_rows if float(row["u_star"]) == u_star]
        failed = [row for row in failed_rows if float(row["u_star"]) == u_star]
        row: dict[str, Any] = {
            "u_star": u_star,
            "completed_n": len(completed),
            "failed_n": len(failed),
        }
        for criterion in criteria:
            values = [float(item[f"{criterion}__coverage"]) for item in completed]
            times = [float(item[f"{criterion}__time_true_s"]) for item in completed]
            longest = [float(item[f"{criterion}__longest_s"]) for item in completed]
            value_mean = mean(values)
            value_sem = sem(values)
            ci95 = 1.96 * value_sem
            row[f"{criterion}__mean_coverage"] = mean(values)
            row[f"{criterion}__std_coverage"] = stdev(values)
            row[f"{criterion}__sem_coverage"] = value_sem
            row[f"{criterion}__ci95_low_coverage"] = max(0.0, value_mean - ci95)
            row[f"{criterion}__ci95_high_coverage"] = min(1.0, value_mean + ci95)
            row[f"{criterion}__min_coverage"] = min(values) if values else 0.0
            row[f"{criterion}__max_coverage"] = max(values) if values else 0.0
            row[f"{criterion}__mean_time_true_s"] = mean(times)
            row[f"{criterion}__mean_longest_s"] = mean(longest)
        summary_rows.append(row)
    return summary_rows


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


def plot_curves(summary_rows: list[dict[str, Any]], out_dir: Path, criteria: list[str], filename: str) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        write_svg_curves(summary_rows, out_dir / filename.replace(".png", ".svg"), criteria)
        return

    x = [float(row["u_star"]) for row in summary_rows]
    plt.figure(figsize=(9, 5.5), dpi=160)
    for criterion in criteria:
        y = [float(row.get(f"{criterion}__mean_coverage", 0.0)) for row in summary_rows]
        low = [float(row.get(f"{criterion}__ci95_low_coverage", value)) for row, value in zip(summary_rows, y)]
        high = [float(row.get(f"{criterion}__ci95_high_coverage", value)) for row, value in zip(summary_rows, y)]
        plt.fill_between(x, low, high, alpha=0.12)
        plt.plot(x, y, marker="o", linewidth=1.8, label=criterion)
    plt.xlabel("u_star (m/s)")
    plt.ylabel("mean time-step coverage")
    plt.ylim(bottom=0.0)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(out_dir / filename)
    plt.close()


def write_svg_curves(summary_rows: list[dict[str, Any]], path: Path, criteria: list[str]) -> None:
    width, height = 900, 520
    margin = 70
    x_values = [float(row["u_star"]) for row in summary_rows]
    y_values = [
        float(row.get(f"{criterion}__mean_coverage", 0.0))
        for row in summary_rows
        for criterion in criteria
    ]
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = 0.0, max(y_values + [1.0e-9])
    colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#17becf"]

    def sx(value: float) -> float:
        return margin + (value - x_min) / (x_max - x_min) * (width - 2 * margin)

    def sy(value: float) -> float:
        return height - margin - (value - y_min) / (y_max - y_min) * (height - 2 * margin)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<line x1="{margin}" y1="{height-margin}" x2="{width-margin}" y2="{height-margin}" stroke="#333"/>',
        f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height-margin}" stroke="#333"/>',
        f'<text x="{width/2}" y="{height-20}" text-anchor="middle" font-family="Arial" font-size="16">u_star (m/s)</text>',
        f'<text x="22" y="{height/2}" text-anchor="middle" transform="rotate(-90 22 {height/2})" font-family="Arial" font-size="16">mean time-step coverage</text>',
    ]
    for idx, criterion in enumerate(criteria):
        color = colors[idx % len(colors)]
        points = [
            f"{sx(float(row['u_star'])):.2f},{sy(float(row.get(f'{criterion}__mean_coverage', 0.0))):.2f}"
            for row in summary_rows
        ]
        lines.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2"/>')
        for row in summary_rows:
            x = sx(float(row["u_star"]))
            mean_y = float(row.get(f"{criterion}__mean_coverage", 0.0))
            low_y = float(row.get(f"{criterion}__ci95_low_coverage", mean_y))
            high_y = float(row.get(f"{criterion}__ci95_high_coverage", mean_y))
            y = sy(mean_y)
            y_low = sy(low_y)
            y_high = sy(high_y)
            lines.append(f'<line x1="{x:.2f}" y1="{y_high:.2f}" x2="{x:.2f}" y2="{y_low:.2f}" stroke="{color}" stroke-width="1" opacity="0.5"/>')
            lines.append(f'<line x1="{x-4:.2f}" y1="{y_high:.2f}" x2="{x+4:.2f}" y2="{y_high:.2f}" stroke="{color}" stroke-width="1" opacity="0.5"/>')
            lines.append(f'<line x1="{x-4:.2f}" y1="{y_low:.2f}" x2="{x+4:.2f}" y2="{y_low:.2f}" stroke="{color}" stroke-width="1" opacity="0.5"/>')
            lines.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" fill="{color}"/>')
        lines.append(
            f'<text x="{width-margin-190}" y="{margin + 18 * idx}" font-family="Arial" font-size="12" fill="{color}">{criterion}</text>'
        )
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_markdown(
    summary_rows: list[dict[str, Any]],
    failed_rows: list[dict[str, Any]],
    criteria: list[str],
    path: Path,
) -> None:
    lines = [
        "# Fixed-L Broad u_star Time-Step Coverage Summary",
        "",
        "Geometry: `L = 322.8 m`, `Sag = 10.48 m`; time step `dt = 0.05 s`, target `4096` steps.",
        "",
        "## Mean Coverage By u_star",
        "",
        "| u_star | completed | failed | " + " | ".join(criteria) + " |",
        "|---:|---:|---:|" + "|".join(["---:" for _ in criteria]) + "|",
    ]
    for row in summary_rows:
        values = [
            f"{float(row.get(f'{criterion}__mean_coverage', 0.0)):.4f}"
            for criterion in criteria
        ]
        lines.append(
            f"| {float(row['u_star']):.3f} | {row['completed_n']} | {row['failed_n']} | "
            + " | ".join(values)
            + " |"
        )
    lines += [
        "",
        "## Core Criteria Uncertainty",
        "",
        "| u_star | completed | C2&C4 mean | C2&C4 95% CI | C4 mean | C4 95% CI | C6 mean | C6 95% CI |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    core = ["C2_and_C4", "C4_rolling_response_growth", "C6_large_response"]
    for row in summary_rows:
        vals = []
        for criterion in core:
            vals.append(f"{float(row.get(f'{criterion}__mean_coverage', 0.0)):.4f}")
            vals.append(
                f"{float(row.get(f'{criterion}__ci95_low_coverage', 0.0)):.4f}-{float(row.get(f'{criterion}__ci95_high_coverage', 0.0)):.4f}"
            )
        lines.append(
            f"| {float(row['u_star']):.3f} | {row['completed_n']} | "
            + " | ".join(vals)
            + " |"
        )
    lines += [
        "",
        "## Failed Or Non-Normal Cases",
        "",
        "| case | u_star | seed | note |",
        "|---|---:|---:|---|",
    ]
    if failed_rows:
        for row in failed_rows:
            lines.append(
                f"| {row['case_label']} | {float(row['u_star']):.3f} | {row.get('seed', '')} | {row.get('note', '')} |"
            )
    else:
        lines.append("| none |  |  |  |")
    lines += [
        "",
        "## Interpretation",
        "",
        "- `C2_sustained_negative_damping` measures time steps where enough element-level effective damping is negative.",
        "- `C4_rolling_response_growth` measures rolling p95 displacement growth and is sensitive to stochastic seed history.",
        "- `C6_large_response` measures displacement exceeding 10% of sag, so it rises when response amplitude becomes structurally large.",
        "- `C2_and_C4` is the most conservative coupled time-domain galloping marker in this batch.",
        "- `C7_clearance_limit` remains a placeholder clearance proxy and should not be used as a calibrated galloping limit yet.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-root", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--manifest", action="append", default=[])
    parser.add_argument("--extra-failed-case", action="append", default=[])
    args = parser.parse_args()

    out_dir = (ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_cases = load_manifest_cases([(ROOT / value).resolve() for value in args.manifest])
    failed_rows = [row for row in manifest_cases.values() if row["status"] == "failed"]
    failed_rows.extend(parse_extra_failed(value) for value in args.extra_failed_case)
    case_rows = read_case_audits((ROOT / args.audit_root).resolve(), manifest_cases)
    summary_rows = summarize_by_ustar(case_rows, failed_rows)
    criteria = sorted(
        {
            key.removesuffix("__coverage")
            for row in case_rows
            for key in row
            if key.endswith("__coverage")
        }
    )

    write_csv(case_rows, out_dir / "case_coverage.csv")
    write_csv(summary_rows, out_dir / "ustar_coverage_summary.csv")
    write_csv(failed_rows, out_dir / "failed_cases.csv")
    (out_dir / "ustar_coverage_summary.json").write_text(
        json.dumps(
            {"cases": case_rows, "summary": summary_rows, "failed_cases": failed_rows},
            indent=2,
        ),
        encoding="utf-8",
    )
    write_markdown(summary_rows, failed_rows, criteria, out_dir / "ustar_coverage_summary.md")

    plot_curves(summary_rows, out_dir, criteria, "coverage_curves_all.png")
    core_criteria = [criterion for criterion in criteria if criterion != "C7_clearance_limit"]
    plot_curves(summary_rows, out_dir, core_criteria, "coverage_curves_core.png")
    print(f"Wrote {out_dir / 'ustar_coverage_summary.md'}")


if __name__ == "__main__":
    main()
