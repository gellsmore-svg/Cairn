# Human-Factors Methodology

Cairn's human-factors layer makes the human cost of a process visible. It is for
design review, operational learning, and AI-assisted conversation. It is not a
clinical, psychometric, or productivity-surveillance instrument.

The central question is:

> What human-system forces are plausibly present in this process step?

## Core Blocks

### HUMAN_DEMAND

Use `HUMAN_DEMAND` to describe what the process asks of the person.

Recommended shape:

- `ORIENT` - how the person becomes aware of the work and understands the
  situation.
- `ACT` - what the person must do, decide, compare, correct, approve, reject, or
  explain.
- `CLOSE` - how the person knows the step is done and what state changed.
- `RECOVER` - how the person gets unstuck, reverses, escalates, defers, or asks
  for more context.
- `ADAPT` - how repeated use changes skill, trust, role, habit, or the wider
  organisation.

Good `HUMAN_DEMAND` text is concrete. It should say what the human actually has
to notice, hold in mind, decide, and recover from.

### HUMAN_LOAD

Use `HUMAN_LOAD` for rough workload cues:

- `focus_actions`
- `business_actions`
- `trivial_actions`
- `explicit_decisions`
- `context_switches`
- `uncertainty_loops`
- `input_burden`
- `closure_clarity`
- `vigilance_load`
- `ambiguity_load`

The most useful distinction is between business work and interface overhead. A
step can have a simple business decision but still impose heavy load through
navigation, missing context, mode switching, or unstructured input.

### HUMAN_FACTORS

Use `HUMAN_FACTORS` to name plausible forces, not to diagnose a person.

Common families:

- `cognitive_load` - working memory, context switching, ambiguity, vigilance.
- `interface_friction` - hidden state, blank input, unclear affordance, mode
  confusion.
- `trust_automation` - automation bias, under-reliance, calibration, hidden
  uncertainty.
- `emotional_agency` - confidence, frustration, recoverability, perceived
  control.
- `social_role` - accountability, authority, status risk, escalation friction.
- `organisational_change` - role shift, deskilling/upskilling, learning loops.
- `behavioural_economics` - defaults, effort avoidance, choice overload,
  anchoring.
- `incentives_game_theory` - queue pressure, gaming metrics, blame avoidance,
  strategic compliance.

### HUMAN_RISK

Use `HUMAN_RISK` to prioritise redesign discussion.

Recommended fields:

```cairn
HUMAN_RISK:
  probability: low | medium | high
  impact: low | medium | high
  confidence: low | medium | high
  score: watch | moderate | significant | critical
  rationale: why this estimate is plausible.
```

These are qualitative design estimates. They are useful when they start a better
conversation. They are harmful when treated as objective measurement.

## Scoring Guidance

Use `watch` when the concern is plausible but low consequence.

Use `moderate` when either probability or impact is medium and recovery is easy.

Use `significant` when:

- probability or impact is high,
- the step affects trust, audit, memory, money, safety, or durable state,
- the human lacks context, authority, or a clear recovery path,
- the burden repeats often enough to shape behaviour.

Use `critical` when high probability and high impact combine with weak recovery,
hidden uncertainty, or accountability without control.

Always include `rationale`. A score without rationale is decoration.

## Offline Analyzer

`cairn-human-factors` runs a portable offline analysis. It looks for structured
Cairn cues and produces:

- factor findings,
- qualitative risk estimates,
- mitigations,
- conversation starters,
- suggested Cairn blocks.

The offline analyzer is conservative scaffolding. It should be good enough to
notice common patterns and start a review, not smart enough to replace one.

## Live Observation

`cairn-live-observe` is the runtime counterpart to the offline analyzer. It
summarises JSON or JSONL observation events from UI probes, logs, agent traces,
queue events, feedback, and output-review agents.

Use it when a product wrapper or observer agent needs to ask:

- What is the system doing repeatedly?
- Where are humans waiting, switching context, repairing, or carrying hidden
  accountability?
- Are agentic outputs grounded, useful, and recoverable?
- Which operational patterns should become product or process improvements?

The live observer should still follow the same guardrails: score process
conditions, not people; distinguish observation from inference; and keep human
review responsible for final judgement.

## LLM Interpretation

LLM interpretation is optional. It sits on top of the offline report:

```text
Cairn document -> offline report -> optional LLM provider -> proposed questions / annotations
```

The LLM should:

- use the offline report as context, not truth,
- propose annotations and questions,
- identify missing context,
- avoid clinical claims,
- keep the human reviewer responsible for final judgement.

Provider options include command wrappers, local llama.cpp/Ollama scripts,
hosted-model CLIs, or `HoglahLLMProvider` for queued execution.

## Anti-Patterns

Avoid:

- scoring a person instead of a process,
- claiming psychological certainty,
- using risk scores for performance management,
- treating human review as meaningful when context, authority, or recovery is
  missing,
- adding large annotation blocks to trivial low-risk steps,
- using an LLM to generate confident explanations without asking the human
  system owner whether they match reality.

## Review Checklist

For each human-facing step, ask:

- How does the person know this needs attention?
- What must they compare, remember, or infer?
- What is business work, and what is interface overhead?
- What happens if information is missing or wrong?
- Can the person recover without shame, blame, or technical debugging?
- Is the human accountable for something they can inspect and control?
- Does the step invite rubber-stamping, over-reliance, or avoidance?
- How does the loop close?
