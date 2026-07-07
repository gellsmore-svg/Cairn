"""CLI for discovering Cairn observer surfaces in a repo or stack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cairn.system_discovery import discover_system, format_system_discovery_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cairn-system-discover",
        description="Discover likely observation surfaces and propose a Cairn observer plan.",
    )
    parser.add_argument("root", nargs="?", default=".", help="Repository or stack root to inspect")
    parser.add_argument(
        "-f",
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        dest="output_format",
        help="Output format",
    )
    parser.add_argument("-o", "--output", help="Write report to file instead of stdout")
    args = parser.parse_args(argv)

    report = discover_system(args.root)
    formatted = format_system_discovery_report(report, output_format=args.output_format)
    out = json.dumps(formatted, indent=2) if args.output_format == "json" else str(formatted)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
