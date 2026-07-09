"""CLI for summarising UI simulation reports as human-load evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cairn.ui_evidence import (
    analyze_ui_simulation_report,
    format_ui_layout_overlay_index,
    format_ui_human_load_report,
    render_ui_layout_overlay,
    render_ui_layout_overlays,
)


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
    parser.add_argument("--layout-svg-output", help="Write a measured layout snapshot as an SVG overlay")
    parser.add_argument("--layout-svg-output-dir", help="Write every measured layout snapshot as numbered SVG overlays")
    parser.add_argument(
        "--layout-snapshot-index",
        type=int,
        default=0,
        help="Zero-based layoutLoad snapshot index to render with --layout-svg-output",
    )
    args = parser.parse_args(argv)

    if args.input in (None, "-"):
        raw = json.loads(sys.stdin.read())
    else:
        raw = json.loads(Path(args.input).read_text(encoding="utf-8"))

    report = analyze_ui_simulation_report(raw)
    formatted = format_ui_human_load_report(report, output_format=args.output_format)
    out = json.dumps(formatted, indent=2) if args.output_format == "json" else str(formatted)
    if args.layout_svg_output:
        svg = render_ui_layout_overlay(raw, snapshot_index=args.layout_snapshot_index)
        if svg is None:
            raise SystemExit(f"layoutLoad snapshot {args.layout_snapshot_index} not found in UI simulation report")
        Path(args.layout_svg_output).write_text(svg, encoding="utf-8")
    if args.layout_svg_output_dir:
        output_dir = Path(args.layout_svg_output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        overlays = render_ui_layout_overlays(raw)
        if not overlays:
            raise SystemExit("no layoutLoad snapshots found in UI simulation report")
        filenames: dict[int, str] = {}
        for index, svg in overlays:
            filename = f"layout-snapshot-{index + 1}.svg"
            (output_dir / filename).write_text(svg, encoding="utf-8")
            filenames[index] = filename
        (output_dir / "index.md").write_text(format_ui_layout_overlay_index(raw, filenames=filenames), encoding="utf-8")

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
