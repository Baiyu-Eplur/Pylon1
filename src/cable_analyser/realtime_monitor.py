# realtime_monitor.py — poll OpenSees output files and update live matplotlib plots
#
# Architecture: OpenSees runs in a child thread; matplotlib GUI stays on the
# main thread (required by Tkinter).
from __future__ import annotations

import time
import threading
from pathlib import Path
from collections import deque
from typing import Callable

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

MAX_POINTS = 2000


class RealtimeMonitor:
    """OpenSees in worker thread, matplotlib GUI on main thread.

    Usage::

        monitor = RealtimeMonitor(output_dir, total_duration)
        monitor.run_solver_in_thread(lambda: solver.run(input_tcl))
        monitor.start_gui_loop()          # blocks until analysis done & window closed
    """

    def __init__(
        self,
        output_dir: str,
        total_duration: float,
        window_seconds: float = 100.0,
        poll_interval: float = 0.3,
        **kwargs,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.total_duration = total_duration
        self.poll_interval = poll_interval
        self._solver_done = threading.Event()
        self._solver_thread: threading.Thread | None = None

        self.t       = deque(maxlen=MAX_POINTS)
        self.disp_y  = deque(maxlen=MAX_POINTS)
        self.disp_z  = deque(maxlen=MAX_POINTS)
        self.vel_y   = deque(maxlen=MAX_POINTS)
        self.vel_z   = deque(maxlen=MAX_POINTS)
        self.acc_y   = deque(maxlen=MAX_POINTS)
        self.acc_z   = deque(maxlen=MAX_POINTS)
        self.damp_t  = deque(maxlen=MAX_POINTS)
        self.damp_xi = deque(maxlen=MAX_POINTS)
        self.progress = 0.0
        self._last_state_time = -1.0

        state_file = self.output_dir / "realtime_state.txt"
        if state_file.exists():
            try:
                state_file.unlink()
            except OSError:
                pass

        damp_file = self.output_dir / "damping_change_log.txt"
        if damp_file.exists():
            try:
                damp_file.unlink()
            except OSError:
                pass

        self.window_size = window_seconds

    # ── solver thread ─────────────────────────────────────────────

    def run_solver_in_thread(self, solver_func: Callable[[], None]) -> None:
        def _wrapper() -> None:
            try:
                solver_func()
            finally:
                self._solver_done.set()

        self._solver_thread = threading.Thread(target=_wrapper, daemon=True)
        self._solver_thread.start()

    # ── file readers ──────────────────────────────────────────────

    def _read_realtime_state(self) -> dict | None:
        path = self.output_dir / "realtime_state.txt"
        if not path.exists():
            return None
        try:
            data: dict[str, float] = {}
            with open(path, "r", errors="replace") as f:
                for line in f:
                    try:
                        parts = line.strip().split()
                        if len(parts) == 2:
                            data[parts[0]] = float(parts[1])
                    except (ValueError, IndexError):
                        continue
            return data if "TIME" in data else None
        except OSError:
            return None

    def _read_damping_log(self) -> tuple[list[float], list[float]]:
        path = self.output_dir / "damping_change_log.txt"
        if not path.exists():
            return [], []
        times: list[float] = []
        xis: list[float] = []
        try:
            with open(path, "rb") as f:
                f.seek(0, 2)
                file_size = f.tell()
                read_size = min(200 * 1024, file_size)
                f.seek(-read_size, 2)
                raw = f.read()
            text = raw.decode("utf-8", errors="replace")
            lines = text.splitlines()
            for line in lines[1:]:
                try:
                    parts = line.strip().split()
                    if len(parts) == 4 and parts[1] == "1":
                        times.append(float(parts[0]))
                        xis.append(float(parts[3]))
                except (ValueError, IndexError):
                    continue
        except OSError:
            pass
        return times, xis

    # ── figure setup ──────────────────────────────────────────────

    def _setup_figure(self) -> None:
        self.fig = plt.figure(figsize=(16, 9))
        self.fig.patch.set_facecolor("#1e1e2e")
        self.fig.suptitle(
            "Cable Analyser — Realtime Monitor",
            color="white", fontsize=14, fontweight="bold",
        )

        gs = gridspec.GridSpec(3, 2, figure=self.fig, hspace=0.45, wspace=0.35)

        titles = [
            "Displacement Y (mm)",   "Displacement Z (mm)",
            "Velocity Y (m/s)",      "Velocity Z (m/s)",
            "Acceleration Y (m/s²)", "Equivalent Damping ξ",
        ]
        colors = [
            "#89dceb", "#a6e3a1", "#fab387",
            "#f38ba8", "#cba6f7", "#f9e2af",
        ]
        positions = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]

        self.axes: list[plt.Axes] = []
        self.lines: list[plt.Line2D] = []

        for idx, (r, c) in enumerate(positions):
            ax = self.fig.add_subplot(gs[r, c])
            ax.set_facecolor("#313244")
            ax.tick_params(colors="#cdd6f4", labelsize=8)
            for spine in ax.spines.values():
                spine.set_color("#45475a")
            ax.set_title(titles[idx], color=colors[idx], fontsize=9, fontweight="bold")
            ax.set_xlabel("Time (s)", color="#cdd6f4", fontsize=7)
            (line,) = ax.plot([], [], color=colors[idx], linewidth=1.2)
            ax.set_xlim(0.0, self.window_size)
            ax.set_ylim(-0.1, 0.1)
            self.axes.append(ax)
            self.lines.append(line)

        self.progress_text = self.fig.text(
            0.5, 0.01, "Waiting for analysis to start...",
            ha="center", color="#cdd6f4", fontsize=10,
            fontname="monospace", transform=self.fig.transFigure,
        )

    # ── data + plot refresh ───────────────────────────────────────

    def _update_data(self) -> None:
        state = self._read_realtime_state()
        if state:
            t = state["TIME"]
            if t > self._last_state_time:
                self._last_state_time = t
                self.t.append(t)
                self.disp_y.append(state.get("DISP_Y", 0))
                self.disp_z.append(state.get("DISP_Z", 0))
                self.vel_y.append(state.get("VEL_Y", 0))
                self.vel_z.append(state.get("VEL_Z", 0))
                self.acc_y.append(state.get("ACCEL_Y", 0))
                self.acc_z.append(state.get("ACCEL_Z", 0))
                self.progress = state.get("PROGRESS", 0)

        damp_times, damp_xis = self._read_damping_log()
        if damp_times:
            self.damp_t  = deque(damp_times[-MAX_POINTS:], maxlen=MAX_POINTS)
            self.damp_xi = deque(damp_xis[-MAX_POINTS:],   maxlen=MAX_POINTS)

    def _update_plots(self) -> None:
        if len(self.t) < 2:
            return

        current_t = list(self.t)[-1]
        ws = self.window_size
        scroll_trigger = ws * 0.8

        if current_t < scroll_trigger:
            x_min = 0.0
            x_max = ws
        elif current_t < ws:
            x_min = 0.0
            x_max = ws
        else:
            x_min = current_t - ws * 0.8
            x_max = x_min + ws

        datasets = [
            (self.t, [v * 1000 for v in self.disp_y]),
            (self.t, [v * 1000 for v in self.disp_z]),
            (self.t, self.vel_y),
            (self.t, self.vel_z),
            (self.t, self.acc_y),
            (self.damp_t, self.damp_xi),
        ]

        for i, (xs, ys) in enumerate(datasets):
            if len(xs) < 2:
                continue
            try:
                xarr = np.array(list(xs), dtype=float)
                yarr = np.array(list(ys), dtype=float)

                self.lines[i].set_data(xarr, yarr)
                self.axes[i].set_xlim(x_min, x_max)

                mask = (xarr >= x_min) & (xarr <= x_max)
                if mask.sum() > 1:
                    y_vis = yarr[mask]
                    y_cur_min = float(y_vis.min())
                    y_cur_max = float(y_vis.max())
                    y_range = y_cur_max - y_cur_min
                    margin = max(y_range * 0.15, 0.001)
                    self.axes[i].set_ylim(
                        y_cur_min - margin,
                        y_cur_max + margin,
                    )
            except Exception:
                continue

        self.progress_text.set_text(
            f"Progress: {self.progress:.1f}%  |  "
            f"T = {current_t:.2f} s / {self.total_duration:.1f} s  |  "
            f"Window: {x_min:.1f} ~ {x_max:.1f} s"
        )

    # ── main-thread GUI loop ──────────────────────────────────────

    def start_gui_loop(self) -> None:
        self._setup_figure()

        plt.ion()
        plt.show(block=False)

        for _ in range(5):
            try:
                self.fig.canvas.flush_events()
            except Exception:
                pass
            time.sleep(0.05)

        while not self._solver_done.is_set():
            _t0 = time.perf_counter()
            try:
                self._update_data()
                self._update_plots()
                self.fig.canvas.draw_idle()
                self.fig.canvas.flush_events()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"[monitor] _tick error: {e}")

            time.sleep(self.poll_interval)
            try:
                self.fig.canvas.flush_events()
            except Exception:
                pass

            _elapsed = time.perf_counter() - _t0
            if _elapsed > 1.0:
                try:
                    _dsize = (self.output_dir / "damping_change_log.txt").stat().st_size // 1024
                except OSError:
                    _dsize = -1
                print(f"[perf] loop took {_elapsed:.2f}s | "
                      f"data={len(self.t)} | "
                      f"damp_log_size={_dsize}KB")

        try:
            self._update_data()
            self._update_plots()
            current_t = list(self.t)[-1] if self.t else self.total_duration
            self.progress_text.set_text(
                f"✓ Analysis Complete  |  "
                f"T = {current_t:.2f} s  |  Progress: 100.0%"
            )
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
        except Exception:
            pass

        plt.ioff()
        print("[monitor] Analysis complete. Close the plot window to continue.")
        plt.show(block=True)
