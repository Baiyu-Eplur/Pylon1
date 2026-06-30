# Path-Load Spatial/Temporal Diagnostic And Root-Cause Interpretation

Date: 2026-06-30

## Objective

The objective was to identify the physical/numerical cause of the abnormal
element-internal-force resultant that appears before the large galloping-like
response. The analysis deliberately did not add any response-based active stop.

The checked chain was:

```text
precomputed Path wind/load input
-> spatial/temporal roughness and coherence
-> structural local/high-wavenumber response
-> node force-balance decomposition near 68.25 s
-> time-step and load-interpolation sensitivity
```

## Baseline Evidence

Baseline run:

```text
output/diagnostics/cable_rod_long_test/calibrated_cable_rod_node_balance_72s_v2/run
```

The first `acc_xz > 100 m/s2` event occurs at:

```text
time = 68.25 s
node = 52
acc_xz = 113.77 m/s2
node internal resultant = 579.67 N
node aero current resultant = 8.08 N
node aero motion delta = 5.17 N
```

This confirms that the first abnormal acceleration is directly driven by
structural internal-force imbalance, not by a local aerodynamic-force spike.

## Original Path-Load Content

Diagnostic output:

```text
output/diagnostics/cable_rod_long_test/comparison/path_load_spatial_temporal_diagnostic
```

Important findings:

- The original `FORCE_3/SIM1` Path-load field is spatially rough along the
  cable nodes.
- Adjacent-node correlation:
  - `Fy` mean correlation: `0.348`;
  - `Fy` minimum correlation: `0.178`;
  - `Fz` mean correlation: `0.575`;
  - `Fz` minimum correlation: `0.465`.
- Spatial high-wavenumber energy fraction near the onset window
  `68.0-69.1 s`:
  - `Fy`, modes above spatial index 12: `0.691`;
  - `Fy`, modes above spatial index 25: `0.436`;
  - `Fz`, modes above spatial index 12: `0.500`;
  - `Fz`, modes above spatial index 25: `0.292`.

Interpretation:

- The Path load contains strong node-to-node force variation. This is not a
  smooth distributed wind load along a continuous cable.
- Such high spatial-frequency forcing can excite local cable/rod deformation
  and adjacent-element end-force imbalance, especially when the response is
  integrated with the same coarse time increment as the force history.

## Sensitivity Cases

Two fixed-duration 72 s controls were run. Neither used a response-based active
stop.

### Case A: Temporal interpolation / smaller structural step

Configuration:

```text
output/diagnostics/cable_rod_long_test/path_load_sensitivity/temporal_interp_dt0p025_72s/temporal_interp_dt0p025_72s.yaml
```

Modification:

- Same `FORCE_3/SIM1` field;
- all force/wind histories linearly interpolated to `dt = 0.025 s`;
- transient target duration remains `72 s`.

Result:

- no `acc_xz > 100 m/s2` event;
- max acceleration over the whole run: `22.31 m/s2`;
- node 52 at `68.25 s`:
  - `acc_xz = 8.58 m/s2`;
  - internal resultant `62.88 N`;
  - aero current resultant `3.85 N`.

### Case B: Spatial smoothing

Configuration:

```text
output/diagnostics/cable_rod_long_test/path_load_sensitivity/spatial_smooth5_dt0p05_72s/spatial_smooth5_dt0p05_72s.yaml
```

Modification:

- Same time sampling `dt = 0.05 s`;
- force/wind histories smoothed along node index with a symmetric 5-point
  binomial kernel `[1, 4, 6, 4, 1]/16`.

Result:

- no `acc_xz > 100 m/s2` event;
- max acceleration over the whole run: `15.00 m/s2`;
- node 52 at `68.25 s`:
  - `acc_xz = 3.43 m/s2`;
  - internal resultant `55.22 N`;
  - aero current resultant `2.61 N`.

## Root-Cause Interpretation

The abnormal 68.25 s event is not a verified galloping instability onset. It is
most consistently explained as a numerical/forcing artefact caused by the
combination of:

1. a spatially rough precomputed nodal Path-load field with low adjacent-node
   force coherence and high spatial-wavenumber energy;
2. a transient solution using the original `0.05 s` load/solver increment,
   which lets the rough nodal load field excite local cable/rod high-frequency
   response;
3. the structural model then converts this local forcing into adjacent-element
   internal-force imbalance, which appears before any large aerodynamic
   motion-correction force.

The fact that both controls remove the large acceleration is important:

- the half-time-step control shows the response is time-step/interpolation
  sensitive;
- the spatial-smoothing control shows the response is also sensitive to
  high-wavenumber nodal forcing;
- because spatial smoothing at the original `0.05 s` step also removes the
  abnormal acceleration, the Path-load spatial roughness is a primary modelling
  issue rather than a pure integrator issue.

## Proposed Model Correction

Do not add a response limit or artificial stop. The correction should make the
forcing physically consistent:

1. Replace direct independent nodal Path loads with a spatially coherent wind
   field before force calculation.
2. Generate wind histories on a physically justified aerodynamic grid using a
   target coherence model, then interpolate the continuous wind/load field to
   structural nodes or elements.
3. Apply aerodynamic loading as element-equivalent distributed loads or as
   nodal loads obtained from a smooth element tributary integration, not as
   mutually jagged independent node forces.
4. Use a structural time step smaller than the wind/load sampling interval, or
   keep solver substeps independent of wind sampling and interpolate loads
   continuously in time.
5. Keep the existing node force-balance diagnostics, element
   strain/tension logs, wind speed, alpha, coefficient, and energy/power logs
   for every formal validation run.

Recommended next validation:

- create a physically coherent wind/load generation branch;
- run three controls with the same weather seed:
  1. original raw Path nodal load;
  2. coherence-filtered nodal load;
  3. element-equivalent distributed load from the same coherent wind field;
- require convergence of galloping indicators under time-step refinement before
  treating a large response as physical galloping.

