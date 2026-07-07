# Psychological: Metacognition and Self-Regulated Learning

Cairn description of metacognitive processes (monitoring and control of one's own thinking) in learning or problem-solving.

## CONTEXT

- **Individual**: Engaged in cognitive task (learning, problem solving).
- **Cognition**: The thinking processes being monitored.
- **Metacognition**: Knowledge and regulation of cognition.

## REQUIREMENTS

```
R1. Metacognition involves monitoring one's own cognitive processes. [MUST]
R2. Control strategies adjust behavior based on monitoring. [MUST]
R3. Effective metacognition improves learning outcomes. [MUST]
R4. Deficits lead to poor self-assessment and persistence on wrong paths. [MUST]
```

## OUTCOMES

Improved performance through better strategy selection and adjustment.

EMERGENT [PSYCHOLOGICAL: enhanced self-awareness and learning efficiency]

---

## PROCESS — Formal

```
PROCESS MetacognitiveRegulation (INPUT: cognitive task; OUTPUT: completed task with learning)
  STATE
    task_knowledge [scope: individual; dir: read/write]
    monitoring [scope: individual; dir: read/write]
    strategies [scope: individual; dir: read/write]

  1. METACOGNITION Plan approach to task. [METACOGNITIVE, COGNITIVE]
  2. METACOGNITION Monitor progress and comprehension during execution. [METACOGNITIVE]
  3. DECISION [ON: strategy adjustment]
     if stuck: change approach
     if successful: continue
  4. REGULATION [STRATEGY: evaluate] Evaluate outcome and reflect. [REGULATION]
  5. STATE UPDATE: updated strategies and self-knowledge.
  6. EMERGENT [PSYCHOLOGICAL: better future performance]

  ITERATE throughout the task.
```

## PROCESS — Operator Profile

```
render-profile: operator

USE METACOGNITION
  Purpose: Think about and improve one's own thinking.
  Owner: Individual learner/problem solver
  Assisted-by: [COGNITIVE] awareness and [REGULATION] control
  1. Plan: choose strategy
  2. Monitor: check if working
  3. Adjust: switch if needed
  4. Evaluate: learn for next time
  Next: Apply insights
```