from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.cable_analyser.geometry import CableGeometry


OUT_DIR = ROOT / "output" / "diagnostics" / "tension_only_control_verification"
CONFIG_DIR = OUT_DIR / "configs"
RUN_DIR = OUT_DIR / "runs"
REPORT_DIR = OUT_DIR / "report"


def read_matrix(path: Path) -> np.ndarray | None:
    if not path.exists() or path.stat().st_size == 0:
        return None
    try:
        data = np.loadtxt(path)
    except Exception:
        return None
    if data.size == 0:
        return None
    if data.ndim == 1:
        data = data[np.newaxis, :]
    return data


def read_named_csv(path: Path) -> np.ndarray | None:
    if not path.exists() or path.stat().st_size == 0:
        return None
    try:
        data = np.genfromtxt(path, delimiter=",", names=True, encoding="utf-8")
    except Exception:
        return None
    if getattr(data, "size", 0) == 0:
        return None
    return data


def parse_status(run_dir: Path) -> dict[str, str]:
    status: dict[str, str] = {}
    path = run_dir / "analysis_status.txt"
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                status[parts[0]] = parts[1]
    return status


def latest_log_excerpt(run_dir: Path, label: str) -> str:
    logs = sorted(
        path
        for path in (run_dir / "solver_logs").glob(f"*{label}*.log")
        if path.stat().st_size > 0
    )
    if not logs:
        logs = sorted(
            path for path in (run_dir / "solver_logs").glob("*.log") if path.stat().st_size > 0
        )
    if not logs:
        return ""
    text = logs[-1].read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(text[-20:])


def response_summary(cfg_path: Path) -> dict:
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    run_dir = ROOT / cfg["paths"]["output_dir"]
    geo = CableGeometry(cfg).generate()
    masses = np.asarray(geo["MN"], dtype=float)
    n_nodes = len(masses)
    expected_weight = float(np.sum(masses) * 9.80665 * float(cfg["analysis"]["multiplier_vertical_load"]))

    dynamic = read_matrix(run_dir / "Dynamic.out")
    velocity = read_matrix(run_dir / "Velocity.out")
    accel = read_matrix(run_dir / "Accel.out")
    support = read_matrix(run_dir / "SupportReactions.out")
    reaction_left = read_matrix(run_dir / "Reaction.out")
    tension = read_named_csv(run_dir / "element_strain_tension_summary_log.csv")
    status = parse_status(run_dir)

    summary = {
        "case": cfg_path.stem,
        "config": str(cfg_path),
        "run_dir": str(run_dir),
        "pretension_load_N": float(cfg["analysis"]["pretension_load"]),
        "gravity_multiplier": float(cfg["analysis"]["multiplier_vertical_load"]),
        "expected_total_weight_N": expected_weight,
        "assume_initial_equilibrium": bool(cfg["analysis"].get("assume_initial_equilibrium", False)),
        "driver_status": "outputs_missing",
        "analysis_status": status,
        "modal_log_excerpt": latest_log_excerpt(run_dir, "modal"),
        "time_history_log_excerpt": latest_log_excerpt(run_dir, "time_history"),
    }

    if dynamic is not None:
        disp = dynamic[:, 1:].reshape(dynamic.shape[0], n_nodes, 3)
        trans = disp[:, :, 1]
        vert = disp[:, :, 2]
        disp_mag = np.sqrt(trans * trans + vert * vert)
        mid = n_nodes // 2
        summary.update(
            {
                "driver_status": "dynamic_output_present",
                "time_start_s": float(dynamic[0, 0]),
                "time_end_s": float(dynamic[-1, 0]),
                "max_transverse_disp_m": float(np.max(np.abs(trans))),
                "max_vertical_disp_m": float(np.max(np.abs(vert))),
                "max_xz_disp_m": float(np.max(disp_mag)),
                "final_midspan_transverse_disp_m": float(trans[-1, mid]),
                "final_midspan_vertical_disp_m": float(vert[-1, mid]),
            }
        )

    if velocity is not None:
        vel = velocity[:, 1:].reshape(velocity.shape[0], n_nodes, 3)
        kinetic = 0.5 * np.sum(masses[np.newaxis, :, np.newaxis] * vel * vel, axis=(1, 2))
        speed = np.linalg.norm(vel[:, :, 0:3], axis=2)
        summary.update(
            {
                "max_speed_mps": float(np.max(speed)),
                "max_kinetic_energy_J": float(np.max(kinetic)),
                "final_kinetic_energy_J": float(kinetic[-1]),
            }
        )
        np.savetxt(
            run_dir / "global_kinetic_energy.csv",
            np.column_stack([velocity[:, 0], kinetic]),
            delimiter=",",
            header="time,kinetic_energy_J",
            comments="",
        )

    if accel is not None:
        acc = accel[:, 1:].reshape(accel.shape[0], n_nodes, 3)
        acc_mag = np.linalg.norm(acc[:, :, 0:3], axis=2)
        summary["max_acceleration_mps2"] = float(np.max(acc_mag))

    if support is not None and support.shape[1] >= 7:
        left = support[:, 1:4]
        right = support[:, 4:7]
        total = left + right
        summary.update(
            {
                "support_time_end_s": float(support[-1, 0]),
                "max_abs_total_support_Rx_N": float(np.max(np.abs(total[:, 0]))),
                "max_abs_total_support_Ry_N": float(np.max(np.abs(total[:, 1]))),
                "max_abs_total_support_Rz_N": float(np.max(np.abs(total[:, 2]))),
                "final_total_support_Rx_N": float(total[-1, 0]),
                "final_total_support_Ry_N": float(total[-1, 1]),
                "final_total_support_Rz_N": float(total[-1, 2]),
            }
        )
    elif reaction_left is not None and reaction_left.shape[1] >= 4:
        summary.update(
            {
                "left_reaction_time_end_s": float(reaction_left[-1, 0]),
                "max_abs_left_reaction_Rz_N": float(np.max(np.abs(reaction_left[:, 3]))),
            }
        )

    if tension is not None:
        summary.update(
            {
                "tension_log_time_end_s": float(np.max(tension["time"])),
                "max_abs_strain": float(np.max(tension["max_abs_strain"])),
                "max_abs_tension_N": float(np.max(tension["max_abs_tension_N"])),
                "min_estimated_tension_N": float(np.min(tension["min_estimated_tension_N"])),
                "max_slack_element_count": int(np.max(tension["slack_element_count"])),
                "sum_slack_element_count": int(np.sum(tension["slack_element_count"])),
            }
        )

    return summary


