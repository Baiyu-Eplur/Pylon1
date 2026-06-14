from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
BASE_CONFIG = (
    ROOT
    / "output"
    / "diagnostics"
    / "typical_incremental_qs_c4_static_balance"
    / "typical_L322P8_H10P48_U0P6_incremental_qs_c4_static_balance_72s.yaml"
)
OUT_DIR = ROOT / "output" / "diagnostics" / "typical_incremental_qs_c4_bidirectional_axial"
CONFIG_PATH = OUT_DIR / "typical_L322P8_H10P48_U0P6_incremental_qs_c4_bidirectional_axial_72s.yaml"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cfg = yaml.safe_load(BASE_CONFIG.read_text(encoding="utf-8"))

    cfg["analysis"]["fiber_section"] = 1
    cfg["analysis"]["structural_model"] = (
        "forceBeamColumn + Elastic + InitStrainMaterial; axial force can be "
        "positive or negative in the section response"
    )
    cfg["analysis"]["comparison_hypothesis"] = (
        "Rollback of the third correction only: allow local negative axial force "
        "while retaining C4 static gravity balance and incremental QS aerodynamic loading."
    )

    cfg["incremental_quasi_steady_aero_force"]["structural_model"] = (
        "forceBeamColumn + Elastic + InitStrainMaterial"
    )
    cfg["incremental_quasi_steady_aero_force"]["diagnostic_question"] = (
        "Does allowing bidirectional axial force produce a more physically "
        "interpretable galloping response than the tension-only branch?"
    )

    cfg["diagnostics"]["rationale"] = (
        "Third-correction rollback test. Keep the corrected damping, force "
        "superposition, and C4 gravity/static-equilibrium workflow, but use the "
        "bidirectional axial forceBeamColumn cable model to test whether local "
        "negative axial force is a useful physical proxy in special cases."
    )

    cfg["paths"]["output_dir"] = "output/diagnostics/typical_incremental_qs_c4_bidirectional_axial/run"
    cfg["paths"]["save_prefix"] = "TYPICAL_INCREMENTAL_QS_C4_BIDIRECTIONAL_AXIAL"

    CONFIG_PATH.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    print(CONFIG_PATH)


if __name__ == "__main__":
    main()
