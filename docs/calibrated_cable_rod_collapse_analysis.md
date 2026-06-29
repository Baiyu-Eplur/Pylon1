# Calibrated Cable/Rod Collapse Analysis

Date: 2026-06-29

Run analysed:

```text
output/diagnostics/cable_rod_long_test/calibrated_cable_rod_monitoring_v2/run
```

Analysis output:

```text
output/diagnostics/cable_rod_long_test/comparison/calibrated_cable_rod_monitoring_v2_collapse_cause
```

## Monitoring Completeness

The first calibrated cable/rod run had all major structural and aerodynamic
diagnostics except free-stream wind speed as an explicit node-level output
column. The monitoring was therefore expanded and the same model was rerun
without any active project-side termination limit.

The rerun now contains:

- displacement, velocity, and acceleration histories;
- support reactions;
- element strain/tension summary and per-element strain/tension records;
- total incremental quasi-steady aerodynamic force records;
- node-level current/reference/delta aerodynamic force;
- node-level aerodynamic power;
- node-level free-stream wind components `wind_y`, `wind_z`, and `U_wind`;
- node-level relative-flow components `rel_y`, `rel_z`, `U_rel`;
- node-level `alpha_deg`, `ref_alpha_deg`, `CD`, `CL`, and clipping flag;
- effective damping/Den Hartog diagnostic log;
- OpenSees solver status and failure code.

The monitoring update changed only the log columns. It did not change the
structural model, aerodynamic force calculation, or solver settings. The rerun
failed at the same physical time and with the same OpenSees reason as the
previous calibrated cable/rod case:

```text
STATUS failed
MESSAGE analysis_did_not_converge_min_factor_reached
TIME 108.05175076831534
ANALYZE_RETURN_CODE -3
FACTOR 6.657041767889234e-10
MIN_FACTOR 1e-06
```

## Event Sequence

The ordered critical events are:

| event | time |
|---|---:|
| key-node acceleration exceeds `100 m/s2` | `68.550000 s` |
| key-node velocity exceeds `1 m/s` | `68.650000 s` |
| incremental QS force exceeds `500 N` | `69.518950 s` |
| first alpha clipping | `69.518950 s` |
| first negative/low tension | `69.861189 s` |
| element strain exceeds `0.001` | `70.518784 s` |
| aerodynamic power exceeds `1000 W` | `71.399952 s` |
| aerodynamic power exceeds `10000 W` | `97.406480 s` |
| element strain exceeds `0.01` | `107.739246 s` |
| element absolute tension exceeds `500 kN` | `107.811040 s` |
| OpenSees failure | `108.051751 s` |

Important peak values:

- maximum key-node displacement: about `9.41 m` at midspan;
- maximum key-node velocity: about `75.10 m/s` at midspan;
- maximum key-node acceleration: about `6.17e4 m/s2` near the quarter point;
- maximum total incremental QS force: about `36.96 kN`;
- maximum absolute total aerodynamic power: about `874.78 kW`;
- maximum element absolute tension estimate: about `952.13 kN`;
- minimum element tension estimate: about `-390.11 kN`;
- initial horizontal support reaction was about `19.8 kN`; near failure it
  reached about `481-517 kN`.

## Direct Cause

The direct cause of the final calculation failure is nonlinear OpenSees
non-convergence in a severe coupled aero-structural state. It is not an input
file error and not an artificial project-side stop.

Immediately before failure:

- relative velocity becomes extremely large at key locations;
- attack angle is already in or near the coefficient clipping range for many
  nodes;
- current aerodynamic force grows far above the original/reference wind load;
- aerodynamic power oscillates with very large positive and negative values;
- element axial demand localizes strongly near the support region;
- support reactions and element forces amplify together;
- adaptive substepping reduces the increment factor below the minimum allowed
  value, producing OpenSees `ANALYZE_RETURN_CODE -3`.

## Root-Cause Interpretation

The earliest abnormal chain is not the final OpenSees convergence failure.
The meaningful physical/model-development chain is:

```text
motion acceleration begins increasing around 68.5 s
-> relative-flow correction increases
-> attack angle reaches the coefficient clipping regime around 69.52 s
-> negative/low tension appears around 69.86 s
-> displacement and velocity grow
-> aerodynamic work and axial force become very large
-> near-support element tension/compression localizes
-> OpenSees cannot converge at 108.05 s
```

The root issue is therefore a coupled modelling problem:

1. The calibrated `forceBeamColumn` branch gives a continuous beam/rod path
   through low-tension states, but it also allows large compressive axial
   demand. This is not a validated post-slack conductor model.
2. The current quasi-steady aerodynamic coefficient use reaches large-angle
   clipping. Once the cable velocity becomes large, the calculation operates
   outside the validated small/moderate-angle Den Hartog galloping regime.
3. The response becomes highly model-branch sensitive after the taut-cable
   state is lost. This means the post-taut/post-slack behaviour is not yet a
   reliable physical prediction.
4. The strongest final element force localization occurs near the support-side
   elements, so support modelling, element formulation, and low-tension
   cable/rod transition must be audited before accepting the result as a
   physical galloping response.

## Proposed Model Improvements

No active displacement, velocity, force, alpha, or slack termination limit
should be added. The next improvements should change the physics or numerical
formulation, not hide the response.

Recommended next steps:

1. Keep first low-tension/slack as a post-processing validity marker for the
   taut-cable galloping regime, not as an active stop.
2. Develop a post-taut cable model that does not allow arbitrary sustained
   compression but also does not collapse into a zero-tangent mechanism. The
   candidate direction is a cable/rod or ANCF-style formulation with bending,
   geometric nonlinearity, and a calibrated unilateral or tension-field axial
   law.
3. Replace coefficient clipping with a physically justified large-angle
   aerodynamic model. This may require post-stall or 0-180 degree coefficient
   data for the selected conductor/ice shape, or a validated dynamic-stall /
   galloping coefficient model.
4. Audit the support/end-region modelling because the largest final axial
   localization appears near the support-side elements rather than only at
   midspan.
5. Add energy consistency diagnostics: structural kinetic energy proxy,
   strain-energy proxy, aerodynamic work, support work, and damping work. This
   will distinguish real galloping energy input from numerical or formulation
   amplification.
6. Run controlled sensitivity tests after each physics update: same wind input,
   same geometry, no active stop, and full monitoring.