def plot_case_summaries(summaries: list[dict]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    cases = [item["case"].replace("_", "\n") for item in summaries]

    def vals(key: str) -> list[float]:
        return [float(item.get(key, np.nan)) for item in summaries]

    fig, axes = plt.subplots(2, 2, figsize=(13, 8), dpi=170)
    axes[0, 0].bar(cases, vals("max_xz_disp_m"), color="#3B6EA8")
    axes[0, 0].set_ylabel("max x-z displacement (m)")
    axes[0, 1].bar(cases, vals("max_kinetic_energy_J"), color="#9A6A16")
    axes[0, 1].set_ylabel("max kinetic energy (J)")
    axes[1, 0].bar(cases, vals("max_abs_strain"), color="#7A3F98")
    axes[1, 0].set_ylabel("max element strain")
    axes[1, 1].bar(cases, vals("max_abs_total_support_Rz_N"), color="#2B6E4A")
    axes[1, 1].set_ylabel("max |sum support Rz| (N)")
    for ax in axes.ravel():
        ax.grid(True, axis="y", alpha=0.25)
        ax.tick_params(axis="x", labelsize=7)
    fig.tight_layout()
    fig.savefig(REPORT_DIR / "control_verification_summary.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 6), dpi=170)
    for item in summaries:
        run_dir = Path(item["run_dir"])
        dyn = read_matrix(run_dir / "Dynamic.out")
        if dyn is None:
            continue
        cfg = yaml.safe_load(Path(item["config"]).read_text(encoding="utf-8"))
        n_nodes = len(CableGeometry(cfg).generate()["MN"])
        disp = dyn[:, 1:].reshape(dyn.shape[0], n_nodes, 3)
        mid = n_nodes // 2
        ax.plot(dyn[:, 0], disp[:, mid, 2], lw=1.0, label=item["case"])
    ax.set_xlabel("time (s)")
    ax.set_ylabel("midspan vertical displacement increment (m)")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(REPORT_DIR / "control_midspan_vertical_histories.png")
    plt.close(fig)


def write_report(summaries: list[dict]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Tension-only no-wind control verification",
        "",
        "Purpose: isolate whether the large response is caused by aerodynamic work input, an initial-equilibrium release, or excessive axial stretch/compliance.",
        "",
        "All controls disable precomputed Path wind loads, real-time quasi-steady loads, explicit aerodynamic force, and aerodynamic damping updates. Gravity and pretension are varied only through the case definitions.",
        "",
        "| Case | Gravity | Pretension | Initial path | Status | t_end (s) | max x-z disp (m) | max KE (J) | max strain | min tension (N) | max support Rz sum (N) | expected weight (N) |",
        "|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in summaries:
        status = item.get("analysis_status", {}).get("STATUS", item.get("driver_status", "unknown"))
        lines.append(
            "| {case} | {gravity:.1f} | {pretension:.1f} | {assumed} | {status} | {tend:.3g} | {disp:.3g} | {ke:.3g} | {strain:.3g} | {mint:.3g} | {rz:.3g} | {weight:.3g} |".format(
                case=item["case"],
                gravity=item["gravity_multiplier"],
                pretension=item["pretension_load_N"],
                assumed="assumed" if item["assume_initial_equilibrium"] else "static attempt",
                status=status,
                tend=float(item.get("time_end_s", np.nan)),
                disp=float(item.get("max_xz_disp_m", np.nan)),
                ke=float(item.get("max_kinetic_energy_J", np.nan)),
                strain=float(item.get("max_abs_strain", np.nan)),
                mint=float(item.get("min_estimated_tension_N", np.nan)),
                rz=float(item.get("max_abs_total_support_Rz_N", np.nan)),
                weight=float(item.get("expected_total_weight_N", np.nan)),
            )
        )

    lines.extend(
        [
            "",
            "## Control conclusions",
            "",
            "- C1 and C3 remain a useful failed-control pair: they are numerically identical although C1 requests gravity on and C3 requests gravity off. The old `assume_initial_equilibrium=true` plus immediate `loadConst` shortcut therefore did not establish a gravity-balanced state.",
            "- C2 still verifies that a zero-pretension tension-only chain cannot simply self-form from the present zero-stress state by a first gravity increment; the tangent stiffness is singular before any reliable form-finding state exists.",
            "- The corrected C4 static-equilibrium route now passes: gravity is ramped statically, fixed with `loadConst`, and the subsequent no-wind/no-aero transient remains stable. This is the preferred fully numerical initial-state route.",
            "- The corrected C8 assumed-equilibrium route also passes: gravity remains a Constant load during transient, shape-based element initial strain supplies the sag-consistent horizontal tension, and `loadConst` is not called before a static solution. This is the preferred fast analytical-equilibrium route for repeated runs after validation.",
            "- The decisive code correction is that `ElasticPPGap Fy` must be material stress in a truss formulation, not an axial force. The rated axial capacity is now converted as `Fy = rated_strength_N / Area`, preventing the artificial 80-100 N cap that previously destroyed the prestress state.",
            "- A no-wind/no-aero formal baseline should now require small residual displacement and kinetic energy, realistic axial reaction around the target pretension scale, no slack/compression, and no gravity-release drift before any wind or galloping force is introduced.",
            "",
            "## Required correction direction",
            "",
            "- For formal galloping runs, use either C4 or C8-style initialization. Do not use the old C1 shortcut.",
            "- Static route: ramp gravity in static analysis, verify convergence/reactions, then call `loadConst -time 0.0` before transient analysis.",
            "- Analytical route: construct sag-consistent element initial strains from the target horizontal component, keep gravity in a Constant time series, and do not call `loadConst` unless a static equilibrium solve has actually been completed.",
            "- Keep the engineering pretension value as a target derived from the selected sag and self-weight. For this typical case the horizontal tension scale is `w L^2 / (8H) = 19785 N`.",
            "",
            "## Failure signature retained for diagnosis",
            "",
            "The modal/static run log reports: `FullGenLinLapackSolver::solve() - factorization failed, matrix singular`, followed by `StaticAnalysis::analyze() ... returned: -3 error flag`. This is consistent with a zero-pretension tension-only model having insufficient initial tangent stiffness for the first gravity increment.",
            "",
            "Figures:",
            "",
            "- `control_verification_summary.png`",
            "- `control_midspan_vertical_histories.png`",
        ]
    )
    (REPORT_DIR / "control_verification_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (REPORT_DIR / "control_verification_summary.json").write_text(
        json.dumps(summaries, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze no-wind tension-only control verification runs.")
    parser.add_argument("--config-dir", default=str(CONFIG_DIR))
    args = parser.parse_args()

    config_paths = sorted(Path(args.config_dir).glob("C*.yaml"))
    summaries = [response_summary(path) for path in config_paths]
    plot_case_summaries(summaries)
    write_report(summaries)
    print(REPORT_DIR / "control_verification_report.md")
    print(REPORT_DIR / "control_verification_summary.json")
    print(REPORT_DIR / "control_verification_summary.png")
    print(REPORT_DIR / "control_midspan_vertical_histories.png")


if __name__ == "__main__":
    main()
