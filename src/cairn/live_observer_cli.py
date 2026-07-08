"""CLI for summarising live product observations as Cairn evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from cairn.live_observer import analyze_live_observations, format_live_observation_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cairn-live-observe",
        description="Summarise JSON/JSONL live observation events as Cairn human/system evidence.",
    )
    parser.add_argument("input", nargs="?", help="Path to JSON/JSONL observations, or stdin with '-'")
    parser.add_argument("--title", default="Live product observation", help="Report title")
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

    try:
        raw = sys.stdin.read() if args.input in (None, "-") else Path(args.input).read_text(encoding="utf-8")
        observations = _load_observations(raw)
    except (OSError, ValueError) as exc:
        print(f"cairn-live-observe: {exc}", file=sys.stderr)
        return 2
    report = analyze_live_observations(observations, title=args.title)
    formatted = format_live_observation_report(report, output_format=args.output_format)
    out = json.dumps(formatted, indent=2) if args.output_format == "json" else str(formatted)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0


def _load_observations(raw: str) -> list[dict[str, Any]]:
    text = raw.strip()
    if not text:
        return []
    if text[0] in "[{":
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            if text[0] == "[":
                raise ValueError(f"Invalid JSON input: {exc}") from exc
            parsed = None
        if isinstance(parsed, list):
            return [_as_record(item, index=index) for index, item in enumerate(parsed, start=1)]
        if isinstance(parsed, dict):
            return [dict(parsed)]
    records: list[dict[str, Any]] = []
    for index, line in enumerate(raw.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(_as_record(json.loads(line), index=index))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {index}: {exc}") from exc
    return records


def _as_record(value: Any, *, index: int) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object at record {index}, got {type(value).__name__}")
    return dict(value)


if __name__ == "__main__":
    raise SystemExit(main())
