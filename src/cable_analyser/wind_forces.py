from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np


def _linear_extrapolate(x: np.ndarray, xp: np.ndarray, fp: np.ndarray) -> np.ndarray:
    values = np.interp(x, xp, fp)
    low = x < xp[0]
    high = x > xp[-1]
    if np.any(low):
        slope = (fp[1] - fp[0]) / (xp[1] - xp[0])
        values[low] = fp[0] + slope * (x[low] - xp[0])
    if np.any(high):
        slope = (fp[-1] - fp[-2]) / (xp[-1] - xp[-2])
        values[high] = fp[-1] + slope * (x[high] - xp[-1])
    return values


def _load_coefficient_table(path: Path) -> np.ndarray:
    try:
        return np.loadtxt(path, delimiter=",")
    except ValueError:
        return np.loadtxt(path)


def time_and_frequency(npt: int, dt: float) -> tuple[np.ndarray, np.ndarray]:
    """Return MATLAB-compatible time and positive-frequency vectors."""
    if npt <= 1:
        raise ValueError("npt must be greater than 1")
    if dt <= 0:
        raise ValueError("dt must be positive")
    duration = npt * dt
    time = np.arange(npt, dtype=float) * dt
    freq = np.arange(1, npt // 2 + 1, dtype=float) / duration
    return time, freq


def kaimal_model(
    mean_u: np.ndarray,
    heights: np.ndarray,
    freq: np.ndarray,
    u_star: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """MATLAB `KaimalModel.m` terms used by `WIND_SIMULATION.mlx`."""
    mean_u = np.asarray(mean_u, dtype=float)
    heights = np.asarray(heights, dtype=float)
    freq = np.asarray(freq, dtype=float)
    fr = freq[None, :] * heights[:, None] / mean_u[:, None]
    safe_freq = np.maximum(freq[None, :], 1e-15)
    su = 102.0 * fr / (1.0 + 33.0 * fr) ** (5.0 / 3.0) * u_star**2 / safe_freq
    sw = 2.0 * fr / (1.0 + 5.0 * fr ** (5.0 / 3.0)) * u_star**2 / safe_freq
    suw = -14.0 * fr / (1.0 + 10.5 * fr) ** (7.0 / 3.0) * u_star**2 / safe_freq
    return su, sw, suw


def davenport_coherence(
    mean_pair_u: np.ndarray,
    dy: np.ndarray,
    dz: np.ndarray,
    freq: float,
    cy: float,
    cz: float,
) -> np.ndarray:
    ay = cy * dy
    az = cz * dz
    return np.exp(-np.sqrt(ay**2 + az**2) * freq / mean_pair_u)


def _sqrt_psd_matrix(matrix: np.ndarray) -> np.ndarray:
    matrix = 0.5 * (matrix + matrix.T)
    try:
        return np.linalg.cholesky(matrix + np.eye(matrix.shape[0]) * 1e-14)
    except np.linalg.LinAlgError:
        eigval, eigvec = np.linalg.eigh(matrix)
        eigval = np.clip(eigval, 0.0, None)
        return (eigvec * np.sqrt(eigval)) @ eigvec.T


def simulate_wind(
    x: np.ndarray,
    z: np.ndarray,
    *,
    u_star: float,
    dt: float,
    npt: int,
    support_elevation: float = 49.4,
    kappa: float = 0.387,
    z0: float = 0.05,
    c_u_y: float = 7.0,
    c_u_z: float = 10.0,
    c_w_y: float = 6.5,
    c_w_z: float = 3.0,
    seed: int | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    """Generate longitudinal and vertical wind histories.

    This ports the friction-based branch of `WIND_SIMULATION.mlx`.
    """
    if u_star <= 0:
        raise ValueError("u_star must be positive")
    x = np.asarray(x, dtype=float)
    z = np.asarray(z, dtype=float)
    heights = support_elevation + z
    if np.any(heights <= z0):
        raise ValueError("all node heights must be greater than z0")

    time, freq = time_and_frequency(npt, dt)
    n_nodes = len(x)
    mean_u = u_star / kappa * np.log(heights / z0)
    su, sw, suw = kaimal_model(mean_u, heights, freq, u_star)

    dy = np.abs(x[:, None] - x[None, :])
    dz = np.abs(heights[:, None] - heights[None, :])
    mean_pair_u = 0.5 * np.abs(mean_u[:, None] + mean_u[None, :])

    rng = np.random.default_rng(seed)
    spectrum = np.zeros((len(freq), 2 * n_nodes), dtype=np.complex128)

    for idx, f in enumerate(freq):
        phase = np.exp(1j * 2.0 * np.pi * rng.random(2 * n_nodes))
        coh_u = davenport_coherence(mean_pair_u, dy, dz, f, c_u_y, c_u_z)
        coh_w = davenport_coherence(mean_pair_u, dy, dz, f, c_w_y, c_w_z)
        suu = np.sqrt(np.outer(su[:, idx], su[:, idx])) * coh_u
        sww = np.sqrt(np.outer(sw[:, idx], sw[:, idx])) * coh_w
        suuw = np.sqrt(np.outer(suw[:, idx], suw[:, idx]).astype(complex))
        suuw = np.real_if_close(suuw * np.sqrt(coh_u * coh_w), tol=1000)
        s = np.block([[suu, suuw], [suuw, sww]]).astype(float)
        spectrum[idx, :] = _sqrt_psd_matrix(s) @ phase

    nu = np.vstack(
        [
            np.zeros((1, 2 * n_nodes), dtype=np.complex128),
            spectrum[:-1, :],
            np.real(spectrum[-1:, :]),
            np.conj(np.flipud(spectrum[:-1, :])),
        ]
    )
    speed = np.real(np.fft.ifft(nu, axis=0) * math.sqrt(len(freq) / dt))
    u = speed[:, :n_nodes] + mean_u[None, :]
    w = speed[:, n_nodes:]

    meta = {
        "u_star_mps": float(u_star),
        "kappa": float(kappa),
        "z0_m": float(z0),
        "support_elevation_m": float(support_elevation),
        "dt_s": float(dt),
        "npt": int(npt),
        "duration_s": float(npt * dt),
        "seed": seed,
        "mean_H_mps": {
            "global": float(np.mean(u)),
            "min_node": float(np.min(np.mean(u, axis=0))),
            "max_node": float(np.max(np.mean(u, axis=0))),
        },
        "mean_V_mps": float(np.mean(w)),
    }
    return time, u, w, meta


def compute_aerodynamic_forces(
    u: np.ndarray,
    w: np.ndarray,
    *,
    diameter: float,
    discretisation: float,
    aero_coeffs_dir: Path,
    ro_air_force: float = 1.293 / 1000.0,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Compute updating-coefficient drag/lift force components."""
    if diameter <= 0:
        raise ValueError("diameter must be positive")
    u = np.asarray(u, dtype=float)
    w = np.asarray(w, dtype=float)
    if u.shape != w.shape:
        raise ValueError("u and w must have the same shape")

    npt, n_nodes = u.shape
    alpha = np.arctan2(w, u)
    cd_data = _load_coefficient_table(aero_coeffs_dir / "C_D_data.txt")
    cl_data = _load_coefficient_table(aero_coeffs_dir / "C_L_data2.txt")
    alpha_deg = np.abs(np.rad2deg(alpha))
    cd = _linear_extrapolate(alpha_deg, cd_data[:, 0], cd_data[:, 1])
    cl = _linear_extrapolate(alpha_deg, cl_data[:, 0], cl_data[:, 1])

    node_area = np.ones(n_nodes) * discretisation * math.pi * diameter / 2.0
    node_area[0] *= 0.5
    node_area[-1] *= 0.5
    areas = np.broadcast_to(node_area[None, :], (npt, n_nodes))

    u_total = np.sqrt(u**2 + w**2)
    f_drag = 0.5 * cd * ro_air_force * u_total**2 * areas
    f_lift = 0.5 * cl * ro_air_force * u_total**2 * areas

    forces = {
        "H_drag": f_drag * np.cos(alpha),
        "V_drag": f_drag * np.sin(alpha),
        "H_lift": f_lift * np.cos(alpha + math.pi / 2.0),
        "V_lift": f_lift * np.sin(alpha + math.pi / 2.0),
        "wind_H": u,
        "wind_V": w,
        "wind_T": u_total,
    }
    meta = {
        "diameter_m": float(diameter),
        "projected_area_formula": "discretisation * pi * diameter / 2, half at end nodes",
        "ro_air_force_ton_per_m3": float(ro_air_force),
        "force_file_units": "kN-equivalent before OpenSees load factor 1000",
        "cd_range": [float(np.min(cd)), float(np.max(cd))],
        "cl_range": [float(np.min(cl)), float(np.max(cl))],
        "alpha_deg_range": [float(np.min(alpha_deg)), float(np.max(alpha_deg))],
    }
    return forces, meta


def write_force_case(
    *,
    time: np.ndarray,
    forces: dict[str, np.ndarray],
    force_dir: Path,
    wind_dir: Path,
    time_file: Path,
    metadata: dict[str, Any],
    overwrite: bool = False,
) -> None:
    """Write MATLAB-compatible NODE_* files and metadata."""
    force_dir = Path(force_dir)
    wind_dir = Path(wind_dir)
    time_file = Path(time_file)
    if force_dir.exists() and any(force_dir.iterdir()) and not overwrite:
        raise FileExistsError(f"{force_dir} already exists and is not empty")
    if wind_dir.exists() and any(wind_dir.iterdir()) and not overwrite:
        raise FileExistsError(f"{wind_dir} already exists and is not empty")

    force_dir.mkdir(parents=True, exist_ok=True)
    wind_dir.mkdir(parents=True, exist_ok=True)
    time_file.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(time_file, time, fmt="%.10g")

    force_components = ("H_drag", "H_lift", "V_drag", "V_lift")
    wind_components = ("wind_H", "wind_V", "wind_T")
    n_nodes = forces["wind_H"].shape[1]
    for node_idx in range(n_nodes):
        node_id = node_idx + 1
        for comp in force_components:
            np.savetxt(force_dir / f"NODE_{node_id}_{comp}.txt", forces[comp][:, node_idx], fmt="%.10g")
        for comp in wind_components:
            data = forces[comp][:, node_idx]
            np.savetxt(force_dir / f"NODE_{node_id}_{comp}.txt", data, fmt="%.10g")
            np.savetxt(wind_dir / f"NODE_{node_id}_{comp}.txt", data, fmt="%.10g")

    metadata = dict(metadata)
    metadata["force_dir"] = str(force_dir)
    metadata["wind_dir"] = str(wind_dir)
    metadata["time_file"] = str(time_file)
    metadata["n_nodes"] = int(n_nodes)
    (force_dir / "generation_metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )


def generate_wind_force_case(
    cfg: dict,
    geo: dict,
    *,
    root: Path | str = ".",
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate wind velocities and force files from a project config."""
    root = Path(root)
    gen = dict(cfg.get("wind_generation", {}))
    if overrides:
        gen.update({k: v for k, v in overrides.items() if v is not None})

    th = cfg["time_history"]
    paths = cfg["paths"]
    material = cfg["material"]
    geom = cfg["geometry"]
    force_name = str(gen.get("force_name", th["folder_1"][0]))
    sim_name = str(gen.get("sim_name", th["folder_2"][0]))
    wind_dir = root / str(gen.get("wind_dir", paths.get("wind_dir", f"data/wind/{sim_name}")))
    force_dir = root / str(paths["forces_dir"]) / force_name / sim_name
    time_file = root / str(gen.get("time_file", paths.get("time_file", "data/aero_coeffs/time.txt")))
    metadata_path = force_dir / "generation_metadata.json"
    if (
        bool(gen.get("reuse_existing", True))
        and not bool(gen.get("overwrite", False))
        and metadata_path.exists()
        and wind_dir.exists()
        and time_file.exists()
    ):
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        existing_u_star = float(metadata.get("wind", {}).get("u_star_mps", float("nan")))
        requested_u_star = float(gen["u_star"])
        if not math.isclose(existing_u_star, requested_u_star, rel_tol=1e-9, abs_tol=1e-12):
            raise FileExistsError(
                f"{force_dir} already contains u_star={existing_u_star}; "
                f"requested u_star={requested_u_star}. Use a new force_name or overwrite=true."
            )
        return metadata

    time, u, w, wind_meta = simulate_wind(
        geo["x"],
        geo["z"],
        u_star=float(gen["u_star"]),
        dt=float(gen.get("dt", th["dt"])),
        npt=int(gen.get("npt", th["npt"])),
        support_elevation=float(gen.get("support_elevation", 49.4)),
        kappa=float(gen.get("kappa", 0.387)),
        z0=float(gen.get("z0", 0.05)),
        c_u_y=float(gen.get("c_u_y", 7.0)),
        c_u_z=float(gen.get("c_u_z", 10.0)),
        c_w_y=float(gen.get("c_w_y", 6.5)),
        c_w_z=float(gen.get("c_w_z", 3.0)),
        seed=gen.get("seed"),
    )
    forces, force_meta = compute_aerodynamic_forces(
        u,
        w,
        diameter=float(material["Dia"]),
        discretisation=float(geom["discretisation"]),
        aero_coeffs_dir=root / str(paths.get("aero_coeffs_dir", "data/aero_coeffs")),
        ro_air_force=float(gen.get("ro_air_force", 1.293 / 1000.0)),
    )
    metadata = {
        "source": "src.cable_analyser.wind_forces",
        "matlab_reference": "D:/Uob/Tower Pylon/TIMUR2/WIND_SIMULATION.mlx",
        "force_name": force_name,
        "sim_name": sim_name,
        "wind": wind_meta,
        "force": force_meta,
    }
    write_force_case(
        time=time,
        forces=forces,
        force_dir=force_dir,
        wind_dir=wind_dir,
        time_file=time_file,
        metadata=metadata,
        overwrite=bool(gen.get("overwrite", False)),
    )
    return metadata
