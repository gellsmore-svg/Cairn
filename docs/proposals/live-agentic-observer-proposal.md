# Live Agentic Observer Proposal

## Purpose

A Cairn live observer is an agentic monitoring layer that watches a running product and records what the whole system is asking of humans, agents, queues, logs, interfaces, and operating processes.

The goal is not only uptime monitoring. The observer asks:

- Is the product reliable and stable?
- Are agentic steps effective, grounded, and recoverable?
- What cognitive or organisational load is being shifted onto users?
- Are humans being asked to trust, approve, repair, or escalate without enough evidence?
- Which repeated issues should become product or process improvements?

This proposal is a natural fit for Noah: a wrapper or orchestrating repo that runs multiple products can host one or more observer agents as a full-time operational role.

## Observation Sources

A live observer can consume:

- UI probes, including Playwright scenarios and screenshots.
- Product logs, for example a Khalid-style message/log stream when available.
- Agent traces, including prompts, tool calls, retrieval, queue events, retries, and outputs.
- Human feedback surfaces, such as thumbs, notes, corrections, escalations, and abandoned tasks.
- Runtime signals, such as latency, errors, restarts, queue depth, and timeouts.
- Output-review events, where another agent marks whether an answer was grounded, useful, overconfident, or missing authority.

## Event Shape

The portable event shape is intentionally small:

```json
{
  "ts": "2026-07-07T20:30:01Z",
  "source": "mahlah-ui",
  "kind": "ui_event",
  "severity": "info",
  "message": "User opened process trace to inspect what happened.",
  "tags": ["context_switch"],
  "human_systems": ["attention switching", "audit reasoning"],
  "duration_ms": 700
}
```

Suggested `kind` values:

- `ui_event`
- `system_log`
- `agent_step`
- `agent_output`
- `agent_output_review`
- `queue_event`
- `feedback`
- `recovery_event`

Suggested tags:

- `error`
- `missing_context`
- `missing_evidence`
- `unsupported_output`
- `overconfident_output`
- `context_switch`
- `waiting`
- `repair_turn`
- `timeout`
- `retry`
- `escalation`

## Cairn Command

`cairn-live-observe` reads JSON or JSONL observation events and produces a Cairn-style evidence report:

```bash
cairn-live-observe docs/observations/noah-live-observer-sample.jsonl \
  --title "Noah live observer sample" \
  --output docs/analysis/noah-live-observer-sample.md
```

The report includes:

- observation counts by source and kind,
- system reliability findings,
- human-load findings,
- agent-effectiveness findings,
- qualitative risk,
- suggested Cairn blocks for review.

## Observer Roles

A mature Noah deployment could run several observers:

- Product observer: watches UI, latency, errors, and visible task completion.
- Human-load observer: watches context switching, uncertainty, recovery loops, feedback burden, and closure clarity.
- Agent-effectiveness observer: reviews LLM outputs for grounding, usefulness, authority boundaries, and unsupported fluency.
- Queue/process observer: watches Hoglah or similar queue health, retries, stuck jobs, and backlog pressure.
- Change-learning observer: clusters repeated findings into product/process improvement proposals.

These should be separate roles, not because they require different code, but because they ask different questions.

## Guardrails

The observer should not become surveillance of individual people.

It should:

- score process and interface conditions, not people,
- aggregate or anonymise where possible,
- distinguish observed evidence from inference,
- make uncertainty explicit,
- produce reviewable Cairn annotations rather than automatic blame,
- help humans recover and improve the system.

## Proposed Stack

```text
Live product
  -> logs / UI probes / agent traces / feedback
  -> observation JSONL
  -> cairn-live-observe
  -> Cairn evidence report
  -> optional role-play or output-review agents
  -> issues, annotations, or process improvements
```

This makes Cairn the shared language between runtime monitoring, human experience, and agentic-system quality.
