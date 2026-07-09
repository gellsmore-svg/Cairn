---
type: Concept
title: Functional layout load
description: A Cairn heuristic for estimating cognitive and pointer/scan effort created by the spatial arrangement of fields, labels, evidence, warnings, and actions.
resource: https://github.com/gellsmore-svg/Cairn/blob/main/docs/FUNCTIONAL-LAYOUT-LOAD.md
tags: [cairn, hci, forms, layout, fitts-law, gestalt, cognitive-load]
timestamp: 2026-07-08T00:00:00Z
---

# Functional layout load

Functional layout load estimates how much extra work a UI layout creates by
separating things the user must understand together.

## Dimensions

- `related_field_distance`
- `label_field_distance`
- `evidence_action_distance`
- `primary_action_distance`
- `cumulative_visual_travel`
- `cumulative_pointer_travel`
- `field_count`
- `column_complexity`
- `grouping_clarity`
- `scan_path_linearity`
- `recovery_distance`
- `ai_output_evidence_distance`
- `uncertainty_action_distance`
- `override_distance`

## Evidence

Use DOM bounding boxes, screenshots, labels, ARIA relationships, DOM grouping,
tab order, and likely interaction sequence. If business relationships are not
encoded in the DOM, an LLM or human analyst may add explicit relations such as
`label_for`, `related`, `evidence_to_action`, `ai_output_to_evidence`,
`uncertainty_to_action`, and `override_for_recommendation`.

## Interpretation

High functional layout load suggests avoidable scanning, memory, comparison,
pointer movement, or error-recovery burden. It should trigger redesign
questions, not claims about a person's ability.

For human-AI augmentation, also inspect whether the AI recommendation,
uncertainty, evidence, source provenance, challenge path, and override action
are spatially connected. A fluent recommendation placed near the primary action
but far from uncertainty or evidence can increase automation-bias risk even when
ordinary form metrics look acceptable. See
[Augmentation process](augmentation-process.md).
