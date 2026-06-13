"""tests/test_tcl_writer.py — unit tests for TclWriter"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from cable_analyser.geometry import CableGeometry
from cable_analyser.tcl_writer import TclWriter


# ─── fixtures / helpers ───────────────────────────────────────────────────

def _full_cfg(output_dir: str) -> dict:
    """Full config dict for TclWriter (uses L=2, disc=1 → 3 nodes)."""
    return {
        "geometry": {
            "type": 3,
            "L": 2.0,
            "Sag": 1.0,
            "discretisation": 1.0,
        },
        "material": {
            "Dia": 0.02862,
            "E": 82_000_000_000.0,
            "G": 4_265_000_000.0,
            "ro": 3480.0,
        },
        "analysis": {
            "type": "TH",
            "fiber_section": 1,
            "pretension_load": 0.0,
            "multiplier_vertical_load": 1.242584042,
            "multiplier_mass": 1.242584042,
            "numbers_of_step_gravity": 10,
            "tolerance": 1e-3,
            "number_of_modes": 2,
        },
        "time_history": {
            "folder_1": ["FORCE_3"],
            "folder_2": ["Test1"],
            "dt": 0.05,
            "npt": 100,
            "ro_air": 1.204,
        },
        "damping": {
            "model": "Rayleigh",
            "xi": 0.01,
            "modes_for_damping": 10,
        },
        "aerodynamic_force": {
            "enabled": False,
            "scale": 1.0,
            "log_stride": 20,
        },
        "aerodynamic_damping": {
            "enabled": True,
            "writeback_mode": "record_only",
            "use_deformed_element_direction": True,
        },
        "quasi_steady_aero_force": {
            "enabled": False,
            "scale": 1.0,
            "log_stride": 20,
            "use_precomputed_loads": True,
        },
        "incremental_quasi_steady_aero_force": {
            "enabled": False,
            "scale": 1.0,
            "log_stride": 20,
            "keep_precomputed_loads": True,
        },
        "solver": {
            "opensees_path": "opensees",
            "input_tcl": "Input.tcl",
            "work_dir": ".",
        },
        "paths": {
            "forces_dir": "data/forces",
            "wind_dir": "data/wind/SIM1",
            "tcl_procedures_dir": "tcl_procedures",
            "output_dir": output_dir,
            "save_prefix": "TEST",
        },
    }


def _fake_modal_out(output_dir: Path) -> None:
    """Write a minimal modal_simple.out so Rayleigh-damping reading doesn't fail."""
    output_dir.mkdir(parents=True, exist_ok=True)
    # columns: mode_id  frequency  MPM×6
    (output_dir / "modal_simple.out").write_text(
        "1.0 2.5 10.0 5.0 80.0 0.0 0.0 0.0\n"
        "2.0 5.0  5.0 10.0 15.0 0.0 0.0 0.0\n"
    )


@pytest.fixture
def writer_ctx(tmp_path):
    """Return (writer, geo_result, tmp_path) for a 3-node V-shape model."""
    out_dir = tmp_path / "output"
    _fake_modal_out(out_dir)
    cfg = _full_cfg(str(out_dir))
    geo = CableGeometry(cfg)
    geo_result = geo.generate()
    writer = TclWriter(cfg, geo_result)
    return writer, geo_result, tmp_path


# ─── modal TCL tests ──────────────────────────────────────────────────────

def test_node_count(writer_ctx):
    """Number of 'node ' commands must equal the number of nodes."""
    writer, geo, tmp = writer_ctx
    out = tmp / "Input.tcl"
    writer.write_modal(output_path=str(out))
    content = out.read_text()
    n_nodes = len(geo["x"])
    assert content.count("node ") == n_nodes


def test_element_count(writer_ctx):
    """Number of 'element ' commands (lowercase) must equal n_nodes - 1."""
    writer, geo, tmp = writer_ctx
    out = tmp / "Input.tcl"
    writer.write_modal(output_path=str(out))
    content = out.read_text()
    n_elements = len(geo["x"]) - 1
    # 'recorder Element' uses capital E → not counted by 'element '
    assert content.count("element ") == n_elements


