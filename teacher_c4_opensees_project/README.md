# C4 Typical OpenSees Project

This folder is a self-contained OpenSees engineering package for the latest
typical galloping verification case.

## Case

- Span: `L = 322.8 m`
- Sag: `H = 10.48 m`
- Wind case: `FORCE_3 / SIM1`, `u_star = 0.6`
- Time step: `dt = 0.05 s`
- Duration: `72 s`
- Initial-state route: C4 static gravity equilibrium
- Aero branch: incremental quasi-steady aerodynamic force
- Structural model: tension-only `corotTruss + ElasticPPGap + InitStrainMaterial`

## How To Run

From this folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_opensees.ps1
```

The script uses:

```text
D:\Pyprogramme\OpenSees3.8.0\bin\OpenSees.exe
```

If OpenSees is installed elsewhere, edit `run_opensees.ps1`.

## Included Files

- `Input.tcl`: final generated OpenSees model and analysis file.
- `inputs_aerodynamic_damping.tcl`: generated aerodynamic/diagnostic parameters.
- `tcl_procedures/`: Tcl procedures sourced by `Input.tcl`.
- `data/aero_coeffs/`: aerodynamic coefficient tables and truncated 72 s time vector.
- `data/forces/FORCE_3/SIM1/`: precomputed Path load files, truncated to the 72 s verification window.
- `data/wind/SIM1/`: wind velocity files, truncated to the 72 s verification window.
- `case_config.yaml`: Python-side configuration that generated this case.
- `reference_analysis_status.txt`: status from the successful reference run.

Note: this teacher-briefing package disables heavy custom Tcl append logs such
as per-node aerodynamic power CSVs, because some Windows/OpenSees Tcl builds
deny those append writes in a copied folder. The model, static C4 equilibrium,
Path wind loads, incremental quasi-steady force branch, and standard OpenSees
recorders remain active. The full diagnostic logs and figures are preserved in
the main project output:

```text
D:\Pyprogramme\pylon1\output\diagnostics\typical_incremental_qs_c4_static_balance\
```

## Expected Output

OpenSees writes output files in this project folder, for example:

```text
Dynamic.out
Velocity.out
Accel.out
SupportReactions.out
element_strain_tension_summary_log.csv
incremental_quasi_steady_aero_force_log.txt
analysis_status.txt
```

The reference successful run ended with:

```text
STATUS success
MESSAGE target_time_reached
TIME 72.0
ANALYZE_RETURN_CODE 0
```

This packaged version was also test-run successfully and printed:

```text
ANALYSIS_STATUS success
ANALYSIS_MESSAGE target_time_reached
ANALYZE_RETURN_CODE 0
```
