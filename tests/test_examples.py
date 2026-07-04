import subprocess
import sys
from pathlib import Path


def test_cairn_examples_pass_skeleton_validation() -> None:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "validate_examples.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout