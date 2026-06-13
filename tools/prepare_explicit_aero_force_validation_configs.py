from __future__ import annotations

import copy
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
BASE_CONFIG = ROOT / "config" / "timur_dynamic_4096.yaml"
OUT_ROOT = ROOT / "output" / "diagnostics" / "explicit_aero_force_validation"
CONFIG_DIR = OUT_ROOT / "configs"
RUN_DIR = OUT_ROOT / "runs"

CASES = [
    {
        "name": "F0_record_only_no_explicit_force",
        "enabled": False,
        "scale": 1.0,
        "note": "Baseline: global structural Rayleigh; aerodynamic damping recorded only.",
    },
    {
        "name": "F1_explicit_force_scale0",
        "enabled": True,
        "scale": 0.0,
        "note": "Null-force check: explicit force machinery enabled but force magnitude is zero.",
    },
    {
        "name": "F2_explicit_force_scale1",
        "enabled": True,
        "scale": 1.0,
        "note": "Physical-scale explicit aerodynamic damping force.",
    },
    {
        "name": "F3_explicit_force_scale10",
        "enabled": True,
        "scale": 10.0,
        "note": "Amplified sensitivity check to confirm monotonic response to the explicit force channel.",
    },
]


def main() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    cfg = yaml.safe_load(BASE_CONFIG.read_text(encoding="utf-8"))
    manifest = {
        "base_config": str(BASE_CONFIG.relative_to(ROOT)),
        "purpose": "Validate explicit velocity-dependent aerodynamic damping force.",
        "common_settings": {
            "L": cfg["geometry"]["L"],
            "Sag": cfg["geometry"]["Sag"],
            "force": cfg["time_history"]["folder_1"][0],
            "sim": cfg["time_history"]["folder_2"][0],
            "dt": cfg["time_history"]["dt"],
            "npt": 1024,
            "global_rayleigh_scale": 1.0,
            "damping_writeback_mode": "record_only",
        },
        "cases": [],
    }
    for spec in CASES:
        case_cfg = copy.deepcopy(cfg)
        case_cfg["time_history"]["npt"] = 1024
        case_cfg.setdefault("damping", {})["global_rayleigh_scale"] = 1.0
        case_cfg["aerodynamic_damping"] = {
            "enabled": True,
            "writeback_mode": "record_only",
        }
        case_cfg["aerodynamic_force"] = {
            "enabled": bool(spec["enabled"]),
            "scale": float(spec["scale"]),
            "log_stride": 1,
        }
        case_cfg["paths"]["output_dir"] = str((RUN_DIR / spec["name"]).relative_to(ROOT)).replace("\\", "/")
        case_cfg["paths"]["save_prefix"] = spec["name"]
        config_path = CONFIG_DIR / f"{spec['name']}.yaml"
        config_path.write_text(yaml.safe_dump(case_cfg, sort_keys=False), encoding="utf-8")
        manifest["cases"].append(
            {
                **spec,
                "config": str(config_path.relative_to(ROOT)),
                "output_dir": case_cfg["paths"]["output_dir"],
            }
        )

    (OUT_ROOT / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    print(OUT_ROOT / "manifest.yaml")


if __name__ == "__main__":
    main()
