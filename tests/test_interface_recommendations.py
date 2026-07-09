from __future__ import annotations

import json

import cairn
from cairn.interface_recommendations import future_state_svg, recommend_interface_changes
from cairn.interface_recommendations_cli import main as recommend_main


def _layout() -> dict:
    return {
        "label": "PO review",
        "viewport": {"width": 1440, "height": 900},
        "elements": [
            {"id": "po_label", "role": "label", "x": 40, "y": 120, "width": 80, "height": 24},
            {"id": "po_number", "role": "field", "x": 300, "y": 116, "width": 220, "height": 36},
            {"id": "ai_recommendation", "role": "evidence", "x": 40, "y": 520, "width": 420, "height": 220},
            {"id": "accept", "role": "button", "x": 1120, "y": 140, "width": 120, "height": 44},
        ],
        "relations": [
            {"from": "po_label", "to": "po_number", "type": "label_for"},
            {"from": "ai_recommendation", "to": "accept", "type": "evidence_to_action"},
        ],
        "sequence": ["po_number", "ai_recommendation", "accept"],
    }


def test_recommend_interface_changes_requires_okf_traceability():
    report = recommend_interface_changes(_layout())

    assert report.recommendations
    for item in report.recommendations:
        assert item.traceability
        assert all(trace.okf_file.startswith("okf/concepts/") for trace in item.traceability)
    assert "future" in future_state_svg(report).lower()
    assert cairn.recommend_interface_changes is recommend_interface_changes


def test_recommend_interface_changes_cli_writes_json_and_svg(tmp_path):
    source = tmp_path / "layout.json"
    output = tmp_path / "recommendations.json"
    svg = tmp_path / "future.svg"
    source.write_text(json.dumps(_layout()), encoding="utf-8")

    rc = recommend_main([str(source), "-f", "json", "-o", str(output), "--future-svg-output", str(svg)])

    assert rc == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["recommendations"]
    assert payload["recommendations"][0]["traceability"]
    assert svg.read_text(encoding="utf-8").startswith("<svg")