def test_boundary_fix(writer_ctx):
    """Exactly 2 'fix ' lines for the two pinned end nodes."""
    writer, _, tmp = writer_ctx
    out = tmp / "Input.tcl"
    writer.write_modal(output_path=str(out))
    fix_lines = [l for l in out.read_text().splitlines() if "fix " in l]
    assert len(fix_lines) == 2


def test_tension_only_truss_model_generation(tmp_path):
    out_dir = tmp_path / "output"
    _fake_modal_out(out_dir)
    cfg = _full_cfg(str(out_dir))
    cfg["analysis"]["fiber_section"] = 2
    cfg["analysis"]["pretension_load"] = 1000.0
    cfg["material"]["rated_strength_N"] = 131900.0
    geo = CableGeometry(cfg)
    geo_result = geo.generate()
    writer = TclWriter(cfg, geo_result)
    out = tmp_path / "Input_TensionOnly.tcl"
    writer.write_modal(output_path=str(out))
    content = out.read_text()
    assert "uniaxialMaterial ElasticPPGap" in content
    assert "uniaxialMaterial InitStrainMaterial 10 1" in content
    assert content.count("element corotTruss") == len(geo_result["x"]) - 1
    assert "forceBeamColumn" not in content
    fix_lines = [line for line in content.splitlines() if line.startswith("fix ")]
    assert len(fix_lines) == len(geo_result["x"])
    assert any(" 0 0 0 1 1 1;" in line for line in fix_lines)


# ─── time-history TCL tests ───────────────────────────────────────────────

def test_force_files_count(writer_ctx):
    """timeSeries Path count must equal 4 × n_nodes (H_drag/lift + V_drag/lift)."""
    writer, geo, tmp = writer_ctx
    out = tmp / "Input_TH.tcl"
    writer.write_time_history(
        th_path="data/forces/FORCE_3/Test1",
        output_path=str(out),
    )
    content = out.read_text()
    n_nodes = len(geo["x"])
    assert content.count("timeSeries Path") == 4 * n_nodes


def test_pattern_count(writer_ctx):
    """Lines starting with 'pattern Plain 1' must equal 4 × n_nodes.

    For n_nodes=3, aero pattern IDs are 101-112 — all begin with '1'.
    The gravity pattern (200000) is excluded by this prefix filter.
    """
    writer, geo, tmp = writer_ctx
    out = tmp / "Input_TH.tcl"
    writer.write_time_history(
        th_path="data/forces/FORCE_3/Test1",
        output_path=str(out),
    )
    n_nodes = len(geo["x"])
    matching = [
        l for l in out.read_text().splitlines()
        if l.startswith("pattern Plain 1")
    ]
    assert len(matching) == 4 * n_nodes


def test_quasi_steady_can_disable_precomputed_force_patterns(tmp_path):
    out_dir = tmp_path / "output"
    _fake_modal_out(out_dir)
    cfg = _full_cfg(str(out_dir))
    cfg["quasi_steady_aero_force"] = {
        "enabled": True,
        "scale": 1.0,
        "log_stride": 1,
        "use_precomputed_loads": False,
    }
    geo = CableGeometry(cfg)
    writer = TclWriter(cfg, geo.generate())
    out = tmp_path / "Input_TH_QS.tcl"
    writer.write_time_history(
        th_path="data/forces/FORCE_3/Test1",
        output_path=str(out),
    )
    content = out.read_text()
    assert "source tcl_procedures/Wind_velocity_reader.tcl" in content
    assert "timeSeries Path" not in content
    assert "NODE_1_H_drag.txt" not in content


# ─── aero damping parameter file test ────────────────────────────────────

def test_incremental_quasi_steady_keeps_precomputed_force_patterns(tmp_path):
    out_dir = tmp_path / "output"
    _fake_modal_out(out_dir)
    cfg = _full_cfg(str(out_dir))
    cfg["quasi_steady_aero_force"] = {
        "enabled": False,
        "scale": 1.0,
        "log_stride": 1,
        "use_precomputed_loads": False,
    }
    cfg["incremental_quasi_steady_aero_force"] = {
        "enabled": True,
        "scale": 1.0,
        "log_stride": 1,
        "keep_precomputed_loads": True,
    }
    geo = CableGeometry(cfg)
    geo_result = geo.generate()
    writer = TclWriter(cfg, geo_result)
    out = tmp_path / "Input_TH_IQS.tcl"
    writer.write_time_history(
        th_path="data/forces/FORCE_3/Test1",
        output_path=str(out),
    )
    content = out.read_text()
    assert "set force_data_dir \"data/forces/FORCE_3/Test1\"" in content
    assert content.count("timeSeries Path") == 4 * len(geo_result["x"])
    assert "NODE_1_H_drag.txt" in content


