# Manifest

Package root:

```text
D:\Pyprogramme\pylon1\teacher_c4_opensees_project
```

Core OpenSees files:

- `Input.tcl`
- `inputs_aerodynamic_damping.tcl`
- `run_opensees.ps1`
- `README.md`
- `case_config.yaml`
- `reference_analysis_status.txt`

Tcl procedures:

- `tcl_procedures/Damping_shifter.tcl`
- `tcl_procedures/Wind_velocity_reader.tcl`
- `tcl_procedures/dynamic2.tcl`
- `tcl_procedures/interpolate.tcl`
- `tcl_procedures/readColumnFromFile.tcl`
- `tcl_procedures/PROCEDURE_OLD.tcl`
- `tcl_procedures/PROCEDURE_Raf_6dof.tcl`

Data folders:

- `data/aero_coeffs/`
- `data/forces/FORCE_3/SIM1/`
- `data/wind/SIM1/`

Validation:

- The package was run from its own root folder using
  `powershell -ExecutionPolicy Bypass -File .\run_opensees.ps1`.
- The run reached `72.0 s`.
- The console reported `ANALYZE_RETURN_CODE 0`.
- Standard recorder outputs were generated in the package root, including
  `Dynamic.out`, `Velocity.out`, `Accel.out`, `Reaction.out`,
  `SupportReactions.out`, `Static.out`, and `Element1.out`.

Packaging note:

- Wind/force histories are truncated to the 72 s verification window
  (`1441` rows at `dt = 0.05 s`) to keep the attachment size manageable.
- Heavy custom append logs are disabled in this copied package. Full diagnostic
  logs and figures remain in the main project output folder.
