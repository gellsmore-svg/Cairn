from __future__ import annotations

import json

from cairn.layout_load import analyze_functional_layout, format_functional_layout_report, render_layout_svg
from cairn.layout_load_cli import main as layout_load_main


def _po_layout() -> dict:
    return {
        "viewport": {"width": 1440, "height": 900},
        "elements": [
            {"id": "po_label", "role": "label", "x": 40, "y": 120, "width": 80, "height": 24},
            {"id": "po_number", "role": "field", "x": 280, "y": 116, "width": 220, "height": 36},
            {"id": "customer", "role": "field", "x": 40, "y": 220, "width": 260, "height": 36},
            {"id": "duplicate_warning", "role": "warning", "x": 980, "y": 620, "width": 260, "height": 48},
            {"id": "evidence_panel", "role": "evidence", "x": 40, "y": 520, "width": 420, "height": 260},
            {"id": "accept", "role": "button", "x": 1120, "y": 140, "width": 120, "height": 44},
        ],
        "relations": [
            {"from": "po_label", "to": "po_number", "type": "label_for"},
            {"from": "po_number", "to": "duplicate_warning", "type": "related"},
            {"from": "customer", "to": "duplicate_warning", "type": "related"},
            {"from": "evidence_panel", "to": "accept", "type": "evidence_to_action"},
        ],
        "sequence": ["po_number", "customer", "duplicate_warning", "evidence_panel", "accept"],
    }


def test_analyze_functional_layout_flags_spatial_load():
    report = analyze_functional_layout(_po_layout())

    assert report.metrics["layout_load"] == "high"
    assert report.metrics["column_count"] >= 3
    factors = {(finding.family, finding.factor) for finding in report.findings}
    assert ("functional_layout_load", "related element distance") in factors
    assert ("functional_layout_load", "label-field distance") in factors
    assert ("functional_layout_load", "column complexity") in factors
    assert "FUNCTIONAL_LAYOUT_LOAD" in report.suggested_blocks


def test_format_functional_layout_report_markdown_and_json():
    report = analyze_functional_layout(_po_layout())

    markdown = format_functional_layout_report(report)
    assert "Functional Layout Load" in markdown
    assert "related element distance" in markdown

    payload = format_functional_layout_report(report, output_format="json")
    assert isinstance(payload, dict)
    assert payload["metrics"]["layout_load"] == "high"


def test_render_layout_svg_draws_elements_and_relations():
    svg = render_layout_svg(_po_layout())

    assert svg.startswith("<svg")
    assert "po_number" in svg
    assert "evidence_to_action" in svg
    assert "<polyline" in svg


def test_layout_load_cli_writes_report(tmp_path):
    source = tmp_path / "layout.json"
    output = tmp_path / "layout.md"
    source.write_text(json.dumps(_po_layout()), encoding="utf-8")

    rc = layout_load_main([str(source), "-o", str(output)])

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    assert "FUNCTIONAL_LAYOUT_LOAD" in text
    assert "cumulative_pointer_travel" in text


def test_layout_load_cli_writes_svg_overlay(tmp_path):
    source = tmp_path / "layout.json"
    output = tmp_path / "layout.md"
    svg = tmp_path / "layout.svg"
    source.write_text(json.dumps(_po_layout()), encoding="utf-8")

    rc = layout_load_main([str(source), "-o", str(output), "--svg-output", str(svg)])

    assert rc == 0
    assert svg.read_text(encoding="utf-8").startswith("<svg")


def test_layout_load_cli_reports_invalid_json(tmp_path, capsys):
    source = tmp_path / "layout.json"
    source.write_text("{not json", encoding="utf-8")

    rc = layout_load_main([str(source)])

    assert rc == 2
    captured = capsys.readouterr()
    assert "cairn-layout-load:" in captured.err
