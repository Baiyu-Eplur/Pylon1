# Geometry Baseline: Span Length And Sag

Last updated: 2026-06-02

This file records the source-backed choice of the initial span length `L` and
sag/downward catenary height `H` before batch `u_star` sweeps. In this project
`H` is the configured `Sag`: the vertical drop from the support level to the
lowest point of the conductor.

## Main Conclusion

European overhead-line standards and design guidance do not prescribe a single
universal relation `H = f(L)` for all conductors. Instead:

- `L` is selected from route/tower/crossing constraints and tower family;
- `H` is obtained from sag-tension calculation for conductor weight, thermal
  state, wind/ice load, creep, installation tension, and clearance limits;
- final design checks must maintain electrical clearance and avoid excessive
  conductor tension.

Therefore, for this research, use:

```text
typical baseline:
L = 322.8 m
H = 10.48 m
H/L = 0.0325
```

This is the calibrated Timur/National-Grid-style baseline already implemented
in `config/timur_baseline.yaml`. It also sits inside the public design range
implied by National Grid RICA examples and European sag-tension guidance.

## Sources And Evidence

### EN 50341 / RICA Clearance Logic

National Grid RICA states that conductor positioning must satisfy phase-ground
and phase-phase clearances both at the tower and at midspan, and that BS EN
50341-1 provides the clearance methodology. It gives the midspan clearance form:

```text
c = k * sqrt(f) + lk + k1 * Dpp
```

where `f` is conductor sag at 40 C. This is important: the standard/design logic
uses sag as an input to clearance checks, but does not give a single universal
sag for every span.

RICA example values for a Curlew conductor:

```text
span 300 m -> sag 7.2 m
span 500 m -> sag 18.0 m
```

Sag ratios:

```text
7.2 / 300 = 0.024
18.0 / 500 = 0.036
```

RICA also records maximum single span lengths for example UK tower families:

```text
L3  275 kV: vertical phase separation 6.10 m, max single span 537 m
L66 275 kV: vertical phase separation 7.16 m, max single span 457 m
L2  400 kV: vertical phase separation 7.85 m, max single span TBC
```

Research interpretation:

- A typical transmission-line span in this context is plausibly in the
  `300-500 m` range.
- Sag/span ratios around `0.024-0.036` are directly supported by RICA examples.
- Galloping checks should also track conductor clashing and phase separation,
  because RICA explicitly treats galloping ellipses and abnormal conductor
  movement as design concerns.

### CIGRE Sag-Tension Guidance

CIGRE Technical Brochure 324, "Sag-Tension calculation methods for overhead
lines", describes sag-tension calculation over conductor temperatures and ice
and wind loads. It emphasizes that there is not a unique universal sag method;
engineers must account for the physical and mathematical relationships behind
catenary sag and tension.

Research interpretation:

- `H` should be treated as a calculated/dependent design variable, not merely as
  an arbitrary geometry setting.
- When varying `L`, use a documented sag rule and store it with each run.

### Public European Design Case

A published multi-circuit/multi-voltage HVAC line study reports:

```text
Polish 400 kV and 220 kV lines: rated span length about 450 m
110 kV lines: nominal span length about 300 m
```

It also states that span selection must coordinate conductor sags while
maintaining required vertical distances and not exceeding permissible conductor
tension.

Research interpretation:

- `L = 300 m` is a common lower transmission/distribution-scale nominal span.
- `L = 450 m` is a common high-voltage transmission nominal span in at least one
  European design setting.
- The current Timur baseline `L = 322.8 m` is a conservative and well-calibrated
  typical starting point.

## Current Conductor-Based Sag Relation

For the current Zebra ACSR baseline:

```text
self-weight w = 15.90 N/m
RTS = 131.9 kN
pretension T0 = 0.15 * RTS = 19.785 kN
```

For shallow spans, the parabolic sag approximation gives:

```text
H(L) ~= w * L^2 / (8 * T0)
```

For the baseline:

```text
H(322.8) ~= 15.90 * 322.8^2 / (8 * 19785) = 10.47 m
```

This matches the calibrated value:

```text
H = 10.48 m
```

Thus the current `L = 322.8 m`, `H = 10.48 m` pair is not arbitrary; it is
consistent with the chosen Zebra self-weight and 15% RTS pretension.

## Recommended Research Settings

### Immediate Typical Case

Use this before the first `u_star` search:

```text
L = 322.8 m
H = 10.48 m
geometry.type = 2 catenary
conductor = Zebra ACSR
self_weight = 15.90 N/m
pretension = 19.785 kN
```

Reason:

- already calibrated in the project;
- directly tied to Timur baseline;
- close to RICA's 300 m example span;
- sag/span ratio `0.0325` lies inside the RICA-supported `0.024-0.036` band.

### First L Sweep

For the first 2D boundary surface, use:

```text
L = 250, 300, 322.8, 350, 400, 450, 500 m
```

For each `L`, define the primary sag from the same conductor/tension law:

```text
H_primary(L) = 15.90 * L^2 / (8 * 19785)
```

Example values:

```text
L = 250 m   H_primary ~= 6.28 m
L = 300 m   H_primary ~= 9.04 m
L = 322.8 m H_primary ~= 10.48 m
L = 350 m   H_primary ~= 12.31 m
L = 400 m   H_primary ~= 16.08 m
L = 450 m   H_primary ~= 20.35 m
L = 500 m   H_primary ~= 25.12 m
```

This primary law keeps conductor and pretension assumptions consistent while
span length varies.

### Sag Sensitivity Band

Because real designs can use different stringing tensions and conductor types,
also keep sensitivity bands:

```text
low sag:     H/L = 0.024
baseline:    H/L = 0.0325
high sag:    H/L = 0.036
```

Use these as secondary sweeps after the primary `H_primary(L)` sweep, not before.

## Decision For Current Workflow

Before the first `u_star` batch:

```text
Use L = 322.8 m and H = 10.48 m.
```

For the eventual 2D result:

```text
u_star_crit = F(L, H_rule, criterion)
```

where `H_rule` is stored explicitly as either:

- `zebra_15pct_RTS_sag_tension`;
- `constant_sag_ratio_0.024`;
- `constant_sag_ratio_0.0325`;
- `constant_sag_ratio_0.036`;
- or another future standard/conductor-specific sag-tension rule.

