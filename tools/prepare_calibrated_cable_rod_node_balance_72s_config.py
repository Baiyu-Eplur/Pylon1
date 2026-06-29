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
    / "calibrated_cable_rod_monitoring_v2"
    / "calibrated_cable_rod_monitoring_v2.yaml"
)
OUT_DIR = ROOT / "output" / "diagnostics" / "cable_rod_long_test" / "calibrated_cable_rod_node_balance_72s_v2"


def main() -> None:
    cfg = deepcopy(yaml.safe_load(BASE_CONFIG.read_text(encoding="utf-8")))
    cfg["time_history"]["dt"] = 0.05
    cfg["time_history"]["npt"] = 1440
    cfg["paths"]["output_dir"] = (
        "output/diagnostics/cable_rod_long_test/calibrated_cable_rod_node_balance_72s_v2/run"
    )
    cfg["paths"]["save_prefix"] = "CABLE_ROD_NODE_BALANCE_72S_V2"
    cfg.setdefault("diagnostics", {})["node_force_balance_enabled"] = True
    cfg["diagnostics"]["node_force_balance_log_stride"] = 1
    cfg["diagnostics"]["element_strain_log_stride"] = 1
    cfg["incremental_quasi_steady_aero_force"]["log_stride"] = 1
    cfg["diagnostics"]["rationale"] = (
        "Focused 72 s diagnostic run. No response-based active stop; target "
        "duration only covers the first abnormal acceleration / alpha-onset "
        "window. Records node force balance every successful OpenSees step."
    )
    cfg["event_stop"] = {
        "enabled": False,
        "rationale": (
            "No project-side active stop. This diagnostic uses a fixed target "
            "duration of 72 s, not a response threshold."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "calibrated_cable_rod_node_balance_72s_v2.yaml"
    path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
