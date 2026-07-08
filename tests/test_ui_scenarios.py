from __future__ import annotations

import json
from pathlib import Path

from cairn.ui_scenario_validate_cli import main as scenario_validate_main
from cairn.ui_scenarios import (
    format_scenario_validation_report,
    load_ui_scenario,
    validate_ui_scenario,
)
from cairn.ui_sim_cli import main as ui_sim_main


ROOT = Path(__file__).resolve().parents[1]


def test_validate_example_scenarios():
    for path in [
        ROOT / "docs" / "scenarios" / "mahlah-human-load.json",
        ROOT / "docs" / "scenarios" / "mahlah-missing-information.json",
        ROOT / "docs" / "scenarios" / "mahlah-recovery-loop.json",
    ]:
        report = validate_ui_scenario(load_ui_scenario(path), path=str(path))

        assert report.ok
        assert report.errors == []
        assert "ok" in format_scenario_validation_report(report)


def test_validate_ui_scenario_reports_action_errors():
    scenario = {
        "name": "broken",
        "steps": [
            {"action": "click"},
            {
                "action": "waitForMagic",
                "humanLoad": {"phase": "execution", "systems": ["attention"], "demand": ""},
            },
        ],
    }

    report = validate_ui_scenario(scenario)

    assert not report.ok
    assert any("steps[0].selector" in error for error in report.errors)
    assert any("unknown action" in error for error in report.errors)
    assert any("humanLoad.demand" in error for error in report.errors)


def test_validate_ui_scenario_accepts_hci_touchpoint_phases():
    scenario = {
        "name": "hci-touchpoints",
        "steps": [
            {
                "action": "assertVisible",
                "selector": "#po-queue",
                "humanLoad": {
                    "phase": "orientation",
                    "systems": ["attention", "working memory"],
                    "demand": "The user understands queue state, priority, and risk before choosing a PO.",
                },
            },
            {
                "action": "assertVisible",
                "selector": "#po-status",
                "humanLoad": {
                    "phase": "handoff",
                    "systems": ["audit reasoning"],
                    "demand": "The user verifies that the completed PO state is visible downstream.",
                },
            },
        ],
    }

    report = validate_ui_scenario(scenario)

    assert report.ok
    assert report.errors == []
    assert not any("not one of" in warning for warning in report.warnings)


def test_scenario_validate_cli_returns_nonzero_for_invalid(tmp_path, capsys):
    scenario = tmp_path / "invalid.json"
    scenario.write_text(json.dumps({"steps": [{"action": "fill", "selector": ".x"}]}), encoding="utf-8")

    rc = scenario_validate_main([str(scenario)])
    captured = capsys.readouterr()

    assert rc == 1
    assert "invalid" in captured.out
    assert "steps[0].value" in captured.out


def test_ui_sim_cli_validates_before_playwright(tmp_path, capsys):
    scenario = tmp_path / "invalid.json"
    scenario.write_text(json.dumps({"steps": [{"action": "click"}]}), encoding="utf-8")

    rc = ui_sim_main([str(scenario), "--project-root", str(tmp_path)])
    captured = capsys.readouterr()

    assert rc == 2
    assert "steps[0].selector" in captured.err
