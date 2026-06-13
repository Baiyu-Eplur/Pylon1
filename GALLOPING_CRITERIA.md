# Galloping Criteria Design

Last updated: 2026-06-02

This file defines the first production set of parallel galloping criteria. The
criteria should be evaluated independently over time. They should not be
collapsed into a single intersection rule at this stage, because the research
goal is to compare their coverage, sensitivity, conservatism, and usefulness
for extracting the critical `u_star` and span-length boundary.

## Source Logic

- Week 7 lecture: galloping is low-frequency, large-amplitude aeroelastic
  instability. The Den Hartog mechanism treats motion-dependent aerodynamic
  force as aerodynamic damping; negative total damping produces exponential
  growth in the linear stage.
- Timur baseline: use friction velocity `u_star`, Kaimal spectrum, Davenport
  coherence, updating aerodynamic coefficients, and time-history demand
  metrics.
- Chabart and Lilien / Rossi et al.: Den Hartog is a vertical-galloping screen;
  Nigol/Clarke and torsional coupling matter for future ice/bundle extensions.
- Zulli/Piccardo/Luongo and Ferretti et al.: stability/eigenvalue and nonlinear
  shallow-cable response should be used as higher-level boundary checks.
- EN 1991-1-4: keep wind definitions explicit. Report the relation between
  `u_star`, simulated mean wind, and Eurocode-style reference wind quantities.
- EN 50341 / National Grid RICA: use clearance, phase spacing, span range, and
  clashing context as engineering consequence criteria, separate from physical
  galloping onset.
- IEC 60826 / EN 50182: use conductor strength, reliability context, and
  conductor data consistency as limit-state and metadata checks.

## Principle

Each run should produce a time-resolved criterion report:

```text
criterion_id
triggered: true/false
first_trigger_time_s
last_trigger_time_s
duration_s or fraction
severity metric
supporting nodes/elements
notes
```

For boundary extraction, each criterion can yield its own coverage function and
derived critical boundary:

```text
coverage_Ci(u_star, L, cable_structure)
u_star_crit_by_Ci_p(L, cable_structure, p)
L_crit_by_Ci_p(u_star, cable_structure, p)
```

Later we can compare or combine criteria, but the first sweep should store all
criteria independently as coverage values. Critical boundaries are iso-coverage
post-processing results, not the only target.

## Criterion Set

### C0: Input And Standard-Range Context

Purpose: classify whether the run belongs to a physically/design-relevant
scenario before judging galloping.

Reason for selection:

- Galloping boundaries are only meaningful when wind definition, terrain
  context, span length, sag, conductor type, and design limit states are stated
  consistently.
- EN 1991-1-4 uses a specific reference-wind definition, while this project uses
  `u_star` and simulated conductor-height wind histories. C0 prevents confusing
  these wind measures.
- EN 50341 / National Grid RICA provide practical overhead-line span,
  clearance, and phase-separation context. IEC 60826 and the Rossi et al. paper
  show why static design checks should be recorded but cannot replace dynamic
  galloping checks.

References:

- EN 1991-1-4 official/catalog source recorded in `RESEARCH_PLAN.md`.
- EN 50341-1 official/catalog source recorded in `RESEARCH_PLAN.md`.
- IEC 60826 official source recorded in `RESEARCH_PLAN.md`.
- National Grid RICA Preliminary Design Considerations, recorded in
  `RESEARCH_PLAN.md`.
- Rossi et al. 2020, extracted text
  `output/reference_extraction/1-s2.0-S0167610520301811-main.txt`.

Time basis: run-level metadata, not a dynamic trigger.

Metrics:

- `u_star`
- mean wind profile and representative mean wind speed
- span length `L`
- sag and sag/span ratio
- conductor type, diameter, self-weight, rated strength
- assumed ice/aerodynamic coefficient state
- roughness length / terrain context

Tags:

- `within_rica_galloping_wind_context`
- `within_design_span_context`
- `outside_reference_range`

Use:

- Do not reject runs. Use this criterion to mark interpretation confidence.

### C1: Den Hartog Aerodynamic Susceptibility

Purpose: identify time/element states where the aerodynamic coefficient slope is
capable of vertical galloping.

Reason for selection:

- Den Hartog's condition is the classical first screen for vertical galloping.
  It is cheap to evaluate and directly uses the aerodynamic coefficient tables
  that drive the current damping update.
- The Week 7 lecture states that the motion-dependent aerodynamic force is
  equivalent to a damping term and that negative aerodynamic damping is the
  Den Hartog galloping criterion.
