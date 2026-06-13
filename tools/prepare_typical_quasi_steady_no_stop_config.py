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
OUT_DIR = ROOT / "output" / "diagnostics" / "typical_quasi_steady_no_stop"
CONFIG_PATH = OUT_DIR / "typical_L322P8_H10P48_U0P6_quasi_steady_no_stop.yaml"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cfg = yaml.safe_load(BASE_CONFIG.read_text(encoding="utf-8"))

    # Keep geometry, material, wind case, solver, damping, and duration identical
    # to typical_explicit_no_stop. Only replace the aeroelastic force model.
    cfg["aerodynamic_force"] = {
        "enabled": False,
        "scale": 1.0,
        "log_stride": 1,
    }
    cfg["quasi_steady_aero_force"] = {
        "enabled": True,
        "scale": 1.0,
        "log_stride": 1,
        "use_precomputed_loads": False,
    }
    cfg["paths"]["output_dir"] = "output/diagnostics/typical_quasi_steady_no_stop/run"
    cfg["paths"]["save_prefix"] = "TYPICAL_QUASI_STEADY_NO_STOP"
    cfg.setdefault("display", {})["plotter"] = False
    cfg.setdefault("display", {})["modal_plotter"] = False
    cfg.setdefault("display", {})["realtime_monitor"] = False

    CONFIG_PATH.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    print(CONFIG_PATH)


if __name__ == "__main__":
    main()
