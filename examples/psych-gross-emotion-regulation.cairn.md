# Psychological: Gross Process Model of Emotion Regulation

Detailed Cairn description of James Gross's Process Model of Emotion Regulation.

This models the five families of strategies individuals use to influence which emotions they have, when they have them, and how they experience and express them.

## CONTEXT

- **Individual**: The person experiencing and regulating emotions.
- **Situation**: External or internal trigger.
- **Emotion**: Multi-component response (experiential, behavioral, physiological).
- **Goals**: Hedonic (feel better), instrumental (achieve goal), eudaimonic (value-aligned).

## REQUIREMENTS

```
R1. Regulation can occur at multiple points in the emotion generative process. [MUST]
R2. Antecedent-focused strategies are generally more effective than response-focused for changing experience. [SHOULD]
R3. Choice of strategy depends on goals, context, and individual differences. [MUST]
R4. Over-use of certain strategies (e.g., chronic suppression) can have costs. [MUST]
```

## OUTCOMES

The individual achieves a modulated emotional response aligned with goals, or experiences costs from poor regulation.

---

## PROCESS — Formal

```
PROCESS RegulateEmotion (INPUT: triggering situation; OUTPUT: modulated emotional response)
  1. APPRAISAL of the situation (primary: relevance; secondary: coping options). [COGNITIVE, APPRAISAL, EMOTIONAL]
  2. DECISION [ON: whether and how to regulate]
     based on goals and context.
  3. REGULATION [STRATEGY: situation_selection | situation_modification | attentional_deployment | cognitive_change | response_modulation]
     [TARGET: attention | cognition | response]
     [GOAL: hedonic | instrumental | eudaimonic]
  4. EMERGENT [SATISFIES: R3]  # changed emotional state or new insight

  ITERATE [UNTIL: goal achieved or situation ends]
```

## PROCESS — Operator Profile

```
render-profile: operator

REGULATE EMOTION
  Purpose: Modify emotional response to better align with goals.
  Owner: Individual
  Assisted-by: [EMOTIONAL] [COGNITIVE] processes, sometimes [SOCIAL] support
  Steps:
  - Appraise situation
  - Choose strategy (e.g., reappraise the meaning)
  - Apply regulation
  - Observe outcome
  Next: Adjust or iterate based on results
```