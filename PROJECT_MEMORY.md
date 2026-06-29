# Project Memory: Cable Galloping Critical Boundary

Last updated: 2026-06-13

## Purpose

This repository studies the effect of galloping on overhead cables. The long-term research target is to obtain a two-variable critical boundary/function for galloping onset:

- independent variables: wind speed / wind load intensity and cable span length;
- target output: critical length and critical wind speed relationship;
- future extensions: cable structural parameters, especially bundle number and related equivalent aerodynamic / mechanical properties.

Core research principle updated on 2026-06-11:

- The purpose of this project is to simulate and study the galloping mechanism
  itself, not merely to obtain a numerically stable structural time-history
  solution.
- A workflow is not considered scientifically adequate if aerodynamic damping
  is only recorded as a post-processing/limit quantity while the OpenSees
  dynamic equation remains unaffected by the galloping energy-transfer
  mechanism.
- For galloping-mechanism simulations, the aerodynamic damping/negative damping
  effect must actively enter the time-domain equation, for example through the
  verified explicit velocity-dependent aerodynamic force channel:

```yaml
aerodynamic_damping:
  enabled: true
  writeback_mode: "record_only"

aerodynamic_force:
  enabled: true
  scale: 1.0
```

- Solver convergence, response severity, and even numerical failure are
  research observations when they arise from a verified galloping force
  mechanism. They should be diagnosed and bounded, but not suppressed merely to
  make the model easier to solve.
- Conservative record-only runs remain useful as controls and diagnostics, but
  they are not the final target workflow for galloping onset/response research.

Critical initial-state update on 2026-06-13:

- The initial gravity/pretension workflow was corrected and verified with
  no-wind/no-aero controls in
  `output/diagnostics/tension_only_control_verification/`.
- The old assumed-equilibrium shortcut was invalid when it declared gravity and
  immediately called `loadConst` without a completed static solve. In that path,
  gravity did not remain as an active balanced load, which made gravity-on and
  gravity-off controls nearly identical.
- `ElasticPPGap Fy` in OpenSees truss materials is a material stress, not an
  axial force. The Tcl generator now converts rated axial force to stress as
  `Fy = rated_strength_N / Area`. Before this correction, the tension-only
  material was capped at about 85 N instead of the intended engineering force
  scale, destroying the prestressed state.
- Verified route A, static equilibrium: ramp gravity statically, verify
  convergence/reactions, then call `loadConst -time 0.0` before transient
  analysis. Control C4 passed with max x-z displacement about 0.00233 m over
  30 s, max kinetic energy about `1.36e-10 J`, min estimated tension about
  `19.78 kN`, and total vertical support reaction about `5146.92 N`, matching
  expected self-weight.
- Verified route B, analytical assumed equilibrium: use sag-consistent,
  element-specific initial strain from the target horizontal tension component,
  keep gravity in a Constant time series, and do not call `loadConst` unless a
  static solve has actually been completed. Control C8 passed with max x-z
  displacement about 0.000305 m over 30 s, max kinetic energy about
  `4.73e-05 J`, min estimated tension about `19.79 kN`, and total vertical
  support reaction about `5147.76 N`, matching expected self-weight.
- Zero-pretension tension-only form-finding is not currently valid from the
  zero-stress state: the static solve reports a singular tangent before a
  reliable form-finding state exists.
- Formal galloping runs must start from route A or route B. The old shortcut
  must not be used for scientific results.

Typical C4 galloping verification on 2026-06-13:

- The C4 static-equilibrium route was applied to the typical galloping case
  `L = 322.8 m`, `H = 10.48 m`, `u_star = 0.6`, `dt = 0.05 s`,
  `npt = 1440` using the incremental quasi-steady aerodynamic-force branch.
- Output directory:
  `output/diagnostics/typical_incremental_qs_c4_static_balance/`.
- A workflow bug was found and fixed before the successful run: the wind reader
  stored the wind/force time vector in the global Tcl variable `time`, but the
  C4 static gravity loop reused `time` as a scalar load-step counter. This
  caused force interpolation to fail with `interpolate: vec1 and vec2 length
  mismatch`. `Wind_velocity_reader.tcl` now preserves `wind_time_vector`, and
  `Damping_shifter.tcl` uses that protected vector for aerodynamic interpolation.
- The successful run reached the target time `72.0 s` with
  `ANALYZE_RETURN_CODE 0`.
- Main response summary: maximum resultant displacement about `1.789 m`,
  maximum resultant velocity about `2.117 m/s`, maximum resultant acceleration
  about `74.29 m/s^2`, maximum reaction/tension-scale result about `21.34 kN`.
- Element tension diagnostics remained physically admissible:
  min estimated tension about `18.69 kN`, max estimated tension about
  `21.00 kN`, maximum strain about `2.73e-5`, and slack element count was `0`
  throughout the recorded diagnostics.
- Incremental aerodynamic-force diagnostics were moderate rather than runaway:
  `F_original` range about `345.8-527.0 N`, `F_current` range about
  `352.5-548.0 N`, `total_abs_delta_force` range about `35.3-135.7 N`,
  max `total_abs_delta_force / F_original` about `0.3045`, and no coefficient
  table clipping was recorded.
- Three-point monitoring nodes were node 26 (1/4 span), node 51 (midspan), and
  node 76 (3/4 span). Effective damping indicators were negative for most of
  the run, consistent with the intended Den Hartog galloping mechanism, but the
  response remained bounded over the 72 s verification window.

## Stage Progress: Corrected Galloping-Mechanism Workflow

Date: 2026-06-13.

This is the current formal workflow for typical-case galloping simulations after
the abnormal-response investigation. It replaces the older workflow that used a
less physical damping/force treatment, allowed non-cable-like axial behavior,
and did not reliably establish gravity equilibrium before the transient
galloping simulation.

### Old workflow and observed problem

The earlier workflow could run dynamic simulations, but several diagnostic
features showed that it was not yet a defensible galloping-mechanism model:

- Aerodynamic damping was often evaluated as a diagnostic or limit quantity,
  while the actual OpenSees time-domain equation did not always receive a
  physically consistent aerodynamic energy-transfer term.
- The explicit negative-damping force branch could turn a Den Hartog
  susceptibility condition into an artificial velocity-aligned positive
  feedback force. This could over-inject energy rather than reproduce a
  quasi-steady drag/lift force balance.
- The full quasi-steady replacement branch risked double-counting the base wind
  load when it was combined with the original Path load.
- The structural cable model could enter nonphysical compression/negative
  tension, which is not acceptable for an overhead conductor.
- The assumed-equilibrium shortcut did not actually verify gravity balance.
  Gravity-on and gravity-off controls could become nearly identical, indicating
  that the transient model was not starting from a reliable self-weight and
  pretension equilibrium state.
- In the C4 static route, the Tcl variable name `time` was reused by the static
  gravity loop, overwriting the wind/force time vector and causing aerodynamic
  interpolation to fail unless a protected wind-time variable was introduced.

The most visible symptom was an abnormal large response near the late-time
typical simulations. Earlier diagnostics showed excessive motion, very large
force feedback in some branches, and physically inadmissible axial behavior in
some runs.

### Four key corrections

1. Damping participation was redefined.

   Problem solved: the old model could identify negative aerodynamic damping
   without necessarily making the galloping energy-transfer mechanism act on
   the structural equation.

   Modification: Rayleigh damping remains the structural baseline damping.
   Aerodynamic damping indicators are kept as diagnostics, while the active
   galloping mechanism is applied through a real-time aerodynamic force branch.
   The current typical workflow uses `aerodynamic_damping.writeback_mode:
   record_only` for monitoring and uses the force branch to affect the
   OpenSees transient equation.

   Scientific role: this prevents the project from becoming only a
   post-processing galloping detector. The aerodynamic mechanism now affects
   the time-domain response.

2. Aerodynamic force application was changed to incremental quasi-steady force.

   Problem solved: the old explicit equivalent-damping force could act like an
   artificially constructed positive feedback term. A full QS replacement could
   also duplicate the original static/dynamic wind load.

   Modification: the current force form is:

   ```text
   F_total = F_original + [F_current - F_reference]
   ```

   where `F_original` is the existing Path wind load, `F_reference` is the
   quasi-steady force evaluated at the reference wind and reference geometry,
   and `F_current` is recalculated at each OpenSees time step from current nodal
   velocity, local deformed direction, relative wind velocity, angle of attack,
   and `C_D/C_L` tables.

   Scientific role: the original weather/load realization is preserved, the
   static base load is not counted twice, and motion-induced aerodynamic
   feedback is added as a physically interpretable increment.

3. Cable element behavior was changed to tension-only.

   Problem solved: overhead cables should not carry compression. Negative
   tension/slack artifacts can cause unrealistic geometry changes and then
   contaminate the aerodynamic calculation through spurious relative velocity
   and force direction.

   Modification: the typical workflow uses a `corotTruss + ElasticPPGap +
   InitStrainMaterial` structural model. `ElasticPPGap Fy` is written in stress
   units as `rated_strength_N / Area`, not as a force. Element strain, estimated
   tension, and slack count are logged throughout formal diagnostic runs.

   Scientific role: the cable remains mechanically cable-like. In the latest
   C4 typical verification, minimum estimated tension stayed about `18.69 kN`,
   maximum estimated tension about `21.00 kN`, maximum strain about `2.73e-5`,
   and slack count stayed `0`.

4. Gravity and initial equilibrium were corrected.

   Problem solved: the transient simulation must start from a verified
   self-weight and pretension equilibrium. The old shortcut did not do this
   reliably. It could remove or freeze gravity incorrectly, and in the C4 route
   the static loop also overwrote the wind time vector.

   Modification: two verified routes now exist. Route C4 ramps gravity in a
   static solve, checks convergence/reactions, then calls `loadConst -time 0.0`
   before transient analysis. Route C8 analytically constructs the sag-
   consistent initial strain, keeps gravity in a Constant time series, and does
   not call `loadConst` unless a static solve has occurred. The formal typical
   galloping verification used C4. `Wind_velocity_reader.tcl` now preserves
   `wind_time_vector`, and `Damping_shifter.tcl` uses that protected vector for
   aerodynamic interpolation.

   Scientific role: the dynamic galloping response is no longer contaminated by
   an unbalanced gravity release or by a static-analysis variable overwriting
   wind/force timing.

### Latest verified typical workflow

The current verified typical workflow is:

```text
Generate geometry and tension-only elements
  -> static gravity ramp with pretension/init strain
  -> verify self-weight reactions and static convergence
  -> loadConst only after successful static equilibrium
  -> modal/Rayleigh structural damping baseline
  -> transient OpenSees solve with original Path wind load
  -> real-time incremental quasi-steady aerodynamic correction
  -> record displacement, velocity, acceleration, reaction, support reaction,
     element strain/tension, aerodynamic force decomposition, nodal aero power,
     C_D/C_L, Delta_D, effective-damping indicator, and x-z paths
```

Latest verified output:

- Config:
  `output/diagnostics/typical_incremental_qs_c4_static_balance/typical_L322P8_H10P48_U0P6_incremental_qs_c4_static_balance_72s.yaml`
- OpenSees output:
  `output/diagnostics/typical_incremental_qs_c4_static_balance/run/`
- Point monitoring:
  `output/diagnostics/typical_incremental_qs_c4_static_balance/point_monitoring/`
- Force diagnostics:
  `output/diagnostics/typical_incremental_qs_c4_static_balance/analysis/`

### Root-cause interpretation of the abnormal large response

The fourth correction, gravity and initial-equilibrium control, was the change
that finally closed the abnormal-response problem in the typical verification.
However, the correct interpretation is not simply "gravity alone caused the
large response." The investigation points to a layered cause:

- The direct workflow root cause was the initial-state/time-history control:
  the old assumed-equilibrium shortcut did not verify gravity balance, and the
  C4 path exposed that the global Tcl `time` variable could be overwritten by
  static loading. This made the transient state and aerodynamic interpolation
  unreliable. This is why the fourth correction was decisive.
- The third correction was a necessary physical safeguard. Without tension-only
  behavior and correct `ElasticPPGap` stress units, the model could enter
  negative or capped axial-force states. That did not by itself explain every
  abnormal response, but it made any later aerodynamic runaway impossible to
  interpret scientifically.
- The second correction prevented a separate force-model artifact: direct
  equivalent negative-damping force or full-force replacement could create
  artificial energy injection or duplicate the base wind load. The final C4 run
  shows the incremental force remained moderate, with max
  `total_abs_delta_force / F_original` about `0.3045`.
- The first correction made the model mechanistically valid for galloping, but
  it was not the main reason the abnormal late response disappeared.

Therefore, the best current conclusion is:

```text
The core trigger of the previously abnormal response was the unverified initial
state and time-vector workflow, resolved by the fourth correction. The other
three corrections were still necessary because they removed independent
physical/modeling artifacts that could otherwise mimic or amplify galloping.
```

This conclusion should remain provisional until the same C4 workflow is tested
over multiple `u_star`, span, and seed values. For now, the latest typical case
supports the interpretation that the large abnormal response was primarily a
workflow/initial-state artifact, not a confirmed physical galloping instability.

This file is the persistent project memory. Before each future change, read this file first. After each meaningful change, update the relevant sections below with:

- what changed;
- why it changed;
- affected files/functions;
- assumptions and validation results;
- open research questions.

## Current Project Snapshot

The codebase is a Python refactor/wrapper around an older MATLAB + OpenSees Tcl workflow in `TIMUR4/`. The active workflow is:

1. Read YAML configuration from `config/default_config.yaml`.
2. Generate cable geometry, section properties, tributary lengths, nodal masses.
3. Generate OpenSees `Input.tcl` for static/modal or time-history analysis.
4. Run OpenSees through a configured executable/batch file.
5. During time-history analysis, update aerodynamic damping through Tcl procedures.
6. Read OpenSees output files and compute peak displacement, reaction, and clearance.
7. Save summary CSV files in `output/`.

The current implementation can run `STATIC`, `MODAL`, and `TH` modes. For `TH`, it always performs a modal run first so `output/modal_simple.out` exists for Rayleigh/aerodynamic damping parameters.

Important note: several existing Python comments and README/config Chinese strings are mojibake/encoding-corrupted, but the executable logic is still readable.

Current research planning files:

- `RESEARCH_PLAN.md`: standards/literature-informed research plan, onset criteria, model audit findings, and coding roadmap.
- `GALLOPING_CRITERIA.md`: parallel, time-resolved galloping criteria design from aerodynamic susceptibility through engineering limit-state exceedance.
- `GEOMETRY_BASELINE.md`: source-backed baseline for span length `L`, sag/downward catenary height `H`, and the first L-H sweep rule.
- `USTAR_RANGE_UK.md`: UK-informed staged `u_star` range linking ordinary wind climate, RICA galloping context, and Eurocode/UK National Annex basic wind speeds.
- `tools/model_sanity_audit.py`: lightweight audit script for geometry, section/mass, damping parameters, and force/wind-file consistency.
- `config/smoke_config.yaml`: clean UTF-8 version of the original 2 m smoke-test configuration.
- `config/timur_baseline.yaml`: Timur baseline configuration with Zebra ACSR, 322.8 m span, 10.48 m catenary sag, 101 nodes, and 15.90 N/m tabulated self-weight.
- `output/model_audit/model_sanity_audit.md`: latest audit report.
- `output/model_audit/smoke/model_sanity_audit.md`: audit for the smoke config.
- `output/model_audit/timur_baseline/model_sanity_audit.md`: audit for the Timur baseline config.
- `tools/dynamic_wind_audit.py`: dynamic wind-input audit for time base, wind profile, PSD, coherence, and force/wind consistency.
- `output/wind_audit/timur_baseline/dynamic_wind_audit.md`: latest dynamic wind-input audit report for Timur baseline.
- `tools/dynamic_response_audit.py`: dynamic response audit for OpenSees output coverage, peak response metrics, response-envelope growth, and aerodynamic damping logs.
- `config/timur_dynamic_short.yaml`: short 51.2 s Timur-scale dynamic calibration case using the same 322.8 m baseline but `npt = 1024`.
- `output/response_audit/timur_dynamic_short/dynamic_response_audit.md`: latest short dynamic-response audit.
- `src/cable_analyser/wind_forces.py`: in-project wind and aerodynamic-force generator ported from the friction-based branch of `WIND_SIMULATION.mlx`.
- `tools/generate_wind_forces.py`: command-line entry point for generating new `u_star` wind/force cases.
- `tools/compare_wind_force_cases.py`: statistical comparison tool for generated wind/force cases against a baseline case.
- `tools/run_ustar_sweep.py`: prepares/generates/optionally executes a reproducible `u_star` sweep.
- `tools/run_l_ustar_sweep.py`: prepares/generates/optionally executes reproducible `L-u_star` sweeps, with seed-aware labels and `--continue-on-error` for severe nonlinear cases.
- `tools/time_step_coverage_audit.py`: applies the active time-domain galloping criteria to each recorded response; supports `--max-records` to enforce a fixed target record window.
- `tools/aggregate_time_step_coverage.py`: aggregates case-level time-step coverage audits by `u_star`, records failed/non-normal cases, and outputs coverage curves.
- `config/timur_generated_ustar.yaml`: example config where `u_star` is the initial wind-load independent variable and `wind_generation.enabled = true`.
- `output/reference_extraction/`: extracted text from Timur's DOCX and local PDF literature.
- `output/reference_extraction/week7_galloping.txt`: extracted text from user-provided `Week7.pdf` lecture notes.

## Directory Map

- `main.py`: command-line entry point.
- `config/default_config.yaml`: main research configuration, including geometry, material, analysis, damping, solver, and path settings.
- `src/cable_analyser/`: active Python package.
- `tcl_procedures/`: OpenSees Tcl procedures used by generated `Input.tcl`.
- `data/forces/`: aerodynamic force time histories, organized as `FORCE_x/SIMx/NODE_*`.
- `data/wind/`: wind velocity time histories used by Tcl aerodynamic damping logic.
- `data/aero_coeffs/`: aerodynamic coefficient tables such as `C_D_data.txt` and `dC_L.txt`.
- `output/`: generated OpenSees outputs and summary CSVs.
- `tests/`: pytest coverage for geometry, Tcl generation, and post-processing.
- `TIMUR4/`: legacy MATLAB/Tcl source and output archive. Treat as reference unless a migration task explicitly touches it.

## Main Execution Flow

Entry:

- `main.py:9` `_build_parser()`: defines CLI arguments `--config`, `--analysis-type`, `--opensees-path`.
- `main.py:42` `main()`: builds `CableAnalysis`, applies CLI overrides, checks solver availability, calls `analysis.run()`.

Orchestration:

- `src/cable_analyser/analysis.py:22` `CableAnalysis`: owns config, geometry, solver, and top-level run logic.
- `analysis.py:30` `__init__`: loads YAML, generates geometry once, instantiates `OpenSeesSolver`.
- `analysis.py:46` `run`: dispatches by `cfg["analysis"]["type"]`.
- `analysis.py:66` `_run_static`: currently reuses `_run_modal()`.
- `analysis.py:71` `_run_modal`: writes modal `Input.tcl`, runs OpenSees.
- `analysis.py:78` `_run_time_history`: loops over `time_history.folder_1` and `folder_2`; for each case runs modal, writes TH Tcl, writes aerodynamic damping parameters, launches realtime monitor, post-processes results, and saves CSV summaries.

Time-history pipeline:

```text
main.py
  -> CableAnalysis(config)
    -> CableGeometry.generate()
    -> TclWriter.write_modal()
    -> OpenSeesSolver.run(Input.tcl)
    -> TclWriter.write_time_history(th_path)
    -> TclWriter.write_aero_damping_params()
    -> RealtimeMonitor + OpenSeesSolver.run(Input.tcl)
    -> postprocess.load_reaction/load_displacement
    -> compute_max_displacement/compute_max_reaction/compute_clearance
    -> save_results
```

## Function And Class Reference

### Geometry: `src/cable_analyser/geometry.py`

- `CableGeometry.__init__` (`geometry.py:18`): reads geometry, material, and mass multiplier from config; computes area, second moments, polar moment, radius of gyration-like value, and self weight.
- `CableGeometry.generate` (`geometry.py:46`): returns all geometry/mass arrays used by Tcl generation.
- `_coordinates` (`geometry.py:86`): supports geometry type `1` parabolic, `2` catenary, `3` broken-line/V shape.
- `_angles` (`geometry.py:116`): element inclination angles.
- `_element_lengths` (`geometry.py:120`): 3D element lengths.
- `_tributary_lengths` (`geometry.py:130`): nodal tributary lengths.
- `_masses` (`geometry.py:138`): translational and torsional nodal mass arrays.

Research relevance: this is where span length `L`, sag, discretisation, diameter, density, and equivalent mass enter the structural model. Bundle number effects will likely require extending material/section/equivalent aerodynamic parameters here or in config.

### Tcl Generation: `src/cable_analyser/tcl_writer.py`

- `TclWriter.__init__` (`tcl_writer.py:21`): stores config, geometry, and Tcl procedure directory.
- `_write_header` (`tcl_writer.py:38`): OpenSees model setup.
- `_write_nodes_and_masses` (`tcl_writer.py:47`): emits nodes and mass commands.
- `_write_section_and_elements` (`tcl_writer.py:58`): emits material, section, transformations, and beam-column elements.
- `_write_custom_function_caller` (`tcl_writer.py:97`): writes callback dispatcher for monitor/custom functions.
- `_write_boundary_conditions` (`tcl_writer.py:117`): pins the two end nodes.
- `_write_gravity_load` (`tcl_writer.py:126`): self-weight pattern.
- `_write_static_solver` (`tcl_writer.py:138`): static solver, static recorders, and gravity load increments.
- `_write_aerodynamic_loads` (`tcl_writer.py:195`): writes four force time histories per node: `H_drag`, `H_lift`, `V_drag`, `V_lift`.
- `_write_rayleigh_damping` (`tcl_writer.py:226`): reads first modal frequency and writes mass-proportional Rayleigh damping.
- `_write_modal_damping` (`tcl_writer.py:236`): writes OpenSees `modalDamping`.
- `write_modal` (`tcl_writer.py:248`): generates static + modal `Input.tcl`.
- `write_time_history` (`tcl_writer.py:280`): generates static + transient `Input.tcl`, sources wind reader, damping shifter, and adaptive transient loop.
- `write_aero_damping_params` (`tcl_writer.py:349`): writes `inputs_aerodynamic_damping.tcl` with `MassM`, `B`, `L`, `ro_air`, `omegaN`.
- `_read_first_frequency` (`tcl_writer.py:375`): reads `output/modal_simple.out`, column 2 as first modal frequency in Hz.

Research relevance: wind load case structure enters through `_write_aerodynamic_loads`; damping model choice enters through `_write_rayleigh_damping`, `_write_modal_damping`, and Tcl aerodynamic damping.

### Solver: `src/cable_analyser/solver.py`

- `OpenSeesSolver.__init__` (`solver.py:17`): stores OpenSees path and working directory.
- `run` (`solver.py:23`): checks executable, builds command, runs OpenSees, raises on nonzero return code.
- `check_available` (`solver.py:60`): accepts exact file path or executable discoverable on PATH.
- `_build_command` (`solver.py:85`): uses `cmd /c` for Windows `.bat` launchers.

Research relevance: parameter sweeps will repeatedly call this layer. Batch-running critical boundary searches should minimize manual GUI/monitor dependency.

### Postprocess: `src/cable_analyser/postprocess.py`

- `load_reaction` (`postprocess.py:13`): reads `Reaction.out`, strips optional time column, returns `[Rx, Ry, Rz]`.
- `load_displacement` (`postprocess.py:34`): reads `Dynamic.out`, strips optional time column, returns lateral `Y` and vertical `Z` matrices.
- `compute_max_reaction` (`postprocess.py:64`): peak resultant reaction.
- `compute_max_displacement` (`postprocess.py:79`): peak resultant displacement from `Y` and `Z`.
- `compute_clearance` (`postprocess.py:94`): dynamic clearance deviation from static geometry.
- `save_results` (`postprocess.py:126`): writes `{prefix}_MAX_DISP.csv`, `{prefix}_MAX_REAC.csv`, `{prefix}_MAX_CLEARANCE.csv`.

Research relevance: galloping onset criterion is not yet formalized here. Current outputs are response magnitudes; a future `gallop_detected` / critical-boundary metric should likely be added near this layer or in a new sweep/evaluation module.

### Realtime Monitor: `src/cable_analyser/realtime_monitor.py`

- `RealtimeMonitor.__init__` (`realtime_monitor.py:30`): prepares polling state and deletes stale realtime files.
- `run_solver_in_thread` (`realtime_monitor.py:74`): runs solver in a worker thread.
- `_read_realtime_state` (`realtime_monitor.py:86`): reads `output/realtime_state.txt`.
- `_read_damping_log` (`realtime_monitor.py:104`): reads recent `output/damping_change_log.txt`.
- `_setup_figure` (`realtime_monitor.py:133`): creates live matplotlib dashboard.
- `_update_data` (`realtime_monitor.py:179`): updates deque buffers.
- `_update_plots` (`realtime_monitor.py:199`): scrolls/rescales plots.
- `start_gui_loop` (`realtime_monitor.py:258`): blocks until solver is done and plot window closes.

Research relevance: useful for single-run diagnosis, but likely inconvenient for automated 2D sweeps because it blocks on the GUI window.

## Tcl Procedure Reference

- `tcl_procedures/Wind_velocity_reader.tcl`: reads `data/aero_coeffs/time.txt`, then builds `wind_velocity_per_element_H` and `wind_velocity_per_element_V` by averaging nodal wind velocities from `data/wind/SIM1/NODE_*_wind_H/V.txt`.
- `tcl_procedures/Damping_shifter.tcl`: loads aerodynamic coefficient tables, sources `inputs_aerodynamic_damping.tcl`, defines `adapt_damp`, computes relative wind/cable velocity, interpolates `CD` and `dCL`, computes equivalent damping `xi_total`, logs damping changes, and calls `setElementRayleighDampingFactors`.
- `tcl_procedures/dynamic2.tcl`: adaptive transient analysis loop; calls registered before/after analyze functions, writes `realtime_state.txt`, manages time-step factor, and terminates at `total_duration`.
- `tcl_procedures/interpolate.tcl`: interpolation helper used by wind and aerodynamic damping logic.
- `tcl_procedures/readColumnFromFile.tcl`: column reader used by wind/aero Tcl procedures.
- `tcl_procedures/PROCEDURE_OLD.tcl`: legacy modal procedure `modal1`.
- `tcl_procedures/PROCEDURE_Raf_6dof.tcl`: modal procedure `modal`, produces `modal_simple.out`.

## Configuration Parameters Of Research Interest

From `config/default_config.yaml`:

- `geometry.L`: current span length control variable.
- `geometry.Sag`: sag; should be included in sensitivity tracking even if not a primary independent variable.
- `geometry.discretisation`: mesh spacing; affects node count and number of required force/wind files.
- `material.Dia`, `E`, `G`, `ro`: cable equivalent properties.
- `analysis.fiber_section`: `0` elastic beam-column, `1` force beam-column with fiber section.
- `analysis.pretension_load`: enters initial strain material.
- `analysis.multiplier_vertical_load`, `analysis.multiplier_mass`: load/mass scaling.
- `time_history.folder_1`: force/wind-load family names such as `FORCE_3`.
- `time_history.folder_2`: simulation/run names such as `Test1`.
- `time_history.dt`, `npt`: transient time step and duration.
- `time_history.ro_air`: air density used by aerodynamic damping.
- `damping.model`: `Rayleigh` or `Modal`.
- `damping.xi`: baseline structural damping ratio.
- `paths.forces_dir`, `paths.wind_dir`, `paths.aero_coeffs` implied by Tcl: data paths for force, wind, and coefficient tables.

## Current Outputs And Meaning

- `output/Dynamic.out`: nodal displacement history.
- `output/Reaction.out`: reaction history at node 1.
- `output/Velocity.out`: nodal velocity history.
- `output/Accel.out`: nodal acceleration history.
- `output/Static.out`: static displacement output.
- `output/modal_simple.out`: modal frequencies and participation data.
- `output/damping_change_log.txt`: aerodynamic damping updates from Tcl.
- `output/realtime_state.txt`: single-step state for live plotting.
- `output/*_MAX_DISP.csv`: maximum resultant displacement matrix.
- `output/*_MAX_REAC.csv`: maximum resultant reaction matrix, stored in kN by `analysis.py`.
- `output/*_MAX_CLEARANCE.csv`: maximum clearance-deviation matrix.

## Latest Dynamic Calibration Status

Date: 2026-05-29.

The model structure has been calibrated to Timur's baseline geometry and self-weight. Dynamic wind-response calibration has started with the internally consistent `FORCE_3/SIM1` wind case.

Implemented support changes:

- `src/cable_analyser/config_loader.py`: fallback YAML loader so configs can run in the bundled Python environment without PyYAML.
- `src/cable_analyser/analysis.py`: no-GUI time-history mode when `display.realtime_monitor: false`; stale realtime/damping logs are cleared before each TH run.
- `tcl_procedures/Damping_shifter.tcl`: debug flag and damping-log stride to reduce excessive logging.
- `tcl_procedures/dynamic2.tcl`: debug flag for several checkpoint/procedure messages.
- `tools/dynamic_response_audit.py`: response-output and damping-log audit script.

Validation runs:

- Full `config/timur_baseline.yaml` TH run was attempted. It timed out after 900 s of wall time at about 160 s simulated time / 4.9% progress. This proves the chain starts but also shows the full case is too slow for routine calibration until output/log verbosity and/or run strategy is improved.
- Short `config/timur_dynamic_short.yaml` TH run completed successfully to 51.2 s simulated time.

Short-run modal/dynamic results:

