# Functional Layout Load

## Metrics
- element_count: 7
- field_count: 2
- action_count: 2
- column_count: 3
- avg_related_distance_px: 747.8
- max_related_distance_px: 1037.6
- avg_label_field_distance_px: 305.0
- max_evidence_action_distance_px: 1037.6
- cumulative_pointer_travel_px: 2008.5
- cumulative_pointer_travel_viewports: 1.18
- layout_load: high

## Findings
- **functional_layout_load: related element distance** - Related fields or evidence/action pairs are spatially separated enough to increase scan effort.
  Mitigation: Group related fields, evidence, warnings, and actions into the same decision region.
- **functional_layout_load: label-field distance** - Labels are far enough from fields that users may need extra visual association work.
  Mitigation: Place labels close to their controls and preserve clear whitespace grouping.
- **functional_layout_load: column complexity** - The form/action surface spans multiple columns, increasing the chance of skipped or misread fields.
  Mitigation: Prefer one main scan path; reserve columns for clearly independent groups.
- **functional_layout_load: cumulative pointer travel** - The likely interaction sequence requires substantial movement across the viewport.
  Mitigation: Move frequent next actions closer to the evidence and fields that justify them.

## Suggested Cairn Blocks
### FUNCTIONAL_LAYOUT_LOAD
```cairn
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
functional_layout_load: related element distance - Related fields or evidence/action pairs are spatially separated enough to increase scan effort.
functional_layout_load: label-field distance - Labels are far enough from fields that users may need extra visual association work.
functional_layout_load: column complexity - The form/action surface spans multiple columns, increasing the chance of skipped or misread fields.
functional_layout_load: cumulative pointer travel - The likely interaction sequence requires substantial movement across the viewport.
```

### IMPROVEMENT
```cairn
Group related fields, evidence, warnings, and actions into the same decision region.
Place labels close to their controls and preserve clear whitespace grouping.
Prefer one main scan path; reserve columns for clearly independent groups.
Move frequent next actions closer to the evidence and fields that justify them.
```