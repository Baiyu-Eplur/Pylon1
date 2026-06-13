# tcl_writer.py — generate Input.tcl and inputs_aerodynamic_damping.tcl for OpenSees
from __future__ import annotations
import math
from pathlib import Path
from typing import IO

import numpy as np


class TclWriter:
    """Write OpenSees Tcl input files from a config dict and geometry result.

    Parameters
    ----------
    config     : full config dict (loaded from default_config.yaml)
    geo_result : dict returned by CableGeometry.generate()
    """

    G_ACCEL = 9.80665  # m/s²

    def __init__(self, config: dict, geo_result: dict) -> None:
        self.cfg = config
        self.geo = geo_result
        self.tcl_dir: str = str(config["paths"]["tcl_procedures_dir"]).replace("\\", "/")
        self.output_dir: str = str(config["paths"].get("output_dir", "Output")).replace("\\", "/")

    def _out(self, filename: str) -> str:
        return f"{self.output_dir}/{filename}"

    # ═══════════════════════════════════════════════════════════════════
    # Internal line-writer helper
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def _w(fid: IO[str], line: str) -> None:
        fid.write(line + "\n")

    # ═══════════════════════════════════════════════════════════════════
    # Private building-block methods
    # ═══════════════════════════════════════════════════════════════════

    def _write_header(self, fid: IO[str], timeseries_tag: int) -> None:
        """wipe / getPID / model basic / timeSeries Linear"""
        w = self._w
        w(fid, "wipe; ")
        w(fid, "set process_id [getPID]; ")
        w(fid, "set is_parallel 0; ")
        w(fid, "model basic -ndm 3 -ndf 6; ")
        w(fid, f"timeSeries Linear {timeseries_tag}; ")

    def _write_nodes_and_masses(self, fid: IO[str]) -> None:
        """node and mass commands for every node."""
        x, y, z = self.geo["x"], self.geo["y"], self.geo["z"]
        MN, MNT = self.geo["MN"], self.geo["MNT"]
        tension_only = self._uses_tension_only_truss()
        for i in range(len(x)):
            self._w(fid,
                f"node {i+1} {x[i]:.6f} {y[i]:.6f} {z[i]:.6f}; ")
            if tension_only:
                self._w(fid, f"mass {i+1} {MN[i]:.6f} {MN[i]:.6f} {MN[i]:.6f} 0 0 0; ")
            else:
                self._w(fid,
                    f"mass {i+1} {MN[i]:.6f} {MN[i]:.6f} {MN[i]:.6f} "
                    f"{MNT[i]:.6f} 0 0; ")

    def _write_section_and_elements(self, fid: IO[str]) -> None:
        """Material, fiber section (if enabled), geomTransf, and elements."""
        ana = self.cfg["analysis"]
        mat = self.cfg["material"]
        geo = self.geo

        fiber = int(ana["fiber_section"])
        E = float(mat["E"])
        G = float(mat["G"])
        Dia = float(mat["Dia"])
        Area = geo["Area"]
        In = geo["In"]
        Io = geo["Io"]
        pretension = float(ana["pretension_load"])
        angles = geo["angles"]
        x = geo["x"]

        if fiber == 1:
            self._w(fid, f"uniaxialMaterial Elastic 1 {E:.6f};")
            eps0 = pretension / Area / E
            self._w(fid, f"uniaxialMaterial InitStrainMaterial 10 1 {eps0:.6e};")
            self._w(fid, f"section Fiber 100 -GJ {G * Io:.6f} {{ ")
            self._w(fid, f"patch circ 10 12 6 0 0 0 {Dia / 2:.6f} 0 360; ")
            self._w(fid, "}; ")
        elif fiber == 2:
            rated_strength = float(mat.get("rated_strength_N", 1.0e12))
            fy = rated_strength / Area
            if self._uses_shape_based_initial_tension():
                for i, initial_tension in enumerate(self._element_initial_tensions(), start=1):
                    eps0 = initial_tension / Area / E
                    base_tag = 10000 + i
                    init_tag = 20000 + i
                    self._w(fid, f"uniaxialMaterial ElasticPPGap {base_tag} {E:.6f} {fy:.6f} 0.0;")
                    self._w(fid, f"uniaxialMaterial InitStrainMaterial {init_tag} {base_tag} {eps0:.6e};")
            else:
                eps0 = pretension / Area / E
                self._w(fid, f"uniaxialMaterial ElasticPPGap 1 {E:.6f} {fy:.6f} 0.0;")
                self._w(fid, f"uniaxialMaterial InitStrainMaterial 10 1 {eps0:.6e};")

        for i in range(len(x) - 1):
            sin_a = -math.sin(angles[i])
            cos_a = math.cos(angles[i])
            if fiber == 0:
                self._w(fid,
                    f"geomTransf Corotational {i+1} {sin_a:.6f} 0 {cos_a:.6f}; ")
                self._w(fid,
                    f"element elasticBeamColumn {i+1} {i+1} {i+2} "
                    f"{Area:.6f} {E:.6f} {G:.6f} "
                    f"{Io:.6e} {In:.6e} {In:.6e} {i+1}; ")
            elif fiber == 1:
                self._w(fid,
                    f"geomTransf Corotational {i+1} {sin_a:.6f} 0 {cos_a:.6f}; ")
                self._w(fid,
                    f"element forceBeamColumn {i+1} {i+1} {i+2} 10 100 {i+1}; ")
            elif fiber == 2:
                material_tag = 20000 + i + 1 if self._uses_shape_based_initial_tension() else 10
                self._w(fid, f"element corotTruss {i+1} {i+1} {i+2} {Area:.12g} {material_tag}; ")
            else:
                raise ValueError(f"Unsupported analysis.fiber_section={fiber!r}")

    def _write_custom_function_caller(self, fid: IO[str]) -> None:
        """CustomFunctionCaller proc definition — fixed content, copied from MATLAB."""
        w = self._w
        w(fid, "# a list of all monitor and custom function actors to be called by the MonitorFunction; ")
        w(fid, "set all_custom_functions {}; ")
        w(fid, "set all_monitor_actors {}; ")
        w(fid, "# the main custom function caller that will call all actors in $all_monitor_actors and in $all_custom_functions list; ")
        w(fid, "proc CustomFunctionCaller {step_id dt T n_iter norm perc process_id is_parallel} {; ")
        w(fid, "\tglobal all_monitor_actors; ")
        w(fid, "\tglobal all_custom_functions; ")
        w(fid, "\t# Call monitors: we pass the parameters needed; ")
        w(fid, "\tforeach p $all_monitor_actors {; ")
        w(fid, "\t\t$p $step_id $dt $T $n_iter $norm $perc $process_id $is_parallel; ")
        w(fid, "\t}; ")
        w(fid, "\t# Call all other custom functions; ")
        w(fid, "\tforeach p $all_custom_functions {; ")
        w(fid, "\t\t$p; ")
        w(fid, "\t}; ")
        w(fid, "}; ")

    def _write_boundary_conditions(self, fid: IO[str]) -> None:
        """fix commands for the two pin-supported end nodes."""
        x, z = self.geo["x"], self.geo["z"]
        # exact comparison is safe: arange + V/parabolic/catenary all produce z==0 at endpoints
        idx0 = int(np.where((x == 0.0) & (z == 0.0))[0][0])
        idxL = int(np.where((x == x.max()) & (z == 0.0))[0][0])
        if self._uses_tension_only_truss():
            for i in range(len(x)):
                if i in (idx0, idxL):
                    self._w(fid, f"fix {i + 1} 1 1 1 1 1 1; ")
                else:
                    self._w(fid, f"fix {i + 1} 0 0 0 1 1 1; ")
        else:
            self._w(fid, f"fix {idx0 + 1} 1 1 1 1 0 0; ")
            self._w(fid, f"fix {idxL + 1} 1 1 1 1 0 0; ")

    def _write_gravity_load(
        self, fid: IO[str], pattern_tag: int, series_tag: int
    ) -> None:
        """Self-weight pattern (Plain load, negative Z)."""
        MN = self.geo["MN"]
        g = self.G_ACCEL
        mult = float(self.cfg["analysis"]["multiplier_vertical_load"])
        self._w(fid, f"pattern Plain {pattern_tag} {series_tag} {{ ")
        for i in range(len(MN)):
            self._w(fid, f"load {i+1} 0 0 {-MN[i] * g * mult:.6f} 0 0 0; ")
        self._w(fid, "}; ")

    def _write_static_solver(
        self, fid: IO[str], test_iterations: int = 100
    ) -> None:
        """Static solver settings + recorders + incremental load loop.

        Parameters
        ----------
        test_iterations : 100 for MODAL run, 200 for TH run (MATLAB convention)
        """
        ana = self.cfg["analysis"]
        tol = float(ana["tolerance"])
        n_steps = int(ana["numbers_of_step_gravity"])
        N = len(self.geo["x"])
        w = self._w

        w(fid, "constraints Transformation")
        w(fid, "numberer Plain")
        w(fid, "system FullGeneral")
        w(fid, f"test NormDispIncr {tol:.2e} {test_iterations}")
        w(fid, "algorithm KrylovNewton")
        w(fid, "integrator LoadControl 0.0")
        w(fid, "analysis Static")
        w(fid, f"recorder Element -file {self._out('Element1.out')} -time -ele 1 force; ")
        w(fid, f"recorder Node -file {self._out('Static.out')} -nodeRange 1 {N} -dof 3 disp; ")

        # incremental load loop — do not modify; matches MATLAB exactly
        w(fid, "set total_time 1.0")
        w(fid, f"set initial_num_incr {n_steps}")
        w(fid, "set time 0.0")
        w(fid, "set time_increment [expr $total_time / $initial_num_incr]")
        w(fid, "integrator LoadControl $time_increment ")
        w(fid, "for {set increment_counter 1} {$increment_counter <= $initial_num_incr} {incr increment_counter} { ")
        w(fid, "\tif {$process_id == 0} { ")
        w(fid, '\t\tputs "Increment: $increment_counter. time_increment = $time_increment. Current time = $time" ')
        w(fid, "\t} ")
        w(fid, "\tset ok [analyze 1 ] ")
        w(fid, "\t#barrier ")
        w(fid, "\tif {$ok == 0} { ")
        w(fid, "\t\tset num_iter [testIter] ")
        w(fid, "\t\tset time [expr $time + $time_increment] ")
        w(fid, "\t\t# print statistics ")
        w(fid, "\t\tset norms [testNorms] ")
        w(fid, "\t\tif {$num_iter > 0} {set last_norm [lindex $norms [expr $num_iter-1]]} else {set last_norm 0.0} ")
        w(fid, "\t\tif {$process_id == 0} { ")
        w(fid, "\t\t} ")
        w(fid, "\t\t# Call Custom Functions ")
        w(fid, "\t\tset perc [expr $time/$total_time] ")
        w(fid, "\t\tCustomFunctionCaller $increment_counter $time_increment $time $num_iter $last_norm $perc $process_id $is_parallel ")
        w(fid, "\t} else { ")
        w(fid, '\t\terror "ERROR: the analysis did not converge" ')
        w(fid, "\t} ")
        w(fid, "} ")
        w(fid, "if {$process_id == 0} { ")
        w(fid, '\tputs "Target time has been reached. Current time = $time" ')
        w(fid, '\tputs "SUCCESS." ')
        w(fid, "} ")

    def _write_aerodynamic_loads(self, fid: IO[str], th_path: str) -> None:
        """Write 4×N aerodynamic time-history load patterns.

        Tag scheme (in = 1-based node index, N = total nodes):
          H_drag : ts={in},     pat={100+in}
          H_lift : ts={in+N},   pat={100+in+N}
          V_drag : ts={in+2N},  pat={100+in+2N}
          V_lift : ts={in+3N},  pat={100+in+3N}
        """
        N = len(self.geo["x"])
        dt = float(self.cfg["time_history"]["dt"])

        components = [
            ("H_drag", 0,       "0 1000 0 0 0 0"),
            ("H_lift", N,       "0 0 1000 0 0 0"),
            ("V_drag", 2 * N,   "0 0 1000 0 0 0"),
            ("V_lift", 3 * N,   "0 1000 0 0 0 0"),
        ]

        th_path_tcl = str(th_path).replace("\\", "/")

        for comp_name, offset, load_dof in components:
            for in_ in range(1, N + 1):
                ts_id = in_ + offset
                pat_id = 100 + ts_id
                fpath = f"{th_path_tcl}/NODE_{in_}_{comp_name}.txt"
                self._w(fid, f"timeSeries Path {ts_id} -dt {dt} -filePath {fpath} -factor 1")
                self._w(fid, f"pattern Plain {pat_id} {ts_id} {{")
                self._w(fid, f"load {in_} {load_dof}")
                self._w(fid, "} ")

    def _write_rayleigh_damping(self, fid: IO[str]) -> None:
        """Read f1 from modal_simple.out and write mass-proportional Rayleigh term.

        alpha = 2 * xi * 2*pi * f1   (beta term omitted, consistent with MATLAB)
        """
        f1 = self._read_first_frequency()
        xi = float(self.cfg["damping"]["xi"])
        scale = float(self.cfg["damping"].get("global_rayleigh_scale", 1.0))
        alpha = scale * 2.0 * xi * 2.0 * math.pi * f1
        self._w(fid, f"rayleigh {alpha:.6f} 0 0 0")

    def _write_modal_damping(self, fid: IO[str]) -> None:
        """modalDamping command for all requested modes."""
        xi = float(self.cfg["damping"]["xi"])
        n = int(self.cfg["damping"]["modes_for_damping"])
        self._w(fid, f"eigen {n};")
        damps = " ".join([f"{xi:.4f}"] * n)
        self._w(fid, f"modalDamping {damps}")

    # ═══════════════════════════════════════════════════════════════════
    # Public main methods
    # ═══════════════════════════════════════════════════════════════════

    def write_modal(self, output_path: str = "Input.tcl") -> None:
        """Generate Input.tcl for static + modal analysis (mirrors MODAL.m)."""
        ana = self.cfg["analysis"]
        N = len(self.geo["x"])
        n_modes = int(ana["number_of_modes"])
        td = self.tcl_dir
        w = self._w

        with open(output_path, "w", encoding="utf-8") as fid:
            self._write_header(fid, timeseries_tag=1)
            w(fid, f'set opensees_output_dir "{self.output_dir}"')
            self._write_nodes_and_masses(fid)
            self._write_section_and_elements(fid)
            self._write_custom_function_caller(fid)
            self._write_boundary_conditions(fid)
            gravity_series_tag = 10001 if self._assumes_initial_equilibrium() else 1
            if self._assumes_initial_equilibrium():
                w(fid, f"timeSeries Constant {gravity_series_tag}; ")
            self._write_gravity_load(fid, pattern_tag=20, series_tag=gravity_series_tag)
            if self._assumes_initial_equilibrium():
                if self._uses_load_const_after_assumed_equilibrium():
                    w(fid, "loadConst -time 0.0")
            else:
                self._write_static_solver(fid, test_iterations=100)

            # modal procedure sources
            w(fid, f"source {td}/PROCEDURE_OLD.tcl; ")
            w(fid, f'modal1 {n_modes} "{self._out("modal_old.out")}"')
            w(fid, f"source {td}/PROCEDURE_Raf_6dof.tcl; ")
            w(fid, f'modal {n_modes} "{self._out("modal_simple.out")}"')

            # eigenvector recorders
            for i in range(1, n_modes + 1):
                w(fid,
                  f'recorder Node -file {self._out(f"Eigen{i}.out")} '
                  f'-nodeRange 1 {N} -dof 1 2 3 "eigen {i}"; ')

            w(fid, "record ")
            w(fid, "exit; ")

    def write_time_history(
        self, th_path: str, output_path: str = "Input.tcl"
    ) -> None:
        """Generate Input.tcl for static + time-history analysis (mirrors TH_Constant.m).

        Parameters
        ----------
        th_path : path to force time-history folder, e.g. "data/forces/FORCE_3/Test1"
        """
        ana = self.cfg["analysis"]
        th = self.cfg["time_history"]
        damp = self.cfg["damping"]
        N = len(self.geo["x"])
        dt = float(th["dt"])
        npt = int(th["npt"])
        duration = npt * dt
        tol = float(ana["tolerance"])
        td = self.tcl_dir
        w = self._w

        with open(output_path, "w", encoding="utf-8") as fid:
            self._write_header(fid, timeseries_tag=10000)
            w(fid, f'set opensees_output_dir "{self.output_dir}"')
            self._write_nodes_and_masses(fid)
            self._write_section_and_elements(fid)
            self._write_custom_function_caller(fid)
            self._write_boundary_conditions(fid)
            gravity_series_tag = 10001 if self._assumes_initial_equilibrium() else 10000
            if self._assumes_initial_equilibrium():
                w(fid, f"timeSeries Constant {gravity_series_tag}; ")
            self._write_gravity_load(fid, pattern_tag=200000, series_tag=gravity_series_tag)

            # wind velocity reader (must precede static loop so variables exist)
            wind_dir = str(self.cfg["paths"].get("wind_dir", "data/wind/SIM1")).replace("\\", "/")
            wind_time_file = str(
                self.cfg["paths"].get("time_file", "data/aero_coeffs/time.txt")
            ).replace("\\", "/")
            w(fid, f'set wind_data_dir "{wind_dir}"')
            w(fid, f'set wind_time_file "{wind_time_file}"')
            w(fid, f"source {td}/Wind_velocity_reader.tcl")

            if self._assumes_initial_equilibrium():
                pass
            else:
                self._write_static_solver(fid, test_iterations=200)
            if (not self._assumes_initial_equilibrium()) or self._uses_load_const_after_assumed_equilibrium():
                w(fid, "loadConst -time 0.0")

            quasi_steady = self.cfg.get("quasi_steady_aero_force", {})
            incremental_qs = self.cfg.get("incremental_quasi_steady_aero_force", {})
            use_precomputed_loads = bool(
                quasi_steady.get("use_precomputed_loads", not bool(quasi_steady.get("enabled", False)))
            )
            if bool(incremental_qs.get("enabled", False)):
                use_precomputed_loads = bool(incremental_qs.get("keep_precomputed_loads", True))
            th_path_tcl = str(th_path).replace("\\", "/")
            w(fid, f'set force_data_dir "{th_path_tcl}"')
            if use_precomputed_loads:
                self._write_aerodynamic_loads(fid, th_path)

            # dynamic recorders
            w(fid, f"recorder Node -file {self._out('Dynamic.out')} -time -nodeRange 1 {N} -dof 1 2 3 disp; ")
            w(fid, f"recorder Node -file {self._out('Reaction.out')} -time -node 1 -dof 1 2 3 reaction; ")
            w(fid, f"recorder Node -file {self._out('SupportReactions.out')} -time -node 1 {N} -dof 1 2 3 reaction; ")
            w(fid, f"recorder Node -file {self._out('Velocity.out')} -time -nodeRange 1 {N} -dof 1 2 3 vel; ")
            w(fid, f"recorder Node -file {self._out('Accel.out')}    -time -nodeRange 1 {N} -dof 1 2 3 accel; ")
            w(fid, "wipeAnalysis")

            # damping
            if str(damp["model"]) == "Rayleigh":
                self._write_rayleigh_damping(fid)
            else:
                self._write_modal_damping(fid)

            # transient solver settings
            w(fid, "constraints Transformation")
            w(fid, "numberer Plain")
            w(fid, "system FullGeneral")
            # MATLAB uses Tollerance/1000 for transient convergence test
            w(fid, f"test NormDispIncr {tol / 1000:.2e} 100")
            w(fid, "algorithm KrylovNewton;")
            w(fid, "integrator Newmark 0.5 0.25")
            w(fid, "analysis Transient")
            w(fid, f"set total_duration {duration:.4f}")
            w(fid, f"set initial_num_incr {npt}")
            w(fid, f"set STKO_VAR_time_increment {dt:.6f}")

            # adaptive loop and aerodynamic damping
            w(fid, f"source {td}/Damping_shifter.tcl")
            w(fid, f"source {td}/dynamic2.tcl")
            w(fid, "# Done! ")
            w(fid, 'puts "ANALYSIS SUCCESSFULLY FINISHED" ')
            w(fid, "exit; ")

    def write_aero_damping_params(
        self, output_path: str = "inputs_aerodynamic_damping.tcl"
    ) -> None:
        """Write inputs_aerodynamic_damping.tcl (separate file, not part of Input.tcl).

        Reads f1 from output/modal_simple.out — must be called after write_modal() has run.
        Uses node index 1 (second node, 0-indexed) for MassM and L, matching MATLAB MN(2)/DX(2).
        """
        f1 = self._read_first_frequency()
        MN = self.geo["MN"]
        DX = self.geo["DX"]
        Dia = float(self.cfg["material"]["Dia"])
        E = float(self.cfg["material"]["E"])
        Area = float(self.geo["Area"])
        pretension = float(self.cfg["analysis"]["pretension_load"])
        ro_air = float(self.cfg["time_history"]["ro_air"])
        wind_generation = self.cfg.get("wind_generation", {})
        incremental_qs_ro_air_density = float(wind_generation.get("ro_air_force", ro_air / 1000.0)) * 1000.0
        xi_structural = float(self.cfg["damping"]["xi"])
        omega_n = 2.0 * math.pi * f1
        aero_damp = self.cfg.get("aerodynamic_damping", {})
        enabled = 1 if bool(aero_damp.get("enabled", True)) else 0
        dcl_scale = float(aero_damp.get("dcl_derivative_scale", 180.0 / math.pi))
        delta_min = float(aero_damp.get("delta_D_min", -1.0e30))
        delta_max = float(aero_damp.get("delta_D_max", 1.0e30))
        use_direction = 1 if bool(aero_damp.get("use_deformed_element_direction", True)) else 0
        writeback_mode = str(aero_damp.get("writeback_mode", "record_only"))
        aero_force = self.cfg.get("aerodynamic_force", {})
        force_enabled = 1 if bool(aero_force.get("enabled", False)) else 0
        force_scale = float(aero_force.get("scale", 1.0))
        force_log_stride = int(aero_force.get("log_stride", 20))
        quasi_steady = self.cfg.get("quasi_steady_aero_force", {})
        qs_enabled = 1 if bool(quasi_steady.get("enabled", False)) else 0
        qs_scale = float(quasi_steady.get("scale", 1.0))
        qs_log_stride = int(quasi_steady.get("log_stride", 20))
        incremental_qs = self.cfg.get("incremental_quasi_steady_aero_force", {})
        incremental_qs_enabled = 1 if bool(incremental_qs.get("enabled", False)) else 0
        incremental_qs_scale = float(incremental_qs.get("scale", 1.0))
        incremental_qs_log_stride = int(incremental_qs.get("log_stride", 20))
        event_stop = self.cfg.get("event_stop", {})
        event_stop_enabled = 1 if bool(event_stop.get("enabled", False)) else 0
        event_disp = float(event_stop.get("max_displacement_m", 1.0e30))
        event_vel = float(event_stop.get("max_velocity_mps", 1.0e30))
        event_acc = float(event_stop.get("max_acceleration_mps2", 1.0e30))
        event_min_xi = float(event_stop.get("min_effective_damping", -1.0e30))
        event_max_alpha = float(event_stop.get("max_alpha_deg", 1.0e30))
        event_max_clipped_fraction = float(event_stop.get("max_clipped_fraction", 1.0e30))
        diagnostics = self.cfg.get("diagnostics", {})
        element_strain_log_stride = int(diagnostics.get("element_strain_log_stride", 1))

        with open(output_path, "w", encoding="utf-8") as fid:
            self._w(fid, f"set MassM {MN[1]:.6f}")
            self._w(fid, f"set B {Dia:.6f}")
            self._w(fid, f"set L {DX[1]:.6f}")
            self._w(fid, f"set ro_air {ro_air:.4f}")
            dx_values = " ".join(f"{float(value):.12g}" for value in DX)
            self._w(fid, f"set node_tributary_lengths {{{dx_values}}}")
            self._w(fid, f"set incremental_qs_ro_air_density {incremental_qs_ro_air_density:.12g}")
            self._w(fid, f"set element_axial_EA {E * Area:.12g}")
            self._w(fid, f"set element_pretension_load {pretension:.12g}")
            pretension_values = " ".join(
                f"{value:.12g}" for value in self._element_initial_tensions()
            )
            self._w(fid, f"set element_pretension_loads {{{pretension_values}}}")
            self._w(fid, f"set element_tension_only {1 if self._uses_tension_only_truss() else 0}")
            self._w(fid, f"set element_strain_log_stride {element_strain_log_stride}")
            self._w(fid, f"set xi_structural {xi_structural:.6f}")
            self._w(fid, f"set omegaN {omega_n:.6f}")
            self._w(fid, f"set enable_aero_damping_update {enabled}")
            self._w(fid, f"set dcl_derivative_scale {dcl_scale:.12g}")
            self._w(fid, f"set delta_D_min {delta_min:.12g}")
            self._w(fid, f"set delta_D_max {delta_max:.12g}")
            self._w(fid, f"set use_deformed_element_direction {use_direction}")
            self._w(fid, f'set damping_writeback_mode "{writeback_mode}"')
            self._w(fid, f"set enable_explicit_aero_damping_force {force_enabled}")
            self._w(fid, f"set explicit_aero_damping_force_scale {force_scale:.12g}")
            self._w(fid, f"set explicit_aero_damping_force_log_stride {force_log_stride}")
            self._w(fid, f"set enable_quasi_steady_aero_force {qs_enabled}")
            self._w(fid, f"set quasi_steady_aero_force_scale {qs_scale:.12g}")
            self._w(fid, f"set quasi_steady_aero_force_log_stride {qs_log_stride}")
            self._w(fid, f"set enable_incremental_quasi_steady_aero_force {incremental_qs_enabled}")
            self._w(fid, f"set incremental_quasi_steady_aero_force_scale {incremental_qs_scale:.12g}")
            self._w(fid, f"set incremental_quasi_steady_aero_force_log_stride {incremental_qs_log_stride}")
            self._w(fid, f"set event_stop_enabled {event_stop_enabled}")
            self._w(fid, f"set event_stop_max_displacement_m {event_disp:.12g}")
            self._w(fid, f"set event_stop_max_velocity_mps {event_vel:.12g}")
            self._w(fid, f"set event_stop_max_acceleration_mps2 {event_acc:.12g}")
            self._w(fid, f"set event_stop_min_effective_damping {event_min_xi:.12g}")
            self._w(fid, f"set event_stop_max_alpha_deg {event_max_alpha:.12g}")
            self._w(fid, f"set event_stop_max_clipped_fraction {event_max_clipped_fraction:.12g}")

    # ═══════════════════════════════════════════════════════════════════
    # Internal utility
    # ═══════════════════════════════════════════════════════════════════

    def _read_first_frequency(self) -> float:
        """Load modal_simple.out and return the first modal frequency (Hz).

        modal_simple.out column layout (from PROCEDURE_Raf_6dof.tcl):
          col 0 : mode index (1-based float)
          col 1 : frequency (Hz)
          col 2+ : modal participation mass ratios per DOF
        """
        output_dir = self.cfg["paths"]["output_dir"]
        modal_path = Path(output_dir) / "modal_simple.out"
        if not modal_path.exists():
            raise FileNotFoundError(
                f"modal_simple.out not found at {modal_path}. "
                "Run write_modal() and execute OpenSees before calling this method."
            )
        data = np.loadtxt(modal_path)
        if data.ndim == 1:          # single mode → make 2-D
            data = data[np.newaxis, :]
        return float(data[0, 1])    # first mode, frequency column

    def _uses_tension_only_truss(self) -> bool:
        return int(self.cfg["analysis"].get("fiber_section", 1)) == 2

    def _assumes_initial_equilibrium(self) -> bool:
        return bool(self.cfg["analysis"].get("assume_initial_equilibrium", False))

    def _uses_load_const_after_assumed_equilibrium(self) -> bool:
        return bool(self.cfg["analysis"].get("load_const_after_assumed_equilibrium", True))

    def _uses_shape_based_initial_tension(self) -> bool:
        mode = str(self.cfg["analysis"].get("initial_tension_mode", "uniform_axial"))
        return mode == "catenary_horizontal_component"

    def _element_initial_tensions(self) -> list[float]:
        pretension = float(self.cfg["analysis"]["pretension_load"])
        if not self._uses_shape_based_initial_tension():
            return [pretension for _ in self.geo["angles"]]
        tensions: list[float] = []
        for angle in self.geo["angles"]:
            cos_a = max(abs(math.cos(float(angle))), 1.0e-9)
            tensions.append(pretension / cos_a)
        return tensions
