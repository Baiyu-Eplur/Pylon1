from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output" / "diagnostics" / "quasi_steady_comparison"


def load_base() -> dict:
    with (ROOT / "config" / "timur_dynamic_4096.yaml").open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def common_typical_config(output_subdir: str) -> dict:
    cfg = load_base()
    cfg["geometry"]["type"] = 1
    cfg["geometry"]["L"] = 322.8
    cfg["geometry"]["Sag"] = 10.48
    cfg["geometry"]["discretisation"] = 3.228
    cfg["time_history"]["folder_1"] = ["FORCE_3"]
    cfg["time_history"]["folder_2"] = ["SIM1"]
    cfg["time_history"]["dt"] = 0.05
    cfg["time_history"]["npt"] = 4096
    cfg["damping"]["model"] = "Rayleigh"
    cfg["damping"]["xi"] = 0.01
    cfg["damping"]["global_rayleigh_scale"] = 1.0
    cfg["aerodynamic_damping"] = {
        "enabled": True,
        "writeback_mode": "record_only",
        "dcl_derivative_scale": 57.2957795131,
    }
    cfg["event_stop"] = {
        "enabled": False,
        "max_displacement_m": 1.0e30,
        "max_velocity_mps": 1.0e30,
        "max_acceleration_mps2": 1.0e30,
        "min_effective_damping": -1.0e30,
    }
    cfg["display"]["plotter"] = False
    cfg["display"]["modal_plotter"] = False
    cfg["display"]["realtime_monitor"] = False
    cfg["paths"]["forces_dir"] = "data/forces"
    cfg["paths"]["wind_dir"] = "data/wind/SIM1"
    cfg["paths"]["time_file"] = "data/aero_coeffs/time.txt"
    cfg["paths"]["output_dir"] = f"output/diagnostics/quasi_steady_comparison/{output_subdir}/run"
    return cfg


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    explicit_cfg = common_typical_config("explicit_damping")
    explicit_cfg["aerodynamic_force"] = {
        "enabled": True,
        "scale": 1.0,
        "log_stride": 1,
    }
    explicit_cfg["quasi_steady_aero_force"] = {
        "enabled": False,
        "scale": 1.0,
        "log_stride": 1,
        "use_precomputed_loads": True,
    }

    quasi_cfg = common_typical_config("quasi_steady_full_force")
    quasi_cfg["aerodynamic_force"] = {
        "enabled": False,
        "scale": 1.0,
        "log_stride": 1,
    }
    quasi_cfg["quasi_steady_aero_force"] = {
        "enabled": True,
        "scale": 1.0,
        "log_stride": 1,
        "use_precomputed_loads": False,
    }

    paths = {
        "explicit": OUT_DIR / "typical_explicit_damping_no_stop.yaml",
        "quasi_steady": OUT_DIR / "typical_quasi_steady_full_force_no_stop.yaml",
    }
    with paths["explicit"].open("w", encoding="utf-8") as f:
        yaml.safe_dump(explicit_cfg, f, sort_keys=False)
    with paths["quasi_steady"].open("w", encoding="utf-8") as f:
        yaml.safe_dump(quasi_cfg, f, sort_keys=False)
    for label, path in paths.items():
        print(f"{label}: {path}")


if __name__ == "__main__":
    main()
