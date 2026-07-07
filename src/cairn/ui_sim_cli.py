"""CLI for running UI simulation scenarios through Playwright.

The implementation delegates to a small Node runner so Cairn does not need a
hard Playwright dependency. Run it from, or point it at, a project that already
has Playwright installed.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cairn-ui-sim",
        description="Run a Playwright-backed UI simulation scenario and collect human-load evidence.",
    )
    parser.add_argument("scenario", help="Path to a JSON UI simulation scenario")
    parser.add_argument("--project-root", default=".", help="Project root whose node_modules include Playwright")
    parser.add_argument("--base-url", help="Override scenario baseUrl")
    parser.add_argument("--output", "-o", help="Write JSON report to this path")
    parser.add_argument("--headed", action="store_true", help="Run browser headed instead of headless")
    parser.add_argument("--timeout", type=int, default=30000, help="Default action timeout in ms")

    args = parser.parse_args(argv)
    runner = Path(__file__).with_name("ui_sim_runner.mjs")
    env = dict(os.environ)
    if args.base_url:
        env["CAIRN_UI_BASE_URL"] = args.base_url
    if args.output:
        env["CAIRN_UI_OUTPUT"] = args.output
    env["CAIRN_UI_HEADED"] = "1" if args.headed else "0"
    env["CAIRN_UI_TIMEOUT"] = str(args.timeout)

    command = ["node", str(runner), str(Path(args.scenario).resolve())]
    proc = subprocess.run(command, cwd=args.project_root, env=env, text=True)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
