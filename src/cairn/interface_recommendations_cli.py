"""CLI for OKF-traceable interface recommendations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from cairn.interface_recommendations import (
    format_interface_recommendations,
    future_state_svg,
    recommend_interface_changes,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cairn-recommend-interface-changes",
        description="Generate OKF-traceable interface change recommendations from UI evidence JSON.",
    )
    parser.add_argument("input", nargs="?", help="UI simulation report or layout JSON; stdin when omitted or '-'")
    parser.add_argument("-f", "--format", choices=("markdown", "json"), default="markdown", dest="output_format")
    parser.add_argument("-o", "--output", help="Write recommendations to file instead of stdout")
    parser.add_argument("--future-svg-output", help="Write a simple future-state SVG summary")
    args = parser.parse_args(argv)

    raw = json.loads(sys.stdin.read()) if args.input in (None, "-") else json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = recommend_interface_changes(raw)
    formatted = format_interface_recommendations(report, output_format=args.output_format)
    out = json.dumps(formatted, indent=2) if args.output_format == "json" else str(formatted)
    if args.future_svg_output:
        Path(args.future_svg_output).write_text(future_state_svg(report), encoding="utf-8")
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
