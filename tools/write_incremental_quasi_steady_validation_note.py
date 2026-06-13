from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "diagnostics" / "typical_incremental_quasi_steady_validity_stop"
NOTE = OUT / "incremental_quasi_steady_validation_note.md"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    NOTE.write_text(
        """# Incremental Quasi-Steady Aero Branch Validation Note

## 1. Modification Summary

The new branch keeps the original OpenSees `Path` wind-force histories and adds
only a real-time motion correction:

```text
F_applied(t) = F_original_path(t) + Delta_F_motion(t)
Delta_F_motion(t) = F_current(t) - F_reference(t)
```

`F_reference` is reconstructed directly from the same original nodal force
files that are applied by OpenSees `Path` time series. `F_current` is computed
at each node with the current deformed local direction, the nodal wind velocity,
and the full relative velocity `wind - cable_velocity`. Therefore the added
load is the difference between the current quasi-steady aerodynamic state and
the exact original baseline already present in the model.

This is different from the previous explicit equivalent-damping branch, which
directly used a scalar Den Hartog damping coefficient. That earlier branch could
produce unrealistically large force growth when cable velocity became large.

## 2. Physical Rationale

Galloping is a self-excited aeroelastic mechanism. The aerodynamic force should
depend on the instantaneous relative wind seen by the moving cable and on the
local aerodynamic orientation of the deformed cable segment. The new branch
matches that requirement more closely than the original velocity-only
approximation because it:

- uses the deformed nodal tangent to define the local aerodynamic plane;
- computes drag and lift from the local nodal relative flow at every OpenSees
  step;
- subtracts the exact original nodal baseline so the original turbulent wind
  loading is not double-counted or replaced.

## 3. Numerical Reasonableness Checks

The diagnostic log explicitly records:

- `F_original`: total absolute original precomputed nodal wind force;
- `F_reference`: the exact original baseline reconstructed from the force files;
- `F_current`: quasi-steady force under wind-minus-cable relative velocity;
- `Delta_F_motion`: the applied motion correction;
- `total_abs_delta_force`: total absolute applied correction.

This makes the energy-input pathway auditable. In the latest validity-stop
typical run, `F_original` and `F_reference` are identical by construction and in
the output, confirming that the static baseline is not counted twice. The
motion/direction correction remains nonlinear, but it is not an artificial
Den-Hartog scalar damping force that is forced to act along the velocity vector.

## 4. Agreement With Published Galloping Behaviour

The response pattern is qualitatively consistent with galloping studies:

- the response remains bounded at first;
- effective aerodynamic damping is frequently negative;
- after an onset period, coupled transverse/vertical motion grows quickly;
- the x-z trajectory expands rather than remaining a small random vibration.

However, quantitative large-amplitude interpretation is limited by the available
aerodynamic coefficient table. The table ends at about `29.9 deg`. Therefore the
formal workflow now stops when the current attack angle leaves this table. The
onset and entry into the validity boundary are meaningful; post-boundary
large-amplitude response requires a wider aerodynamic coefficient table.

## 5. Interruption / Termination Interpretation

The earlier no-stop incremental run was externally stopped by command timeout,
not by an OpenSees `-3` convergence failure. The latest formal run stopped
normally with OpenSees return code `0` because the configured event stop detected
that the current quasi-steady attack angle exceeded the available coefficient
table. This is a model-validity stop, not a numerical solver failure.

## 6. Current Verdict

The baseline-matched incremental quasi-steady branch is the preferred current
mechanism because it preserves the original wind input, avoids double-counting
the precomputed loads, lets motion-driven aerodynamic feedback enter the
OpenSees time-domain equations, and exposes the force budget directly in the
output logs.

The remaining limitation is not the branch logic itself, but the aerodynamic
coefficient range. Future quantitative post-onset studies require either:

- a wider aerodynamic coefficient table covering high angles of attack, or
- an explicit research convention that treats angle-table exit as the event
  defining severe galloping onset / invalid post-onset response.
""",
        encoding="utf-8",
    )
    print(NOTE)


if __name__ == "__main__":
    main()
