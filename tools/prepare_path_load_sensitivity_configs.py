from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import numpy as np
import yaml


ROOT = Path(__file__).resolve().parents[1]
BASE_CONFIG = (
    ROOT
    / "output"
    / "diagnostics"
    / "cable_rod_long_test"
    / "calibrated_cable_rod_node_balance_72s_v2"
    / "calibrated_cable_rod_node_balance_72s_v2.yaml"
)
SOURCE_FORCE = ROOT / "data" / "forces" / "FORCE_3" / "SIM1"
SOURCE_WIND = ROOT / "data" / "wind" / "SIM1"
OUT_ROOT = ROOT / "output" / "diagnostics" / "cable_rod_long_test" / "path_load_sensitivity"

NODES = 101
SOURCE_DT = 0.05
TARGET_SECONDS = 72.0
SOURCE_N = int(TARGET_SECONDS / SOURCE_DT) + 1
COMPONENTS = ["H_drag", "H_lift", "V_drag", "V_lift", "wind_H", "wind_T", "wind_V"]
WIND_COMPONENTS = ["wind_H", "wind_T", "wind_V"]


def load_component_matrix(component: str) -> np.ndarray:
    rows = []
    for node in range(1, NODES + 1):
        rows.append(np.loadtxt(SOURCE_FORCE / f"NODE_{node}_{component}.txt", max_rows=SOURCE_N))
    return np.asarray(rows)


def write_force_matrix(force_dir: Path, component: str, matrix: np.ndarray) -> None:
    force_dir.mkdir(parents=True, exist_ok=True)
    for node in range(1, NODES + 1):
        np.savetxt(force_dir / f"NODE_{node}_{component}.txt", matrix[node - 1], fmt="%.12g")


def write_wind_dir(wind_dir: Path, matrices: dict[str, np.ndarray]) -> None:
    wind_dir.mkdir(parents=True, exist_ok=True)
    for component in WIND_COMPONENTS:
        matrix = matrices[component]
        for node in range(1, NODES + 1):
            np.savetxt(wind_dir / f"NODE_{node}_{component}.txt", matrix[node - 1], fmt="%.12g")


def resample_matrix(matrix: np.ndarray, dt_new: float) -> np.ndarray:
    source_time = np.arange(SOURCE_N) * SOURCE_DT
    target_n = int(TARGET_SECONDS / dt_new) + 1
    target_time = np.arange(target_n) * dt_new
    return np.vstack([np.interp(target_time, source_time, row) for row in matrix])


def smooth_matrix_spatial(matrix: np.ndarray) -> np.ndarray:
    # Symmetric 5-point binomial smoothing along node index. Edge padding avoids
    # artificial end-node force loss.
    kernel = np.asarray([1.0, 4.0, 6.0, 4.0, 1.0]) / 16.0
    padded = np.pad(matrix, ((2, 2), (0, 0)), mode="edge")
    out = np.zeros_like(matrix)
    for i, weight in enumerate(kernel):
        out += weight * padded[i : i + matrix.shape[0], :]
    return out


def write_config(
    case_name: str,
    force_name: str,
    sim_name: str,
    wind_dir: Path,
    time_file: Path,
    dt: float,
    npt: int,
    rationale: str,
) -> Path:
    cfg = deepcopy(yaml.safe_load(BASE_CONFIG.read_text(encoding="utf-8")))
    cfg["time_history"]["folder_1"] = [force_name]
    cfg["time_history"]["folder_2"] = [sim_name]
    cfg["time_history"]["dt"] = dt
    cfg["time_history"]["npt"] = npt
    cfg["paths"]["wind_dir"] = str(wind_dir.relative_to(ROOT)).replace("\\", "/")
    cfg["paths"]["time_file"] = str(time_file.relative_to(ROOT)).replace("\\", "/")
    cfg["paths"]["output_dir"] = str((OUT_ROOT / case_name / "run").relative_to(ROOT)).replace("\\", "/")
    cfg["paths"]["save_prefix"] = case_name.upper()
    cfg["diagnostics"]["node_force_balance_enabled"] = True
    cfg["diagnostics"]["node_force_balance_log_stride"] = 1
    cfg["diagnostics"]["element_strain_log_stride"] = 1
    cfg["diagnostics"]["rationale"] = rationale
    cfg["incremental_quasi_steady_aero_force"]["log_stride"] = 1
    cfg["event_stop"] = {
        "enabled": False,
        "rationale": "No response-based active stop. Fixed target duration only.",
    }
    cfg["sensitivity_case"] = {
        "name": case_name,
        "rationale": rationale,
        "force_name": force_name,
        "sim_name": sim_name,
        "wind_dir": cfg["paths"]["wind_dir"],
        "time_file": cfg["paths"]["time_file"],
    }
    out_dir = OUT_ROOT / case_name
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{case_name}.yaml"
    path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    return path


