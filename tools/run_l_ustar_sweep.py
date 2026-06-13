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


def parse_values(text: str) -> list[float]:
    values = []
    for item in text.split(","):
        item = item.strip()
        if item:
            values.append(float(item))
    if not values:
        raise ValueError("at least one value is required")
    return values


def label(value: float, precision: int) -> str:
    return f"{value:.{precision}f}".replace(".", "P")


def sag_from_l(base_cfg: dict[str, Any], l_value: float, mode: str) -> float:
    base_l = float(base_cfg["geometry"]["L"])
    base_sag = float(base_cfg["geometry"]["Sag"])
    if mode == "baseline_parabolic":
        return base_sag * (l_value / base_l) ** 2
    if mode == "keep_ratio":
        return base_sag * l_value / base_l
    if mode == "parabolic_tension":
        weight = float(base_cfg["material"]["self_weight_N_per_m"])
        tension = float(base_cfg["analysis"]["pretension_load"])
        return weight * l_value**2 / (8.0 * tension)
    raise ValueError(f"Unknown sag mode: {mode}")


def build_case_config(
    base_cfg: dict[str, Any],
    *,
    l_value: float,
    sag_value: float,
    u_star: float,
    npt: int,
    dt: float,
    seed: int,
    sweep_name: str,
    output_root: Path,
    l_precision: int,
    u_precision: int,
) -> tuple[dict[str, Any], dict[str, str]]:
    l_label = label(l_value, l_precision)
    u_label = label(u_star, u_precision)
    case_label = f"L{l_label}_U{u_label}_SEED{seed}"
    force_name = f"FORCE_PY_{case_label}_N{npt}"
    sim_name = "SIM1"
    wind_dir = f"data/wind/SIM_PY_{case_label}_N{npt}"
    time_file = f"{wind_dir}/time.txt"
    output_dir = str(output_root / "runs" / case_label)

    cfg = deepcopy(base_cfg)
    cfg["geometry"]["L"] = float(l_value)
    cfg["geometry"]["Sag"] = float(sag_value)
    cfg["geometry"]["discretisation"] = float(l_value) / 100.0
    cfg["analysis"]["type"] = "TH"
    cfg["time_history"]["folder_1"] = [force_name]
    cfg["time_history"]["folder_2"] = [sim_name]
    cfg["time_history"]["dt"] = dt
    cfg["time_history"]["npt"] = npt
    cfg.setdefault("wind_generation", {})
    cfg["wind_generation"].update(
        {
            "enabled": True,
            "u_star": float(u_star),
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
    cfg["paths"]["save_prefix"] = f"{sweep_name}_{case_label}"
    cfg.setdefault("display", {})["realtime_monitor"] = False

    return cfg, {
        "case_label": case_label,
        "force_name": force_name,
        "sim_name": sim_name,
        "wind_dir": wind_dir,
        "time_file": time_file,
        "output_dir": output_dir,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare/generate/run an L-u_star grid sweep.")
    parser.add_argument("--base-config", default="config/timur_generated_ustar.yaml")
    parser.add_argument("--l-values", required=True, help="Comma-separated span lengths.")
    parser.add_argument("--u-stars", required=True, help="Comma-separated u_star values.")
    parser.add_argument(
        "--sag-mode",
        choices=["baseline_parabolic", "parabolic_tension", "keep_ratio"],
        default="baseline_parabolic",
    )
    parser.add_argument("--npt", type=int, default=2048)
    parser.add_argument("--dt", type=float, default=0.05)
    parser.add_argument("--seed-base", type=int, default=20260800)
    parser.add_argument("--sweep-name", default="l_ustar_sweep")
    parser.add_argument("--out-dir", default="output/sweeps/l_ustar_sweep")
    parser.add_argument("--l-label-precision", type=int, default=1)
    parser.add_argument("--u-label-precision", type=int, default=3)
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue sweep and record failed cases when OpenSees exits non-zero.",
    )
    args = parser.parse_args()

    base_cfg = load_config(ROOT / args.base_config)
    l_values = parse_values(args.l_values)
    u_stars = parse_values(args.u_stars)
    out_root = ROOT / args.out_dir
    config_dir = out_root / "configs"
    cases = []
    case_index = 0

    for l_value in l_values:
        sag_value = sag_from_l(base_cfg, l_value, args.sag_mode)
        for u_star in u_stars:
            seed = args.seed_base + case_index
            cfg, paths = build_case_config(
                base_cfg,
                l_value=l_value,
                sag_value=sag_value,
                u_star=u_star,
                npt=args.npt,
                dt=args.dt,
                seed=seed,
                sweep_name=args.sweep_name,
                output_root=out_root,
                l_precision=args.l_label_precision,
                u_precision=args.u_label_precision,
            )
            config_path = config_dir / f"{paths['case_label']}.yaml"
            dump_config(cfg, config_path)
            case = {
                "case_label": paths["case_label"],
                "L_m": float(l_value),
                "Sag_m": float(sag_value),
                "u_star": float(u_star),
                "seed": seed,
                "config_path": str(config_path.relative_to(ROOT)),
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
                try:
                    subprocess.run(
                        [sys.executable, str(ROOT / "main.py"), "--config", str(config_path)],
                        cwd=ROOT,
                        check=True,
                    )
                    case["executed"] = True
                except subprocess.CalledProcessError as exc:
                    case["executed"] = False
                    case["failed"] = True
                    case["returncode"] = exc.returncode
                    if not args.continue_on_error:
                        raise
            cases.append(case)
            case_index += 1

    manifest = {
        "sweep_name": args.sweep_name,
        "base_config": args.base_config,
        "sag_mode": args.sag_mode,
        "l_values": l_values,
        "u_stars": u_stars,
        "npt": args.npt,
        "dt": args.dt,
        "generated_forces": bool(args.generate),
        "executed": bool(args.execute),
        "cases": cases,
    }
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {out_root / 'manifest.json'}")


if __name__ == "__main__":
    main()
