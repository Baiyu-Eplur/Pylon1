# Research Plan: Galloping Critical Boundary

Last updated: 2026-06-02

## 1. Research Objective

Build a verified simulation and analysis workflow for the galloping onset of overhead transmission conductors. The target result is a critical boundary:

```text
V_crit = f(L, cable_structure)
or equivalently
L_crit = g(V, cable_structure)
```

where `V` is mean wind speed / wind load intensity, `L` is span length, and `cable_structure` includes conductor type, sag/tension state, bundle number, aerodynamic coefficients, damping model, and possible ice accretion state.

This project should use Timur Bolotin's dissertation as the baseline model, but extend it from fragility/risk mapping toward a direct galloping-onset boundary and a reusable parameter-sweep engine.

## 2. Baseline From Timur's Paper

Source:

- `reference/basement/Timur's Paper PDF.docx`
- Extracted text: `output/reference_extraction/timur_paper_docx_extracted.txt`

Key baseline values and methods extracted from the paper:

- Conductor: Zebra ACSR.
- Diameter: 28.62 mm.
- Area: 643.32 mm2 total, 484.5 mm2 nominal.
- Self-weight: 15.90 N/m in Timur's table.
- Rated tensile strength: 131.9 kN.
- Modulus of elasticity: 69,000 N/mm2.
- Representative National Grid span: 322.8 m.
- Representative support height: 49.4 m after tower/cross-arm correction.
- Maximum sag: 10.48 m from catenary formulation with pretension of 15% rated tensile strength.
- FE model: force-based OpenSees elements, corotational transformation, geometric nonlinearity.
- Wind field: Kaimal spectrum + Davenport coherence.
- Wind intensity measure: friction velocity `u*`, with cases 0.10 to 2.20 m/s, corresponding to mean speeds 1.74 to 38.33 m/s.
- Time-history reliability: three simulations per wind intensity.
- Baseline damping: 1% Rayleigh damping.
- Previous limit states:
  - tension: 131.9 kN;
  - displacement/conductor clashing: 6.09 m for L3 tower worst case;
  - clearance: 1.4 m for a specific falling-streetlight scenario.

Important limitation to fix:

- Timur's work mainly maps demand/capacity failure probabilities; our next step should directly identify galloping onset and critical boundaries, not only exceedance of response limits.

## 3. Current Code Audit

Audit script added:

- `tools/model_sanity_audit.py`

Latest audit output:

- `output/model_audit/model_sanity_audit.md`
- `output/model_audit/model_sanity_audit.json`
- `output/model_audit/smoke/model_sanity_audit.md`
- `output/model_audit/timur_baseline/model_sanity_audit.md`
- `output/wind_audit/timur_baseline/dynamic_wind_audit.md`
- `output/response_audit/timur_dynamic_short/dynamic_response_audit.md`

Current findings from `config/default_config.yaml`:

- The active config is still a small smoke-test model: `L = 2.0 m`, `Sag = 1.0 m`, `discretisation = 1.0 m`.
- `geometry.type = 3`, which means broken-line/V-shape in the code. With only 3 nodes, this is numerically identical to the parabolic profile at those nodes, so it can falsely appear parabolic in a coarse audit.
- This is not Timur's research-scale catenary model (`L = 322.8 m`, `Sag = 10.48 m`, about 101 elements).
- The generated force case `FORCE_3/Test1` matches the 3-node smoke-test model.
- Wind files exist for 101 nodes in `data/wind/SIM1`, which matches Timur-scale data better than the current 3-node config.
- Current section calculation uses `self_weight = Area * ro * g`, producing 21.95 N/m with `ro = 3480 kg/m3`; Timur's Zebra table uses 15.90 N/m. This mismatch must be resolved before production sweeps.
- `modal_simple.out` exists, and current first modal frequency used by the audit is about 2.29088 Hz, giving Rayleigh mass coefficient alpha about 0.28788 for xi = 0.01.
- The current workflow does not export full global stiffness matrix `K` or damping matrix `C`; only element definitions, modal outputs, and Rayleigh/modal damping commands are available.

Implemented after the first audit:

- `config/smoke_config.yaml` preserves the original small 2 m runnable smoke case in clean UTF-8 YAML.
- `config/timur_baseline.yaml` defines the research baseline from Timur's paper:
  - `geometry.type = 2` catenary;
  - `L = 322.8 m`;
  - `Sag = 10.48 m`;
  - `discretisation = 3.228 m`, giving 101 nodes and 100 elements;
  - Zebra table self-weight override `self_weight_N_per_m = 15.90`;
  - pretension `19785 N`, 15% of 131.9 kN.
- `CableGeometry` now accepts optional `material.self_weight_N_per_m`, while retaining density-derived self-weight when no override is supplied.
- The catenary generator now solves the exact catenary parameter so the configured sag is reproduced at midspan. The earlier closed-form approximation produced about `-10.539 m` for a requested `10.48 m` Timur sag.
- Latest Timur baseline audit confirms:
  - best shape match: catenary;
  - nodes/elements: 101/100;
  - midpoint/minimum z: `-10.48 m`;
  - self-weight: `15.9 N/m`;
  - force files for `FORCE_3/SIM1`: 101 per component;
  - wind H/V files: 101/101.
- Caveat: `modal_simple.out` found during audit is an existing file in `output/`; it is not proof that Timur baseline modal analysis has been freshly run.

Dynamic wind-response calibration audit:

- `tools/dynamic_wind_audit.py` was added to check time-base consistency, wind-profile consistency, Kaimal PSD spot checks, Davenport-like coherence spot checks, and force/wind consistency.
- `config/timur_baseline.yaml` now uses `npt = 65536` so the transient analysis length matches the available `time.txt`, wind files, and force files. The earlier `70536` value would run beyond the available wind/force histories; this is only valid if a deliberate ring-down tail is implemented consistently.
- Latest wind audit confirms:
  - config dt and file dt both `0.05 s`;
  - config npt and file rows both `65536`;
  - duration `3276.8 s`;
  - inferred friction velocity across all nodes is essentially constant at `u* = 0.6000 m/s`;
  - horizontal wind mean is about `10.45 m/s`;
  - vertical wind mean is essentially zero;
  - Kaimal PSD log10 RMSE at sampled nodes is about `0.01-0.11`;
  - H-drag force files are strongly correlated with `wind_H^2`, with sampled correlations about `0.989-0.992`.

Interpretation:

- The available `FORCE_3/SIM1` dynamic wind input is internally coherent and appears to represent the `u* = 0.60 m/s` case from Timur's friction-velocity set.
- The next dynamic-response calibration should run this single case through OpenSees and compare response metrics against Timur's Table 4 for the matching `u* = 0.60/0.70-ish` case, after confirming the exact force-case mapping.

Dynamic response calibration status:

- A full `config/timur_baseline.yaml` TH run starts correctly but is currently too slow for routine iteration: a 900 s wall-time attempt reached only about 160 s simulated time, or about 4.9% of the full 3276.8 s case.
- User preference is accuracy over runtime. Long engineering analysis time is acceptable if it preserves model fidelity.
- `config/timur_dynamic_short.yaml` was added as a 51.2 s calibration case (`npt = 1024`) using the same Timur-scale geometry and `FORCE_3/SIM1` wind/force inputs.
- The short TH run completed successfully and wrote complete displacement, velocity, acceleration, reaction, damping-log, and summary CSV outputs. It has now been rerun after correcting the Den Hartog derivative units in `Damping_shifter.tcl`.
- Modal check from the short run:
  - mode 1 frequency `0.171003521 Hz`, period `5.84783 s`, dominant MY participation about `80.995%`;
  - modes 2 and 3 frequencies `0.340307129 Hz` and `0.341752038 Hz`.