- Mode 1 frequency: `0.171003521 Hz`, period `5.84783 s`, dominant MY participation about `80.995%`.
- Mode 2 frequency: `0.340307129 Hz`.
- Mode 3 frequency: `0.341752038 Hz`.
- Total translational mass reported by OpenSees: about `524.839` in MX/MY/MZ.
- Peak displacement: `1.85014 m`, at node 42 (`x = 132.348 m`).
- Peak reaction: `24.2736 kN`.
- Max clearance metric: `0.215955 m`.
- Min clearance metric: `-0.307773 m`.
- Output coverage: 101 nodes, 1024 dynamic/reaction/velocity/acceleration steps, `dt = 0.05 s`.
- Response envelope: late-window p95 displacement is about `2.7-2.8x` early-window p95, but late/mid ratio is about `0.96`; the response grows from startup but does not keep growing through the final window.
- Aerodynamic damping log: 5093 sampled entries, `xi_total` range about `0.02723` to `0.12018`, mean `0.05155`, negative count `0`.

Current interpretation:

- Wind input, force input, OpenSees transient analysis, response output, and damping-log generation are functioning for the short Timur-scale calibration case.
- This short `u* ~= 0.60 m/s` case does not satisfy the proposed negative-effective-damping galloping criterion.
- The 51.2 s run is too short to prove absence of galloping; it is a calibration and workflow-validation run, not a production result.

## Wind And Aerodynamic Force Generation Logic

Source reviewed on 2026-05-29:

- `D:\Uob\Tower Pylon\TIMUR2\WIND_SIMULATION.mlx`
- Supporting MATLAB files: `KaimalModel.m`, `cohDavenport.m`, `get_CABLE_Geometry.m`
- Generated source data: `D:\Uob\Tower Pylon\TIMUR2\FORCES_UPDATING_COEFFS\FORCE_3\SIM1`

Current finding:

- Wind/force files used by this Python/OpenSees project are precomputed by MATLAB, not generated on the fly by `src/cable_analyser`.
- Current Python `TclWriter._write_aerodynamic_loads()` reads the four force components per node and applies them as OpenSees `Path` time series.
- The Tcl load vectors multiply file values by `1000`; this matches the original MATLAB-generated `Input.tcl`. Interpretation: MATLAB writes aerodynamic forces in kN-like values, then OpenSees receives N through the `1000` load-vector factor.

Original wind simulation chain:

1. Cable geometry is generated with:
   - `Geometry = 1` parabolic in `WIND_SIMULATION.mlx`;
   - `L = 322.8 m`;
   - `Sag = 10.48 m`;
   - `Discretisation = 3.228 m`;
   - support elevation `49.4 m`.
2. Time base:
   - `fs = 20 Hz`;
   - `M = 16`;
   - `N = 2^16 = 65536`;
   - `dt = 0.05 s`;
   - `time.txt` is written from this vector.
3. Mean wind can be generated in two modes:
   - code-based mode from Eurocode-style basic wind velocity and terrain roughness;
   - friction-based mode, currently used for the available data.
4. For the reviewed available force case:
   - `WIND_LOADING = 'FRICTION-BASED'`;
   - `u_star = 0.6 m/s`;
   - `kappa = 0.387`;
   - `z0 = 0.05 m`;
   - mean profile `U(z) = u_star / kappa * log(z / z0)`.
5. Turbulent wind is simulated with:
   - Kaimal one-point spectra from `KaimalModel.m`;
   - Davenport coherence from `cohDavenport.m`;
   - longitudinal component `u` and vertical component `w`;
   - cross-spectrum approximation between `u` and `w`.
6. Angle of attack:
   - `alpha_rad = atan2(w, u)`.
7. Aerodynamic coefficients:
   - `C_D_data.txt`;
   - `C_L_data2.txt`;
   - interpolation by `abs(rad2deg(alpha_rad))`.
8. Updating-coefficient force formula:
   - `u_T = sqrt(u^2 + w^2)`;
   - tributary projected area per node `A_i = discretisation * pi * DIAMETER / 2`, with half area at end nodes;
   - `DIAMETER = 0.02862 m`;
   - `ro_air = 1.293/1000 tons/m3`;
   - `F_D = 0.5 * C_D * ro_air * u_T^2 * A_i`;
   - `F_L = 0.5 * C_L * ro_air * u_T^2 * A_i`;
   - `F_D_X = F_D * cos(alpha_rad)`;
   - `F_D_Y = F_D * sin(alpha_rad)`;
   - `F_L_X = F_L * cos(alpha_rad + pi/2)`;
   - `F_L_Y = F_L * sin(alpha_rad + pi/2)`.
9. Files written per node:
   - `NODE_i_H_drag.txt = F_D_X`;
   - `NODE_i_V_drag.txt = F_D_Y`;
   - `NODE_i_H_lift.txt = F_L_X`;
   - `NODE_i_V_lift.txt = F_L_Y`;
   - `NODE_i_wind_H.txt = u`;
   - `NODE_i_wind_V.txt = w`;
   - `NODE_i_wind_T.txt = u_T`.

Important distinction:

- Force generation uses `ro_air = 1.293/1000 tons/m3` in MATLAB so that the written force files are compatible with the original OpenSees load scaling.
- Aerodynamic damping in Tcl uses `inputs_aerodynamic_damping.tcl`; original MATLAB TH scripts write `set ro_air 1.204`. This value is part of the damping formula, not the precomputed force-file formula. Do not change it casually without a unit-consistency audit.

Research implication:

- To increase wind loading accurately, the best next path is to port or wrap `WIND_SIMULATION.mlx` logic into a reproducible Python/MATLAB generation step with configurable `u_star`, span length, sag, node count, and random seed.
- Simple multiplication of existing force files can be useful for bracketing, but it will not update angle of attack, aerodynamic coefficients, wind coherence, or damping wind histories. It should be labeled as an engineering scaling approximation, not a faithful regenerated wind case.

Implementation update:

- `src/cable_analyser/wind_forces.py` now ports the friction-based MATLAB workflow into Python:
  - time/frequency vector generation;
  - log-law mean wind profile from `u_star`;
  - Kaimal longitudinal/vertical spectra and cross-spectrum;
  - Davenport coherence;
  - random-phase spectral simulation for `u` and `w`;
  - updating-coefficient drag/lift force generation;
  - MATLAB-compatible `NODE_*` force and wind files plus metadata.
- `tools/generate_wind_forces.py` can generate a new case without running OpenSees.
- `CableAnalysis._run_time_history()` will auto-generate a case before TH analysis when `wind_generation.enabled: true`.
- Existing generated cases are reused by default when `reuse_existing: true`, unless `overwrite: true` is set. Reuse checks the stored `u_star` and errors if the requested `u_star` differs from existing metadata.
- `TclWriter.write_time_history()` now writes `wind_data_dir` and `wind_time_file` into `Input.tcl`.
- `tcl_procedures/Wind_velocity_reader.tcl` now reads those variables instead of always using `data/wind/SIM1`, while preserving the old defaults if variables are absent.

Example command verified:

```powershell
& 'C:\Users\haoya\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\generate_wind_forces.py --config config\timur_baseline.yaml --u-star 0.8 --force-name FORCE_TEST_USTAR_0P80 --sim-name SIM_TEST --wind-dir data\wind\SIM_TEST_USTAR_0P80 --time-file data\wind\SIM_TEST_USTAR_0P80\time.txt --npt 64 --seed 123 --overwrite --metadata-out output\wind_generation_test\metadata.json
```

Validation result:

- The short generation smoke test completed.
- For `u_star = 0.8 m/s`, `npt = 64`, generated mean horizontal wind was about `13.94 m/s`, consistent with the previous `u_star = 0.6 m/s` case scaling from about `10.45 m/s`.
- Generated files were written under `data/forces/FORCE_TEST_USTAR_0P80/SIM_TEST` and `data/wind/SIM_TEST_USTAR_0P80`.
- `compileall src tools` passed.

Baseline reproduction validation:

- Generated Python `u_star = 0.6 m/s` cases for comparison with original MATLAB `FORCE_3/SIM1`:
  - medium case: `FORCE_PY_USTAR_0P60_N4096/SIM1`, `npt = 4096`, duration `204.8 s`;
  - longer medium case: `FORCE_PY_USTAR_0P60_N16384/SIM1`, `npt = 16384`, duration `819.2 s`;
  - full case: `FORCE_PY_USTAR_0P60_N65536/SIM1`, `npt = 65536`, duration `3276.8 s`.
- Full case generation took about 373 s wall time and completed successfully.
- Full generated wind metadata:
  - global mean horizontal wind `10.452801821 m/s`;
  - node mean range `10.321303149` to `10.690980927 m/s`;
  - mean vertical wind essentially zero;
  - angle-of-attack range about `0` to `26.37 deg`.
- Full statistical comparison report:
  - `output/wind_generation_compare/ustar_0p60_n65536/wind_force_case_comparison.md`;
  - JSON: `output/wind_generation_compare/ustar_0p60_n65536/wind_force_case_comparison.json`.
- Full comparison against original `FORCE_3/SIM1`:
  - inferred `u_star` from sampled nodes:
    - original base mean `0.60000236 m/s`;
    - Python generated mean `0.60000000 m/s`;
  - horizontal wind means at sampled nodes match to about `0.001%` or better;
  - horizontal wind standard deviations differ by about `0%` to `12%` at sampled nodes, acceptable for independent random-phase realizations;
  - coherence sample means are same order of magnitude:
    - base `0.0073-0.0094`;
    - generated `0.0071-0.0096`;
  - `H_drag` mean differences average about `0.15%`, with standard-deviation differences averaging about `4.8%`;
  - `V_lift`, the dominant vertical lift component, mean differences average about `2.6%`, with standard-deviation differences averaging about `2.6%`;
  - `H_lift` and `V_drag` means are very small near zero, so relative mean differences can look large even when standard deviations and absolute magnitudes are consistent.

Interpretation:

- The Python generator reproduces the original MATLAB force/wind-generation workflow well enough for research use as a `u_star`-controlled input generator.
- Generated histories are statistically equivalent, not time-identical, because random phases are not expected to match the original MATLAB realization.
- The full `npt = 65536` comparison should be treated as the validation baseline for future `u_star` sweeps.

Current caveats:

- The generator ports the friction-based workflow, not the Eurocode code-based branch.
- The full-coherence spectral simulation follows the MATLAB formulation and may be computationally heavy for `npt = 65536` and 101 nodes. This is acceptable for accuracy-first production runs, but small `npt` should be used only for software smoke tests.
- Generated wind cases should use unique force/wind directory names unless `overwrite: true` is intentional.

## u_star Sweep Infrastructure

Implemented on 2026-05-29:

- `tools/run_ustar_sweep.py` creates per-case YAML configs, force/wind directory names, output directories, and a sweep manifest.
- It can run in three modes:
  - prepare only: write configs and manifest;
  - `--generate`: also generate wind/force files;
  - `--execute`: also run OpenSees TH analyses.
- Production scan manifest prepared:
  - `output/sweeps/ustar_baseline_scan/manifest.md`;
  - config directory: `output/sweeps/ustar_baseline_scan/configs`;
  - values: `u_star = 0.60, 0.80, 1.00, 1.20, 1.50, 2.00`;
  - `npt = 65536`, `dt = 0.05 s`.
- Smoke scan verified:
  - command generated `u_star = 0.6` and `0.8`, `npt = 256`;
  - manifest: `output/sweeps/ustar_smoke/manifest.md`;
  - generated sample files under `data/forces/FORCE_PY_USTAR_0P6_N256/SIM1` and `data/forces/FORCE_PY_USTAR_0P8_N256/SIM1`.

Dynamic-response assessment update:

- `tools/dynamic_response_audit.py` now includes `galloping_assessment`.
- Current candidate triggers:
  - negative damping: `damping_log.negative_count > 0`;
  - sustained growth: global response envelope `late_over_mid >= 1.20` and `late_over_early >= 1.50`.
- Re-audited the existing short Timur dynamic run:
  - `output/response_audit/timur_dynamic_short_with_assessment/dynamic_response_audit.md`;
  - result: `galloping_candidate = False`.

## Galloping Mechanism And Critical Conditions

Updated on 2026-05-29 after reading:

- `C:\Users\haoya\Downloads\Week7.pdf`;
- extracted text: `output/reference_extraction/week7_galloping.txt`;
- local literature, especially Rossi et al. 2020 and Chabart & Lilien 1998.

Mechanism confirmed:

- Galloping is a low-frequency, large-amplitude aeroelastic instability of slender structures.
- For overhead conductors it is classically associated with accreted ice/snow or otherwise asymmetric aerodynamic sections.
- It is not ordinary gust buffeting; it can occur in smooth wind because body motion changes the relative wind angle and hence the aerodynamic force.
- The Den Hartog vertical galloping mechanism is quasi-steady:
  - relative wind changes angle of attack;
  - lift/drag coefficients change with angle;
  - the motion-dependent aerodynamic force can act in the direction of motion;
  - that term is equivalent to aerodynamic damping;
  - if total damping becomes negative, vibration amplitude grows exponentially in the linear regime.
- Literature adds that Den Hartog is a vertical-galloping screen, while Nigol/Clarke covers torsional galloping/coupling. For the current single-conductor vertical response workflow, Den Hartog/effective damping is the primary criterion; torsional/bundle extensions remain future work.

Important correction:

- `data/aero_coeffs/dC_L.txt` stores `dC_L/dalpha` per degree, inherited from the original MATLAB line `diff(C_L)/diff(alpha_value)` where `alpha_value` is in degrees.
- Den Hartog's criterion requires alpha in radians.
- Therefore the damping logic must use:

```text
dCL_rad = dCL_degree * 180 / pi
delta_D = dCL_rad + C_D
```

- `tcl_procedures/Damping_shifter.tcl` has been corrected to convert the stored derivative from per degree to per radian before computing `xi_total`.
- `src/cable_analyser/tcl_writer.py` now writes `xi_structural` from `damping.xi`; `Damping_shifter.tcl` uses it instead of hard-coded `0.01`.

Current critical-condition hierarchy:

1. Aerodynamic susceptibility screen:

```text
delta_D(alpha) = dC_L/dalpha + C_D < 0
```

where `alpha` is in radians. This is necessary for Den Hartog vertical galloping but not sufficient for a full line response boundary.

2. Linear effective-damping threshold:

```text
xi_total = xi_structural + rho_air * U_rel * B * L_e / (4 * M_e * omega_n) * delta_D
incipient instability when xi_total < 0
```

The corresponding local screening speed is:

```text
U_crit = -4 * M_e * omega_n * xi_structural / (rho_air * B * L_e * delta_D), for delta_D < 0
```

This is a screening value; final interpretation should use full dynamic simulation because modal mass, mode shape, nonlinear motion, and spatially varying wind matter.

3. Time-history galloping candidate:

- `tools/dynamic_response_audit.py` now reports `galloping_assessment`.
- A candidate is triggered by sustained negative effective damping or sustained response-envelope growth.
- Current thresholds:
  - `negative_damping_seen`: any logged `xi_total < 0`;
  - `sustained_negative_damping`: `negative_fraction >= 0.005` and `min_xi < -1e-4`;
  - `sustained_growth`: global response envelope `late_over_mid >= 1.20` and `late_over_early >= 1.50`;
  - `confirmed_galloping`: sustained negative damping and sustained growth.

4. Engineering limit-state exceedance remains separate:

- tension capacity;
- conductor clash/clearance;
- displacement thresholds.

These are consequences/risk measures, not the physical onset criterion itself.

Audit results:

- `tools/galloping_criterion_audit.py` was added.
- Latest report:
  - `output/galloping_criterion/timur_dynamic_short/galloping_criterion_audit.md`.
- With stored per-degree derivative, Den Hartog `delta_D` never becomes negative, which explains the previous false stability tendency.
- With corrected per-radian derivative, `delta_D` has negative regions. The smoothed audit finds broad negative ranges including approximately `0-11.9 deg` and several ranges between about `20.7-29.9 deg`.
- The raw local `U_crit` screening values can be very low because the aerodynamic coefficient slope is steep and noisy; use them as susceptibility markers, not final boundary values.
- The previous short TH response audit was produced before this damping-unit correction; it is useful for workflow validation but not a valid final galloping/non-galloping conclusion under the corrected mechanism.

Corrected-damping TH test:

- Run completed on 2026-05-29:

```powershell
& 'C:\Users\haoya\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' main.py --config config\timur_dynamic_short.yaml --analysis-type TH
```

- This reran the 51.2 s Timur short case with corrected Den Hartog derivative units.
- Response audit:
  - `output/response_audit/timur_dynamic_short_corrected_damping/dynamic_response_audit.md`;
  - JSON: `output/response_audit/timur_dynamic_short_corrected_damping/dynamic_response_audit.json`.
- Modal frequencies stayed unchanged:
  - mode 1 `0.171003521 Hz`;
  - mode 2 `0.340307129 Hz`;
  - mode 3 `0.341752038 Hz`.
- Peak response metrics in this short window stayed at:
  - max displacement `1.85014 m`;
  - max reaction `24.2736 kN`;
  - max clearance metric `0.215955 m`.
- Damping changed fundamentally:
  - damping-log samples: `5094`;
  - `min_xi = -0.25519`;
  - `max_xi = 0.04738`;
  - `mean_xi = -0.01747`;
  - negative entries: `1222`;
  - negative fraction: `0.23989`.
- Galloping assessment:
  - `galloping_candidate = True`;
  - `confirmed_galloping = False`;
  - triggers: `negative_effective_damping_seen`, `sustained_negative_effective_damping`;
  - sustained response growth: `False` because late/mid envelope ratio is about `0.959`.

Interpretation:

- The corrected mechanism now detects aerodynamic negative damping even at the `u_star ~= 0.6` baseline wind case.
- The short 51.2 s run is long enough to verify mechanism activation but too short to confirm galloping by response growth.
- Next physical test should be a longer corrected-damping run, preferably at `u_star = 0.6` for baseline continuity and then `u_star = 0.8/1.0` if growth is still absent.

Longer corrected-damping mechanism verification:

- Implemented output-directory routing for OpenSees recorders:
  - `src/cable_analyser/tcl_writer.py` now writes modal/static/dynamic recorder files to `paths.output_dir`;
  - `src/cable_analyser/analysis.py` creates `paths.output_dir` before solver runs;
  - `tcl_procedures/Damping_shifter.tcl` and `tcl_procedures/dynamic2.tcl` use the configured output directory for damping/realtime logs.
- Added robust incomplete-row handling in `tools/dynamic_response_audit.py`, because failed nonlinear analyses can leave a final partial recorder line.
- Added mechanism-verification configs:
  - `config/timur_dynamic_2048.yaml`, 102.4 s, completed successfully;
  - `config/timur_dynamic_3072.yaml`, target 153.6 s, reached about `150.531 s` before convergence failure near 98% progress;
  - `config/timur_dynamic_4096.yaml`, target 204.8 s, reached about `160.135 s` before convergence failure.
- Complete 2048-step verification report:
  - `output/response_audit/timur_dynamic_2048_corrected_damping/dynamic_response_audit.md`.
- 2048-step results:
  - max displacement `2.20825 m`;
  - max reaction `26.6719 kN`;
  - damping samples `10189`;
  - `min_xi = -0.28129`;
  - `mean_xi = -0.02586`;
  - negative fraction `0.27382`;
  - global late/early envelope ratio `1.58333`;
  - `galloping_candidate = True`.
- 3072-step near-instability report:
  - `output/response_audit/timur_dynamic_3072_corrected_damping/dynamic_response_audit.md`.
- 3072-step results before convergence failure:
  - damping-log end time `150.53119 s`;
  - max displacement `6.92909 m`;
  - max reaction `212.672 kN`;
  - `min_xi = -0.56847`;
  - `mean_xi = -0.04411`;
  - negative fraction `0.35034`;
  - global late/early envelope ratio `3.25447`;
  - convergence failure occurred after the response had entered a much larger nonlinear range.
- 4096-step exploratory result:
  - max displacement `8.88208 m`;
  - max reaction `271.969 kN`;
  - convergence failure near `160.135 s`;
  - the first 4096 run happened before the damping-log output-directory fix, so its response metrics are useful but its damping log is missing.

Interpretation:

- The corrected mechanism is now verified at three levels:
  1. coefficient-level Den Hartog audit shows negative `delta_D` only after the per-degree to per-radian derivative conversion;
  2. time-history logs show sustained negative effective damping in complete 51.2 s and 102.4 s runs;
  3. longer runs show response amplification into a severe nonlinear regime and eventual convergence failure around 150-160 s.
- The current strict `confirmed_galloping` flag remains `False` because its sustained-growth rule requires `late_over_mid >= 1.20`; this is conservative and can miss cases that grow strongly early and then approach a large-amplitude nonlinear/limit-cycle or numerical-instability region.
- For boundary extraction, keep two labels:
  - `incipient_galloping`: sustained negative effective damping;
  - `developed_large_response`: strong response growth, large displacement/reaction, or convergence failure after response amplification.
- The next coding step should refine the galloping classifier so it separates incipient negative damping, developed large-amplitude galloping/limit-cycle behavior, and numerical nonconvergence caused by excessive response.

## Parallel Criteria Design

Updated on 2026-06-02:

- Added `GALLOPING_CRITERIA.md` to define a parallel criterion set instead of prematurely combining all indicators into one intersection rule.
- On 2026-06-02, each criterion was expanded with a selection rationale and supporting references from Week 7, Timur, Rossi et al. 2020, Chabart and Lilien 1998, ICWE14, Hagedorn, Zulli/Piccardo/Luongo, Ferretti et al., EN 1991-1-4, EN 50341, EN 50182, IEC 60826, and National Grid RICA.
- Criteria are designed to be evaluated independently over time for each run:
  - `C0` input and standard-range context;
  - `C1` Den Hartog aerodynamic susceptibility;
  - `C2` effective negative damping;
  - `C3` aerodynamic work / energy injection;
  - `C4` dynamic response growth;
  - `C5` low-frequency large-amplitude galloping signature;
  - `C6` developed large response / nonlinear instability;
  - `C7` engineering limit-state exceedance;
  - `C8` future linearized eigenvalue / stability boundary.
- First implementation should focus on `C1`, `C2`, `C4`, `C6`, and `C7`, because existing damping logs, displacement/reaction outputs, conductor strength data, and RICA/Timur thresholds already support them.
- The first output labels should be independent:
  - `aero_susceptible`;
  - `incipient_galloping`;
  - `energy_injection`;
  - `response_growth`;
  - `galloping_signature`;
  - `developed_large_response`;
  - `engineering_exceedance`;
  - `eigen_unstable`.
- Each criterion should store trigger status, first/last trigger time, duration or fraction, severity, and affected nodes/elements. This will allow separate critical boundaries such as `u_star_crit_by_C2(L)` and `u_star_crit_by_C7(L)`.
- Criteria check conclusion: no criterion should be deleted at this stage; C1/C2/C4/C6/C7 should be implemented first, with C3/C5/C8 added after the initial workflow is stable.
- Workflow validation sequence before batch testing:
  1. static/modal baseline;
  2. wind/force generation consistency;
  3. 1024/2048-step corrected time-history replay;
  4. isolated output and damping-log integrity;
  5. criteria audit for a known `u_star ~= 0.6` case.
- Initial staged `u_star` plan:
  - calibration sweep: `0.20, 0.30, 0.40, 0.50, 0.60`;
  - refinement step: `0.025` to `0.05` near first trigger;
  - developed-response sweep: `0.70, 0.80, 1.00, 1.20`;
  - high-load envelope: `1.50, 2.00` after lower-bound behavior is understood.

## Test Coverage

Existing pytest tests cover:

- geometry endpoint/symmetry/shape, tributary length identity, self-weight formula;
- Tcl node/element/fix counts, force time series count, aerodynamic damping parameter file;
- postprocess output parsing, resultant reaction/displacement, clearance formula.

Current command:

```powershell
pytest tests -v
```

OpenSees execution is not covered by unit tests because it depends on the local solver installation and data files.

## Known Issues / Risks

- The repository is not currently a git repository, so changes should be logged carefully in this file.
- README/config/code comments contain mojibake; future documentation should use clean UTF-8.
- The default config is currently a 2 m smoke-test model with `geometry.type = 3` broken-line/V shape, not the 322.8 m Timur baseline.
- With only three nodes, the current V-shape and parabolic profile coincide at the sampled nodes, so shape checks can be misleading unless mesh resolution is increased.
- Timur's baseline uses Zebra self-weight 15.90 N/m, while the current code's density-derived self-weight is 21.95 N/m for the default material values.
- `CableGeometry` now supports `material.self_weight_N_per_m`; use this for tabulated conductor self-weight when reproducing published conductor data.
- `geometry.type = 2` now solves the exact catenary parameter numerically, so configured sag is reproduced at midspan.
- Existing `output/modal_simple.out` may be stale with respect to a selected config; always rerun modal analysis before using damping parameters for a new baseline or sweep.
- `config/timur_baseline.yaml` uses `npt = 65536` to match available wind/force files. A longer ring-down tail should be implemented explicitly, not by silently running past the input data.
- Full Timur baseline TH is computationally slow in the present Tcl/OpenSees setup: a 900 s wall-time attempt reached only about 160 s simulated time / 4.9% progress. User preference is accuracy over runtime, so long engineering analysis time is acceptable when needed.
- `config/timur_dynamic_short.yaml` is the current dynamic calibration shortcut. It validates the chain but should not be used as final galloping evidence.
- `RealtimeMonitor.start_gui_loop()` blocks until the plot window is closed, which is not ideal for automated parameter sweeps.
- `TclWriter.write_aero_damping_params()` uses node index `1` (`MN[1]`, `DX[1]`) for damping parameters, matching the migrated MATLAB behavior, but this should be revisited for longer spans/nonuniform discretisations.
- `Wind_velocity_reader.tcl` hardcodes `data/wind/SIM1` rather than using the Python config `paths.wind_dir` or `time_history.folder_2`.
- Galloping onset is not yet represented as a formal boolean/criterion. Current response metrics are continuous maxima.
- Bundle number is not yet an explicit config variable or model branch.
- Changing `geometry.L` changes node count when `discretisation` is fixed, so matching `data/forces/.../NODE_*` and `data/wind/.../NODE_*` files becomes a central constraint for length sweeps.

## Research Roadmap

Near-term:

1. Preserve accuracy first; use longer engineering analysis time when necessary rather than changing model physics for speed.
2. Reproduce Timur's baseline model response metrics: Zebra ACSR, `L = 322.8 m`, sag about 10.48 m, 101 elements, catenary geometry, and Table 4 response metrics where possible.
3. Keep Timur Zebra self-weight as `15.90 N/m` for baseline reproduction; document any density-derived alternative separately.
4. Define a reproducible galloping/onset criterion from Den Hartog screening, effective negative damping, dynamic envelope growth, and/or eigenvalue crossing.
3. If the current case does not reach a galloping boundary, explore longer spans/lower stiffness and higher wind loading.
4. Port or wrap the original MATLAB wind/force-generation logic from `D:\Uob\Tower Pylon\TIMUR2\WIND_SIMULATION.mlx` so `u_star`, span length, sag, and random seed can be changed consistently.
5. Add a parameter sweep driver over span length `L` and wind/force intensity.
6. Save run metadata with outputs: `L`, sag, discretisation, wind case/intensity, bundle number, damping model, onset result, peak metrics.
7. Build an interpolation/regression surface for the critical boundary.

Cable-structure extensions:

1. Add explicit `cable.bundle_number` or `material.bundle_number`.
2. Define how bundle number maps to equivalent diameter, mass, stiffness, aerodynamic coefficients, and force files.
3. Separate structural-equivalent parameters from aerodynamic-equivalent parameters if needed.

Validation:

1. Preserve unit tests for existing geometry/Tcl/postprocess behavior.
2. Add regression tests for generated Tcl when adding sweep or bundle parameters.
3. Keep representative small OpenSees cases for smoke testing if solver availability permits.

## Change Log

