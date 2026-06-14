# analysis.py — top-level orchestrator: config → geometry → tcl → OpenSees → results
from __future__ import annotations

import numpy as np
import shutil
from pathlib import Path

from .config_loader import load_config
from .geometry import CableGeometry
from .tcl_writer import TclWriter
from .solver import OpenSeesSolver
from .postprocess import (
    load_reaction,
    load_displacement,
    compute_max_reaction,
    compute_max_displacement,
    compute_clearance,
    save_results,
)
from .wind_forces import generate_wind_force_case


class CableAnalysis:
    """Orchestrate geometry → Tcl generation → OpenSees → post-processing.

    Parameters
    ----------
    config_path : path to a YAML config file (e.g. config/default_config.yaml)
    """

    def __init__(self, config_path: str) -> None:
        self.cfg = load_config(config_path)

        self.geo = CableGeometry(self.cfg)
        self.geo_result = self.geo.generate()

        self.solver = OpenSeesSolver(
            opensees_path=self.cfg["solver"]["opensees_path"],
            work_dir=self.cfg["solver"].get("work_dir", "."),
        )

    # ═══════════════════════════════════════════════════════════════════
    # Public entry point
    # ═══════════════════════════════════════════════════════════════════

    def run(self) -> None:
        """Dispatch to the appropriate analysis method based on config."""
        analysis_type = self.cfg["analysis"]["type"]

        if analysis_type == "STATIC":
            self._run_static()
        elif analysis_type == "MODAL":
            self._run_modal()
        elif analysis_type == "TH":
            self._run_time_history()
        else:
            raise ValueError(
                f"未知分析类型: {analysis_type!r}。"
                "有效值为 'STATIC' | 'MODAL' | 'TH'"
            )

    # ═══════════════════════════════════════════════════════════════════
    # Analysis runners
    # ═══════════════════════════════════════════════════════════════════

    def _run_static(self) -> None:
        """Static + modal analysis (STATIC is a subset of MODAL in our pipeline)."""
        # MODAL.m already contains the static phase; reuse it.
        self._run_modal()

    def _run_modal(self) -> None:
        """Write Input.tcl for static + modal analysis and run OpenSees."""
        Path(self.cfg["paths"]["output_dir"]).mkdir(parents=True, exist_ok=True)
        input_tcl = self.cfg["solver"]["input_tcl"]
        writer = TclWriter(self.cfg, self.geo_result)
        writer.write_modal(output_path=input_tcl)
        self._archive_generated_tcl(
            input_tcl, Path(self.cfg["paths"]["output_dir"]) / "Input_modal.tcl"
        )
        self.solver.run(
            input_tcl,
            log_dir=Path(self.cfg["paths"]["output_dir"]) / "solver_logs",
            run_label="modal",
        )

    def _run_time_history(self) -> None:
        """Double loop over folder_1 × folder_2, mirroring the MATLAB for iu/ju loops.

        For each (FORCE_x, SIMx) pair:
          1. MODAL run  — static equilibrium + extract modal frequencies for damping
          2. TH run     — aerodynamic loading time-history
          3. Post-process and accumulate MAX_DISP / MAX_REAC / MAX_CLEARANCE
        Results are saved to CSV via save_results().
        """
        wind_generation_cfg = self.cfg.get("wind_generation", {})
        if wind_generation_cfg.get("enabled", False):
            meta = generate_wind_force_case(
                self.cfg,
                self.geo_result,
                root=Path(self.cfg["solver"].get("work_dir", ".")),
            )
            print(
                "Generated wind/force case: "
                f"{meta['force_name']} / {meta['sim_name']} "
                f"(u_star={meta['wind']['u_star_mps']} m/s)"
            )

        folder_1_list: list[str] = self.cfg["time_history"]["folder_1"]
        folder_2_list: list[str] = self.cfg["time_history"]["folder_2"]
        forces_dir = Path(self.cfg["paths"]["forces_dir"])
        output_dir = self.cfg["paths"]["output_dir"]
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        input_tcl = self.cfg["solver"]["input_tcl"]
        n_nodes = len(self.geo_result["x"])

        n1, n2 = len(folder_1_list), len(folder_2_list)
        MAX_DISP = np.zeros((n1, n2))
        MAX_REAC = np.zeros((n1, n2))
        MAX_CLEARANCE = np.zeros((n1, n2))

        for iu, f1 in enumerate(folder_1_list):
            for ju, f2 in enumerate(folder_2_list):
                th_path = forces_dir / f1 / f2
                print(f"\n>>> [{iu+1}/{n1}, {ju+1}/{n2}] Running: {f1} / {f2}")

                writer = TclWriter(self.cfg, self.geo_result)

                # ── Step 1: Modal (static equilibrium + frequencies) ──────
                writer.write_modal(output_path=input_tcl)
                self._archive_generated_tcl(input_tcl, Path(output_dir) / "Input_modal.tcl")
                self.solver.run(
                    input_tcl,
                    log_dir=Path(output_dir) / "solver_logs",
                    run_label=f"{f1}_{f2}_modal",
                )

                # ── Step 2: Time-history ───────────────────────────────────
                writer.write_time_history(
                    th_path=str(th_path),
                    output_path=input_tcl,
                )
                self._archive_generated_tcl(input_tcl, Path(output_dir) / "Input_time_history.tcl")
                # inputs_aerodynamic_damping.tcl must live next to Input.tcl
                aero_tcl = str(
                    Path(self.cfg["solver"].get("work_dir", "."))
                    / "inputs_aerodynamic_damping.tcl"
                )
                writer.write_aero_damping_params(output_path=aero_tcl)
                aero_tcl_path = Path(aero_tcl)
                aero_tcl_archive = Path(output_dir) / "inputs_aerodynamic_damping.tcl"
                aero_tcl_archive.write_text(
                    aero_tcl_path.read_text(encoding="utf-8"),
                    encoding="utf-8",
                )

                for stale_name in (
                    "realtime_state.txt",
                    "damping_change_log.txt",
                    "analysis_status.txt",
                    "event_stop_log.txt",
                    "explicit_aero_damping_force_log.txt",
                    "quasi_steady_aero_force_log.txt",
                    "incremental_quasi_steady_aero_force_log.txt",
                    "incremental_qs_node_power_log.csv",
                    "element_strain_tension_log.csv",
                    "element_strain_tension_summary_log.csv",
                ):
                    stale_path = Path(output_dir) / stale_name
                    if stale_path.exists():
                        stale_path.unlink()

                display_cfg = self.cfg.get("display", {})
                use_monitor = bool(display_cfg.get("realtime_monitor", True))
                if use_monitor:
                    from .realtime_monitor import RealtimeMonitor

                    th_cfg = self.cfg["time_history"]
                    monitor = RealtimeMonitor(
                        output_dir=output_dir,
                        total_duration=int(th_cfg["npt"]) * float(th_cfg["dt"]),
                        window_seconds=100.0,
                        poll_interval=0.3,
                    )
                    monitor.run_solver_in_thread(
                        lambda _tcl=input_tcl: self.solver.run(
                            _tcl,
                            log_dir=Path(output_dir) / "solver_logs",
                            run_label=f"{f1}_{f2}_time_history",
                        )
                    )
                    monitor.start_gui_loop()
                    if monitor._solver_thread:
                        monitor._solver_thread.join(timeout=10)
                else:
                    self.solver.run(
                        input_tcl,
                        log_dir=Path(output_dir) / "solver_logs",
                        run_label=f"{f1}_{f2}_time_history",
                    )

                # ── Step 3: Post-processing ───────────────────────────────
                self._raise_if_tcl_analysis_failed(Path(output_dir))

                R = load_reaction(output_dir)
                Y, Z = load_displacement(output_dir, n_nodes)

                MAX_DISP[iu, ju] = compute_max_displacement(Y, Z)
                MAX_REAC[iu, ju] = compute_max_reaction(R) / 1000.0  # N → kN
                MAX_CLEARANCE[iu, ju] = float(
                    np.max(compute_clearance(Y, Z, self.geo_result["z"]))
                )

        save_results(
            {
                "MAX_DISP": MAX_DISP,
                "MAX_REAC": MAX_REAC,
                "MAX_CLEARANCE": MAX_CLEARANCE,
                "folder_1": folder_1_list,
                "folder_2": folder_2_list,
            },
            output_dir=output_dir,
            prefix=self.cfg["paths"]["save_prefix"],
        )

    @staticmethod
    def _archive_generated_tcl(source: str, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    def _raise_if_tcl_analysis_failed(self, output_dir: Path) -> None:
        status_path = output_dir / "analysis_status.txt"
        if not status_path.exists():
            return

        values: dict[str, str] = {}
        for line in status_path.read_text(encoding="utf-8", errors="replace").splitlines():
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                values[parts[0]] = parts[1]

        if values.get("STATUS") == "failed":
            message = values.get("MESSAGE", "unknown_tcl_analysis_failure")
            time = values.get("TIME", "unknown")
            code = values.get("ANALYZE_RETURN_CODE", "unknown")
            raise RuntimeError(
                "OpenSees Tcl transient analysis failed "
                f"at t={time}s with analyze return code {code}: {message}. "
                f"See {status_path} and {output_dir / 'solver_logs'}."
            )
