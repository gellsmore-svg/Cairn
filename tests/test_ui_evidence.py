from __future__ import annotations

import json
from pathlib import Path

from cairn.ui_evidence import analyze_ui_simulation_report, format_ui_human_load_report
from cairn.ui_evidence_cli import main as ui_evidence_main


ROOT = Path(__file__).resolve().parents[1]


def test_ui_simulation_report_becomes_human_load_evidence():
    raw = json.loads((ROOT / "docs" / "analysis" / "mahlah-ui-sim-report.json").read_text(encoding="utf-8"))
    report = analyze_ui_simulation_report(raw)

    assert report.scenario == "mahlah-human-load"
    assert report.metrics["contextSwitches"] == 3
    factors = {(finding.family, finding.factor) for finding in report.findings}
    assert ("cognitive_load", "context switching") in factors
    assert ("organisational_change", "feedback capture burden") in factors
    assert report.risk is not None
    assert report.risk.score == "significant"
    assert "HUMAN_DEMAND" in report.suggested_blocks
    assert "HUMAN_LOAD" in report.suggested_blocks
    assert "context_switches: 3" in report.suggested_blocks["HUMAN_LOAD"]


def test_format_ui_human_load_report_markdown_and_json():
    raw = json.loads((ROOT / "docs" / "analysis" / "mahlah-ui-sim-report.json").read_text(encoding="utf-8"))
    report = analyze_ui_simulation_report(raw)

    markdown = format_ui_human_load_report(report)
    assert "UI Human-Load Evidence" in markdown
    assert "context switching" in markdown

    payload = format_ui_human_load_report(report, output_format="json")
    assert isinstance(payload, dict)
    assert payload["suggested_blocks"]["HUMAN_LOAD"]


def test_ui_evidence_cli_writes_markdown(tmp_path):
    source = ROOT / "docs" / "analysis" / "mahlah-ui-sim-report.json"
    output = tmp_path / "ui-evidence.md"
    rc = ui_evidence_main([str(source), "-o", str(output)])

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    assert "Suggested Cairn Blocks" in text
    assert "HUMAN_RISK" in text
