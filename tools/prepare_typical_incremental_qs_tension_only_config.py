from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
BASE_CONFIG = (
    ROOT
    / "output"
    / "diagnostics"
    / "typical_incremental_qs_mapping_fixed_power_strain"
    / "typical_L322P8_H10P48_U0P6_incremental_qs_mapping_fixed_power_strain.yaml"
)
OUT_DIR = ROOT / "output" / "diagnostics" / "typical_incremental_qs_tension_only"
CONFIG_PATH = OUT_DIR / "typical_L322P8_H10P48_U0P6_incremental_qs_tension_only_90s.yaml"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cfg = yaml.safe_load(BASE_CONFIG.read_text(encoding="utf-8"))
    cfg["analysis"]["fiber_section"] = 2
    cfg["analysis"]["assume_initial_equilibrium"] = True
    cfg["time_history"]["dt"] = 0.05
    cfg["time_history"]["npt"] = 1440
    cfg["incremental_quasi_steady_aero_force"] = {
        "enabled": True,
        "scale": 1.0,
        "log_stride": 100,
        "keep_precomputed_loads": True,
        "force_component_convention": "match_original_path_load",
        "structural_model": "corotTruss + ElasticPPGap + InitStrainMaterial",
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
            "No active project-side stop. This diagnostic run checks whether "
            "the tension-only corotTruss cable model removes negative tension "
            "near the previous 69 s abnormal-response onset."
        ),
    }
    cfg["diagnostics"] = {
        "element_strain_log_stride": 100,
        "rationale": (
            "Reduced heavy diagnostic-log frequency for 90 s verification; "
            "OpenSees displacement, velocity, and acceleration recorders remain active."
        ),
    }
    cfg["solver"]["opensees_path"] = r"D:\Pyprogramme\OpenSees3.8.0\bin\OpenSees.exe"
    cfg["paths"]["output_dir"] = "output/diagnostics/typical_incremental_qs_tension_only/run_v7_72s"
    cfg["paths"]["save_prefix"] = "TYPICAL_INCREMENTAL_QS_TENSION_ONLY"
    cfg.setdefault("display", {})["plotter"] = False
    cfg.setdefault("display", {})["modal_plotter"] = False
    cfg.setdefault("display", {})["realtime_monitor"] = False
    CONFIG_PATH.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    print(CONFIG_PATH)


if __name__ == "__main__":
    main()
