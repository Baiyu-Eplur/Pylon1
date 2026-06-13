from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
BASE_CONFIG = (
    ROOT
    / "output"
    / "diagnostics"
    / "typical_explicit_no_stop"
    / "typical_L322P8_H10P48_U0P6_explicit_force_no_stop.yaml"
)
OUT_DIR = ROOT / "output" / "diagnostics" / "typical_directional_explicit_no_stop"
CONFIG_PATH = OUT_DIR / "typical_L322P8_H10P48_U0P6_directional_explicit_no_stop.yaml"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cfg = yaml.safe_load(BASE_CONFIG.read_text(encoding="utf-8"))

    # Keep the original dynamic wind-force workflow and explicit aerodynamic
    # damping force. Only change the local-flow calculation so attack angle and
    # damping use the deformed element direction at each OpenSees step.
    cfg["aerodynamic_damping"] = {
        **cfg.get("aerodynamic_damping", {}),
        "enabled": True,
        "writeback_mode": "record_only",
        "use_deformed_element_direction": True,
    }
    cfg["aerodynamic_force"] = {
        "enabled": True,
        "scale": 1.0,
        "log_stride": 1,
    }
    cfg["quasi_steady_aero_force"] = {
        "enabled": False,
        "scale": 1.0,
        "log_stride": 1,
        "use_precomputed_loads": True,
    }
    cfg["paths"]["output_dir"] = "output/diagnostics/typical_directional_explicit_no_stop/run"
    cfg["paths"]["save_prefix"] = "TYPICAL_DIRECTIONAL_EXPLICIT_NO_STOP"
    cfg.setdefault("display", {})["plotter"] = False
    cfg.setdefault("display", {})["modal_plotter"] = False
    cfg.setdefault("display", {})["realtime_monitor"] = False

    CONFIG_PATH.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    print(CONFIG_PATH)


if __name__ == "__main__":
    main()
