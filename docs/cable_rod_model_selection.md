# Cable/Rod Structural Model Selection for Long-Time Galloping Tests

Date: 2026-06-14

## Purpose

This note defines the structural-model rationale for the next long-time
galloping tests. The goal is not to stop the simulation at slack onset. The
goal is to choose a structural model that remains physically interpretable when
the conductor enters low-tension or slack-like states.

## Why pure tension-only truss is insufficient after slack

The current tension-only branch uses a `corotTruss` element with a
`ElasticPPGap + InitStrainMaterial` material. This is physically attractive for
a taut overhead conductor because it prevents sustained axial compression.
However, once local shortening is demanded, the element force is clamped to
zero. A local group of zero-force truss elements can then lose axial tangent
stiffness and create a numerical mechanism.

The 200 s extension confirmed this mechanism: in the current typical case, the
first slack event occurs around the midspan region at about `89.736640 s`.
Elements `50-52` demand negative raw elastic tension, and elements `50-51`
would require about `-130` to `-144 kN` if the material were linear elastic.
The tension-only branch correctly clamps these to zero, but the local
stiffness loss is followed by abrupt velocity, acceleration, attack-angle, and
aerodynamic-force growth.

Therefore the pure tension-only truss branch is appropriate for taut-cable
galloping before slack, but not sufficient for post-slack dynamics.

## Literature basis

### Small-disturbance galloping model

Den Hartog-type galloping criteria are small-disturbance aerodynamic stability
criteria. They are useful for identifying negative aerodynamic damping in a
taut, small-angle quasi-steady setting, but they do not model slack-cable
post-buckling or low-tension rod behavior. In this project they remain
diagnostic limits, not a complete post-slack structural model.

### High/low tension cable zones

Goyal and Perkins propose a hybrid rod-catenary cable model for cases with
both high- and low-tension zones. Their key observation is directly relevant:
high-tension cable zones can be treated efficiently with catenary/cable
elements, while localized low-tension zones may require rod elements to capture
flexure and torsion. Source:
`https://arxiv.org/abs/physics/0702224`.

This supports adding a conductor branch that can represent bending and torsion
in low-tension zones rather than leaving a pure truss chain with zero tangent
stiffness.

### Rod/self-contact and low-tension dynamics

Goyal, Perkins, and Lee discuss low-tension cable configurations such as loops,
tangles, and kinks using Kirchhoff rod theory with bending, torsion, and
self-contact. Source: `https://arxiv.org/abs/physics/0702198`.

Our overhead conductor case is not a marine cable self-contact study, but the
same modelling lesson applies: low-tension cable dynamics cannot be represented
by axial tension alone.

### Exact tension-field cable elements

Recent cable finite-element work based on exact tension fields also emphasizes
geometrically exact mechanics and accurate internal force fields for cable
structures. Source: `https://arxiv.org/abs/2401.05609`.

This supports improving the cable internal-force representation instead of
interpreting post-slack truss artifacts as calibrated galloping.

### OpenSees structural element basis

OpenSees `forceBeamColumn` is a force-based beam-column element. The official
documentation describes that it uses a basic system with end rotations and
axial deformation and relies on a geometric transformation between basic and
global systems. Source:
`https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/forceBeamColumn.html`.

This makes it a reasonable first OpenSees-native candidate for a
post-slack-capable conductor branch, provided that EA, EI, GJ, mass, gravity,
and pretension are explicitly audited and not treated as arbitrary tuning
parameters.

## Candidate model branches

### Branch A: current tension-only

Purpose: baseline physical taut-cable model.

Element:

```text
corotTruss + ElasticPPGap + InitStrainMaterial
```

Interpretation:

- valid for taut conductor response;
- prevents sustained compression;
- slack onset is a physical state transition, not a numerical error;
- post-slack response is not fully modelled.

### Branch B: calibrated cable_rod

Purpose: OpenSees-native approximation to a conductor with axial, bending, and
torsional stiffness.

Element:

```text
forceBeamColumn + Corotational transformation + fiber/elastic section
```

Interpretation:

- adds bending and torsion so low-tension zones do not immediately become
  zero-stiffness mechanisms;
- can represent post-slack/low-tension shapes more continuously than a pure
  truss chain;
- still needs careful interpretation because a beam/rod branch can carry axial
  compression in a way a real stranded conductor may release through local
  buckling, bending, or contact.

### Branch C: small-compression-regularized tension-only

Purpose: sensitivity branch only.

Element concept:

```text
tension-only axial response + very small compression/regularization stiffness
```

Interpretation:

- not a true compressive conductor model;
- used only to test whether the zero-tangent slack transition is causing a
  numerical mechanism;
- if results are strongly sensitive to the regularization ratio, post-slack
  response should not be reported as a robust physical prediction.

## Test plan

Use the same typical case and same wind input for:

1. current tension-only;
2. calibrated cable_rod;
3. small-compression-regularized tension-only.

Compare:

- first slack or low-tension time;
- first negative tension time, if applicable;
- first large-strain time;
- first attack-angle clipping time;
- continuity of displacement, velocity, acceleration, aerodynamic force, and
  aerodynamic power;
- achieved analysis time and OpenSees failure reason;
- sensitivity of post-slack response to structural branch.

The desired outcome is not to hide instability. The desired outcome is to know
whether the instability is a robust galloping/low-tension response or a branch
artifact caused by the pure tension-only truss model.
