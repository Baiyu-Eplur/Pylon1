# main.py — entry point for cable_analyser
from __future__ import annotations

import argparse
import sys
from src.cable_analyser.analysis import CableAnalysis


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cable_analyser",
        description="Cable Analyser — OpenSees wind-response analysis wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --config config/default_config.yaml
  python main.py --analysis-type MODAL
  python main.py --analysis-type TH --opensees-path "D:/Pyprogramme/OpenSees3.8.0/bin/OpenSees.exe"
""",
    )
    parser.add_argument(
        "--config",
        default="config/default_config.yaml",
        metavar="PATH",
        help="配置文件路径 (default: config/default_config.yaml)",
    )
    parser.add_argument(
        "--analysis-type",
        choices=["STATIC", "MODAL", "TH"],
        metavar="TYPE",
        help="覆盖配置文件中的分析类型 (STATIC | MODAL | TH)",
    )
    parser.add_argument(
        "--opensees-path",
        metavar="PATH",
        help="覆盖配置文件中的 solver.opensees_path",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    analysis = CableAnalysis(args.config)

    # CLI overrides take precedence over config file values
    if args.analysis_type:
        analysis.cfg["analysis"]["type"] = args.analysis_type

    if args.opensees_path:
        analysis.cfg["solver"]["opensees_path"] = args.opensees_path
        # Re-instantiate solver so the new path takes effect
        from src.cable_analyser.solver import OpenSeesSolver
        analysis.solver = OpenSeesSolver(
            opensees_path=args.opensees_path,
            work_dir=analysis.cfg["solver"].get("work_dir", "."),
        )

    if not analysis.solver.check_available():
        sys.exit(1)

    analysis.run()


if __name__ == "__main__":
    main()
