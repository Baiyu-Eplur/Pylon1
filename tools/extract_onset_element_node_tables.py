from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "output" / "diagnostics" / "typical_incremental_qs_mapping_fixed_power_strain"
RUN = CASE / "run"
OUT = CASE / "analysis" / "onset_root_cause_69s"


def extract_elements() -> None:
    keep_elements = {40, 41, 42, 43, 44, 45, 46, 47}
    keep_times = [69.45, 69.50, 69.55, 69.60, 69.65, 69.70, 69.75]
    rows_by_time: dict[float, list[dict[str, str]]] = {t: [] for t in keep_times}
    with (RUN / "element_strain_tension_log.csv").open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            t = float(row["time"])
            if t < 69.40:
                continue
            if t > 69.78:
                break
            element = int(float(row["element"]))
            if element not in keep_elements:
                continue
            nearest = min(keep_times, key=lambda x: abs(x - t))
            if abs(nearest - t) < 0.012:
                row["_nearest"] = f"{nearest:.2f}"
                rows_by_time[nearest].append(row)
    out = OUT / "critical_element_strain_tension_samples.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "sample_time",
            "actual_time",
            "element",
            "strain",
            "delta_tension_N",
            "estimated_total_tension_N",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for sample in keep_times:
            # Keep only one row per actual element closest to the sample.
            best: dict[int, dict[str, str]] = {}
            for row in rows_by_time[sample]:
                element = int(float(row["element"]))
                if element not in best or abs(float(row["time"]) - sample) < abs(float(best[element]["time"]) - sample):
                    best[element] = row
            for element in sorted(best):
                row = best[element]
                writer.writerow(
                    {
                        "sample_time": f"{sample:.2f}",
                        "actual_time": row["time"],
                        "element": row["element"],
                        "strain": row["strain"],
                        "delta_tension_N": row["delta_tension_N"],
                        "estimated_total_tension_N": row["estimated_total_tension_N"],
                    }
                )
    print(out)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    extract_elements()
