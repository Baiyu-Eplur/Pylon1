"""Prepare extreme damping diagnostic configs for the typical model."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml


ROOT = Path("output/diagnostics/extreme_damping_controls")
BASE_CONFIG = Path(
    "output/diagnostics/strong_response_controls/configs/C_no_aero_damping_update.yaml"
)

CASES = {
    "D0_zero_global_rayleigh_xi0": {
        "xi": 0.0,
        "note": "Aerodynamic damping disabled; global Rayleigh mass term alpha should be zero.",
    },
    "D1_high_global_rayleigh_xi0p50": {
        "xi": 0.5,
        "note": "Aerodynamic damping disabled; intentionally high structural/global damping.",
    },
}


def main() -> None:
    base = yaml.safe_load(BASE_CONFIG.read_text(encoding="utf-8"))
    configs_dir = ROOT / "configs"
    runs_dir = ROOT / "runs"
    configs_dir.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)

    manifest = {"base_config": str(BASE_CONFIG), "cases": {}}
    for case_id, spec in CASES.items():
        cfg = deepcopy(base)
        cfg["damping"]["xi"] = float(spec["xi"])
        cfg["aerodynamic_damping"] = {
            "enabled": False,
            "dcl_derivative_scale": 180.0 / 3.141592653589793,
            "delta_D_min": -1.0e30,
            "delta_D_max": 1.0e30,
            "note": spec["note"],
        }
        cfg["paths"]["output_dir"] = str((runs_dir / case_id).resolve())
        cfg["paths"]["save_prefix"] = f"extreme_damping_{case_id}"
        cfg["display"]["realtime_monitor"] = False
        config_path = configs_dir / f"{case_id}.yaml"
        config_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
        manifest["cases"][case_id] = {
            "config": str(config_path),
            "output_dir": cfg["paths"]["output_dir"],
            "damping_xi": cfg["damping"]["xi"],
            "aerodynamic_damping": cfg["aerodynamic_damping"],
        }

    manifest_path = ROOT / "manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
