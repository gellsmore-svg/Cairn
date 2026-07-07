from __future__ import annotations

import json
from pathlib import Path

from cairn.galeed_adapter import galeed_event_to_observation, galeed_llm_call_to_observation
from cairn.galeed_observe_cli import main as galeed_observe_main
from cairn.live_observer_cli import _load_observations


ROOT = Path(__file__).resolve().parents[1]


def test_galeed_trace_event_maps_to_live_observation():
    event = {
        "trace_id": "trace_1",
        "session_id": "sess_1",
        "request_id": "req_1",
        "type": "llm.call.completed",
        "status": "completed",
        "severity": "info",
        "source": "hoglah",
        "summary": "answer -> 12 chars",
        "timestamp": "2026-07-07T20:40:00Z",
        "metadata": {"duration_ms": 5000, "provenance": False},
    }

    observation = galeed_event_to_observation(event)

    assert observation["kind"] == "agent_output"
    assert observation["duration_ms"] == 5000
    assert "missing_evidence" in observation["tags"]
    assert observation["correlation"]["trace_id"] == "trace_1"
    assert "trust calibration" in observation["human_systems"]


def test_galeed_llm_call_maps_to_observation():
    call = {
        "trace_id": "trace_1",
        "session_id": "sess_1",
        "source": "tirzah",
        "call_id": "call_1",
        "step_name": "answer",
        "status": "completed",
        "output": "Fluent answer without sources",
        "duration_ms": 3001,
    }

    observation = galeed_llm_call_to_observation(call)

    assert observation["kind"] == "agent_output"
    assert "missing_evidence" in observation["tags"]
    assert observation["duration_ms"] == 3001


def test_galeed_observe_cli_writes_report_and_observations(tmp_path):
    source = ROOT / "docs" / "galeed" / "sample-trace-events.jsonl"
    report = tmp_path / "report.md"
    observations = tmp_path / "observations.jsonl"

    rc = galeed_observe_main(
        [
            str(source),
            "--title",
            "Galeed bridge test",
            "--observations-output",
            str(observations),
            "-o",
            str(report),
        ]
    )

    assert rc == 0
    assert "Galeed bridge test" in report.read_text(encoding="utf-8")
    converted = _load_observations(observations.read_text(encoding="utf-8"))
    assert len(converted) == 5
    assert any("missing_evidence" in item.get("tags", []) for item in converted)
