# Psychological: Dual-Process Decision Making

Cairn description of dual-process theories (System 1 vs System 2) in decision making under uncertainty or affect.

## CONTEXT

- **Individual**: Faced with decision.
- **System 1**: Fast, intuitive, emotional, heuristic-based.
- **System 2**: Slow, deliberate, analytical, effortful.
- **Context**: Time pressure, emotions, complexity.

## REQUIREMENTS

```
R1. Decisions involve both automatic and controlled processes. [MUST]
R2. System 1 provides quick defaults; System 2 can override or monitor. [MUST]
R3. High affect or low resources favor System 1. [MUST]
R4. Post-decision rationalization often occurs. [MUST]
```

## OUTCOMES

A decision is made, often with justification aligning it to self-image.

EMERGENT [PSYCHOLOGICAL: choice + rationalization or regret]

---

## PROCESS — Formal

```
PROCESS DualProcessDecision (INPUT: decision situation; OUTPUT: choice + justification)
  STATE
    impulses [scope: individual; dir: read]
    analysis [scope: individual; dir: read/write]

  1. SYSTEM-1 generates fast emotional or heuristic impulse. [EMOTIONAL, COGNITIVE]
  2. DECISION [ON: engage System 2]
     low resources or time pressure → use impulse
     high stakes → engage analysis
  3. SYSTEM-2 evaluates options, evidence, values. [COGNITIVE]
  4. Integrate or override. [REGULATION]
  5. STATE UPDATE: choice made + post-decision rationalization.
  6. EMERGENT [PSYCHOLOGICAL: action + updated beliefs]

  AWAIT [EVENT: outcome feedback; TIMEOUT: variable]
```

## PROCESS — Operator Profile

```
render-profile: operator

MAKE DECISION (DUAL PROCESS)
  Purpose: Reach a choice balancing speed and accuracy.
  Owner: Individual
  Assisted-by: [EMOTIONAL] intuition and [COGNITIVE] reasoning
  1. System 1 flashes initial response
  2. If needed, slow down for analysis
  3. Choose and justify
  Next: Act and learn from results
```