- 2026-05-29: Created this project memory file after initial repository review. Summarized research purpose, active workflow, code/function map, Tcl chain, risks, and roadmap.
- 2026-05-29: Added `RESEARCH_PLAN.md` with Timur baseline extraction, standards/literature source log, onset criteria, experimental design, and coding roadmap. Added `tools/model_sanity_audit.py` and generated `output/model_audit/model_sanity_audit.md`.
- 2026-05-29: Added `config/smoke_config.yaml` and `config/timur_baseline.yaml`. Updated `CableGeometry` to support tabulated self-weight and exact catenary sag. Added geometry tests for catenary sag and self-weight override. Regenerated smoke and Timur baseline audit reports.
- 2026-05-29: Added `tools/dynamic_wind_audit.py`, generated `output/wind_audit/timur_baseline/dynamic_wind_audit.md`, and set Timur baseline `npt` to 65536 to match the available wind and force histories. Audit indicates `FORCE_3/SIM1` corresponds to an internally consistent `u* ~= 0.60 m/s` wind case.
- 2026-05-29: Added no-GUI TH execution, fallback config loading, short Timur dynamic config, Tcl debug/log throttling, and `tools/dynamic_response_audit.py`. Full baseline TH timed out after 900 s at about 4.9% progress; short 51.2 s TH completed and produced a valid response audit with no negative effective damping entries.
- 2026-05-29: Reviewed original MATLAB wind/force-generation source `D:\Uob\Tower Pylon\TIMUR2\WIND_SIMULATION.mlx`. Documented Kaimal + Davenport wind simulation, friction-based `u_star = 0.6 m/s` profile, updating aerodynamic coefficients, node tributary area, drag/lift decomposition, file outputs, and OpenSees load-unit scaling.
- 2026-05-29: Added in-project wind/force generation from `u_star`: `src/cable_analyser/wind_forces.py`, `tools/generate_wind_forces.py`, and `config/timur_generated_ustar.yaml`. Updated Tcl wind reading to use configured wind directories/time files. Smoke-generated `u_star = 0.8`, `npt = 64` test data and verified compilation.
- 2026-05-29: Generated Python `u_star = 0.6` wind/force cases at `npt = 4096`, `16384`, and full `65536`; added `tools/compare_wind_force_cases.py`; compared full generated case with original `FORCE_3/SIM1`. Mean profile, inferred `u_star`, coherence, and main force statistics are consistent enough to use the Python generator for future `u_star` sweeps.
- 2026-05-29: Added `tools/run_ustar_sweep.py`, prepared `output/sweeps/ustar_baseline_scan` for `u_star = 0.60, 0.80, 1.00, 1.20, 1.50, 2.00`, and added `galloping_assessment` to `tools/dynamic_response_audit.py`.
- 2026-05-29: Read user-provided Week 7 galloping lecture notes. Corrected Den Hartog derivative units in `Damping_shifter.tcl`, added `xi_structural` to generated damping parameters, added `tools/galloping_criterion_audit.py`, and refined galloping critical conditions into aerodynamic susceptibility, effective negative damping, sustained response growth, and separate engineering limit states.
- 2026-05-29: Reran `config/timur_dynamic_short.yaml` with corrected damping. The short case now shows sustained negative effective damping (`negative_fraction ~= 0.24`, `min_xi ~= -0.255`) and is flagged as a galloping candidate, but not confirmed because response-envelope growth is not sustained within 51.2 s.
- 2026-05-29: Added isolated output-directory routing and longer corrected-damping tests. The 2048-step run completed and confirmed sustained negative damping plus early-to-late response growth. Longer 3072/4096-step exploratory runs entered large nonlinear response and failed to converge around 150-160 s, supporting that the corrected mechanism can drive severe instability in the current baseline.
- 2026-06-02: Added `GALLOPING_CRITERIA.md` with a parallel time-resolved criteria set C0-C8. The criteria intentionally remain separate so future sweeps can compare each criterion's coverage and critical boundary.
- 2026-06-02: Expanded `GALLOPING_CRITERIA.md` with selection reasons, literature/standard references, criteria check conclusion, workflow validation sequence, and a staged initial `u_star` sweep plan.
- 2026-06-02: Added `GEOMETRY_BASELINE.md` and `USTAR_RANGE_UK.md`; confirmed the first batch should use `L = 322.8 m`, `H = 10.48 m`, and a UK-informed staged `u_star` range beginning with `0.20-0.60`.

## Geometry Baseline And L-H Relation

Updated on 2026-06-02:

- Added `GEOMETRY_BASELINE.md`.
- Main conclusion: European overhead-line standards and design guidance do not prescribe a single universal `H = f(L)` relation. Sag is obtained from sag-tension calculation and then checked against clearance, tension, wind/ice, and tower/route constraints.
- Public design evidence:
  - National Grid RICA uses sag in midspan clearance checks and gives example Curlew conductor sag/span pairs:
    - `300 m -> 7.2 m`, ratio `0.024`;
    - `500 m -> 18.0 m`, ratio `0.036`.
  - RICA records example maximum single span lengths:
    - L3 275 kV: `537 m`;
    - L66 275 kV: `457 m`.
  - A public European multi-voltage HVAC study reports nominal/rated spans of about `450 m` for Polish 400/220 kV lines and about `300 m` for 110 kV lines.
- Current project baseline:
  - `L = 322.8 m`;
  - `H/Sag = 10.48 m`;
  - `H/L = 0.0325`;
  - Zebra self-weight `w = 15.90 N/m`;
  - RTS `131.9 kN`;
  - pretension `T0 = 0.15 RTS = 19.785 kN`.
- The current baseline sag follows the shallow parabolic sag-tension approximation:

```text
H(L) ~= w * L^2 / (8 * T0)
H(322.8) ~= 15.90 * 322.8^2 / (8 * 19785) = 10.47 m ~= 10.48 m
```

- Decision before the first `u_star` search:
  - keep the existing calibrated typical case `L = 322.8 m`, `H = 10.48 m`.
- First L sweep recommendation:

```text
L = 250, 300, 322.8, 350, 400, 450, 500 m
H_primary(L) = 15.90 * L^2 / (8 * 19785)
```

- Secondary sag sensitivity bands after the primary sweep:

```text
H/L = 0.024, 0.0325, 0.036
```

## UK-Informed u_star Range

Updated on 2026-06-02:

- Added `USTAR_RANGE_UK.md`.
- The current generator uses:

```text
U(z) = u_star / 0.387 * log(z / 0.05)
```

- At 10 m open-country height:

```text
U10 = 13.691 * u_star
u_star = 0.07304 * U10
```

- At the current conductor heights, the validated `FORCE_3/SIM1` case gives:

```text
u_star = 0.600 m/s -> mean conductor wind ~= 10.45 m/s
mean conductor wind ~= 17.42 * u_star
```

- UK/RICA/Eurocode interpretation:
  - ordinary UK 10 m climatic means support roughly `u_star ~= 0.22-0.58`;
  - RICA galloping context `5-15 m/s` maps at conductor height to about `u_star ~= 0.29-0.86`;
  - UK Eurocode-style 10 m basic wind speeds around `22-32 m/s` map to about `u_star ~= 1.61-2.34`.
- First staged sweep for `L = 322.8 m`, `H = 10.48 m`:

```text
Stage 1: 0.20, 0.30, 0.40, 0.50, 0.60
Stage 2: 0.70, 0.80, 0.90
Stage 3: 1.00, 1.20
Stage 4: 1.50, 2.00, 2.35
```

- Refinement rule near first trigger:

```text
step = 0.025 to 0.05 in u_star
```

## Stage 1 u_star Sweep Result

Updated on 2026-06-02:

- Baseline geometry was rechecked with `L = 322.8 m`, `H/Sag = 10.48 m`.
- Static/model audit output:
  - `output/model_audit/timur_baseline_recheck/model_sanity_audit.md`;
  - exact catenary fit, 101 nodes / 100 elements;
  - first frequency `0.171003521 Hz`;
  - self-weight `15.90 N/m`.
- Wind audit output:
  - `output/wind_audit/timur_baseline_recheck/dynamic_wind_audit.md`;
  - generated/validated wind record has `dt = 0.05 s`, `npt = 65536`;
  - inferred `u_star ~= 0.600`;
  - mean conductor-height wind `~= 10.45 m/s`;
  - H-drag correlations with `wind_H^2` are about `0.989-0.992`.
- Den Hartog criterion audit output:
  - `output/galloping_criterion/timur_dynamic_short_recheck/galloping_criterion_audit.md`;
  - corrected derivative uses radians, not degrees;
  - corrected negative Den Hartog fraction about `0.567`, smoothed fraction about `0.640`.
- Stage 1 sweep executed:
  - summary: `output/response_audit/ustar_stage1_uk_l322_h1048_n2048/stage1_summary.md`;
  - manifest: `output/sweeps/manifest.json`;
  - configs: `output/sweeps/configs/ustar_0P20.yaml` through `ustar_0P60.yaml`;
  - run outputs: `output/sweeps/runs/ustar_0P20` through `ustar_0P60`.
- Stage 1 settings:

```text
u_star = 0.20, 0.30, 0.40, 0.50, 0.60
npt = 2048
dt = 0.05 s
duration = 102.4 s
seed_base = 20260602
```

- Stage 1 response-audit result:

```text
u_star  max_disp_m  max_reaction_kN  neg_damping_fraction  current_C2+C4_confirmed
0.20    0.167       20.09            0.163                  no
0.30    0.480       20.24            0.245                  no
0.40    1.440       21.74            0.105                  yes
0.50    1.793       22.57            0.233                  yes
0.60    2.991       24.93            0.288                  no, mid-window peak then decay
```

- Interpretation:
  - C2 negative effective damping appears even at low `u_star`, so it remains an early susceptibility screen.
  - The first short-run confirmed C2+C4 response bracket is between `u_star = 0.30` and `0.40`.
  - `u_star = 0.60` has the largest displacement and strongest negative damping, but its late-window envelope decays after a middle-window peak; it must be checked with longer time histories and/or repeated seeds.
- Next local refinement:

```text
u_star = 0.325, 0.350, 0.375, 0.400
```

## Stage 1 Local Refinement Result

Updated on 2026-06-02:

- Refinement summary:
  - `output/response_audit/ustar_refine1_uk_l322_h1048_n2048/refine1_summary.md`.
- Sweep manifest:
  - `output/sweeps/ustar_refine1_uk_l322_h1048_n2048/manifest.json`.
- Refinement settings:

```text
u_star = 0.325, 0.350, 0.375, 0.400
npt = 2048
dt = 0.05 s
duration = 102.4 s
seed_base = 20260620
```

- Refinement response-audit result:

```text
u_star  max_disp_m  max_reaction_kN  neg_damping_fraction  current_C2+C4_confirmed
0.325   0.517       20.29            0.113                  no, near threshold
0.350   0.632       20.53            0.102                  no
0.375   0.823       20.70            0.237                  no
0.400   1.440       21.74            0.105                  yes
```

- Strict short-run C2+C4 refinement bracket:

```text
0.375 < u_star_crit <= 0.400
```

- Important workflow note:
  - `tools/run_ustar_sweep.py` names generated force/wind cases by `u_star` and `npt`, not by seed.
  - If an existing force case has the same `u_star`, the generator reuses it by default even if a new seed is requested.
  - For repeated-seed studies, add a seed/realization tag to `force_name` and `wind_dir`, or intentionally set overwrite behavior.
- Tool update after this finding:
  - `tools/run_ustar_sweep.py` now supports `--label-precision` and `--include-seed-in-name`.
  - Use `--label-precision 3` for refinement points such as `0.325`.
  - Use `--include-seed-in-name` for repeated-realization studies so configs, force dirs, wind dirs, and output dirs include the seed.
  - Dry-run verification output:
    - `output/sweeps/dryrun_seed_names/manifest.json`.

## Key u_star Long-Record Verification

Updated on 2026-06-02:

- Long-record summary:
  - `output/response_audit/ustar_key_long1_uk_l322_h1048_n4096/key_long1_summary.md`.
- Sweep manifest:
  - `output/sweeps/ustar_key_long1_uk_l322_h1048_n4096/manifest.json`.
- Settings:

```text
u_star = 0.350, 0.375, 0.400
npt = 4096
dt = 0.05 s
duration = 204.8 s
seed_base = 20260700
seed-aware naming = true
```

- Response-audit result:

```text
u_star  seed      max_disp_m  max_reaction_kN  neg_damping_fraction  current_C2+C4_confirmed
0.350   20260700  0.820       20.96            0.214                  no
0.375   20260701  0.874       21.08            0.414                  no
0.400   20260702  1.392       22.22            0.112                  yes
```

- Current strict long-record bracket:

```text
0.375 < u_star_crit <= 0.400
```

- Interpretation:
  - `0.350` and `0.375` satisfy C2 sustained negative effective damping but not C4 response growth.
  - `0.400` satisfies both C2 and C4.
  - The longer record confirms that C2 alone is not a sufficient onset definition for the present workflow.

- Next recommended verification:

```text
Repeated realizations: u_star = 0.375, 0.400, npt = 4096
Bracket refinement after repeated-realization check: u_star = 0.385, 0.390, 0.395
Final long records: u_star = 0.375, 0.390, 0.400, npt = 65536
```

## Key u_star Repeated-Seed Verification

Updated on 2026-06-02:

- Repeated-seed summary:
  - `output/response_audit/ustar_key_repeat1_uk_l322_h1048_n4096/repeat1_summary.md`.
- Sweep manifest:
  - `output/sweeps/ustar_key_repeat1_uk_l322_h1048_n4096/manifest.json`.
- Settings:

```text
u_star = 0.375, 0.400
npt = 4096
dt = 0.05 s
duration = 204.8 s
seed_base = 20260720
seed-aware naming = true
```

- Repeated-seed response-audit result:

```text
u_star  seed      max_disp_m  max_reaction_kN  neg_damping_fraction  current_C2+C4_confirmed
0.375   20260720  1.272       21.21            0.192                  no
0.400   20260721  0.922       22.26            0.380                  no
```

- Combined `4096`-step evidence:

```text
u_star  tested_seeds          C2_positive_count  C4_confirmed_count
0.350   20260700              1/1                0/1
0.375   20260701,20260720     2/2                0/2
0.400   20260702,20260721     2/2                1/2
```

- Updated boundary interpretation:
  - C2 sustained negative effective damping is robust across all key `4096`-step runs.
  - C4 response-growth confirmation is sensitive to turbulent realization and time-window phasing near `u_star = 0.400`.
  - Treat `u_star = 0.375-0.400` as an early observed transition band in one part
    of the curve, not as the main research target.
  - Future boundary extraction should estimate coverage trends across a wider
    `u_star` range before selecting iso-coverage thresholds.

## Window-Occupancy Galloping Metrics

Updated on 2026-06-02:

- Added window audit tool:
  - `tools/window_criteria_audit.py`.
- First key-case window summary:
  - `output/window_criteria_audit/key_4096_window_summary.md`.
- Default windowing:

```text
window = 20 s
step = 10 s
n_windows = 19 for a 204.8 s record
```

- First occupancy results:

```text
case                         C2       C4       C6       C7       C2&C4
0P350_SEED20260700           1.000    0.158    0.000    1.000    0.158
0P375_SEED20260701           1.000    0.000    0.000    1.000    0.000
0P400_SEED20260702           1.000    0.105    0.105    1.000    0.105
0P375_SEED20260720           1.000    0.105    0.211    1.000    0.105
0P400_SEED20260721           1.000    0.158    0.000    1.000    0.158
```

- Interpretation:
  - Whole-record classification and window occupancy are complementary.
  - C2 is active in every tested key-case window, so it is a susceptibility
    screen, not an occurrence probability by itself.
  - C4/C2&C4 window fractions around `0.000-0.158` show that near-boundary
    galloping-compatible behavior appears intermittently.
  - C7 currently triggers in every window, so the clearance proxy must be
    recalibrated before being used as a physical failure probability.
  - Future boundary extraction should report both binary whole-record onset and
    occupancy thresholds such as `C2C4_window_fraction >= 0.05, 0.10, 0.20`.

## Time-Step Coverage Limits

Updated on 2026-06-02:

- Added time-step coverage audit tool:
  - `tools/time_step_coverage_audit.py`.
- First key-case time-step summary:
  - `output/time_step_coverage_audit/key_4096_time_step_summary.md`.
- Time-step definition:

```text
dt = 0.05 s
coverage_fraction = problem_time_steps / total_time_steps
problem_time_s = problem_time_steps * dt
```

- Current time-step coverage results:

```text
case                         C2        C4        C6        C7        C2&C4     longest C2&C4
0P350_SEED20260700           0.0498    0.2068    0.0000    0.9849    0.0103    0.05 s
0P375_SEED20260701           0.0498    0.0000    0.0000    0.9851    0.0000    0.00 s
0P400_SEED20260702           0.0491    0.1748    0.0142    0.9905    0.0085    0.05 s
0P375_SEED20260720           0.0498    0.1538    0.0305    0.9907    0.0078    0.05 s
0P400_SEED20260721           0.0498    0.2236    0.0000    0.9912    0.0110    0.05 s
```

- Updated workflow decision:
  - time-step coverage is now the primary limit format;
  - window occupancy is retained as an interpretive/smoothing layer;
  - whole-record binary criteria are retained only as secondary summaries;
  - candidate occurrence thresholds for C2&C4 coverage: `0.005`, `0.010`, `0.020`.
  - critical thresholds are now post-processed iso-coverage levels, not the
    first-stage sampling goal.

## L-u_star Grid Workflow Pilot

Updated on 2026-06-02:

- Added L-u_star grid tool:
  - `tools/run_l_ustar_sweep.py`.
- Dry-run validation:
  - `output/sweeps/dryrun_l_ustar_grid_v2/manifest.json`.
- Pilot executed grid:
  - sweep manifest: `output/sweeps/pilot_l_ustar_grid_n1024/manifest.json`;
  - coverage summary: `output/time_step_coverage_audit/pilot_l_ustar_grid_n1024/pilot_l_ustar_grid_summary.md`.
- Pilot settings:

```text
L = 300.0, 322.8 m
u_star = 0.375, 0.400
npt = 1024
dt = 0.05 s
duration = 51.2 s
sag_mode = baseline_parabolic
H(L) = 10.48 * (L / 322.8)^2
```

- Pilot result:
  - all four OpenSees cases completed;
  - all four time-step coverage audits completed;
  - this validates the L-u_star workflow but is too short for final boundary conclusions.
- Next production grid:

```text
L = 300, 322.8, 350 m
u_star = 0.375, 0.400
npt = 4096
```

Then expand to:

```text
L = 250, 300, 322.8, 350, 400, 450, 500 m
u_star local range = 0.35 to 0.45
```

## Fixed-L Broad u_star Coverage Sweep Plan

Updated on 2026-06-02:

- User corrected the research direction after adopting coverage metrics:
  - with coverage as the primary output, the goal is the trend/function
    `coverage(u_star)` rather than only a critical interval.
  - different criteria may have different trends, so the first sweep should be
    broader and coarser.
- Fixed geometry for next sweep:

```text
L = 322.8 m
H = 10.48 m
npt = 4096
dt = 0.05 s
duration = 204.8 s
```

- Recommended first broad sweep:

```text
u_star = 0.20, 0.30, 0.40, 0.50, 0.60, 0.80, 1.00, 1.20
seeds_per_u_star = 2
n_cases = 16
```

- Optional high/stress extension after reviewing first curves:

```text
u_star = 1.50, 2.00, 2.35
seeds_per_u_star = 1 or 2
```

- Primary result:

```text
coverage_C2(u_star)
coverage_C4(u_star)
coverage_C6(u_star)
coverage_C7(u_star)
coverage_C2C4(u_star)
```

- Refine only after the broad sweep, in areas where curves are steep,
  non-monotonic, or cross `p = 0.005/0.010/0.020`.

## Fixed-L Broad u_star Coverage Sweep Result

Updated on 2026-06-02:

- Executed the approved fixed-geometry broad sweep:

```text
L = 322.8 m
H = 10.48 m
u_star = 0.20, 0.30, 0.40, 0.50, 0.60, 0.80, 1.00, 1.20
npt = 4096
dt = 0.05 s
target duration = 204.8 s
```

- Output locations:

```text
initial sweep outputs: output/sweeps/fixedL322_broad_ustar_n4096_s2/
continuation outputs: output/sweeps/fixedL322_broad_ustar_n4096_s2_cont/
case audits: output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/cases/
summary table: output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/ustar_coverage_summary.md
case CSV: output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/case_coverage.csv
summary CSV: output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/ustar_coverage_summary.csv
core curve: output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/coverage_curves_core.svg
all-criteria curve: output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/coverage_curves_all.svg
failed cases: output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/failed_cases.csv
```

- Successful/non-normal cases:
  - 15 completed cases entered coverage averaging.
  - 2 non-normal cases were recorded separately:
    - `L322P8_U0P500_SEED20260906`;
    - `L322P8_U1P200_SEED20260916`.
- Important audit correction:
  - high `u_star` cases can produce more than 4096 rows in `Dynamic.out` because the nonlinear solution writes adaptive substep records;
  - final coverage curves therefore use `tools/time_step_coverage_audit.py --max-records 4096`;
  - raw row counts remain recorded in each case audit as a numerical-severity indicator.

Final mean time-step coverage values:

```text
u_star  C2&C4   C2 neg damping  C4 growth  C6 large response  C7 clearance proxy
0.20    0.0020  0.0498          0.0361     0.0000             0.9788
0.30    0.0095  0.0498          0.1892     0.0000             0.9940
0.40    0.0022  0.0487          0.0602     0.0001             0.9960
0.50    0.0103  0.0425          0.3136     0.2222             0.9944
0.60    0.0057  0.0342          0.2587     0.6337             0.9985
0.80    0.0070  0.0171          0.3678     0.8621             0.9996
1.00    0.0025  0.0130          0.3438     0.8910             0.9995
1.20    0.0000  0.0056          0.1013     0.9858             0.9998
```

Current interpretation:

- C6 large-response coverage rises sharply after `u_star ~= 0.50`, indicating a developed large-amplitude response regime.
- C4 response-growth coverage is stochastic/non-monotonic but generally elevated from `u_star ~= 0.50` through `1.00`.
- C2 negative-damping coverage decreases with larger response in this batch, likely because once the conductor enters a large-motion regime, instantaneous aerodynamic state spends less time in the small-angle negative-damping condition.
- C2&C4 remains small and non-monotonic; it is conservative and should be treated as a strict simultaneous-mechanism marker rather than the only galloping indicator.
- C7 is still a placeholder clearance proxy and should not be used as a calibrated galloping decision criterion.

## Fixed-L Key u_star Extra Seeds And Uncertainty Bands

Updated on 2026-06-03:

- Added five additional seeds at each key wind intensity:

```text
u_star = 0.50, 0.60, 0.80, 1.00
seeds = 20261000 to 20261019
L = 322.8 m
H = 10.48 m
npt = 4096
dt = 0.05 s
```

- New sweep output:

```text
output/sweeps/fixedL322_key_ustar_extra_seeds_n4096_s5/
```

- These new samples were audited into the existing fixed-L result set:

```text
output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/cases/
```

- Aggregated result files were regenerated:

```text
summary markdown: output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/ustar_coverage_summary.md
summary CSV: output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/ustar_coverage_summary.csv
case CSV: output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/case_coverage.csv
core uncertainty curve: output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/coverage_curves_core.svg
all-criteria uncertainty curve: output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/coverage_curves_all.svg
failed cases: output/time_step_coverage_audit/fixedL322_broad_ustar_n4096_s2/failed_cases.csv
```

- `tools/aggregate_time_step_coverage.py` now computes:
  - mean coverage;
  - standard deviation;
  - standard error of the mean;
  - approximate 95% confidence intervals;
  - SVG curve error bars when Matplotlib is unavailable.

Final combined sample counts:

```text
u_star  completed  failed/non-normal
0.20    2          0
0.30    2          0
0.40    2          0
0.50    5          3
0.60    6          1
0.80    7          0
1.00    6          1
1.20    1          1
```

Core criteria with approximate 95% CI:

```text
u_star  C2&C4 mean [95% CI]     C4 mean [95% CI]       C6 mean [95% CI]
0.20    0.0020 [0.0000,0.0058]  0.0361 [0.0000,0.1070] 0.0000 [0.0000,0.0000]
0.30    0.0095 [0.0047,0.0143]  0.1892 [0.0906,0.2878] 0.0000 [0.0000,0.0000]
0.40    0.0022 [0.0000,0.0065]  0.0602 [0.0049,0.1154] 0.0001 [0.0000,0.0004]
0.50    0.0065 [0.0020,0.0109]  0.2803 [0.2021,0.3586] 0.3461 [0.1951,0.4970]
0.60    0.0026 [0.0002,0.0050]  0.2343 [0.1613,0.3072] 0.6222 [0.5589,0.6855]
0.80    0.0039 [0.0019,0.0059]  0.3059 [0.2463,0.3655] 0.8423 [0.8120,0.8726]
1.00    0.0008 [0.0000,0.0019]  0.1992 [0.0792,0.3193] 0.8891 [0.8092,0.9689]
1.20    0.0000 [0.0000,0.0000]  0.1013 [0.1013,0.1013] 0.9858 [0.9858,0.9858]
```

Updated interpretation:

- C6 is now clearly monotonic over the key range and acts as the strongest
  developed-response severity metric.
- C4 remains elevated over `u_star = 0.50` to `1.00`, with stochastic variation;
  it should be reported with uncertainty bands rather than as a crisp threshold.
- C2&C4 stays small and non-monotonic, so it is best treated as a conservative
  simultaneous-mechanism marker.
- The `u_star = 0.50` region has both high C4/C6 variability and multiple
  non-normal runs, making it an important transition/stability band.
- Next expansion to multiple `L` should use at least 3 seeds per key point and
  preserve failed-case counts as a separate outcome.

## Bilingual Fixed-L Coverage Report

Updated on 2026-06-03:

- Created a Chinese/English bilingual Word report for the fixed-span time-domain
  coverage study.
- Report builder:

```text
tools/build_bilingual_galloping_report.py
```

- Final DOCX:

```text
output/reports/galloping_fixedL322_bilingual/Galloping_FixedL322_TimeDomain_Coverage_Report_Bilingual.docx
```

- Generated chart asset:

```text
output/reports/galloping_fixedL322_bilingual/core_criteria_uncertainty.png
```

- Report contents:
  - study setup;
  - bilingual C2/C4/C6/C2&C4 definitions;
  - mean coverage table;
  - uncertainty-band table;
  - C2&C4/C4/C6 curve with approximate 95% CI;
  - failed/non-normal sample table;
  - current conclusions and next L-expansion plan.
- Visual render QA note:
  - the bundled render workflow could not run because LibreOffice/`soffice` is
    not installed in the current environment;
  - structural DOCX QA passed: 53 paragraphs, 8 headings, 3 tables, 1 embedded
    PNG image, and expected table dimensions.

## Multi-Span L-u_star Sweep: L = 300, 350, 400 m

Updated on 2026-06-03:

- Executed the requested multi-span sweep:

```text
L = 300, 350, 400 m
u_star = 0.30, 0.40, 0.50, 0.60, 0.80, 1.00
seeds_per_point = 3
npt = 4096
dt = 0.05 s
target duration = 204.8 s
```

- Sag/downward height rule:

```text
sag_mode = parabolic_tension
H(L) = w L^2 / (8 T0)
w = 15.90 N/m
T0 = 19.785 kN
```

- Matched sag values:

```text
L = 300 m -> H = 9.0409 m
L = 350 m -> H = 12.3057 m
L = 400 m -> H = 16.0728 m
```

- Sweep outputs:

```text
output/sweeps/L300_ustar_grid_n4096_s3/
output/sweeps/L350_ustar_grid_n4096_s3/
output/sweeps/L400_ustar_grid_n4096_s3/
```

- Post-processing outputs:

```text
output/time_step_coverage_audit/L300_350_400_ustar_grid_n4096_s3/l_ustar_coverage_summary.md
output/time_step_coverage_audit/L300_350_400_ustar_grid_n4096_s3/l_ustar_coverage_summary.csv
output/time_step_coverage_audit/L300_350_400_ustar_grid_n4096_s3/case_coverage.csv
output/time_step_coverage_audit/L300_350_400_ustar_grid_n4096_s3/failed_cases.csv
output/time_step_coverage_audit/L300_350_400_ustar_grid_n4096_s3/C2_coverage_by_L.svg
output/time_step_coverage_audit/L300_350_400_ustar_grid_n4096_s3/C4_coverage_by_L.svg
output/time_step_coverage_audit/L300_350_400_ustar_grid_n4096_s3/C6_coverage_by_L.svg
output/time_step_coverage_audit/L300_350_400_ustar_grid_n4096_s3/C2C4_coverage_by_L.svg
output/time_step_coverage_audit/L300_350_400_ustar_grid_n4096_s3/failed_fraction_by_L.svg
```

- New aggregation tool:

```text
tools/aggregate_l_ustar_coverage.py
```

- Completion counts:

```text
L = 300 m: 15 completed, 3 failed/non-normal
L = 350 m: 12 completed, 6 failed/non-normal
L = 400 m: 14 completed, 4 failed/non-normal
Total: 41 completed, 13 failed/non-normal, 54 planned
```

- Key result pattern:
  - C6 large-response coverage increases strongly with `u_star` for all three
    spans and reaches high values at `u_star >= 0.80`.
  - C4 response-growth coverage is non-monotonic but remains useful as a
    seed-sensitive process indicator.
  - C2 negative-damping coverage tends to be highest at low `u_star` and lower
    in developed large-response regimes.
  - C2&C4 remains small and conservative.
  - Failed/non-normal cases are already significant from `u_star = 0.50-0.80`,
    especially for longer spans, and should be treated as an auxiliary
    instability curve rather than discarded.

## Multi-Span Failed-Case Reason Audit

Updated on 2026-06-03:

- Audited the 13 failed/non-normal cases from the multi-span sweep.
- Compact audit file:

```text
output/time_step_coverage_audit/L300_350_400_ustar_grid_n4096_s3/failed_reason_audit.csv
```

- Main finding:
  - The failed cases are not force-generation or missing-input failures.
  - Each failed case entered the OpenSees transient analysis and wrote recorder
    outputs (`Dynamic.out`, `Static.out`, `Reaction.out`,
    `damping_change_log.txt`).
  - The common signature is a non-normal OpenSees termination during strong
    nonlinear dynamic response: `Dynamic.out` ends with an incomplete row
    (`last_cols < 304`) and no `*_MAX_DISP.csv` / `*_MAX_REAC.csv` /
    `*_MAX_CLEARANCE.csv` post-run summaries are produced.

- Physical/numerical interpretation:
  - These cases should be classified as coupled instability/non-convergence
    events rather than discarded preprocessing errors.
  - They generally show substantial negative aerodynamic damping before
    termination; negative-damping fractions range from about 0.296 to 0.826
    across the failed set, with minimum logged effective damping ratios reaching
    about `-1.55`.
  - Failure-prone cells are:

```text
L=300 m: u_star=0.60 (1/3), 0.80 (2/3)
L=350 m: u_star=0.50 (1/3), 0.60 (1/3), 0.80 (2/3), 1.00 (2/3)
L=400 m: u_star=0.50 (2/3), 0.80 (2/3)
```

- Reporting rule:
  - Keep completed cases for C2/C4/C6/C2&C4 coverage statistics.
  - Report failed/non-normal fraction as a separate auxiliary instability
    surface:

```text
failed_fraction(L, u_star)
```

