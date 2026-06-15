# Cable/Rod Long-Time Typical-Case Test Results

Date: 2026-06-14

Branch: `cable-rod-long-timeseries-test`

Purpose:

- Compare structural cable branches under the same typical geometry, gravity
  equilibrium route, and FORCE_3/SIM1 wind input.
- Do not use project-side event-stop limits.
- Continue each run until the requested 200 s target, natural OpenSees failure,
  or external runtime timeout.

Local output root:

```text
output/diagnostics/cable_rod_long_test
```

Key generated outputs:

```text
output/diagnostics/cable_rod_long_test/comparison/cable_rod_long_test_summary.json
output/diagnostics/cable_rod_long_test/comparison/cable_rod_long_test_core_comparison.png
output/diagnostics/cable_rod_long_test/comparison/current_tension_only_events.md
output/diagnostics/cable_rod_long_test/comparison/calibrated_cable_rod_events.md
output/diagnostics/cable_rod_long_test/comparison/regularized_tension_only_events.md
```

Each run directory also archives the Tcl input used by OpenSees:

```text
Input_modal.tcl
Input_time_history.tcl
inputs_aerodynamic_damping.tcl
```

## Run Status

| branch | structural model | reached time | status |
|---|---|---:|---|
| `current_tension_only` | `corotTruss + ElasticPPGap + InitStrainMaterial` | 117.608 s | external 2 h timeout; no OpenSees failure status written |
| `calibrated_cable_rod` | `forceBeamColumn + Corotational + circular fiber section` | 108.052 s | natural OpenSees failure, `ANALYZE_RETURN_CODE -3` |
| `regularized_tension_only` | tension-only with residual compression stiffness `1e-4 E` | 141.830 s | external 2 h timeout; no OpenSees failure status written |

The calibrated cable/rod branch failed naturally with:

```text
STATUS failed
MESSAGE analysis_did_not_converge_min_factor_reached
TIME 108.05175076831534
TARGET_TIME 200.0000
PROGRESS 54.02587538415767
ANALYZE_RETURN_CODE -3
FACTOR 6.657041767889234e-10
MIN_FACTOR 1e-06
```

## Earliest Event Chains

### Current Tension-Only

- first acceleration over `100 m/s2`: `88.350 s`;
- first velocity over `1 m/s`: `89.350 s`;
- first low-tension/slack/strain event: `89.736640 s`;
- first incremental QS force over `500 N`: `89.867828 s`;
- first attack-angle clipping: `90.455775 s`;
- first displacement over `2 m`: `90.779 s`.

Interpretation:

- The abnormal chain is still
  dynamic amplification -> low tension/slack -> local near-zero tangent
  mechanism -> large relative-flow angle -> increased aerodynamic correction.
- This branch avoids negative force by construction, but post-slack response is
  not physically resolved by the pure truss formulation.

### Calibrated Cable/Rod

- first acceleration over `100 m/s2`: `68.300 s`;
- first velocity over `1 m/s`: `68.650 s`;
- first incremental QS force over `500 N` and first attack-angle clipping:
  `69.518950 s`;
- first negative/low tension: `69.861189 s`;
- first displacement over `2 m`: `72.520 s`;
- natural OpenSees failure: `108.051751 s`.

Peak values before failure:

- maximum displacement: `9.475 m`;
- maximum velocity: `211.716 m/s`;
- minimum tension estimate: `-390.114 kN`;
- maximum absolute tension estimate: `952.130 kN`;
- maximum absolute strain estimate: `0.0210`;
- maximum total absolute incremental QS force: `36.956 kN`;
- maximum aerodynamic nodal power magnitude: `385.215 kW`.

Interpretation:

- This branch provides a continuous rod/beam path through low-tension states,
  but it also allows large compressive axial demand.
- Under the current aerodynamic and structural assumptions, it enters
  large-angle aerodynamics before the first recorded negative tension.
- It does not by itself solve the abnormal-response problem; instead it reveals
  a different post-taut-cable failure path involving large relative velocity,
  large-angle coefficient clipping, and severe convergence difficulty.

### Regularized Tension-Only Sensitivity

- first acceleration over `100 m/s2`: `88.400 s`;
- first velocity over `1 m/s`: `89.550 s`;
- first incremental QS force over `500 N`: `91.472550 s`;
- first low-tension/slack/negative residual-compression entry: `91.673316 s`;
- first attack-angle clipping: `91.710519 s`;
- first displacement over `2 m`: `92.365900 s`.

Peak values before external timeout:

- maximum displacement: `6.561 m`;
- maximum velocity: `41.529 m/s`;
- minimum tension estimate: `-218.633 N`;
- maximum absolute tension estimate: `926.437 kN`;
- maximum absolute strain estimate: `0.0497`;
- maximum slack count: `56`;
- maximum total absolute incremental QS force: `3.826 kN`.

Interpretation:

- The small residual compression stiffness delays and smooths the pure
  zero-tangent slack mechanism by about 1.9 s relative to the pure
  tension-only branch.
- It strongly limits the magnitude of recorded negative tension, as intended.
- It does not make post-slack response physically valid: large strain,
  many slack/low-tension elements, attack-angle clipping, and high force/power
  still occur.

## Main Conclusion

The problem is not solved by simply choosing one of the three tested structural
branches.

- Pure tension-only is better than allowing a cable to carry sustained
  compression, but after slack it creates a local mechanism with near-zero
  tangent stiffness.
- The calibrated beam/rod branch is more continuous and literature-consistent
  for low-tension modelling, but with the current single-line OpenSees model it
  permits large compressive axial demand and reaches non-convergence after
  large-angle aerodynamic amplification.
- The small-compression regularization is useful as a sensitivity check because
  it shows that the zero-compression tangent contributes to numerical
  sharpness, but it is not a physical post-slack model.

The next model improvement should not be an active stop limit. It should
improve the physical post-slack representation. Candidate next steps:

1. Keep a taut-cable galloping validity marker at first slack/low-tension
   onset, while separately developing a post-slack model.
2. Calibrate a cable/rod or ANCF-style branch against known low-tension cable
   dynamics rather than relying on the current simple `forceBeamColumn` branch.
3. Add a bounded large-angle aerodynamic coefficient model or post-stall
   coefficient table, because the current coefficient use reaches clipping in
   all branches after large relative velocity develops.
4. Add energy-consistency diagnostics around local element shortening,
   aerodynamic work, structural strain energy, and support reactions to
   separate physical galloping energy input from post-validity numerical
   amplification.
