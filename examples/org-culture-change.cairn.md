# Organisational: Schein Culture Change Process

Cairn description of Edgar Schein's model for understanding and changing organizational culture (artefacts, espoused values, basic assumptions).

## CONTEXT

- **Organisation**: Existing culture as shared assumptions.
- **Leadership**: Primary culture creators and changers.
- **Change triggers**: External crises or internal failures.

## REQUIREMENTS

```
R1. Culture is the deepest level of shared assumptions. [MUST]
R2. Change requires unfreezing basic assumptions. [MUST]
R3. New assumptions must be learned through new behaviors and successes. [MUST]
R4. Leadership modeling and embedding mechanisms are critical. [MUST]
```

## OUTCOMES

Shifted organizational culture aligned with new strategy or environment.

EMERGENT [CULTURAL: new shared assumptions and behaviors]

---

## PROCESS — Formal

```
PROCESS ChangeCulture (INPUT: cultural misalignment; OUTPUT: new cultural assumptions)
  STATE
    artefacts         [scope: org; dir: read/write]  ref: C1
    espoused_values   [scope: org; dir: read/write]  ref: C2
    basic_assumptions [scope: org; dir: read/write]  ref: C3

  1. DIAGNOSE current culture (artefacts, values, assumptions). [CULTURAL, STRATEGIC]
  2. Create disconfirming evidence or anxiety to unfreeze. [LEADERSHIP]
  3. Provide psychological safety for learning new assumptions. [POWER, CULTURAL]
  4. ITERATE new behaviors, structures, and successes to embed.
     STATE UPDATE: basic_assumptions ← new shared beliefs  ref: C3
  5. REINFORCEMENT through leadership modeling and systems.
  6. EMERGENT [CULTURAL: new way of perceiving and acting]

  AWAIT [EVENT: cultural stabilization; TIMEOUT: multi-year]
```

## PROCESS — Operator Profile

```
render-profile: executive

CHANGE ORGANISATIONAL CULTURE (SCHE IN)
  Purpose: Shift deep assumptions to support new direction.
  Owner: Top leaders and culture champions
  Assisted-by: [CULTURAL] interventions, [STRATEGIC] alignment
  1. Surface current assumptions
  2. Create motivation to change (unfreeze)
  3. Teach and model new ways
  4. Embed through structures and successes
  5. Stabilize (refreeze)
  Next: Continuously reinforce
```