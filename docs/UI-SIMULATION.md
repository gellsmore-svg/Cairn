# UI Simulation

Cairn can use browser-driven UI simulations to collect evidence about human load in an actual interface. The intent is not to replace UX judgement with automation. It is to make the cognitive and social cost of a process step visible enough that an LLM, developer, or product team can discuss it directly.

The first prototype is `cairn-ui-sim`. It delegates to Playwright from the target project, so Cairn does not need to carry a browser runtime as a hard dependency.

## Model

A scenario is a JSON file with a base URL and ordered steps. Each step can be a browser action, an assertion, or a human-load annotation.

The useful unit of analysis is usually not just "the user clicks a button". A step can contain several human experiences:

- Awareness: noticing that work is needed and finding the relevant surface.
- Execution: performing the work, including prompts, choices, form entry, review, and correction.
- Notification: receiving the result and understanding whether the work is complete.
- Inspection: optionally opening traces, logs, provenance, or explanations.
- Feedback: reporting the quality of the outcome back into the system.

Those phases map onto Cairn's human factors vocabulary. A scenario can name the human systems plausibly involved, such as attention, working memory, trust calibration, social risk, configuration burden, and context switching.

## Running A Scenario

Install Cairn in editable mode, then run the scenario against a project that already has Playwright installed:

```bash
cairn-ui-sim docs/scenarios/mahlah-human-load.json \
  --project-root ../Mahlah \
  --base-url http://localhost:5273
```

The report is written to the scenario's `output` path unless `--output` is supplied. Relative output paths are resolved from the scenario file, not from the target project.

After running the browser simulation, summarise it as human-load evidence:

```bash
cairn-ui-evidence docs/analysis/mahlah-ui-sim-report.json \
  --output docs/analysis/mahlah-ui-evidence.md
```

This second step turns mechanical observations into suggested Cairn blocks such
as `HUMAN_DEMAND`, `HUMAN_LOAD`, `HUMAN_FACTORS`, and `HUMAN_RISK`.

## Scenario Actions

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
- `popup`
- `screenshot`
- `finding`

Most selector-based actions accept an optional zero-based `index`, which is useful when a UI has repeated controls.

## Evidence Shape

The report records:

- Mechanical counts: clicks, fills, waits, assertions, popups, context switches, and screenshots.
- Browser observations: what was clicked, filled, selected, waited for, or opened.
- Human-load observations: phase, involved human systems, and the demand being placed on the user.
- Findings: estimated risks, impacts, and mitigations supplied by the scenario author or later by an LLM.

The next layer is an LLM reviewer that consumes this report together with a Cairn process description and asks: "what human systems are plausibly present in this process step, and where does the interface create avoidable load?"

## Where This Goes Next

The intended stack is:

```text
Playwright scenario
  -> UI simulation report
  -> deterministic human-load evidence
  -> optional LLM role-play / critique
  -> revised Cairn process annotations
```

The LLM layer should not pretend to be a real user study. Its job is to simulate
plausible user experience, search for missing context, and initiate better
questions for the developer or process owner. The deterministic evidence layer
keeps that conversation grounded in what the interface actually required.
