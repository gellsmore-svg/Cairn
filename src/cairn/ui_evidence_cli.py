"""CLI for summarising UI simulation reports as human-load evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cairn.ui_evidence import analyze_ui_simulation_report, format_ui_human_load_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cairn-ui-evidence",
        description="Summarise a cairn-ui-sim JSON report as human-load evidence.",
    )
    parser.add_argument("input", nargs="?", help="Path to UI simulation report JSON, or stdin with '-'")
    parser.add_argument(
        "-f",
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        dest="output_format",
        help="Output format",
    )
    parser.add_argument("-o", "--output", help="Write to file instead of stdout")
    args = parser.parse_args(argv)

    if args.input in (None, "-"):
        raw = json.loads(sys.stdin.read())
    else:
        raw = json.loads(Path(args.input).read_text(encoding="utf-8"))

    report = analyze_ui_simulation_report(raw)
    formatted = format_ui_human_load_report(report, output_format=args.output_format)
    out = json.dumps(formatted, indent=2) if args.output_format == "json" else str(formatted)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
