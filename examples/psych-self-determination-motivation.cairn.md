# Psychological: Self-Determination Theory Motivation Process

Cairn description of Deci & Ryan's Self-Determination Theory (SDT) as process of intrinsic vs extrinsic motivation and basic psychological needs satisfaction.

## CONTEXT

- **Individual**: With innate psychological needs.
- **Environment**: Social context supporting or thwarting needs.
- **Motivation**: Continuum from amotivation to intrinsic.

## REQUIREMENTS

```
R1. Three basic needs: autonomy, competence, relatedness. [MUST]
R2. Need satisfaction leads to intrinsic motivation and well-being. [MUST]
R3. Controlling environments lead to extrinsic motivation or amotivation. [MUST]
R4. Internalization process moves extrinsic toward intrinsic. [MUST]
```

## OUTCOMES

Autonomous motivation, enhanced performance, persistence, and psychological health.

EMERGENT [PSYCHOLOGICAL: integrated self-regulation and vitality]

---

## PROCESS — Formal

```
PROCESS SelfDetermineMotivation (INPUT: activity/context; OUTPUT: motivated engagement)
  STATE
    needs_satisfaction [scope: individual; dir: read/write]
    motivation_type [scope: individual; dir: read/write]

  1. APPRAISAL of environment support for autonomy/competence/relatedness. [APPRAISAL, EMOTIONAL]
  2. DECISION [ON: motivation locus]
     supportive → intrinsic motivation
     controlling → extrinsic or amotivation
  3. ITERATE [REGULATION: internalization of extrinsic motives]
  4. STATE UPDATE: needs_satisfaction ↑ → motivation_type shifts toward autonomous
  5. EMERGENT [PSYCHOLOGICAL: enhanced engagement, persistence, well-being]

  AWAIT [EVENT: need thwarting or support; TIMEOUT: ongoing]
```

## PROCESS — Operator Profile

```
render-profile: operator

SUPPORT AUTONOMOUS MOTIVATION (SDT)
  Purpose: Foster intrinsic drive through need satisfaction.
  Owner: Facilitator (teacher, manager, therapist)
  Assisted-by: [MOTIVATIONAL] structure, [EMOTIONAL] warmth
  1. Provide meaningful choices (autonomy)
  2. Offer optimal challenges and feedback (competence)
  3. Build connections (relatedness)
  4. Support internalization
  Next: Monitor vitality and persistence
```