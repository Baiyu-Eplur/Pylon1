from __future__ import annotations

import argparse
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cable_analyser.config_loader import dump_config, load_config
from cable_analyser.geometry import CableGeometry
from cable_analyser.wind_forces import generate_wind_force_case


def parse_u_stars(text: str) -> list[float]:
    values = []
    for item in text.split(","):
        item = item.strip()
        if item:
            values.append(float(item))
    if not values:
        raise ValueError("at least one u_star is required")
    return values


def ustar_label(u_star: float, precision: int = 2) -> str:
    return f"{u_star:.{precision}f}".replace(".", "P")


def build_case_config(
    base_cfg: dict[str, Any],
    *,
    u_star: float,
    npt: int,
    dt: float,
    seed: int,
    sweep_name: str,
    output_root: Path,
    label_precision: int,
    include_seed_in_name: bool,
) -> tuple[dict[str, Any], dict[str, str]]:
    label = ustar_label(u_star, precision=label_precision)
    case_label = f"{label}_SEED{seed}" if include_seed_in_name else label
    force_name = f"FORCE_PY_USTAR_{case_label}_N{npt}"
    sim_name = "SIM1"
    wind_dir = f"data/wind/SIM_PY_USTAR_{case_label}_N{npt}"
    time_file = f"{wind_dir}/time.txt"
    output_dir = str(output_root / "runs" / f"ustar_{case_label}")
    cfg = deepcopy(base_cfg)
    cfg["analysis"]["type"] = "TH"
    cfg["time_history"]["folder_1"] = [force_name]
    cfg["time_history"]["folder_2"] = [sim_name]
    cfg["time_history"]["dt"] = dt
    cfg["time_history"]["npt"] = npt
    cfg.setdefault("wind_generation", {})
    cfg["wind_generation"].update(
        {
            "enabled": True,
            "u_star": u_star,
            "force_name": force_name,
            "sim_name": sim_name,
            "wind_dir": wind_dir,
            "time_file": time_file,
            "seed": seed,
            "reuse_existing": True,
            "overwrite": False,
        }
    )
    cfg["paths"]["wind_dir"] = wind_dir
    cfg["paths"]["time_file"] = time_file
    cfg["paths"]["output_dir"] = output_dir
    cfg["paths"]["save_prefix"] = f"{sweep_name}_USTAR_{case_label}"
    paths = {
        "label": label,
        "case_label": case_label,
        "force_name": force_name,
        "sim_name": sim_name,
        "wind_dir": wind_dir,
        "time_file": time_file,
        "output_dir": output_dir,
    }
    return cfg, paths


def write_manifest_markdown(manifest: dict[str, Any], path: Path) -> None:
    lines = [
        "# u_star Sweep Manifest",
        "",
        f"Sweep: `{manifest['sweep_name']}`",
        f"Base config: `{manifest['base_config']}`",
        f"npt/dt: `{manifest['npt']}` / `{manifest['dt']}`",
        f"Generated forces: `{manifest['generated_forces']}`",
        f"Executed analyses: `{manifest['executed']}`",
        "",
        "| u_star | Config | Force dir | Wind dir | Output dir |",
        "|---:|---|---|---|---|",
    ]
    for case in manifest["cases"]:
        lines.append(
            f"| {case['u_star']} | `{case['config_path']}` | "
            f"`{case['force_dir']}` | `{case['wind_dir']}` | `{case['output_dir']}` |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare/generate/run a u_star sweep.")
    parser.add_argument("--base-config", default="config/timur_baseline.yaml")
    parser.add_argument("--u-stars", required=True, help="Comma-separated values, e.g. 0.6,0.8,1.0")
    parser.add_argument("--npt", type=int, default=65536)
    parser.add_argument("--dt", type=float, default=0.05)
    parser.add_argument("--seed-base", type=int, default=20260529)
    parser.add_argument("--sweep-name", default="ustar_sweep")
    parser.add_argument("--out-dir", default="output/sweeps/ustar_sweep")
    parser.add_argument(
        "--label-precision",
        type=int,
        default=2,
        help="Decimal places used in generated case labels. Use 3 for values such as 0.325.",
    )
    parser.add_argument(
        "--include-seed-in-name",
        action="store_true",
        help="Include the seed in config, force, wind, and output names for repeated-realization studies.",
    )
    parser.add_argument("--generate", action="store_true", help="Generate wind/force files for each case.")
    parser.add_argument("--execute", action="store_true", help="Run OpenSees TH analysis for each case.")
    args = parser.parse_args()

    out_root = ROOT / args.out_dir
    config_dir = out_root / "configs"
    manifest_path = out_root / "manifest.json"
    base_cfg = load_config(ROOT / args.base_config)
    u_stars = parse_u_stars(args.u_stars)
    cases = []

    for idx, u_star in enumerate(u_stars):
        cfg, paths = build_case_config(
            base_cfg,
            u_star=u_star,
            npt=args.npt,
            dt=args.dt,
            seed=args.seed_base + idx,
            sweep_name=args.sweep_name,
            output_root=out_root,
            label_precision=args.label_precision,
            include_seed_in_name=args.include_seed_in_name,
        )
        config_path = config_dir / f"ustar_{paths['case_label']}.yaml"
        dump_config(cfg, config_path)
        case = {
            "u_star": u_star,
            "seed": args.seed_base + idx,
            "config_path": str(config_path.relative_to(ROOT)),
            "case_label": paths["case_label"],
            "force_dir": str((ROOT / cfg["paths"]["forces_dir"] / paths["force_name"] / paths["sim_name"]).relative_to(ROOT)),
            "wind_dir": paths["wind_dir"],
            "time_file": paths["time_file"],
            "output_dir": paths["output_dir"],
            "generated": False,
            "executed": False,
        }
        if args.generate:
            geo = CableGeometry(cfg).generate()
            meta = generate_wind_force_case(cfg, geo, root=ROOT)
            case["generated"] = True
            case["generation_u_star"] = meta["wind"]["u_star_mps"]
        if args.execute:
            subprocess.run(
                [sys.executable, str(ROOT / "main.py"), "--config", str(config_path)],
                cwd=ROOT,
                check=True,
            )
            case["executed"] = True
        cases.append(case)

    manifest = {
        "sweep_name": args.sweep_name,
        "base_config": args.base_config,
        "u_stars": u_stars,
        "npt": args.npt,
        "dt": args.dt,
        "label_precision": args.label_precision,
        "include_seed_in_name": bool(args.include_seed_in_name),
        "generated_forces": bool(args.generate),
        "executed": bool(args.execute),
        "cases": cases,
    }
    out_root.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    write_manifest_markdown(manifest, out_root / "manifest.md")
    print(f"Wrote {manifest_path}")


if __name__ == "__main__":
    main()
