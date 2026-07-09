from __future__ import annotations

import json

import cairn
from cairn.reporting import build_analysis_report, format_analysis_report
from cairn.reporting_cli import main as report_main


def _process() -> str:
    return """
PROCESS — Review AI-assisted PO.
  1. Review AI recommendation with uncertainty display. [HUMAN, ASSISTED-BY: LLM]
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: medium
"""


def _layout() -> dict:
    return {
        "scenario": "po-report",
        "metrics": {"clicks": 0, "fills": 0, "waits": 0, "contextSwitches": 0, "layoutSnapshots": 1},
        "observations": [],
        "layoutLoad": [
            {
                "viewport": {"width": 1200, "height": 800},
                "elements": [
                    {"id": "warning", "role": "warning", "x": 40, "y": 600, "width": 300, "height": 60},
                    {"id": "accept", "role": "button", "x": 980, "y": 120, "width": 120, "height": 44},
                ],
                "relations": [{"from": "warning", "to": "accept", "type": "evidence_to_action"}],
                "sequence": ["warning", "accept"],
            }
        ],
    }


def test_build_analysis_report_includes_recommendations():
    report = build_analysis_report(process_text=_process(), interface_evidence=_layout())

    assert report.recommendations is not None
    assert report.recommendations.recommendations
    markdown = format_analysis_report(report)
    assert "Traceable Interface Recommendations" in markdown
    assert "Future State Visual" in markdown
    assert "```svg" in markdown
    assert "okf/concepts/" in markdown
    assert cairn.build_analysis_report is build_analysis_report


def test_generate_report_cli_writes_markdown(tmp_path):
    process = tmp_path / "process.cairn.md"
    evidence = tmp_path / "evidence.json"
    output = tmp_path / "report.md"
    process.write_text(_process(), encoding="utf-8")
    evidence.write_text(json.dumps(_layout()), encoding="utf-8")

    rc = report_main(["--input", str(process), "--interface-evidence", str(evidence), "-o", str(output)])

    assert rc == 0
    assert "Executive Summary" in output.read_text(encoding="utf-8")
