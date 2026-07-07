# Galeed Emitter Contract for Cairn Observation

Products should emit a small observation event whenever a user, agent, queue, or
runtime step changes the human experience of the process. Galeed can store the
event as a durable trace record; Cairn can then convert it into live-observation
evidence.

## Cairn Observation Event

```json
{
  "ts": "2026-07-07T21:15:00Z",
  "source": "mahlah-ui",
  "kind": "ui_event",
  "severity": "warning",
  "message": "User opened trace after unclear answer.",
  "tags": ["context_switch", "missing_evidence"],
  "human_systems": ["audit reasoning", "trust calibration"],
  "duration_ms": 700,
  "correlation": {
    "trace_id": "trace_1",
    "request_id": "req_1"
  }
}
```

Required fields:

- `source`: product or subsystem emitting the event.
- `kind`: one of `ui_event`, `system_log`, `agent_step`, `agent_output`,
  `agent_output_review`, `queue_event`, `feedback`, or `recovery_event`.
- `message`: a short factual summary of what was observed.

Recommended fields:

- `ts`: ISO timestamp. Cairn can generate one if omitted.
- `severity`: `debug`, `info`, `warning`, `error`, or `critical`.
- `tags`: process and risk cues such as `missing_context`, `missing_evidence`,
  `context_switch`, `waiting`, `retry`, `repair_turn`, or `escalation`.
- `human_systems`: human load cues such as `trust calibration`,
  `uncertainty management`, `accountability`, `recall`, `language`, or
  `audit reasoning`.
- `duration_ms`: visible wait, tool latency, queue delay, or step duration.
- `correlation`: shared ids such as `request_id`, `session_id`, `trace_id`,
  `plan_id`, and `job_id`.

## Galeed Trace Shape

When storing the event in Galeed, preserve correlation ids at the top level and
carry Cairn-specific cues in metadata:

```json
{
  "event_id": "evt_1",
  "schema_version": "1.0",
  "seq": 1,
  "timestamp": "2026-07-07T21:15:00Z",
  "source": "tirzah-agent",
  "type": "llm.call.completed",
  "status": "ok",
  "severity": "info",
  "summary": "Generated approval recommendation without cited authority.",
  "trace_id": "trace_1",
  "request_id": "req_1",
  "metadata": {
    "cairn_kind": "agent_output",
    "tags": ["missing_evidence"],
    "human_systems": ["trust calibration", "uncertainty management"],
    "duration_ms": 4200
  }
}
```

The helper `observation_to_galeed_trace_event` maps Cairn observation kinds to
Galeed event types, while `cairn-galeed-observe` maps Galeed exports back into
Cairn evidence reports.
