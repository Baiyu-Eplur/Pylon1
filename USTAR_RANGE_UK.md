# UK-Informed u_star Range

Last updated: 2026-06-02

This file defines the staged `u_star` range for the first galloping boundary
tests. The range links the project friction-velocity input to UK wind climate
and Eurocode-style reference wind speeds.

## Project Wind Conversion

The current wind generator uses the friction-based log-law branch inherited from
`WIND_SIMULATION.mlx`:

```text
U(z) = u_star / kappa * log(z / z0)
kappa = 0.387
z0 = 0.05 m
```

For 10 m open-country wind:

```text
U10 = u_star / 0.387 * log(10 / 0.05)
U10 = 13.691 * u_star
u_star = 0.07304 * U10
```

For the current conductor-height range, the validated baseline gives:

```text
u_star = 0.600 m/s -> mean conductor wind ~= 10.45 m/s
mean conductor wind ~= 17.42 * u_star
```

The exact conductor-height factor varies by node height, but `17.42` is the
validated full-span mean from `FORCE_3/SIM1`.

## UK Wind Context

### Ordinary / climatic mean winds

Met Office long-term climate pages report monthly mean wind speed at 10 m in
knots for UK station locations. Typical annual mean station values are much
lower than structural design wind speeds. They generally support a low-to-medium
operational band rather than an extreme design band.

Interpretation for this project:

```text
U10 ~= 3 to 8 m/s -> u_star ~= 0.22 to 0.58 m/s
```

### RICA galloping context

National Grid RICA records galloping as associated with moderate/high winds,
commonly around:

```text
5 to 15 m/s
```

Using the project conductor-height factor:

```text
U_conductor = 5 m/s  -> u_star ~= 0.29 m/s
U_conductor = 15 m/s -> u_star ~= 0.86 m/s
```

Interpretation:

- `u_star = 0.30 to 0.90` is the central physical galloping search band.
- The current validated case `u_star = 0.60` corresponds to about `10.45 m/s`
  mean conductor-height wind and lies near the middle of this band.

### UK Eurocode / National Annex extreme wind context

EN 1991-1-4 defines fundamental/basic wind speed as a 10-minute mean wind at
10 m height in open terrain, with annual exceedance probability 0.02 for the
standard design working life. UK National Annex sources and design guides report
regional 10 m open-country basic wind speeds approximately spanning:

```text
22 to 32 m/s
```

This maps to:

```text
U10 = 22 m/s -> u_star ~= 1.61 m/s
U10 = 32 m/s -> u_star ~= 2.34 m/s
```

Interpretation:

- `u_star = 1.50 to 2.35` is an extreme/design-context stress-test band.
- These values are not the best first search for onset; they are likely to
  produce severe response and numerical difficulty after the lower boundary is
  understood.

## Staged Sweep Range

Use staged ranges rather than one uniform grid.

### Stage 1: Calibration / lower boundary

```text
u_star = 0.20, 0.30, 0.40, 0.50, 0.60
```

Purpose:

- locate whether C1/C2/C4/C6 begin below the already validated `0.60` case;
- stay inside ordinary-to-moderate UK wind conditions.

### Stage 2: Central galloping band

```text
u_star = 0.70, 0.80, 0.90
```

Purpose:

- cover the upper part of the RICA galloping context;
- test developed response before entering Eurocode extreme wind levels.

### Stage 3: Developed response / stress band

```text
u_star = 1.00, 1.20
```

Purpose:

- probe nonlinear/developed response and engineering exceedance;
- still below the upper Eurocode extreme-wind band.

### Stage 4: Eurocode extreme-context envelope

```text
u_star = 1.50, 2.00, 2.35
```

Purpose:

- compare against high UK basic wind contexts;
- use as stress tests only after lower ranges are classified.

## Refinement Rule

After the first triggered criterion is found, refine locally:

```text
step = 0.025 to 0.05 in u_star
```

Example:

```text
if C2 first triggers between 0.30 and 0.40:
run 0.325, 0.350, 0.375
```

Store separate thresholds:

```text
u_star_crit_by_C1
u_star_crit_by_C2
u_star_crit_by_C4
u_star_crit_by_C6
u_star_crit_by_C7
```

## Decision For First Batch

Before running very high wind cases, execute Stage 1:

```text
u_star = 0.20, 0.30, 0.40, 0.50, 0.60
L = 322.8 m
H = 10.48 m
duration = start with 2048 steps for workflow classification
```

If the workflow remains stable and C2/C4/C6 boundaries are bracketed, move to:

```text
u_star = 0.70, 0.80, 0.90, 1.00, 1.20
```

Then reserve:

```text
u_star = 1.50, 2.00, 2.35
```

for Eurocode extreme-context envelope checks.

## Stage 1 Execution Result

Executed on 2026-06-02 with:

```text
L = 322.8 m
H/Sag = 10.48 m
npt = 2048
dt = 0.05 s
duration = 102.4 s
seed_base = 20260602
```

Summary:

