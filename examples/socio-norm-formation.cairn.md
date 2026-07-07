# Sociological: Norm Formation and Enforcement

Cairn description of how social norms emerge, are maintained, and enforced in groups (from symbolic interactionism and functionalism).

## CONTEXT

- **Group**: Collection of individuals interacting regularly.
- **Norms**: Shared expectations for behavior.
- **Sanctions**: Rewards for conformity, punishments for deviance.

## REQUIREMENTS

```
R1. Norms emerge from repeated interactions and shared meanings. [MUST]
R2. Norms reduce uncertainty and coordinate behavior. [MUST]
R3. Enforcement maintains social order. [MUST]
R4. Norms can evolve or be challenged over time. [MUST]
```

## OUTCOMES

Stable patterns of behavior and group cohesion, or change when norms are contested.

EMERGENT [SOCIAL: social order or cultural shift]

---

## PROCESS — Formal

```
PROCESS NormFormation (INPUT: group interactions; OUTPUT: established and enforced norms)
  STATE
    norms [scope: group; dir: read/write]
    compliance [scope: group; dir: read/write]

  1. Repeated interactions produce behavioral patterns. [SOCIAL, SYMBOLIC]
  2. DECISION [ON: what becomes expected]
  3. INSTITUTIONALIZE through communication and modeling. [NORM]
  4. Enforce via positive/negative sanctions. [POWER]
  5. ITERATE monitoring and adjustment.
  6. EMERGENT [CULTURAL: internalized shared expectations]

  AWAIT [EVENT: deviance or external pressure; TIMEOUT: ongoing]
```

## PROCESS — Operator Profile

```
render-profile: group

FORM AND MAINTAIN NORMS
  Purpose: Create predictable social behavior in the group.
  Owner: Group members collectively
  Assisted-by: [SOCIAL] interaction, [POWER] sanctions
  1. Observe and repeat successful behaviors
  2. Communicate expectations
  3. Reward conformity, sanction deviation
  4. Adjust as group evolves
  Next: Socialize new members
```