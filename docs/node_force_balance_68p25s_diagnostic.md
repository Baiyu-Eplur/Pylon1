# Node Force-Balance Diagnostic at the First Large-Acceleration Window

Date: 2026-06-29

## Purpose

This diagnostic was added to identify which force component directly produces
the first large nodal acceleration near `68.25 s` in the calibrated cable/rod
typical galloping case. No response-based active stop was used. The run was a
fixed-duration `72 s` diagnostic so that the known onset window was fully
covered.

## Model And Output

Configuration:

```text
output/diagnostics/cable_rod_long_test/calibrated_cable_rod_node_balance_72s_v2/calibrated_cable_rod_node_balance_72s_v2.yaml
```

OpenSees output:

```text
output/diagnostics/cable_rod_long_test/calibrated_cable_rod_node_balance_72s_v2/run
```

Post-processing output:

```text
output/diagnostics/cable_rod_long_test/comparison/node_force_balance_72s_v2
```

Main files:

- `node_force_balance_log.csv`: per-node time history of external aerodynamic
  force, inertia, Rayleigh damping resistance, gravity, adjacent element end
  force resultants, and equilibrium residual.
- `focus_force_balance_events.csv`: force decomposition at the main
  acceleration threshold events.
- `node52_66_69p5s_samples.csv`: detailed samples for node 52.
- `top_internal_force_jumps_67p5_69p2s.csv`: largest internal-force jumps near
  the onset window.
- `node52_force_balance_66_69p5s.png`: node 52 force-component time history.
- `key_event_force_component_bars.png`: component magnitudes at key events.

The run reached the fixed target time:

```text
STATUS success
MESSAGE target_time_reached
TIME 72.0
ANALYZE_RETURN_CODE 0
```

## Diagnostic Implementation

The Tcl workflow now records, at every successful OpenSees step when enabled:

- node mass, acceleration, velocity;
- inertial force `m a`;
- structural Rayleigh damping resistance `alpha_M m v`;
- gravity `-m g`;
- node-level aerodynamic force components:
  `aero_ref`, `aero_delta`, `aero_current`;
- left and right adjacent element translational end-force contributions;
- total element internal resultant at the node;
- residual:

```text
residual = aero_current + gravity - inertia - damping - element_internal
```

The first diagnostic attempt treated the second element node as the end node,
but the current `forceBeamColumn` branch can return an internal/control node in
`eleNodes`. This was corrected by using the first and last node tags as the
physical element ends, consistent with the aerodynamic local-direction logic.

The corrected diagnostic gives residuals of only about `0.1-3 N` at the key
events, so the component decomposition is numerically self-consistent.

## Main Findings

At the first `>100 m/s2` event:

```text
time = 68.25 s
node = 52
acc_xz = 113.77 m/s2
inertial_xz = 595.42 N
aero_current_xz = 8.08 N
aero_delta_xz = 5.17 N
left element 51 resultant = 282.46 N
right element 52 resultant = 302.63 N
residual_xz = 2.05 N
```

Therefore the direct force balance at `68.25 s` is dominated by adjacent
element internal-force resultants, not by a sudden large aerodynamic force. The
local aerodynamic force is two orders of magnitude smaller than the internal
and inertial terms at that instant.

The later acceleration growth between about `68.8-69.1 s` also coincides with
rapid changes in structural internal-force resultants. In the same window,
changes in node-level aerodynamic force remain much smaller than the internal
force jumps. The global aerodynamic motion correction increases during this
period, but alpha clipping and strong aerodynamic power input occur later,
after the structural motion has already grown.

The element strain/tension logs show no slack or large strain at `68.25 s`.
Typical nearby strains are still around `10^-5` to `10^-4`, and estimated
tensions remain in the ordinary pretension-dominated range. Thus the first
large acceleration is not triggered by a low-tension/slack transition.

## Interpretation

The first abnormal acceleration is a structural dynamic force-redistribution
event under the current wind loading and calibrated cable/rod model. The
incremental quasi-steady aerodynamic branch does not directly inject a large
local force at `68.25 s`; instead, aerodynamic feedback becomes important after
the motion has grown enough to increase relative wind angle, motion correction,
and eventually coefficient clipping.

This means the next model-improvement step should not be to reduce the
aerodynamic force artificially. The next check should target the structural
dynamic source of the internal-force jump:

1. verify whether the original Path wind load contains high spatial-frequency
   or low-coherence nodal components that excite local cable/rod modes;
2. compare the modal content of the response against the first few physical
   cable modes and against element-level high-frequency modes;
3. test whether smaller structural time steps or force interpolation change
   the onset of the internal-force jump;
4. audit the forceBeamColumn cable/rod discretisation and mass distribution for
   spurious local modes.