def test_aero_damp_file(writer_ctx):
    """inputs_aerodynamic_damping.tcl must define all 5 required variables."""
    writer, _, tmp = writer_ctx
    out = tmp / "inputs_aerodynamic_damping.tcl"
    writer.write_aero_damping_params(output_path=str(out))
    content = out.read_text()
    for var in (
        "MassM",
        "B",
        "L",
        "ro_air",
        "node_tributary_lengths",
        "incremental_qs_ro_air_density",
        "element_tension_only",
        "xi_structural",
        "omegaN",
        "damping_writeback_mode",
        "use_deformed_element_direction",
        "enable_explicit_aero_damping_force",
        "explicit_aero_damping_force_scale",
        "enable_quasi_steady_aero_force",
        "quasi_steady_aero_force_scale",
        "quasi_steady_aero_force_log_stride",
        "enable_incremental_quasi_steady_aero_force",
        "incremental_quasi_steady_aero_force_scale",
        "incremental_quasi_steady_aero_force_log_stride",
        "event_stop_max_alpha_deg",
        "event_stop_max_clipped_fraction",
    ):
        assert var in content, f"Variable '{var}' missing from aero damping file"
    assert 'set damping_writeback_mode "record_only"' in content
    assert "set use_deformed_element_direction 1" in content
    assert "set enable_explicit_aero_damping_force 0" in content
    assert "set enable_quasi_steady_aero_force 0" in content
    assert "set enable_incremental_quasi_steady_aero_force 0" in content


def test_tension_only_flag_written_to_aero_params(tmp_path):
    out_dir = tmp_path / "output"
    _fake_modal_out(out_dir)
    cfg = _full_cfg(str(out_dir))
    cfg["analysis"]["fiber_section"] = 2
    geo = CableGeometry(cfg)
    writer = TclWriter(cfg, geo.generate())
    out = tmp_path / "inputs_aerodynamic_damping.tcl"
    writer.write_aero_damping_params(output_path=str(out))
    content = out.read_text()
    assert "set element_tension_only 1" in content


def test_quasi_steady_aero_params_are_written(tmp_path):
    out_dir = tmp_path / "output"
    _fake_modal_out(out_dir)
    cfg = _full_cfg(str(out_dir))
    cfg["quasi_steady_aero_force"] = {
        "enabled": True,
        "scale": 0.25,
        "log_stride": 3,
        "use_precomputed_loads": False,
    }
    geo = CableGeometry(cfg)
    writer = TclWriter(cfg, geo.generate())
    out = tmp_path / "inputs_aerodynamic_damping.tcl"
    writer.write_aero_damping_params(output_path=str(out))
    content = out.read_text()
    assert "set enable_quasi_steady_aero_force 1" in content
    assert "set quasi_steady_aero_force_scale 0.25" in content
    assert "set quasi_steady_aero_force_log_stride 3" in content


def test_incremental_quasi_steady_aero_params_are_written(tmp_path):
    out_dir = tmp_path / "output"
    _fake_modal_out(out_dir)
    cfg = _full_cfg(str(out_dir))
    cfg["incremental_quasi_steady_aero_force"] = {
        "enabled": True,
        "scale": 0.5,
        "log_stride": 2,
        "keep_precomputed_loads": True,
    }
    geo = CableGeometry(cfg)
    writer = TclWriter(cfg, geo.generate())
    out = tmp_path / "inputs_aerodynamic_damping.tcl"
    writer.write_aero_damping_params(output_path=str(out))
    content = out.read_text()
    assert "set enable_incremental_quasi_steady_aero_force 1" in content
    assert "set incremental_quasi_steady_aero_force_scale 0.5" in content
    assert "set incremental_quasi_steady_aero_force_log_stride 2" in content
