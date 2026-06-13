"""tests/test_postprocess.py — unit tests for postprocess functions"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import pytest
from cable_analyser.postprocess import (
    load_reaction,
    load_displacement,
    compute_max_reaction,
    compute_max_displacement,
    compute_clearance,
)


# ─── loader tests ─────────────────────────────────────────────────────────

def test_displacement_column_indexing(tmp_path):
    """Y = data[:, 1::3] and Z = data[:, 2::3] (mirrors MATLAB d(:,2:3:end))."""
    # 2 time steps × 2 nodes → 6 columns: X1 Y1 Z1 X2 Y2 Z2
    raw = np.array([
        [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0, 10.0, 11.0, 12.0],
    ])
    np.savetxt(tmp_path / "Dynamic.out", raw)

    Y, Z = load_displacement(str(tmp_path), n_nodes=2)

    np.testing.assert_array_equal(Y, raw[:, 1::3])
    np.testing.assert_array_equal(Z, raw[:, 2::3])


def test_load_reaction_shape(tmp_path):
    """load_reaction must return shape (T, 3) — time column stripped."""
    raw = np.array([
        [0.05, 100.0, -200.0, 50.0],
        [0.10, 110.0, -210.0, 55.0],
    ])
    np.savetxt(tmp_path / "Reaction.out", raw)

    R = load_reaction(str(tmp_path))

    assert R.shape == (2, 3)
    np.testing.assert_array_equal(R, raw[:, 1:4])


def test_load_reaction_skips_comments(tmp_path):
    """Comment lines starting with '#' must be ignored."""
    (tmp_path / "Reaction.out").write_text(
        "# OpenSees recorder output\n"
        "0.05 3.0 4.0 0.0\n"
        "0.10 6.0 8.0 0.0\n"
    )
    R = load_reaction(str(tmp_path))
    assert R.shape == (2, 3)


# ─── compute_max_reaction ─────────────────────────────────────────────────

def test_resultant_reaction():
    """[3, 4, 0] → resultant == 5 (3-4-5 triangle)."""
    R = np.array([[3.0, 4.0, 0.0]])
    assert compute_max_reaction(R) == pytest.approx(5.0, rel=1e-10)


def test_max_reaction_picks_maximum():
    """Peak over multiple time steps is returned."""
    R = np.array([
        [0.0, 0.0, 1.0],   # resultant 1
        [3.0, 4.0, 0.0],   # resultant 5 ← max
        [1.0, 0.0, 0.0],   # resultant 1
    ])
    assert compute_max_reaction(R) == pytest.approx(5.0, rel=1e-10)


# ─── compute_max_displacement ─────────────────────────────────────────────

def test_max_displacement_purely_vertical():
    """Pure Z displacement → resultant equals |Z|."""
    Y = np.zeros((5, 3))
    Z = np.full((5, 3), 0.25)
    Z[2, 1] = 0.7   # planted maximum
    assert compute_max_displacement(Y, Z) == pytest.approx(0.7, rel=1e-10)


# ─── compute_clearance ────────────────────────────────────────────────────

def test_clearance_zero_displacement():
    """When Y=0 and Z=0, clearance must be exactly 0 at every node and step.

    Derivation:
      P_NEW_Z = z_static[i] + 0 = z_static[i]
      clearance = sqrt(0 + z_static[i]^2) - |z_static[i]| = 0
    """
    T, N = 10, 5
    Y = np.zeros((T, N))
    Z = np.zeros((T, N))
    z_static = np.array([0.0, -0.5, -1.0, -0.5, 0.0])

    clearance = compute_clearance(Y, Z, z_static)

    np.testing.assert_allclose(clearance, 0.0, atol=1e-12)


def test_clearance_formula():
    """Single-node, single-step: verify the exact clearance formula.

    z_static = -1.0,  Y_dyn = 0.3,  Z_dyn = 0.4
      P_NEW_Z = -1.0 + 0.4 = -0.6
      clearance = sqrt(0.3^2 + (-0.6)^2) - |-1.0|
               = sqrt(0.09 + 0.36) - 1.0
               = sqrt(0.45) - 1.0
    """
    Y = np.array([[0.3]])
    Z = np.array([[0.4]])
    z_static = np.array([-1.0])

    expected = np.sqrt(0.3 ** 2 + (-0.6) ** 2) - 1.0

    clearance = compute_clearance(Y, Z, z_static)
    assert clearance[0, 0] == pytest.approx(expected, rel=1e-10)


def test_clearance_shape():
    """Output shape must be (T, n_nodes)."""
    T, N = 20, 4
    Y = np.random.rand(T, N)
    Z = np.random.rand(T, N)
    z_static = np.linspace(-1.0, 0.0, N)
    clearance = compute_clearance(Y, Z, z_static)
    assert clearance.shape == (T, N)
