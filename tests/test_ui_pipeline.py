from __future__ import annotations

from pathlib import Path
import sys

from cairn.ui_pipeline_cli import main as ui_pipeline_main


ROOT = Path(__file__).resolve().parents[1]


def test_ui_pipeline_from_report_writes_default_outputs(tmp_path, capsys):
    scenario = ROOT / "docs" / "scenarios" / "mahlah-recovery-loop.json"
    report = ROOT / "docs" / "analysis" / "mahlah-recovery-loop-ui-sim-report.json"
    evidence = tmp_path / "evidence.md"
    annotations = tmp_path / "annotations.cairn.md"

    rc = ui_pipeline_main(
        [
            str(scenario),
            "--from-report",
            str(report),
            "--evidence-output",
            str(evidence),
            "--annotations-output",
            str(annotations),
            "--step-title",
            "Pipeline recovery annotations",
        ]
    )
    captured = capsys.readouterr()

    assert rc == 0
    assert "evidence:" in captured.out
    assert "UI Human-Load Evidence" in evidence.read_text(encoding="utf-8")
    annotation_text = annotations.read_text(encoding="utf-8")
    assert "## Pipeline recovery annotations" in annotation_text
    assert "RECOVERY:" in annotation_text


def test_ui_pipeline_from_report_can_roleplay_with_command_provider(tmp_path):
    script = tmp_path / "fake_roleplay.py"
    script.write_text(
        "import json, sys\n"
        "payload = json.load(sys.stdin)\n"
        "print(json.dumps({'text': 'Pipeline roleplay: ' + payload['context']['ui_evidence']['scenario']}))\n",
        encoding="utf-8",
    )
    scenario = ROOT / "docs" / "scenarios" / "mahlah-recovery-loop.json"
    report = ROOT / "docs" / "analysis" / "mahlah-recovery-loop-ui-sim-report.json"
    roleplay = tmp_path / "roleplay.md"

    rc = ui_pipeline_main(
        [
            str(scenario),
            "--from-report",
            str(report),
            "--evidence-output",
            str(tmp_path / "evidence.md"),
            "--annotations-output",
            str(tmp_path / "annotations.cairn.md"),
            "--roleplay-output",
            str(roleplay),
            "--llm-command",
            f"{sys.executable} {script}",
        ]
    )

    assert rc == 0
    assert roleplay.read_text(encoding="utf-8") == "Pipeline roleplay: mahlah-recovery-loop"
