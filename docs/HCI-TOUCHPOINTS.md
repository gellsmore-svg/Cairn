# HCI Touchpoint Analysis

Cairn treats the user interface as part of the process, not as a cosmetic layer
around it. If a human has to notice, interpret, decide, enter, verify, wait,
recover, or explain something through a UI, that UI state is a human process
touchpoint.

This guide is written for consuming LLMs as much as for human reviewers. When
an LLM analyzes a Cairn process that includes a screen, form, dashboard, queue,
portal, or agentic UI, it should explicitly inspect the HCI touchpoints before
scoring human risk.

## Touchpoint Phases

For every human-facing process step, map the UI across these phases:

- `awareness` - how the person knows there is work to do.
- `orientation` - how the person understands the situation, current state,
  priority, risk, and available next actions.
- `execution` - what the person must click, type, select, compare, approve,
  reject, correct, or escalate.
- `feedback` - how the interface responds while work is in progress.
- `notification` - how the person knows the work has completed or moved state.
- `recovery` - how the person gets unstuck after missing data, invalid input,
  disagreement, error, timeout, or a wrong decision.
- `handoff` - how the result becomes visible to the next person, queue, system,
  audit trail, or future self.
- `adaptation` - how repeated use changes skill, trust, habits, workarounds,
  team norms, or organisational load.

The common failure is to analyze only `execution`. Many costly HCI problems live
in `orientation`, `feedback`, `recovery`, and `handoff`.

## LLM Review Protocol

When analyzing a UI-mediated step, the LLM should answer these questions:

1. What is the human goal at this exact UI state?
2. What does the person have to perceive before they can act?
3. What does the person have to remember from another screen, document, email,
   policy, or conversation?
4. Which actions are business work, and which are interface overhead?
5. Where does the UI require explicit decisions that are not actually part of
   the business task?
6. What state, confidence, evidence, priority, or consequence is hidden,
   delayed, ambiguous, duplicated, or visually weak?
7. What feedback does the UI provide after an action, and is it enough to close
   the loop?
8. What happens when information is missing, wrong, stale, disputed, or late?
9. Can the person recover without technical debugging, shame, blame, or loss of
   work?
10. What audit, accountability, or handoff burden remains after the screen says
    the step is done?

The LLM should distinguish observed evidence from inference. A screenshot,
selector, text label, disabled button, error message, timeout, or click path is
evidence. A claim about confusion, confidence, or workload is an inference that
should be phrased as plausible, not certain.

## Cognitive Aesthetic Rubric

In Cairn, "cognitive aesthetic" means how visual design shapes thinking. It is
not about prettiness. Assess whether the interface helps the person perceive,
prioritize, decide, and recover.

Use this rubric:

- `visual_hierarchy` - the primary status, risk, and next action are visually
  dominant before decoration or secondary metadata.
- `information_scent` - labels, grouping, and navigation make the next useful
  place/action predictable.
- `recognition_over_recall` - needed context is visible at the point of action,
  rather than held in memory.
- `state_visibility` - running, waiting, failed, saved, submitted, escalated,
  and complete states are explicit.
- `affordance_clarity` - clickable, editable, disabled, required, risky, and
  final actions are visually distinct.
- `perceptual_grouping` - related fields, evidence, warnings, and decisions are
  near each other and visually connected.
- `decision_shape` - the UI separates business decisions from navigation,
  housekeeping, and tool-operation decisions.
- `error_prevention` - risky actions, missing data, duplicate work, and invalid
  combinations are prevented or warned before submission.
- `error_recovery` - the user can see what failed, why it matters, how to fix
  it, and whether work was preserved.
- `accessibility_and_focus` - labels, instructions, focus movement, keyboard
  access, contrast, and target size support users under varied conditions.
- `confidence_cues` - source, authority, uncertainty, timestamp, owner, and
  audit implications are available where trust is required.
- `density_fit` - information density matches the work: operational tools may
  be dense, but must still be scannable and ordered by task relevance.

Useful external anchors include Nielsen Norman Group's
[10 usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)
around system status, real-world match, user control, recognition over recall,
error prevention, and recovery, and W3C
[WCAG 2.2](https://www.w3.org/TR/WCAG22/) guidance for accessible labels,
instructions, focus, and input support.

## Playwright Evidence Protocol

When Playwright or another browser agent is available, collect evidence in this
order:

1. Capture a screenshot for each meaningful process state.
2. Record the user goal, expected next action, and visible primary action for
   each state.
3. Record key selectors and visible text for status, risk, evidence, next
   action, errors, and confirmation.
4. Count clicks, field entries, waits, explicit decisions, context switches, and
   recovery loops.
5. Trigger at least one plausible error or missing-information path.
6. Verify whether completion is visible in the original work queue or downstream
   handoff surface.
7. Produce `HUMAN_DEMAND`, `HUMAN_LOAD`, `HUMAN_FACTORS`, `HUMAN_RISK`, and
   `IMPROVEMENT` notes with evidence references.

Do not rely on a single happy path. Cognitive load is often revealed by
exceptions, missing data, disabled actions, stale state, and unclear closure.

## Suggested Cairn Shape

```cairn
HCI_TOUCHPOINT:
  phase: orientation
  ui_surface: purchase order review queue
  human_goal: decide which incoming customer PO needs action first
  visible_evidence: screenshot po-queue-01.png; selector #po-risk-column
  hidden_or_weak_context: duplicate PO warning is below the fold
  cognitive_aesthetic:
    visual_hierarchy: risk marker competes with decorative status chips
    recognition_over_recall: customer credit status is not visible
    state_visibility: queue item does not show whether matching is still running
  human_load:
    focus_actions: 5
    explicit_decisions: 2
    context_switches: 1
    recall_required: true
  risk:
    probability: medium
    impact: high
    confidence: medium
  improvement: group customer, PO validity, duplicate risk, and next action in one decision panel.
```

If the target Cairn document does not yet support a dedicated
`HCI_TOUCHPOINT` block, capture the same content inside `HUMAN_DEMAND`,
`HUMAN_LOAD`, `HUMAN_FACTORS`, `HUMAN_RISK`, `SUPPORT`, and `IMPROVEMENT`.

## LLM Output Contract

For each analyzed UI step, return:

- a short touchpoint map by phase,
- evidence references,
- cognitive aesthetic findings,
- human-load counts or estimates,
- qualitative human risk with rationale,
- specific redesign suggestions,
- open questions for the product/process owner.

The output should make underplayed UI costs visible. It should not claim that an
automated review proves real user experience.