- Response audit:
  - max displacement `1.85014 m` at node 42 (`x = 132.348 m`);
  - max reaction `24.2736 kN`;
  - max/min clearance metric `0.215955 m` / `-0.307773 m`;
  - response p95 grows from early to later windows by about `2.83x`, but late/mid ratio is about `0.959`, so there is no sustained final-window growth in this short run;
  - corrected aerodynamic damping samples have `xi_total` from about `-0.25519` to `0.04738`, with negative fraction about `0.23989`.

Interpretation for galloping:

- The corrected short `u* ~= 0.60 m/s` run validates that the dynamic chain now activates the Den Hartog negative-effective-damping mechanism.
- The run is flagged as `galloping_candidate = True` because sustained negative effective damping is present.
- The run is not yet `confirmed_galloping` because sustained response-envelope growth is not present within the 51.2 s window.
- This short run is a mechanism-validation test, not a final boundary point. It should be followed by longer corrected-damping runs before production wind-speed/span sweeps.
- If the calibrated baseline does not reach a galloping boundary, the next physical levers are increasing span length / reducing stiffness and increasing wind loading.

Original wind-force generation source:

- `D:\Uob\Tower Pylon\TIMUR2\WIND_SIMULATION.mlx` is the source for the current dynamic wind and force files.
- It generates the reviewed `FORCE_3/SIM1` case in friction-based mode with `u_star = 0.6 m/s`, `kappa = 0.387`, `z0 = 0.05 m`, and `U(z) = u_star/kappa * log(z/z0)`.
- It uses Kaimal spectra from `KaimalModel.m` and Davenport coherence from `cohDavenport.m`, with longitudinal `u` and vertical `w` wind components.
- Aerodynamic angle is `alpha = atan2(w, u)`.
- Drag and lift coefficients are interpolated from `C_D_data.txt` and `C_L_data2.txt`.
- Updating-coefficient force generation uses:

```text
u_T = sqrt(u^2 + w^2)
A_i = discretisation * pi * DIAMETER / 2, half at end nodes
F_D = 0.5 * C_D * ro_air * u_T^2 * A_i
F_L = 0.5 * C_L * ro_air * u_T^2 * A_i
F_D_X = F_D * cos(alpha)
F_D_Y = F_D * sin(alpha)
F_L_X = F_L * cos(alpha + pi/2)
F_L_Y = F_L * sin(alpha + pi/2)
```

- MATLAB uses `DIAMETER = 0.02862 m` and `ro_air = 1.293/1000 tons/m3` for force generation. Current OpenSees load patterns multiply force-file values by `1000`, matching the original generated `Input.tcl`.
- Important: simple force-file multiplication can bracket higher/lower loading, but the more accurate research path is to regenerate wind and force histories for each `u_star`, span, sag, and seed so angle of attack, aerodynamic coefficients, coherence, and damping wind histories remain consistent.

In-project implementation:

- `src/cable_analyser/wind_forces.py` now implements the friction-based wind and force generation logic.
- `tools/generate_wind_forces.py` generates new force/wind cases from command-line `--u-star`.
- `config/timur_generated_ustar.yaml` is the first config template where `u_star` is the wind-load independent variable.
- `wind_generation.enabled: true` triggers generation before a TH analysis; `enabled: false` preserves replay of existing force files.
- `reuse_existing: true` reuses a previously generated case with matching folder names; `overwrite: true` deliberately regenerates it.
- `TclWriter` and `Wind_velocity_reader.tcl` now pass/read configured wind velocity directory and time file, so aerodynamic damping uses the same generated wind case as the OpenSees force time histories.

Generation smoke test:

- `u_star = 0.8 m/s`, `npt = 64`, seed `123` generated successfully under `data/forces/FORCE_TEST_USTAR_0P80/SIM_TEST` and `data/wind/SIM_TEST_USTAR_0P80`.
- Generated mean horizontal wind was about `13.94 m/s`, consistent with scaling from the existing `u_star ~= 0.6 m/s` case.
- This is a software validation run only, not a physics result.

Full `u_star = 0.6` validation:

- Python-generated cases were produced for `npt = 4096`, `16384`, and full `65536`.
- Full generated case:
  - force folder: `data/forces/FORCE_PY_USTAR_0P60_N65536/SIM1`;
  - wind folder: `data/wind/SIM_PY_USTAR_0P60_N65536`;
  - duration: `3276.8 s`;
  - seed: `20260529`;
  - generated global mean horizontal wind: `10.452801821 m/s`.
- Full comparison report:
  - `output/wind_generation_compare/ustar_0p60_n65536/wind_force_case_comparison.md`.
- Main comparison findings against original `FORCE_3/SIM1`:
  - inferred `u_star`: original `0.60000236 m/s`, Python `0.60000000 m/s`;
  - sampled horizontal wind means agree to about `0.001%` or better;
  - sampled horizontal wind standard deviations differ by about `0-12%`, consistent with independent random-phase realizations;
  - coherence means over sampled node pairs are same order and close;
  - `H_drag` means differ by about `0.15%` on average;
  - dominant `V_lift` means and standard deviations differ by about `2.6%` on average;
  - large relative differences in `H_lift` and `V_drag` means are caused by near-zero means; their standard deviations and absolute magnitudes are comparable.

Conclusion:

- The Python generator is validated as statistically consistent with the original MATLAB `u_star = 0.6` workflow and is suitable for future `u_star` sweeps.

Sweep infrastructure:

- `tools/run_ustar_sweep.py` now prepares/generates/optionally executes `u_star` scan cases.
- Prepared production manifest:
  - `output/sweeps/ustar_baseline_scan/manifest.md`;
  - values: `u_star = 0.60, 0.80, 1.00, 1.20, 1.50, 2.00`;
  - duration: `npt = 65536`, `dt = 0.05 s`.
- Verified smoke sweep:
  - `output/sweeps/ustar_smoke/manifest.md`;
  - generated `u_star = 0.6` and `0.8`, `npt = 256`.

Galloping assessment:

- `tools/dynamic_response_audit.py` now emits a `galloping_assessment` block.
- Current working triggers:
  - negative effective damping if any logged `xi_total < 0`;
  - sustained response growth if the global response envelope has `late_over_mid >= 1.20` and `late_over_early >= 1.50`.
- Existing short Timur run remains `galloping_candidate = False`.

Week 7 lecture mechanism check:

- Source: `C:\Users\haoya\Downloads\Week7.pdf`.
- Extracted text: `output/reference_extraction/week7_galloping.txt`.
- Lecture confirms:
  - galloping is low-frequency, large-amplitude aeroelastic instability;
  - classically overhead conductors with accreted ice/snow;
  - it occurs through motion-dependent aerodynamic forces in smooth wind, not as ordinary gust buffeting;
  - Den Hartog's quasi-steady criterion is based on aerodynamic damping becoming negative;
  - if structural plus aerodynamic damping is negative, the linear response grows exponentially.
- Mechanism correction found:
  - `dC_L.txt` stores derivative per degree;
  - Den Hartog requires derivative per radian;
  - `Damping_shifter.tcl` has been corrected with `dCL_rad = dCL_degree * 180/pi`;
  - `xi_structural` is now written from `damping.xi` instead of being hard-coded.

Revised critical-condition definition:

1. Aerodynamic susceptibility:

```text
delta_D(alpha) = dC_L/dalpha + C_D < 0, alpha in radians
```

2. Incipient dynamic instability:

```text
xi_total = xi_structural + xi_aero < 0
```

where the current Tcl implementation uses:

```text
xi_aero = rho_air * U_rel * B * L_e / (4 * M_e * omega_n) * delta_D
```

3. Confirmed time-history galloping:

```text
sustained_negative_damping AND sustained_response_growth
```

4. Engineering failure/exceedance:

