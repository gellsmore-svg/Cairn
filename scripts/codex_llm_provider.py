#!/usr/bin/env python3
"""Use `codex exec` as a Cairn command LLM provider.

The script reads Cairn's standard LLM provider payload from stdin:

    {"task": "...", "prompt": "...", "context": {...}}

It writes:

    {"text": "..."}

This keeps Cairn provider-neutral while making local Codex CLI trials easy.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from json import JSONDecodeError


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except JSONDecodeError as exc:
        raise SystemExit("expected Cairn LLM provider JSON on stdin") from exc
    prompt = str(payload.get("prompt") or "")
    cwd = os.environ.get("CAIRN_CODEX_PROVIDER_CWD", os.getcwd())
    timeout = int(os.environ.get("CAIRN_CODEX_PROVIDER_TIMEOUT", "180"))
    sandbox = os.environ.get("CAIRN_CODEX_PROVIDER_SANDBOX", "read-only")

    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "codex-last-message.md"
        proc = subprocess.run(
            ["codex", "exec", "-s", sandbox, "--ephemeral", "-o", str(output), "-"],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=timeout,
            cwd=cwd,
            check=False,
        )
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout).strip()
            raise RuntimeError(f"codex exec failed with exit code {proc.returncode}: {detail}")
        text = output.read_text(encoding="utf-8") if output.exists() else proc.stdout

    print(json.dumps({"text": text.strip()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
