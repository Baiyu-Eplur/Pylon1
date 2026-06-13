from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cable_analyser.config_loader import load_config
from cable_analyser.geometry import CableGeometry
from cable_analyser.wind_forces import generate_wind_force_case


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate MATLAB-compatible wind velocities and aerodynamic force files.",
    )
    parser.add_argument("--config", default="config/timur_baseline.yaml")
    parser.add_argument("--u-star", type=float, required=True, help="Friction velocity in m/s.")
    parser.add_argument("--force-name", required=True, help="Output force folder, e.g. FORCE_USTAR_0P80.")
    parser.add_argument("--sim-name", default="SIM1", help="Output simulation folder.")
    parser.add_argument("--wind-dir", help="Output wind folder, e.g. data/wind/SIM_USTAR_0P80.")
    parser.add_argument("--time-file", help="Output time vector path.")
    parser.add_argument("--npt", type=int, help="Number of time steps. Defaults to config time_history.npt.")
    parser.add_argument("--dt", type=float, help="Time step in seconds. Defaults to config time_history.dt.")
    parser.add_argument("--seed", type=int, help="Random seed for reproducible phase generation.")
    parser.add_argument("--support-elevation", type=float, default=49.4)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--metadata-out", help="Optional path to write generation metadata JSON.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    cfg = load_config(ROOT / args.config)
    geo = CableGeometry(cfg).generate()
    overrides = {
        "u_star": args.u_star,
        "force_name": args.force_name,
        "sim_name": args.sim_name,
        "wind_dir": args.wind_dir,
        "time_file": args.time_file,
        "npt": args.npt,
        "dt": args.dt,
        "seed": args.seed,
        "support_elevation": args.support_elevation,
        "overwrite": args.overwrite,
    }
    metadata = generate_wind_force_case(cfg, geo, root=ROOT, overrides=overrides)
    text = json.dumps(metadata, indent=2)
    if args.metadata_out:
        out = ROOT / args.metadata_out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
