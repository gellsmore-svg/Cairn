from __future__ import annotations

import json
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


def test_ui_pipeline_from_report_writes_layout_overlay_when_measured(tmp_path, capsys):
    scenario = ROOT / "docs" / "scenarios" / "customer-po-review-layout.json"
    report = ROOT / "docs" / "analysis" / "customer-po-review-ui-sim-report.json"
    layout_svg = tmp_path / "po-layout-overlay.svg"

    rc = ui_pipeline_main(
        [
            str(scenario),
            "--from-report",
            str(report),
            "--evidence-output",
            str(tmp_path / "evidence.md"),
            "--annotations-output",
            str(tmp_path / "annotations.cairn.md"),
            "--layout-svg-output",
            str(layout_svg),
        ]
    )
    captured = capsys.readouterr()

    assert rc == 0
    assert "layout_svg:" in captured.out
    assert "duplicate_warning" in layout_svg.read_text(encoding="utf-8")


def test_ui_pipeline_from_report_writes_selected_layout_snapshot(tmp_path, capsys):
    scenario = ROOT / "docs" / "scenarios" / "customer-po-review-layout.json"
    report = tmp_path / "multi-layout-ui-sim-report.json"
    layout_svg = tmp_path / "selected-layout-overlay.svg"
    report.write_text(
        json.dumps(
            {
                "scenario": "multi-layout-flow",
                "metrics": {"clicks": 0, "fills": 0, "waits": 0, "contextSwitches": 0, "layoutSnapshots": 2},
                "observations": [],
                "layoutLoad": [
                    {
                        "viewport": {"width": 800, "height": 600},
                        "elements": [
                            {"id": "first_state_action", "role": "button", "x": 120, "y": 80, "width": 140, "height": 44}
                        ],
                        "sequence": ["first_state_action"],
                    },
                    {
                        "viewport": {"width": 800, "height": 600},
                        "elements": [
                            {"id": "second_state_action", "role": "button", "x": 420, "y": 320, "width": 140, "height": 44}
                        ],
                        "sequence": ["second_state_action"],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    rc = ui_pipeline_main(
        [
            str(scenario),
            "--from-report",
            str(report),
            "--evidence-output",
            str(tmp_path / "evidence.md"),
            "--annotations-output",
            str(tmp_path / "annotations.cairn.md"),
            "--layout-svg-output",
            str(layout_svg),
            "--layout-snapshot-index",
            "1",
        ]
    )
    captured = capsys.readouterr()

    assert rc == 0
    assert "layout_svg:" in captured.out
    text = layout_svg.read_text(encoding="utf-8")
    assert "second_state_action" in text
    assert "first_state_action" not in text


def test_ui_pipeline_from_report_writes_all_layout_snapshots(tmp_path, capsys):
    scenario = ROOT / "docs" / "scenarios" / "customer-po-review-layout.json"
    report = tmp_path / "multi-layout-ui-sim-report.json"
    layout_svg_dir = tmp_path / "layout-overlays"
    report.write_text(
        json.dumps(
            {
                "scenario": "multi-layout-flow",
                "metrics": {"clicks": 0, "fills": 0, "waits": 0, "contextSwitches": 0, "layoutSnapshots": 2},
                "observations": [],
                "layoutLoad": [
                    {
                        "viewport": {"width": 800, "height": 600},
                        "elements": [
                            {"id": "first_state_action", "role": "button", "x": 120, "y": 80, "width": 140, "height": 44}
                        ],
                        "sequence": ["first_state_action"],
                    },
                    {
                        "viewport": {"width": 800, "height": 600},
                        "elements": [
                            {"id": "second_state_action", "role": "button", "x": 420, "y": 320, "width": 140, "height": 44}
                        ],
                        "sequence": ["second_state_action"],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    rc = ui_pipeline_main(
        [
            str(scenario),
            "--from-report",
            str(report),
            "--evidence-output",
            str(tmp_path / "evidence.md"),
            "--annotations-output",
            str(tmp_path / "annotations.cairn.md"),
            "--layout-svg-output-dir",
            str(layout_svg_dir),
        ]
    )
    captured = capsys.readouterr()

    assert rc == 0
    assert "layout_svg_dir:" in captured.out
    assert "layout_svg_index:" in captured.out
    assert "first_state_action" in (layout_svg_dir / "layout-snapshot-1.svg").read_text(encoding="utf-8")
    assert "second_state_action" in (layout_svg_dir / "layout-snapshot-2.svg").read_text(encoding="utf-8")
    index = (layout_svg_dir / "index.md").read_text(encoding="utf-8")
    assert "[layout-snapshot-1.svg](layout-snapshot-1.svg)" in index
    assert "Snapshot 2" in index


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
