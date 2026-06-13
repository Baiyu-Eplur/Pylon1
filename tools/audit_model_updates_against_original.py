from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = Path(r"D:\Uob\Tower Pylon\TIMUR2")
OUT = ROOT / "output" / "diagnostics" / "model_update_audit"

CASES = [
    {
        "key": "v1_incremental_before_force_mapping_fix",
        "label": "V1 incremental QS before force-transfer fix",
        "run": ROOT / "output/diagnostics/typical_incremental_quasi_steady_formal_no_stop/run",
        "config": ROOT / "output/diagnostics/typical_incremental_quasi_steady_formal_no_stop/typical_L322P8_H10P48_U0P6_incremental_quasi_steady_formal_no_stop.yaml",
        "model_note": "forceBeamColumn cable; incremental QS branch before later Path-load component mapping/power-strain diagnostics",
    },
    {
        "key": "v2_mapping_fixed_beam",
        "label": "V2 mapping-fixed incremental QS, beam-column cable",
        "run": ROOT / "output/diagnostics/typical_incremental_qs_mapping_fixed_power_strain/run",
        "config": ROOT / "output/diagnostics/typical_incremental_qs_mapping_fixed_power_strain/typical_L322P8_H10P48_U0P6_incremental_qs_mapping_fixed_power_strain.yaml",
        "model_note": "forceBeamColumn cable; Path-load convention fixed; node power and element strain/tension logs added",
    },
    {
        "key": "v3_tension_only",
        "label": "V3 tension-only incremental QS",
        "run": ROOT / "output/diagnostics/typical_incremental_qs_tension_only/run_v7_72s",
        "config": ROOT / "output/diagnostics/typical_incremental_qs_tension_only/typical_L322P8_H10P48_U0P6_incremental_qs_tension_only_90s.yaml",
        "model_note": "corotTruss + ElasticPPGap + InitStrainMaterial tension-only cable; same FORCE_3/SIM1 input; 72 s target",
    },
]

POINTS = [("quarter_1", "1/4 span", 26), ("midspan", "Midspan", 51), ("quarter_3", "3/4 span", 76)]


def read_status(path: Path) -> dict[str, str]:
    status_path = path / "analysis_status.txt"
    if not status_path.exists():
        return {"STATUS": "not_recorded"}
    result: dict[str, str] = {}
    for line in status_path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            result[parts[0]] = parts[1]
    return result


def load_matrix(path: Path) -> np.ndarray | None:
    if not path.exists() or path.stat().st_size == 0:
        return None
    data = np.loadtxt(path)
    return data[np.newaxis, :] if data.ndim == 1 else data


def node_cols(node_id: int) -> tuple[int, int, int]:
    start = 1 + (node_id - 1) * 3
    return start, start + 1, start + 2


def force_log(path: Path) -> dict[str, float]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    first = path.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    if first.startswith("time "):
        arr = np.genfromtxt(path, names=True, encoding="utf-8")
        names = arr.dtype.names or ()
        get = lambda name, default=np.nan: np.asarray(arr[name], dtype=float) if name in names else np.array([default])
    else:
        raw = np.loadtxt(path)
        if raw.ndim == 1:
            raw = raw[np.newaxis, :]
        names = (
            "time",
            "F_original",
            "F_reference",
            "F_current",
            "Delta_F_motion",
            "total_abs_delta_force",
            "max_abs_delta_force",
            "scale",
            "max_alpha_reference_deg",
            "max_alpha_current_deg",
            "clipped_count",
            "node_count",
        )
        data = {name: raw[:, idx] for idx, name in enumerate(names[: raw.shape[1]])}
        get = lambda name, default=np.nan: data.get(name, np.array([default]))
    out = {
        "force_time_end_s": float(np.nanmax(get("time"))),
        "max_F_current_N": float(np.nanmax(get("F_current"))),
        "max_total_abs_delta_force_N": float(np.nanmax(get("total_abs_delta_force"))),
        "max_max_abs_delta_force_N": float(np.nanmax(get("max_abs_delta_force"))),
        "max_alpha_current_deg": float(np.nanmax(get("max_alpha_current_deg"))),
        "max_clipped_count": int(np.nanmax(get("clipped_count", 0.0))),
    }
    if not math.isnan(float(np.nanmax(get("total_delta_power")))):
        out["max_total_delta_power_W"] = float(np.nanmax(get("total_delta_power")))
        out["min_total_delta_power_W"] = float(np.nanmin(get("total_delta_power")))
    return out


