# UI Simulation

Cairn can use browser-driven UI simulations to collect evidence about human load in an actual interface. The intent is not to replace UX judgement with automation. It is to make the cognitive and social cost of a process step visible enough that an LLM, developer, or product team can discuss it directly.

The first prototype is `cairn-ui-sim`. It delegates to Playwright from the target project, so Cairn does not need to carry a browser runtime as a hard dependency.

## Model

A scenario is a JSON file with a base URL and ordered steps. Each step can be a browser action, an assertion, or a human-load annotation.

The useful unit of analysis is usually not just "the user clicks a button". A step can contain several human experiences:

- Awareness: noticing that work is needed and finding the relevant surface.
- Orientation: understanding the current state, priority, risk, evidence, and
  available next action.
- Execution: performing the work, including prompts, choices, form entry, review, and correction.
- Feedback: seeing how the interface responds while work is in progress.
- Notification: receiving the result and understanding whether the work is complete.
- Inspection: optionally opening traces, logs, provenance, or explanations.
- Recovery: handling missing information, wrong state, errors, or disagreement.
- Handoff: seeing how the result reaches the next person, queue, system, or
  audit trail.
- Adaptation: noticing how repeated use changes skill, trust, shortcuts, or
  organisational behaviour.

Those phases map onto Cairn's human factors vocabulary. A scenario can name the human systems plausibly involved, such as attention, working memory, trust calibration, social risk, configuration burden, and context switching.

## Running A Scenario

Install Cairn in editable mode, then run the scenario against a project that already has Playwright installed:

```bash
cairn-ui-sim docs/scenarios/mahlah-human-load.json \
  --project-root ../Mahlah \
  --base-url http://localhost:5273
```

The report is written to the scenario's `output` path unless `--output` is supplied. Relative output paths are resolved from the scenario file, not from the target project.

For the complete workflow in one pass:

```bash
cairn-ui-pipeline docs/scenarios/mahlah-recovery-loop.json \
  --project-root ../Mahlah \
  --base-url http://localhost:5273 \
  --llm-command scripts/codex_llm_provider.py \
  --persona novice-repair-user \
  --persona queue-pressure-operator
```

The pipeline validates the scenario, runs the browser simulation, writes the
JSON report, generates the evidence summary, exports the Cairn annotation
snippet, and runs role-play when an LLM provider is supplied. Use `--from-report`
to regenerate evidence, annotations, or role-play from an existing report
without opening a browser.

After running the browser simulation, summarise it as human-load evidence:

```bash
cairn-ui-evidence docs/analysis/mahlah-ui-sim-report.json \
  --output docs/analysis/mahlah-ui-evidence.md
```

This second step turns mechanical observations into suggested Cairn blocks such
as `HUMAN_DEMAND`, `HUMAN_LOAD`, `HUMAN_FACTORS`, and `HUMAN_RISK`.

Then ask an LLM to role-play plausible user experience from the grounded
evidence:

```bash
cairn-ui-roleplay docs/analysis/mahlah-ui-sim-report.json \
  --llm-command "python scripts/my_llm_wrapper.py" \
  --output docs/analysis/mahlah-ui-roleplay.md
```

`cairn-ui-roleplay` also supports `--hoglah-model` for queued execution. The
LLM receives the raw browser report, the deterministic evidence summary, and a
set of personas. Use `--persona` repeatedly to supply domain-specific
perspectives.

For a local Codex CLI trial, use the included command-provider wrapper:

```bash
cairn-ui-roleplay docs/analysis/mahlah-recovery-loop-ui-sim-report.json \
  --llm-command scripts/codex_llm_provider.py \
  --persona novice-repair-user \
  --persona queue-pressure-operator \
  --persona accountable-approver-without-authority-evidence \
  --output docs/analysis/mahlah-recovery-loop-ui-roleplay.md
```

Set `CAIRN_CODEX_PROVIDER_CWD`, `CAIRN_CODEX_PROVIDER_TIMEOUT`, or
`CAIRN_CODEX_PROVIDER_SANDBOX` to tune the wrapper.

Finally, export a review-ready Cairn annotation snippet:

