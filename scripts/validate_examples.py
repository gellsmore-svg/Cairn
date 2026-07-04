#!/usr/bin/env python3
"""Light skeleton checks for Cairn markdown examples (not full SPEC prose validation)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"

REQUIRED_MODES = ("CONTEXT", "REQUIREMENTS", "PROCESS")
PROCESS_HEADING = re.compile(r"^##\s+PROCESS\b", re.MULTILINE)
NUMBERED_STEP = re.compile(r"^\s*\d+(?:\.\d+)*[a-z]?\.\s", re.MULTILINE)


def validate(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for mode in REQUIRED_MODES:
        if mode not in text:
            errors.append(f"{path.name}: missing {mode} block")
    if not PROCESS_HEADING.search(text):
        errors.append(f"{path.name}: missing ## PROCESS section")
    if "PROCESS" in text and not NUMBERED_STEP.search(text):
        errors.append(f"{path.name}: PROCESS present but no numbered steps found")
    if text.count("```") % 2 != 0:
        errors.append(f"{path.name}: unbalanced fenced code blocks")
    return errors


def main() -> int:
    files = sorted(EXAMPLES.glob("*.cairn.md"))
    if not files:
        print("no examples found", file=sys.stderr)
        return 1
    all_errors: list[str] = []
    for path in files:
        all_errors.extend(validate(path))
    if all_errors:
        for err in all_errors:
            print(err, file=sys.stderr)
        return 1
    print(f"ok: {len(files)} example(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())