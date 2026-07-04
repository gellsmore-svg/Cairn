#!/usr/bin/env python3
"""Grammar validation for Cairn markdown examples."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"

if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from cairn.grammar import parse_document, validate_document  # noqa: E402


def validate(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    doc = parse_document(text)
    errors: list[str] = []
    if doc.parse_errors:
        errors.extend(f"{path.name}: {err}" for err in doc.parse_errors)
    if not doc.processes:
        errors.append(f"{path.name}: no PROCESS backbone parsed")
    return errors


def main() -> int:
    files = sorted(EXAMPLES.glob("*.cairn.md"))
    if not files:
        print("no examples found", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    wf_notes = 0
    for path in files:
        all_errors.extend(validate(path))
        doc = parse_document(path.read_text(encoding="utf-8"))
        wf_notes += len(validate_document(doc))

    if all_errors:
        for err in all_errors:
            print(err, file=sys.stderr)
        return 1

    print(f"ok: {len(files)} example(s) parsed; {wf_notes} well-formedness note(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())