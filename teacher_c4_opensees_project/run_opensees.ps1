$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$opensees = "D:\Pyprogramme\OpenSees3.8.0\bin\OpenSees.exe"

if (-not (Test-Path -LiteralPath $opensees)) {
    throw "OpenSees executable not found: $opensees"
}

Set-Location -LiteralPath $projectDir

$outputFiles = @(
    "Dynamic.out", "Reaction.out", "SupportReactions.out", "Velocity.out", "Accel.out",
    "Static.out", "Element1.out", "analysis_status.txt", "damping_change_log.txt",
    "element_strain_tension_log.csv", "element_strain_tension_summary_log.csv",
    "incremental_qs_node_power_log.csv", "incremental_quasi_steady_aero_force_log.txt",
    "realtime_state.txt", "event_stop_log.txt"
)
foreach ($file in $outputFiles) {
    if (Test-Path -LiteralPath $file) {
        Remove-Item -LiteralPath $file -Force
    }
}

& $opensees "Input.tcl"