## Multi-Span Supplementary Cases And Result Package

Updated on 2026-06-03:

- Added supplementary seeds at high-failure / low-completed grid cells:

```text
L=300 m, u_star=0.80: +2 seeds
L=350 m, u_star=0.80: +2 seeds
L=350 m, u_star=1.00: +2 seeds
L=400 m, u_star=0.50: +2 seeds
L=400 m, u_star=0.80: +2 seeds
```

- Supplementary sweep manifests:

```text
output/sweeps/L300_extra_highfail_n4096_s2/manifest.json
output/sweeps/L350_extra_highfail_n4096_s4/manifest.json
output/sweeps/L400_extra_highfail_n4096_s4/manifest.json
```

- Combined original + supplementary dataset:

```text
64 planned cases
48 completed cases
16 failed/non-normal cases
```

- Combined audit and aggregation root:

```text
output/time_step_coverage_audit/L300_350_400_ustar_grid_n4096_s3_plus_extra/
```

- The supplementary cases confirmed that several high-risk cells still have a
  high non-normal termination fraction after adding seeds:

```text
L=300, u_star=0.80: completed/planned = 2/5, failed_fraction = 60%
L=350, u_star=0.80: completed/planned = 2/5, failed_fraction = 60%
L=350, u_star=1.00: completed/planned = 2/5, failed_fraction = 60%
L=400, u_star=0.50: completed/planned = 3/5, failed_fraction = 40%
L=400, u_star=0.80: completed/planned = 3/5, failed_fraction = 40%
```

- New result packaging tool:

```text
tools/build_l_ustar_result_package.py
```

- Result package outputs:

```text
output/time_step_coverage_audit/L300_350_400_ustar_grid_n4096_s3_plus_extra/result_package/
```

- Important files in the package:

```text
coverage_big_table_by_geometry.xlsx
coverage_big_table_source.csv
geometry_reliability_summary.csv
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

## Multi-Span Research Report

Updated on 2026-06-04:

- Added a formal multi-span research report based on the latest `plus_extra`
  result package.
- Report generator:

```text
tools/build_multispan_galloping_report.py
```

- Report output:

```text
output/reports/galloping_multispan_plus_extra/Galloping_Multispan_TimeDomain_Coverage_Report.docx
```

- Report structure:
  - research framework and methodology;
  - criteria design and interpretation;
  - experiment matrix and data reliability;
  - coverage results;
  - separate 2D surfaces for C6, C4, C2, C2&C4, failed fraction, and C7;
  - interpretation, limitations, and next-step recommendations.

- Important report cautions:
  - C6 is presented as the clearest current developed-response surface.
  - C4 is retained as a stochastic response-growth process indicator.
  - C2 is interpreted as a mechanism/effective-damping indicator, not a
    monotonic severity curve.
  - C2&C4 is interpreted as a strict conservative simultaneous marker.
  - C7 is explicitly marked as uncalibrated and excluded from primary
    galloping conclusions until the engineering clearance/limit-state threshold
    is recalibrated.
  - Failed/non-normal cases are retained as `failed_fraction(L, u_star)`.

- QA status:
  - Structural DOCX QA passed: 47 paragraphs, 8 main headings, 6 tables,
    2 sections, and 7 embedded PNG images.
  - Render QA with `render_docx.py` could not be completed because
    LibreOffice/`soffice` was not available in the current runtime.

## Meeting Presentation Materials

Updated on 2026-06-09:

- Added a meeting slide deck focused on:
  - research framework;
  - end-to-end workflow;
  - time-domain limits/criteria design;
  - rationale for separating mechanism, response, and engineering consequence;
  - literature and standard basis for each limit;
  - current multi-span coverage results and next steps.

- Deck generator:

```text
tools/build_meeting_deck.js
```

- Final meeting deliverables:

```text
output/reports/galloping_meeting_deck/Galloping_Research_Framework_Workflow_Limits_Meeting.pptx
output/reports/galloping_meeting_deck/Galloping_Research_Framework_Workflow_Limits_Speaker_Notes.md
```

- Slide structure:
  - 15 slides total.
  - Slides 1-6: objective, research question, framework, model setup, workflow.
  - Slides 7-9: limits design principle, current time-domain limits, and
    literature/standard evidence.
  - Slides 10-13: experiment matrix, coverage table, C6/C4 surfaces, C2/C2&C4
    and failed-fraction surfaces.
  - Slides 14-15: next steps and traceability.

- QA status:
  - PPTX structural QA passed: 15 slide XML parts, 7 embedded media files,
    presentation XML present.
  - Speaker-notes Markdown contains 15 slide notes.
  - Full visual render QA was not performed in the current runtime.

## Single-Point Monitoring Demonstration

Updated on 2026-06-09:

- Added a display-oriented single-point monitoring workflow while retaining the
  existing production limits as full-line time-domain criteria.
- Baseline demonstration case:

```text
L = 322.8 m
H/Sag = 10.48 m
u_star = 0.60 m/s
seed = 20260909
dt = 0.05 s
records used = 4096
duration = 204.8 s
```

- Observation points:

```text
1/4 span  -> node 26, adjacent elements 25 and 26
Midspan   -> node 51, adjacent elements 50 and 51
3/4 span  -> node 76, adjacent elements 75 and 76
```

- Direction convention for this demonstration:
  - plotted `x` displacement is the aerodynamic horizontal wind-vibration
    direction used by the wind and damping routines, corresponding to OpenSees
    DOF 2 in the current span-aligned model;
  - plotted `z` displacement corresponds to OpenSees DOF 3;
  - OpenSees DOF 1 is the spanwise coordinate and is not used as the displayed
    aerodynamic `x` direction.

- New result builder:

```text
tools/build_single_point_demo_package.py
```

- Result package:

```text
output/single_point_demo/L322P8_U0P600_SEED20260909/
```

- Key outputs:

```text
single_point_demo_tables.xlsx
single_point_summary.csv
single_point_displacement_timeseries.csv
single_point_aero_coeff_timeseries.csv
single_point_damping_timeseries.csv
monitor_points_geometry.png
displacement_x_timeseries.png
displacement_z_timeseries.png
cd_timeseries.png
cl_timeseries.png
damping_timeseries.png
single_point_demo_metadata.json
```

- Interpretation note:
  - the single-point plots are for presentation, diagnosis, and mechanism
    explanation;
  - they do not replace the production `C2`, `C4`, `C6`, `C2&C4`, `C7`, and
    failed-fraction limits, which remain full-line or all-element time-domain
    coverage criteria.

- New bilingual slide-deck builder:

```text
tools/build_single_point_demo_decks.js
```

- Final bilingual PPT deliverables:

```text
output/reports/single_point_demo_decks/Galloping_Single_Point_Demo_CN.pptx
output/reports/single_point_demo_decks/Galloping_Single_Point_Demo_EN.pptx
```

- PPT QA status:
  - each deck has 10 slides and 7 embedded media files;
  - PPTX text extraction confirmed normal Chinese and English text encoding;
  - full visual render QA was not performed in the current runtime.

- Correction after inspecting the demonstration plots:
  - `tools/build_single_point_demo_package.py` was updated so
    `negative_xi_fraction_recorded` is computed only over valid damping-log
    samples, not over missing/NaN damping times.
  - Updated recorded negative-damping fractions for the single-point demo are:

```text
1/4 span  -> 0.3506
Midspan   -> 0.3236
3/4 span  -> 0.6604
```

  - Therefore the 3/4-span point is not literally always negative; it has the
    highest negative-damping fraction among the three observed points in this
    stochastic realization.

- Additional damping-flow audit on 2026-06-09:
  - Added Den Hartog term outputs:

```text
output/single_point_demo/L322P8_U0P600_SEED20260909/den_hartog_delta_curve.png
output/single_point_demo/L322P8_U0P600_SEED20260909/den_hartog_delta_timeseries.png
output/single_point_demo/L322P8_U0P600_SEED20260909/damping_formula_flow_audit/
```

  - The audit confirms that `dC_L.txt` is consistent with a derivative per
    degree, so multiplying by `180/pi` in `Damping_shifter.tcl` is
    dimensionally correct for Den Hartog's per-radian criterion.
  - Current damping formula parameters are:

```text
MassM = 6.565677
B = 0.028620
L_e = 4.049516
rho_air = 1.2040
xi_structural = 0.010000
omegaN = 0.867627
k_per_mps = 0.00612388
```

  - Under the present aerodynamic table, `delta_D = dC_L/dalpha + C_D` is
    strongly negative over the small-angle range, with `delta_D_min = -16.585`
    and a minimum implied `U_crit` of about `0.10 m/s`. This makes C2 very
    sensitive; C2 should be interpreted as aerodynamic/effective-damping
    susceptibility and not as a standalone severity criterion.
  - Workflow issue found: existing `Dynamic.out`, `Velocity.out`, `Accel.out`,
    and `Reaction.out` records did not include an explicit `-time` column, while
    the adaptive transient solver produced more rows than the 4096 wind input
    records. Existing single-point displacement plots are therefore diagnostic
    plots with a nominal row-index time axis. Future simulations must use
    time-stamped recorders.
  - Code update: `src/cable_analyser/tcl_writer.py` now writes `-time` for
    dynamic displacement, velocity, acceleration, and reaction recorders.

## 2026-06-09 MATLAB-Python workflow validation

- Added validation orchestrator:

```text
tools/build_matlab_python_validation.py
```

- Validation output root:

```text
output/workflow_validation/matlab_python_force3_baseline/
```

- Matched case:
  - geometry `L = 322.8 m`, `H/Sag = 10.48 m`;
  - wind/force input `data/forces/FORCE_3/SIM1`;
  - `npt = 4096`, `dt = 0.05 s`;
  - monitoring nodes: Node 26 at 1/4 span, Node 51 at midspan, Node 76 at
    3/4 span.

- The MATLAB validation copy is not the untouched original script. It applies
  only parity fixes required for a fair comparison:
  - same `FORCE_3/SIM1` input files;
  - same exact catenary geometry expression as Python;
  - current corrected `Damping_shifter.tcl`, including the per-degree to
    per-radian `dC_L/dalpha` conversion;
  - explicit `-time` columns in the dynamic/reaction recorders.

- Deliverables:

```text
output/workflow_validation/matlab_python_force3_baseline/python/three_point_outputs/
output/workflow_validation/matlab_python_force3_baseline/matlab/three_point_outputs/
output/workflow_validation/matlab_python_force3_baseline/comparison/python_matlab_three_point_comparison.csv
output/workflow_validation/matlab_python_force3_baseline/comparison/workflow_validation_report.md
```

- Each side contains four-panel plots for horizontal displacement, vertical
  displacement, `C_D`, `C_L`, Den Hartog `delta_D`, effective damping, and an
  `x-z` trajectory plot for the three monitoring points.

- Run-completion result:

```text
Python: 6396 dynamic rows, 0.050-160.135 s
MATLAB: 26074 dynamic rows, 0.050-186.388 s
```

- Interpretation:
  - up to 120 s, MATLAB and Python are very close at all three monitoring
    points; displacement RMS differences are below `0.001 m`;
  - after about 140 s, the response grows rapidly and the two workflows diverge
    in the severe nonlinear/non-normal solver regime;
  - this supports that the active Python workflow is correctly matched to the
    MATLAB reference for geometry, force scaling, coefficient lookup, and
    damping mechanism in the early/moderate-response interval;
  - failed or non-normal long-response simulations must remain explicit output
    states and should be interpreted together with coverage metrics.

## 2026-06-09 broken-line minimal 3-node validation

- Added the minimal broken-line validation orchestrator:

```text
tools/build_broken_line_minimal_validation.py
```

- Validation output root:

```text
output/workflow_validation/broken_line_minimal_3node/
```

- Matched case:
  - geometry type `3`, broken-line V shape;
  - `L = 2.0 m`, `Sag = 1.0 m`, `discretisation = 1.0 m`;
  - nodes `1` and `3` have fixed translations; node `2` is the only dynamic
    response point;
  - force input `data/forces/FORCE_3/Test1`;
  - `npt = 4096`, `dt = 0.05 s`.

- MATLAB validation-copy parity fixes:
  - uses the same three-node broken-line coordinates as Python;
  - uses the same current `tcl_procedures` files, including corrected
    aerodynamic damping;
  - records `Dynamic.out`, `Velocity.out`, `Accel.out`, and `Reaction.out`
    with explicit `-time` columns.

- Deliverables:

```text
output/workflow_validation/broken_line_minimal_3node/python/minimal_outputs/
output/workflow_validation/broken_line_minimal_3node/matlab/minimal_outputs/
output/workflow_validation/broken_line_minimal_3node/comparison/python_matlab_all_record_comparison.csv
output/workflow_validation/broken_line_minimal_3node/comparison/broken_line_minimal_validation_report.md
```

- Result:

```text
Python: 4096 dynamic rows, 0.050-204.800 s
MATLAB: 4096 dynamic rows, 0.050-204.800 s
Compared record channels: 33
Maximum Python-MATLAB difference over all compared channels: 0
```

- Interpretation:
  - the minimal three-node workflow is exactly matched between Python and
    MATLAB for displacement, velocity, acceleration, support reaction, and
    aerodynamic damping log;
  - this strongly validates the core OpenSees/Tcl workflow migration when
    geometry and solver path are simple;
  - the larger-span catenary differences found previously are therefore more
    likely associated with severe nonlinear response/adaptive-solver path
    sensitivity than with a basic Python-vs-MATLAB implementation mismatch.

## 2026-06-10 meeting preparation package

- Meeting material root:

```text
output/reports/meeting_2026_06_10/
```

- Tcl model-file package:

```text
output/reports/meeting_2026_06_10/model_tcl_package/
output/reports/meeting_2026_06_10/model_tcl_package/MODEL_TCL_INDEX.md
output/reports/meeting_2026_06_10/model_tcl_package/model_tcl_manifest.csv
```

- Tcl package contents:
  - shared fixed Tcl procedures;
  - Python-generated catenary validation Tcl;
  - MATLAB-generated catenary validation Tcl;
  - Python-generated broken-line minimal Tcl;
  - MATLAB-generated broken-line minimal Tcl;
  - legacy TIMUR4 reference Tcl/MATLAB generator files.

- Meeting report and decks:

```text
output/reports/meeting_2026_06_10/Galloping_Meeting_Report_CN_2026_06_10.docx
output/reports/meeting_2026_06_10/Galloping_Meeting_CN_2026_06_10.pptx
output/reports/meeting_2026_06_10/Galloping_Meeting_EN_2026_06_10.pptx
```

- Builder scripts:

```text
tools/prepare_meeting_materials.py
tools/build_meeting_2026_06_10_report.py
tools/build_meeting_2026_06_10_decks.js
```

- Report focus:
  - detailed code workflow from YAML/config to coverage surfaces;
  - Tcl/OpenSees calculation-flow explanation;
  - monitoring-point choices and geometry alternatives;
  - time-step coverage metric;
  - limit definitions and sources for delta/negative damping, displacement
    growth, large response, and clearance/consequence;
  - single-point and multi-span/catenary results;
  - MATLAB/Python workflow validation.

- QA status:
  - Tcl package: 23 files copied, no missing files.
  - DOCX structural QA: 15 embedded media files and expected title text present.
  - PPTX structural QA: Chinese deck and English deck each contain 18 slides
    and 17 embedded media files.
  - DOCX render QA could not be completed because the local render helper could
    not find the LibreOffice/office conversion executable.

- 2026-06-10 update: added a critical-wind-speed discussion to the Word report
  and both PPT decks.
  - Code-consistent local critical relative speed:

```text
U_cr,e = 4 M_e xi omega_n / (rho B L_e |Delta_D|)
```

  - For the current single-point catenary demo:

```text
U_cr,min ~= 0.0985 m/s
equivalent u_star ~= 0.0057 m/s at the monitored conductor heights
```

  - Interpretation recorded in the materials: this very low value is a C2
    mechanism/onset threshold caused by the strongly negative current
    aerodynamic table, not the final engineering critical wind speed. Final
    `L-u_star` boundaries should still come from time-domain coverage surfaces,
    especially C4/C6/C2&C4 and failed fraction.

- 2026-06-10 update: revised the meeting materials per user direction to stop
  presenting sweep/multi-span result maps in this meeting package and focus on
  two examples:
  - Example 1: the catenary three-monitor single-case demonstration, used to
    explain displacement, `Delta_D`, effective damping, and the time-history
    meaning of each limit.
  - Example 2: the three-node broken-line minimal MATLAB/Python/OpenSees
    validation, used to prove that the core Tcl/OpenSees workflow is matched in
    the simplest dynamic model.
- The limits explanation in the report/decks was expanded from a summary table
  into a mathematical workflow:
  - per-time-step indicator: `I_i(t_k) = 1` if limit `i` is triggered;
  - coverage: `coverage_i = sum_k I_i(t_k) / N_valid`;
  - `Delta_D = C_D + dC_L/dalpha`, with `dC_L/dalpha` converted to per-radian
    units before use;
  - `C2` checks whether `xi_total = xi_structural + rho U_rel B L_e Delta_D /
    (4 M_e omega_n)` becomes negative with spatial/threshold safeguards;
  - `C4` checks rolling-window response growth using the full-line response
    envelope and p95 ratios;
  - `C6` checks developed large response using the current `0.10H` displacement
    scale;
  - `C7` is retained as the clearance/spacing engineering-consequence channel
    but remains calibration-dependent;
  - `C2&C4` is a synchronous combination rule, not a new physical model.
- Revised deliverables:

```text
output/reports/meeting_2026_06_10/Galloping_Meeting_Report_CN_2026_06_10_v2.docx
output/reports/meeting_2026_06_10/Galloping_Meeting_CN_2026_06_10.pptx
output/reports/meeting_2026_06_10/Galloping_Meeting_EN_2026_06_10.pptx
```

- QA after this revision:
  - DOCX structural QA passed for `Galloping_Meeting_Report_CN_2026_06_10_v2.docx`.
  - PPTX structural QA passed; both Chinese and English decks contain 17 slides.
  - Text extraction confirmed the decks no longer contain the sweep-result
    headings such as "Multi-Span Results" or "C6 Large-Response Coverage
    Surface".
  - DOCX render QA was attempted again but still failed because the environment
    could not find an installed office conversion executable.
  - The original Word filename was not overwritten because it was locked/open in
    Word; the updated Word report was saved as `_v2.docx`.

## 2026-06-11 OpenSees 3.8 Solver And Termination Diagnostics

- Updated the active solver path from the old `CABLE_OPENSEES3/opensees.bat`
  launcher to:

```text
D:\Pyprogramme\OpenSees3.8.0\bin\OpenSees.exe
```

- Source configs updated:
  - `config/default_config.yaml`
  - `config/smoke_config.yaml`
  - `config/timur_baseline.yaml`
  - `config/timur_dynamic_short.yaml`
  - `config/timur_dynamic_2048.yaml`
  - `config/timur_dynamic_3072.yaml`
  - `config/timur_dynamic_4096.yaml`
  - `config/timur_generated_ustar.yaml`

- Solver logging was added in `src/cable_analyser/solver.py`:
  - every OpenSees run can now write `*.stdout.log`, `*.stderr.log`, and
    `*.meta.json` under `output_dir/solver_logs/`;
  - metadata records command, working directory, OpenSees path, UTC start/finish
    timestamps, elapsed seconds, return code, and stdout/stderr tails.

- Tcl-level status logging was added in `tcl_procedures/dynamic2.tcl`:
  - success writes `analysis_status.txt` with `STATUS success`;
  - non-convergence writes `STATUS failed`, failure time, target time, progress,
    increment, `ANALYZE_RETURN_CODE`, adaptive `FACTOR`, and `MIN_FACTOR`.

- Python now checks Tcl status before post-processing in
  `src/cable_analyser/analysis.py`.
  - If `analysis_status.txt` reports `STATUS failed`, `CableAnalysis` raises a
    `RuntimeError` instead of silently treating incomplete records as a completed
    case.
  - This makes sweep `continue_on_error` handling classify such cases as failed.

- Added `tools/audit_opensees_run_status.py`.
  - It aggregates `Dynamic.out`, `Velocity.out`, `Accel.out`, `Reaction.out`,
    `Static.out`, `Element1.out`, `damping_change_log.txt`,
    `realtime_state.txt`, `analysis_status.txt`, and `solver_logs/`.
  - It writes:

```text
termination_audit/opensees_termination_audit.json
termination_audit/opensees_termination_audit.md
termination_audit/monitoring_file_summary.csv
```

- Re-ran the meeting/demo case using OpenSees 3.8.0:

```text
output/diagnostics/opensees_3p8_rerun_L322P8_U0P600_SEED20260909/
```

- Diagnostic rerun conclusion:
  - the case does not reach the requested `204.8 s` target;
  - it stops at approximately `160.439 s`, i.e. `78.34%` progress;
  - OpenSees Tcl reports `analyze failed, returned: -3 error flag`;
  - the convergence test failed after 100 iterations with current norm
    `1.18846e-06` versus tolerance `1e-06`;
  - adaptive step factor was reduced to `6.201018947437347e-7`, below the
    configured minimum `1e-06`;
  - `analysis_status.txt` records
    `MESSAGE analysis_did_not_converge_min_factor_reached`;
  - damping log at termination contains `46661` rows with
    `min_xi_total = -0.7619751964141613` and `15212` negative-xi rows.

- Main diagnostic output files:

```text
output/diagnostics/opensees_3p8_rerun_L322P8_U0P600_SEED20260909/run/analysis_status.txt
output/diagnostics/opensees_3p8_rerun_L322P8_U0P600_SEED20260909/run/solver_logs/
output/diagnostics/opensees_3p8_rerun_L322P8_U0P600_SEED20260909/run/termination_audit/opensees_termination_audit.md
output/diagnostics/opensees_3p8_rerun_L322P8_U0P600_SEED20260909/run/termination_audit/monitoring_file_summary.csv
```

## 2026-06-11 Typical Model Strong-Response Control Tests

Purpose: investigate whether the sudden strong response and OpenSees
non-convergence in the typical catenary case is caused by a model-building
omission, by the Den Hartog derivative unit conversion, by excessive negative
aerodynamic damping, or by another part of the dynamic loading/solver workflow.

Baseline case used for all controls:

```text
L = 322.8 m
H = 10.48 m
u_star = 0.6 m/s
seed = 20260909
npt = 4096
target duration = 204.8 s
OpenSees = D:\Pyprogramme\OpenSees3.8.0\bin\OpenSees.exe
```

Three diagnostic controls were generated with
`tools/prepare_strong_response_control_configs.py`:

- A: `dcl_derivative_scale = 1.0`, no per-degree to per-radian amplification.
- B: keep the per-radian derivative conversion, but cap
  `Delta_D = dC_L/dalpha + C_D` with `delta_D_min = -2.0`.
- C: disable adaptive aerodynamic damping updates entirely while retaining the
  same precomputed external wind-force histories.

Code support added for these controls:

- `src/cable_analyser/tcl_writer.py` writes aerodynamic damping control flags:
  `enable_aero_damping_update`, `dcl_derivative_scale`, `delta_D_min`, and
  `delta_D_max`.
- `tcl_procedures/Damping_shifter.tcl` applies those flags when computing
  `xi_total`; if disabled, it keeps `xi_total = xi_structural`.
- `tools/summarize_strong_response_controls.py` aggregates the three diagnostic
  runs into:

```text
output/diagnostics/strong_response_controls/control_comparison.csv
output/diagnostics/strong_response_controls/control_comparison.md
```

Control-test result:

| Case | Termination | Negative damping | Main response |
|---|---|---:|---|
| A: no dCL rad conversion | failed at `160.43890698784924 s`, `ANALYZE_RETURN_CODE = -3` | `0` rows | same as B/C |
| B: Delta_D capped at -2 | failed at `160.43890698784924 s`, `ANALYZE_RETURN_CODE = -3` | `14910` rows | same as A/C |
| C: aerodynamic damping update disabled | failed at `160.43890698784924 s`, `ANALYZE_RETURN_CODE = -3` | not logged/disabled | same as A/B |

Shared response quantities:

```text
max displacement envelope = 8.725196250032203 m
max velocity envelope     = 58.20166661240553 m/s
max acceleration envelope = 13083.61496712969 m/s^2
duplicate-time fraction   = 0.43255386500561627
max duplicate count       = 583
```

The main recorder files are byte-identical across A/B/C:

```text
Dynamic.out  SHA256 = D1536ACAF0D55BF40B2616EA89AD8796F78F38FECFAB5A96C403C238D3B12D6B
Velocity.out SHA256 = A19371F40ED921B20BF513468086790911539A83272C082079E7582F003F17CF
Accel.out    SHA256 = 67DE0D107AE693D6AD55E7C42DFBBBB1A32825B44D993AFA08A21742E10B24D6
```

Current interpretation:

- This specific strong-response/non-convergence path is not caused solely by
  the per-degree to per-radian `dC_L` scaling.
- It is also not caused solely by negative aerodynamic damping, because case A
  has no negative damping rows and case C disables aerodynamic damping update,
  yet both reproduce the same structural response and failure time.
- Because A/B/C produce byte-identical displacement, velocity, and acceleration
  histories, the next diagnostic priority is to check why the dynamic response
  is insensitive to `setElementRayleighDampingFactors` changes, and to verify
  the external wind-force histories, load-pattern application, and transient
  solver/integrator configuration.

Immediate next checks:

- Save a per-run copy of `inputs_aerodynamic_damping.tcl` for provenance.
- Run an intentionally extreme damping-control case, for example zero global
  Rayleigh damping or very high structural damping, to test whether damping can
  affect the OpenSees response at all.
- Compare force time histories around `135-160 s` and identify whether a
  coherent load burst or interpolation/indexing issue aligns with the onset.
- Check whether `setElementRayleighDampingFactors` is active for the cable
  element formulation used here, or whether the global `rayleigh` command at
  dynamic setup dominates/locks the effective damping matrix.

## 2026-06-11 Extreme Damping Verification

Purpose: directly test whether the OpenSees dynamic response changes when the
structural/global Rayleigh damping ratio is changed strongly. This follows the
A/B/C finding that aerodynamic-damping update variants produced byte-identical
main response histories.

Implementation:

- Added `tools/prepare_extreme_damping_configs.py`.
- Added `tools/summarize_extreme_damping_controls.py`.
- `src/cable_analyser/analysis.py` now archives the exact
  `inputs_aerodynamic_damping.tcl` used by each run into that run's output
  directory.

Cases:

| Case | Damping setting | Aerodynamic damping update | Result |
|---|---:|---|---|
| C baseline | `xi = 0.01` | disabled | failed at `160.439 s` |
| D0 zero damping | `xi = 0.0` | disabled | abnormal OpenSees exit at about `154.325 s`; no Tcl `analysis_status.txt` |
| D1 high damping | `xi = 0.5` | disabled | completed to `204.8 s` |

Main quantitative results:

| Case | Last time | Max disp | Max vel | Max accel | Classification |
|---|---:|---:|---:|---:|---|
| C baseline | `160.439 s` | `8.725196250032203 m` | `58.20166661240553 m/s` | `13083.61496712969 m/s^2` | `tcl_analysis_failed` |
| D0 zero damping | `154.325 s` | `7.249690747452611 m` | `42.993543704463356 m/s` | `7633.496077944889 m/s^2` | `opensees_nonzero_exit` |
| D1 high damping | `204.8 s` | `0.7846576859883805 m` | `0.728875122937592 m/s` | `8.3740262298289 m/s^2` | `completed_to_target_duration` |

The main response files are not identical across these cases:

```text
C Dynamic.out  SHA256 = D1536ACAF0D55BF40B2616EA89AD8796F78F38FECFAB5A96C403C238D3B12D6B
D0 Dynamic.out SHA256 = 10CCF438411324010598375E4F20E32F69B6647B480FC444DE678FB8050CC6CC
D1 Dynamic.out SHA256 = 3CA8D2FE84DA2A6FB7AFBE7932206FC42311883108106CE11D5D3F7CAD2B6D4C
```

Output summary files:

```text
output/diagnostics/extreme_damping_controls/extreme_damping_comparison.csv
output/diagnostics/extreme_damping_controls/extreme_damping_comparison.md
```

Interpretation:

- OpenSees does respond to structural/global Rayleigh damping changes.
- Therefore, the previous byte-identical A/B/C response histories should not be
  interpreted as "damping is ignored in general".
- A more precise interpretation is that the aerodynamic-damping update variants
  tested in A/B/C did not change the effective global response path for that
  particular case, while changing `damping.xi` directly does.
- This suggests the next model-building check should focus on how adaptive
  `setElementRayleighDampingFactors` interacts with the initial global
  `rayleigh` command and the `forceBeamColumn` element formulation. The global
  mass-proportional Rayleigh term is demonstrably active; the element-level
  adaptive update may be too small relative to it, overwritten/not assembled as
  expected, or not effective for the current element formulation/damping option.

## 2026-06-11 Damping Writeback Matrix E1-E4

Purpose: verify whether the project should use global Rayleigh damping,
element-level damping writeback, or a combination, and specifically check for
double-counting of structural damping.

Test matrix requested:

| Case | Global damping | Element damping/writeback |
|---|---|---|
| E1 | `0` | `xi_structural` |
| E2 | `xi_structural` | no writeback; record only |
| E3 | `0` | `xi_structural + xi_aero(t)` |
| E4 | `xi_structural` | `xi_aero(t)` |

Implementation changes:

- `src/cable_analyser/tcl_writer.py` now supports
  `damping.global_rayleigh_scale`; default is `1.0`, so old configs remain
  compatible.
- `src/cable_analyser/tcl_writer.py` writes
  `aerodynamic_damping.writeback_mode` into `inputs_aerodynamic_damping.tcl`.
- `tcl_procedures/Damping_shifter.tcl` now supports four modes:
  `record_only`, `structural_only`, `aero_only`, and `total`.
- `tools/prepare_damping_writeback_matrix_configs.py` generates the four E
  configurations.
- `tools/summarize_damping_writeback_matrix.py` aggregates the four results and
  hashes `Dynamic.out`, `Velocity.out`, and `Accel.out`.

Outputs:

```text
output/diagnostics/damping_writeback_matrix/manifest.yaml
output/diagnostics/damping_writeback_matrix/damping_writeback_matrix_comparison.csv
output/diagnostics/damping_writeback_matrix/damping_writeback_matrix_comparison.md
output/diagnostics/damping_writeback_matrix/runs/E1_global0_element_structural/
output/diagnostics/damping_writeback_matrix/runs/E2_global_structural_record_only/
output/diagnostics/damping_writeback_matrix/runs/E3_global0_element_total/
output/diagnostics/damping_writeback_matrix/runs/E4_global_structural_element_aero/
```

Main quantitative results:

| Case | Configuration | Termination | Last time | Max disp | Max vel | Max accel | Dynamic hash group |
|---|---|---|---:|---:|---:|---:|---|
| E1 | global `0`; element `xi_structural` | `opensees_nonzero_exit` | `154.325 s` | `7.249690747452611 m` | `42.993543704463356 m/s` | `7633.496077944889 m/s^2` | A |
| E2 | global `xi_structural`; element record only | `analysis_did_not_converge_min_factor_reached` | `160.43890698784924 s` | `8.725196250032203 m` | `58.20166661240553 m/s` | `13083.61496712969 m/s^2` | B |
| E3 | global `0`; element `xi_structural + xi_aero(t)` | `opensees_nonzero_exit` | `154.325 s` | `7.249690747452611 m` | `42.993543704463356 m/s` | `7633.496077944889 m/s^2` | A |
| E4 | global `xi_structural`; element `xi_aero(t)` | `analysis_did_not_converge_min_factor_reached` | `160.43890698784924 s` | `8.725196250032203 m` | `58.20166661240553 m/s` | `13083.61496712969 m/s^2` | B |

Key conclusion:

- E1 and E3 are byte-identical in the main structural response histories.
- E2 and E4 are byte-identical in the main structural response histories.
- Therefore, for the current OpenSees model and element formulation, the
  adaptive element-level `setElementRayleighDampingFactors` writeback does not
  measurably change the solved displacement/velocity/acceleration histories.
- The global `rayleigh` damping channel is active and controls the structural
  damping branch: global off gives the E1/E3 path; global on gives the E2/E4
  path.

Modelling decision from this verification:

- Do not use `global = xi_structural` together with `element =
  xi_structural + xi_aero(t)` as the production workflow; it is conceptually a
  double-counting risk, even though the current element writeback does not
  measurably affect the response.
- For verified structural dynamics, keep global Rayleigh damping for
  `xi_structural`.
- Until a velocity-dependent aerodynamic damping force implementation is added
  and verified, use element damping calculations as diagnostic/limit quantities
  (`xi_aero`, `xi_total`, Den Hartog `Delta_D`) rather than assuming they modify
  the OpenSees response.
- If aerodynamic damping must actively enter the time-domain equation, implement
  it as an explicit aerodynamic velocity-dependent force term in the external
  load/update logic, or replace the current damping channel with a verified
  OpenSees formulation whose element-level damping update demonstrably changes
  the response in a controlled benchmark.

Code decision applied after the E1-E4 verification:

- Default `aerodynamic_damping.writeback_mode` is now `record_only` in
  `src/cable_analyser/tcl_writer.py`.
- Fallback default inside `tcl_procedures/Damping_shifter.tcl` is now
  `record_only`.
- `config/default_config.yaml` and `config/timur_dynamic_4096.yaml` explicitly
  set `damping.global_rayleigh_scale: 1.0` and
  `aerodynamic_damping.writeback_mode: "record_only"`.
- `tests/test_tcl_writer.py` now checks that the generated
  `inputs_aerodynamic_damping.tcl` includes
  `set damping_writeback_mode "record_only"`.

Verification after code decision:

```text
python -m py_compile src/cable_analyser/tcl_writer.py tools/prepare_damping_writeback_matrix_configs.py tools/summarize_damping_writeback_matrix.py
pytest tests/test_tcl_writer.py -q
6 passed
YAML parse check passed for config/default_config.yaml and config/timur_dynamic_4096.yaml
```

## 2026-06-11 Explicit Aerodynamic Damping Force Implementation

Purpose: move aerodynamic damping from a diagnostic/limit quantity into the
actual OpenSees time-domain equation as an explicit velocity-dependent
aerodynamic force:

```text
M u_ddot + C_struct u_dot + K u = F_wind(t) + F_aero_damping(u_dot, t)
```

This follows the E1-E4 finding that element-level
`setElementRayleighDampingFactors` writeback did not measurably change the
solved structural response.

Implementation:

- `src/cable_analyser/tcl_writer.py` now writes explicit-force controls into
  `inputs_aerodynamic_damping.tcl`:
  - `enable_explicit_aero_damping_force`
  - `explicit_aero_damping_force_scale`
  - `explicit_aero_damping_force_log_stride`
- `config/default_config.yaml` and `config/timur_dynamic_4096.yaml` now include:

```yaml
aerodynamic_force:
  enabled: false
  scale: 1.0
  log_stride: 20
