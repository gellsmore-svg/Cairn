# Relational Substrate in Cairn — grammar sandbox and sweep (representative slice)

A Cairn description of **Relational Substrate as it currently stands** — a
browser sandbox and analysis bench for the substrate grammar (route, closure,
phase, charge, continuity). This example stress-tests Cairn on a **deterministic,
human-driven** modelling flow with almost no LLM steps — useful contrast to the
family's agentic products.

The project is a **directional / conceptual lens**, not a quantitative predictor;
see its validation-status docs for honest standing.

---

## CONTEXT

- **operator** — researcher adjusting sliders, presets, and sweep parameters.
- **grammar state** — `{route, closure, phase, charge, continuity}` derived from
  UI inputs via `deriveGrammar`.
- **single encounter** — one `calculateOutcome(input)` snapshot (admitted /
  returned / stored / scattered fractions + closure metrics).
- **sequence trace** — `simulateSequence(base, n)` with memory carry across steps.
- **coherence sweep** — batch rule-model exploration (`npm run sweep`).

## REQUIREMENTS

```
R1. Outcomes SHALL be computed from explicit grammar inputs, not rendered curves. [MUST]
R2. Multi-step traces SHALL carry memory (continuity + stress) across steps.      [MUST]
R3. Sweeps SHALL be reproducible from recorded input signatures.                  [SHOULD]
R4. The UI SHALL expose grammar state and identity-at-risk readouts live.         [SHOULD]
R5. Claims SHALL remain directional unless a separate magnitude test passes.       [MUST]
```

## OUTCOMES

The operator can explore how admissibility and identity persistence respond to
grammar alignment, run short multi-step histories, and batch-scan parameter space —
without conflating the abstract model with domain simulators.

---

## PROCESS — Formal

```
PROCESS ExploreScenario (INPUT: slider_state, preset; OUTPUT: outcome_view)
  1. Map UI controls to closed/transient forms and scenario preset.           [CODE, DETERMINISTIC]
  2. CALL deriveGrammar(slider_state) → grammar_state                          [CODE, DETERMINISTIC]
  3. CALL calculateOutcome(grammar_state) → fractions, closure_metrics         [CODE, DETERMINISTIC] [SATISFIES: R1]
  4. Render outcome fractions, identity preserved/at-risk, route-split viz.  [CODE]
  OUTPUT: outcome_view

PROCESS RunSequenceTrace (INPUT: base_input, n_steps; OUTPUT: trace)
  1. ITERATE [OVER: 1..n_steps; MAX: n_steps]
     1.1 Apply step perturbation to base_input (regime schedule).             [CODE]
     1.2 CALL simulateSequence(step_input, memory_carry) → step_outcome       [CODE] [SATISFIES: R2]
         STATE UPDATE: memory_carry ← accumulated continuity + stress
     1.3 Record identity score, grammar alignment, durability estimate.      [CODE]
  2. Summarize path-dependent order effect (gentle-first vs harsh-first).      [CODE]
  OUTPUT: trace

PROCESS RunCoherenceSweep (INPUT: sweep_config; OUTPUT: sweep_report)
  1. Generate parameter grid from sweep_config.                               [CODE, DETERMINISTIC]
  2. ITERATE [OVER: grid points; MAX: sweep_budget]
     2.1 CALL calculateOutcome(point) → metrics                               [CODE, BATCH]
     2.2 Classify high/low grammar regions and preservation rates.            [CODE]
  3. Write sweep_report with signatures for reproduction.                       [CODE] [SATISFIES: R3]
  OUTPUT: sweep_report
```

## PROCESS — operator profile (rendered view)

```
render-profile: operator

TUNE a scenario
  Purpose:  See how grammar alignment affects admissibility and identity in one snapshot.
  Owner:    Operator
  Assisted by: browser UI (sliders, presets)
  Next:     run a 3-step trace or launch a sweep

TEST a history
  Purpose:  Ask whether identity survives a short sequence of encounters.
  Owner:    Operator
  Outputs:  per-step trace + order-effect readout
```

## PROCESS — Narrative (same backbone)

```
PROCESS — ExploreScenario: interactive sandbox loop.
  Sliders → derive grammar → calculate outcome → render.

PROCESS — RunSequenceTrace: path-dependent memory carry.
  Step through a regime schedule with simulateSequence; compare orderings.

PROCESS — RunCoherenceSweep: batch exploration offline.
  Grid search calculateOutcome; report grammar signatures.
```

---

## Agentic steps in this slice

**None by default.** Every step is `[CODE, DETERMINISTIC]`. The operator is
human; there is no LLM planner, `ITERATE` termination is numeric, and `RECURSE`
does not appear.

This deliberately exercises Cairn on a **non-agentic** scientific bench — useful
for verifying that REQUIREMENTS, MILESTONE-less PROCESS, and `ITERATE [MAX: n]`
work without `[LLM, STOCHASTIC]` tags.

A *potential* agentic extension (not implemented) would be an LLM `[STOCHASTIC]`
step proposing regime schedules for `RunSequenceTrace`, gated by human `AWAIT`.

---

## Stress-test notes

What worked: multiple PROCESSes for UI vs batch vs sequence; pure CODE tags;
`ITERATE` with numeric bounds; clear OUTCOMES about directional standing.

Rough edges:

1. **No REQUIREMENTS acceptance sub-blocks** — RS uses simpler R# lines; could
   add ACCEPTANCE examples when linking to pre-registered tests.
2. **No CALL composition** — standalone project; no `CALL Tirzah` / family links.
3. **Validation layer** — `analysis/` scripts are a fourth PROCESS family not
   expanded here (held-out tests, order-effect derivation).