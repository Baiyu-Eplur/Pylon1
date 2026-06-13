from __future__ import annotations

from copy import deepcopy
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
OUT_DIR = ROOT / "output" / "diagnostics" / "tension_only_control_verification"
CONFIG_DIR = OUT_DIR / "configs"


def no_wind_no_aero_config(base: dict) -> dict:
    cfg = deepcopy(base)
    cfg["analysis"]["type"] = "TH"
    cfg["analysis"]["fiber_section"] = 2
    cfg["time_history"]["dt"] = 0.05
    cfg["time_history"]["npt"] = 600
    cfg["solver"]["opensees_path"] = r"D:\Pyprogramme\OpenSees3.8.0\bin\OpenSees.exe"
    cfg.setdefault("display", {})["plotter"] = False
    cfg.setdefault("display", {})["modal_plotter"] = False
    cfg.setdefault("display", {})["realtime_monitor"] = False

    cfg["aerodynamic_damping"] = {
        "enabled": False,
        "writeback_mode": "record_only",
        "use_deformed_element_direction": True,
        "rationale": "Control verification: no aerodynamic damping or aero-force feedback.",
    }
    cfg["aerodynamic_force"] = {"enabled": False, "scale": 1.0, "log_stride": 1}
    cfg["quasi_steady_aero_force"] = {
        "enabled": False,
        "scale": 1.0,
        "log_stride": 1,
        "use_precomputed_loads": False,
    }
    cfg["incremental_quasi_steady_aero_force"] = {
        "enabled": False,
        "scale": 1.0,
        "log_stride": 1,
        "keep_precomputed_loads": False,
        "force_component_convention": "match_original_path_load",
        "rationale": "Control verification: original Path loads and incremental QS loads both disabled.",
    }
    cfg["event_stop"] = {
        "enabled": False,
        "rationale": "Control verification: do not actively stop; record natural OpenSees result.",
    }
    cfg["diagnostics"] = {
        "element_strain_log_stride": 1,
        "rationale": "Dense strain/tension diagnostics for no-wind control verification.",
    }
    cfg["paths"]["save_prefix"] = "TENSION_ONLY_CONTROL"
    return cfg


def build_configs() -> dict[str, Path]:
    base = yaml.safe_load(BASE_CONFIG.read_text(encoding="utf-8"))
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    cases: dict[str, dict] = {}

    c1 = no_wind_no_aero_config(base)
    c1["analysis"]["pretension_load"] = 19785.0
    c1["analysis"]["multiplier_vertical_load"] = 1.0
    c1["analysis"]["assume_initial_equilibrium"] = True
    c1["paths"]["output_dir"] = "output/diagnostics/tension_only_control_verification/runs/C1_gravity_on_pretension_on_assumed_eq"
    cases["C1_gravity_on_pretension_on_assumed_eq"] = c1

    c2 = no_wind_no_aero_config(base)
    c2["analysis"]["pretension_load"] = 0.0
    c2["analysis"]["multiplier_vertical_load"] = 1.0
    c2["analysis"]["assume_initial_equilibrium"] = False
    c2["analysis"]["numbers_of_step_gravity"] = 20
    c2["paths"]["output_dir"] = "output/diagnostics/tension_only_control_verification/runs/C2_gravity_on_pretension_off_static_attempt"
    cases["C2_gravity_on_pretension_off_static_attempt"] = c2

    c3 = no_wind_no_aero_config(base)
    c3["analysis"]["pretension_load"] = 19785.0
    c3["analysis"]["multiplier_vertical_load"] = 0.0
    c3["analysis"]["assume_initial_equilibrium"] = True
    c3["paths"]["output_dir"] = "output/diagnostics/tension_only_control_verification/runs/C3_gravity_off_pretension_on_assumed_eq"
    cases["C3_gravity_off_pretension_on_assumed_eq"] = c3

    c4 = no_wind_no_aero_config(base)
    c4["analysis"]["pretension_load"] = 19785.0
    c4["analysis"]["multiplier_vertical_load"] = 1.0
    c4["analysis"]["assume_initial_equilibrium"] = False
    c4["analysis"]["numbers_of_step_gravity"] = 20
    c4["paths"]["output_dir"] = "output/diagnostics/tension_only_control_verification/runs/C4_gravity_on_pretension_on_static_equilibrium"
    cases["C4_gravity_on_pretension_on_static_equilibrium"] = c4

    c5 = no_wind_no_aero_config(base)
    c5["analysis"]["pretension_load"] = 19785.0
    c5["analysis"]["initial_tension_mode"] = "catenary_horizontal_component"
    c5["analysis"]["multiplier_vertical_load"] = 1.0
    c5["analysis"]["assume_initial_equilibrium"] = True
    c5["paths"]["output_dir"] = "output/diagnostics/tension_only_control_verification/runs/C5_gravity_on_shape_pretension_constant_gravity"
    cases["C5_gravity_on_shape_pretension_constant_gravity"] = c5

    c6 = no_wind_no_aero_config(base)
    c6["analysis"]["pretension_load"] = 0.0
    c6["analysis"]["multiplier_vertical_load"] = 1.0
    c6["analysis"]["assume_initial_equilibrium"] = True
    c6["paths"]["output_dir"] = "output/diagnostics/tension_only_control_verification/runs/C6_gravity_on_pretension_off_constant_gravity"
    cases["C6_gravity_on_pretension_off_constant_gravity"] = c6

    c7 = no_wind_no_aero_config(base)
    c7["analysis"]["pretension_load"] = 0.0
    c7["analysis"]["multiplier_vertical_load"] = 1.0
    c7["analysis"]["assume_initial_equilibrium"] = True
    c7["analysis"]["load_const_after_assumed_equilibrium"] = False
    c7["paths"]["output_dir"] = "output/diagnostics/tension_only_control_verification/runs/C7_gravity_on_no_pretension_no_loadconst"
    cases["C7_gravity_on_no_pretension_no_loadconst"] = c7

    c8 = no_wind_no_aero_config(base)
    c8["analysis"]["pretension_load"] = 19785.0
    c8["analysis"]["initial_tension_mode"] = "catenary_horizontal_component"
    c8["analysis"]["multiplier_vertical_load"] = 1.0
    c8["analysis"]["assume_initial_equilibrium"] = True
    c8["analysis"]["load_const_after_assumed_equilibrium"] = False
    c8["paths"]["output_dir"] = "output/diagnostics/tension_only_control_verification/runs/C8_gravity_on_shape_pretension_no_loadconst"
    cases["C8_gravity_on_shape_pretension_no_loadconst"] = c8

    paths: dict[str, Path] = {}
    for name, cfg in cases.items():
        path = CONFIG_DIR / f"{name}.yaml"
        path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
        paths[name] = path
    return paths


def main() -> None:
    paths = build_configs()
    for name, path in paths.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
