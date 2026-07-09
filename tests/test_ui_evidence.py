from __future__ import annotations

import json
from pathlib import Path

import sys

from cairn.llm_adapters import LLMRequest, LLMResponse
from cairn.ui_evidence import (
    analyze_ui_simulation_report,
    build_ui_roleplay_prompt,
    format_cairn_annotation_snippet,
    format_ui_human_load_report,
    interpret_ui_experience,
    render_ui_layout_overlay,
)
from cairn.ui_annotations_cli import main as ui_annotations_main
from cairn.ui_evidence_cli import main as ui_evidence_main
from cairn.ui_roleplay_cli import main as ui_roleplay_main


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


def test_missing_information_report_marks_uncertainty_load():
    raw = json.loads(
        (ROOT / "docs" / "analysis" / "mahlah-missing-information-ui-sim-report.json").read_text(encoding="utf-8")
    )
    report = analyze_ui_simulation_report(raw)

    factors = {(finding.family, finding.factor) for finding in report.findings}
    assert ("cognitive_load", "uncertainty load") in factors
    assert report.risk is not None
    assert report.risk.score == "significant"
    assert "uncertainty management" in report.suggested_blocks["HUMAN_LOAD"]


def test_ui_evidence_includes_functional_layout_load_snapshots():
    raw = {
        "scenario": "po-review-layout",
        "metrics": {"clicks": 1, "fills": 0, "waits": 0, "contextSwitches": 0, "layoutSnapshots": 1},
        "observations": [
            {
                "type": "human_load",
                "phase": "orientation",
                "systems": ["attention"],
                "demand": "The user orients to PO risk and available action.",
            }
        ],
        "layoutLoad": [
            {
                "viewport": {"width": 1440, "height": 900},
                "elements": [
                    {"id": "po_number", "role": "field", "x": 40, "y": 120, "width": 200, "height": 36},
                    {"id": "duplicate_warning", "role": "warning", "x": 980, "y": 620, "width": 260, "height": 48},
                    {"id": "accept", "role": "button", "x": 1120, "y": 140, "width": 120, "height": 44},
                ],
                "relations": [
                    {"from": "po_number", "to": "duplicate_warning", "type": "related"},
                    {"from": "duplicate_warning", "to": "accept", "type": "evidence_to_action"},
                ],
                "sequence": ["po_number", "duplicate_warning", "accept"],
            }
        ],
    }

    report = analyze_ui_simulation_report(raw)

    factors = {(finding.family, finding.factor) for finding in report.findings}
    assert any(family == "functional_layout_load" and "layout traversal load" in factor for family, factor in factors)
    assert "FUNCTIONAL_LAYOUT_LOAD" in report.suggested_blocks
    assert "layout_load:" in report.suggested_blocks["FUNCTIONAL_LAYOUT_LOAD"]

    snippet = format_cairn_annotation_snippet(report, step_title="PO layout evidence")
    assert "FUNCTIONAL_LAYOUT_LOAD:" in snippet
    assert "layout_load:" in snippet


def test_render_ui_layout_overlay_uses_first_layout_snapshot():
    raw = json.loads((ROOT / "docs" / "analysis" / "customer-po-review-ui-sim-report.json").read_text(encoding="utf-8"))

    svg = render_ui_layout_overlay(raw)

    assert svg is not None
    assert svg.startswith("<svg")
    assert "duplicate_warning" in svg
    assert "evidence_to_action" in svg


def test_render_ui_layout_overlay_can_select_snapshot_index():
    raw = _multi_snapshot_report()

    svg = render_ui_layout_overlay(raw, snapshot_index=1)

    assert svg is not None
    assert "second_state_action" in svg
    assert "first_state_action" not in svg


def test_format_ui_human_load_report_markdown_and_json():
    raw = json.loads((ROOT / "docs" / "analysis" / "mahlah-ui-sim-report.json").read_text(encoding="utf-8"))
    report = analyze_ui_simulation_report(raw)

    markdown = format_ui_human_load_report(report)
    assert "UI Human-Load Evidence" in markdown
    assert "context switching" in markdown

    payload = format_ui_human_load_report(report, output_format="json")
    assert isinstance(payload, dict)
    assert payload["suggested_blocks"]["HUMAN_LOAD"]


def test_format_cairn_annotation_snippet():
    raw = json.loads((ROOT / "docs" / "analysis" / "mahlah-ui-sim-report.json").read_text(encoding="utf-8"))
    report = analyze_ui_simulation_report(raw)

    snippet = format_cairn_annotation_snippet(report, step_title="Review Mahlah UI human load")
    assert snippet.startswith("## Review Mahlah UI human load")
    assert "HUMAN_DEMAND:" in snippet
    assert "HUMAN_RISK:" in snippet
    assert "context_switches: 3" in snippet
    assert "Treat this as design evidence" in snippet