- Rossi et al. explicitly state the Den Hartog coefficient condition and also
  note that it identifies possible AoA ranges but is not sufficient by itself to
  prove occurrence.
- Chabart and Lilien use aerodynamic coefficient curves and Den-Hartog unstable
  regions in wind-tunnel validation, which supports retaining C1 as a separate
  susceptibility layer.

References:

- Week 7 lecture extraction, `output/reference_extraction/week7_galloping.txt`,
  pages 18-22.
- Den Hartog 1932 / 1956 as cited by Rossi et al. 2020.
- Rossi et al. 2020, especially extracted lines around the Den Hartog
  coefficient and its necessary-but-not-sufficient role.
- Chabart and Lilien 1998, extracted text
  `output/reference_extraction/1-s2.0-S0167610598000889-main.txt`.

Formula:

```text
delta_D(alpha) = dC_L/dalpha + C_D
```

where `alpha` is in radians. In the current coefficient file,
`dC_L/dalpha` is stored per degree and must be converted:

```text
dCL_rad = dCL_degree * 180 / pi
```

Time filter:

- Evaluate `delta_D(t, element)` at each damping update.
- Trigger `C1_seen` when any `delta_D < 0`.
- Trigger `C1_sustained` when negative fraction is at least `0.005` over the
  considered time window or persists for at least one first-mode period.

Outputs:

- `min_delta_D`
- `negative_delta_D_fraction`
- `negative_delta_D_duration_s`
- elements and time intervals with negative `delta_D`

Interpretation:

- Necessary screen for Den Hartog vertical galloping.
- Not sufficient by itself, because structural damping, mode shape, and
  nonlinear response may still prevent developed galloping.

### C2: Effective Negative Damping

Purpose: detect incipient dynamic instability in the actual model.

Reason for selection:

- C1 alone is aerodynamic. C2 adds structural damping, wind speed, element
  length, mass, diameter, and natural frequency, so it is closer to actual
  dynamic instability.
- The Week 7 lecture states that instability occurs when the total damping
  becomes negative, not merely when the aerodynamic term is negative.
- Rossi et al. note that actual occurrence requires total damping to vanish and
  a critical velocity to be reached.
- The current model already logs `xi_total`, making C2 immediately implementable
  and well matched to our corrected Tcl mechanism.

References:

- Week 7 lecture extraction, `output/reference_extraction/week7_galloping.txt`,
  pages 19-22.
- Rossi et al. 2020, extracted discussion of total damping and critical
  galloping velocity.
- ICWE14 aerodynamic damping paper,
  `output/reference_extraction/ICWE14_ID02306.txt`, for the importance of
  aerodynamic damping implementation.

Formula:

```text
xi_total(t, element) = xi_structural + xi_aero(t, element)
incipient when xi_total < 0
```

Current Tcl implementation:

```text
xi_aero = rho_air * U_rel * B * L_e / (4 * M_e * omega_n) * delta_D
```

Time filter:

- Trigger `C2_seen` when any `xi_total < 0`.
- Trigger `C2_sustained` when:

```text
negative_fraction >= 0.005 and min_xi < -1e-4
```

- Also record period-based persistence, e.g. negative damping persists for
  at least one first-mode period.

Outputs:

- `min_xi`
- `mean_xi`
- `negative_xi_fraction`
- `negative_xi_duration_s`
- affected elements

Interpretation:

- Primary label for `incipient_galloping`.
- More model-aware than C1 because it includes wind speed, mass, diameter,
  element length, modal frequency, and structural damping.

### C3: Aerodynamic Work / Energy Injection

Purpose: distinguish negative damping that actually injects energy into the
moving conductor from coefficient-only susceptibility.

Reason for selection:

- Galloping is an energy-instability problem: the aerodynamic force must do net
  positive work on the motion over time.
- Negative damping is a linearized description; an energy/work criterion checks
  whether the simulated force and velocity histories actually transfer energy
  into the conductor.
- This criterion is useful for cases where C2 is intermittently negative but the
  response does not grow, and for separating turbulent forcing from
  self-excited motion.

References:

- Week 7 lecture extraction, pages 19-22, where motion-dependent aerodynamic
  force acts in the same direction as body motion.
- Hagedorn 1982 overhead-line vibration paper,
  `output/reference_extraction/1-s2.0-S0022460X82800904-main.txt`, for
  energy-balance style thinking in wind-excited overhead lines.