```text
tension, clearance, or conductor-clashing thresholds exceeded
```

This is a consequence/limit-state classification and should be reported separately from physical galloping onset.

New audit:

- `tools/galloping_criterion_audit.py`;
- report: `output/galloping_criterion/timur_dynamic_short/galloping_criterion_audit.md`.
- Result: stored per-degree derivative falsely gives no Den Hartog-negative regions; corrected per-radian derivative gives substantial negative `delta_D` regions. The previous short TH result should therefore be treated only as workflow validation until rerun with corrected damping.

Corrected-damping TH test:

- Reran `config/timur_dynamic_short.yaml` after the `dC_L/dalpha` unit correction.
- Report:
  - `output/response_audit/timur_dynamic_short_corrected_damping/dynamic_response_audit.md`;
  - `output/response_audit/timur_dynamic_short_corrected_damping/dynamic_response_audit.json`.
- Result:
  - `min_xi = -0.25519`;
  - `mean_xi = -0.01747`;
  - `negative_fraction = 0.23989`;
  - `galloping_candidate = True`;
  - `confirmed_galloping = False`.
- Interpretation: the baseline `u* ~= 0.60 m/s` case already contains sustained negative effective damping after the correction, but the 51.2 s window is too short to prove a self-sustained galloping response by envelope growth.

Longer mechanism-verification tests:

- Added output-isolated configs:
  - `config/timur_dynamic_2048.yaml`, 102.4 s;
  - `config/timur_dynamic_3072.yaml`, target 153.6 s;
  - `config/timur_dynamic_4096.yaml`, target 204.8 s.
- Complete 2048-step run:
  - report: `output/response_audit/timur_dynamic_2048_corrected_damping/dynamic_response_audit.md`;
  - max displacement `2.20825 m`;
  - max reaction `26.6719 kN`;
  - `min_xi = -0.28129`;
  - `mean_xi = -0.02586`;
  - negative damping fraction `0.27382`;
  - global late/early envelope ratio `1.58333`;
  - `galloping_candidate = True`.
- 3072-step run:
  - report: `output/response_audit/timur_dynamic_3072_corrected_damping/dynamic_response_audit.md`;
  - reached damping-log time `150.53119 s` before convergence failure near 98% progress;
  - max displacement before failure `6.92909 m`;
  - max reaction before failure `212.672 kN`;
  - `min_xi = -0.56847`;
  - `mean_xi = -0.04411`;
  - negative damping fraction `0.35034`;
  - global late/early envelope ratio `3.25447`.
- 4096-step exploratory run:
  - reached about `160.135 s` before convergence failure;
  - max displacement `8.88208 m`;
  - max reaction `271.969 kN`;
  - its damping log is missing because it was run before the output-directory log fix.
- Interpretation:
  - the corrected Den Hartog/effective damping mechanism is now verified by coefficient audit, complete 2048-step time history, and longer near-instability runs;
  - strict `confirmed_galloping` remains conservative because it requires continued late-window growth, while the longer runs show strong growth into a large nonlinear response and then convergence failure;
  - for production boundary work, classify results with at least two stages: `incipient_galloping` from sustained negative damping and `developed_large_response` from strong response growth, large displacement/reaction, or convergence failure after amplification.

Immediate model-verification tasks:

1. Replace the smoke-test geometry with a research config matching Timur: `L = 322.8 m`, catenary or high-resolution parabolic approximation, sag around 10.48 m, 101 elements or a mesh that is justified by convergence.
2. Decide whether self-weight should follow physical density from `Area * ro * g` or tabulated conductor self-weight. For Zebra, Timur's 15.90 N/m should be reproduced in the baseline case.
3. Add a diagnostic mode to export/check assembled mass and damping surrogates. If full OpenSees global `K`/`C` export is not practical, validate through modal frequencies, mode shapes, static sag/tension, and Rayleigh/modal damping coefficients.
4. Validate wind simulation by comparing simulated mean profile and PSD against log-law and Kaimal targets, as Timur did.

## 4. Standards And Verifiable Sources

These are the initial standards/sources to anchor the design ranges and limit states. Full standard texts are not all freely accessible, so this section records official catalog pages and publicly accessible National Grid deliverables.

### EN 50341-1: Overhead electrical lines

Use for overhead-line design context, actions on lines, electrical clearances, conductor/conductor spacing, and national normative aspects.

Verified source:

- AFNOR page for NF EN 50341-1, European kinship EN 50341-1:2012. It states the standard applies to new overhead electrical lines above AC 1 kV and lists table-of-contents topics including actions on lines, electrical requirements, conductors, clearances, and annexes.
- URL: https://www.boutique.afnor.org/en-gb/standard/nf-en-503411/overhead-electrical-lines-exceeding-ac-1-kv-part-1-general-requirements-com/fa175101/46100

Research use:

- Use EN 50341-1 and the relevant UK National Normative Aspects / National Grid documents to define phase-to-phase and phase-to-earth clearance calculations.
- RICA Preliminary Design gives a mid-span spacing form based on BS EN 50341-1:

```text
c = k * sqrt(f) + lk + k1 * Dpp
```

where `c` is required mid-span clearance, `f` is sag, `lk` is insulator/fitting swing length, `Dpp` is phase-to-phase clearance, and `k`, `k1` are code/project factors.

### EN 1991-1-4: Eurocode wind actions

Use for wind-speed definitions, terrain categories, roughness, and consistency checks against log-law wind assumptions.

Verified source:

- EN 1991-1-4 catalog/extract page records fundamental basic wind velocity as a characteristic 10-minute mean wind velocity with annual exceedance probability 0.02, at 10 m above ground in flat open country terrain. It also states that this corresponds to terrain category II.
- URL: https://standards.iteh.ai/catalog/standards/cen/2a6d2a81-04ae-4fd9-94ef-1df52bf042bd/en-1991-1-4-2005

Research use:

- Keep wind-speed definitions explicit: 10-minute mean at 10 m open terrain vs simulated time-history mean speeds vs friction velocity `u*`.
- Retain Timur's roughness length `z0 = 0.05 m` for open country only if it matches the selected terrain category/national annex.

### EN 50182: Conductors for overhead lines

Use for conductor-type definitions and mechanical/electrical characteristics of stranded overhead conductors.

Verified source:

- EVS page for EVS-EN 50182:2002, based on EN 50182:2001, describes the standard as specifying electrical and mechanical characteristics of round-wire concentric-lay bare overhead conductors.
- URL: https://www.evs.ee/en/evs-en-50182-2002

Research use:

- Build conductor database entries from standard/utility data: diameter, area, rated strength, mass/self-weight, E, G, thermal expansion.

### IEC 60826: Design criteria for overhead transmission lines

Use as an international reliability/design framework for overhead transmission-line loading/strength, especially wind/ice climate data and semi-probabilistic design.

Verified source:

- IEC 60826:2017 official IEC page states that it specifies loading and strength requirements for overhead lines using reliability-based design principles, applies to 45 kV and above, and provides a framework for national standards using local climatic data.
- URL: https://webstore.iec.ch/en/publication/33148

Research use:

- Use as a reliability framework, but note from the Rossi et al. paper that static combined wind/ice design alone may not capture dynamic galloping response.

### National Grid RICA deliverables

Use for UK-specific phase spacing, galloping context, and design recommendations.

Verified sources:

- RICA project page: https://www.nationalgrid.com/electricity-transmission/innovation/rica
- RICA Preliminary Design Considerations PDF: https://www.nationalgrid.com/electricity-transmission/document/137841/download

Relevant extracted values:

