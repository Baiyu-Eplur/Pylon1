from __future__ import annotations

import copy
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "output" / "diagnostics" / "opensees_3p8_rerun_L322P8_U0P600_SEED20260909" / "config.yaml"
OUT = ROOT / "output" / "diagnostics" / "strong_response_controls"


CASES = {
    "A_dcl_scale_1_no_rad_conversion": {
        "enabled": True,
        "dcl_derivative_scale": 1.0,
        "delta_D_min": -1.0e30,
        "delta_D_max": 1.0e30,
        "note": "Treat dC_L table as already in formula units; no 180/pi amplification.",
    },
    "B_dcl_rad_scale_delta_cap_minus2": {
        "enabled": True,
        "dcl_derivative_scale": 57.29577951308232,
        "delta_D_min": -2.0,
        "delta_D_max": 1.0e30,
        "note": "Keep per-radian conversion but cap Delta_D lower bound at -2.0.",
    },
    "C_no_aero_damping_update": {
        "enabled": False,
        "dcl_derivative_scale": 57.29577951308232,
        "delta_D_min": -1.0e30,
        "delta_D_max": 1.0e30,
        "note": "Disable adaptive aerodynamic damping; retain external wind force histories.",
    },
}


def main() -> None:
    base = yaml.safe_load(BASE.read_text(encoding="utf-8"))
    config_dir = OUT / "configs"
    config_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"base_config": str(BASE.relative_to(ROOT)), "cases": []}

    for label, aero in CASES.items():
        cfg = copy.deepcopy(base)
        cfg["aerodynamic_damping"] = dict(aero)
        cfg["paths"]["output_dir"] = str((OUT / "runs" / label).resolve())
        cfg["paths"]["save_prefix"] = f"strong_response_control_{label}"
        cfg["solver"]["opensees_path"] = r"D:\Pyprogramme\OpenSees3.8.0\bin\OpenSees.exe"
        cfg["wind_generation"]["reuse_existing"] = True
        cfg["wind_generation"]["overwrite"] = False
        path = config_dir / f"{label}.yaml"
        path.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
        manifest["cases"].append(
            {
                "label": label,
                "config_path": str(path.relative_to(ROOT)),
                "output_dir": cfg["paths"]["output_dir"],
                "aerodynamic_damping": cfg["aerodynamic_damping"],
            }
        )

    (OUT / "manifest.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(OUT / "manifest.yaml")


if __name__ == "__main__":
    main()
