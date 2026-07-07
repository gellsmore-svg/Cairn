# Psychological: Cognitive Dissonance Reduction

Cairn description of Festinger's cognitive dissonance theory as a psychological process of tension reduction after inconsistency between beliefs, attitudes, or behaviors.

## CONTEXT

- **Individual**: Holds conflicting cognitions (beliefs, attitudes, actions).
- **Dissonance**: Psychological discomfort from inconsistency.
- **Reduction strategies**: Change behavior, change cognition, add consonant cognitions, trivialize.

## REQUIREMENTS

```
R1. Dissonance arises from inconsistency between cognitions. [MUST]
R2. Individuals are motivated to reduce dissonance. [MUST]
R3. Reduction can occur via multiple strategies. [MUST]
R4. Magnitude of dissonance affects effort to reduce. [MUST]
```

## OUTCOMES

Reduced psychological tension and restored cognitive consistency.

EMERGENT [PSYCHOLOGICAL: attitude or behavior change, rationalization]

---

## PROCESS — Formal

```
PROCESS ReduceCognitiveDissonance (INPUT: conflicting cognitions; OUTPUT: consistency restored)
  STATE
    cognitions [scope: individual; dir: read/write]
    dissonance_level [scope: individual; dir: read/write]

  1. Detect inconsistency between beliefs/actions. [COGNITIVE, EMOTIONAL]
  2. APPRAISAL [TYPE: primary] of dissonance magnitude and importance.
  3. DECISION [ON: reduction strategy]
     change behavior
     change cognition
     add consonant cognitions
     trivialize importance
  4. Apply strategy. [REGULATION]
  5. STATE UPDATE: cognitions aligned, dissonance reduced.
  6. EMERGENT [PSYCHOLOGICAL: new attitude or justified behavior]

  ITERATE if new inconsistency arises.
```

## PROCESS — Operator Profile

```
render-profile: operator

REDUCE DISSONANCE
  Purpose: Resolve internal conflict from inconsistent cognitions.
  Owner: Individual
  Assisted-by: [COGNITIVE] justification or [BEHAVIORAL] change
  1. Notice the conflict
  2. Assess how important it is
  3. Choose how to resolve (e.g. change mind or rationalize)
  4. Implement the change
  Next: Monitor for new inconsistencies
```