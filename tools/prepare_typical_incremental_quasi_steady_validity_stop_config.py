from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
BASE_CONFIG = (
    ROOT
    / "output"
    / "diagnostics"
    / "typical_incremental_quasi_steady_no_stop"
    / "typical_L322P8_H10P48_U0P6_incremental_quasi_steady_no_stop.yaml"
)
OUT_DIR = ROOT / "output" / "diagnostics" / "typical_incremental_quasi_steady_validity_stop"
CONFIG_PATH = OUT_DIR / "typical_L322P8_H10P48_U0P6_incremental_quasi_steady_validity_stop.yaml"


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
    }
    cfg["aerodynamic_force"] = {
        "enabled": False,
        "scale": 1.0,
        "log_stride": 1,
    }
    cfg["quasi_steady_aero_force"] = {
        "enabled": False,
        "scale": 1.0,
        "log_stride": 1,
        "use_precomputed_loads": True,
    }
    cfg["event_stop"] = {
        "enabled": True,
        "max_displacement_m": 1.0e30,
        "max_velocity_mps": 1.0e30,
        "max_acceleration_mps2": 1.0e30,
        "min_effective_damping": -1.0e30,
        "max_alpha_deg": 29.9,
        "max_clipped_fraction": 0.05,
        "rationale": (
            "Stop once the real-time quasi-steady attack angle leaves the "
            "available aerodynamic coefficient table. This records entry into "
            "the severe galloping / out-of-validity-domain regime as a valid "
            "research output."
        ),
    }
    cfg["paths"]["output_dir"] = "output/diagnostics/typical_incremental_quasi_steady_validity_stop/run"
    cfg["paths"]["save_prefix"] = "TYPICAL_INCREMENTAL_QUASI_STEADY_VALIDITY_STOP"
    cfg.setdefault("display", {})["plotter"] = False
    cfg.setdefault("display", {})["modal_plotter"] = False
    cfg.setdefault("display", {})["realtime_monitor"] = False

    CONFIG_PATH.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    print(CONFIG_PATH)


if __name__ == "__main__":
    main()