def tension_log(run: Path) -> dict[str, float | int]:
    path = run / "element_strain_tension_summary_log.csv"
    if not path.exists() or path.stat().st_size == 0:
        return {}
    arr = np.genfromtxt(path, delimiter=",", names=True, encoding="utf-8")
    names = arr.dtype.names or ()
    result: dict[str, float | int] = {
        "tension_log_time_end_s": float(np.nanmax(arr["time"])),
    }
    if "min_estimated_tension_N" in names:
        result["min_estimated_tension_N"] = float(np.nanmin(arr["min_estimated_tension_N"]))
        result["slack_log_count_total"] = int(np.nansum(arr["slack_element_count"])) if "slack_element_count" in names else 0
        after69 = arr[arr["time"] >= 69.0]
        if after69.size:
            result["min_estimated_tension_after69_N"] = float(np.nanmin(after69["min_estimated_tension_N"]))
            result["slack_log_count_after69"] = int(np.nansum(after69["slack_element_count"])) if "slack_element_count" in names else 0
    elif "max_abs_tension_N" in names:
        detail = run / "element_strain_tension_log.csv"
        if detail.exists():
            rows = np.genfromtxt(detail, delimiter=",", names=True, encoding="utf-8")
            if "estimated_total_tension_N" in (rows.dtype.names or ()):
                result["min_estimated_tension_N"] = float(np.nanmin(rows["estimated_total_tension_N"]))
                result["negative_tension_rows"] = int(np.sum(rows["estimated_total_tension_N"] < 0.0))
                after69 = rows[rows["time"] >= 69.0]
                if after69.size:
                    result["min_estimated_tension_after69_N"] = float(np.nanmin(after69["estimated_total_tension_N"]))
                    result["negative_tension_rows_after69"] = int(np.sum(after69["estimated_total_tension_N"] < 0.0))
    if "max_abs_tension_N" in names:
        result["max_abs_tension_N"] = float(np.nanmax(arr["max_abs_tension_N"]))
    if "max_abs_strain" in names:
        result["max_abs_strain"] = float(np.nanmax(arr["max_abs_strain"]))
    return result


def parse_original_input() -> dict[str, Any]:
    input_tcl = ORIGINAL / "Input.tcl"
    text = input_tcl.read_text(encoding="utf-8", errors="replace")
    return {
        "original_root": str(ORIGINAL),
        "primary_structure_generators": [
            str(ORIGINAL / "MODAL.m"),
            str(ORIGINAL / "TH_Updating.m"),
            str(ORIGINAL / "CABLE_ANALYSER_Updating.m"),
        ],
        "primary_wind_generator": str(ORIGINAL / "WIND_SIMULATION.mlx"),
        "primary_generated_tcl": str(input_tcl),
        "primary_aero_damping_tcl": str(ORIGINAL / "Damping_shifter.tcl"),
        "force_input_dir": str(ORIGINAL / "FORCES_UPDATING_COEFFS/FORCE_3/SIM1"),
        "node_count": len(re.findall(r"^node\s+", text, flags=re.MULTILINE)),
        "forceBeamColumn_count": text.count("element forceBeamColumn"),
        "corotTruss_count": text.count("element corotTruss"),
        "elasticPPGap_count": text.count("ElasticPPGap"),
        "path_timeseries_count": text.count("timeSeries Path"),
        "has_H_drag": "H_drag" in text,
        "has_H_lift": "H_lift" in text,
        "has_V_drag": "V_drag" in text,
        "has_V_lift": "V_lift" in text,
        "rayleigh_line": next((line.strip() for line in text.splitlines() if line.strip().startswith("rayleigh ")), ""),
        "dynamic_source": next((line.strip() for line in text.splitlines() if "dynamic2.tcl" in line), ""),
        "load_mapping": {
            "H_drag": "DOF2, factor 1000",
            "H_lift": "DOF3, factor 1000",
            "V_drag": "DOF3, factor 1000",
            "V_lift": "DOF2, factor 1000",
        },
    }


