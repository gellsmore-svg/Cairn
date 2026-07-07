"""CLI for LLM role-play review of UI human-load evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cairn.llm_adapters import CommandLLMProvider, HoglahLLMProvider
from cairn.ui_evidence import analyze_ui_simulation_report, interpret_ui_experience


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cairn-ui-roleplay",
        description="Ask an LLM to role-play plausible user experience from a cairn-ui-sim report.",
    )
    parser.add_argument("input", nargs="?", help="Path to UI simulation report JSON, or stdin with '-'")
    parser.add_argument("-o", "--output", help="Write Markdown to file instead of stdout")
    parser.add_argument("--json", action="store_true", help="Write the full interpretation payload as JSON")
    parser.add_argument("--persona", action="append", default=[], help="Persona/perspective to simulate; repeatable")
    parser.add_argument("--cairn-source", help="Optional Cairn source file to include as process context")
    parser.add_argument(
        "--llm-command",
        help="Command provider. Receives JSON on stdin and returns plain text or JSON {text: ...}.",
    )
    parser.add_argument("--hoglah-model", help="Optional Hoglah-backed provider model name")
    parser.add_argument("--hoglah-real", action="store_true", help="Use Hoglah's real adapter instead of its safe stub")
    parser.add_argument("--llm-timeout", type=int, default=120, help="Timeout in seconds for the LLM provider")
    args = parser.parse_args(argv)

    if args.llm_command and args.hoglah_model:
        parser.error("choose either --llm-command or --hoglah-model, not both")
    if not args.llm_command and not args.hoglah_model:
        parser.error("choose --llm-command or --hoglah-model")

    if args.input in (None, "-"):
        raw = json.loads(sys.stdin.read())
    else:
        raw = json.loads(Path(args.input).read_text(encoding="utf-8"))

    cairn_source = Path(args.cairn_source).read_text(encoding="utf-8") if args.cairn_source else None
    evidence = analyze_ui_simulation_report(raw)
    if args.llm_command:
        provider = CommandLLMProvider(args.llm_command, timeout=args.llm_timeout)
    else:
        provider = HoglahLLMProvider(model=args.hoglah_model, use_real=args.hoglah_real, timeout=args.llm_timeout)

    interpretation = interpret_ui_experience(
        raw,
        provider,
        evidence=evidence,
        personas=args.persona or None,
        cairn_source=cairn_source,
    )
    out = json.dumps(interpretation.to_dict(), indent=2) if args.json else interpretation.text

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
