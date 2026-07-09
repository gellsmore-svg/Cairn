"""CLI for producing a Cairn agent harness plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cairn.agent_harness import build_agent_harness_plan, format_agent_harness_plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cairn-agent-harness-plan",
        description="Plan deterministic Cairn CLI/API steps for an interactive agent harness.",
    )
    parser.add_argument("--process", help="Optional Cairn process file")
    parser.add_argument("--ui-evidence", help="Optional UI simulation report JSON")
    parser.add_argument("--layout", help="Optional layout JSON")
    parser.add_argument("--output-dir", default="cairn-agent-output", help="Directory the planned commands should write to")
    parser.add_argument("--title", default="Tool-assisted Cairn agent analysis")
    parser.add_argument("-f", "--format", choices=("markdown", "json", "shell"), default="markdown", dest="output_format")
    parser.add_argument("-o", "--output", help="Write plan to file instead of stdout")
    args = parser.parse_args(argv)

    plan = build_agent_harness_plan(
        process_path=args.process,
        ui_evidence_path=args.ui_evidence,
        layout_path=args.layout,
        output_dir=args.output_dir,
        title=args.title,
    )
    formatted = format_agent_harness_plan(plan, output_format=args.output_format)
    out = json.dumps(formatted, indent=2) if isinstance(formatted, dict) else formatted
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
