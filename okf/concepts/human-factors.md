---
type: Concept
title: Human factors semantics
description: A browsable lens library for asking which cognitive, psychological, social, organisational, behavioural-economic, and incentive forces may be present in a Cairn process step.
resource: https://github.com/gellsmore-svg/Cairn/blob/main/SPEC.md
tags: [cairn, human-factors, cognition, trust, organisational-change]
timestamp: 2026-07-07T00:00:00Z
---

# Human factors semantics

Cairn can describe a human-facing process step operationally, but the deeper
question is:

> What human-system forces are plausibly present in this step?

This concept file is a browsable lens library for AI-assisted review. It is not a
clinical or psychometric instrument. It helps an agent ask better questions,
surface likely human burden, and start a practical design conversation.

## Factor Families

### Cognitive Load

**Meaning:** demand on attention, working memory, reasoning, vigilance, and
decision capacity.

**Common factors:** working memory burden, attention fragmentation, ambiguity
load, decision fatigue, vigilance fatigue, context switching, interruption cost,
choice overload.

**Cairn cues:** high `context_switches`, many `explicit_decisions`, missing
context, nested review, long evidence chains, high `uncertainty_loops`.

**Mitigations:** co-locate evidence, reduce navigation, chunk decisions, show
progress, prefill safe defaults, separate business decisions from system-use
actions.

### Interface Friction

**Meaning:** cognitive effort caused by the interface rather than the business
task.

**Common factors:** unclear affordance, hidden state, mode confusion, weak
feedback, unnecessary clicks, duplicate entry, poor error messages.

**Cairn cues:** high `trivial_actions`, high `input_burden`, unclear `CLOSE`,
manual re-entry, user must remember data from another screen.

**Mitigations:** remove non-business actions, make state visible, use inline
validation, offer structured inputs, make closure unmistakable.

### Trust And Automation

**Meaning:** whether a person can rely on automation appropriately.

**Common factors:** automation bias, under-reliance, authority effect, poor trust
calibration, opacity, false precision, hidden uncertainty, explanation
over-trust.

**Cairn cues:** `[ASSISTED-BY: LLM]`, `[GATED]`, AI recommendation before
evidence, missing confidence, weak source provenance, human accountable for an
AI-shaped decision, one-way AI recommendation, weak override path.

**Mitigations:** show evidence before recommendation where needed, expose
uncertainty and disagreement, require reasons for high-impact approval, separate
AI suggestion from human decision, make inspect/reject/defer legitimate and
low effort.

### Emotional And Agency Impact

**Meaning:** how the process affects confidence, control, stress, shame, safety,
and willingness to act.

**Common factors:** anxiety, frustration, helplessness, loss of agency, fear of
blame, low perceived control, confidence erosion.

**Cairn cues:** high consequence with low control, unclear recovery, irreversible
actions, public failure, hostile error paths, no safe escalation.

**Mitigations:** provide reversible steps, safe escalation, calm feedback,
visible recovery paths, human-readable explanations, and permission to pause.

### Social And Role Dynamics

**Meaning:** interpersonal and role pressures that shape behaviour.

**Common factors:** role conflict, status risk, conformity pressure, diffusion of
responsibility, accountability without authority, social proof, escalation
friction.

**Cairn cues:** approval gates, manager pressure, cross-team dependency, unclear
owner, public metrics, human reviewer signs off on AI-generated work.

**Mitigations:** clarify ownership, show authority boundaries, make escalation
normal, preserve dissent, keep accountability aligned with control.

### Organisational Change

**Meaning:** how repeated use changes work, skill, authority, identity, and
incentives.

**Common factors:** deskilling, upskilling, role shift, resistance, legitimacy,
process ownership, institutional learning, human-AI role complementarity.

**Cairn cues:** `CHANGE_IMPACT`, new review duties, automation of old tasks,
new metrics, AI-mediated decisions, repeated exception patterns.

**Mitigations:** training, visible audit trail, reversible rollout, feedback
loops, role clarity, manager support, recognition of new skill.

### Augmentation Process

**Meaning:** whether a human-AI workflow extends human capacity through
complementary roles, cognitive-state awareness, adaptation, and calibrated trust.

**Common factors:** cognitive-state visibility, adaptation loop closure, role
complementarity, shared mental model maintenance, automation bias, interaction
pattern richness.

**Cairn cues:** `[ASSISTED-BY: LLM]`, `ADAPT`, `HUMAN_LOAD`, hidden model
adaptation, AI recommendation without contestability, human accountable for
AI-shaped judgement, repeated use changes skill or role.

**Mitigations:** name the AI role and human role separately, show why adaptation
happened, preserve human override, expose evidence and uncertainty, support
challenge/revise/escalate, track longitudinal outcomes and workarounds.

See [Augmentation process](augmentation-process.md).

### Behavioural Economics

**Meaning:** predictable patterns in choice under effort, risk, time pressure, or
default framing.

**Common factors:** default effect, loss aversion, present bias, effort
avoidance, salience bias, anchoring, sunk cost.

**Cairn cues:** preselected option, one-click approval, delayed downside, visible
short-term pressure, hidden long-term risk, blank free-text input.

**Mitigations:** set safe defaults, make risks salient, reduce effort for the
right action, avoid manipulative framing, provide structured reasons.

### Incentives And Game Theory

**Meaning:** how agents may behave strategically under incentives, blame, scarce
resources, or misaligned goals.

**Common factors:** principal-agent problem, strategic compliance, blame
avoidance, signalling, gaming metrics, moral hazard, tragedy of the commons.

**Cairn cues:** performance targets, audit exposure, unclear responsibility,
manual override, pressure to close queue, hidden external costs.

**Mitigations:** align metrics with outcomes, make tradeoffs visible, log
override reasons, avoid punishing escalation, review system-level patterns.

## Estimated Risk

Use `HUMAN_RISK:` to support prioritisation, not to pretend precision. The
recommended scale is qualitative:

- `probability: low | medium | high`
- `impact: low | medium | high`
- `confidence: low | medium | high`
- `score: watch | moderate | significant | critical`

The score is a design judgement. A useful heuristic:

- low probability + low impact = `watch`
- one medium dimension = `moderate`
- high probability or high impact = `significant`
- high probability + high impact, especially with low recovery = `critical`

Always include the reason. A score without rationale is decoration.

## Agent Conversation Starters

An AI reviewing a step should ask:

- What must the human keep in mind here?
- What information is missing at the moment of decision?
- Is the person accountable for something they cannot inspect or control?
- Which actions are business work, and which are interface overhead?
- What happens to capacity under time pressure, stress, interruption, or social
  pressure?
- Does the process create incentives to rubber-stamp, defer, escalate, or hide
  uncertainty?
- How does the loop close, and how does the person know it closed?
- If AI augments the step, what human capacity is being extended and what new
  load, bias, or accountability has moved into the interface?