```

- `tcl_procedures/Damping_shifter.tcl` now defines
  `apply_explicit_aero_damping_force`, registered as a before-analyze callback
  when `aerodynamic_force.enabled` is true.
- `tcl_procedures/dynamic2.tcl` no longer overwrites a pre-registered
  `STKO_VAR_OnBeforeAnalyze_CustomFunctions` list. This was necessary because
  `Damping_shifter.tcl` is sourced before `dynamic2.tcl`.
- `tests/test_tcl_writer.py` checks that the explicit-force parameters are
  written.
- Added:

```text
tools/prepare_explicit_aero_force_validation_configs.py
tools/summarize_explicit_aero_force_validation.py
```

Mathematical form used in Tcl:

```text
Delta_D(alpha) = dC_L/dalpha + C_D
c_aero,e(t) = scale * rho_air * U_rel,e(t) * B * L_e * Delta_D(alpha) / 2
F_aero,e(t) = -c_aero,e(t) * v_cable,e(t)
```

The element force is distributed equally to the two end nodes in the lateral
`y` and vertical `z` translational DOFs. Therefore:

- If `Delta_D < 0`, then `c_aero < 0`, and
  `F_aero = -c_aero v` acts in the direction of velocity, injecting energy.
- If `Delta_D > 0`, then `c_aero > 0`, and the force opposes velocity,
  dissipating energy.

Validation matrix:

Common setting:

```text
L = 322.8 m
Sag = 10.48 m
FORCE_3 / SIM1
dt = 0.05 s
npt = 1024
target duration = 51.2 s
global structural Rayleigh damping active
element damping writeback = record_only
```

Cases:

| Case | Explicit force | Scale | Purpose |
|---|---|---:|---|
| F0 | disabled | `1.0` | baseline |
| F1 | enabled | `0.0` | null-force check |
| F2 | enabled | `1.0` | physical-scale explicit aerodynamic damping force |
| F3 | enabled | `10.0` | amplified sensitivity check only |

Validation results:

| Case | Termination | Last response time | Max abs disp | Max abs vel | Max abs acc | Max total explicit force | Dynamic hash group |
|---|---|---:|---:|---:|---:|---:|---|
| F0 | `target_time_reached` | `51.2 s` | `1.84569 m` | `2.71939 m/s` | `38.5733 m/s^2` | none | A |
| F1 | `target_time_reached` | `51.2 s` | `1.84569 m` | `2.71939 m/s` | `38.5733 m/s^2` | `0 N` | A |
| F2 | `target_time_reached` | `51.2 s` | `6.01761 m` | `8.55278 m/s` | `71.661 m/s^2` | `667.04863 N` | B |
| F3 | no `analysis_status.txt`; extreme numerical blow-up | `8.49303 s` | `5.36886e6 m` | `1.55295e14 m/s` | `4.52109e21 m/s^2` | `7.5963682e22 N` | C |

Output summary files:

```text
output/diagnostics/explicit_aero_force_validation/manifest.yaml
output/diagnostics/explicit_aero_force_validation/explicit_aero_force_validation_summary.csv
output/diagnostics/explicit_aero_force_validation/explicit_aero_force_validation_summary.md
output/diagnostics/explicit_aero_force_validation/runs/F0_record_only_no_explicit_force/
output/diagnostics/explicit_aero_force_validation/runs/F1_explicit_force_scale0/
output/diagnostics/explicit_aero_force_validation/runs/F2_explicit_force_scale1/
output/diagnostics/explicit_aero_force_validation/runs/F3_explicit_force_scale10/
```

Interpretation:

- F0 and F1 have identical main-response hash group A. Therefore merely
  registering/removing/recreating the explicit load pattern does not introduce a
  false response when the force scale is zero.
- F1 has an `explicit_aero_damping_force_log.txt` with every force value equal
  to zero, proving the callback was active while the null-force condition was
  respected.
- F2 has nonzero explicit aerodynamic damping force and a different response
  hash group B. The physical-scale explicit force therefore actively enters the
  OpenSees time-domain equation and changes the structural response.
- F3 is intentionally not a production setting. Its rapid blow-up and solver
  failure demonstrate that the explicit force channel can feed back strongly
  into the nonlinear response when scaled up.

Current modelling decision:

- Production/default configs keep `aerodynamic_force.enabled: false` until a
  research case explicitly requests active aerodynamic damping.
- For active galloping-mechanism simulations, use:

```yaml
aerodynamic_damping:
  enabled: true
  writeback_mode: "record_only"
aerodynamic_force:
  enabled: true
  scale: 1.0
```

- Do not combine active explicit aerodynamic force with element-level damping
  writeback unless a separate benchmark proves that such coupling is intended
  and not double-counting the same aerodynamic energy term.

Verification:

```text
python -m py_compile src/cable_analyser/tcl_writer.py tools/prepare_explicit_aero_force_validation_configs.py tools/summarize_explicit_aero_force_validation.py
pytest tests/test_tcl_writer.py -q
6 passed
```

## 2026-06-11 Typical Case With Active Explicit Galloping Mechanism

Purpose: apply the explicit velocity-dependent aerodynamic damping force to the
typical long dynamic case and check whether galloping appears for the research
baseline geometry.

Configuration:

```text
L = 322.8 m
Sag = 10.48 m
FORCE_3 / SIM1
dt = 0.05 s
npt = 4096
target duration = 204.8 s
global structural Rayleigh damping active
element damping writeback = record_only
explicit aerodynamic damping force = enabled, scale = 1.0
```

Generated config:

```text
output/diagnostics/typical_explicit_galloping/typical_L322P8_H10P48_U0P6_explicit_force.yaml
```

Run output:

```text
output/diagnostics/typical_explicit_galloping/run/
```

Diagnostics and analysis:

```text
output/diagnostics/typical_explicit_galloping/run/termination_audit/opensees_termination_audit.md
output/diagnostics/typical_explicit_galloping/run/strong_response_diagnosis/strong_response_diagnosis.md
output/diagnostics/typical_explicit_galloping/analysis/typical_explicit_galloping_analysis.md
output/diagnostics/typical_explicit_galloping/analysis/response_envelopes_log.png
output/diagnostics/typical_explicit_galloping/analysis/explicit_force_log.png
output/diagnostics/typical_explicit_galloping/analysis/xi_total_scatter.png
```

Result summary:

| Quantity | Value |
|---|---:|
| Last recorded time | `72.2835 s` |
| Target time | `204.8 s` |
| Completed fraction | `35.29%` |
| Max displacement envelope | about `98-99 m` |
| Max velocity envelope | about `2290-2375 m/s` |
| Max acceleration envelope | about `6.9e5-8.5e5 m/s^2` |
| Max total explicit aerodynamic damping force | `1.54e7 N` |
| Minimum logged `xi_total` | `-41.2981` |
| Negative `xi_total` fraction in damping log rows | `0.648` |
| Duplicate-time fraction | `0.895` |

Interpretation:

- The galloping mechanism is active in the typical case. Negative total
  damping appears early and persists over substantial fractions of the time
  windows.
- Response grows gradually first, then accelerates strongly:
  - `35-40 s`: p95 displacement about `3.97 m`, growth vs base about `8.06`.
  - `60-65 s`: p95 displacement about `12.34 m`, growth vs base about `25.06`.
  - `65-70 s`: p95 displacement about `20.48 m`, growth vs base about `41.57`.
  - `70-75 s`: p95 displacement about `75.08 m`, growth vs base about `152.41`;
    `xi_total` minimum reaches `-41.2981` and negative-damping fraction is
    about `0.901`.
- The explicit aerodynamic damping force is nonzero and grows with structural
  response, confirming that the galloping energy-transfer mechanism is entering
  the OpenSees time-domain equation rather than being only post-processed.
- The excessive response still appears and causes practical interruption of
  the long run. This is now interpreted as a physically/mechanistically
  triggered galloping instability under the active force model, not the earlier
  unexplained record-only/element-writeback behaviour.
- The run was externally interrupted by the 20-minute command timeout before a
  Tcl `analysis_status.txt` could be written. No residual OpenSees/Python
  process remained afterward. Because output reached only about `72.28 s`, the
  case should be treated as an incomplete-but-informative severe galloping
  event.

Workflow assessment:

- Correct for mechanism: yes. The active explicit force path is used, and
  force/response/damping logs support active galloping feedback.
- Correct for long-run completion: no. Severe galloping causes substepping and
  excessive response, preventing a clean 204.8 s completion under the current
  settings.
- Next recommended workflow improvement is to add event-based stopping and
  classification, for example stop when displacement, velocity, explicit force,
  or negative-damping severity exceeds a research-defined threshold. This
  should classify the run as galloping/failed-limit rather than waiting for
  OpenSees to become numerically impractical.

## 2026-06-11 Three-Point Monitoring For Typical Explicit Case

Purpose: monitor the 1/4-span, midspan, and 3/4-span nodes in the active
explicit-galloping typical case, including transverse/vertical displacement,
transverse/vertical velocity, x-z displacement path, aerodynamic coefficients,
Den Hartog `Delta_D`, and effective damping indicator.

Monitoring points:

```text
Node 26 = 1/4 span
Node 51 = midspan
Node 76 = 3/4 span
```

Files added/updated:

```text
tools/monitor_typical_explicit_points.py
tcl_procedures/Damping_shifter.tcl
output/diagnostics/typical_explicit_galloping/point_monitoring/
```

Important modelling correction found during this monitoring step:

- The aerodynamic coefficient tables `C_D_data.txt` and `C_L_data2.txt` cover
  only about `0-29.9 deg`.
- The new explicit aerodynamic damping force originally used a direct
  `atan2(v_rel_z, v_rel_y)` lookup angle. In late strong-response phases this
  can produce raw angles up to about `160-178 deg`, which is inconsistent with
  the original `adapt_damp` lookup convention.
- `Damping_shifter.tcl` was corrected so the explicit force uses the same
  positive-along-wind relative-angle convention as `adapt_damp`, with a zero
  division guard and explicit clamping to the aerodynamic table maximum.
- `tools/monitor_typical_explicit_points.py` was updated to use the same
  solver-consistent lookup angle and clamped interpolation. It still records
  `alpha_raw_deg` in the CSV outputs as a diagnostic.

Current point-monitoring results for the already-recorded typical run:

| Point | Node | max abs x disp | max abs z disp | max abs x vel | max abs z vel | lookup alpha | raw alpha | clipped fraction | min `Delta_D` | min `xi_eff` | `xi_eff<0` fraction |
|---|---:|---:|---:|---:|---:|---|---|---:|---:|---:|---:|
| 1/4 span | 26 | `23.2155 m` | `92.1291 m` | `769.148 m/s` | `2282.86 m/s` | `0-29.9 deg` | `0-159.8 deg` | `0.905` | `-16.5499` | `-49.7113` | `0.989` |
| Midspan | 51 | `26.0725 m` | `76.0092 m` | `519.142 m/s` | `694.861 m/s` | `0-29.9 deg` | `0-177.9 deg` | `0.907` | `-16.5466` | `-33.4866` | `0.986` |
| 3/4 span | 76 | `15.8485 m` | `43.7611 m` | `257.654 m/s` | `478.49 m/s` | `0-29.9 deg` | `0-176.7 deg` | `0.906` | `-16.5347` | `-10.2587` | `0.987` |

Interpretation:

- The three observed points show coupled transverse/vertical response growth,
  not an isolated single-node artefact.
- The x-z paths expand from small loops into large trajectories, consistent
  with a self-excited galloping-type instability.
- `Delta_D` and `xi_eff` are negative over most of the recorded point histories,
  so the Den Hartog/effective-damping mechanism is active.
- However, the very high angle-clipping fraction means the late extreme phase
  lies outside the available aerodynamic table range. Therefore the present
  run is valid as a mechanism/instability diagnostic, but its final amplitudes
  should not be treated as physically calibrated production results.
- Next priority: rerun the typical active case after the corrected explicit
  force lookup convention, preferably with event-based stopping/classification
  so severe galloping is captured as a research result before solver slowdown
  or nonconvergence dominates.

## 2026-06-11 Corrected Event-Stop Typical Run

Purpose: rerun the typical `L = 322.8 m`, `H = 10.48 m`, `FORCE_3/SIM1`
active-galloping case with corrected explicit-force coefficient lookup and
event-based stopping, so entering severe galloping becomes an explicit output
state instead of an OpenSees failure.

Pre-run workflow audit findings:

- OpenSees path is `D:\Pyprogramme\OpenSees3.8.0\bin\OpenSees.exe`.
- Dynamic recorders include `-time` for displacement, velocity, acceleration,
  and reaction.
- Global Rayleigh structural damping remains active with `xi = 0.01`.
- Element-level aerodynamic damping writeback remains `record_only`; active
  galloping feedback enters through the explicit velocity-dependent aerodynamic
  force.
- Existing wind input for the three observation nodes remains within the
  aerodynamic coefficient table range before structural motion is considered:
  maximum wind-only angle is about `21-22 deg`, below the `0-29.9 deg` table
  limit.

Critical implementation correction:

- `tcl_procedures/readColumnFromFile.tcl` previously split lines only on
  whitespace. Because `C_D_data.txt` and `C_L_data2.txt` are comma-separated,
  Tcl read the first coefficient-table column with a trailing comma. This made
  Tcl-side interpolation inconsistent with Python post-processing.
- The reader now parses both comma and whitespace separated numeric fields via:

```tcl
set fields [regexp -all -inline {[^,\t ]+} $line]
```

- After this fix, Tcl `damping_change_log.txt` and Python post-processing agree:
  negative effective damping is active in the run.

Event-stop controls:

```yaml
event_stop:
  enabled: true
  max_displacement_m: 5.24        # 0.5H
  max_velocity_mps: 50.0
  max_acceleration_mps2: 5000.0
  min_effective_damping: -5.0
```

Generated config:

```text
output/diagnostics/typical_explicit_event_stop/typical_L322P8_H10P48_U0P6_explicit_force_event_stop.yaml
```

Main run outputs:

```text
output/diagnostics/typical_explicit_event_stop/run/
output/diagnostics/typical_explicit_event_stop/run/termination_audit/opensees_termination_audit.md
output/diagnostics/typical_explicit_event_stop/analysis/typical_explicit_event_stop_analysis.md
output/diagnostics/typical_explicit_event_stop/analysis/typical_explicit_event_stop_stats.json
output/diagnostics/typical_explicit_event_stop/point_monitoring/
```

Run status:

| Quantity | Value |
|---|---:|
| Tcl status | `event_stop` |
| Message | `event_stop_max_displacement` |
| Stop time | `5.15 s` |
| Analyze return code | `0` |
| Max displacement envelope | `5.36805 m` |
| Max velocity envelope | `8.16761 m/s` |
| Max acceleration envelope | `36.0206 m/s^2` |
| Minimum logged `xi_total` | `-1.24585` |
| Negative `xi_total` fraction | `0.968` |
| Max total explicit aerodynamic force | `3919.97 N` |
| Max element explicit aerodynamic force | `122.132 N` |

Three-point monitoring summary:

| Point | Node | max abs x disp | max abs z disp | max abs x vel | max abs z vel | lookup angle range | clipped fraction | min `xi_eff` | `xi_eff<0` fraction |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| 1/4 span | 26 | `3.38448 m` | `0.793798 m` | `4.57963 m/s` | `1.88821 m/s` | `0.0374-15.8 deg` | `0.000` | `-0.952537` | `0.845` |
| Midspan | 51 | `5.01425 m` | `1.6208 m` | `6.02159 m/s` | `2.24611 m/s` | `0.0876-13.8 deg` | `0.000` | `-0.84836` | `0.932` |
| 3/4 span | 76 | `2.65999 m` | `1.59343 m` | `5.14401 m/s` | `1.66412 m/s` | `0.0527-9.52 deg` | `0.000` | `-1.12736` | `1.000` |

Interpretation:

- The corrected event-stop run is now internally consistent: Tcl damping logs,
  explicit force, and Python point monitoring all use the same coefficient-table
  reading and angle lookup convention.
- The run stopped by a designed severe-response event, not by OpenSees
  nonconvergence. Therefore this is a valid labelled severe-galloping output.
- The aerodynamic table produces very strong negative `Delta_D` at small angles,
  so the response reaches the half-sag displacement threshold very quickly.
  This confirms active galloping feedback under the present coefficient set.
- Scientific caution: the next calibration question is whether the aerodynamic
  coefficient slope and explicit-force scaling are physically calibrated for
  the intended iced-conductor condition. The mechanism now works, but the
  strength of the mechanism must be justified before using this case as a final
  engineering probability/coverage result.

## 2026-06-12 Typical Explicit Case Without Active Event Stop

Purpose: respond to the modelling concern that the previous event-stop run may
have hidden the natural solver behaviour. This rerun disables all active
research stop limits and lets OpenSees continue until it either reaches the
target duration or fails naturally.

Configuration:

```text
output/diagnostics/typical_explicit_no_stop/typical_L322P8_H10P48_U0P6_explicit_force_no_stop.yaml
```

Key settings:

```yaml
L: 322.8
Sag: 10.48
dt: 0.05
npt: 4096
force: FORCE_3/SIM1
aerodynamic_damping.writeback_mode: record_only
aerodynamic_force.enabled: true
aerodynamic_force.scale: 1.0
event_stop.enabled: false
```

Main outputs:

```text
output/diagnostics/typical_explicit_no_stop/run/
output/diagnostics/typical_explicit_no_stop/run/termination_audit/opensees_termination_audit.md
output/diagnostics/typical_explicit_no_stop/analysis/typical_explicit_no_stop_analysis.md
output/diagnostics/typical_explicit_no_stop/analysis/typical_explicit_no_stop_stats.json
output/diagnostics/typical_explicit_no_stop/point_monitoring/
```

Solver outcome:

| Quantity | Value |
|---|---:|
| Tcl status | `failed` |
| Message | `analysis_did_not_converge_min_factor_reached` |
| Stop/failure time | `10.921618207737705 s` |
| Target time | `204.8 s` |
| Analyze return code | `-3` |
| Final factor | `4.73320477617254e-7` |
| Minimum allowed factor | `1e-6` |

Response summary:

| Quantity | Value |
|---|---:|
| Max displacement envelope | `99.9816 m` at `10.9001 s` |
| Max velocity envelope | `5169.82 m/s` at `10.9216 s` |
| Max acceleration envelope | `1.31808e6 m/s^2` at `10.9216 s` |
| First envelope > `1.048 m` | `4.0 s` |
| First envelope > `5.24 m` | `5.2 s` |
| First envelope > `10.48 m` | `9.00779 s` |
| First envelope > `50 m` | `10.8085 s` |
| Damping log format | `time element previous_xi_total xi_total` |
| Min logged `xi_total` | `-112.30746568120777` |
| Negative `xi_total` row fraction | `0.8961538461538462` |
| Max absolute logged explicit force value | `2.4811459419599652e8` |

Three-point no-stop monitoring:

| Point | Node | max abs x disp | max abs z disp | max abs x vel | max abs z vel | raw angle range | clipped fraction | min `Delta_D` | min `xi_eff` | `xi_eff<0` fraction |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|
| 1/4 span | 26 | `57.0107 m` | `85.9411 m` | `3432.21 m/s` | `4917 m/s` | `0.0374-178 deg` | `0.415` | `-16.4857` | `-126.046` | `0.826` |
| Midspan | 51 | `68.5905 m` | `99.4007 m` | `1473.63 m/s` | `2196.95 m/s` | `0.0876-168 deg` | `0.500` | `-16.5397` | `-55.5416` | `0.926` |
| 3/4 span | 76 | `52.0616 m` | `64.6974 m` | `628.925 m/s` | `447.584 m/s` | `0.0527-177 deg` | `0.370` | `-16.4117` | `-16.2372` | `0.896` |

Interpretation:

- The run is not actively stopped by project limits. OpenSees naturally fails
  after severe response, repeatedly reducing the substep factor and then
  stopping when the factor falls below the allowed minimum. This confirms that
  the previous strong response was not an artifact of the event-stop trigger.
- Effective aerodynamic damping is active. `xi_total` is negative for most
  logged rows, pointwise `Delta_D = dC_L/dalpha + C_D` is strongly negative for
  sustained intervals, and the explicit velocity-dependent force grows with
  response.
- The response has qualitative galloping features: low-frequency coupled
  transverse/vertical growth, expanding x-z paths, and spanwise response at
  1/4, midspan, and 3/4 points. It should be described as severe
  galloping/divergent aeroelastic instability, not as a calibrated stable
  limit-cycle amplitude.
- The magnitude and growth rate are too strong for final engineering
  prediction. Likely reasons are steep `dC_L/dalpha` after per-degree to
  per-radian conversion, lack of nonlinear aerodynamic saturation outside the
  coefficient table range, and the simplified scalar damping-force projection
  being applied to both transverse and vertical velocity components.

Wind-load logic conclusion:

- The original MATLAB and current Python wind-force workflow precompute
  background drag/lift loads from wind histories, coefficient tables, and
  static tributary projected area. They do not recompute the full drag/lift
  vector from the moving cable at every OpenSees step.
- In the current model, motion-dependent aeroelastic feedback is supplied by
  `apply_explicit_aero_damping_force` in `tcl_procedures/Damping_shifter.tcl`.
  This is a defensible reduced-order Den Hartog galloping mechanism, but it is
  not yet a fully coupled quasi-steady force model.
- If final quantitative prediction is required, the next model-improvement
  branch should implement full real-time quasi-steady drag/lift recomputation
  from local relative wind, cable velocity, and possibly displaced local cable
  orientation, then compare it against the current reduced-order damping-force
  formulation.

## 2026-06-12 Real-Time Quasi-Steady Full-Force Branch

Purpose: implement and test a full real-time quasi-steady aerodynamic-force
branch. This branch recomputes drag and lift during the OpenSees transient
analysis from local relative wind, cable velocity, and instantaneous local
cable orientation, instead of using only a scalar Den Hartog equivalent damping
force.

Implemented files:

```text
tcl_procedures/Damping_shifter.tcl
src/cable_analyser/tcl_writer.py
src/cable_analyser/analysis.py
config/default_config.yaml
tests/test_tcl_writer.py
tools/prepare_quasi_steady_comparison_configs.py
```

Implementation details:

- `Damping_shifter.tcl` now reads `C_L_data2.txt` in addition to `C_D_data.txt`
  and `dC_L.txt`.
- New Tcl procedure: `apply_quasi_steady_aero_force`.
- For each element and each transient step, the procedure:
  1. reads current nodal displacement and velocity;
  2. builds the instantaneous element tangent from deformed node positions;
  3. reads the same element-averaged wind histories used by the previous
     damping workflow;
  4. computes relative wind as `v_wind - v_cable`;
  5. removes the component parallel to the instantaneous cable tangent;
  6. computes attack angle, interpolates `C_D` and `C_L`;
  7. computes `qL = 0.5 * ro_air * U^2 * B * L_e`;
  8. applies full drag plus lift to the two element nodes.
- The branch logs:

```text
quasi_steady_aero_force_log.txt
```

with columns:

```text
time total_abs_force max_element_force scale max_raw_alpha_deg clipped_count element_count
```

Configuration interface:

```yaml
quasi_steady_aero_force:
  enabled: true
  scale: 1.0
  log_stride: 1
  use_precomputed_loads: false
```

Important modelling rule:

- For the full quasi-steady branch, `use_precomputed_loads: false` should be
  used by default. The precomputed `H_drag/H_lift/V_drag/V_lift` force files
  are then not applied as OpenSees load patterns; only the wind velocity files
  are read. This avoids double-counting aerodynamic load.
- The old explicit branch remains available:

```yaml
aerodynamic_force:
  enabled: true
