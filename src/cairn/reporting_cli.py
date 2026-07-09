"""CLI for generating Cairn analysis reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cairn.reporting import build_analysis_report, format_analysis_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cairn-generate-report",
        description="Generate a structured Cairn analysis report from process and/or UI evidence.",
    )
    parser.add_argument("--input", help="Optional Cairn process file")
    parser.add_argument("--interface-evidence", help="Optional UI simulation report or layout JSON")
    parser.add_argument("-f", "--format", choices=("markdown", "json", "html", "pdf"), default="markdown", dest="output_format")
    parser.add_argument("-o", "--output", help="Write report to file")
    parser.add_argument("--title", default="Cairn Analysis Report")
    args = parser.parse_args(argv)

    process_text = Path(args.input).read_text(encoding="utf-8") if args.input else None
    evidence = json.loads(Path(args.interface_evidence).read_text(encoding="utf-8")) if args.interface_evidence else None
    report = build_analysis_report(title=args.title, process_text=process_text, interface_evidence=evidence)
    formatted = format_analysis_report(report, output_format=args.output_format)
    if args.output:
        if isinstance(formatted, bytes):
            Path(args.output).write_bytes(formatted)
        else:
            Path(args.output).write_text(json.dumps(formatted, indent=2) if isinstance(formatted, dict) else str(formatted), encoding="utf-8")
    else:
        if isinstance(formatted, bytes):
            raise SystemExit("binary report output requires --output")
        print(json.dumps(formatted, indent=2) if isinstance(formatted, dict) else formatted)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