```bash
cairn-ui-annotations docs/analysis/mahlah-ui-sim-report.json \
  --step-title "Review Mahlah UI human load" \
  --output docs/analysis/mahlah-ui-annotations.cairn.md
```

This emits `HUMAN_DEMAND`, `HUMAN_LOAD`, `HUMAN_FACTORS`, and `HUMAN_RISK`
blocks with a short evidence header. It is intentionally a snippet rather than
an automatic edit: a human process owner should decide where it belongs.

## Scenario Actions

Validate scenario shape before running a browser:

```bash
cairn-ui-scenario-validate docs/scenarios/mahlah-human-load.json
```

`cairn-ui-sim` runs the same validation by default. Use `--skip-validation` only
when experimenting with runner changes.

Supported actions in the prototype:

- `assertVisible`
- `assertCountAtLeast`
- `assertTextIncludes`
- `click`
- `fill`
- `press`
- `select`
- `waitForSelector`
- `waitForText`
- `waitForNonEmptyText`
- `waitForCountAtLeast`
- `measureLayout`
- `popup`
- `screenshot`
- `finding`

Most selector-based actions accept an optional zero-based `index`, which is useful when a UI has repeated controls.

`measureLayout` records DOM geometry for functional layout load analysis:

```json
{
  "action": "measureLayout",
  "label": "Measure PO review layout",
  "elements": [
    {"id": "po_number", "selector": "#po-number", "role": "field"},
    {"id": "duplicate_warning", "selector": "#duplicate-warning", "role": "warning"},
    {"id": "accept", "selector": "#accept", "role": "button"}
  ],
  "relations": [
    {"from": "po_number", "to": "duplicate_warning", "type": "related"},
    {"from": "duplicate_warning", "to": "accept", "type": "evidence_to_action"}
  ],
  "sequence": ["po_number", "duplicate_warning", "accept"]
}
```

The runner stores the bounding boxes under `layoutLoad`. The evidence layer then
adds `FUNCTIONAL_LAYOUT_LOAD` findings and blocks automatically.

Each step may include `humanLoad`:

```json
{
  "phase": "execution",
  "systems": ["language", "working memory"],
  "demand": "The user translates intent into a prompt while preserving the business question."
}
```

Known phases are `awareness`, `orientation`, `execution`, `feedback`,
`notification`, `inspection`, `recovery`, `handoff`, `adaptation`, and
`organisational_pressure`.

Steps may also set `contextSwitch: true` when the action moves the user into a
different surface, mode, or mental frame. The evidence layer counts this
separately from ordinary clicks.

## Evidence Shape

The report records:

- Mechanical counts: clicks, fills, waits, assertions, popups, context switches, and screenshots.
- Browser observations: what was clicked, filled, selected, waited for, or opened.
- Layout snapshots: measured element rectangles, relationships, and task
  sequence for functional layout load analysis.
- Human-load observations: phase, involved human systems, and the demand being placed on the user.
- Findings: estimated risks, impacts, and mitigations supplied by the scenario author or later by an LLM.

The next layer is an LLM reviewer that consumes this report together with a
Cairn process description and asks: "what human systems are plausibly present in
this process step, which HCI touchpoints mediate the work, and where does the
interface create avoidable cognitive load?"

For cognitive-aesthetic review, ask the LLM to inspect visual hierarchy,
information scent, recognition over recall, state visibility, affordance
clarity, perceptual grouping, error prevention, recovery, accessibility, focus,
confidence cues, and information density. See
[`HCI-TOUCHPOINTS.md`](HCI-TOUCHPOINTS.md).

## Where This Goes Next

The intended stack is:

```text
Playwright scenario
  -> UI simulation report
  -> deterministic human-load evidence
  -> optional LLM role-play / critique
  -> review-ready Cairn annotation snippet
  -> revised Cairn process annotations
```

The LLM layer should not pretend to be a real user study. Its job is to simulate
plausible user experience, search for missing context, and initiate better
questions for the developer or process owner. The deterministic evidence layer
keeps that conversation grounded in what the interface actually required.

The role-play prompt asks the LLM to separate observed evidence from inference
and to look for awareness, execution, closure, recovery, and organisational
pressure. This makes it useful for design conversation without treating the
model as a substitute for real user research.
