# Live Agentic Observer Proposal

## Purpose

A Cairn live observer is an agentic monitoring layer that watches a running product and records what the whole system is asking of humans, agents, queues, logs, interfaces, and operating processes.

The goal is not only uptime monitoring. The observer asks:

- Is the product reliable and stable?
- Are agentic steps effective, grounded, and recoverable?
- What cognitive or organisational load is being shifted onto users?
- Are humans being asked to trust, approve, repair, or escalate without enough evidence?
- Which repeated issues should become product or process improvements?

This proposal is a natural fit for Noa as the runtime host: Noa already orchestrates the sibling products, while the observer capability itself should remain portable enough to run outside Noa when a single product or deployment needs it.

## Observation Sources

A live observer can consume:

- UI probes, including Playwright scenarios and screenshots.
- Product logs, especially Galeed's structured cross-project trace/log spine.
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

Before wiring observers, discover likely observation surfaces:

```bash
cairn-system-discover ../Noa --output docs/analysis/noa-system-discovery.md
```

For a sibling checkout layout, run discovery at the parent directory as well:

```bash
cairn-system-discover ~/domains --output docs/analysis/family-system-discovery.md
```

The discovery step is intentionally lightweight. It looks for runtime-host
signals, Galeed trace/log surfaces, Playwright-capable UIs, Hoglah-style queues,
and Cairn scenario/spec assets, then proposes an observation plan.

`cairn-live-observe` reads JSON or JSONL observation events and produces a Cairn-style evidence report:

```bash
cairn-live-observe docs/observations/noa-live-observer-sample.jsonl \
  --title "Noa live observer sample" \
  --output docs/analysis/noa-live-observer-sample.md
```

The report includes:

- observation counts by source and kind,
- system reliability findings,
- human-load findings,
- agent-effectiveness findings,
- qualitative risk,
- suggested Cairn blocks for review.

## Observer Roles

A mature Noa deployment could run several observers:

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
  -> Galeed logs / UI probes / agent traces / feedback
  -> observation JSONL
  -> cairn-live-observe
  -> Cairn evidence report
  -> optional role-play or output-review agents
  -> issues, annotations, or process improvements
```

This makes Cairn the shared language between runtime monitoring, human experience, and agentic-system quality.

## Placement Decision

The observer should be a **portable observer framework** with Noa as the natural
deployment host, rather than a Noa-only feature.

Rationale:

- Noa's contract is orchestration, configuration, health, and runtime cohesion;
  it should not vendor the observer's core analysis logic.
- Cairn is the better home for the evidence vocabulary, human/system analysis,
  and annotation output.
- Galeed is the better home for durable cross-project telemetry and correlation
  identifiers.
- Product repos such as Mahlah or Tirzah should emit local events and expose UI
  surfaces, but should not each reinvent holistic observation.
- A future named observer sibling could own long-running agents, scheduling,
  clustering, issue creation, and policy, while reusing Cairn and Galeed.

In short:

```text
Cairn = observation language and analysis
Galeed = trace/log spine
Noa = runtime host and stack wiring
Products = event emitters and UI targets
Observer agent = optional long-running worker over the stack
```

This keeps the system composable. Noa can run it for the whole local stack, but a
single product can still use the same observer tools during development or CI.

## Non-Deterministic Systems

Many of the family tools are stochastic or agentic: the same input can lead to
different retrieval paths, model outputs, timings, or repair loops. The observer
therefore should not expect one canonical execution trace.

Instead it should:

- observe distributions and repeated patterns,
- preserve correlation ids across traces, jobs, sessions, and plans,
- compare visible output against evidence sufficiency,
- detect repair loops and missing authority,
- treat differences between runs as signal rather than noise,
- ask whether variance changes human load, trust, or recoverability.

This is where Cairn adds value: it gives stochastic runtime behaviour a
reviewable process language.