def test_ui_evidence_cli_writes_markdown(tmp_path):
    source = ROOT / "docs" / "analysis" / "mahlah-ui-sim-report.json"
    output = tmp_path / "ui-evidence.md"
    rc = ui_evidence_main([str(source), "-o", str(output)])

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    assert "Suggested Cairn Blocks" in text
    assert "HUMAN_RISK" in text


def test_ui_evidence_cli_writes_layout_svg(tmp_path):
    source = ROOT / "docs" / "analysis" / "customer-po-review-ui-sim-report.json"
    output = tmp_path / "ui-evidence.md"
    svg = tmp_path / "layout-overlay.svg"
    rc = ui_evidence_main([str(source), "-o", str(output), "--layout-svg-output", str(svg)])

    assert rc == 0
    assert svg.read_text(encoding="utf-8").startswith("<svg")


def test_ui_evidence_cli_writes_selected_layout_snapshot(tmp_path):
    source = tmp_path / "multi-snapshot-report.json"
    output = tmp_path / "ui-evidence.md"
    svg = tmp_path / "layout-overlay.svg"
    source.write_text(json.dumps(_multi_snapshot_report()), encoding="utf-8")

    rc = ui_evidence_main(
        [
            str(source),
            "-o",
            str(output),
            "--layout-svg-output",
            str(svg),
            "--layout-snapshot-index",
            "1",
        ]
    )

    assert rc == 0
    text = svg.read_text(encoding="utf-8")
    assert "second_state_action" in text
    assert "first_state_action" not in text


def test_ui_annotations_cli_writes_cairn_snippet(tmp_path):
    source = ROOT / "docs" / "analysis" / "mahlah-ui-sim-report.json"
    output = tmp_path / "ui-annotations.cairn.md"
    rc = ui_annotations_main([str(source), "--step-title", "Review generated UI evidence", "-o", str(output)])

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    assert "## Review generated UI evidence" in text
    assert "HUMAN_LOAD:" in text
    assert "context_switches: 3" in text


class FakeRoleplayProvider:
    name = "fake-roleplay"

    def complete(self, request: LLMRequest) -> LLMResponse:
        assert request.task == "cairn.ui_experience.roleplay"
        assert "ui_evidence" in request.context
        assert "novice" in request.prompt
        return LLMResponse(
            text="## Role-play snapshots\n\nThe novice user loses context at the dev log.",
            provider=self.name,
        )


def test_interpret_ui_experience_uses_provider():
    raw = json.loads((ROOT / "docs" / "analysis" / "mahlah-ui-sim-report.json").read_text(encoding="utf-8"))
    evidence = analyze_ui_simulation_report(raw)
    prompt = build_ui_roleplay_prompt(raw, evidence, personas=["novice reviewer"])
    assert "not a real user study" in prompt
    assert "novice reviewer" in prompt

    interpretation = interpret_ui_experience(raw, FakeRoleplayProvider(), evidence=evidence)
    assert interpretation.provider == "fake-roleplay"
    assert "novice user" in interpretation.personas[0]
    assert "dev log" in interpretation.text


def test_ui_roleplay_cli_command_provider(tmp_path):
    script = tmp_path / "fake_roleplay.py"
    script.write_text(
        "import json, sys\n"
        "payload = json.load(sys.stdin)\n"
        "assert payload['task'] == 'cairn.ui_experience.roleplay'\n"
        "assert 'ui_evidence' in payload['context']\n"
        "print(json.dumps({'text': 'Roleplay OK: ' + payload['context']['ui_evidence']['scenario']}))\n",
        encoding="utf-8",
    )
    source = ROOT / "docs" / "analysis" / "mahlah-ui-sim-report.json"
    output = tmp_path / "roleplay.md"
    rc = ui_roleplay_main([str(source), "--llm-command", f"{sys.executable} {script}", "-o", str(output)])

    assert rc == 0
    assert output.read_text(encoding="utf-8") == "Roleplay OK: mahlah-human-load"


def _multi_snapshot_report() -> dict:
    return {
        "scenario": "multi-layout-flow",
        "metrics": {"clicks": 0, "fills": 0, "waits": 0, "contextSwitches": 0, "layoutSnapshots": 2},
        "observations": [],
        "layoutLoad": [
            {
                "viewport": {"width": 800, "height": 600},
                "elements": [
                    {"id": "first_state_field", "role": "field", "x": 40, "y": 80, "width": 200, "height": 36},
                    {"id": "first_state_action", "role": "button", "x": 320, "y": 80, "width": 120, "height": 40},
                ],
                "sequence": ["first_state_field", "first_state_action"],
            },
            {
                "viewport": {"width": 800, "height": 600},
                "elements": [
                    {"id": "second_state_warning", "role": "warning", "x": 60, "y": 220, "width": 220, "height": 56},
                    {"id": "second_state_action", "role": "button", "x": 460, "y": 420, "width": 140, "height": 44},
                ],
                "relations": [
                    {"from": "second_state_warning", "to": "second_state_action", "type": "evidence_to_action"}
                ],
                "sequence": ["second_state_warning", "second_state_action"],
            },
        ],
    }
