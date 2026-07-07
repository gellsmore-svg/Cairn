"""CLI for exporting Cairn annotation snippets from UI simulation reports."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cairn.ui_evidence import analyze_ui_simulation_report, format_cairn_annotation_snippet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cairn-ui-annotations",
        description="Export HUMAN_* Cairn annotation blocks from a cairn-ui-sim report.",
    )
    parser.add_argument("input", nargs="?", help="Path to UI simulation report JSON, or stdin with '-'")
    parser.add_argument("-o", "--output", help="Write snippet to file instead of stdout")
    parser.add_argument("--step-title", help="Heading to use for the generated Cairn snippet")
    parser.add_argument("--no-header", action="store_true", help="Only emit annotation blocks, without heading/evidence")
    args = parser.parse_args(argv)

    if args.input in (None, "-"):
        raw = json.loads(sys.stdin.read())
    else:
        raw = json.loads(Path(args.input).read_text(encoding="utf-8"))

    report = analyze_ui_simulation_report(raw)
    out = format_cairn_annotation_snippet(
        report,
        step_title=args.step_title,
        include_header=not args.no_header,
    )

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
