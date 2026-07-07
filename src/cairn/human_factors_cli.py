"""CLI for offline Cairn human-factors analysis."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cairn.human_factors import analyze_human_factors, format_human_factors_report, interpret_human_factors
from cairn.llm_adapters import CommandLLMProvider, HoglahLLMProvider


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cairn-human-factors",
        description="Analyze a Cairn document for plausible human-system factors and qualitative risk.",
    )
    parser.add_argument("input", nargs="?", help="Path to .cairn.md file (or stdin with '-')")
    parser.add_argument(
        "-f",
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        dest="output_format",
        help="Output format",
    )
    parser.add_argument("-o", "--output", help="Write to file instead of stdout")
    parser.add_argument(
        "--llm-command",
        help="Optional command provider. Receives JSON on stdin and returns plain text or JSON {text: ...}.",
    )
    parser.add_argument("--hoglah-model", help="Optional Hoglah-backed provider model name")
    parser.add_argument("--hoglah-real", action="store_true", help="Use Hoglah's real adapter instead of its safe stub")
    parser.add_argument("--llm-timeout", type=int, default=120, help="Timeout in seconds for --llm-command")

    args = parser.parse_args(argv)
    if args.input in (None, "-"):
        source = sys.stdin.read()
    else:
        source = Path(args.input).read_text(encoding="utf-8")

    report = analyze_human_factors(source)
    interpretation = None
    if args.llm_command and args.hoglah_model:
        parser.error("choose either --llm-command or --hoglah-model, not both")
    if args.llm_command:
        provider = CommandLLMProvider(args.llm_command, timeout=args.llm_timeout)
        interpretation = interpret_human_factors(source, provider, report=report)
    elif args.hoglah_model:
        provider = HoglahLLMProvider(model=args.hoglah_model, use_real=args.hoglah_real, timeout=args.llm_timeout)
        interpretation = interpret_human_factors(source, provider, report=report)

    if args.output_format == "json":
        payload = {"offline_report": report.to_dict()}
        if interpretation:
            payload["llm_interpretation"] = interpretation.to_dict()
        out = json.dumps(payload, indent=2)
    else:
        out = str(format_human_factors_report(report, output_format=args.output_format))
        if interpretation:
            out += "\n\n# LLM Interpretation\n\n" + interpretation.text

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
