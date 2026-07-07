"""Portable producer contract for Cairn live-observation events."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


OBSERVATION_KINDS = {
    "ui_event",
    "system_log",
    "agent_step",
    "agent_output",
    "agent_output_review",
    "queue_event",
    "feedback",
    "recovery_event",
}

OBSERVATION_SEVERITIES = {"debug", "info", "warning", "error", "critical"}

CORRELATION_KEYS = ("request_id", "session_id", "trace_id", "plan_id", "job_id")


def observation_event(
    *,
    source: str,
    kind: str,
    message: str,
    ts: str | None = None,
    severity: str = "info",
    tags: list[str] | None = None,
    human_systems: list[str] | None = None,
    duration_ms: int | None = None,
    correlation: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a normalized Cairn observation event for product emitters."""
    if kind not in OBSERVATION_KINDS:
        raise ValueError(f"Unsupported observation kind: {kind}")
    if severity not in OBSERVATION_SEVERITIES:
        raise ValueError(f"Unsupported observation severity: {severity}")

    event = {
        "ts": ts or _utc_now(),
        "source": source,
        "kind": kind,
        "severity": severity,
        "message": message,
        "tags": _unique(tags or []),
        "human_systems": _unique(human_systems or []),
        "duration_ms": int(duration_ms or 0),
        "correlation": _normalize_correlation(correlation or {}),
        "metadata": dict(metadata or {}),
    }
    return _drop_empty(event)


def observation_to_galeed_trace_event(
    observation: dict[str, Any],
    *,
    event_id: str | None = None,
    seq: int | None = None,
    schema_version: str = "1.0",
) -> dict[str, Any]:
    """Convert a Cairn observation event into a Galeed-compatible trace event."""
    normalized = observation_event(
        ts=observation.get("ts"),
        source=str(observation.get("source") or "cairn-observer"),
        kind=str(observation.get("kind") or "system_log"),
        severity=str(observation.get("severity") or "info"),
        message=str(observation.get("message") or "Observation event"),
        tags=[str(tag) for tag in observation.get("tags", [])],
        human_systems=[str(item) for item in observation.get("human_systems", [])],
        duration_ms=int(observation.get("duration_ms") or 0),
        correlation=dict(observation.get("correlation") or {}),
        metadata=dict(observation.get("metadata") or {}),
    )
    metadata = dict(normalized.get("metadata") or {})
    metadata.update(
        {
            "cairn_kind": normalized["kind"],
            "tags": normalized.get("tags", []),
            "human_systems": normalized.get("human_systems", []),
            "duration_ms": normalized.get("duration_ms", 0),
        }
    )
    if "missing_evidence" in normalized.get("tags", []):
        metadata["missing_evidence"] = True
    if "missing_context" in normalized.get("tags", []):
        metadata["sufficient"] = False
    metadata = _drop_empty(metadata)

    trace_event = {
        "event_id": event_id,
        "schema_version": schema_version,
        "seq": seq,
        "timestamp": normalized["ts"],
        "source": normalized["source"],
        "type": _galeed_type_for_observation(normalized),
        "status": _status_for_severity(normalized["severity"]),
        "severity": normalized["severity"],
        "summary": normalized["message"],
        "metadata": metadata,
    }
    trace_event.update(normalized.get("correlation", {}))
    return _drop_empty(trace_event)


def _galeed_type_for_observation(observation: dict[str, Any]) -> str:
    kind = observation["kind"]
    if kind == "ui_event":
        return "message.user.observed"
    if kind == "feedback":
        return "feedback.submitted"
    if kind == "queue_event":
        return "job.observed"
    if kind == "agent_step":
        return "process.step.observed"
    if kind == "agent_output":
        return "llm.call.completed"
    if kind == "agent_output_review":
        return "answer.reviewed"
    if kind == "recovery_event":
        return "process.recovery.observed"
    return "system.log.observed"


def _status_for_severity(severity: str) -> str:
    if severity in {"error", "critical"}:
        return "failed"
    if severity == "warning":
        return "warning"
    return "ok"


def _normalize_correlation(correlation: dict[str, Any]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key in CORRELATION_KEYS:
        value = correlation.get(key)
        if value:
            normalized[key] = str(value)
    return normalized


def _unique(items: list[str]) -> list[str]:
    return sorted({str(item) for item in items if str(item).strip()})


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _drop_empty(data: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in data.items() if value not in (None, {}, [])}
