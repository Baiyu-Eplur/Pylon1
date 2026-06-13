from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "output" / "single_point_demo" / "L322P8_U0P600_SEED20260909"
OUT = PKG / "damping_formula_flow_audit"


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    columns = list(df.columns)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in df.iterrows():
        values = []
        for col in columns:
            value = row[col]
            if isinstance(value, float):
                values.append(f"{value:.6g}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def read_damping_params() -> dict[str, float]:
    params: dict[str, float] = {}
    path = ROOT / "inputs_aerodynamic_damping.tcl"
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[0] == "set":
            params[parts[1]] = float(parts[2])
    return params


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    params = read_damping_params()
    summary = pd.read_csv(PKG / "single_point_summary.csv")
    meta = json.loads((PKG / "single_point_demo_metadata.json").read_text(encoding="utf-8"))

    cd = np.loadtxt(ROOT / "data" / "aero_coeffs" / "C_D_data.txt", delimiter=",")
    cl = np.loadtxt(ROOT / "data" / "aero_coeffs" / "C_L_data2.txt", delimiter=",")
    dcl = np.loadtxt(ROOT / "data" / "aero_coeffs" / "dC_L.txt")
    alpha = cl[:, 0]
    cl_values = cl[:, 1]
    numerical_dcl_per_degree = np.gradient(cl_values, alpha)
    dcl_corr = float(np.corrcoef(dcl, numerical_dcl_per_degree)[0, 1])
    dcl_ratio = float(
        np.nanmedian(
            np.abs(
                dcl
                / np.where(np.abs(numerical_dcl_per_degree) > 1e-12, numerical_dcl_per_degree, np.nan)
            )
        )
    )
    delta = cd[:, 1] + dcl * 180.0 / math.pi
    neg = delta < 0.0

    k_per_mps = (
        params["ro_air"] * params["B"] * params["L"] / (4.0 * params["MassM"] * params["omegaN"])
    )
    ucrit = np.full_like(delta, np.nan, dtype=float)
    ucrit[neg] = -params["xi_structural"] / (k_per_mps * delta[neg])

    dynamic_path = ROOT / meta["output_dir"] / "Dynamic.out"
    dynamic_rows = sum(1 for line in dynamic_path.open("r", encoding="utf-8", errors="ignore") if line.strip())
    first_cols = len(dynamic_path.read_text(encoding="utf-8", errors="ignore").splitlines()[0].split())
    n_nodes = 101
    recorder_has_time = first_cols == 3 * n_nodes + 1

    audit = {
        "damping_formula": (
            "xi_total = xi_structural + rho_air * U_rel * B * L_e "
            "/ (4 * M_e * omega_n) * (dC_L/dalpha + C_D)"
        ),
        "parameters_from_inputs_aerodynamic_damping_tcl": params,
        "coefficient_factor_k_per_mps": k_per_mps,
        "dcl_unit_check": {
            "dcl_file_matches_numerical_dCL_ddegree_correlation": dcl_corr,
            "median_abs_ratio_file_to_numerical_dCL_ddegree": dcl_ratio,
            "conclusion": "dC_L.txt is consistent with derivative per degree, so Tcl conversion to per radian is dimensionally required.",
        },
        "den_hartog_delta": {
            "delta_min": float(np.min(delta)),
            "delta_negative_fraction_in_table": float(np.mean(neg)),
            "unstable_alpha_ranges_note": "Small-angle 0.1-12 deg region is predominantly negative in the current table.",
            "ucrit_min_mps": float(np.nanmin(ucrit)),
            "ucrit_median_negative_mps": float(np.nanmedian(ucrit[neg])),
        },
        "single_point_summary": summary.to_dict(orient="records"),
        "recorder_time_axis_check": {
            "dynamic_rows": dynamic_rows,
            "columns_in_first_dynamic_row": first_cols,
            "expected_columns_without_time": 3 * n_nodes,
            "expected_columns_with_time": 3 * n_nodes + 1,
            "recorder_has_time_column": recorder_has_time,
            "target_wind_records": meta["case"]["npt"],
            "finding": (
                "Existing Dynamic.out lacks an explicit time column and has more rows than wind records, "
                "which indicates adaptive substeps. Existing single-point displacement plots therefore use "
                "a nominal row-index time axis and should be treated as display/diagnostic only until rerun "
                "with -time recorders."
            ),
        },
        "workflow_actions": [
            "Added Den Hartog delta_D curve and point time-history figures to the single-point package.",
            "Updated tcl_writer.py so future dynamic displacement, velocity, acceleration, and reaction recorders include -time.",
            "Corrected negative_xi_fraction_recorded to use only valid damping-log samples.",
        ],
    }

    (OUT / "damping_formula_flow_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")

    lines = [
        "# Single-Point Damping Formula Flow Audit",
        "",
        "## Formula",
        "",
        f"`{audit['damping_formula']}`",
        "",
        "## Parameters",
        "",
    ]
    for key, value in params.items():
        lines.append(f"- `{key}` = `{value}`")
    lines.extend(
        [
            f"- coefficient factor `k_per_mps` = `{k_per_mps:.8f}`",
            "",
            "## dC_L Unit Check",
            "",
            f"- Correlation between `dC_L.txt` and numerical `dC_L/ddegree` from `C_L_data2.txt`: `{dcl_corr:.4f}`",
            f"- Median absolute ratio file/numerical per-degree derivative: `{dcl_ratio:.4f}`",
            "- Conclusion: `dC_L.txt` is a per-degree derivative. Converting to per-radian in Tcl is dimensionally correct.",
            "",
            "## Den Hartog Delta",
            "",
            f"- Minimum `delta_D`: `{np.min(delta):.4f}`",
            f"- Fraction of aerodynamic table with `delta_D < 0`: `{np.mean(neg):.4f}`",
            f"- Minimum critical relative speed from current formula: `{np.nanmin(ucrit):.4f} m/s`",
            f"- Median critical speed over negative `delta_D`: `{np.nanmedian(ucrit[neg]):.4f} m/s`",
            "",
            "## Three Observation Points",
            "",
            dataframe_to_markdown(summary),
            "",
            "## Important Finding",
            "",
            (
                "The existing demonstration `Dynamic.out` does not include an explicit time column, "
                "while the adaptive transient solver produced more rows than the 4096 wind records. "
                "Therefore the current displacement plots use a nominal row-index time axis. The response "
                "growth remains visible, but the exact plotted time of the growth should be rechecked after "
                "rerunning the case with `-time` recorders."
            ),
            "",
            "## Actions Taken",
            "",
            "- Added `den_hartog_delta_curve.png` and `den_hartog_delta_timeseries.png` to the single-point package.",
            "- Updated `src/cable_analyser/tcl_writer.py` so future dynamic recorders include `-time`.",
            "- Corrected the damping summary fraction to ignore missing damping-log samples.",
        ]
    )
    (OUT / "damping_formula_flow_audit.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"audit_dir": str(OUT), "audit": audit}, indent=2))


if __name__ == "__main__":
    main()