```

Comparison setup:

```text
output/diagnostics/quasi_steady_comparison/typical_explicit_damping_no_stop.yaml
output/diagnostics/quasi_steady_comparison/typical_quasi_steady_full_force_no_stop.yaml
```

Both cases use:

- typical geometry: `L = 322.8 m`, `Sag = 10.48 m`;
- `FORCE_3/SIM1` wind histories;
- `dt = 0.05 s`, `npt = 4096`, target duration `204.8 s`;
- OpenSees 3.8.0;
- Rayleigh structural damping, `xi = 0.01`;
- no event stop.

Main comparison outputs:

```text
output/diagnostics/quasi_steady_comparison/explicit_damping/run/
output/diagnostics/quasi_steady_comparison/quasi_steady_full_force/run/
output/diagnostics/quasi_steady_comparison/comparison_report/quasi_steady_comparison_report.md
output/diagnostics/quasi_steady_comparison/comparison_report/comparison_stats.json
output/diagnostics/quasi_steady_comparison/comparison_report/midspan_displacement_comparison.png
output/diagnostics/quasi_steady_comparison/comparison_report/aero_force_comparison.png
```

Comparison result:

| Case | Aero model | Precomputed force files | Solver status | Last time | Max displacement envelope | Max velocity envelope | Max acceleration envelope | Max total aero force |
|---|---|---|---|---:|---:|---:|---:|---:|
| `explicit_damping` | scalar equivalent velocity damping force | yes | failed, `-3` | `10.8891 s` | `108.891 m` | `6211.26 m/s` | `1.95114e6 m/s^2` | `3.99736e8 N` |
| `quasi_steady_full_force` | real-time full drag/lift | no | success | `204.8 s` | `1.03969 m` | `1.0454 m/s` | `7.93671 m/s^2` | `579.946 N` |

Interpretation:

- The full quasi-steady branch is now technically active and verified by a
  complete 204.8 s run. It uses local relative wind and deformed local cable
  orientation at every transient step.
- The previous explicit damping branch is much more aggressive. It transforms
  Den Hartog susceptibility directly into a velocity-proportional energy-input
  force and still naturally fails near 10.9 s under the same wind histories.
- The new full-force branch does not reproduce that explosive response. This
  is a major diagnostic result: the two formulations are not equivalent.
- `adapt_damp` still records mostly negative Den Hartog `xi_total` in the
  quasi-steady run, but because `writeback_mode = record_only`, this diagnostic
  damping is not injected into the structural equation. The solved force is the
  full quasi-steady drag/lift vector.
- Scientific caution: the stable quasi-steady result must not yet be taken as
  proof that galloping is absent. It means the present full-force sign
  convention, `C_L(alpha)` table, relative-flow projection, and Den Hartog
  diagnostic linearization must now be reconciled. The next audit should check
  the small-perturbation derivative of the implemented full force and verify
  that it yields the expected Den Hartog aerodynamic damping sign.

## 2026-06-12 Corrected Typical Quasi-Steady Comparison Against `typical_explicit_no_stop`

Important correction:

- The first quick quasi-steady comparison used `geometry.type = 1`, while the
  user's requested baseline `output/diagnostics/typical_explicit_no_stop` uses
  `geometry.type = 2`.
- Therefore a strict same-model comparison was rerun from the exact
  `typical_explicit_no_stop` YAML, changing only the aerodynamic force
  formulation and output directory.

Strict same-model quasi-steady config:

```text
output/diagnostics/typical_quasi_steady_no_stop/typical_L322P8_H10P48_U0P6_quasi_steady_no_stop.yaml
```

Configuration equivalence:

| Item | Explicit baseline | Quasi-steady branch |
|---|---|---|
| Geometry type | `2` | `2` |
| L / Sag | `322.8 / 10.48 m` | `322.8 / 10.48 m` |
| Wind case | `FORCE_3/SIM1` | `FORCE_3/SIM1` |
| dt / npt | `0.05 / 4096` | `0.05 / 4096` |
| Structural damping | `Rayleigh, xi = 0.01` | `Rayleigh, xi = 0.01` |
| Event stop | `false` | `false` |
| Old precomputed force files applied as loads | yes | no |
| Active aero force | explicit equivalent damping force | real-time full quasi-steady drag/lift |

Rationale for disabling precomputed force files in the quasi-steady branch:

- The precomputed `H_drag/H_lift/V_drag/V_lift` files already represent an
  aerodynamic force based on wind-only attack angle and static tributary area.
- The new branch recomputes drag/lift at every step. Applying both would
  double-count aerodynamic loads.
- The wind velocity files are still read and are exactly the same
  `FORCE_3/SIM1` wind histories.

Strict same-model result outputs:

```text
output/diagnostics/typical_quasi_steady_no_stop/run/
output/diagnostics/typical_quasi_steady_no_stop/run/termination_audit/opensees_termination_audit.md
output/diagnostics/typical_quasi_steady_no_stop/point_monitoring/
output/diagnostics/typical_quasi_steady_no_stop/comparison_with_typical_explicit_no_stop/typical_quasi_steady_design_and_comparison.md
output/diagnostics/typical_quasi_steady_no_stop/comparison_with_typical_explicit_no_stop/typical_quasi_vs_explicit_stats.json
output/diagnostics/typical_quasi_steady_no_stop/comparison_with_typical_explicit_no_stop/typical_midspan_response_comparison.png
output/diagnostics/typical_quasi_steady_no_stop/comparison_with_typical_explicit_no_stop/typical_aero_force_comparison.png
```

Result summary:

| Case | Status | Last time | Max displacement envelope | Max velocity envelope | Max acceleration envelope | Max total aero force |
|---|---|---:|---:|---:|---:|---:|
| `typical_explicit_no_stop` | failed, `-3` | `10.9216 s` | `99.9816 m` | `5169.82 m/s` | `1.31808e6 m/s^2` | `2.48115e8 N` |
| `typical_quasi_steady_no_stop` | success | `204.8 s` | about `1.04 m` | about `1.05 m/s` | about `7.94 m/s^2` | about `580 N` |

Research interpretation:

- With the same geometry and wind histories, the old explicit equivalent
  damping-force branch produces severe divergent response and natural solver
  nonconvergence.
- The full quasi-steady branch completes the target duration with small
  response.
- Therefore the previous extreme response is not caused by the structure or
  wind history alone; it is tied to the scalar equivalent damping-force
  implementation.
- The full quasi-steady branch is now the preferred baseline for physical
  time-domain aeroelastic force coupling.
- The next required scientific audit is a small-perturbation linearization of
  the implemented full quasi-steady force to check its effective aerodynamic
  damping sign against Den Hartog's `dC_L/dalpha + C_D` criterion and our
  `C_L` sign convention.

Reporting/tooling note:

- `tools/monitor_typical_explicit_points.py` was updated after the strict
  comparison so the "Reasonableness Checks" section is conditional on actual
  response amplitude and coefficient-table clipping. This prevents the
  quasi-steady small-response case from being described with old severe-gallop
  wording.
- Validation after this change: `pytest tests/test_tcl_writer.py -q` passed
  with `8 passed`.

## 2026-06-12 Revised Main-Line Aeroelastic Modification

User clarification:

- The intended research modification is not to replace the original wind-load
  workflow with a full real-time drag/lift model.
- The intended modification is to preserve the original dynamic wind-force
  workflow and improve the per-step attack-angle / aerodynamic-damping
  calculation by including the current deformed element direction.

Main-line model after clarification:

```text
F_total(t) = F_precomputed_original_wind(t)
           + F_explicit_equivalent_aero_damping(
                 relative wind,
                 cable velocity,
                 deformed element direction
             )
```

Preserved:

- precomputed `H_drag/H_lift/V_drag/V_lift` force files remain applied through
  OpenSees `Path` time series;
- same `FORCE_3/SIM1` wind histories;
- same explicit equivalent aerodynamic damping force pathway;
- `aerodynamic_damping.writeback_mode = record_only`.

Changed:

- `Damping_shifter.tcl` now has helper procedure
  `get_element_local_aero_basis`.
- `apply_explicit_aero_damping_force` now projects cable velocity and relative
  wind into the local aerodynamic basis built from the current deformed element
  tangent.
- `adapt_damp` now uses the same local basis for Den Hartog attack angle,
  `Delta_D`, and `xi_total`.
- `src/cable_analyser/tcl_writer.py` now writes:

```text
set use_deformed_element_direction 1
```

to `inputs_aerodynamic_damping.tcl`.

Configuration switch:

```yaml
aerodynamic_damping:
  use_deformed_element_direction: true
```

Important interpretation of the orange branch:

- The previous orange `quasi_steady_full_force` result is now treated as an
  exploratory full-replacement branch, not the main research workflow.
- It changed too much at once by disabling precomputed wind-force files and
  replacing them with full real-time drag/lift. It remains useful as a
  sensitivity/reference model but should not be presented as the corrected
  original workflow.

Direction-aware typical config:

```text
output/diagnostics/typical_directional_explicit_no_stop/typical_L322P8_H10P48_U0P6_directional_explicit_no_stop.yaml
```

Design note:

```text
output/diagnostics/typical_directional_explicit_no_stop/directional_explicit_design_note.md
```

Verification:

- `pytest tests/test_tcl_writer.py -q` passed with `8 passed`.
- A 4096-step no-stop run was attempted. The external tool timed out before
  OpenSees wrote `analysis_status.txt`, so the run is not a complete production
  result.
- Partial audit:

```text
output/diagnostics/typical_directional_explicit_no_stop/run/termination_audit/opensees_termination_audit.md
```

- Partial run state:
  - last recorded time about `10.9281 s`;
  - severe response had already developed;
  - minimum logged `xi_total` about `-934`;
  - no lingering OpenSees process after timeout.

Interpretation:

- Including the deformed element direction is now implemented and active.
- The direction-aware original branch still enters the severe-response regime
  near the same time window as the previous explicit branch, although the
  no-stop run became too slow to finish before tool timeout.
- Next run should use a research event stop / solver-state stop so severe
  galloping is recorded as a valid output before excessive substepping.

## 2026-06-12 Incremental Quasi-Steady Aero Force Branch

Purpose:

- Keep the original precomputed OpenSees `Path` wind-force workflow.
- Add only the real-time motion-induced quasi-steady correction:

```text
F_applied = F_original_path + Delta_F_motion
Delta_F_motion = F_current - F_reference
```

Implementation:

- Added `apply_incremental_quasi_steady_aero_force` in
  `tcl_procedures/Damping_shifter.tcl`.
- Added original force-file loading helpers:
  `load_incremental_original_force_data` and
  `get_incremental_original_force_component`.
- Added registration through `STKO_VAR_OnBeforeAnalyze_CustomFunctions` with
  constant time series tag `902000`.
- Added config section:

```yaml
incremental_quasi_steady_aero_force:
  enabled: false
  scale: 1.0
  log_stride: 20
  keep_precomputed_loads: true
```

- `src/cable_analyser/tcl_writer.py` now writes `force_data_dir` into
  `Input.tcl` and writes:

```text
set enable_incremental_quasi_steady_aero_force ...
set incremental_quasi_steady_aero_force_scale ...
set incremental_quasi_steady_aero_force_log_stride ...
```

- `src/cable_analyser/analysis.py` clears stale
  `incremental_quasi_steady_aero_force_log.txt` before runs.
- Unit tests updated. Verification:

```text
python -m pytest tests/test_tcl_writer.py -q
10 passed
```

Special diagnostic log:

```text
incremental_quasi_steady_aero_force_log.txt
```

Columns:

```text
time
F_original
F_reference
F_current
Delta_F_motion
total_abs_delta_force
max_abs_delta_force
scale
max_alpha_reference_deg
max_alpha_current_deg
clipped_count
ele_count
```

Definitions:

- `F_original`: nodal absolute total of the original force files after the
  OpenSees `1000` load factor.
- `F_reference`: element-integrated quasi-steady absolute force using current
  deformed local basis and wind-only relative velocity.
- `F_current`: element-integrated quasi-steady absolute force using current
  deformed local basis and wind-minus-cable relative velocity.
- `Delta_F_motion` / `total_abs_delta_force`: element-integrated absolute
  magnitude of `F_current - F_reference`; this is the extra load actually
  applied by the new branch.

Typical diagnostic config:

```text
output/diagnostics/typical_incremental_quasi_steady_no_stop/typical_L322P8_H10P48_U0P6_incremental_quasi_steady_no_stop.yaml
```

Generated outputs:

```text
output/diagnostics/typical_incremental_quasi_steady_no_stop/run
output/diagnostics/typical_incremental_quasi_steady_no_stop/point_monitoring
output/diagnostics/typical_incremental_quasi_steady_no_stop/analysis
```

Run status:

- Full 4096-step no-stop run was attempted twice.
- The run did not naturally fail with OpenSees `-3`; it was externally stopped
  by command timeout before target duration.
- Last usable partial time: about `114.243 s`.
- Audit:

```text
output/diagnostics/typical_incremental_quasi_steady_no_stop/run/termination_audit/opensees_termination_audit.md
```

Key numerical observations from the partial typical result:

- `F_original`: about `313-672 N`.
- `F_reference`: about `464-466 N`.
- `F_current`: about `399-4049 N`.
- `total_abs_delta_force`: about `0-3866 N`.
- Maximum `total_abs_delta_force / F_original`: about `10.96`.
- Final `total_abs_delta_force / F_original`: about `4.82`.
- Current-angle clipping fraction in the incremental log: about `0.725`.
- Three monitored points show large vertical response after about `102 s`.
- Effective damping indicators become strongly negative over much of the record,
  confirming that negative aerodynamic damping feedback is active.

Interpretation:

- The new incremental branch avoids the old explicit equivalent-damping force
  explosion (`1e8-1e9 N` scale). The force correction stays in the `1e3 N`
  range in the partial run.
- The response still enters a strong nonlinear phase after about `102 s`, but
  this phase is dominated by high cable velocity and attack angles far beyond
  the available aerodynamic coefficient table.
- Because many rows are clamped to the table limit (`29.9 deg`), post-onset
  dynamics should be interpreted as "severe galloping / outside aerodynamic
  table validity" rather than a quantitatively validated large-amplitude
  response.
- Next methodological improvement should add an angle-domain event flag or stop
  condition, and/or extend the aerodynamic coefficient table to the high-angle
  range before interpreting the post-102 s response quantitatively.

## 2026-06-12 Baseline-Matched Incremental Quasi-Steady Branch

Strict correction after methodology review:

- The earlier incremental branch was direction-aware but used a quasi-steady
  reference force that was not exactly the same baseline as the original
  `Path` wind force files.
- The corrected branch now uses the original nodal force files themselves as
  the baseline:

```text
F_total(t) = F_original_path(t)
           + [F_current_nodal(t) - F_original_nodal(t)]
```

where:

- `F_original_path(t)` is already applied by OpenSees `Path` time series.
- `F_original_nodal(t)` is reconstructed from
  `NODE_i_H_drag/H_lift/V_drag/V_lift.txt` with the same OpenSees `1000`
  factor.
- `F_current_nodal(t)` is computed at every OpenSees step from:
  - current nodal velocity;
  - current deformed nodal tangent / local aerodynamic plane;
  - nodal wind histories `NODE_i_wind_H/wind_V.txt`;
  - same projected-area convention as the original generator:
    `pi * Dia * node_tributary_length / 2`;
  - same aerodynamic-force density basis:
    `wind_generation.ro_air_force * 1000`.

Important interpretation:

- The new scheme does **not** remove nonlinear terms. `F_current - F_original`
  can still contain speed-squared, attack-angle, coefficient-table, direction,
  and deformation nonlinearities.
- The correction is that we no longer write Den Hartog's small-perturbation
  negative-damping criterion as an artificial force always acting along the
  velocity vector.
- The force budget is now baseline-matched: `F_original` and `F_reference` are
  identical in the log by construction and by result.

Formal typical run:

```text
output/diagnostics/typical_incremental_quasi_steady_validity_stop
```

Config:

```text
output/diagnostics/typical_incremental_quasi_steady_validity_stop/typical_L322P8_H10P48_U0P6_incremental_quasi_steady_validity_stop.yaml
```

Run result:

- OpenSees return code: `0`.
- Status: `event_stop`.
- Event reason: `event_stop_max_alpha`.
- Stop time: about `50.30 s`.
- Event log:

```text
output/diagnostics/typical_incremental_quasi_steady_validity_stop/run/event_stop_log.txt
```

Event values:

- max displacement envelope: about `1.098 m`;
- max velocity envelope: about `3.987 m/s`;
- max acceleration envelope: about `72.467 m/s^2`;
- min effective damping: about `-0.994`;
- max current attack angle: about `35.174 deg`;
- clipped fraction at stop: about `0.00990`.

Force diagnostics:

- `F_original == F_reference`: about `319-570 N`.
- `F_current`: about `619-1402 N`.
- `total_abs_delta_force`: about `520-1409 N`.
- maximum `total_abs_delta_force / F_original`: about `3.58`.

Outputs:

```text
output/diagnostics/typical_incremental_quasi_steady_validity_stop/run
output/diagnostics/typical_incremental_quasi_steady_validity_stop/run/termination_audit
output/diagnostics/typical_incremental_quasi_steady_validity_stop/point_monitoring
output/diagnostics/typical_incremental_quasi_steady_validity_stop/analysis
output/diagnostics/typical_incremental_quasi_steady_validity_stop/incremental_quasi_steady_validation_note.md
```

Formal simulation output prerequisite:

Every formal single-case simulation from this point onward must produce:

- raw OpenSees files: `Dynamic.out`, `Velocity.out`, `Accel.out`,
  `Reaction.out`, `Element1.out`, `damping_change_log.txt`,
  `analysis_status.txt` or solver logs if no status file exists;
- aerodynamic force log:
  `incremental_quasi_steady_aero_force_log.txt`;
- three observation-point CSV files for nodes 26, 51, and 76, including:
  time, x/z displacement, x/z velocity, x/z acceleration, wind components,
  relative speed, raw and lookup attack angle, `C_D`, `C_L`, `Delta_D`, and
  `xi_eff`;
- figures:
  - point displacement x/z;
  - point velocity x/z;
  - point acceleration x/z;
  - x-z displacement paths;
  - `C_D` / `C_L`;
  - attack angle;
  - `Delta_D`;
  - `xi_eff`;
  - force decomposition (`F_original`, `F_reference`, `F_current`,
    `Delta_F_motion`, `total_abs_delta_force`);
  - force ratio / branch comparison where relevant;
- termination audit using `tools/audit_opensees_run_status.py`.

Current verdict:

- The baseline-matched incremental quasi-steady branch is the current preferred
  mechanism for formal typical simulations.
- The `event_stop_max_alpha` result is not a numerical failure; it marks the
  point where the current aerodynamic coefficient table is exceeded. For
  quantitative post-event large-amplitude galloping, the aerodynamic coefficient
  table must be extended beyond about `29.9 deg`.

## 2026-06-12 Formal Run Termination Policy Update

User instruction:

- For subsequent research runs, do **not** set active termination limits.
- Formal simulations should run until either:
  - the target OpenSees duration is completed, or
  - OpenSees naturally fails/interupts/convergence-breaks.

Implications:

- Do not use project-side event stops such as:
  - displacement threshold stop;
  - velocity threshold stop;
  - acceleration threshold stop;
  - effective-damping threshold stop;
  - attack-angle / aerodynamic-table-validity stop.
- If an attack angle exceeds the available aerodynamic coefficient table, keep
  computing and record the exceedance/clipping diagnostics, but do not stop the
  OpenSees analysis because of it.
- Natural OpenSees interruption is now part of the research output, not an
  error to be avoided by early project-side stopping.

Required recording remains unchanged:

- Always keep `analysis_status.txt` if OpenSees/Tcl writes one.
- If no `analysis_status.txt` exists, preserve solver stdout/stderr logs and run
  `tools/audit_opensees_run_status.py`.
- Always output the force decomposition, observation-point time histories,
  point figures, x-z trajectories, coefficient histories, damping indicators,
  and termination audit.

Historical note:

- The `typical_incremental_quasi_steady_validity_stop` run remains useful as a
  diagnostic showing when the coefficient-table boundary is first crossed.
- It should **not** be used as the default formal simulation protocol going
  forward.

## 2026-06-12 Formal No-Stop Typical Rerun

Run protocol:

- Baseline-matched incremental quasi-steady branch.
- No active project-side event stop:

```yaml
event_stop:
  enabled: false
