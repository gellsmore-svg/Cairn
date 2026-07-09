# Future Usage Logging And Analysis Spec

This is a future specification, not an implementation. It describes how a
running product could emit real-world touchpoint data that later flows back
through Cairn's HCI, human-factors, augmentation, and layout lenses.

## Boundary

This should probably become a separate repo or module, such as
`cairn-usage-analytics`, if it grows beyond a small event schema. Cairn core
should keep the semantic contract, not own product telemetry storage,
dashboards, identity, consent, or retention policy.

## Architecture

```text
Product UI / agent surface
  -> touchpoint event emitter
  -> privacy filter / consent gate
  -> event log
  -> Cairn replay and analysis
  -> recommendations and reports
```

The product emits events when a person notices work, orients, acts, waits,
recovers, challenges AI output, overrides, hands off, or completes a flow. Later
analysis compares actual usage against the designed Cairn process.

## Example Event

```json
{
  "event_type": "touchpoint.action",
  "schema_version": "0.1",
  "session_id": "anon-session-123",
  "process_id": "incoming-customer-po",
  "step_id": "review-duplicate-risk",
  "phase": "execution",
  "timestamp": "2026-07-09T12:00:00Z",
  "surface": "po-review-ui",
  "action": "accept_ai_recommendation",
  "ui": {
    "selector": "#accept-po",
    "visible_label": "Accept PO",
    "layout_snapshot_id": "layout-4"
  },
  "augmentation": {
    "ai_recommendation_visible": true,
    "uncertainty_visible": true,
    "evidence_opened": false,
    "override_available": true,
    "challenge_path_used": false
  },
  "load": {
    "context_switches": 1,
    "wait_ms": 320,
    "recovery_loop": false
  },
  "privacy": {
    "user_id": "pseudonymous",
    "content_redacted": true,
    "consent_basis": "product-analytics"
  }
}
```

## Mapping To OKF Concepts

- `phase` maps to `okf/concepts/hci-touchpoints.md`.
- `layout_snapshot_id` maps to `okf/concepts/functional-layout-load.md`.
- `augmentation` maps to `okf/concepts/augmentation-process.md`.
- `load` maps to `okf/concepts/human-factors.md`.
- Session handoff and repeated-use patterns map to organisational change,
  skill shift, trust calibration, and feedback suppression.

## Privacy And Ethics

- Prefer pseudonymous IDs and aggregate analysis by default.
- Redact business content unless explicitly needed and approved.
- Log enough context to support recovery and design improvement, not covert
  worker surveillance.
- Separate product performance analytics from individual performance scoring.
- Make consent, retention, access control, and deletion policy explicit.
- Treat cognitive-state data as sensitive. Physiological or inferred workload
  signals need a higher consent and governance bar.

## Future Analysis Questions

- Do people inspect evidence before accepting AI recommendations?
- Are overrides available but unused, or unavailable at the point of need?
- Which touchpoint phases produce recovery loops?
- Does actual pointer/scan path match the intended process?
- Do adaptation triggers reduce load or create hidden state drift?
- Are certain roles or experience levels helped less by the augmentation?

## Suggested Repo Shape

```text
cairn-usage-analytics/
  schemas/
    touchpoint-event.schema.json
  emitters/
    browser/
    python/
  replay/
    hci_touchpoint_replay.py
    augmentation_replay.py
  reports/
    usage-pattern-report.md
```

## Next Steps

1. Draft JSON Schema for `touchpoint.action`, `touchpoint.feedback`,
   `touchpoint.recovery`, `augmentation.challenge`, and `handoff.complete`.
2. Build a small browser emitter that can attach to Playwright scenarios.
3. Add a replay tool that converts event logs into Cairn UI evidence reports.
4. Validate with one real workflow before generalising.