- RICA notes that vertical and horizontal offsets help maintain mid-span clearances and reduce conductor clashing during galloping.
- RICA states galloping commonly involves ice accretion, moderate/high wind speeds of 5-15 m/s, steady low-turbulence transverse winds over open terrain, lakes, or crossings.
- RICA recommends galloping studies over span ranges from shortest to maximum for each tower type.
- RICA table gives example vertical phase separations and maximum single span lengths:
  - L3 275 kV: 6.10 m vertical phase separation, 537 m max single span.
  - L66 275 kV: 7.16 m vertical phase separation, 457 m max single span.
  - L2 400 kV: 7.85 m vertical phase separation, max single span not given in the extracted text.

## 5. Literature Review Matrix

Local literature folder:

- `reference/literature papers`
- Extracted text: `output/reference_extraction/`

Initial paper map:

| File | Main contribution | How we use it |
|---|---|---|
| `1-s2.0-S0167610598000889-main.pdf` | Chabart & Lilien wind-tunnel galloping of electrical lines; distinguishes Den Hartog and flutter galloping; emphasizes ice shape, wind speed, detuning, damping, and bundle effects. | Use for experimental validation logic, reduced wind speed, galloping ellipse, bundle motivation. |
| `1-s2.0-S0167610520301811-main.pdf` | Combined wind and atmospheric icing on overhead lines; uses Den Hartog/Nigol criteria; notes IEC 60826 static design may miss dynamic galloping. | Use for onset criteria, ice/wind parameter space, and comparison against code-based static load design. |
| `s11071-020-05886-y.pdf` | Zulli/Piccardo/Luongo: nonlinear effects of mean wind force on galloping onset in shallow cables; computes critical wind velocity and modes including equilibrium swing and aerodynamic damping. | Use as theoretical foundation for `V_crit(L, sag)` and stability/eigenvalue-based onset. |
| `Advances in Mathematical Physics - 2019 - Ferretti...pdf` | Continuum approach to nonlinear in-plane galloping of shallow flexible cables. | Use for reduced/analytical model checks and post-critical behavior. |
| `ICWE14_ID02306.pdf` | Aerodynamic damping of conductor cables; compares damping implementations; argues modal damping can represent aerodynamic damping better than Rayleigh damping. | Use to audit current Rayleigh approach and design modal/aero damping alternatives. |
| `1-s2.0-S016761052030221X-mainext.pdf` | Identification of nonlinear aerodynamic damping from non-Gaussian response PDFs for wind-excited flexible structures. | Use as an advanced data-driven damping-identification option after simulations exist. |
| `1-s2.0-S0022460X82800904-main.pdf` and duplicate `(1)` | Hagedorn: damped wind-excited vibrations of overhead lines with Stockbridge dampers, impedance matrix and energy balance. | Use for damping-device modeling and energy-balance validation, not primary galloping onset. |
| `Simpson-Windinducedvibrationoverhead-1983.pdf` | Overview of wind-induced vibration of overhead power transmission lines. | Use for taxonomy and physical background. |

## 6. Proposed Galloping Onset Criteria

Detailed criteria specification:

- `GALLOPING_CRITERIA.md`

Use multiple criteria rather than one fragile threshold. At this research stage,
the criteria should be evaluated independently over time, not combined by a
single intersection rule:

The criteria file now includes the selection reason and supporting references
for each criterion. The reference base includes Week 7 lecture notes, Timur's
paper, Rossi et al. 2020, Chabart and Lilien 1998, ICWE14 aerodynamic damping,
Hagedorn energy-balance-style overhead-line vibration work,
Zulli/Piccardo/Luongo, Ferretti et al., EN 1991-1-4, EN 50341, EN 50182,
IEC 60826, and National Grid RICA.

1. Aerodynamic/Den Hartog screening:

```text
delta_D = C_D + dC_L/dalpha
Potential vertical galloping when delta_D < 0
```

This is necessary but not always sufficient because structural damping and multi-DOF coupling matter.

2. Effective damping criterion:

```text
xi_total(t, element) = xi_structural + xi_aero(t, element)
Galloping candidate when min(xi_total) < 0
```

The current Tcl formula already computes an element-wise `xi_total`; this should be logged robustly and post-processed as an onset metric.

3. Dynamic growth criterion:

```text
response envelope grows over a sustained time window
and does not settle to bounded forced vibration
```

This guards against transient spikes being mistaken for galloping.

4. Eigen/stability criterion:

```text
critical condition when a linearized eigenvalue crosses into positive real part
```

This is the cleanest theoretical route for the final `V_crit(L)` surface, following the shallow-cable literature.

5. Engineering limit-state exceedance:

```text
tension > capacity
or conductor-clashing envelope overlaps
or clearance demand exceeds allowed clearance
```

This remains important for risk/utility relevance but is not the same as galloping onset.

Parallel criterion set now adopted:

| ID | Criterion | Main output label | Current implementation priority |
|---|---|---|---|
| C0 | Input and standard-range context | `within_reference_context` | High |
| C1 | Den Hartog aerodynamic susceptibility | `aero_susceptible` | High |
| C2 | Effective negative damping | `incipient_galloping` | High |
| C3 | Aerodynamic work / energy injection | `energy_injection` | Medium |
| C4 | Dynamic response growth | `response_growth` | High |
| C5 | Low-frequency large-amplitude signature | `galloping_signature` | Medium |
| C6 | Developed large response / nonlinear instability | `developed_large_response` | High |
| C7 | Engineering limit-state exceedance | `engineering_exceedance` | High |
| C8 | Linearized eigenvalue / stability boundary | `eigen_unstable` | Future |
 
Each criterion should report:

```text
triggered
first_trigger_time_s
last_trigger_time_s
duration_s or fraction
severity
affected nodes/elements
notes
```

For the first boundary study, extract separate boundaries for each criterion,
for example:

```text
u_star_crit_by_C2(L)
u_star_crit_by_C4(L)
u_star_crit_by_C7(L)
```

This lets us study which criterion is more conservative, which captures the
earliest onset, and which better predicts engineering consequence.

Criteria check conclusion:

- No criterion should be removed at this stage.
- C1/C2/C4/C6/C7 should be implemented first because existing outputs already
  support them.
- C3/C5/C8 should be added after force/velocity work reconstruction, response
  PSD/frequency analysis, and stability extraction are mature.

## 7. Experimental Design

Geometry baseline:

- Detailed source-backed geometry decision file: `GEOMETRY_BASELINE.md`.
- UK-informed wind-intensity range file: `USTAR_RANGE_UK.md`.
- European standards/design guidance do not give one universal `H = f(L)` relation. Sag is a sag-tension result that must be checked against clearance, tension, wind/ice, and tower/route constraints.
- Before the first `u_star` search, use the calibrated typical case:

```text
L = 322.8 m
H/Sag = 10.48 m
H/L = 0.0325
conductor = Zebra ACSR
self-weight = 15.90 N/m
pretension = 19.785 kN = 15% RTS
```

- This pair is mechanically consistent with:

```text
H(L) ~= w * L^2 / (8 * T0)
H(322.8) ~= 10.47 m ~= 10.48 m
```

- Public design context:
  - National Grid RICA example sag/span pairs: `300 m -> 7.2 m` and `500 m -> 18.0 m`;
  - RICA example max single span lengths: L3 `537 m`, L66 `457 m`;
  - public European case: nominal/rated spans about `450 m` for 400/220 kV and `300 m` for 110 kV.

Phase A: Baseline reproduction

- Reproduce Timur's Zebra, 322.8 m, 10.48 m sag, 101-element model.
- Reproduce modal frequencies/mode shapes against Timur outputs if available.
- Reproduce selected time-history metrics from Timur Table 4.
- Resolve self-weight discrepancy before any new sweeps.
- Make full-length TH execution practical by reducing console/log overhead and by defining whether calibration uses full 3276.8 s records or shorter statistically representative windows.

Phase B: Model verification