```

- Target duration: `204.8 s` (`4096` steps at `dt = 0.05 s`).
- Solver: `D:\Pyprogramme\OpenSees3.8.0\bin\OpenSees.exe`.

Config:

```text
output/diagnostics/typical_incremental_quasi_steady_formal_no_stop/typical_L322P8_H10P48_U0P6_incremental_quasi_steady_formal_no_stop.yaml
```

Output directories:

```text
output/diagnostics/typical_incremental_quasi_steady_formal_no_stop/run
output/diagnostics/typical_incremental_quasi_steady_formal_no_stop/run/termination_audit
output/diagnostics/typical_incremental_quasi_steady_formal_no_stop/point_monitoring
output/diagnostics/typical_incremental_quasi_steady_formal_no_stop/analysis
```

Termination:

- Status: `failed`.
- Message: `analysis_did_not_converge_min_factor_reached`.
- OpenSees analyze return code: `-3`.
- Final time: `86.43379095621202 s`.
- Target progress: about `42.204%`.
- Increment: `17607`.
- Adaptive factor: `2.020204161772889e-9`, below `min_factor = 1e-06`.

Audit:

```text
output/diagnostics/typical_incremental_quasi_steady_formal_no_stop/run/termination_audit/opensees_termination_audit.md
```

Key force diagnostics:

- `F_original == F_reference`: about `304-914 N`.
- `F_current`: about `619-11425 N`.
- `total_abs_delta_force`: about `520-11419 N`.
- Maximum `total_abs_delta_force / F_original`: about `28.18`.
- Final `total_abs_delta_force / F_original`: about `8.68`.
- Current attack angle reaches almost `90 deg`; about `93.5%` of force-log rows
  have at least one clipped node.

Three-point response summary:

- Nodes: 26 (`1/4 span`), 51 (`midspan`), 76 (`3/4 span`).
- Last response time in point-monitoring files: about `86.4338 s`.
- Maximum observed displacements:
  - 1/4 span: `|x| <= 2.23 m`, `|z| <= 4.70 m`;
  - midspan: `|x| <= 3.00 m`, `|z| <= 6.16 m`;
  - 3/4 span: `|x| <= 2.30 m`, `|z| <= 4.76 m`.
- Maximum observed velocities:
  - 1/4 span: `|vx| <= 39.85 m/s`, `|vz| <= 48.41 m/s`;
  - midspan: `|vx| <= 65.09 m/s`, `|vz| <= 38.71 m/s`;
  - 3/4 span: `|vx| <= 48.15 m/s`, `|vz| <= 54.29 m/s`.
- Maximum observed accelerations are very large (`~8.6e3` to `1.52e4 m/s^2`),
  consistent with the solver entering a severe nonlinear / nonconvergent
  response phase near the final time.

Interpretation:

- The run obeyed the no-active-stop policy. The stop is an OpenSees natural
  convergence failure, not a project-side limit.
- The large force correction and response growth begin after about `58-60 s`.
- The post-onset response uses clipped aerodynamic coefficients for much of the
  record; therefore this run is valid as a no-stop numerical experiment and
  failure/onset diagnostic, but quantitative post-clipping large-amplitude
  aerodynamic interpretation still requires extending the coefficient table.

### 2026-06-12 Diagnostic: Cause of force growth near 60 s

Question investigated: why the incremental quasi-steady force grows rapidly
from about `58-60 s`.

Additional diagnostic script:

```text
tools/diagnose_incremental_force_power.py
```

Findings:

- The original weather/path load does not jump near `60 s`; the growth is in
  `F_current - F_reference`.
- Three monitored points show that, after `58 s`, the reconstructed local
  current aerodynamic force usually has negative mean mechanical power
  (`F_current . v < 0`) and the reconstructed incremental force also usually has
  negative mean mechanical power (`Delta_F_motion . v < 0`). Thus the large
  force magnitude at those points is mainly resisting the already large motion,
  not simply pushing it.
- The drag contribution is consistently dissipative in the large-response
  windows. Lift can add or remove energy depending on phase and coefficient
  sign, so the full quasi-steady force cannot be treated as a pure damper.
- Time-step setting: the nominal transient step is `dt = 0.05 s`; the first
  modal frequencies in the formal run are about `0.171 Hz` and `0.34 Hz`, so
  the nominal step is not obviously too coarse for the low modes. However, the
  aerodynamic update is explicit at the step boundary; once velocities and
  attack angles change rapidly, a time-step sensitivity check (`0.025 s`,
  `0.01 s`) is still required.
- Important implementation risk: the precomputed Path load applies force
  components as

```text
H_drag -> transverse
H_lift -> vertical
V_drag -> vertical
V_lift -> transverse
```

  so the reference nodal load is reconstructed as

```text
fy = H_drag + V_lift
fz = H_lift + V_drag
```

  but the real-time quasi-steady force currently uses the conventional local
  decomposition

```text
local_y = qA * CD * ey - qA * CL * ez
local_z = qA * CD * ez + qA * CL * ey
```

  This may not be baseline-compatible with the precomputed Path load convention.
  A zero-motion baseline check at nodes 26, 51, and 76 found nonzero
  `F_current(v=0) - F_reference`, with mean difference about `7.4-7.6 N` per
  monitored node while the mean reference force is about `4.5-4.6 N`.

Required correction before accepting the branch:

- Make the real-time force decomposition and the precomputed `H/V drag/lift`
  Path load convention identical, or regenerate/rewrite the precomputed load
  convention so both are physically and numerically consistent.
- Add direct per-node logging of `delta_fx`, `delta_fy`, `delta_fz`,
  `Delta_F_motion . nodeVel`, `drag_power`, `lift_power`, `U_rel`, `alpha`,
  `CD`, and `CL` around the onset. Global force magnitude alone is not enough
  to diagnose galloping energy input.

### 2026-06-12 Diagnostic: axial stretch and post-40 s motion/force relation

New diagnostic scripts:

```text
tools/diagnose_element_length_variation.py
tools/diagnose_motion_force_after_40s.py
```

Outputs:

```text
output/diagnostics/typical_incremental_quasi_steady_formal_no_stop/analysis/element_length_variation_summary.json
output/diagnostics/typical_incremental_quasi_steady_formal_no_stop/analysis/element_length_variation_windows.csv
output/diagnostics/typical_incremental_quasi_steady_formal_no_stop/analysis/after_40s_motion_force/after_40s_force_motion_strain_overview.png
output/diagnostics/typical_incremental_quasi_steady_formal_no_stop/analysis/after_40s_motion_force/after_40s_summary.json
```

Model form:

- Current typical model uses `forceBeamColumn` with a circular fiber section,
  `Corotational` transformation, and `InitStrainMaterial` for pretension.
- This is not an inextensible cable model; element length change is permitted
  and resisted by section axial stiffness `EA`.

Material / strength reference for current typical case:

- Diameter: `0.02862 m`.
- Area: about `6.433e-4 m^2`.
- `E = 69 GPa`, so `EA = 4.439e7 N`.
- Pretension strain: about `4.46e-4`.
- Rated-strength strain (`131.9 kN / EA`): about `2.97e-3`.

Measured geometric length change from existing formal no-stop run:

| Time window | max abs strain | max length change |
|---|---:|---:|
| `0-40 s` | `2.21e-4` | `0.00072 m` |
| `40-50 s` | `2.87e-4` | `0.00093 m` |
| `50-58 s` | `2.19e-3` | `0.00713 m` |
| `58-65 s` | `2.53e-3` | `0.00818 m` |
| `65-75 s` | `6.51e-3` | `0.02118 m` |
| `75-86.43 s` | `6.66e-3` | `0.02157 m` |

Interpretation:

- Before `50 s`, element length variation is small.
- From `50-65 s`, axial strain approaches the rated-strength strain.
- After about `65 s`, maximum geometric strain exceeds the rated-strength
  equivalent strain by more than a factor of two. A rough `EA * strain`
  estimate gives about `295 kN` at the maximum, above the `131.9 kN` rated
  strength.
- Therefore the later response cannot be treated as a physically credible
  high-stiffness coordinated cable motion. The axial/stretch state must be
  corrected or used as a failure/invalidity indicator before further galloping
  interpretation.

Post-40 s force/motion relation:

- The onset around `57-58 s` coincides with attack angle leaving the coefficient
  table and max element strain jumping upward.
- Three-point reconstructed `Delta_F_motion . velocity` is mostly negative
  after `50 s`, especially during `58-75 s`; the force increment is generally
  resisting the large point motion rather than causing it directly.
- Continued speed growth despite negative aerodynamic power indicates the
  response has likely entered a nonphysical structural/large-deformation state,
  with stored/released structural energy, boundary constraints, and invalid
  high-angle aerodynamic lookup dominating the observed motion.

Next required model checks/fixes:

- Treat axial strain exceeding rated-strength strain as a physical invalidity
  or failure indicator.
- Consider an inextensible or tension-dominated cable formulation, axial
  stiffness scaling sensitivity, or a tension/failure stop diagnostic to
  separate realistic galloping from structural-model breakdown.
- Rerun the typical case only after fixing the baseline force convention and
  adding direct per-node aerodynamic power and element strain/tension logging.

### 2026-06-12 Update: force mapping fixed and power/strain logs added

Code changes:

- `tcl_procedures/Damping_shifter.tcl`
  - Incremental QS force now matches the original Path-load component mapping:

```text
H_drag -> transverse
V_lift -> transverse
H_lift -> vertical
V_drag -> vertical
```

  - The real-time current force is therefore assembled as:

```text
local_y = qA * C_D * e_y + qA * C_L * e_y
local_z = qA * C_D * e_z - qA * C_L * e_z
```

  - Added global force-log columns:

```text
total_delta_power
total_current_power
total_drag_power
total_lift_power
baseline_mismatch_abs
max_baseline_mismatch_abs
```

  - Added per-node log:

```text
incremental_qs_node_power_log.csv
```

  with node force components, node velocity, `Delta_F . v`, current/drag/lift
  power, `U_rel`, `alpha`, `CD`, `CL`, clipping flag, and baseline mismatch.

  - Added per-element geometric strain / estimated tension logs:

```text
element_strain_tension_log.csv
element_strain_tension_summary_log.csv
```

- `src/cable_analyser/tcl_writer.py`
  - Writes `element_axial_EA`, `element_pretension_load`, and
    `element_strain_log_stride`.

- `src/cable_analyser/analysis.py`
  - Clears the new diagnostic logs before a fresh TH run.

- New scripts:

```text
tools/prepare_typical_incremental_qs_mapping_fixed_power_strain_config.py
tools/analyse_mapping_fixed_power_strain_case.py
```

Verification:

```text
pytest tests/test_tcl_writer.py -q
```

passed: `10 passed`.

Rerun:

```text
output/diagnostics/typical_incremental_qs_mapping_fixed_power_strain
```

The run was externally interrupted by the Codex shell timeout after 20 minutes,
not by OpenSees natural convergence failure. It nevertheless reached
`95.8592259125844 s`, so the requested `40-65 s` diagnostic interval is fully
covered.

Important outputs:

```text
output/diagnostics/typical_incremental_qs_mapping_fixed_power_strain/run/incremental_quasi_steady_aero_force_log.txt
output/diagnostics/typical_incremental_qs_mapping_fixed_power_strain/run/incremental_qs_node_power_log.csv
output/diagnostics/typical_incremental_qs_mapping_fixed_power_strain/run/element_strain_tension_log.csv
output/diagnostics/typical_incremental_qs_mapping_fixed_power_strain/run/element_strain_tension_summary_log.csv
output/diagnostics/typical_incremental_qs_mapping_fixed_power_strain/analysis/trigger_40_65/trigger_40_65_summary.json
output/diagnostics/typical_incremental_qs_mapping_fixed_power_strain/analysis/trigger_40_65/trigger_40_65_overview.png
output/diagnostics/typical_incremental_qs_mapping_fixed_power_strain/point_monitoring
```

Key event times from the corrected run:

| Event | Time |
|---|---:|
| first `max_alpha_current_deg > 29.9 deg` | `69.51330692520463 s` |
| first `Delta_F_motion > 1500 N` | `69.68470297336587 s` |
| first `max_abs_strain > 0.002` | `69.69799921869279 s` |
| first `max_abs_strain > rated-strength strain` | `69.7176026573158 s` |
| first `total_delta_power > 10 kW` | `69.74924193572579 s` |

Corrected `40-65 s` interpretation:

- The earlier `58-60 s` abnormal force growth is removed by the component
  mapping fix.
- In `40-65 s`, `max_alpha_current_deg` remains below the coefficient-table
  limit and `clipped_count = 0`.
- In `40-65 s`, global `Delta_F_motion` is small compared with the previous
  run:
  - `40-50 s`: mean about `67.8 N`;
  - `50-58 s`: mean about `66.5 N`;
  - `58-65 s`: mean about `90.4 N`.
- In `40-65 s`, global `Delta_F . v` is negative in every logged row
  (`total_delta_power_positive_fraction = 0` for each window), so the
  aerodynamic increment is not driving the motion in that interval.
- In `40-65 s`, max geometric strain is very small:
  - `40-50 s`: `2.37e-5`;
  - `50-58 s`: `4.01e-5`;
  - `58-65 s`: `5.95e-5`.
- Baseline mismatch is now small:
  - global mean about `1.33 N`;
  - global max about `2.17 N`;
  - per-node max in `40-65 s` about `0.16 N`.

Post-65 s:

- The true instability/invalidity onset now occurs around `69.5-69.75 s`.
- In `65-75 s`, mean `Delta_F_motion` rises to about `2710 N`, max alpha
  reaches almost `90 deg`, up to `60/101` nodes are clipped, and max strain
  reaches `0.00573`.
- In `75-95.86 s`, mean `Delta_F_motion` is about `12029 N`, max strain reaches
  `0.01463`, and estimated max tension reaches about `669 kN`.
- Drag remains strongly dissipative in the severe-response phase, while lift
  becomes the dominant positive-power term after the onset.

Conclusion:

- The old `58-60 s` abnormal response was largely caused by force-component
  mapping inconsistency.
- After fixing the mapping, the remaining severe response begins later, near
  `69.5 s`, where aerodynamic table extrapolation/clipping, positive lift
  power, and excessive axial strain appear almost together.
- The corrected workflow now has the necessary logs to separate aerodynamic
  energy input from structural invalidity.

### 2026-06-13 Root-cause trace for the `69.5-69.75 s` onset

User observation: the corrected typical run still shows abnormal motion around
`69.5-69.75 s`. We traced all available records upward from the response.

New scripts / outputs:

```text
tools/trace_mapping_fixed_onset_root_cause.py
tools/check_incremental_time_series_alignment.py
tools/extract_onset_element_node_tables.py
```

```text
output/diagnostics/typical_incremental_qs_mapping_fixed_power_strain/analysis/onset_root_cause_69s/onset_root_cause_trace.json
output/diagnostics/typical_incremental_qs_mapping_fixed_power_strain/analysis/onset_root_cause_69s/onset_68p5_70p2_chain.png
output/diagnostics/typical_incremental_qs_mapping_fixed_power_strain/analysis/onset_root_cause_69s/time_series_alignment_check.json
output/diagnostics/typical_incremental_qs_mapping_fixed_power_strain/analysis/onset_root_cause_69s/critical_element_strain_tension_samples.csv
```

Main event order:

| Event | Time |
|---|---:|
| first adaptive time step differs from `0.05 s` | `68.95 s` |
| first estimated total element tension becomes negative | `69.06538461538285 s` |
| first `max_alpha_current_deg > 29.9 deg` / clipping | `69.51330692520463 s` |
| first `Delta_F_motion > 1000 N` | `69.65545123364667 s` |
| first `max_abs_strain > 0.001` | `69.67140672803896 s` |
| first `Delta_F_motion > 1500 N` | `69.68470297336587 s` |
| first `max_abs_strain > 0.002` | `69.69799921869279 s` |
| first `max_abs_strain > rated-strength strain` | `69.7176026573158 s` |
| first `total_delta_power > 10 kW` | `69.74924193572579 s` |

Important root-cause evidence:

- The earliest nonphysical event is not aerodynamic coefficient clipping.
- At `69.06538461538285 s`, many middle-span elements already have negative
  estimated total tension. Elements `41-59` are negative in the same time row.
- Examples from the first negative-tension row:
  - element `41`: strain `-4.5616e-4`, estimated total tension `-0.46 kN`;
  - element `45`: strain `-5.3174e-4`, estimated total tension `-3.82 kN`;
  - element `52`: strain `-5.8233e-4`, estimated total tension `-6.06 kN`.
- The negative-tension region appears before attack-angle table clipping. This
  means the structural model has already entered a cable-invalid state before
  the aerodynamic high-angle runaway.
- Around `69.45 s`, elements `44-45` are already negative tension:
  - element `44`: estimated total tension `-1.18 kN`;
  - element `45`: estimated total tension `-1.92 kN`.
- The same local group then flips rapidly:
  - at `69.60 s`, elements `42-45` carry about `47-51 kN`;
  - at `69.65 s`, elements `42-45` are again negative, down to about
    `-18.9 kN`;
  - at `69.70 s`, element `42` jumps to about `132.3 kN`, near/exceeding rated
    strength;
  - at `69.75 s`, several elements become strongly negative again, e.g.
    element `46` about `-117.9 kN`.

Interpretation:

- The current `forceBeamColumn` fiber-section model permits axial compression,
  bending, and slack-like sign changes. A real overhead cable cannot carry
  sustained compression; it should go slack/tension-only or be constrained by a
  cable/inextensible formulation.
- Therefore the root event for the `69.5-69.75 s` abnormal response is most
  likely structural-model invalidity: a middle-span region loses positive
  tension and then snaps between compression-like and high-tension states.
- Aerodynamic high angle, large `Delta_F_motion`, and positive lift-power
  bursts are later consequences/amplifiers of this invalid structural state,
  not the first cause.

Additional bug found and fixed:

- `get_incremental_time_series_component` in
  `tcl_procedures/Damping_shifter.tcl` used
  `currentTime / STKO_VAR_time_increment` to index force/wind files.
- `STKO_VAR_time_increment` is adaptive, while force/wind files are sampled on
  the fixed wind time vector (`dt = 0.05 s`). Once the solver reduced the time
  step after `68.95 s`, this caused real-time QS wind/reference-force reads to
  de-synchronize from the OpenSees Path load.
- Numerical alignment check:
  - before adaptive stepping (`40, 58, 65 s`), logged and correct reference
    force matched nearly exactly;
  - at `69.513 s`, logged `F_reference` was about `483.6 N` while correct
    fixed-time reference was about `515.7 N`;
  - at `69.655 s`, logged `F_reference` was about `692.2 N` while correct
    reference was about `529.7 N`.
- Fix applied on `2026-06-13`: always interpolate force/wind histories using
  the original `time` vector; do not use adaptive solver increment as file dt.

Verification after the fix:

```text
pytest tests/test_tcl_writer.py -q
```

passed: `10 passed`.

Required next modelling correction:

- Replace or augment the beam-column cable representation with a tension-only /
  cable-appropriate axial behavior, or add a physical invalidity/failure
  criterion at zero/low tension before interpreting galloping after this point.
- Rerun the corrected real-time QS branch after the time-alignment fix and
  tension-valid cable treatment. Until then, post-`69 s` results are diagnostic
  evidence of structural-model breakdown, not reliable galloping physics.

### 2026-06-13 Tension-only cable correction and 72 s verification

User decision: the cable model must not carry compression. It should behave as
a tension-only cable, with slack/zero tension replacing the previous
compression-like negative-tension state.

OpenSees material/element probes:

```text
tools/opensees_tension_only_probe.tcl
tools/opensees_tension_material_behavior_probe.tcl
tools/opensees_corot_truss_6dof_probe.tcl
tools/opensees_tension_only_initstrain_probe.tcl
```

Probe conclusions:

- `ENT` in OpenSees is not suitable here because it behaves in the
  compression-only direction for the sign convention tested.
- `ElasticPPGap` with positive `Fy` and `gap = 0.0` gives the required
  tension-only response: positive extension carries force, compression gives
  zero force.
- `InitStrainMaterial` wrapping `ElasticPPGap` preserves the cable pretension
  while still preventing negative compression after sufficient shortening.
- `corotTruss` works in the active `model basic -ndm 3 -ndf 6` setting when all
  nodal rotational DOFs are fixed. This is appropriate for a cable-like member
  whose governing structural action is axial tension, not bending stiffness.

Implemented model branch:

- `analysis.fiber_section = 2` now selects a tension-only cable branch in
  `src/cable_analyser/tcl_writer.py`.
- Element formulation:

```tcl
uniaxialMaterial ElasticPPGap 1 E Fy 0.0
uniaxialMaterial InitStrainMaterial 10 1 eps0
element corotTruss ele i j Area 10
```

- Internal node rotational DOFs are fixed: `fix node 0 0 0 1 1 1`.
- End nodes remain fully fixed.
- Rotational masses are set to zero for this cable-only branch.
- `analysis.assume_initial_equilibrium = true` was added for this diagnostic
  branch. The given catenary/parabolic geometry plus pretension/self-weight
  design is treated as the already formed initial equilibrium state. This avoids
  the nonphysical intermediate load path where full initial strain is combined
  with partial gravity and the tension-only cable can become singular.

Diagnostic/logging corrections:

- `inputs_aerodynamic_damping.tcl` now writes `element_tension_only`.
- `log_element_strain_tension` now records both:
  - `raw_elastic_tension_N`: what the old linear axial estimate would have
    reported;
  - `estimated_total_tension_N`: the tension-only estimate actually used for
    validity checks, clamped to zero when the raw estimate is negative.
- The summary log now includes `min_estimated_tension_N` and
  `slack_element_count`.
- `readColumnFromFile.tcl` now skips blank/missing fields.
- `interpolate.tcl` was replaced with a standard robust linear interpolation
  implementation. The old version failed at the first time point because it
  decremented the index to `-1`.

Verification commands:

```text
pytest tests/test_tcl_writer.py -q
```

passed: `12 passed`.

Tension-only diagnostic configuration:

```text
tools/prepare_typical_incremental_qs_tension_only_config.py
output/diagnostics/typical_incremental_qs_tension_only/typical_L322P8_H10P48_U0P6_incremental_qs_tension_only_90s.yaml
```

The final verification run used `dt = 0.05 s`, `npt = 1440` (`72 s`) and wrote
to:

```text
output/diagnostics/typical_incremental_qs_tension_only/run_v7_72s
```

OpenSees status:

```text
STATUS success
MESSAGE target_time_reached
TIME 72.0
TARGET_TIME 72.0000
PROGRESS 100.0
ANALYZE_RETURN_CODE 0
```

Tension-only summary:

```text
output/diagnostics/typical_incremental_qs_tension_only/run_v7_72s/tension_only_summary/tension_only_run_summary.json
output/diagnostics/typical_incremental_qs_tension_only/run_v7_72s/tension_only_summary/tension_only_tension_slack_summary.png
output/diagnostics/typical_incremental_qs_tension_only/run_v7_72s/tension_only_summary/tension_only_force_power_alpha_summary.png
```

Key numerical findings:

- `estimated_total_tension_N` has no negative rows.
- Raw linear-elastic tension has `5` negative rows, all in element `5` between
  about `4.08-4.38 s`; the tension-only estimate correctly clamps these to
  `0 N`, marking slack rather than compression.
- After `69 s`, there is no slack:
  - `min_estimated_tension_after_69s_N = 764346.53 N`;
  - `slack_log_count_after_69s = 0`.
- At the end of the logged tension summary (`71.8444 s`):
  - max estimated tension is about `17.19 MN`;
  - max absolute strain is about `0.3868`.

Three-point monitoring outputs:

```text
output/diagnostics/typical_incremental_qs_tension_only/run_v7_72s/point_monitoring
```

Key point-response values:

- 1/4 span node `26`: max transverse displacement `57.90 m`, max vertical
  displacement `4.45 m`.
- Midspan node `51`: max transverse displacement `73.76 m`, max vertical
  displacement `4.89 m`.
- 3/4 span node `76`: max transverse displacement `52.61 m`, max vertical
  displacement `4.31 m`.
- Coefficient lookup clipping fraction is `0.0` at all three monitored points.

Interpretation:

- The original negative-tension/structural-compression defect is solved for the
  corrected tension-only branch. The model now represents compression demand as
  zero-tension slack rather than a physically impossible compressive cable.
- The severe response is not removed. It now appears as a very large
  tension-only galloping-type response with large axial strain and very high
  tension. Therefore the next modelling question is no longer "why does the
  cable carry negative tension?" but "why does the corrected tension-only
  aeroelastic system still develop unrealistically large transverse response and
  axial strain?"
- Before interpreting late-time amplitudes as realistic engineering galloping,
  the next checks should address axial extensibility/inextensibility,
  pretension/sag consistency, force distribution under large displacement, and
  whether a physical failure/validity limit should be applied when strain or
  tension exceeds conductor capacity.

### 2026-06-13 Permanent original-model reference and three-version audit

Purpose: before further interpretation of the tension-only result, we audited
the current workflow against the original Timur MATLAB/OpenSees model and
compared the last three typical-case branches.

Permanent original-model reference for future audits:

```text
Original project root:
D:\Uob\Tower Pylon\TIMUR2

Original wind/force generator:
D:\Uob\Tower Pylon\TIMUR2\WIND_SIMULATION.mlx

Original generated OpenSees Tcl:
D:\Uob\Tower Pylon\TIMUR2\Input.tcl

Original structure/time-history generators:
D:\Uob\Tower Pylon\TIMUR2\MODAL.m
D:\Uob\Tower Pylon\TIMUR2\TH_Updating.m
D:\Uob\Tower Pylon\TIMUR2\CABLE_ANALYSER_Updating.m

Original aerodynamic damping Tcl:
D:\Uob\Tower Pylon\TIMUR2\Damping_shifter.tcl