- Chabart and Lilien 1998, for limit-cycle validation and the role of damping in
  galloping amplitudes.

Preferred metric:

```text
P_aero(t) = F_aero(t) dot v(t)
```

or, if force decomposition is hard to reconstruct:

```text
energy_proxy(t) = response_velocity(t)^2
```

Time filter:

- Trigger `C3_positive_work_seen` when aerodynamic work is positive over a
  moving window.
- Trigger `C3_sustained_energy_injection` when positive-work fraction exceeds
  `0.55` over at least one first-mode period, or when the late/early energy
  proxy ratio exceeds `1.5`.

Outputs:

- positive-work fraction
- cumulative aerodynamic work
- late/early kinetic-energy proxy ratio

Interpretation:

- Important bridge between damping theory and actual time-history growth.
- Should be implemented after force/velocity histories can be aligned cleanly.

### C4: Dynamic Response Growth

Purpose: detect whether the time-history response grows in a galloping-like way.

Reason for selection:

- The final observable phenomenon is not only negative damping but growth of
  conductor motion. Week 7 describes exponentially increasing amplitude in the
  unstable linear stage.
- Rossi et al. compute vertical oscillation amplitude and additional horizontal
  tension as galloping consequences, supporting response growth as a separate
  time-history criterion.
- Our recent corrected runs showed that a strict final-window growth rule can be
  too conservative when the response grows early and then reaches a large
  nonlinear plateau or fails numerically. Therefore C4 keeps separate labels for
  early growth, sustained growth, and growth-then-plateau.

References:

- Week 7 lecture extraction, pages 18-22.
- Rossi et al. 2020, dynamic-analysis sections and tables of galloping
  displacement/tension increments.
- Timur baseline extracted text,
  `output/reference_extraction/timur_paper_docx_extracted.txt`, for time-history
  demand metrics and structural response outputs.

Metrics:

- global resultant displacement envelope
- midspan resultant displacement envelope
- selected modal/node envelope
- peak-to-peak amplitude over moving windows

Time filter:

- Use windows of at least one first-mode period where possible.
- Trigger `C4_early_growth` when:

```text
late_over_early >= 1.50
```

- Trigger `C4_sustained_growth` when:

```text
late_over_mid >= 1.20 and late_over_early >= 1.50
```

- Record plateau cases separately:

```text
large_growth_then_plateau
```

when late/early is large but late/mid is near 1.0.

Outputs:

- envelope ratios
- growth slope by window
- first time a growth threshold is exceeded

Interpretation:

- Good for developed response.
- Conservative if the response grows early and then reaches a large limit-cycle
  or numerical nonlinearity before the final window.

### C5: Low-Frequency Large-Amplitude Galloping Signature

Purpose: separate galloping from ordinary gust buffeting or high-frequency
aeolian vibration.

Reason for selection:

- The Week 7 lecture defines galloping as low-frequency, large-amplitude
  vibration.
- Rossi et al. also describe galloping as low-frequency, high-amplitude motion
  and distinguish it from aeolian vibration/wake-induced oscillation.
- Chabart and Lilien report galloping frequencies and galloping ellipse behavior
  in wind-tunnel tests. This supports using frequency content and amplitude
  normalization as a separate signature check.

References:

- Week 7 lecture extraction, page 18.
- Rossi et al. 2020, extracted text around low-frequency/high-amplitude
  galloping and distinction from other conductor motions.
- Chabart and Lilien 1998, wind-tunnel galloping frequency and ellipse
  observations.
- Simpson 1983 overview,
  `output/reference_extraction/Simpson-Windinducedvibrationoverhead-1983.txt`,
  for wind-induced conductor-motion taxonomy.

Metrics:

- dominant response frequency
- first-mode frequency `f1`
- low-frequency power ratio
- amplitude normalized by diameter, sag, and span

Suggested filters:

```text
0.5*f1 <= f_dominant <= 2.0*f1
low_frequency_power_ratio >= 0.50
A/D >= 10
or A/Sag >= 0.10
```

Outputs:

- dominant frequency
- `f_dominant/f1`
- amplitude/diameter
- amplitude/sag

Interpretation:

- Anchored in the lecture definition of galloping as low-frequency,
  large-amplitude motion.
- Particularly useful to avoid confusing turbulent buffeting with galloping.

### C6: Developed Large Response / Nonlinear Instability

Purpose: identify when an incipient galloping case has moved into a severe
large-response regime.

Reason for selection:

- Some runs may leave the linear onset region quickly. A developed-response
  criterion captures the practical transition into severe nonlinear behavior,
  large displacement, large reaction/tension, or solver failure caused by
  amplified response.
- Chabart and Lilien report cases where amplitudes became too high to obtain a
  clean limit cycle; this supports classifying strong-amplitude cases even when
  the time history does not remain numerically well behaved.
- Our corrected 3072/4096-step runs show the same issue: sustained negative
  damping and response amplification were followed by convergence failure in
  the severe response range.

References:

- Chabart and Lilien 1998, wind-tunnel limit-cycle and high-amplitude
  observations.
- Rossi et al. 2020, response amplitude and added tension as dynamic galloping
  consequences.
- Project reports:
  `output/response_audit/timur_dynamic_2048_corrected_damping/dynamic_response_audit.md`
  and
  `output/response_audit/timur_dynamic_3072_corrected_damping/dynamic_response_audit.md`.

Triggers:

- max displacement exceeds a selected amplitude threshold;
- reaction/tension grows sharply;
- clearance/clashing metric becomes severe;
- solver convergence fails after response amplification and sustained negative
  damping.

Suggested initial filters:

```text
max_displacement >= 0.10*Sag
or max_displacement >= 10*D
or global late/early envelope ratio >= 3.0
or nonlinear convergence failure after C2_sustained
```

Outputs:

- max displacement
- max reaction/tension
- min clearance
- convergence status and failure time

Interpretation:

- This is not the earliest onset condition.
- It is a practical marker for developed galloping or severe nonlinear response.

### C7: Engineering Limit-State Exceedance

Purpose: keep Eurocode/National Grid/utility consequences separate from
physical galloping onset.

Reason for selection:

- Engineering consequence is not the same as physical onset. A conductor can be
  aerodynamically unstable before any clearance/tension threshold is exceeded,
  or can exceed a demand threshold due to large response.
- Timur's work uses tension, displacement/clashing, and clearance style limit
  states, which are directly useful for comparing physical onset with
  operational risk.
- EN 50341/RICA support clearance and phase-spacing context, EN 50182 supports
  conductor mechanical properties, and IEC 60826 provides overhead-line loading
  and reliability context.

References:

- Timur paper extraction,
  `output/reference_extraction/timur_paper_docx_extracted.txt`.
- EN 50341-1 source recorded in `RESEARCH_PLAN.md`.
- EN 50182 source recorded in `RESEARCH_PLAN.md`.
- IEC 60826 source recorded in `RESEARCH_PLAN.md`.
- National Grid RICA Preliminary Design Considerations, recorded in
  `RESEARCH_PLAN.md`.
- Rossi et al. 2020, for the argument that dynamic galloping can exceed what is
  captured by static design alone.

Subcriteria:

- C7a tension/strength:

```text
tension_ratio = max_tension / rated_strength
```

- C7b phase clashing / conductor separation:

```text
dynamic_envelope >= available_phase_spacing_or_clashing_threshold
```

- C7c ground/object clearance:

```text
minimum_clearance <= required_clearance_margin
```

- C7d design wind context:

```text
wind case lies inside or outside chosen Eurocode/RICA design context
```

Current known baseline thresholds to track:

- Zebra RTS: `131.9 kN`.
- Timur previous tension limit: `131.9 kN`.
- Timur/RICA-related L3 clashing threshold: `6.09 m`.
- Timur previous clearance scenario threshold: `1.4 m`.

Interpretation:

- These are consequence and safety criteria.
- A run can exceed C7 without being the earliest physical onset, and can satisfy
  C1/C2 without yet exceeding C7.

### C8: Linearized Eigenvalue / Stability Boundary

Purpose: obtain the cleanest theoretical critical boundary after the time-history
workflow is mature.

Reason for selection:

- A time-history boundary can depend on record length, seed, and nonlinear
  response saturation. A linearized eigen/stability criterion offers a cleaner
  theoretical estimate of onset.
- Zulli/Piccardo/Luongo and Ferretti et al. treat shallow-cable galloping through
  stability and nonlinear-response frameworks, which are well aligned with the
  final goal of a smooth `u_star_crit(L)` surface.
- C8 is intentionally future-stage because the current OpenSees workflow does
  not yet expose a clean global linearized aeroelastic operator.

References:

- Zulli, Piccardo, and Luongo 2020,
  `output/reference_extraction/s11071-020-05886-y.txt`.