- Geometry: catenary vs parabolic approximation error over span/sag ranges.
- Mesh: convergence with 51, 101, 201 elements.
- Damping: compare Rayleigh, modal, and current element-updated Rayleigh aerodynamic damping.
- Wind: verify mean profile, PSD, and coherence.
- Data completeness: force and wind files must match node count for each configuration.

Phase C: Critical-boundary sweep

- Span length range: first use `L = 250, 300, 322.8, 350, 400, 450, 500 m`; this covers the calibrated baseline, RICA/UK-relevant span context, and public European nominal-span examples. Later extend toward RICA maximum single spans such as `537 m` if the solver and geometry remain robust.
- Sag range: define by sag-tension calculation; start with sag/span ratios anchored by Timur (10.48/322.8 = 0.0325) and RICA examples (7.2/300 = 0.024, 18.0/500 = 0.036).
- Primary sag rule for the first L sweep:

```text
H_primary(L) = 15.90 * L^2 / (8 * 19785)
```

- Secondary sag sensitivity bands:

```text
H/L = 0.024, 0.0325, 0.036
```

- Wind speed range: include RICA galloping range 5-15 m/s, extend below/above for boundary bracketing and Timur cases. In the current `u_star` workflow, use staged ranges:
  - calibration: `u_star = 0.20, 0.30, 0.40, 0.50, 0.60`;
  - local refinement: `0.025` to `0.05` increments around first criterion trigger;
  - central galloping band: `0.70, 0.80, 0.90`;
  - developed response: `1.00, 1.20`;
  - high-load Eurocode envelope: `1.50, 2.00, 2.35` only after lower-range behavior is understood.
- `u_star` mapping used for interpretation:

```text
U10 = 13.691 * u_star
mean conductor wind ~= 17.42 * u_star
```

- UK-informed interpretation:
  - ordinary UK 10 m climatic wind: roughly `u_star ~= 0.22-0.58`;
  - RICA galloping wind context `5-15 m/s` at conductor height: roughly `u_star ~= 0.29-0.86`;
  - UK Eurocode/NA basic wind context `22-32 m/s` at 10 m: roughly `u_star ~= 1.61-2.34`.
- Ice states: no ice, representative eccentric ice, and mass-only ice as a lower-fidelity baseline.
- Structure: single conductor first, then 2-bundle and 4-bundle with torsion/bundle wake effects.
- Wind/force generation: port or call `WIND_SIMULATION.mlx` logic so each sweep point can regenerate consistent wind velocities and aerodynamic forces. Use force scaling only as a labeled preliminary bracketing approximation.

Phase D: Boundary extraction

- For each `(L, sag, structure)` run wind speeds by bracketing/bisection:
  - find lowest `V` where onset criterion is met;
  - store `V_crit`, criterion trigger, peak response metrics, and uncertainty flags.
- Fit/interpolate `V_crit(L, structure)` and report confidence/validity domain.

Before the first production batch, perform workflow validation in this sequence:

1. Static/modal baseline: sag, self-weight, modal frequencies.
2. Wind/force generation: regenerated `u_star = 0.6` consistency with
   `FORCE_3/SIM1`.
3. Time-history replay: 1024/2048-step corrected baseline metrics.
4. Output integrity: isolated `paths.output_dir`, damping-log time coverage,
   incomplete-row handling.
5. Criteria audit: C1/C2/C4/C6/C7 summary for the known `u_star ~= 0.6` case.

## 8. Coding Roadmap

1. Add named configs:
   - `config/smoke_config.yaml`
   - `config/timur_baseline.yaml`
   - `config/timur_dynamic_short.yaml`
   - `config/sweep_template.yaml`
2. Add and harden batch mode that disables `RealtimeMonitor` for automated runs while preserving the same analysis logic.
3. Extend the new wind/force generation module by validating generated `u_star = 0.6` against the existing `FORCE_3/SIM1` statistics.
4. Add optional Eurocode/code-based generation branch if needed.
5. Expose coefficient mode: updating, constant, and legacy third-year constants.
6. Add richer resumable metadata for each generated case.
7. Optionally add force-file scaling only for preliminary bracketing, with clear metadata that it is not a regenerated turbulent wind case.
8. Add postprocessing for:
   - minimum/mean element aerodynamic damping;
   - negative damping duration;
   - response envelope slope;
   - galloping ellipse / clashing overlap;
   - demand/capacity values.
9. Harden the sweep driver with resumable output metadata and automatic response-audit aggregation after each OpenSees run.
10. Implement the first parallel criteria set from `GALLOPING_CRITERIA.md`, starting with C1/C2/C4/C6/C7.
11. Add critical-boundary fitting and plotting.

## 8.1 Completed Stage 1 u_star Sweep

Date: 2026-06-02

Baseline geometry:

```text
L = 322.8 m
H/Sag = 10.48 m
```

Completed short classification sweep:

```text
u_star = 0.20, 0.30, 0.40, 0.50, 0.60
npt = 2048
dt = 0.05 s
duration = 102.4 s
```

Summary file:

```text
output/response_audit/ustar_stage1_uk_l322_h1048_n2048/stage1_summary.md
```

Current result:

- C2 negative effective damping is present in all Stage 1 cases and is therefore an early susceptibility screen.
- C2+C4 response-growth confirmation occurs at `u_star = 0.40` and `0.50`.
- `u_star = 0.60` shows stronger negative damping and larger displacement, but the late-window envelope decays after a middle-window peak; keep it as a developed-response candidate, not a final confirmed threshold from this short single-seed run.
- First short-run critical bracket for current C2+C4 workflow:

```text
0.30 < u_star_crit <= 0.40
```

Next planned refinement:

```text
u_star = 0.325, 0.350, 0.375, 0.400
```

Then repeat longer confirmation records for selected points:

```text
u_star = 0.30, 0.35, 0.40, 0.50, 0.60
```

Refinement completed on 2026-06-02:

```text
u_star = 0.325, 0.350, 0.375, 0.400
npt = 2048
duration = 102.4 s
```

Summary:

```text
output/response_audit/ustar_refine1_uk_l322_h1048_n2048/refine1_summary.md
```

Current strict short-run C2+C4 bracket:

```text
0.375 < u_star_crit <= 0.400
```

Required before multi-seed confirmation:

- update sweep generation so force/wind case names include a seed or realization id;
- otherwise, repeated `u_star` cases can reuse existing wind/force files even when a different seed is requested.

Implemented on 2026-06-02:

```text
tools/run_ustar_sweep.py --label-precision 3 --include-seed-in-name
```

Verification:

```text
python -m compileall tools/run_ustar_sweep.py
output/sweeps/dryrun_seed_names/manifest.json
```

Use this seed-aware naming for all future repeated-realization sweeps.

Long-record verification completed on 2026-06-02:

```text
u_star = 0.350, 0.375, 0.400
npt = 4096
duration = 204.8 s
seed-aware naming = true
```

Summary:

```text
output/response_audit/ustar_key_long1_uk_l322_h1048_n4096/key_long1_summary.md
```

Result:

```text
0.375 < u_star_crit <= 0.400
```

Interpretation:

- `0.350` and `0.375` are C2-susceptible but not C4-confirmed.
- `0.400` remains C2+C4-confirmed after doubling the time-history length.

Next after adopting coverage metrics:

```text
sample a broad u_star range first, then refine only where coverage curves require it
```

Repeated-seed verification completed on 2026-06-02:

```text
u_star = 0.375, 0.400
npt = 4096
duration = 204.8 s
seed_base = 20260720
```

Summary:

```text
output/response_audit/ustar_key_repeat1_uk_l322_h1048_n4096/repeat1_summary.md
```

Combined `4096`-step evidence:

```text
u_star = 0.350: C2 1/1, C4 0/1
u_star = 0.375: C2 2/2, C4 0/2
u_star = 0.400: C2 2/2, C4 1/2
```

Updated interpretation:

- The onset boundary is a transition probability band near `u_star = 0.375-0.400`, not yet a deterministic single value.
- Near-boundary C4 must be reported as a realization-dependent time-history criterion.
- Next runs should estimate confirmation probability:

```text
P(C4 confirmation | u_star, L=322.8, H=10.48, duration=204.8s)
```

Updated direction after adopting time-step coverage:

- The primary output is now a trend/function:

```text
coverage = f(u_star, L, H, criterion)
```

- The immediate fixed-`L` sweep should use a wider `u_star` range and a moderate
  number of seeds rather than dense local refinement around `0.375-0.400`.
- Local refinement is a second-stage action for curve features such as steep
  transitions, plateaus, or non-monotonic criterion behavior.
- Critical values such as `u_star_crit_C2C4_p010` are now post-processed
  iso-coverage thresholds, not the primary search target.

Window-occupancy extension added on 2026-06-02:

```text
tools/window_criteria_audit.py
output/window_criteria_audit/key_4096_window_summary.md
```

Rationale:

- Galloping is not necessarily a whole-record binary state under stochastic
  turbulent forcing.
- Near-boundary cases can satisfy C2/C4/C6/C7 only in part of the time history.
- Store each criterion as both a whole-record result and a window fraction.

Future sweep outputs should include:

```text
C2_window_fraction
C4_window_fraction
C6_window_fraction
C7_window_fraction
C2C4_window_fraction
whole_record_C2C4_confirmed
```

Future function and boundary surfaces:

```text
coverage_Ci(u_star, L, H)
u_star_crit_occupancy(L, H, p), p = 0.005, 0.010, 0.020
```

Time-step coverage workflow added on 2026-06-02:

```text
tools/time_step_coverage_audit.py
output/time_step_coverage_audit/key_4096_time_step_summary.md
```

This is now the primary limit workflow. For every future case, record:

```text
C2_problem_time_s, C2_coverage_fraction
C4_problem_time_s, C4_coverage_fraction
C6_problem_time_s, C6_coverage_fraction
C7_problem_time_s, C7_coverage_fraction
C2C4_problem_time_s, C2C4_coverage_fraction
C2C4_longest_continuous_s
```

Candidate critical boundary definitions:

```text
u_star_crit_C2C4_p005(L, H)
u_star_crit_C2C4_p010(L, H)
u_star_crit_C2C4_p020(L, H)
```

For the current `204.8 s` validation record:

```text
p = 0.005 -> about 1.024 s
p = 0.010 -> about 2.048 s
p = 0.020 -> about 4.096 s
```

L-u_star grid pilot completed on 2026-06-02:

```text
tools/run_l_ustar_sweep.py
output/sweeps/pilot_l_ustar_grid_n1024/manifest.json
output/time_step_coverage_audit/pilot_l_ustar_grid_n1024/pilot_l_ustar_grid_summary.md
```

Pilot grid:

```text
L = 300.0, 322.8 m
u_star = 0.375, 0.400
npt = 1024
duration = 51.2 s
sag_mode = baseline_parabolic
```

Validation result:

- grid config generation works;
- seed-aware wind/force path generation works;
- OpenSees execution works for all pilot cases;
- time-step coverage audit works for all pilot cases.

Next grid:

```text
L = 300, 322.8, 350 m
u_star = 0.375, 0.400
npt = 4096
```

After this validation grid, expand to broad `u_star` trend sampling first.

## 8.2 Fixed-L Broad u_star Coverage Sweep

Added on 2026-06-02 after adopting coverage metrics.

Fixed geometry:

```text
L = 322.8 m
H = 10.48 m
npt = 4096
dt = 0.05 s
duration = 204.8 s
```

Purpose:

- estimate coverage trends for all active criteria across a physically meaningful
  `u_star` range;
- compare whether C2, C4, C6, C7, and C2&C4 have different response trends;
- avoid overfitting the first transition band before seeing the whole curve.

Recommended first broad sweep:

```text
u_star = 0.20, 0.30, 0.40, 0.50, 0.60, 0.80, 1.00, 1.20
seeds_per_u_star = 2
n_cases = 16
```

Reasons:

- `0.20-0.60` covers ordinary-to-moderate UK operational/galloping context and
  the previously observed transition zone.
- `0.80-1.20` tests developed response before entering Eurocode extreme-wind
  stress-test levels.
- Two seeds per point are enough to expose gross trend and realization
  sensitivity without prematurely spending all compute on local refinement.

Optional second broad/high sweep after reviewing the first curve:

```text
u_star = 1.50, 2.00, 2.35
seeds_per_u_star = 1 or 2
```

Do this only if the first broad sweep remains numerically stable and the
developed-response trend is still unclear.

Trend outputs per `u_star`:

```text
mean/std/min/max coverage for C2, C4, C6, C7, C2&C4
mean/std/min/max problem_time_s for each criterion
mean/std/max longest_continuous_s for C2&C4
```

Second-stage refinement rule:

```text
refine where coverage_Ci changes rapidly, becomes non-monotonic, or crosses p = 0.005/0.010/0.020
```

Execution update on 2026-06-02:

```text
completed coverage samples = 15
non-normal / failed samples = 2
final summary = output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/ustar_coverage_summary.md
core trend curve = output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/coverage_curves_core.svg
all criteria curve = output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/coverage_curves_all.svg
```

The broad sweep confirmed that the research should use trend curves and not a
single binary critical threshold:

- C6 large-response coverage increases strongly from `u_star = 0.50` onward.
- C4 rolling-growth coverage is elevated but non-monotonic, so more seeds are
  needed before using it as a smooth probability-like curve.
- C2 negative-damping coverage is highest in the low-to-mid range and declines
  in the developed large-response range.
- C2&C4 is a strict simultaneous-mechanism marker and remains small.
- C7 remains uncalibrated and should be excluded from primary galloping claims.

Important numerical note:

- some high-`u_star` cases wrote more than 4096 `Dynamic.out` rows because of
  adaptive nonlinear substep records;
- production coverage comparisons should use `--max-records 4096` for the
  common target window while retaining raw row count as a numerical-severity
  diagnostic.

Recommended next step:

```text
For L = 322.8, repeat u_star = 0.50, 0.60, 0.80, 1.00 with 3 to 5 additional seeds.
Then fit provisional mean and uncertainty bands for C4, C6, and C2&C4.
After that, expand to L = 300, 350, 400 m using the same broad u_star grid.
```

Execution update on 2026-06-03:

- The extra-seed fixed-L step has been completed.
- Key-range completed sample counts are now:

```text
u_star = 0.50 -> 5 completed, 3 failed/non-normal
u_star = 0.60 -> 6 completed, 1 failed/non-normal
u_star = 0.80 -> 7 completed, 0 failed/non-normal
u_star = 1.00 -> 6 completed, 1 failed/non-normal
```

- Updated result files:

```text
output/sweeps/fixedL322_key_ustar_extra_seeds_n4096_s5/
output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/ustar_coverage_summary.md
output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/coverage_curves_core.svg
```

Current conclusion:

- C6 is the most stable severity trend metric and rises from about `0.35` at
  `u_star = 0.50` to about `0.89` at `u_star = 1.00`.
- C4 remains a useful response-growth mechanism metric, but must be reported
  with uncertainty bands.
- C2&C4 is too conservative to be the only response probability curve; retain it
  as a strict simultaneous-mechanism marker.
- Failed/non-normal run counts should become a fourth output curve alongside
  C4, C6, and C2&C4 coverage.

Next L-expansion recommendation:

```text
L = 300, 322.8, 350, 400 m
u_star = 0.40, 0.50, 0.60, 0.80, 1.00
seeds_per_point = 3 initially
npt = 4096
dt = 0.05 s
```

