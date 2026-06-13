# solver.py — invoke the OpenSees executable and stream its output
from __future__ import annotations
from datetime import datetime, timezone
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


class OpenSeesSolver:
    """Wrapper around the OpenSees executable.

    Parameters
    ----------
    opensees_path : path to opensees binary or .bat launcher
    work_dir      : directory in which Input.tcl lives and OpenSees will run
    """

    def __init__(self, opensees_path: str, work_dir: str = ".") -> None:
        self.opensees_path = opensees_path
        self.work_dir = Path(work_dir)

    # ──────────────────────────────────────────────────────────────────

    def run(
        self,
        input_tcl: str = "Input.tcl",
        *,
        log_dir: str | Path | None = None,
        run_label: str | None = None,
    ) -> bool:
        """Execute OpenSees on *input_tcl* and stream its output in real time.

        Returns
        -------
        True if OpenSees exited with code 0.

        Raises
        ------
        RuntimeError  if the exit code is non-zero.
        """
        if not self.check_available():
            raise RuntimeError(
                f"OpenSees not found at: {self.opensees_path!r}\n"
                "请在 config/default_config.yaml 的 solver.opensees_path 中"
                "指定 OpenSees 可执行文件路径"
            )

        cmd = self._build_command(input_tcl)
        log_paths = self._prepare_log_paths(log_dir, run_label)

        print(f"[solver] Running: {' '.join(str(c) for c in cmd)}")
        print(f"[solver] Working directory: {self.work_dir.resolve()}")

        started_at = datetime.now(timezone.utc)
        stdout_tail: list[str] = []
        stderr_tail: list[str] = []

        proc = subprocess.Popen(
            cmd,
            cwd=self.work_dir,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        assert proc.stdout is not None
        assert proc.stderr is not None

        stdout_text, stderr_text = proc.communicate()
        if stdout_text:
            print(stdout_text, end="")
            stdout_tail = stdout_text.splitlines()[-80:]
        if stderr_text:
            print(stderr_text, end="", file=sys.stderr)
            stderr_tail = stderr_text.splitlines()[-80:]

        finished_at = datetime.now(timezone.utc)
        return_code = int(proc.returncode)

        if log_paths:
            log_paths["stdout"].write_text(stdout_text or "", encoding="utf-8", errors="replace")
            log_paths["stderr"].write_text(stderr_text or "", encoding="utf-8", errors="replace")
            meta: dict[str, Any] = {
                "run_label": run_label or "opensees_run",
                "input_tcl": input_tcl,
                "command": [str(c) for c in cmd],
                "work_dir": str(self.work_dir.resolve()),
                "opensees_path": str(self.opensees_path),
                "started_at_utc": started_at.isoformat(),
                "finished_at_utc": finished_at.isoformat(),
                "elapsed_seconds": (finished_at - started_at).total_seconds(),
                "return_code": return_code,
                "stdout_log": str(log_paths["stdout"]),
                "stderr_log": str(log_paths["stderr"]),
                "stdout_tail": stdout_tail,
                "stderr_tail": stderr_tail,
            }
            log_paths["meta"].write_text(
                json.dumps(meta, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        if return_code != 0:
            raise RuntimeError(
                f"OpenSees exited with code {return_code}. "
                f"Check solver logs under {log_dir or self.work_dir} for details."
            )

        return True

    def check_available(self) -> bool:
        """Return True if *opensees_path* points to an accessible file.

        Prints a friendly message and returns False when it cannot be found.
        """
        path = Path(self.opensees_path)

        # Accept an exact file match or a name resolvable on PATH
        if path.is_file():
            return True

        # Try locating the executable on PATH (for bare names like "opensees")
        import shutil
        if shutil.which(self.opensees_path) is not None:
            return True

        print(
            f"[solver] OpenSees 未找到: {self.opensees_path!r}\n"
            "请在 config/default_config.yaml 的 solver.opensees_path 中"
            "指定 OpenSees 可执行文件路径"
        )
        return False

    # ──────────────────────────────────────────────────────────────────

    def _build_command(self, input_tcl: str) -> list[str]:
        """Build the subprocess command list for the current platform."""
        path = self.opensees_path

        if sys.platform == "win32" and str(path).lower().endswith(".bat"):
            # .bat files must be launched through cmd on Windows
            return ["cmd", "/c", str(path), input_tcl]

        return [str(path), input_tcl]

    def _prepare_log_paths(
        self,
        log_dir: str | Path | None,
        run_label: str | None,
    ) -> dict[str, Path] | None:
        if log_dir is None:
            return None

        out_dir = Path(log_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        safe_label = "".join(
            ch if ch.isalnum() or ch in ("-", "_", ".") else "_"
            for ch in (run_label or "opensees_run")
        )
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        prefix = out_dir / f"{stamp}_{safe_label}"
        return {
            "stdout": prefix.with_suffix(".stdout.log"),
            "stderr": prefix.with_suffix(".stderr.log"),
            "meta": prefix.with_suffix(".meta.json"),
        }
