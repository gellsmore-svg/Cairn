# UI Human-Load Evidence: customer-po-review-layout

## Metrics
- assertions: 1
- clicks: 0
- contextSwitches: 0
- fills: 0
- layoutSnapshots: 1
- popups: 0
- screenshots: 0
- waits: 0

## Phases
- **orientation**
  - The coordinator must orient to customer identity, PO number, duplicate risk, and available next action.

## Human Systems
attention, working memory

## Findings
- **functional_layout_load: high layout traversal load** - Layout geometry suggests avoidable scan or pointer effort: avg related distance 747.8px; pointer travel 1.18 viewport(s).
  Mitigation: Group related fields, evidence, warnings, and actions into one decision region where possible.
- **scenario_finding: PO layout review finding** - Duplicate warning and exception evidence are too far from the accept action, so the operator may approve before integrating the relevant risk cues.
  Mitigation: Group PO identity, duplicate warning, line exceptions, and accept/repair actions in one decision panel.

## Risk
significant (probability: medium; impact: high; confidence: medium)
Estimated from observed UI actions, context switches, and scenario annotations; validate with real users.

## Suggested Cairn Blocks
### HUMAN_DEMAND
```cairn
ORIENTATION: The coordinator must orient to customer identity, PO number, duplicate risk, and available next action.
```

### HUMAN_LOAD
```cairn
focus_actions: 0
trivial_actions: 0
context_switches: 0
input_burden: 0 fill action(s)
closure_clarity: uncertain
human_systems: attention, working memory
```

### FUNCTIONAL_LAYOUT_LOAD
```cairn
snapshot_1:
  element_count: 7
  field_count: 2
  action_count: 2
  column_count: 3
  avg_related_distance_px: 747.8
  max_related_distance_px: 1037.6
  avg_label_field_distance_px: 305.0
  max_evidence_action_distance_px: 1037.6
  cumulative_pointer_travel_px: 2008.5
  cumulative_pointer_travel_viewports: 1.18
  layout_load: high
```

### HUMAN_FACTORS
```cairn
functional_layout_load: high layout traversal load - Layout geometry suggests avoidable scan or pointer effort: avg related distance 747.8px; pointer travel 1.18 viewport(s).
scenario_finding: PO layout review finding - Duplicate warning and exception evidence are too far from the accept action, so the operator may approve before integrating the relevant risk cues.
```

### HUMAN_RISK
```cairn
probability: medium
impact: high
confidence: medium
score: significant
rationale: Estimated from observed UI actions, context switches, and scenario annotations; validate with real users.
```