- Ferretti et al. 2019,
  `output/reference_extraction/Advances_in_Mathematical_Physics_-_2019_-_Ferretti_-_A_Continuum_Approach_to_the_Nonlinear.txt`.
- ICWE14 aerodynamic damping paper,
  `output/reference_extraction/ICWE14_ID02306.txt`.

Trigger:

```text
real(lambda_max) > 0
```

or equivalent sign change in modal/effective damping.

Outputs:

- critical wind speed from eigen/stability model
- unstable mode
- comparison against time-history C2/C4/C6

Interpretation:

- Future criterion, not required for the first time-history sweep.
- Useful for fitting smooth `u_star_crit(L)` surfaces.

## First Classification Labels

Every run should be able to receive multiple labels:

```text
aero_susceptible          = C1_sustained
incipient_galloping       = C2_sustained
energy_injection          = C3_sustained_energy_injection
response_growth           = C4_early_growth or C4_sustained_growth
galloping_signature       = C5 low-frequency large-amplitude
developed_large_response  = C6
engineering_exceedance    = any C7
eigen_unstable            = C8
```

Do not require all labels to be true. Store all of them and compare boundaries
after sweep data exists.

## Recommended First Implementation Order

1. Implement C1/C2/C4/C6/C7, because the existing outputs already support most
   of these.
2. Add C5 after response PSD or modal-frequency postprocessing is added.
3. Add C3 after aerodynamic work can be reconstructed from force and velocity
   histories.
4. Add C8 after the time-history criteria are stable and sweep data exists.

## Criteria Check

The selected criteria are consistent with the project purpose and the current
evidence base:

- C1/C2 represent the physical Den Hartog/effective-damping onset mechanism.
- C4/C5 represent the observable galloping response signature.
- C6 captures developed large-amplitude/nonlinear behavior that may not satisfy
  a strict final-window growth rule.
- C7 keeps engineering safety and utility consequences separate from physical
  onset.
- C0 prevents misuse of results outside the wind/span/conductor context.
- C3 and C8 are valuable but should be implemented after the first sweep logic
  is stable.

No criterion should be deleted at this stage. The first implementation should
avoid requiring simultaneous truth of all criteria.

## Workflow Validation Before Batch Runs

Before a production `u_star` sweep, validate the workflow in this order:

1. Static/modal baseline:
   - catenary sag matches `10.48 m`;
   - self-weight matches `15.90 N/m`;
   - modal frequencies remain stable against previous corrected runs.
2. Wind/force generation:
   - generated `u_star = 0.6` reproduces the original MATLAB `FORCE_3/SIM1`
     statistics within the existing comparison tolerances;
   - wind velocity directory, force directory, and time file are aligned.
3. Time-history replay:
   - 1024-step and 2048-step corrected baseline runs reproduce the known
     negative damping and response metrics.
4. Output integrity:
   - recorder files are written to isolated `paths.output_dir`;
   - damping log reaches the expected dynamic time;
   - incomplete final rows are handled if nonlinear convergence fails.
5. Criteria audit:
   - C1/C2/C4/C6/C7 produce a JSON/Markdown summary for a known case;
   - the known `u_star ~= 0.6` baseline is classified as at least
     `incipient_galloping` under C2.

## Initial u_star Sweep Recommendation

Use staged ranges rather than one coarse sweep:

1. Calibration sweep:

```text
u_star = 0.20, 0.30, 0.40, 0.50, 0.60
```

Purpose: find whether the corrected baseline has a lower incipient threshold
below the current `0.60` case.

2. Boundary refinement around first C2/C4/C6 trigger:

```text
step size = 0.025 to 0.05 in u_star
```

Purpose: this is now a second-stage task only after broad coverage trends have
been sampled.

3. Developed-response sweep:

```text
u_star = 0.70, 0.80, 1.00, 1.20
```

Purpose: examine C6/C7 severe-response and engineering-exceedance behavior.

4. High-load envelope, only after the lower range is understood:

```text
u_star = 1.50, 2.00
```

Purpose: stress-test developed response and compare with Timur's broader wind
intensity set. These cases may be numerically severe and should be treated as
engineering stress tests rather than first boundary points.

## Window-Occupancy Extension

Added on 2026-06-02:

Galloping should not be treated only as a whole-record binary state. For
stochastic turbulent inputs, near-boundary galloping can appear in specific
time windows and then decay or be interrupted by changing aerodynamic state.

For each selected criterion, store both:

```text
whole_record_result = true/false
window_fraction = windows satisfying criterion / total windows
```

Current windowed criteria:

