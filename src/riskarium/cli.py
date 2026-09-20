"""Command line: `riskarium validate CASE` and `riskarium report CASE -o DIR`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .heatmap import render as render_heatmap
from .model import CaseError, load_case
from .report import render_report
from .scoring import summarize


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="riskarium",
        description="Build a risk register and an ISO 27001 mapping from a YAML case file.",
    )
    parser.add_argument("--version", action="version", version=f"riskarium {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("validate", help="check a case file without writing anything")
    check.add_argument("case", type=Path)

    report = sub.add_parser("report", help="write report.md and heatmap.svg")
    report.add_argument("case", type=Path)
    report.add_argument("-o", "--out", type=Path, default=Path("."), help="output directory")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        case = load_case(args.case)
    except (CaseError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    summary = summarize(case)
    if args.command == "validate":
        print(f"OK: {len(case.risks)} risks, {len(case.sources)} sources")
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "report.md").write_text(render_report(case), encoding="utf-8")
    (args.out / "heatmap.svg").write_text(render_heatmap(case), encoding="utf-8")
    print(
        f"wrote {args.out / 'report.md'} and {args.out / 'heatmap.svg'} "
        f"(mean score {summary.mean_before:.1f} -> {summary.mean_after:.1f})"
    )
    return 0
