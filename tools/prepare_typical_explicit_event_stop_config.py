from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
BASE_CONFIG = ROOT / "config" / "timur_dynamic_4096.yaml"
OUT_DIR = ROOT / "output" / "diagnostics" / "typical_explicit_event_stop"
CONFIG_PATH = OUT_DIR / "typical_L322P8_H10P48_U0P6_explicit_force_event_stop.yaml"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cfg = yaml.safe_load(BASE_CONFIG.read_text(encoding="utf-8"))

    span = 322.8
    sag = 10.48
    cfg["geometry"]["L"] = span
    cfg["geometry"]["Sag"] = sag
    cfg["time_history"]["folder_1"] = ["FORCE_3"]
    cfg["time_history"]["folder_2"] = ["SIM1"]
    cfg["time_history"]["dt"] = 0.05
    cfg["time_history"]["npt"] = 4096
    cfg.setdefault("damping", {})["global_rayleigh_scale"] = 1.0
    cfg["aerodynamic_damping"] = {
        "enabled": True,
        "writeback_mode": "record_only",
    }
    cfg["aerodynamic_force"] = {
        "enabled": True,
        "scale": 1.0,
        "log_stride": 1,
    }
    cfg["event_stop"] = {
        "enabled": True,
        "max_displacement_m": 0.5 * sag,
        "max_velocity_mps": 50.0,
        "max_acceleration_mps2": 5000.0,
        "min_effective_damping": -5.0,
        "rationale": (
            "Stop when the line has entered a severe galloping-response state, "
            "not at first negative damping. Displacement threshold is half sag; "
            "velocity and acceleration thresholds guard severe nonlinear response."
        ),
    }
    cfg["solver"]["opensees_path"] = r"D:\Pyprogramme\OpenSees3.8.0\bin\OpenSees.exe"
    cfg["paths"]["output_dir"] = "output/diagnostics/typical_explicit_event_stop/run"
    cfg["paths"]["save_prefix"] = "TYPICAL_EXPLICIT_EVENT_STOP"
    cfg.setdefault("display", {})["realtime_monitor"] = False

    CONFIG_PATH.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    print(CONFIG_PATH)


if __name__ == "__main__":
    main()
