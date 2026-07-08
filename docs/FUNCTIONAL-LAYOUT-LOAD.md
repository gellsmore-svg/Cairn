# Functional Layout Load

Functional layout load is the cognitive and motor effort created by the spatial
arrangement of fields, labels, evidence, warnings, and actions. It overlaps with
form design, HCI touchpoints, visual hierarchy, and cognitive aesthetic, but it
focuses specifically on whether the layout makes the user's functional task
easy to scan, traverse, and complete.

This is not eye tracking. Cairn estimates visual and pointer traversal load
from UI geometry, relationships, and likely interaction sequence. Treat it as a
design heuristic that points to review questions, not as a direct measurement
of a person.

## Source Patterns

Useful established anchors:

- Fitts's Law: pointer effort depends on target distance and size. See NN/g's
  [Fitts's Law and Its Applications in UX](https://www.nngroup.com/articles/fitts-law/).
- Gestalt proximity and grouping: related elements are easier to understand
  when visually grouped.
- Form design guidance: NN/g recommends grouping related fields and placing
  labels near associated inputs in
  [Group Form Elements Effectively Using White Space](https://www.nngroup.com/articles/form-design-white-space/).
- Baymard's form research highlights the usability cost of excess fields and
  difficult form structures, including
  [field count](https://baymard.com/blog/checkout-flow-average-form-fields) and
  [multicolumn forms](https://baymard.com/blog/avoid-multi-column-forms).
- WCAG 2.2 provides accessibility anchors for labels, instructions, focus, input
  support, and target interaction.

## Heuristic Dimensions

Use these dimensions when reviewing a form or operational UI:

- `related_field_distance` - distance between fields that must be compared or
  understood together.
- `label_field_distance` - distance between a label and its input/control.
- `evidence_action_distance` - distance between evidence/risk cues and the
  action they justify.
- `primary_action_distance` - distance from the user's likely current locus to
  the next required action.
- `cumulative_visual_travel` - estimated scan distance across the task path.
- `cumulative_pointer_travel` - estimated mouse/pointer distance across the
  interaction sequence.
- `field_count` - number of fields or controls that must be read or completed.
- `column_complexity` - number of horizontal lanes the user must scan across.
- `grouping_clarity` - whether related fields, warnings, and actions are
  visually grouped.
- `scan_path_linearity` - whether the task can be completed in a predictable
  top-to-bottom or left-to-right path.
- `recovery_distance` - distance from error/warning to the control or evidence
  needed to fix it.

## JSON Input

`cairn-layout-load` accepts a JSON object:

```json
{
  "viewport": {"width": 1440, "height": 900},
  "elements": [
    {"id": "po_number", "role": "field", "x": 280, "y": 116, "width": 220, "height": 36},
    {"id": "duplicate_warning", "role": "warning", "x": 980, "y": 620, "width": 260, "height": 48},
    {"id": "accept", "role": "button", "x": 1120, "y": 140, "width": 120, "height": 44}
  ],
  "relations": [
    {"from": "po_number", "to": "duplicate_warning", "type": "related"},
    {"from": "duplicate_warning", "to": "accept", "type": "evidence_to_action"}
  ],
  "sequence": ["po_number", "duplicate_warning", "accept"]
}
```

Coordinates are CSS pixels in the current viewport. A Playwright script can
collect them with `locator.boundingBox()`. An LLM or human reviewer can supply
relationships when DOM hierarchy does not encode the business relationship.

In Cairn UI scenarios, use the `measureLayout` action to collect this geometry
during `cairn-ui-sim`. The resulting `layoutLoad` snapshots are consumed by
`cairn-ui-evidence` automatically.

## CLI

```bash
cairn-layout-load po-layout.json -o po-layout-load.md
cairn-layout-load po-layout.json -f json
```

The report includes metrics, findings, and suggested Cairn blocks such as:

```cairn
FUNCTIONAL_LAYOUT_LOAD:
  element_count: 6
  field_count: 2
  column_count: 3
  avg_related_distance_px: 810.4
  cumulative_pointer_travel_viewports: 2.1
  layout_load: high
```

See `docs/analysis/customer-po-review-layout.json` and
`docs/analysis/customer-po-review-layout-load.md` for a worked incoming customer
PO review example.

For the browser-simulation shape, see:

- `docs/scenarios/customer-po-review-layout.json`
- `docs/analysis/customer-po-review-ui-sim-report.json`
- `docs/analysis/customer-po-review-ui-evidence.md`
- `docs/analysis/customer-po-review-ui-annotations.cairn.md`

## Interpretation

High layout load suggests that users may be doing avoidable spatial work:

- scanning back and forth between related fields,
- associating labels with distant controls,
- moving from evidence to action across disconnected regions,
- skipping fields in multicolumn layouts,
- losing track of warnings or state while completing a form,
- needing extra recovery effort after errors.

Recommended mitigations:

- group related fields, warnings, evidence, and actions into one decision region,
- keep labels close to controls,
- prefer one dominant scan path for transactional forms,
- move primary actions close to the evidence that justifies them,
- avoid wide multicolumn layouts unless columns represent clearly independent
  groups,
- keep error messages beside the fields/actions needed for recovery.
