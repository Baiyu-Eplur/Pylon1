from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
BASE_CONFIG = (
    ROOT
    / "output"
    / "diagnostics"
    / "typical_incremental_qs_tension_only"
    / "typical_L322P8_H10P48_U0P6_incremental_qs_tension_only_90s.yaml"
)
OUT_DIR = ROOT / "output" / "diagnostics" / "typical_incremental_qs_c4_static_balance"
CONFIG_PATH = OUT_DIR / "typical_L322P8_H10P48_U0P6_incremental_qs_c4_static_balance_72s.yaml"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cfg = yaml.safe_load(BASE_CONFIG.read_text(encoding="utf-8"))

    cfg["analysis"]["fiber_section"] = 2
    cfg["analysis"]["pretension_load"] = 19785.0
    cfg["analysis"]["numbers_of_step_gravity"] = 20
    cfg["analysis"]["assume_initial_equilibrium"] = False
    cfg["analysis"].pop("load_const_after_assumed_equilibrium", None)
    cfg["analysis"]["initial_state_route"] = (
        "C4_static_gravity_equilibrium: ramp gravity in static analysis, "
        "then loadConst before transient"
    )

    cfg["time_history"]["dt"] = 0.05
    cfg["time_history"]["npt"] = 1440

    cfg["aerodynamic_damping"] = {
        "enabled": True,
        "writeback_mode": "record_only",
        "use_deformed_element_direction": True,
        "rationale": (
            "Record Den Hartog/effective-damping diagnostics while the active "
            "aerodynamic input is supplied by the incremental quasi-steady force branch."
        ),
    }
    cfg["aerodynamic_force"] = {
        "enabled": False,
        "scale": 1.0,
        "log_stride": 1,
        "rationale": "Old explicit equivalent-damping force is disabled.",
    }
    cfg["quasi_steady_aero_force"] = {
        "enabled": False,
        "scale": 1.0,
        "log_stride": 1,
        "use_precomputed_loads": True,
    }
    cfg["incremental_quasi_steady_aero_force"] = {
        "enabled": True,
        "scale": 1.0,
        "log_stride": 20,
        "keep_precomputed_loads": True,
        "force_component_convention": "match_original_path_load",
        "structural_model": "corotTruss + ElasticPPGap + InitStrainMaterial",
        "initial_state_route": "C4_static_gravity_equilibrium",
        "diagnostics": [
            "F_original",
            "F_reference",
            "F_current",
            "Delta_F_motion",
            "total_abs_delta_force",
            "per_node_delta_power",
            "per_node_current_drag_lift_power",
            "baseline_mapping_mismatch",
            "per_element_geometric_strain_and_EA_tension",
        ],
    }
    cfg["diagnostics"] = {
        "element_strain_log_stride": 20,
        "rationale": (
            "Formal typical galloping verification with C4 static initial balance; "
            "record force decomposition, nodal power, element strain/tension, "
            "and standard displacement/velocity/acceleration histories."
        ),
    }
    cfg["event_stop"] = {
        "enabled": False,
        "rationale": (
            "No active project-side stop. The run should continue until the "
            "requested duration or natural OpenSees failure, with status/logs recorded."
        ),
    }
    cfg["solver"]["opensees_path"] = r"D:\Pyprogramme\OpenSees3.8.0\bin\OpenSees.exe"
    cfg["paths"]["output_dir"] = "output/diagnostics/typical_incremental_qs_c4_static_balance/run"
    cfg["paths"]["save_prefix"] = "TYPICAL_INCREMENTAL_QS_C4_STATIC_BALANCE"
    cfg.setdefault("display", {})["plotter"] = False
    cfg.setdefault("display", {})["modal_plotter"] = False
    cfg.setdefault("display", {})["realtime_monitor"] = False

    CONFIG_PATH.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    print(CONFIG_PATH)


if __name__ == "__main__":
    main()