```text
output/response_audit/ustar_stage1_uk_l322_h1048_n2048/stage1_summary.md
```

Short-run classification:

| u_star | Mean conductor wind approx. (m/s) | Max displacement (m) | Negative damping fraction | C2+C4 confirmed |
|---:|---:|---:|---:|:---:|
| 0.20 | 3.48 | 0.167 | 0.163 | no |
| 0.30 | 5.23 | 0.480 | 0.245 | no |
| 0.40 | 6.97 | 1.440 | 0.105 | yes |
| 0.50 | 8.71 | 1.793 | 0.233 | yes |
| 0.60 | 10.45 | 2.991 | 0.288 | no, middle-window peak then decay |

The first short-run C2+C4 confirmed bracket is:

```text
0.30 < u_star_crit <= 0.40
```

This is a workflow-classification result, not the final statistical boundary.
The next refinement should run:

```text
u_star = 0.325, 0.350, 0.375, 0.400
```

Selected longer/repeated-seed cases should then verify `0.35`, `0.40`, and
`0.60`.

## Stage 1 Local Refinement Result

Executed on 2026-06-02:

```text
u_star = 0.325, 0.350, 0.375, 0.400
npt = 2048
dt = 0.05 s
duration = 102.4 s
```

Summary:

```text
output/response_audit/ustar_refine1_uk_l322_h1048_n2048/refine1_summary.md
```

Short-run classification:

| u_star | Mean conductor wind approx. (m/s) | Max displacement (m) | Negative damping fraction | C2+C4 confirmed |
|---:|---:|---:|---:|:---:|
| 0.325 | 5.66 | 0.517 | 0.113 | no, near threshold |
| 0.350 | 6.10 | 0.632 | 0.102 | no |
| 0.375 | 6.53 | 0.823 | 0.237 | no |
| 0.400 | 6.97 | 1.440 | 0.105 | yes |

Strict short-run bracket:

```text
0.375 < u_star_crit <= 0.400
```

Before repeated-seed testing, update generated force/wind case naming to include
the seed or realization id, because the current sweep generator reuses existing
same-`u_star` wind/force files by default.

Implemented tool support:

```text
tools/run_ustar_sweep.py --label-precision 3 --include-seed-in-name
```

This should be used for the next repeated-seed refinement around:

```text
u_star = 0.325, 0.350, 0.375, 0.400
```

## Key Long-Record Verification

Executed on 2026-06-02:

```text
u_star = 0.350, 0.375, 0.400
npt = 4096
dt = 0.05 s
duration = 204.8 s
seed-aware naming = true
```

Summary:

```text
output/response_audit/ustar_key_long1_uk_l322_h1048_n4096/key_long1_summary.md
```

Long-record classification:

| u_star | Mean conductor wind approx. (m/s) | Max displacement (m) | Negative damping fraction | C2+C4 confirmed |
|---:|---:|---:|---:|:---:|
| 0.350 | 6.10 | 0.820 | 0.214 | no |
| 0.375 | 6.53 | 0.874 | 0.414 | no |
| 0.400 | 6.97 | 1.392 | 0.112 | yes |

The current strict long-record bracket is:

```text
0.375 < u_star_crit <= 0.400
```

Next verification should repeat `0.375` and `0.400` with additional seeds before
fitting the final local boundary.

## Key Repeated-Seed Verification

Executed on 2026-06-02:

```text
u_star = 0.375, 0.400
npt = 4096
dt = 0.05 s
duration = 204.8 s
seed-aware naming = true
```

Summary:

```text
output/response_audit/ustar_key_repeat1_uk_l322_h1048_n4096/repeat1_summary.md
```

Repeated-seed classification:

| u_star | seed | Mean conductor wind approx. (m/s) | Max displacement (m) | Negative damping fraction | C2+C4 confirmed |
|---:|---:|---:|---:|---:|:---:|
| 0.375 | 20260720 | 6.53 | 1.272 | 0.192 | no |
| 0.400 | 20260721 | 6.97 | 0.922 | 0.380 | no |

Combined `4096`-step evidence:

```text
u_star = 0.350: C2 1/1, C4 0/1
u_star = 0.375: C2 2/2, C4 0/2
u_star = 0.400: C2 2/2, C4 1/2
```

Current interpretation:

```text
u_star = 0.375 to 0.400 is the observed C2+C4 transition band.
```

The final `u_star_crit` should be extracted statistically, for example by
estimating the probability of C4 confirmation for each `u_star`, rather than by
using a single turbulent realization.

## Public Source Links

- Met Office long-term climate averages: https://www.metoffice.gov.uk/research/climate/maps-and-data/location-specific-long-term-averages
- National Grid RICA galloping report: https://www.nationalgrid.com/document/337841/download
- EN 1991-1-4 wind action reference summary: https://steelcalculator.app/reference/european-wind-load/
- UK EN 1991-1-4 National Annex example/basic wind speed guide: https://skyciv.com/docs/tech-notes/loading/wind-load-calculation-for-signs-en-1991/
