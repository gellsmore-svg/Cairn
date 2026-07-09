---
type: Concept
title: HCI touchpoints and cognitive aesthetic
description: A Cairn lens for analyzing UI-mediated human work across awareness, orientation, execution, feedback, recovery, handoff, and adaptation.
resource: https://github.com/gellsmore-svg/Cairn/blob/main/docs/HCI-TOUCHPOINTS.md
tags: [cairn, hci, ui, cognitive-load, cognitive-aesthetic, playwright]
timestamp: 2026-07-08T00:00:00Z
---

# HCI touchpoints and cognitive aesthetic

In Cairn, a user interface is part of the process. A screen, queue, form,
dashboard, or agentic chat surface mediates the human work of noticing,
orienting, deciding, acting, recovering, and handing off.

## Touchpoint Map

When an agent analyzes a UI-mediated process step, it should map:

- `awareness` - how the user knows work exists.
- `orientation` - how the user understands state, risk, evidence, priority, and
  next actions.
- `execution` - what the user clicks, types, selects, compares, approves,
  rejects, corrects, or escalates.
- `feedback` - how the UI responds while work is in progress.
- `notification` - how completion or state change is communicated.
- `recovery` - how missing information, errors, stale state, or disagreement are
  handled.
- `handoff` - how the result reaches the next person, queue, system, audit
  trail, or future self.
- `adaptation` - how repeated use changes skill, shortcuts, trust, roles, and
  organisational habits; in human-AI workflows, how the system notices or
  responds to workload, confidence, disagreement, or user correction.

## Cognitive Aesthetic

The cognitive aesthetic of a UI is how the visual and interaction design shapes
thinking. It is not decoration. Review:

- visual hierarchy,
- information scent,
- recognition over recall,
- state visibility,
- affordance clarity,
- perceptual grouping,
- decision shape,
- error prevention,
- error recovery,
- accessibility and focus,
- confidence cues,
- bias-mitigation affordances,
- cognitive-state and adaptation visibility,
- interaction pattern richness,
- density fit.

## Evidence

Useful evidence includes screenshots, selectors, visible labels, disabled
states, error messages, wait states, confirmation messages, click paths, context
switches, recovery paths, AI recommendations, uncertainty displays, override
paths, adaptation triggers, and evidence of whether the person can challenge or
revise AI output. Claims about human confusion or confidence should be marked as
inference unless validated by user research.

## Cairn Output

Preferred output is a short touchpoint map plus `HUMAN_DEMAND`, `HUMAN_LOAD`,
`HUMAN_FACTORS`, `HUMAN_RISK`, and `IMPROVEMENT` notes grounded in evidence.
For human-AI workflows, also ask the questions in
[Augmentation process](augmentation-process.md): what capacity is being
augmented, how trust is calibrated, and how adaptation closes.
