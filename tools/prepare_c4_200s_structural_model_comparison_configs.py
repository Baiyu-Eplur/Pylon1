from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
BASE_TENSION_ONLY = (
    ROOT
    / "output"
    / "diagnostics"
    / "typical_incremental_qs_c4_static_balance"
    / "typical_L322P8_H10P48_U0P6_incremental_qs_c4_static_balance_72s.yaml"
)
OUT_ROOT = ROOT / "output" / "diagnostics" / "c4_structural_model_comparison_200s"


def write_case(cfg: dict, case_name: str) -> Path:
    case_dir = OUT_ROOT / case_name
    case_dir.mkdir(parents=True, exist_ok=True)
    path = case_dir / f"{case_name}.yaml"
    path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    return path


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    base = yaml.safe_load(BASE_TENSION_ONLY.read_text(encoding="utf-8"))

    common = deepcopy(base)
    common["time_history"]["dt"] = 0.05
    common["time_history"]["npt"] = 4000
    common["event_stop"] = {
        "enabled": False,
        "rationale": (
            "No active project-side stop. The 200 s comparison should continue "
            "until the requested duration or natural OpenSees failure."
        ),
    }
    common.setdefault("display", {})["plotter"] = False
    common.setdefault("display", {})["modal_plotter"] = False
    common.setdefault("display", {})["realtime_monitor"] = False

    tension = deepcopy(common)
    tension["analysis"]["fiber_section"] = 2
    tension["analysis"]["structural_model"] = (
        "corotTruss + ElasticPPGap + InitStrainMaterial"
    )
    tension["analysis"]["comparison_hypothesis"] = (
        "200 s continuation of the current physical tension-only cable branch."
    )
    tension["incremental_quasi_steady_aero_force"]["structural_model"] = (
        "corotTruss + ElasticPPGap + InitStrainMaterial"
    )
    tension["diagnostics"]["rationale"] = (
        "200 s structural-model comparison: tension-only branch, same wind and "
        "same incremental QS aerodynamic force as the bidirectional axial branch."
    )
    tension["paths"]["output_dir"] = (
        "output/diagnostics/c4_structural_model_comparison_200s/"
        "tension_only/run"
    )
    tension["paths"]["save_prefix"] = "C4_200S_TENSION_ONLY"

    bidir = deepcopy(common)
    bidir["analysis"]["fiber_section"] = 1
    bidir["analysis"]["structural_model"] = (
        "forceBeamColumn + Elastic + InitStrainMaterial"
    )
    bidir["analysis"]["comparison_hypothesis"] = (
        "200 s rollback test of the third correction: allow positive and "
        "negative axial force while keeping C4 balance and incremental QS force."
    )
    bidir["incremental_quasi_steady_aero_force"]["structural_model"] = (
        "forceBeamColumn + Elastic + InitStrainMaterial"
    )
    bidir["diagnostics"]["rationale"] = (
        "200 s structural-model comparison: bidirectional axial branch, same wind "
        "and same incremental QS aerodynamic force as the tension-only branch."
    )
    bidir["paths"]["output_dir"] = (
        "output/diagnostics/c4_structural_model_comparison_200s/"
        "bidirectional_axial/run"
    )
    bidir["paths"]["save_prefix"] = "C4_200S_BIDIRECTIONAL_AXIAL"

    print(write_case(tension, "tension_only"))
    print(write_case(bidir, "bidirectional_axial"))


if __name__ == "__main__":
    main()
