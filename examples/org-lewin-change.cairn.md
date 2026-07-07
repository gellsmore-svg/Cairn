# Organisational: Lewin's 3-Stage Change Model

Cairn description of Kurt Lewin's foundational Unfreeze-Change-Refreeze model for organisational change.

## CONTEXT

- **Organisation**: Current equilibrium state.
- **Driving forces**: Pressures for change.
- **Restraining forces**: Resistance and inertia.
- **New state**: Desired future configuration.

## REQUIREMENTS

```
R1. Change requires unfreezing the status quo. [MUST]
R2. Movement to new state needs support and training. [MUST]
R3. New state must be refrozen to prevent regression. [MUST]
R4. Balance of forces determines success. [MUST]
```

## OUTCOMES

Organisation moves to and stabilizes in a new, more effective state.

EMERGENT [SATISFIES: R3]  # new equilibrium and behaviors

---

## PROCESS — Formal

```
PROCESS ManageChange (INPUT: need for transformation; OUTPUT: new stable state)
  STATE
    current_state [scope: org; dir: read/write]
    forces [scope: org; dir: read]

  1. UNFROZEN: Increase driving forces or decrease restraining forces to create motivation for change. [LEADERSHIP, STRATEGIC]
     STATE UPDATE: current_state ← disequilibrium
  2. CHANGE: Move the system to new level through new processes, training, and structures. [ITERATE]
     STATE UPDATE: current_state ← transition
  3. REFROZEN: Stabilize the new state via policies, culture, and reinforcement mechanisms. [REINFORCEMENT, CULTURAL]
     STATE UPDATE: current_state ← new equilibrium

  # EMERGENT [SATISFIES: R3]  # sustained new performance level
```

## PROCESS — Operator Profile

```
render-profile: operator

MANAGE CHANGE (LEWIN)
  Purpose: Shift the organisation from old to new stable state.
  Owner: Change leaders
  Assisted-by: Force field analysis, communication, training
  1. Unfreeze: show why change is needed
  2. Change: implement new ways of working
  3. Refreeze: lock in the gains
  Next: Monitor and maintain
```