Rationale:

- `L = 322.8` now has enough seed coverage to act as the baseline anchor.
- `L = 300` and `350` test local span sensitivity without changing the model too
  aggressively.
- `L = 400` begins the lower-stiffness extension where galloping/large-response
  coverage should increase.
- Use the same `--max-records 4096` post-processing rule and store failed cases
  separately.

Execution update on 2026-06-03:

- Completed the first multi-span production sweep:

```text
L = 300, 350, 400 m
u_star = 0.30, 0.40, 0.50, 0.60, 0.80, 1.00
seeds_per_point = 3
sag_mode = parabolic_tension
```

- Matched sag values:

```text
H(300) = 9.0409 m
H(350) = 12.3057 m
H(400) = 16.0728 m
```

- Result location:

```text
output/time_step_coverage_audit/L300_350_400_ustar_grid_n4096_s3/l_ustar_coverage_summary.md
```

- Completion:

```text
54 planned cases
41 completed cases
13 failed/non-normal cases
```

Current multi-span interpretation:

- Longer spans show severe-response and failure/non-normal behavior at lower or
  comparable `u_star`, consistent with reduced modal frequency/stiffness.
- The 13 failed/non-normal cases have been audited. They are not wind-load
  generation or missing-file errors; they are OpenSees transient-analysis
  non-normal terminations during strong nonlinear response, with incomplete
  final recorder rows and no post-run `*_MAX_*.csv` summaries. Therefore the
  failed fraction should be treated as an auxiliary instability indicator.
- C6 should be the primary surface for developed response:

```text
coverage_C6(L, u_star)
```

- C4 should be retained as a growth-process surface:

```text
coverage_C4(L, u_star)
```

- C2&C4 should remain the strict simultaneous-mechanism surface, while the
  failed/non-normal fraction should be reported as an auxiliary instability
  surface:

```text
coverage_C2C4(L, u_star)
failed_fraction(L, u_star)
```

Recommended immediate next step:

```text
Add 2-3 extra seeds at cells with high failure rate or single completed sample:
L=300: u_star=0.80
L=350: u_star=0.80, 1.00
L=400: u_star=0.50, 0.80
```

Then generate the first 2D contour/heatmap package for C4, C6, C2&C4, and
failed_fraction.

When adding extra seeds, retain the same failed-case audit rule:

```text
missing post-run MAX summary + incomplete Dynamic.out final row
    -> non-normal dynamic termination
    -> counted in failed_fraction(L, u_star)
```

Execution update on 2026-06-03:

- The supplementary seed plan above has been executed.
- Combined dataset:

```text
64 planned cases
48 completed cases
16 failed/non-normal cases
```

- Current primary result package:

```text
output/time_step_coverage_audit/L300_350_400_ustar_grid_n4096_s3_plus_extra/result_package/
```

- The package contains:

```text
coverage_big_table_by_geometry.xlsx
coverage_tables_all_geometries.png
coverage_table_L300_H9.041.png
coverage_table_L350_H12.306.png
coverage_table_L400_H16.073.png
C2C4_surface.png
C2_negative_damping_surface.png
C4_growth_surface.png
C6_large_response_surface.png
C7_surface.png
failed_fraction_surface.png
```

Next research step:

```text
Use the plus_extra package as the current multi-span baseline, then decide
whether to add more L levels before fitting/interpolating the final
coverage(L, u_star) response surfaces.
```

Report update on 2026-06-04:

- Current formal report:

```text
output/reports/galloping_multispan_plus_extra/Galloping_Multispan_TimeDomain_Coverage_Report.docx
```

- The report now emphasizes:
  - methodology and research framework;
  - time-domain coverage definition;
  - separate criteria design;
  - non-normal termination as an auxiliary instability surface;
  - C7 limitation and need for future engineering recalibration.

- QA note:
  - Structural DOCX QA passed.
  - Visual render QA could not be completed because LibreOffice/`soffice` is
    unavailable in this runtime.

Meeting-material update on 2026-06-09:

- Current meeting deck:

```text
output/reports/galloping_meeting_deck/Galloping_Research_Framework_Workflow_Limits_Meeting.pptx
```

- Speaker notes:

```text
output/reports/galloping_meeting_deck/Galloping_Research_Framework_Workflow_Limits_Speaker_Notes.md
```

- The deck is organized to explain:
  - why the research target is `coverage_i(L, u_star)` rather than only a
    single binary critical velocity;
  - how the wind-generation, OpenSees time-history, and time-step coverage
    audit are connected;
  - why the current limits are separated into mechanism, response, and
    engineering consequence layers;
  - which literature/standard sources support each layer;
  - why C6 and failed fraction are currently the strongest trend surfaces,
    while C7 is retained but not yet calibrated for primary conclusions.

Single-point demonstration update on 2026-06-09:

- A single-point monitoring demonstration has been added for presentation and
  mechanism explanation.
- The demonstration uses the current baseline setting:

```text
L = 322.8 m
H/Sag = 10.48 m
u_star = 0.60 m/s
seed = 20260909
records used = 4096
duration = 204.8 s
```

- Monitored locations:

```text
1/4 span, midspan, and 3/4 span
nodes 26, 51, and 76
```

- Deliverables:

```text
output/single_point_demo/L322P8_U0P600_SEED20260909/
output/reports/single_point_demo_decks/Galloping_Single_Point_Demo_CN.pptx
output/reports/single_point_demo_decks/Galloping_Single_Point_Demo_EN.pptx
```

- Workflow boundary:
  - the single-point results are used to explain local displacement response,
    aerodynamic coefficient histories, and adjacent-element damping histories;
  - formal galloping limits remain the full-line/all-element time-domain
    coverage criteria.

Recommended immediate next step:

```text
Use the bilingual single-point decks for the meeting explanation of the
framework and limits. After feedback, decide whether future representative
cases should automatically generate the same point-monitoring package alongside
the full-line coverage audit.
```

Damping-flow audit update on 2026-06-09:

- Added Den Hartog term figures and an audit file:

```text
output/single_point_demo/L322P8_U0P600_SEED20260909/den_hartog_delta_curve.png
output/single_point_demo/L322P8_U0P600_SEED20260909/den_hartog_delta_timeseries.png
output/single_point_demo/L322P8_U0P600_SEED20260909/damping_formula_flow_audit/damping_formula_flow_audit.md
```

- Key finding:
  - `dC_L.txt` is consistent with `dC_L/ddegree`, so the current Tcl conversion
    to `dC_L/dradian` is correct.
  - However, the current aerodynamic table makes
    `delta_D = dC_L/dalpha + C_D` strongly negative over the dominant
    small-angle range, causing C2 to be highly sensitive.
  - C2 should remain a susceptibility/onset channel and should not be used
    alone as the final galloping severity measure.

- Workflow correction:
  - dynamic OpenSees recorders have been updated in
    `src/cable_analyser/tcl_writer.py` to include `-time`;
  - rerun the baseline single-point case before using exact displacement-growth
    time in reports or meeting slides, because the existing diagnostic plot
    used nominal row-index time while the solver had adaptive substeps.

MATLAB-Python workflow validation on 2026-06-09:

- A matched validation case has been built and executed for the baseline
  `FORCE_3/SIM1` record:

```text
tools/build_matlab_python_validation.py
output/workflow_validation/matlab_python_force3_baseline/
```

- The output package contains separate Python and MATLAB subfolders, plus a
  comparison folder:

```text
python/three_point_outputs/
matlab/three_point_outputs/
comparison/python_matlab_three_point_comparison.csv
comparison/workflow_validation_report.md
```

- The three monitoring points are:

```text
Node 26 = 1/4 span
Node 51 = midspan
Node 76 = 3/4 span
```

