from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cable_analyser.config_loader import load_config
from cable_analyser.geometry import CableGeometry
from cable_analyser.postprocess import (
    compute_clearance,
    compute_max_displacement,
    compute_max_reaction,
    load_displacement,
    load_reaction,
)


def load_output_matrix(path: Path, max_rows: int | None = None) -> np.ndarray | None:
    if not path.exists() or path.stat().st_size == 0:
        return None
    rows = []
    expected_cols = None
    skipped = 0
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if max_rows is not None and len(rows) >= max_rows:
                break
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split()
            if expected_cols is None:
                expected_cols = len(parts)
            if len(parts) != expected_cols:
                skipped += 1
                continue
            try:
                rows.append([float(value) for value in parts])
            except ValueError:
                skipped += 1
    if not rows:
        return None
    data = np.array(rows, dtype=float)
    if skipped:
        print(f"Skipped {skipped} incomplete rows in {path}")
    if data.ndim == 1:
        data = data[np.newaxis, :]
    return data


def envelope_growth_metric(series: np.ndarray) -> dict:
    if len(series) < 20:
        return {"usable": False}
    n = len(series)
    block = max(10, n // 10)
    early = float(np.percentile(series[:block], 95))
    late = float(np.percentile(series[-block:], 95))
    mid = float(np.percentile(series[n // 2:n // 2 + block], 95))
    return {
        "usable": True,
        "early_p95": early,
        "mid_p95": mid,
        "late_p95": late,
        "late_over_mid": late / mid if abs(mid) > 1e-12 else None,
        "late_over_early": late / early if abs(early) > 1e-12 else None,
    }


def read_damping_log(path: Path) -> dict:
    if not path.exists() or path.stat().st_size == 0:
        return {
            "exists": path.exists(),
            "n": 0,
            "min_xi": None,
            "max_xi": None,
            "negative_count": 0,
            "negative_fraction": 0.0,
        }
    data = np.loadtxt(path)
    if data.ndim == 1:
        data = data[np.newaxis, :]
    time = data[:, 0]
    xi = data[:, 3]
    return {
        "exists": True,
        "n": int(len(xi)),
        "min_time_s": float(np.min(time)),
        "max_time_s": float(np.max(time)),
        "min_xi": float(np.min(xi)),
        "max_xi": float(np.max(xi)),
        "mean_xi": float(np.mean(xi)),
        "negative_count": int(np.sum(xi < 0)),
        "negative_fraction": float(np.mean(xi < 0)),
    }


def galloping_assessment(audit: dict) -> dict:
    damping = audit["damping_log"]
    envelope = audit["global_resultant_envelope"]
    negative_fraction = float(damping.get("negative_fraction", 0.0) or 0.0)
    min_xi = damping.get("min_xi")
    negative_damping_seen = bool(damping.get("negative_count", 0) > 0)
    sustained_negative_damping = bool(
        negative_fraction >= 0.005
        and min_xi is not None
        and float(min_xi) < -1.0e-4
    )
    sustained_growth = False
    if envelope.get("usable"):
        late_over_mid = envelope.get("late_over_mid")
        late_over_early = envelope.get("late_over_early")
        sustained_growth = bool(
            late_over_mid is not None
            and late_over_early is not None
            and late_over_mid >= 1.20
            and late_over_early >= 1.50
        )
    confirmed = sustained_negative_damping and sustained_growth
    incipient = sustained_negative_damping or sustained_growth
    triggers = []
    if negative_damping_seen:
        triggers.append("negative_effective_damping_seen")
    if sustained_negative_damping:
        triggers.append("sustained_negative_effective_damping")
    if sustained_growth:
        triggers.append("sustained_response_growth")
    return {
        "galloping_candidate": incipient,
        "confirmed_galloping": confirmed,
        "triggers": triggers,
        "negative_damping_seen": negative_damping_seen,
        "sustained_negative_damping": sustained_negative_damping,
        "sustained_growth": sustained_growth,
        "criteria": {
            "aerodynamic_susceptibility": "Den Hartog delta_D = dC_L/dalpha + C_D < 0, alpha in radians",
            "negative_damping_seen": "damping_log.negative_count > 0",
            "sustained_negative_damping": "negative_fraction >= 0.005 and min_xi < -1e-4",
            "sustained_growth": "global late_over_mid >= 1.20 and late_over_early >= 1.50",
            "confirmed_galloping": "sustained_negative_damping and sustained_growth",
        },
    }


def build_audit(config_path: Path) -> dict:
    cfg = load_config(config_path)
    geo = CableGeometry(cfg).generate()
    output_dir = ROOT / cfg["paths"]["output_dir"]
    n_nodes = len(geo["x"])

    dynamic_raw = load_output_matrix(output_dir / "Dynamic.out")
    reaction_raw = load_output_matrix(output_dir / "Reaction.out")
    velocity_raw = load_output_matrix(output_dir / "Velocity.out")
    accel_raw = load_output_matrix(output_dir / "Accel.out")

    if dynamic_raw is None:
        raise FileNotFoundError(output_dir / "Dynamic.out")
    if reaction_raw is None:
        raise FileNotFoundError(output_dir / "Reaction.out")

    disp_data = dynamic_raw
    if disp_data.shape[1] == 3 * n_nodes + 1:
        disp_data = disp_data[:, 1:]
    if disp_data.shape[1] != 3 * n_nodes:
        raise ValueError(
            f"Dynamic.out has {disp_data.shape[1]} displacement columns; "
            f"expected {3 * n_nodes}"
        )
    y = disp_data[:, 1::3]
    z = disp_data[:, 2::3]

    reaction = reaction_raw
    if reaction.shape[1] == 4:
        reaction = reaction[:, 1:]
    resultant_disp = np.sqrt(y**2 + z**2)
    node_peak = np.max(resultant_disp, axis=0)
    peak_node_index = int(np.argmax(node_peak))
    clearance = compute_clearance(y, z, geo["z"])

    time_steps = dynamic_raw.shape[0]
    dt = float(cfg["time_history"]["dt"])
    duration = time_steps * dt

    mid_node = n_nodes // 2
    mid_resultant = resultant_disp[:, mid_node]
    all_node_max_each_step = np.max(resultant_disp, axis=1)

    damping_log = read_damping_log(output_dir / "damping_change_log.txt")
    audit = {
        "config": str(config_path.relative_to(ROOT)),
        "output_dir": str(output_dir.relative_to(ROOT)),
        "n_nodes": n_nodes,
        "time_steps_dynamic": int(dynamic_raw.shape[0]),
        "time_steps_reaction": int(reaction_raw.shape[0]),
        "time_steps_velocity": int(velocity_raw.shape[0]) if velocity_raw is not None else None,
        "time_steps_accel": int(accel_raw.shape[0]) if accel_raw is not None else None,
        "dt_s": dt,
        "duration_s": duration,
        "damping_log_end_time_s": damping_log.get("max_time_s"),
        "max_displacement_m": compute_max_displacement(y, z),
        "max_displacement_node": peak_node_index + 1,
        "max_displacement_node_x_m": float(geo["x"][peak_node_index]),
        "max_reaction_kN": compute_max_reaction(reaction) / 1000.0,
        "max_clearance_m": float(np.max(clearance)),
        "min_clearance_m": float(np.min(clearance)),
        "midspan_resultant_envelope": envelope_growth_metric(mid_resultant),
        "global_resultant_envelope": envelope_growth_metric(all_node_max_each_step),
        "damping_log": damping_log,
    }
    audit["galloping_assessment"] = galloping_assessment(audit)
    return audit


def write_markdown(audit: dict, path: Path) -> None:
    lines = [
        "# Dynamic Response Audit",
        "",
        f"Config: `{audit['config']}`",
        f"Output dir: `{audit['output_dir']}`",
        "",
        "## Output Coverage",
        "",
        f"- Nodes: `{audit['n_nodes']}`",
        f"- Dynamic/reaction steps: `{audit['time_steps_dynamic']}` / `{audit['time_steps_reaction']}`",
        f"- Velocity/accel steps: `{audit['time_steps_velocity']}` / `{audit['time_steps_accel']}`",
        f"- dt/duration: `{audit['dt_s']}` s / `{audit['duration_s']}` s",
        f"- Damping-log end time: `{audit['damping_log_end_time_s']}` s",
        "",
        "## Peak Metrics",
        "",
        f"- Max displacement: `{audit['max_displacement_m']:.6g}` m",
        f"- Max displacement node: `{audit['max_displacement_node']}` at x = `{audit['max_displacement_node_x_m']:.6g}` m",
        f"- Max reaction: `{audit['max_reaction_kN']:.6g}` kN",
        f"- Max clearance: `{audit['max_clearance_m']:.6g}` m",
        f"- Min clearance: `{audit['min_clearance_m']:.6g}` m",
        "",
        "## Envelope Growth",
        "",
        f"- Midspan resultant: `{audit['midspan_resultant_envelope']}`",
        f"- Global stepwise max resultant: `{audit['global_resultant_envelope']}`",
        "",
        "## Aerodynamic Damping Log",
        "",
        f"`{audit['damping_log']}`",
        "",
        "## Galloping Assessment",
        "",
        f"`{audit['galloping_assessment']}`",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/timur_baseline.yaml")
    parser.add_argument("--out-dir", default="output/response_audit/timur_baseline")
    args = parser.parse_args()

    config_path = (ROOT / args.config).resolve()
    out_dir = (ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    audit = build_audit(config_path)
    (out_dir / "dynamic_response_audit.json").write_text(
        json.dumps(audit, indent=2), encoding="utf-8"
    )
    write_markdown(audit, out_dir / "dynamic_response_audit.md")
    print(f"Wrote {out_dir / 'dynamic_response_audit.md'}")


if __name__ == "__main__":
    main()
