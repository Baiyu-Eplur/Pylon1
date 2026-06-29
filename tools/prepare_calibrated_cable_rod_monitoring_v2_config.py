from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
BASE_CONFIG = (
    ROOT
    / "output"
    / "diagnostics"
    / "cable_rod_long_test"
    / "calibrated_cable_rod"
    / "calibrated_cable_rod.yaml"
)
OUT_DIR = ROOT / "output" / "diagnostics" / "cable_rod_long_test" / "calibrated_cable_rod_monitoring_v2"


def main() -> None:
    cfg = deepcopy(yaml.safe_load(BASE_CONFIG.read_text(encoding="utf-8")))
    cfg["paths"]["output_dir"] = (
        "output/diagnostics/cable_rod_long_test/calibrated_cable_rod_monitoring_v2/run"
    )
    cfg["paths"]["save_prefix"] = "CABLE_ROD_LONG_CALIBRATED_CABLE_ROD_MONITORING_V2"
    cfg["diagnostics"]["rationale"] = (
        "Re-run of calibrated cable_rod with expanded node-level aerodynamic "
        "monitoring: free-stream wind components, U_wind, reference alpha, "
        "relative-flow components, equivalent aerodynamic loads, and power."
    )
    cfg["incremental_quasi_steady_aero_force"]["monitoring_update"] = (
        "Node power log includes wind_y, wind_z, U_wind, ref_alpha_deg, rel_y, rel_z."
    )
    cfg["event_stop"] = {
        "enabled": False,
        "rationale": (
            "No project-side active stop. Continue until target duration or "
            "natural OpenSees failure while recording expanded monitoring."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "calibrated_cable_rod_monitoring_v2.yaml"
    path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