Original FORCE_3/SIM1 force and wind histories:
D:\Uob\Tower Pylon\TIMUR2\FORCES_UPDATING_COEFFS\FORCE_3\SIM1
```

Original generated model facts from `Input.tcl`:

- `101` nodes.
- `100` `forceBeamColumn` elements.
- No `corotTruss` / no `ElasticPPGap`.
- `404` Path time series, i.e. four force components for each node.
- Path-load convention:
  - `H_drag` -> OpenSees DOF 2, factor `1000`;
  - `H_lift` -> OpenSees DOF 3, factor `1000`;
  - `V_drag` -> OpenSees DOF 3, factor `1000`;
  - `V_lift` -> OpenSees DOF 2, factor `1000`.
- Original Rayleigh line in the generated Tcl:
  `rayleigh 0.002429 0 0.036669 0`.
- Original `CABLE_ANALYSER_Updating.m` uses `E = 82 GPa` and
  `Pretention_load = 0`; current research typical configs use Zebra ACSR
  `E = 69 GPa` and `pretension_load = 19.785 kN`.

Audit outputs:

```text
tools/audit_model_updates_against_original.py
output/diagnostics/model_update_audit/original_model_reference.json
output/diagnostics/model_update_audit/three_version_comparison.csv
output/diagnostics/model_update_audit/three_version_comparison.json
output/diagnostics/model_update_audit/model_update_audit_report.md
output/diagnostics/model_update_audit/midspan_response_three_versions.png
output/diagnostics/model_update_audit/incremental_force_three_versions.png
```

Three compared branches:

1. `typical_incremental_quasi_steady_formal_no_stop/run`
   - Incremental QS branch before the later force-component mapping fix.
   - Uses `forceBeamColumn`.
2. `typical_incremental_qs_mapping_fixed_power_strain/run`
   - Path-load force-component convention fixed.
   - Still uses `forceBeamColumn`.
   - Adds node power and element strain/tension logs.
3. `typical_incremental_qs_tension_only/run_v7_72s`
   - Uses corrected incremental QS force convention.
   - Uses `corotTruss + ElasticPPGap + InitStrainMaterial`.
   - Uses `assume_initial_equilibrium=true` and a `72 s` target.

Numerical comparison:

| Version | Status | End time | Max global disp | Max global vel | Max global accel | Max total abs Delta F | Tension after 69 s |
|---|---:|---:|---:|---:|---:|---:|---|
| V1 pre mapping-fix | failed `-3` | `86.434 s` | `6.323 m` | `65.59 m/s` | `4.71e4 m/s2` | `1.142e4 N` | not logged |
| V2 mapping-fixed beam | status file not recorded | `95.859 s` | `11.40 m` | `140.2 m/s` | `6.23e4 m/s2` | `2.448e4 N` | negative tension after 69 s; min about `-440.6 kN`; `42474` negative rows |
| V3 tension-only | success | `72.0 s` | `73.76 m` | `4.317 m/s` | `1089.75 m/s2` | `413 N` | no negative estimated tension; min after 69 s about `764.3 kN`; slack after 69 s `0` |

Interpretation of the three recent major changes:

- Damping application change:
  - Necessary. Original/update-style `setElementRayleighDampingFactors` changes
    element damping after a step and does not itself put a physically explicit
    velocity-dependent aerodynamic force into the current time-step equation.
  - Current branch keeps `adapt_damp` as a recorder only:
    `damping_writeback_mode = record_only`.
  - Structural damping remains through global Rayleigh damping; aeroelastic
    feedback enters through explicit/incremental force.
- Force-superposition change:
  - Necessary. Full real-time QS replacement can remove or double-count the
    precomputed weather scenario.
  - Adopted form:
    `F_total = F_path + [F_current - F_reference]`.
  - This preserves the original `FORCE_3/SIM1` Path load and adds only the
    motion-induced correction.
- Force-component mapping correction:
  - Necessary. Original Path loads use `Fy = H_drag + V_lift` and
    `Fz = H_lift + V_drag`; the corrected branch matches this convention.
- Tension-only element:
  - Necessary. V2 proves that the beam-column cable branch enters physically
    invalid negative tension after `69 s`.
  - V3 removes negative estimated tension and represents compression demand as
    slack/zero tension.

Important caveats / possible workflow issues found:

- V3 is mechanically more correct for cable axial behavior, but its late
  amplitude and strain are not automatically realistic.
- V3 uses `assume_initial_equilibrium=true` to avoid the singular partial-gravity
  load path of the tension-only cable. This is defensible only if the initial
  geometry, pretension, and self-weight are already a consistent found shape.
  Because `loadConst -time 0.0` follows a skipped static analysis, gravity-load
  equivalence to the original workflow must be explicitly revalidated.
- Current research typical configs differ from the original Timur input in at
  least material modulus, pretension, and Rayleigh damping formulation. These
  differences may be justified by the current Zebra ACSR design basis, but they
  are not part of the three recent galloping-mechanism fixes and should be
  either documented as intentional research assumptions or matched in a separate
  parameter-controlled audit.

Current scientific conclusion:

- V1 and V2 are less reliable for final galloping interpretation:
  - V1 has force-transfer issues and fails;
  - V2 has corrected force transfer but structurally invalid negative cable
    tension.
- V3 is the best current branch for the galloping mechanism because it preserves
  the weather scenario, applies motion-induced aerodynamic feedback explicitly,
  and prevents nonphysical cable compression.
- V3 is not yet final for quantitative engineering amplitude prediction until
  the gravity/initial-equilibrium and parameter-matching caveats above are
  resolved.

### 2026-06-13 Clarification: Rayleigh damping, gravity/mass, pretension, and late large response

Rayleigh / effective damping clarification:

- Rayleigh damping in the OpenSees model is the numerical representation of
  structural/basic damping, usually written `C_s = alpha_M M + beta_K K`.
- It is not the aerodynamic galloping damping itself. It is a way to realise a
  target structural damping ratio, e.g. `xi_structural = 0.01`.
- Aerodynamic galloping feedback should enter as an additional aerodynamic
  force or aerodynamic damping contribution derived from relative wind and
  aerodynamic coefficients.
- Therefore the physical total effective damping indicator is:
  `xi_eff = xi_structural + xi_aero`.
- No duplication occurs if:
  - `xi_structural` is represented once by global Rayleigh damping; and
  - `xi_aero` enters through the explicit/incremental aerodynamic force.
- Duplication would occur if global Rayleigh already represents structural
  damping and the aerodynamic force branch also adds another structural
  `-2 xi_structural omega M v` term, or if element damping writeback uses
  `xi_total = xi_structural + xi_aero` while global Rayleigh structural damping
  is still active.
- Current tension-only run `run_v7_72s`:
  - global Rayleigh line: `rayleigh 0.001404 0 0 0`;
  - `damping_writeback_mode = record_only`;
  - `adapt_damp` records `xi_eff` but does not call
    `setElementRayleighDampingFactors`;
  - aerodynamic feedback enters through `apply_incremental_quasi_steady_aero_force`.
  This means structural damping and aerodynamic force are not intentionally
  double-counted in the current branch.

Gravity and mass audit for `run_v7_72s`:

- Current generated `Input.tcl` contains `101` nodal mass definitions.
- Total translational mass in each direction:
  `524.839426 kg`.
- The gravity pattern `pattern Plain 200000 10000` contains `101` nodal loads.
- Sum of gravity loads:
  `-5146.916591 N`.
- `M*g = -524.839426 * 9.80665 = -5146.916557 N`.
- Difference is only about `3.4e-05 N`, i.e. rounding error.
- Therefore mass and gravity are written consistently.
- However, because `analysis.assume_initial_equilibrium=true` skips the static
  gravity solve, this only proves gravity is present as a load pattern. It does
  not prove OpenSees has solved the initial static equilibrium. A separate
  no-wind/no-aero gravity-equilibrium control is still needed.

Pretension audit:

- Original `D:\Uob\Tower Pylon\TIMUR2\CABLE_ANALYSER_Updating.m` has:
  `Pretention_load = 0.*10000`, so original generated `Input.tcl` writes
  `InitStrainMaterial ... 0.000000`.
- Therefore the original Timur updating model did not apply explicit initial
  pretension.
- Current research typical config uses `pretension_load = 19785 N`.
- This value matches the parabolic horizontal tension estimate
  `T_H = w L^2 / (8 Sag)` with `w = 15.9 N/m`, `L = 322.8 m`,
  `Sag = 10.48 m`.
- Interpretation: current pretension is an engineering/found-shape assumption,
  not an original MATLAB default.
- If we decide to follow the original model strictly, pretension should be
  removed and tension should arise from a validated gravity/form-finding step.
  For a tension-only cable, that requires a robust cable form-finding or
  initial-stress procedure, not the previous partial-gravity load ramp from zero
  tension.

Late large response audit for `run_v7_72s`:

- From `60-72 s`, monitored displacement becomes very large while velocities
  and accelerations are not as explosively high as the previous beam-column
  failure branch:
  - midspan max transverse displacement in `60-72 s`: about `73.76 m`;
  - midspan max speed in `60-72 s`: about `2.59 m/s`;
  - midspan max acceleration in `60-72 s`: about `6.58 m/s2`.
- Force correction does not explode:
  - `max total_abs_delta_force` after `69 s`: about `413 N`;
  - `max_alpha_current_deg` after `69 s`: about `13 deg`;
  - coefficient clipping count after `69 s`: `0`.
- Tension/strain are the concerning quantities:
  - max tension rises from about `16.18 MN` in `60-69 s` to about `17.19 MN`
    in `69-72 s`;
  - max axial strain rises to about `0.3868`;
  - no negative tension and no slack after `69 s`.
- Damping indicator remains strongly negative over many elements:
  - effective damping log in `69-72 s` has min about `-15.33`, mean about
    `-8.50`, max about `0.30`.
- Interpretation: the post-69 s branch is no longer the previous negative
  tension failure. It is a large-displacement/large-strain response of a very
  extensible tension-only truss chain under persistent negative aerodynamic
  damping indicators. The main unresolved issue is whether the axial
  extensibility/initial-equilibrium assumptions allow unphysical stretching.

Immediate required checks:

1. Run no-wind/no-aero controls with the tension-only branch:
   - gravity on/off;
   - pretension on/off or found-shape pretension;
   - record support reactions, acceleration, displacement, and element tension.
2. Add both support reactions, not just node 1, to verify total vertical
   equilibrium.
3. Decide whether `pretension_load = 19785 N` is a fixed engineering
   found-shape condition or should be replaced by gravity-generated tension.
4. If keeping engineering pretension, verify the initial internal axial forces
   balance self-weight for the chosen geometry before dynamic wind is applied.
5. Add conductor validity/failure checks: strain and tension should not be
   interpreted beyond rated strength or realistic cable extensibility.

### 2026-06-13 No-wind tension-only control verification

Purpose: isolate whether the abnormal large response is caused by aerodynamic
work input, initial-equilibrium release, gravity/pretension handling, or axial
over-flexibility before interpreting the windy typical case as true galloping.

Implementation updates:

- `src/cable_analyser/tcl_writer.py` now records both end-support reactions in
  `SupportReactions.out` for time-history analyses, while keeping the original
  left-support `Reaction.out` for compatibility.
- Control config generator:
  `tools/prepare_tension_only_control_verification_configs.py`.
- Control postprocessor:
  `tools/analyse_tension_only_control_verification.py`.
- Output root:
  `output/diagnostics/tension_only_control_verification`.
- Summary report:
  `output/diagnostics/tension_only_control_verification/report/control_verification_report.md`.
- Figures:
  `output/diagnostics/tension_only_control_verification/report/control_verification_summary.png`
  and
  `output/diagnostics/tension_only_control_verification/report/control_midspan_vertical_histories.png`.

Control cases:

| Case | Wind/aero | Gravity | Pretension | Initial path | Result |
|---|---|---:|---:|---|---|
| C1 | off | on | `19785 N` | `assume_initial_equilibrium=true` | completed 30 s |
| C2 | off | on | `0 N` | static gravity attempt | failed at first static increment |
| C3 | off | off | `19785 N` | `assume_initial_equilibrium=true` | completed 30 s |

Key numerical results:

- C1 and C3 are numerically identical:
  - `max_xz_disp_m = 0.294474`;
  - `max_kinetic_energy_J = 0.0260523`;
  - `max_abs_strain = 1.65247e-4`;
  - `min_estimated_tension_N = 12449.8`;
  - `max_abs_total_support_Rz_N = 21.4374`.
- C1 expected total self-weight is about `5146.9 N`, but the recorded
  two-support vertical reaction sum reaches only about `21 N` and returns to
  `0 N`.
- Therefore the current `assume_initial_equilibrium=true` branch does **not**
  apply/freeze gravity at load factor 1.0. It skips the static solve and then
  calls `loadConst -time 0.0` while the gravity pattern uses a `Linear`
  timeSeries, so the effective gravity factor is consistent with being frozen
  at zero.
- C2 fails at the first static increment with OpenSees:
  `FullGenLinLapackSolver::solve() - factorization failed, matrix singular`,
  followed by `StaticAnalysis::analyze() ... returned: -3 error flag`.
  Interpretation: a zero-pretension tension-only chain cannot self-form under
  gravity from the current zero-stress state using the existing static load
  path.

Research correctness conclusion:

- The no-wind/no-aero response in C1/C3 is an initial pretension/geometry
  release, not aerodynamic galloping.
- The latest windy large-strain response cannot yet be interpreted as a pure
  galloping result because the formal initial state is not a verified
  gravity-plus-tension equilibrium.
- The correct next model update is not to tune forces down. It is to establish
  a scientifically valid initial state:
  1. either perform a robust static/form-finding step for the tension-only
     cable; or
  2. explicitly construct a consistent initial stress/strain state from the
     selected sag/self-weight/target horizontal tension and verify it through
     support reactions and no-wind free-response stability.
- Acceptance before further galloping interpretation:
  - C1 support reactions approximately balance self-weight;
  - residual velocity and global kinetic energy remain small and decaying;
  - no large drift under no-wind/no-aero;
  - no slack elements;
  - axial strain remains within a physically plausible conductor range.

### 2026-06-13 Bidirectional axial rollback test of the third correction

Purpose:

- The user noted that some literature and special modelling situations may
  permit local negative axial force / negative tension as an effective local
  state. Therefore the previous tension-only assumption should be tested rather
  than treated as an unquestioned truth.
- We performed a controlled rollback of the third correction only: keep the
  corrected aerodynamic-force treatment, keep damping as diagnostic /
  record-only, keep the C4 static gravity equilibrium route, but change the
  structural element branch from tension-only `corotTruss + ElasticPPGap +
  InitStrainMaterial` back to the bidirectional axial `forceBeamColumn +
  Elastic + InitStrainMaterial` branch.

Code and configuration:

- Added:

```text
tools/prepare_typical_incremental_qs_c4_bidirectional_axial_config.py
tools/analyse_c4_bidirectional_axial_comparison.py
```

- Generated config:

```text
output/diagnostics/typical_incremental_qs_c4_bidirectional_axial/typical_L322P8_H10P48_U0P6_incremental_qs_c4_bidirectional_axial_72s.yaml
```

- Output directory:

```text
output/diagnostics/typical_incremental_qs_c4_bidirectional_axial/run
```

- Comparison directory:

```text
output/diagnostics/typical_incremental_qs_c4_bidirectional_axial/comparison
```

Run status:

- OpenSees 3.8.0 completed the 72 s target duration successfully.
- `analysis_status.txt` reports:

```text
STATUS success
MESSAGE target_time_reached
TIME 72.0
ANALYZE_RETURN_CODE 0
```

Key comparison against the C4 tension-only branch:

| quantity | C4 tension-only | C4 bidirectional axial |
|---|---:|---:|
| max x-z displacement | `0.1897 m` | `1.3800 m` |
| max x-z velocity | `0.3346 m/s` | `12.3582 m/s` |
| max x-z acceleration | `73.81 m/s2` | `6157.92 m/s2` |
| minimum estimated tension | `18.69 kN` | `-20.35 kN` |
| first logged negative tension | none | `69.861 s` |
| max absolute tension | `21.00 kN` | `65.10 kN` |
| max absolute strain | `2.73e-5` | `1.02e-3` |
| max total absolute incremental QS force | `135.74 N` | `1469.20 N` |
| max attack angle in force log | `14.79 deg` | `62.73 deg` |
| maximum clipped node count | `0` | `8` |

Interpretation:

- Before about `68-69 s`, the tension-only and bidirectional-axial branches
  are almost identical in tension, strain, monitored displacement, and force
  history. This confirms that the corrected damping, force superposition, and
  C4 gravity route are still active and comparable.
- The bidirectional branch first logs negative tension at about `69.861 s`.
  After that point, it develops much larger vertical displacement, velocity,
  acceleration, strain, incremental aerodynamic force, and attack angle. The
  force table also begins to clip attack angles.
- Therefore the rollback does not make the response obviously more benign or
  more stable. It demonstrates that allowing local negative axial force is a
  modelling choice with major post-onset consequences.

Current research conclusion:

- We should no longer state absolutely that any negative tension is impossible
  or automatically invalid in every modelling context.
- For this OpenSees workflow, however, allowing negative axial force in the
  beam-column branch strongly changes the post-`69 s` response and can push
  the aerodynamic calculation into larger-angle / clipped-coefficient regimes.
- The correct next stance is comparative rather than dogmatic:
  - use the tension-only branch when representing a physical overhead
    conductor that cannot carry sustained compression;
  - use the bidirectional axial branch as a sensitivity / alternative modelling
    hypothesis, especially if a cited formulation intentionally treats local
    negative axial force as an effective linearized state;
  - report both only with a clear note that post-negative-tension response is
    sensitive to the structural element assumption and should not be mixed with
    the tension-only physical interpretation.

### 2026-06-14 200 s extension attempt for structural-model comparison

Purpose:

- Extend the latest typical C4 incremental-QS case from 72 s to 200 s for both
  structural assumptions:
  1. tension-only `corotTruss + ElasticPPGap + InitStrainMaterial`;
  2. bidirectional axial `forceBeamColumn + Elastic + InitStrainMaterial`.
- Keep the same wind case, same C4 static gravity equilibrium route, same
  record-only damping diagnostics, and same incremental QS aerodynamic force
  formulation.

Code and configuration:

```text
tools/prepare_c4_200s_structural_model_comparison_configs.py
tools/analyse_c4_200s_structural_model_comparison.py
```

Generated configs:

```text
output/diagnostics/c4_structural_model_comparison_200s/tension_only/tension_only.yaml
output/diagnostics/c4_structural_model_comparison_200s/bidirectional_axial/bidirectional_axial.yaml
```

Outputs:

```text
output/diagnostics/c4_structural_model_comparison_200s/tension_only/run
output/diagnostics/c4_structural_model_comparison_200s/bidirectional_axial/run
output/diagnostics/c4_structural_model_comparison_200s/comparison
```

Important execution note:

- Neither model completed the requested 200 s target.
- The tension-only model did not naturally fail inside OpenSees, but after a
  two-hour external execution window it had only advanced to about `129.43 s`.
  Because the process was externally terminated, `analysis_status.txt` is
  missing for that run. The available time histories are valid only up to the
  last recorded time.
- The bidirectional axial model naturally failed in OpenSees at
  `108.05175076831534 s`, with:

```text
STATUS failed
MESSAGE analysis_did_not_converge_min_factor_reached
ANALYZE_RETURN_CODE -3
FACTOR 6.657041767889234e-10
MIN_FACTOR 1e-06
```

Key partial-result summary:

| quantity | tension-only, partial to `129.43 s` | bidirectional axial, failed at `108.05 s` |
|---|---:|---:|
| max x-z displacement | `6.264 m` | `9.475 m` |
| max x-z velocity | `42.46 m/s` | `211.72 m/s` |
| max x-z acceleration | `25202.63 m/s2` | `130912.01 m/s2` |
| minimum estimated tension | `0.0 kN` | `-390.11 kN` |
| negative tension rows | `0` | `763` |
| max absolute tension | `934.63 kN` | `952.13 kN` |
| max absolute strain | `0.03817` | `0.02100` |
| max total absolute incremental QS force | `3547 N` | `36956 N` |
| max attack angle | about `90 deg` | about `90 deg` |
| max clipped node count | `56` | `54` |
| max / min total delta power | `+20.9 / -19.7 kW` | `+349 / -875 kW` |

Interpretation:

- The 72 s comparison did not reveal the full long-time behavior. Extending the
  target duration shows that both structural assumptions eventually leave the
  small-angle / validated-aerodynamic range under the current wind input.
- The bidirectional axial branch destabilizes earlier: negative tension begins
  after about `69.86 s`, the vertical displacement drifts upward, aerodynamic
  force and power spike, and OpenSees fails at about `108.05 s`.
- The tension-only branch delays the large response until about `90 s`, then
  develops slack elements and large high-frequency axial/tension oscillations.
  It did not naturally fail before the external runtime limit, but it also did
  not remain in a physically comfortable regime. At the last recorded state
  around `129.43 s`, midspan vertical displacement is about `6.23 m`, max
  strain has reached about `3.8%`, and the force table is frequently clipped.
- Therefore the 200 s extension should not be treated as a successful 200 s
  simulation. It should be treated as a long-time stability/validity test
  showing that the current typical case enters a post-validity large-response
  regime before 200 s.

Research implication:

- For future formal sweeps, we need explicit reporting of:
  - achieved simulation time;
  - OpenSees natural failure code or external timeout;
  - first large-angle/clipping time;
  - first slack or negative-tension time;
  - first strain/tension validity-limit crossing.
- We should not interpret post-clipping large-angle response as calibrated
  galloping physics unless the aerodynamic coefficient model is extended to
  large attack angles and the structural formulation is validated for the
  observed strain/slack/negative-tension range.

### 2026-06-14 Abnormal-onset tracing for the 200 s extension

Purpose:

- Read the 200 s extension outputs parameter by parameter and identify which
  observable first enters an abnormal-response state.
- Separate the physical/numerical onset sequence from the final solver outcome.

Additional analysis script:

```text
tools/trace_c4_200s_abnormal_onset.py
```

Output:

```text
output/diagnostics/c4_structural_model_comparison_200s/comparison/abnormal_onset/abnormal_onset_summary.json
output/diagnostics/c4_structural_model_comparison_200s/comparison/abnormal_onset/tension_only_abnormal_onset.md
output/diagnostics/c4_structural_model_comparison_200s/comparison/abnormal_onset/bidirectional_axial_abnormal_onset.md
```

Tension-only event order:

| event | first time |
|---|---:|
| acceleration exceeds `100 m/s2` | `88.350 s` |
| velocity exceeds `1 m/s` | `89.350 s` |
| first slack element | `89.736640 s` |
| max strain exceeds `0.001` | `89.736640 s` |
| total incremental QS force exceeds `500 N` | `89.867828 s` |
| velocity exceeds `5 m/s` | `90.010400 s` |
| max strain exceeds `0.005` | `90.089155 s` |
| max strain exceeds `0.01` | `90.155116 s` |
| max absolute tension exceeds `100 kN` and `500 kN` | `90.155116 s` |
| total incremental QS force exceeds `1000 N` | `90.215278 s` |
| displacement exceeds `0.5 m` | `90.274100 s` |
| attack angle exceeds `30 deg` and clipping begins | `90.455775 s` |
| displacement exceeds `1 m` | `90.486500 s` |
| displacement exceeds `2 m` | `90.779000 s` |
| attack angle exceeds `60 deg` | `91.359154 s` |
| total delta power exceeds `10 kW` | `100.196864 s` |

Tension-only interpretation:

- The first flagged abnormal parameter is acceleration at `88.35 s`, followed
  by velocity growth.
- The first structural-validity event is slack at `89.736640 s`, initially in
  elements around the midspan region (`50-52`) and later other local regions.
- Aerodynamic large-angle/clipping occurs after the structural/dynamic onset,
  not before it.
- Solver status is missing because the run was externally terminated after a
  two-hour runtime window at about `129.43 s`; this is not an OpenSees natural
  failure. However, by then the case is already outside the validated
  small-angle / no-slack interpretation range.

Bidirectional axial event order:

| event | first time |
|---|---:|
| acceleration exceeds `100 m/s2` | `68.300 s` |
| velocity exceeds `1 m/s` | `68.650 s` |
| total incremental QS force exceeds `500 N` | `69.518950 s` |
| attack-angle clipping begins | `69.518950 s` |
| node delta power exceeds `100 W` | `69.518950 s` |
| velocity exceeds `5 m/s` | `69.571400 s` |
| displacement exceeds `0.5 m` | `69.732700 s` |
| first negative element tension | `69.861189 s` |
| attack angle exceeds `30 deg` and `60 deg` | `70.170455 s` |
| total incremental QS force exceeds `1000 N` | `70.501756 s` |
| max strain exceeds `0.001` | `70.518784 s` |
| displacement exceeds `1 m` | `70.518800 s` |
| total delta power exceeds `1000 W` | `71.399952 s` |
| displacement exceeds `2 m` | `72.520000 s` |
| max absolute tension exceeds `100 kN` | `92.701329 s` |
| total delta power exceeds `10 kW` | `97.406480 s` |
| max strain exceeds `0.005` | `104.925084 s` |
| max strain exceeds `0.01` | `107.739246 s` |
| max absolute tension exceeds `500 kN` | `107.811040 s` |

Bidirectional axial interpretation:

- The first flagged abnormal parameter is again acceleration, but about
  `20 s` earlier than in the tension-only branch.
- Large aerodynamic correction and coefficient clipping begin at
  `69.518950 s`, slightly before the first logged negative tension at
  `69.861189 s`.
- First negative-tension rows include elements `33`, `34`, `44`, `54`, and
  `55`, with estimated tension down to about `-5.72 kN` at first onset.
- The final OpenSees failure at `108.051750768 s` is a numerical convergence
  failure in a highly nonlinear state, not a project-side active stop:

```text
CTestNormDispIncr failed after 100 iterations
DirectIntegrationAnalysis::analyze() failed at time 108.052
OpenSees analyze returned -3
increment factor reduced to 6.657e-10, below minimum 1e-06
```

Overall root-cause reading:

- In both branches, acceleration/velocity growth appears before gross
  displacement thresholds.
- In the bidirectional branch, aerodynamic large-angle/clipping and force
  amplification precede the first recorded negative-tension row by a fraction
  of a second, then negative tension strongly amplifies the nonlinear response.
- In the tension-only branch, slack and strain growth precede aerodynamic
  clipping; the branch avoids negative tension but later enters a severe
  slack/large-strain regime.
- Therefore the earliest abnormal indicator is dynamic response amplification
  (acceleration), while the earliest model-validity indicators differ by
  branch:
  - tension-only: slack + strain onset at about `89.74 s`;
  - bidirectional axial: aerodynamic clipping/force growth at about
    `69.52 s`, followed by negative tension at about `69.86 s`.

### 2026-06-14 Focused tension-only failure-mechanism audit

Purpose:

- After the 200 s extension, focus only on the tension-only branch and identify
  how its late failure mechanism develops.
- Key question: if negative tension is prevented, why does the model still
  enter a large-response/slack/large-strain regime?

Additional analysis script:

```text
tools/diagnose_tension_only_failure_mechanism.py
```

Output:

```text
output/diagnostics/c4_structural_model_comparison_200s/comparison/tension_only_failure_mechanism/tension_only_failure_mechanism_summary.json
output/diagnostics/c4_structural_model_comparison_200s/comparison/tension_only_failure_mechanism/tension_only_86_94_onset_chain.png
```

Windowed state:

| window | max disp | max vel | max acc | min tension | max slack | max strain | max alpha | clipped |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `86-88 s` | `0.092 m` | `0.378 m/s` | `99.56 m/s2` | `16.76 kN` | `0` | `6.82e-5` | `10.70 deg` | `0` |
| `88-91 s` | `2.872 m` | `36.83 m/s` | `25202 m/s2` | `0` | `43` | `0.0323` | `46.79 deg` | `3` |
| `91-96 s` | `5.687 m` | `38.97 m/s` | `25202 m/s2` | `0` | `52` | `0.0379` | `89.87 deg` | `27` |
| `110-130 s` | `6.264 m` | `42.46 m/s` | `25203 m/s2` | `0` | `51` | `0.0356` | `89.99 deg` | `56` |

Detailed onset sequence:

- `88.35 s`: first acceleration threshold crossing. The largest x-z
  acceleration is at node `40`, about `102.6 m/s2`, while displacement and
  velocity are still small (`z` displacement about `0.021 m`, velocity about
  `0.21 m/s`). This is best interpreted as a high-frequency dynamic warning,
  not the macro failure itself.
- `89.736640 s`: first slack event. It occurs near midspan:
  - element `50`: strain `-0.003380`, raw elastic tension demand
    `-130.27 kN`, tension-only estimate clamped to `0`;
  - element `51`: strain `-0.003690`, raw elastic tension demand
    `-144.01 kN`, clamped to `0`;
  - element `52`: strain `-0.000492`, raw elastic tension demand
    `-2.06 kN`, clamped to `0`.
- At the same first-slack instant, neighboring elements around the midspan
  have very low positive remaining tension (`~1.4-5.2 kN`), so the local
  structural tangent is already close to a slack mechanism.
- `89.867828 s`: total incremental QS force exceeds `500 N`.
- `90.215278 s`: total incremental QS force exceeds `1000 N`.
- `90.455775 s`: attack-angle clipping begins and total delta power exceeds
  `1000 W`.
- `91.359154 s`: attack angle exceeds `60 deg`.

Mechanism interpretation:

- The tension-only model does not fail through negative tension. Instead, the
  local midspan region demands compression/shortening under dynamic motion.
  The tension-only material correctly prevents compressive cable force by
  setting the affected element force to zero, but this also removes local
  axial stiffness.
- Once several neighboring elements go slack or near-slack, the structural
  system develops a local mechanism. This produces a sudden jump in velocity
  and acceleration, which then increases relative wind speed and attack angle
  in the incremental QS force calculation.
- The aerodynamic model is not the earliest abnormal source in this branch:
  before `88 s`, alpha is about `10.7 deg` and no coefficient clipping occurs.
  Large-angle/clipped aerodynamics starts after slack and strain onset.
- After slack onset, the aerodynamic correction can inject significant power
  into the now much softer/slackened shape, so the response grows into the
  post-validity regime.
- Therefore the tension-only branch failure mechanism is:

```text
dynamic amplification -> local midspan shortening/compression demand
-> tension-only clamp creates slack/near-zero tangent region
-> local mechanism and high acceleration/velocity
-> relative-flow/attack-angle growth
-> aerodynamic force and power amplification
-> large displacement, large strain, large clipped-angle response
```

Research implication:

- Tension-only behavior is physically better than allowing a cable to carry
  sustained compression, but it does not by itself guarantee a valid
  post-slack simulation.
- Once slack occurs, the current single-chain cable model needs either:
  - a clear "slack onset / loss of taut-cable validity" limit state; or
  - a more complete post-slack cable/contact/geometric formulation if we want
    to simulate beyond slack.
- For galloping interpretation, results after the first slack event
  (`89.736640 s` in this run) should be treated as post-validity unless the
  research objective explicitly includes slack-cable dynamics.

### 2026-06-14 Cable/Rod Long-Time Structural-Branch Test

Purpose:

- Start a new non-overwriting long-time test on Git branch
  `cable-rod-long-timeseries-test`.
- The research objective is not to hide or actively terminate abnormal
  response, but to determine which cable structural formulation remains
  physically interpretable after slack/low-tension onset.
- All production runs for this stage should keep the project-side event stop
  disabled and should continue to the requested time or natural OpenSees
  convergence failure.

Literature/model-choice basis:

- Den Hartog galloping theory is a small-disturbance, taut-cable diagnostic
  basis. It supports interpreting negative aerodynamic damping near the
  equilibrium state, but it does not validate large-angle, slack, or post-slack
  cable dynamics.
- Goyal & Perkins high/low tension hybrid cable modelling shows why low-tension
  cable regions require rod/cable formulations beyond a pure taut-string model.
- Exact tension-field cable element and large-deformation rod/ANCF-type cable
  literature motivate separating taut-cable validity from post-slack cable/rod
  dynamics.
- Therefore pure tension-only truss is retained as the current taut-cable
  baseline, but is not assumed to be adequate after slack because zero
  compressive tangent can create a local mechanism once multiple neighbouring
  elements go slack.

New tracked files/scripts:

```text
docs/cable_rod_model_selection.md
tools/audit_structural_parameters.py
tools/prepare_cable_rod_long_test_configs.py
tools/analyse_cable_rod_long_test.py
```

Structural parameter audit output:

```text
output/diagnostics/cable_rod_long_test/parameter_audit/structural_parameter_audit.json
```

Audited typical-model values:

- `L = 322.8 m`, `Sag = 10.48 m`, sag/span ratio `0.03247`.
- Zebra ACSR, diameter `0.02862 m`, area `6.43323e-4 m2`.
- `E = 69 GPa`, `G = 4.265 GPa`.
- mass per unit length from self-weight: `1.62135 kg/m`.
- `EA = 44.389 MN`, `EI = 2272.47 N m2`, `GJ = 280.93 N m2`.
- pretension `19.785 kN`, equal to about `15%` of rated strength.
- parabolic horizontal tension from `wL^2/(8H)` is `19.761 kN`, matching the
  configured pretension within about `0.12%`.

Structural branches for the long-time comparison:

1. `current_tension_only`: `fiber_section = 2`,
   `corotTruss + ElasticPPGap + InitStrainMaterial`.
2. `calibrated_cable_rod`: `fiber_section = 3`,
   `forceBeamColumn + Corotational + circular fiber section`, with the same
   audited `EA/EI/GJ/mass/pretension/gravity`.
3. `regularized_tension_only`: `fiber_section = 4`,
   `corotTruss` with `ElasticPPGap` in parallel with a residual elastic
   stiffness of `1e-4 E`. This is a sensitivity branch only, not a claim that
   the conductor can physically carry sustained compression.

Traceability rule added:

- Each production run archives the generated OpenSees Tcl input in the run
  directory:
  - `Input_modal.tcl`
  - `Input_time_history.tcl`
  - `inputs_aerodynamic_damping.tcl`
- The root-level `Input.tcl` remains a temporary working input and may be
  overwritten by later runs; the archived copies are the case-specific record.

Smoke-check status:

- `MODAL` run passed for all three branches with OpenSees `3.8.0`.
- The first three modal frequencies remain essentially matched around
  `0.171 Hz`, `0.340 Hz`, and `0.342 Hz`, confirming that the new branches are
  consistent with the same small-disturbance equilibrium stiffness and mass
  before the long-time nonlinear response diverges.

Planned comparison metrics:

- first slack or low-tension time;
- first large strain/tension amplification;
- whether nonphysical jumps occur;
- attack-angle clipping onset;
- continuity of incremental aerodynamic force and aerodynamic power;
- sensitivity of the response to the structural branch.

Long-time typical-case results:

```text
output/diagnostics/cable_rod_long_test/comparison/cable_rod_long_test_summary.json
output/diagnostics/cable_rod_long_test/comparison/cable_rod_long_test_core_comparison.png
docs/cable_rod_long_test_results.md
```

Run statuses:

- `current_tension_only`: external 2 h timeout after reaching `117.608 s`.
  No OpenSees failure status was written before the timeout.
- `calibrated_cable_rod`: natural OpenSees failure at
  `108.051750768 s`, `ANALYZE_RETURN_CODE -3`,
  `analysis_did_not_converge_min_factor_reached`.
- `regularized_tension_only`: external 2 h timeout after reaching
  `141.830 s`. No OpenSees failure status was written before the timeout.

Earliest event comparison:

- `current_tension_only`:
  - acceleration over `100 m/s2`: `88.350 s`;
  - first low-tension/slack/strain event: `89.736640 s`;
  - first attack-angle clipping: `90.455775 s`.
- `calibrated_cable_rod`:
  - acceleration over `100 m/s2`: `68.300 s`;
  - first force amplification and alpha clipping: `69.518950 s`;
  - first negative/low tension: `69.861189 s`;
  - OpenSees failure: `108.051751 s`.
- `regularized_tension_only`:
  - acceleration over `100 m/s2`: `88.400 s`;
  - first force amplification: `91.472550 s`;
  - first low-tension/slack/residual negative entry: `91.673316 s`;
  - first alpha clipping: `91.710519 s`.

Interpretation:

- The three branches remain highly sensitive after the taut-cable state is
  lost, so the abnormal response is not solved by simply selecting one of the
  tested branches.
- Pure tension-only avoids sustained negative force but creates a near-zero
  tangent local mechanism after slack.
- Calibrated beam/rod provides a continuous low-tension path and is closer to
  low-tension cable/rod modelling literature, but the current simple branch
  permits large compressive axial demand and still enters large-angle
  aerodynamic amplification and non-convergence.
- Small-compression regularization smooths the zero-tangent mechanism and
  delays onset by about `1.9 s`, but it is a sensitivity branch rather than a
  physical post-slack model.
- The next research direction should not be an active stop limit. The project
  should mark first slack/low-tension as a taut-cable validity boundary for
  galloping interpretation, while separately developing and validating a
  post-slack cable/rod or ANCF-style model with appropriate large-angle
  aerodynamic coefficients.

### 2026-06-29 Current Core Methodology for Model Development

This is the current highest-priority working principle for the next stage of
the galloping research project.

Research objective:

- The purpose of this project is to build a more realistic and accurate
  galloping model, not merely to make OpenSees runs finish or to suppress
  abnormal response.
- Before the model is physically validated, no project-side active limit,
  event-stop threshold, or artificial boundary condition should be added to
  terminate the analysis early.
- A run should continue until the requested duration or until OpenSees itself
  naturally fails/converges unsuccessfully. Natural OpenSees failure is a valid
  research output and must be recorded.

Model-update workflow:

1. Apply one physically motivated model update at a time when possible.
2. Run the updated model under controlled, comparable inputs.
3. Record the full time-history response and solver state.
4. After the run, judge whether the response is consistent with real structural
   response, galloping mechanics, and published engineering/research cases.
5. If the response is unreasonable or the solver fails, trace backward from the
   abnormal/failure time through all recorded variables to infer the likely
   modelling error or missing physics.
6. Use that diagnosis to improve the model in the next iteration.

Mandatory monitoring data for formal model-update runs:

- Geometry and deformed cable shape over time.
- Element internal force state, including axial strain/tension or equivalent
  rod/cable internal force measures.
- Inter-element/local interaction indicators whenever available or newly added.
- Key-node kinematics at least at quarter-span, midspan, and three-quarter-span:
  displacement, velocity, and acceleration in the relevant directions.
- Aerodynamic quantities, including `C_L`, `C_D`, angle of attack, relative
  wind velocity, incremental/full aerodynamic force components, and aerodynamic
  power/work indicators.
- Wind input and equivalent loading at key monitoring locations, including
  local free-stream wind speed, local relative wind speed, equivalent nodal or
  element aerodynamic load components, and the corresponding angle of attack
  at quarter-span, midspan, and three-quarter-span.
- Effective damping and Den Hartog/delta-type diagnostic quantities, clearly
  marked as diagnostics when they are not directly applied to the equation of
  motion.
- Support reactions and solver/convergence state over time.
- Any additional diagnostics needed to answer the active modelling question may
  be added, but existing required monitoring channels should not be removed.

Failure/abnormal-response analysis rule:

- If OpenSees stops, record the OpenSees return code, status file, last solver
  norms, factor/substepping state, final physical time, and the latest complete
  rows of all response logs.
- Diagnose the failure by tracing backward from the failure/abnormal time:
  structural kinematics -> element force/strain -> aerodynamic force/power ->
  damping/diagnostic quantities -> support reactions -> solver convergence.
- The goal of this diagnosis is to identify a physical modelling deficiency or
  numerical formulation issue, then propose the next scientifically justified
  model improvement.

Explicit prohibition:

- Do not make the model appear successful by adding active displacement,
  velocity, slack, force, or attack-angle termination limits.
- Such quantities may be recorded and used as post-processing validity markers,
  but they should not actively stop the formal model-development simulations.

### 2026-06-29 Calibrated Cable/Rod Collapse Cause Analysis

Updated monitoring requirement:

- Formal runs must explicitly record key-location wind input and equivalent
  load variables. Required node-level aerodynamic columns now include
  free-stream wind components, `U_wind`, reference alpha, relative-flow
  components, `U_rel`, current alpha, `C_D`, `C_L`, reference/current/delta
  force components, and aerodynamic power.

Monitoring implementation:

- `tcl_procedures/Damping_shifter.tcl` now writes additional node-level
  columns to `incremental_qs_node_power_log.csv`:
  `wind_y`, `wind_z`, `U_wind`, `ref_alpha_deg`, `rel_y`, and `rel_z`.
- A non-overwriting rerun config was generated by:

```text
tools/prepare_calibrated_cable_rod_monitoring_v2_config.py
```

New rerun output:

```text
output/diagnostics/cable_rod_long_test/calibrated_cable_rod_monitoring_v2/run
```

Collapse analysis output:

```text
output/diagnostics/cable_rod_long_test/comparison/calibrated_cable_rod_monitoring_v2_collapse_cause
docs/calibrated_cable_rod_collapse_analysis.md
```

Monitoring completeness after rerun:

- displacement, velocity, acceleration: present;
- support reactions: present;
- element strain/tension summary and per-element logs: present;
- total and node-level aerodynamic force/power logs: present;
- node-level free-stream wind, relative wind, alpha, `C_D`, `C_L`: present;
- effective damping diagnostic: present;
- solver status/failure code: present.

Rerun result:

- The run naturally failed with OpenSees, not by project-side active stop.
- Failure time remained `108.051750768 s`.
- Failure status:

```text
STATUS failed
MESSAGE analysis_did_not_converge_min_factor_reached
ANALYZE_RETURN_CODE -3
FACTOR 6.657041767889234e-10
MIN_FACTOR 1e-06
```

Ordered event chain:

- key-node acceleration exceeds `100 m/s2`: `68.550000 s`;
- key-node velocity exceeds `1 m/s`: `68.650000 s`;
- incremental QS force exceeds `500 N`: `69.518950 s`;
- first alpha clipping: `69.518950 s`;
- first negative/low tension: `69.861189 s`;
- element strain exceeds `0.001`: `70.518784 s`;
- aerodynamic power exceeds `1000 W`: `71.399952 s`;
- aerodynamic power exceeds `10000 W`: `97.406480 s`;
- element strain exceeds `0.01`: `107.739246 s`;
- element absolute tension exceeds `500 kN`: `107.811040 s`;
- OpenSees failure: `108.051751 s`.

Direct cause:

- The final failure is a nonlinear convergence failure in a severe coupled
  aero-structural state. Before failure, relative velocity, alpha clipping,
  aerodynamic force/power, support reactions, and element axial force all
  amplify strongly.

Root-cause interpretation:

- The current calibrated `forceBeamColumn` branch provides a continuous
  low-tension beam/rod path, but it also permits large compressive axial
  demand and near-support force localization.
- The quasi-steady aerodynamic model is driven into a large-angle clipped
  coefficient regime after motion grows, which is outside the validated
  small/moderate-angle galloping range.
- Therefore the collapse is not solved by the present cable/rod branch; it
  exposes that post-taut/post-slack dynamics and large-angle aerodynamics need
  a more physical formulation.

Next model-improvement direction:

1. Keep slack/low-tension as a post-processing validity marker for the
   taut-cable galloping regime, not as an active stop.
2. Develop a post-taut cable/rod or ANCF-style model with bending, geometric
   nonlinearity, and a calibrated unilateral/tension-field axial law.
3. Replace coefficient clipping with a validated large-angle/post-stall
   aerodynamic coefficient model.
4. Audit support/end-region modelling because peak axial localization appears
   near the support-side elements.
5. Add energy consistency diagnostics for kinetic energy proxy, strain-energy
   proxy, aerodynamic work, support work, and damping work.
