"""CLI for validating Cairn UI simulation scenario files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cairn.ui_scenarios import format_scenario_validation_report, load_ui_scenario, validate_ui_scenario


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cairn-ui-scenario-validate",
        description="Validate a Cairn UI simulation scenario JSON file.",
    )
    parser.add_argument("scenario", help="Path to a JSON UI simulation scenario")
    parser.add_argument("-f", "--format", choices=("text", "json"), default="text", dest="output_format")
    parser.add_argument("-o", "--output", help="Write validation report to file instead of stdout")
    args = parser.parse_args(argv)

    path = Path(args.scenario)
    report = validate_ui_scenario(load_ui_scenario(path), path=str(path))
    formatted = format_scenario_validation_report(report, output_format=args.output_format)
    out = json.dumps(formatted, indent=2) if args.output_format == "json" else str(formatted)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