- C2 window: sustained negative effective damping in the window.
- C4 window: local response-growth window.
- C6 window: large response in the window.
- C7 window: engineering/clearance limit in the window.
- C2&C4 window: negative effective damping and local response growth in the
  same window.

Current implementation:

```text
tools/window_criteria_audit.py
```

First key-case summary:

```text
output/window_criteria_audit/key_4096_window_summary.md
```

Use window fractions as coverage/probability-like metrics, not as final
statistical probabilities until enough independent seeds are available.

## Time-Step Coverage Limits

Added on 2026-06-02:

The primary workflow should now evaluate criteria in the time domain, because
OpenSees records displacement, acceleration, and damping at discrete time steps.
Window occupancy remains useful for interpretation, but time-step coverage is
the main limit form.

Definition:

```text
coverage_fraction = problem_time_steps / total_time_steps
problem_time_s = problem_time_steps * dt
```

Current implementation:

```text
tools/time_step_coverage_audit.py
```

First key-case summary:

```text
output/time_step_coverage_audit/key_4096_time_step_summary.md
```

Current time-domain limits:

- C2: enough elements have negative effective damping at the same time step.
- C4: rolling response-growth limit assigned to time steps.
- C6: displacement exceeds a sag-based response limit at a time step.
- C7: engineering clearance proxy exceeds its limit at a time step.
- C2&C4: simultaneous time-step occurrence.

Future function and boundary surfaces should include:

```text
coverage_Ci(u_star, L, H)
u_star_crit_coverage(L, H, p)
```

where `p` is a required coverage fraction such as `0.005`, `0.010`, or `0.020`.

The first broad sweep should prioritize trend estimation over dense local
critical-point search.

## Fixed-Record Time-Step Coverage Implementation Note

Updated on 2026-06-02 after the fixed `L = 322.8 m` broad `u_star` sweep.

The intended comparison window is:

```text
npt = 4096
dt = 0.05 s
target duration = 204.8 s
```

However, severe nonlinear cases can write more than `4096` rows to
`Dynamic.out`. These extra rows appear when the solver enters adaptive
subincrement behavior. They should not be allowed to inflate or dilute
coverage curves relative to ordinary cases.

Current rule for production comparisons:

```text
tools/time_step_coverage_audit.py --max-records 4096
```

This means:

- coverage is computed on the common target record window;
- raw `Dynamic.out` row count is still stored in each audit report;
- cases that return nonzero or fail to complete are stored in a separate failed
  case table, not averaged into coverage;
- if a case produces many extra rows but returns normally, it can enter the
  coverage curve after truncation, while the raw row count remains a numerical
  severity flag.

For the fixed-L broad sweep, final result files are:

```text
output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/ustar_coverage_summary.md
output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/coverage_curves_core.svg
output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/coverage_curves_all.svg
```

Criterion interpretation after this batch:

- C6 is the clearest developed-response indicator in the current data.
- C4 is physically useful but seed-sensitive; use mean and uncertainty bands.
- C2 is a mechanism indicator, not a monotonic severity curve by itself.
- C2&C4 is conservative and should be retained as a strict simultaneous marker.
- C7 remains uncalibrated and should be excluded from primary galloping claims.

## Uncertainty Bands And Non-Normal Runs

Updated on 2026-06-03 after adding five seeds at
`u_star = 0.50, 0.60, 0.80, 1.00`.

Coverage curves should now be reported as:

```text
mean_coverage_Ci(u_star)
95% CI for mean_coverage_Ci(u_star)
failed_or_non_normal_fraction(u_star)
```

The failed/non-normal fraction is not itself a galloping criterion, because it
can include numerical convergence limits. It is still physically important for
this project because severe galloping-like response, large displacement, and
strong negative damping can all make the nonlinear solver difficult to complete.

Current handling:

- completed runs enter C2/C4/C6/C2&C4 coverage averages;
- failed or non-normal runs are stored in `failed_cases.csv`;
- failed-case counts are reported next to each `u_star`;
- uncertainty bands use the standard error of completed-run coverage values
  with an approximate 95% interval;
- for small `n`, these bands are descriptive rather than final statistical
  confidence statements.

For current research claims:

- use C6 as the developed-response severity curve;
- use C4 as the response-growth mechanism curve;
- use C2&C4 as the strict simultaneous-mechanism curve;
- include failed/non-normal fraction as an auxiliary instability curve;
- do not use C7 in primary galloping conclusions until the clearance limit is
  physically recalibrated.
