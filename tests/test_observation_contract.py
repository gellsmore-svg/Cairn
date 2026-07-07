from __future__ import annotations

from cairn.galeed_adapter import galeed_event_to_observation
from cairn.observation_contract import observation_event, observation_to_galeed_trace_event


def test_observation_event_normalizes_producer_payload():
    event = observation_event(
        ts="2026-07-07T21:15:00Z",
        source="mahlah-ui",
        kind="ui_event",
        severity="warning",
        message="User opened trace after unclear answer.",
        tags=["context_switch", "context_switch", "missing_evidence"],
        human_systems=["audit reasoning", "trust calibration", "trust calibration"],
        duration_ms=700,
        correlation={"trace_id": "trace_1", "ignored": "nope"},
    )

    assert event["tags"] == ["context_switch", "missing_evidence"]
    assert event["human_systems"] == ["audit reasoning", "trust calibration"]
    assert event["correlation"] == {"trace_id": "trace_1"}


def test_observation_can_round_trip_through_galeed_trace_event():
    observation = observation_event(
        ts="2026-07-07T21:15:00Z",
        source="tirzah-agent",
        kind="agent_output",
        severity="info",
        message="Generated approval recommendation without cited authority.",
        tags=["missing_evidence"],
        human_systems=["trust calibration", "uncertainty management"],
        duration_ms=4200,
        correlation={"trace_id": "trace_1", "request_id": "req_1"},
    )

    galeed_event = observation_to_galeed_trace_event(observation, event_id="evt_1", seq=1)
    converted = galeed_event_to_observation(galeed_event)

    assert galeed_event["type"] == "llm.call.completed"
    assert galeed_event["metadata"]["cairn_kind"] == "agent_output"
    assert galeed_event["trace_id"] == "trace_1"
    assert converted["kind"] == "agent_output"
    assert "missing_evidence" in converted["tags"]
    assert converted["duration_ms"] == 4200


def test_observation_round_trip_preserves_non_special_tags():
    observation = observation_event(
        ts="2026-07-07T21:16:00Z",
        source="mahlah-ui",
        kind="ui_event",
        severity="warning",
        message="User left answer view to reconstruct missing process context.",
        tags=["context_switch", "repair_turn", "waiting"],
        human_systems=["audit reasoning", "vigilance"],
        duration_ms=900,
        correlation={"session_id": "sess_1", "trace_id": "trace_1"},
    )

    galeed_event = observation_to_galeed_trace_event(observation)
    converted = galeed_event_to_observation(galeed_event)

    assert "context_switch" in converted["tags"]
    assert "repair_turn" in converted["tags"]
    assert "waiting" in converted["tags"]
    assert "audit reasoning" in converted["human_systems"]
    assert "vigilance" in converted["human_systems"]
