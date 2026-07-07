"""CLI for turning Galeed exports into Cairn live-observation evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from cairn.galeed_adapter import galeed_records_to_observations
from cairn.live_observer import analyze_live_observations, format_live_observation_report
from cairn.live_observer_cli import _load_observations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cairn-galeed-observe",
        description="Convert Galeed trace/LLM-call exports into Cairn live-observation evidence.",
    )
    parser.add_argument("input", nargs="?", help="Path to Galeed JSON/JSONL records, or stdin with '-'")
    parser.add_argument("--record-type", choices=("trace_event", "llm_call"), default="trace_event")
    parser.add_argument("--title", default="Galeed live observation", help="Report title")
    parser.add_argument("--observations-output", help="Write converted observation JSONL to this path")
    parser.add_argument(
        "-f",
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        dest="output_format",
        help="Report output format",
    )
    parser.add_argument("-o", "--output", help="Write report to file instead of stdout")
    args = parser.parse_args(argv)

    raw = sys.stdin.read() if args.input in (None, "-") else Path(args.input).read_text(encoding="utf-8")
    records = _load_records(raw)
    observations = galeed_records_to_observations(records, record_type=args.record_type)

    if args.observations_output:
        Path(args.observations_output).write_text(
            "\n".join(json.dumps(item) for item in observations) + "\n",
            encoding="utf-8",
        )

    report = analyze_live_observations(observations, title=args.title)
    formatted = format_live_observation_report(report, output_format=args.output_format)
    out = json.dumps(formatted, indent=2) if args.output_format == "json" else str(formatted)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0


def _load_records(raw: str) -> list[dict[str, Any]]:
    return _load_observations(raw)


if __name__ == "__main__":
    raise SystemExit(main())
