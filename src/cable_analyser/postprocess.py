# postprocess.py — load OpenSees output files and compute response quantities
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════
# Loaders
# ═══════════════════════════════════════════════════════════════════════════

def load_reaction(output_dir: str) -> np.ndarray:
    """Load Output/Reaction.out and return the force columns only.

    File layout (OpenSees recorder Node output):
        With -time flag:    time  Rx  Ry  Rz   (4 columns)
        Without -time flag: Rx  Ry  Rz          (3 columns)
    Comment lines starting with '#' are skipped.

    Returns
    -------
    np.ndarray, shape (T, 3) — columns [Rx, Ry, Rz] in Newtons.
    """
    path = Path(output_dir) / "Reaction.out"
    data = np.loadtxt(path, comments="#")
    if data.ndim == 1:
        data = data[np.newaxis, :]
    # 4 cols → [time, Rx, Ry, Rz]: skip column 0
    # 3 cols → [Rx, Ry, Rz]:       use as-is
    return data[:, -3:]


def load_displacement(output_dir: str, n_nodes: int) -> tuple[np.ndarray, np.ndarray]:
    """Load Output/Dynamic.out and split into Y and Z displacement matrices.

    File layout per row:
        Without -time:  X1  Y1  Z1  X2  Y2  Z2  ...  XN  YN  ZN      (3N cols)
        With -time:     time  X1  Y1  Z1  X2  Y2  Z2  ...  XN  YN  ZN (3N+1 cols)

    Slicing (after stripping the optional time column):
        Y  ←  data[:, 1::3]
        Z  ←  data[:, 2::3]

    Returns
    -------
    Y : np.ndarray, shape (T, n_nodes)
    Z : np.ndarray, shape (T, n_nodes)
    """
    path = Path(output_dir) / "Dynamic.out"
    data = np.loadtxt(path, comments="#")
    # Strip leading time column if present (3N+1 cols → 3N cols)
    if data.shape[1] % 3 != 0:
        data = data[:, 1:]
    Y = data[:, 1::3]   # lateral (horizontal) displacement
    Z = data[:, 2::3]   # vertical displacement
    return Y, Z


# ═══════════════════════════════════════════════════════════════════════════
# Response quantity computations
# ═══════════════════════════════════════════════════════════════════════════

def compute_max_reaction(R: np.ndarray) -> float:
    """Return the peak resultant reaction force.

    Parameters
    ----------
    R : shape (T, 3) — [Rx, Ry, Rz] in Newtons.

    Returns
    -------
    float — max(R_resultant) in Newtons.
    """
    R_resultant = np.sqrt(R[:, 0] ** 2 + R[:, 1] ** 2 + R[:, 2] ** 2)
    return float(np.max(R_resultant))


def compute_max_displacement(Y: np.ndarray, Z: np.ndarray) -> float:
    """Return the peak resultant nodal displacement across all nodes and time.

    Parameters
    ----------
    Y, Z : shape (T, n_nodes) — lateral and vertical displacements (m).

    Returns
    -------
    float — max(sqrt(Y² + Z²)) in metres.
    """
    DTOT = np.sqrt(Y ** 2 + Z ** 2)
    return float(np.max(DTOT))


def compute_clearance(
    Y: np.ndarray,
    Z: np.ndarray,
    z_static: np.ndarray,
) -> np.ndarray:
    """Compute the dynamic clearance deviation from the static geometry.

    For each node i (0-indexed):
        P_NEW_Z[:, i] = z_static[i] + Z[:, i]
        clearance[:, i] = sqrt(Y[:, i]² + P_NEW_Z[:, i]²) − |z_static[i]|

    Parameters
    ----------
    Y, Z      : shape (T, n_nodes)
    z_static  : shape (n_nodes,) — static equilibrium z-coordinates (m).

    Returns
    -------
    np.ndarray, shape (T, n_nodes) — clearance at every node and time step.
    """
    n_nodes = Y.shape[1]
    clearance = np.empty_like(Y)
    for i in range(n_nodes):
        P_NEW_Z = z_static[i] + Z[:, i]
        clearance[:, i] = np.sqrt(Y[:, i] ** 2 + P_NEW_Z ** 2) - abs(z_static[i])
    return clearance


# ═══════════════════════════════════════════════════════════════════════════
# Results persistence and summary
# ═══════════════════════════════════════════════════════════════════════════

def save_results(results: dict, output_dir: str, prefix: str) -> None:
    """Save MAX_DISP / MAX_REAC / MAX_CLEARANCE matrices to CSV and print summary.

    Expected keys in *results*:
        "MAX_DISP"      : np.ndarray, shape (n_force, n_sim)
        "MAX_REAC"      : np.ndarray, shape (n_force, n_sim), in kN
        "MAX_CLEARANCE" : np.ndarray, shape (n_force, n_sim)
        "folder_1"      : list[str]   row labels (FORCE_x names)
        "folder_2"      : list[str]   column labels (SIMx names)

    Output files:
        {output_dir}/{prefix}_MAX_DISP.csv
        {output_dir}/{prefix}_MAX_REAC.csv
        {output_dir}/{prefix}_MAX_CLEARANCE.csv
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    row_labels = results.get("folder_1", None)
    col_labels = results.get("folder_2", None)

    for key, filename in [
        ("MAX_DISP",      f"{prefix}_MAX_DISP.csv"),
        ("MAX_REAC",      f"{prefix}_MAX_REAC.csv"),
        ("MAX_CLEARANCE", f"{prefix}_MAX_CLEARANCE.csv"),
    ]:
        matrix = np.atleast_2d(results[key])
        df = pd.DataFrame(matrix, index=row_labels, columns=col_labels)
        df.to_csv(out / filename)

    # ── Console summary (matches MATLAB disp format) ──────────────────
    max_reac = float(np.max(results["MAX_REAC"]))
    max_disp = float(np.max(results["MAX_DISP"]))
    max_clr  = float(np.max(results["MAX_CLEARANCE"]))

    sep = "***********************"
    print(sep)
    print(f"Max tension load as reaction = {max_reac:.2f} kN")
    print(sep)
    print(f"Max displacement = {max_disp:.4f} m")
    print(sep)
    print(f"Max clearance = {max_clr:.4f} m")
    print(sep)