def summarize_case(case: dict[str, Any]) -> dict[str, Any]:
    run = case["run"]
    cfg = yaml.safe_load(case["config"].read_text(encoding="utf-8"))
    dyn = load_matrix(run / "Dynamic.out")
    vel = load_matrix(run / "Velocity.out")
    acc = load_matrix(run / "Accel.out")
    row: dict[str, Any] = {
        "key": case["key"],
        "label": case["label"],
        "run": str(run),
        "config": str(case["config"]),
        "model_note": case["model_note"],
        "fiber_section": cfg.get("analysis", {}).get("fiber_section"),
        "assume_initial_equilibrium": cfg.get("analysis", {}).get("assume_initial_equilibrium", False),
        "damping_model": cfg.get("damping", {}).get("model"),
        "damping_xi": cfg.get("damping", {}).get("xi"),
        "aero_damping_writeback_mode": cfg.get("aerodynamic_damping", {}).get("writeback_mode"),
        "incremental_qs_enabled": cfg.get("incremental_quasi_steady_aero_force", {}).get("enabled", False),
        "keep_precomputed_loads": cfg.get("incremental_quasi_steady_aero_force", {}).get("keep_precomputed_loads", None),
        "force_component_convention": cfg.get("incremental_quasi_steady_aero_force", {}).get("force_component_convention", ""),
    }
    row.update({f"status_{k}": v for k, v in read_status(run).items()})
    if dyn is not None:
        t = dyn[:, 0]
        row["dynamic_time_end_s"] = float(t[-1])
        row["dynamic_records"] = int(len(t))
        vals = dyn[:, 1:]
        row["max_abs_global_disp_m"] = float(np.nanmax(np.abs(vals)))
        for _key, label, node in POINTS:
            _, cy, cz = node_cols(node)
            row[f"{label}_max_abs_y_disp_m"] = float(np.nanmax(np.abs(dyn[:, cy])))
            row[f"{label}_max_abs_z_disp_m"] = float(np.nanmax(np.abs(dyn[:, cz])))
    if vel is not None:
        row["max_abs_global_vel_mps"] = float(np.nanmax(np.abs(vel[:, 1:])))
    if acc is not None:
        row["max_abs_global_accel_mps2"] = float(np.nanmax(np.abs(acc[:, 1:])))
    row.update(force_log(run / "incremental_quasi_steady_aero_force_log.txt"))
    row.update(tension_log(run))
    return row


