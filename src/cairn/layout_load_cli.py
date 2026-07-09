"""CLI for functional layout load analysis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from cairn.layout_load import analyze_functional_layout, format_functional_layout_report, render_layout_svg


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze form/functional layout cognitive load from UI geometry JSON.")
    parser.add_argument("input", nargs="?", help="Input JSON file. Reads stdin when omitted or '-'.")
    parser.add_argument("-o", "--output", help="Output path. Writes stdout when omitted.")
    parser.add_argument("-f", "--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--svg-output", help="Optional SVG overlay output path.")
    args = parser.parse_args(argv)

    try:
        raw = sys.stdin.read() if args.input in (None, "-") else Path(args.input).read_text(encoding="utf-8")
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("input JSON must be an object")
        report = analyze_functional_layout(payload)
        formatted = format_functional_layout_report(report, output_format=args.format)
        out = json.dumps(formatted, indent=2) if args.format == "json" else str(formatted)
        if args.svg_output:
            Path(args.svg_output).write_text(render_layout_svg(payload), encoding="utf-8")
        if args.output:
            Path(args.output).write_text(out, encoding="utf-8")
        else:
            print(out)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"cairn-layout-load: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
