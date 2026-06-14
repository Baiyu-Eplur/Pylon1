from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
BASE_CONFIG = (
    ROOT
    / "output"
    / "diagnostics"
    / "c4_structural_model_comparison_200s"
    / "tension_only"
    / "tension_only.yaml"
)
OUT_ROOT = ROOT / "output" / "diagnostics" / "cable_rod_long_test"


def write_case(cfg: dict, case_name: str) -> Path:
    case_dir = OUT_ROOT / case_name
    case_dir.mkdir(parents=True, exist_ok=True)
    path = case_dir / f"{case_name}.yaml"
    path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    return path


def common_base() -> dict:
    cfg = yaml.safe_load(BASE_CONFIG.read_text(encoding="utf-8"))
    cfg["time_history"]["dt"] = 0.05
    cfg["time_history"]["npt"] = 4000
    cfg["event_stop"] = {
        "enabled": False,
        "rationale": (
            "Long-time physical-model comparison. No project-side active stop; "
            "the run should continue until target time or natural OpenSees failure."
        ),
    }
    cfg["diagnostics"]["element_strain_log_stride"] = 20
    cfg["incremental_quasi_steady_aero_force"]["log_stride"] = 20
    cfg.setdefault("display", {})["plotter"] = False
    cfg.setdefault("display", {})["modal_plotter"] = False
    cfg.setdefault("display", {})["realtime_monitor"] = False
    cfg["paths"]["save_prefix"] = "CABLE_ROD_LONG_TEST"
    return cfg


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    base = common_base()

    tension = deepcopy(base)
    tension["analysis"]["fiber_section"] = 2
    tension["analysis"].pop("compression_regularization_ratio", None)
    tension["analysis"]["structural_model"] = (
        "current tension-only: corotTruss + ElasticPPGap + InitStrainMaterial"
    )
    tension["analysis"]["comparison_hypothesis"] = (
        "Baseline taut-cable branch; physically prevents sustained compression."
    )
    tension["incremental_quasi_steady_aero_force"]["structural_model"] = (
        "current tension-only corotTruss"
    )
    tension["diagnostics"]["rationale"] = (
        "Cable/rod long-time comparison baseline: current tension-only truss branch."
    )
    tension["paths"]["output_dir"] = "output/diagnostics/cable_rod_long_test/current_tension_only/run"
    tension["paths"]["save_prefix"] = "CABLE_ROD_LONG_CURRENT_TENSION_ONLY"

    cable_rod = deepcopy(base)
    cable_rod["analysis"]["fiber_section"] = 3
    cable_rod["analysis"].pop("compression_regularization_ratio", None)
    cable_rod["analysis"]["structural_model"] = (
        "calibrated cable_rod: forceBeamColumn + Corotational + circular fiber section"
    )
    cable_rod["analysis"]["comparison_hypothesis"] = (
        "Adds conductor bending/torsion and a continuous low-tension rod path, "
        "while retaining audited EA, EI, GJ, mass, pretension, and gravity."
    )
    cable_rod["incremental_quasi_steady_aero_force"]["structural_model"] = (
        "calibrated cable_rod forceBeamColumn"
    )
    cable_rod["diagnostics"]["rationale"] = (
        "Cable/rod long-time comparison: calibrated beam/rod branch using the "
        "same physical section parameters as the audited conductor."
    )
    cable_rod["paths"]["output_dir"] = "output/diagnostics/cable_rod_long_test/calibrated_cable_rod/run"
    cable_rod["paths"]["save_prefix"] = "CABLE_ROD_LONG_CALIBRATED_CABLE_ROD"

    regularized = deepcopy(base)
    regularized["analysis"]["fiber_section"] = 4
    regularized["analysis"]["compression_regularization_ratio"] = 1.0e-4
    regularized["analysis"]["structural_model"] = (
        "regularized tension-only sensitivity: ElasticPPGap in parallel with "
        "1e-4 E elastic residual stiffness"
    )
    regularized["analysis"]["comparison_hypothesis"] = (
        "Sensitivity branch only. Tests whether the ideal zero-compression "
        "tangent of the pure tension-only truss creates a numerical mechanism."
    )
    regularized["incremental_quasi_steady_aero_force"]["structural_model"] = (
        "regularized tension-only corotTruss"
    )
    regularized["diagnostics"]["rationale"] = (
        "Cable/rod long-time comparison: small-compression regularization "
        "sensitivity branch, not a physical compressive conductor model."
    )
    regularized["paths"]["output_dir"] = "output/diagnostics/cable_rod_long_test/regularized_tension_only/run"
    regularized["paths"]["save_prefix"] = "CABLE_ROD_LONG_REGULARIZED_TENSION_ONLY"

    print(write_case(tension, "current_tension_only"))
    print(write_case(cable_rod, "calibrated_cable_rod"))
    print(write_case(regularized, "regularized_tension_only"))


if __name__ == "__main__":
    main()