def main() -> None:
    matrices = {component: load_component_matrix(component) for component in COMPONENTS}

    configs: list[Path] = []

    # Case 1: same spatial field, half time step, linearly interpolated force
    # histories. This checks time-step and Path-load temporal interpolation.
    dt_half = 0.025
    force_name = "FORCE_DIAG_TEMP_INTERP_0P025_72S"
    sim_name = "SIM1"
    force_dir = ROOT / "data" / "forces" / force_name / sim_name
    wind_dir = ROOT / "data" / "wind" / "SIM_DIAG_TEMP_INTERP_0P025_72S"
    time_file = ROOT / "data" / "wind" / "time_diag_temp_interp_0p025_72s.txt"
    resampled = {component: resample_matrix(matrix, dt_half) for component, matrix in matrices.items()}
    for component, matrix in resampled.items():
        write_force_matrix(force_dir, component, matrix)
    write_wind_dir(wind_dir, resampled)
    np.savetxt(time_file, np.arange(resampled["H_drag"].shape[1]) * dt_half, fmt="%.12g")
    configs.append(
        write_config(
            "temporal_interp_dt0p025_72s",
            force_name,
            sim_name,
            wind_dir,
            time_file,
            dt_half,
            int(TARGET_SECONDS / dt_half),
            "Sensitivity control: same FORCE_3/SIM1 field linearly interpolated to dt=0.025 s.",
        )
    )

    # Case 2: same temporal sampling, spatially smoothed nodal histories. This
    # checks whether adjacent-node high-wavenumber forcing drives local modes.
    force_name = "FORCE_DIAG_SPATIAL_SMOOTH5_72S"
    sim_name = "SIM1"
    force_dir = ROOT / "data" / "forces" / force_name / sim_name
    wind_dir = ROOT / "data" / "wind" / "SIM_DIAG_SPATIAL_SMOOTH5_72S"
    time_file = ROOT / "data" / "wind" / "time_diag_spatial_smooth5_72s.txt"
    smoothed = {component: smooth_matrix_spatial(matrix) for component, matrix in matrices.items()}
    for component, matrix in smoothed.items():
        write_force_matrix(force_dir, component, matrix)
    write_wind_dir(wind_dir, smoothed)
    np.savetxt(time_file, np.arange(SOURCE_N) * SOURCE_DT, fmt="%.12g")
    configs.append(
        write_config(
            "spatial_smooth5_dt0p05_72s",
            force_name,
            sim_name,
            wind_dir,
            time_file,
            SOURCE_DT,
            int(TARGET_SECONDS / SOURCE_DT),
            "Sensitivity control: same FORCE_3/SIM1 histories smoothed along node index with a 5-point binomial kernel.",
        )
    )

    manifest = {
        "source_force_dir": str(SOURCE_FORCE.relative_to(ROOT)),
        "source_wind_dir": str(SOURCE_WIND.relative_to(ROOT)),
        "target_seconds": TARGET_SECONDS,
        "configs": [str(path.relative_to(ROOT)) for path in configs],
    }
    (OUT_ROOT / "path_load_sensitivity_manifest.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
    )
    for path in configs:
        print(path)


if __name__ == "__main__":
    main()
