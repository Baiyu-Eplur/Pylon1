"""Prepare E1-E4 damping writeback matrix configs."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml


ROOT = Path("output/diagnostics/damping_writeback_matrix")
BASE_CONFIG = Path(
    "output/diagnostics/strong_response_controls/configs/C_no_aero_damping_update.yaml"
)

CASES = {
    "E1_global0_element_structural": {
        "global_rayleigh_scale": 0.0,
        "enabled": False,
        "writeback_mode": "structural_only",
        "note": "global = 0, element writeback = xi_structural",
    },
    "E2_global_structural_record_only": {
        "global_rayleigh_scale": 1.0,
        "enabled": True,
        "writeback_mode": "record_only",
        "note": "global = xi_structural, element no writeback; record xi_total only",
    },
    "E3_global0_element_total": {
        "global_rayleigh_scale": 0.0,
        "enabled": True,
        "writeback_mode": "total",
        "note": "global = 0, element writeback = xi_structural + xi_aero(t)",
    },
    "E4_global_structural_element_aero": {
        "global_rayleigh_scale": 1.0,
        "enabled": True,
        "writeback_mode": "aero_only",
        "note": "global = xi_structural, element writeback = xi_aero(t)",
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
        cfg["damping"]["xi"] = 0.01
        cfg["damping"]["global_rayleigh_scale"] = float(spec["global_rayleigh_scale"])
        cfg["aerodynamic_damping"] = {
            "enabled": bool(spec["enabled"]),
            "dcl_derivative_scale": 180.0 / 3.141592653589793,
            "delta_D_min": -1.0e30,
            "delta_D_max": 1.0e30,
            "writeback_mode": spec["writeback_mode"],
            "note": spec["note"],
        }
        cfg["paths"]["output_dir"] = str((runs_dir / case_id).resolve())
        cfg["paths"]["save_prefix"] = f"damping_writeback_{case_id}"
        cfg["display"]["realtime_monitor"] = False

        config_path = configs_dir / f"{case_id}.yaml"
        config_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
        manifest["cases"][case_id] = {
            "config": str(config_path),
            "output_dir": cfg["paths"]["output_dir"],
            "global_rayleigh_scale": cfg["damping"]["global_rayleigh_scale"],
            "aerodynamic_damping": cfg["aerodynamic_damping"],
        }

    manifest_path = ROOT / "manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
