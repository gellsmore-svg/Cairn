# Organisational: ADKAR Model for Individual Change

Cairn description of the Prosci ADKAR model, focusing on the individual journey that enables organisational change.

## CONTEXT

- **Individual** undergoing change.
- **Organisation** implementing initiative.
- **Change** as the shift in work, processes, or mindset.

## REQUIREMENTS

```
R1. Change occurs at the individual level first. [MUST]
R2. All five elements (Awareness, Desire, Knowledge, Ability, Reinforcement) are necessary. [MUST]
R3. Barriers at any element block progress. [MUST]
R4. Reinforcement sustains the change. [MUST]
```

## OUTCOMES

Individuals adopt the change, leading to organisational results.

EMERGENT [SATISFIES: R4]  # collective adoption

---

## PROCESS — Formal

```
PROCESS FacilitateADKARChange (INPUT: change initiative; OUTPUT: adopted new behaviour)
  STATE
    awareness     [scope: individual; dir: read/write]
    desire        [scope: individual; dir: read/write]
    knowledge     [scope: individual; dir: read/write]
    ability       [scope: individual; dir: read/write]
    reinforcement [scope: org; dir: read/write]

  1. Build AWARENESS of why the change is needed. [LEADERSHIP, STAKEHOLDER]
  2. Generate DESIRE to participate and support the change. [MOTIVATIONAL, POWER]
  3. Provide KNOWLEDGE on how to change. [STRATEGIC]
  4. Develop ABILITY to implement the change. [ITERATE: training and practice]
  5. REINFORCEMENT to sustain the change. [REINFORCEMENT, CULTURAL]

  # EMERGENT [SATISFIES: R4]  # widespread, sustained adoption
```