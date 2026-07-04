# Milcah in Cairn — recursive coherence-pressure rounds (representative slice)

A Cairn description of **Milcah as it currently stands**, for the slice that
exercises recursive multi-LLM reasoning with **burden symmetry** and bounded
rounds. Milcah pressure-tests frameworks for coherence; it does not decide
truth.

This example is maintained in Cairn (canonical stress-test location); the same
process is referenced from Milcah's own docs.

---

## CONTEXT

- **Milcah** — the coherence engine: "What would have to be true for this to
  remain coherent?"
- **burden symmetry** — every framework gets the *same* challenges; none is
  protected for popularity, authority, or preference.
- **family backends** — ontology via **Mahalath**, memory via **Tirzah**, LLM
  execution via **Hoglah**.

## REQUIREMENTS

```
R1. Every framework SHALL face identical challenge structures.            [MUST]
R2. Uncertainty SHALL be a permitted terminal state; forced certainty is
    forbidden.                                                            [MUST]
R3. Coherence scores SHALL exclude popularity / confidence / institutional
    acceptance.                                                           [MUST]
R4. Rounds SHALL be bounded (convergence / threshold / repeat / review / budget). [MUST]
```

## OUTCOMES

A coherence report: visible assumptions, ontology state, fractures, symmetric
burden, sharpened uncertainty — never a verdict of "truth".

---

## PROCESS — Formal

```
PROCESS AnalyzeFramework (INPUT: framework; OUTPUT: coherence_report)
  STATE
    units       [scope: process; dir: read/write]  ref: U1
    ontology    [scope: process; dir: read/write]  ref: U2
    debt        [scope: process; dir: read/write]  ref: U3
    fractures   [scope: process; dir: write]       ref: U4

  1. MILESTONE FRAME — Ingest the framework and extract reasoning. [LLM, STOCHASTIC, SYNC]
     STATE UPDATE: units ← typed reasoning units
  2. MILESTONE PLACE — Build/validate the worldview ontology.
     CALL Mahalath.BuildOntology(units) → ontology              [EXTERNAL, ASSISTED-BY: LLM]
  3. MILESTONE PRESSURE — Recursively pressure-test each node.
     ITERATE [UNTIL: round converges OR repeated objections; MAX: round_budget] [SATISFIES: R4]
       3.1 RECURSE [BASE: node resolved or atomic; MAX_DEPTH: none-fixed]
             Ask the five pressure questions per node.            [LLM, STOCHASTIC]
       3.2 Generate counter-frameworks + strongest objections.    [LLM, STOCHASTIC, ASSISTED-BY: EXTERNAL]
       3.3 Apply identical challenge structures to all rivals.   [CODE, DETERMINISTIC] [SATISFIES: R1]
       3.4 Evaluate reasoning steps for fallacies.                 [LLM, STOCHASTIC]
           STATE UPDATE: fractures += located fallacies
       3.5 Update explanatory debt + coherence metrics.          [CODE, DETERMINISTIC] [SATISFIES: R3]
       3.6 BREAK [IF: convergence reached OR objection pattern repeats]
  4. MILESTONE REVIEW — surface unresolved states for a human.
     AWAIT [EVENT: human review; TIMEOUT: never]                   [HUMAN, ASSISTED-BY: LLM]
  5. MILESTONE REPORT — emit the coherence report.                 [CODE, DETERMINISTIC]
  OUTPUT: coherence_report
  CONSTRAINTS: permitted terminals include unresolved, equivalent burden,
               insufficient information. [SATISFIES: R2]
```

---

## Stress-test notes

What worked: `MILESTONE`, nested `ITERATE` + `RECURSE`, `CALL` to an external
ontology builder, deterministic scoring steps mixed with stochastic LLM steps,
explicit permitted terminal states.

Rough edge: **multi-LLM reconciliation** (extract with N models, merge by text
or semantic agreement) is a real Milcah feature not yet spelled out as a Cairn
construct — today it's implied inside step 1 as a single LLM step.