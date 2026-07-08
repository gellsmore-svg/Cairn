## Customer PO review layout evidence

PURPOSE:
  Record human-load evidence observed during UI simulation `customer-po-review-layout`.

EVIDENCE:
  ui_simulation: customer-po-review-layout
  clicks: 0
  fills: 0
  waits: 0
  context_switches: 0
  popups: 0

HUMAN_DEMAND:
  ORIENTATION: The coordinator must orient to customer identity, PO number, duplicate risk, and available next action.

HUMAN_LOAD:
  focus_actions: 0
  trivial_actions: 0
  context_switches: 0
  input_burden: 0 fill action(s)
  closure_clarity: uncertain
  human_systems: attention, working memory

FUNCTIONAL_LAYOUT_LOAD:
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

HUMAN_FACTORS:
  functional_layout_load: high layout traversal load - Layout geometry suggests avoidable scan or pointer effort: avg related distance 747.8px; pointer travel 1.18 viewport(s).
  scenario_finding: PO layout review finding - Duplicate warning and exception evidence are too far from the accept action, so the operator may approve before integrating the relevant risk cues.

HUMAN_RISK:
  probability: medium
  impact: high
  confidence: medium
  score: significant
  rationale: Estimated from observed UI actions, context switches, and scenario annotations; validate with real users.

REVIEW:
  Treat this as design evidence, not measurement of a person.
  Confirm the annotations with the process owner and representative users before adopting.