def plot_midspan(cases: list[dict[str, Any]]) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(12, 7.5), dpi=170, sharex=True)
    colors = ["#7A3F98", "#2E6FBB", "#B84A62"]
    for case, color in zip(cases, colors):
        dyn = load_matrix(case["run"] / "Dynamic.out")
        if dyn is None:
            continue
        _, cy, cz = node_cols(51)
        mask = dyn[:, 0] <= 72.0
        axes[0].plot(dyn[mask, 0], dyn[mask, cy], lw=0.85, label=case["key"], color=color)
        axes[1].plot(dyn[mask, 0], dyn[mask, cz], lw=0.85, label=case["key"], color=color)
    axes[0].set_title("Midspan response comparison, common 0-72 s window")
    axes[0].set_ylabel("transverse displacement y (m)")
    axes[1].set_ylabel("vertical displacement z (m)")
    axes[1].set_xlabel("time (s)")
    for ax in axes:
        ax.grid(True, alpha=0.25)
        ax.legend(loc="best", fontsize=8)
        ax.axvspan(69.0, 70.0, color="#B84A62", alpha=0.10)
    fig.tight_layout()
    fig.savefig(OUT / "midspan_response_three_versions.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 5.8), dpi=170)
    for case, color in zip(cases, colors):
        log = case["run"] / "incremental_quasi_steady_aero_force_log.txt"
        if not log.exists():
            continue
        first = log.read_text(encoding="utf-8", errors="replace").splitlines()[0]
        if first.startswith("time "):
            arr = np.genfromtxt(log, names=True, encoding="utf-8")
            t = arr["time"]
            y = arr["total_abs_delta_force"]
        else:
            raw = np.loadtxt(log)
            t = raw[:, 0]
            y = raw[:, 5]
        mask = t <= 72.0
        ax.plot(t[mask], y[mask], lw=0.85, label=case["key"], color=color)
    ax.set_title("Incremental motion-correction force comparison")
    ax.set_ylabel("total_abs_delta_force (N)")
    ax.set_xlabel("time (s)")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best", fontsize=8)
    ax.axvspan(69.0, 70.0, color="#B84A62", alpha=0.10)
    fig.tight_layout()
    fig.savefig(OUT / "incremental_force_three_versions.png")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    original = parse_original_input()
    rows = [summarize_case(case) for case in CASES]
    plot_midspan(CASES)

    (OUT / "original_model_reference.json").write_text(json.dumps(original, indent=2), encoding="utf-8")
    (OUT / "three_version_comparison.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with (OUT / "three_version_comparison.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    md: list[str] = []
    md.append("# Model-Update Audit Against Original Timur Workflow")
    md.append("")
    md.append("## Permanent Original-Model Reference")
    md.append("")
    md.append(f"- Original project root: `{original['original_root']}`")
    md.append(f"- Wind/force generator: `{original['primary_wind_generator']}`")
    md.append(f"- Generated Tcl reference: `{original['primary_generated_tcl']}`")
    md.append(f"- Original damping Tcl: `{original['primary_aero_damping_tcl']}`")
    md.append(f"- Original FORCE_3/SIM1 data: `{original['force_input_dir']}`")
    md.append("")
    md.append("Original generated model facts:")
    md.append(f"- Nodes: `{original['node_count']}`")
    md.append(f"- `forceBeamColumn` elements: `{original['forceBeamColumn_count']}`")
    md.append(f"- `corotTruss` elements: `{original['corotTruss_count']}`")
    md.append(f"- Path load time series: `{original['path_timeseries_count']}`")
    md.append(f"- Rayleigh line: `{original['rayleigh_line']}`")
    md.append("- Load convention: `H_drag` and `V_lift` to OpenSees DOF 2; `H_lift` and `V_drag` to DOF 3; all with factor 1000.")
    md.append("- Original `CABLE_ANALYSER_Updating.m` uses `E = 82 GPa` and `Pretention_load = 0`; the current research typical configs use Zebra ACSR `E = 69 GPa` and `pretension_load = 19.785 kN`.")
    md.append("- Original `TH_Updating.m` writes Rayleigh damping with both mass and stiffness terms (`rayleigh alpha 0 beta 0`); the active Python writer currently uses mass-proportional Rayleigh only (`rayleigh alpha 0 0 0`).")
    md.append("")
    md.append("## Three-Version Result Summary")
    md.append("")
    md.append("| Version | Status | End time (s) | Max global disp (m) | Max global vel (m/s) | Max global accel (m/s^2) | Max total abs Delta F (N) | Min tension after 69s (N) | Negative/slack after 69s |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for row in rows:
        status = row.get("status_STATUS", "not_recorded")
        neg_slack = row.get("negative_tension_rows_after69", row.get("slack_log_count_after69", "n/a"))
        md.append(
            f"| {row['key']} | {status} | {row.get('dynamic_time_end_s', float('nan')):.3f} | "
            f"{row.get('max_abs_global_disp_m', float('nan')):.4g} | {row.get('max_abs_global_vel_mps', float('nan')):.4g} | "
            f"{row.get('max_abs_global_accel_mps2', float('nan')):.4g} | {row.get('max_total_abs_delta_force_N', float('nan')):.4g} | "
            f"{row.get('min_estimated_tension_after69_N', float('nan')):.4g} | {neg_slack} |"
        )
    md.append("")
    md.append("## Audit Conclusions")
    md.append("")
    md.append("1. The original Timur model is preserved as the fixed reference listed above. It uses `forceBeamColumn` cable elements, precomputed Path wind loads, and element damping update via `setElementRayleighDampingFactors`.")
    md.append("2. The damping change is necessary because damping writeback alone changes a solver damping coefficient after a step and does not by itself represent a physically explicit velocity-dependent aerodynamic force in the current time-step equation. The current branch keeps `adapt_damp` as a recorder (`record_only`) and injects the aeroelastic feedback through an explicit incremental quasi-steady force.")
    md.append("3. The force-superposition change is necessary because full real-time QS replacement double-counts or removes the static precomputed wind scenario. The adopted equation is `F_path + (F_current - F_reference)`, preserving the original weather/load scenario while adding only motion-induced aeroelastic correction.")
    md.append("4. The force-component mapping change is necessary because OpenSees Path loads define `Fy = H_drag + V_lift` and `Fz = H_lift + V_drag`; the corrected branch now matches that convention.")
    md.append("5. The tension-only element change is necessary because the previous beam-column cable can carry nonphysical compression. V2 shows negative estimated cable tension after 69 s; V3 has no negative estimated tension after 69 s and represents compression demand as slack/zero tension.")
    md.append("6. V3 is mechanically more correct than V1/V2 for a cable, but its large late response and axial strain are not yet automatically realistic. The next scientific check should focus on axial extensibility/inextensibility, conductor strength/validity limits, and whether the current pretension/sag and QS force assumptions remain valid in the large-response regime.")
    md.append("7. Workflow caveat: V3 uses `assume_initial_equilibrium=true` to avoid the singular partial-gravity load path of a tension-only cable. This is physically defensible only if the initial geometry, pretension, and self-weight are already a consistent found shape. Because `loadConst -time 0.0` follows a skipped static analysis, gravity-load equivalence to the original workflow must be explicitly revalidated before treating V3 amplitudes as final quantitative results.")
    md.append("8. Workflow caveat: the current research baseline intentionally differs from the original Timur input in material modulus, pretension, and Rayleigh damping formulation. These may be justified research updates, but they are not part of the three recent galloping-mechanism fixes and should be documented or re-run in a parameter-matched audit if exact original-model comparison is required.")
    md.append("")
    md.append("Generated figures:")
    md.append("- `midspan_response_three_versions.png`")
    md.append("- `incremental_force_three_versions.png`")
    (OUT / "model_update_audit_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(OUT / "model_update_audit_report.md")
    print(OUT / "three_version_comparison.csv")
    print(OUT / "midspan_response_three_versions.png")
    print(OUT / "incremental_force_three_versions.png")


if __name__ == "__main__":
    main()