- The MATLAB validation copy was adjusted only for parameter/workflow parity:
  same exact catenary, same `FORCE_3/SIM1` load files, corrected aerodynamic
  damping Tcl, and time-stamped recorders.
- Result:
  - Python dynamic output reaches `160.135 s`;
  - MATLAB dynamic output reaches `186.388 s`;
  - both are non-normal/incomplete relative to the requested `204.8 s` record
    because the response enters a severe large-displacement regime.
- Important validation conclusion:
  - over `0-120 s`, MATLAB and Python agree very closely, with three-point
    displacement RMS differences below `0.001 m`;
  - therefore there is no current evidence of a fundamental mismatch in
    geometry, force-file scaling, aerodynamic coefficient interpolation, or
    damping-formula implementation;
  - the later divergence should be handled as nonlinear solver-path sensitivity
    in a galloping/large-response regime, not as a simple workflow mismatch.

Recommended next validation step:

```text
Use the matched validation package as the reference workflow check. For future
production sweeps, require explicit status fields for complete, failed, and
non-normal runs, and compute coverage metrics only over valid time-stamped
records.
```

Broken-line minimal workflow validation on 2026-06-09:

- A second validation package was created for the original three-node
  broken-line smoke model:

```text
tools/build_broken_line_minimal_validation.py
output/workflow_validation/broken_line_minimal_3node/
```

- Model definition:

```text
Geometry type = 3, broken-line V shape
L = 2.0 m
Sag = 1.0 m
Nodes = 3
Only Node 2 is dynamically free in translation
Input = FORCE_3/Test1
npt = 4096
dt = 0.05 s
```

- Output records:

```text
Dynamic.out
Velocity.out
Accel.out
Reaction.out
damping_change_log.txt
all-node exported CSV files
middle-node comparison figures
middle-node x-z trajectory figures
```

- Validation result:
  - Python and MATLAB both complete the full `204.8 s` record;
  - the unified all-record comparison table contains `33` compared channels;
  - maximum Python-MATLAB absolute difference across all compared channels is
    exactly `0`.

- Research implication:
  - the core migrated workflow is validated in the simplest broken-line
    dynamic model;
  - this supports using the Python workflow for further research after keeping
    explicit status flags for long-span nonlinear/non-normal runs;
  - when large-span cases diverge after response growth, the first explanation
    should be nonlinear solution-path sensitivity rather than a basic
    implementation mismatch.

Meeting preparation package on 2026-06-10:

- Generated a complete meeting-material package:

```text
output/reports/meeting_2026_06_10/
```

- Model-file/Tcl package:

```text
output/reports/meeting_2026_06_10/model_tcl_package/
```

- Final presentation/report files:

```text
Galloping_Meeting_Report_CN_2026_06_10.docx
Galloping_Meeting_CN_2026_06_10.pptx
Galloping_Meeting_EN_2026_06_10.pptx
```

- These materials should be used for the next meeting to explain:
  - the research objective as `coverage_i(L, u_star)`;
  - the code workflow from config to wind loads, Tcl generation, OpenSees
    response, time-step limits, and result aggregation;
  - the Tcl/OpenSees calculation flow and file responsibilities;
  - why single-point monitors are explanatory while production limits remain
    full-line/all-element coverage criteria;
  - limits for delta/Den Hartog susceptibility, negative damping, response
    growth, large displacement, and clearance/consequence;
  - current single-point and multi-span/catenary results;
  - workflow validation using both the exact three-node broken-line match and
    the catenary early-response match.

- QA note:
  - PPTX structural QA passed for both language decks;
  - DOCX structural QA passed;
  - DOCX visual render QA was attempted but skipped because the renderer could
    not find an installed office conversion executable.

- Critical-wind-speed discussion added after user follow-up:
  - The report and both PPT decks now include the code-consistent local
    negative-damping critical relative speed:

```text
U_cr,e = 4 M_e xi omega_n / (rho B L_e |Delta_D|)
```

  - Current single-point catenary demo gives:

```text
U_cr,min ~= 0.0985 m/s
equivalent u_star ~= 0.0057 m/s
```

  - Research interpretation:
    this is a local C2 mechanism threshold, not the final design critical wind
    speed. It confirms that the present aerodynamic coefficient table makes
    negative damping very sensitive; production critical boundaries should
    still be extracted from time-domain coverage surfaces.

- Meeting-material revision after user follow-up:
  - The current meeting package should not present the sweep/multi-span result
    maps as the main result. Those maps remain research outputs for later trend
    analysis, but this meeting version focuses on two examples only:
    1. the catenary three-monitor single-case demonstration;
    2. the three-node broken-line minimal MATLAB/Python/OpenSees validation.
  - The limits section should be presented mathematically:
    - each limit is a time-step indicator `I_i(t_k)`;
    - the reported value is `coverage_i = sum I_i / N_valid`;
    - `Delta_D` is the Den Hartog susceptibility term;
    - `C2` is negative total damping;
    - `C4` is rolling-window response growth;
    - `C6` is developed large response relative to sag `H`;
    - `C7` is a clearance/spacing consequence channel pending real standard
      and tower-geometry calibration;
    - `C2&C4` is a coincidence filter combining mechanism and growth.
  - Updated files:

```text
output/reports/meeting_2026_06_10/Galloping_Meeting_Report_CN_2026_06_10_v2.docx
output/reports/meeting_2026_06_10/Galloping_Meeting_CN_2026_06_10.pptx
output/reports/meeting_2026_06_10/Galloping_Meeting_EN_2026_06_10.pptx
```

- OpenSees 3.8.0 and termination diagnostics update on 2026-06-11:
  - The active solver path is now:

```text
D:\Pyprogramme\OpenSees3.8.0\bin\OpenSees.exe
```

  - OpenSees process `return_code` alone is not sufficient for classifying
    failed nonlinear transient runs. In the checked example, `OpenSees.exe`
    returned 0 while the Tcl dynamic loop reported `analyze failed, returned:
    -3 error flag`.
  - The workflow now records both process-level logs and Tcl-level analysis
    status:
    - `solver_logs/*.stdout.log`
    - `solver_logs/*.stderr.log`
    - `solver_logs/*.meta.json`
    - `analysis_status.txt`
    - `termination_audit/opensees_termination_audit.md`
    - `termination_audit/monitoring_file_summary.csv`
  - The checked `L=322.8 m`, `H=10.48 m`, `u_star=0.60`, `seed=20260909`
    case terminates early at `t ~= 160.439 s` rather than the target `204.8 s`.
    The recorded reason is:

```text
STATUS failed
MESSAGE analysis_did_not_converge_min_factor_reached
ANALYZE_RETURN_CODE -3
FACTOR 6.201018947437347e-7
MIN_FACTOR 1e-06
```

  - Research interpretation:
    this case should be treated as a failed/non-normal transient case, not as a
    completed coverage sample. Its failure is useful evidence for the auxiliary
    instability/non-normal fraction, but post-processed maxima from the
    incomplete record should not be mixed into completed-case averages.

## 9. Open Questions

- Should the production geometry be exact catenary, parabolic shallow-cable approximation, or both with quantified error?
- Should Zebra baseline use table self-weight directly or density-derived self-weight?
- Can OpenSees expose global tangent stiffness/damping matrices in this setup, or should verification rely on modal/static benchmarks?
- How much can the current TH runtime be reduced by suppressing per-step Tcl output, increasing recorder stride for exploratory sweeps, or splitting long records into representative windows?
- What ice-shape parameterization should be used for Den Hartog/Nigol coefficients?
- How should bundle number map to equivalent aerodynamic and torsional DOFs?
- What is the final primary onset criterion: negative effective damping, eigenvalue crossing, response growth, or a combined decision rule?
