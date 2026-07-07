# Psychological: Operant Conditioning and Reinforcement

Cairn description of Skinner's operant conditioning as a psychological process of learning through consequences.

## CONTEXT

- **Organism**: The learner (human or animal in behavioral psych).
- **Behavior**: Operant response.
- **Consequences**: Reinforcement (positive/negative) or punishment.
- **Environment**: Discriminative stimuli.

## REQUIREMENTS

```
R1. Behavior is shaped by its consequences. [MUST]
R2. Positive reinforcement increases behavior. [MUST]
R3. Schedules of reinforcement affect persistence. [MUST]
R4. Extinction occurs when reinforcement stops. [MUST]
```

## OUTCOMES

Learned behavior patterns, strengthened or weakened based on contingencies.

EMERGENT [PSYCHOLOGICAL: acquired habits or skills]

---

## PROCESS — Formal

```
PROCESS OperantConditioning (INPUT: behavior in context; OUTPUT: learned response pattern)
  STATE
    behavior_rate [scope: individual; dir: read/write]
    reinforcement_history [scope: individual; dir: read]

  1. BEHAVIORAL Emit behavior in presence of discriminative stimulus. [BEHAVIORAL]
  2. REGULATION [STRATEGY: consequence] CONSEQUENCE: reinforcement or punishment delivered. [REGULATION]
     POSITIVE_REINFORCEMENT: increase behavior
     NEGATIVE_REINFORCEMENT: increase by removal
     PUNISHMENT: decrease
  3. ITERATE [SCHEDULE: continuous | fixed-ratio | variable-interval]
  4. STATE UPDATE: behavior_rate adjusted
  5. EMERGENT [PSYCHOLOGICAL: stable operant response or extinction]

  AWAIT [EVENT: schedule change or extinction; TIMEOUT: variable]
```

## PROCESS — Operator Profile

```
render-profile: operator

SHAPE BEHAVIOR (OPERANT)
  Purpose: Increase or decrease specific behaviors via consequences.
  Owner: Behavior modifier (therapist, parent, manager)
  Assisted-by: [BEHAVIORAL] contingencies, [COGNITIVE] awareness if human
  1. Identify target behavior and baseline
  2. Arrange reinforcement schedule
  3. Deliver consistently
  4. Monitor and adjust
  Next: Fade to maintenance or extinguish
```