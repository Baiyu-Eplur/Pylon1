"""tests/test_geometry.py — unit tests for CableGeometry"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import math
import numpy as np
import pytest
from cable_analyser.geometry import CableGeometry


# ─── helpers ──────────────────────────────────────────────────────────────

def _geo_cfg(geo_type: int, L: float = 2.0, Sag: float = 1.0, disc: float = 1.0) -> dict:
    """Minimal config dict accepted by CableGeometry."""
    return {
        "geometry": {
            "type": geo_type,
            "L": L,
            "Sag": Sag,
            "discretisation": disc,
        },
        "material": {
            "Dia": 0.02862,
            "E": 82_000_000_000.0,
            "G": 4_265_000_000.0,
            "ro": 3480.0,
        },
        "analysis": {
            "multiplier_mass": 1.242584042,
        },
    }


def _make(geo_type, **kwargs) -> tuple[CableGeometry, dict]:
    cfg = _geo_cfg(geo_type, **kwargs)
    geo = CableGeometry(cfg)
    return geo, geo.generate()


# ─── geometry shape tests ─────────────────────────────────────────────────

def test_parabolic_endpoints():
    """Parabola: endpoints at z=0, midpoint sag = -Sag."""
    _, r = _make(1, L=10.0, Sag=2.0, disc=1.0)
    z = r["z"]
    assert z[0] == pytest.approx(0.0, abs=1e-12)
    assert z[-1] == pytest.approx(0.0, abs=1e-12)
    assert float(z.min()) == pytest.approx(-2.0, rel=1e-10)


def test_catenary_symmetry():
    """Catenary z-profile must be symmetric about L/2 to within 1e-10."""
    _, r = _make(2, L=10.0, Sag=2.0, disc=1.0)
    z = r["z"]
    # reverse of z (flip left-right) must equal z
    assert np.max(np.abs(z - z[::-1])) < 1e-10


def test_catenary_exact_sag():
    """Catenary midpoint must match the configured sag."""
    _, r = _make(2, L=10.0, Sag=2.0, disc=1.0)
    assert float(r["z"].min()) == pytest.approx(-2.0, abs=1e-10)


def test_broken_line_apex():
    """V-shape: apex at midpoint == -Sag; both ends at 0."""
    _, r = _make(3, L=2.0, Sag=1.0, disc=1.0)
    z = r["z"]
    N = len(z)
    assert z[N // 2] == pytest.approx(-1.0, abs=1e-12)   # apex
    assert z[0] == pytest.approx(0.0, abs=1e-12)
    assert z[-1] == pytest.approx(0.0, abs=1e-12)


# ─── tributary-length identity ────────────────────────────────────────────

def test_dx_sum_vs_DX_sum():
    """sum(DX) must equal sum(dx) for any geometry (exact identity)."""
    for geo_type in (1, 2, 3):
        _, r = _make(geo_type, L=10.0, Sag=2.0, disc=1.0)
        assert np.sum(r["DX"]) == pytest.approx(np.sum(r["dx"]), rel=1e-12)


# ─── section-property formula ─────────────────────────────────────────────

def test_self_weight_formula():
    """self_weight must equal Area * ro * g (not a hard-coded constant)."""
    Dia = 0.02862
    ro = 3480.0
    g = 9.80665
    Area = math.pi * Dia ** 2 / 4
    expected = Area * ro * g

    geo, _ = _make(3)          # geometry type irrelevant for section props
    assert abs(geo.self_weight - expected) < 1e-6


def test_self_weight_override():
    """Optional tabulated self-weight should override density-derived weight."""
    cfg = _geo_cfg(3)
    cfg["material"]["self_weight_N_per_m"] = 15.9
    geo = CableGeometry(cfg)
    assert geo.self_weight == pytest.approx(15.9, rel=1e-12)
