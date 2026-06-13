from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
BASE_CONFIG = (
    ROOT
    / "output"
    / "diagnostics"
    / "typical_incremental_quasi_steady_formal_no_stop"
    / "typical_L322P8_H10P48_U0P6_incremental_quasi_steady_formal_no_stop.yaml"
)
OUT_DIR = ROOT / "output" / "diagnostics" / "typical_incremental_qs_mapping_fixed_power_strain"
CONFIG_PATH = OUT_DIR / "typical_L322P8_H10P48_U0P6_incremental_qs_mapping_fixed_power_strain.yaml"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cfg = yaml.safe_load(BASE_CONFIG.read_text(encoding="utf-8"))
    cfg["time_history"]["dt"] = 0.05
    cfg["time_history"]["npt"] = 4096
    cfg["incremental_quasi_steady_aero_force"] = {
        "enabled": True,
        "scale": 1.0,
        "log_stride": 1,
        "keep_precomputed_loads": True,
        "force_component_convention": "match_original_path_load",
        "diagnostics": [
            "per_node_delta_power",
            "per_node_current_drag_lift_power",
            "baseline_mapping_mismatch",
            "per_element_geometric_strain_and_EA_tension",
        ],
    }
    cfg["event_stop"] = {
        "enabled": False,
        "rationale": (
            "No active project-side stop. This rerun checks the corrected "
            "Path-load force-component convention plus node power and element "
            "strain/tension diagnostics."
        ),
    }
    cfg["solver"]["opensees_path"] = r"D:\Pyprogramme\OpenSees3.8.0\bin\OpenSees.exe"
    cfg["paths"]["output_dir"] = "output/diagnostics/typical_incremental_qs_mapping_fixed_power_strain/run"
    cfg["paths"]["save_prefix"] = "TYPICAL_INCREMENTAL_QS_MAPPING_FIXED_POWER_STRAIN"
    cfg.setdefault("display", {})["plotter"] = False
    cfg.setdefault("display", {})["modal_plotter"] = False
    cfg.setdefault("display", {})["realtime_monitor"] = False
    CONFIG_PATH.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    print(CONFIG_PATH)


if __name__ == "__main__":
    main()
