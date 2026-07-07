"""Convert Galeed trace data into Cairn live-observation events."""

from __future__ import annotations

from typing import Any


def galeed_event_to_observation(event: dict[str, Any]) -> dict[str, Any]:
    """Convert one Galeed trace event dict into a Cairn observation event."""
    metadata = dict(event.get("metadata") or {})
    event_type = str(event.get("type") or "unknown")
    tags = _tags_for_event(event_type, event, metadata)
    observation = {
        "ts": event.get("timestamp"),
        "source": event.get("source") or "galeed",
        "kind": _kind_for_event(event_type),
        "severity": event.get("severity") or _severity_from_status(event.get("status")),
        "message": event.get("summary") or event_type,
        "tags": tags,
        "human_systems": _human_systems_for_event(event_type, tags, metadata),
        "duration_ms": _duration_ms(metadata),
        "correlation": _correlation(event, metadata),
        "galeed": {
            "event_id": event.get("event_id"),
            "type": event_type,
            "status": event.get("status"),
            "seq": event.get("seq"),
            "schema_version": event.get("schema_version"),
        },
    }
    return _drop_empty(observation)


def galeed_llm_call_to_observation(call: dict[str, Any]) -> dict[str, Any]:
    """Convert one Galeed llm_calls document into a Cairn observation event."""
    status = str(call.get("status") or ("failed" if call.get("error") else "completed"))
    tags = ["llm_call"]
    if status == "failed" or call.get("error"):
        tags.append("error")
    if call.get("output") and not _has_grounding_marker(call):
        tags.append("missing_evidence")
    observation = {
        "ts": call.get("completed_at") or call.get("started_at"),
        "source": call.get("source") or "galeed-llm",
        "kind": "agent_output" if status == "completed" else "system_log",
        "severity": "error" if status == "failed" or call.get("error") else "info",
        "message": _llm_call_message(call),
        "tags": tags,
        "human_systems": ["trust calibration"] if "missing_evidence" in tags else [],
        "duration_ms": call.get("duration_ms") or 0,
        "correlation": _correlation(call, dict(call.get("metadata") or {})),
        "galeed": {
            "call_id": call.get("call_id"),
            "step_name": call.get("step_name"),
            "parent_call_id": call.get("parent_call_id"),
            "model": call.get("model"),
            "status": status,
        },
    }
    return _drop_empty(observation)


def galeed_records_to_observations(
    records: list[dict[str, Any]],
    *,
    record_type: str = "trace_event",
) -> list[dict[str, Any]]:
    """Convert Galeed trace events or LLM call docs into Cairn observations."""
    if record_type == "llm_call":
        return [galeed_llm_call_to_observation(record) for record in records]
    return [galeed_event_to_observation(record) for record in records]


def _kind_for_event(event_type: str) -> str:
    if event_type.startswith("message.") or event_type.startswith("feedback."):
        return "feedback" if event_type.startswith("feedback.") else "ui_event"
    if event_type.startswith("job."):
        return "queue_event"
    if event_type.startswith("llm.call."):
        return "agent_output"
    if event_type.startswith(("model.", "retrieval.", "context.", "specialist.", "research.", "process.")):
        return "agent_step"
    if event_type.startswith("answer."):
        return "agent_output"
    return "system_log"


def _tags_for_event(event_type: str, event: dict[str, Any], metadata: dict[str, Any]) -> list[str]:
    tags = [event_type.replace(".", "_")]
    status = str(event.get("status") or "").lower()
    severity = str(event.get("severity") or "").lower()
    if status in {"failed", "error"} or severity == "error" or event_type.endswith(".failed"):
        tags.append("error")
    if event_type.startswith("job.") and event_type not in {"job.completed", "job.cancelled"}:
        tags.append("waiting")
    if event_type in {"retrieval.mongo.failed", "context.sufficiency"} and metadata.get("sufficient") is False:
        tags.append("missing_context")
    if event_type == "llm.call.failed":
        tags.append("unsupported_output")
    if metadata.get("missing_evidence") or metadata.get("provenance") is False:
        tags.append("missing_evidence")
    return sorted(set(tags))


def _human_systems_for_event(event_type: str, tags: list[str], metadata: dict[str, Any]) -> list[str]:
    systems: set[str] = set()
    if "waiting" in tags:
        systems.add("vigilance")
    if "missing_context" in tags or "missing_evidence" in tags:
        systems.add("uncertainty management")
        systems.add("trust calibration")
    if event_type.startswith("feedback."):
        systems.add("language")
        systems.add("recall")
    for item in metadata.get("human_systems", []):
        systems.add(str(item))
    return sorted(systems)


def _duration_ms(metadata: dict[str, Any]) -> int:
    for key in ("duration_ms", "elapsed_ms", "latency_ms"):
        try:
            return int(metadata.get(key) or 0)
        except (TypeError, ValueError):
            continue
    return 0


def _severity_from_status(status: Any) -> str:
    return "error" if str(status or "").lower() == "failed" else "info"


def _correlation(data: dict[str, Any], metadata: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key in ("request_id", "session_id", "trace_id", "plan_id", "job_id"):
        value = data.get(key) if data.get(key) is not None else metadata.get(key)
        if value:
            out[key] = str(value)
    return out


def _llm_call_message(call: dict[str, Any]) -> str:
    step = call.get("step_name") or call.get("model") or "LLM call"
    if call.get("error"):
        return f"{step} failed: {str(call['error'])[:160]}"
    return f"{step} completed with {len(call.get('output') or '')} output chars"


def _has_grounding_marker(call: dict[str, Any]) -> bool:
    metadata = dict(call.get("metadata") or {})
    if metadata.get("grounded") is True or metadata.get("provenance") is True:
        return True
    text = str(call.get("output") or "").lower()
    return any(marker in text for marker in ("source:", "sources:", "citation", "evidence:"))


def _drop_empty(data: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in data.items() if value not in (None, {}, [])}
