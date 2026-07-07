# Sociological: Social Movements and Collective Action

Cairn description of social movement processes (resource mobilization, framing, political opportunity) leading to social change.

## CONTEXT

- **Grievance group**: Shared discontent.
- **Mobilizing structures**: Organizations, networks.
- **Framing**: Collective action frames.
- **Opportunity structures**: Political and social openings.

## REQUIREMENTS

```
R1. Grievances alone do not produce movements. [MUST]
R2. Resource mobilization and organization are necessary. [MUST]
R3. Framing processes create shared identity and urgency. [MUST]
R4. Political opportunities enable action. [MUST]
R5. Cycles of protest and abeyance. [MUST]
```

## OUTCOMES

Social change, new policies, cultural shifts, or movement decline/co-optation.

EMERGENT [SOCIAL: transformed institutions or norms]

---

## PROCESS — Formal

```
PROCESS SocialMovement (INPUT: structural grievance; OUTPUT: social change or decline)
  STATE
    resources     [scope: group; dir: read/write]  ref: S1
    frames        [scope: group; dir: read/write]  ref: S2
    opportunities [scope: society; dir: read]  ref: S3

  1. Frame grievances as injustice and actionable. [SYMBOLIC, SOCIAL]
  2. MOBILIZE resources and build organizations. [GROUP, POWER]
  3. Exploit political opportunities.
  4. ITERATE collective action (protests, campaigns).
  5. DECISION [ON: outcomes]
     success → institutionalization
     failure → abeyance or decline
  6. EMERGENT [SOCIAL: policy change, cultural shift, or backlash]

  AWAIT [EVENT: new opportunities or repression; TIMEOUT: cyclical]
```

## PROCESS — Operator Profile

```
render-profile: group

BUILD SOCIAL MOVEMENT
  Purpose: Convert grievance into sustained collective action and change.
  Owner: Movement leaders and organizations
  Assisted-by: [SOCIAL] framing, [POWER] mobilization
  1. Frame the issue
  2. Organize resources and people
  3. Seize opportunities
  4. Sustain action and adapt
  Next: Institutionalize gains or cycle to next wave
```