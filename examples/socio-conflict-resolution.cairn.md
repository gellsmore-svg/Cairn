# Sociological: Conflict and Resolution in Groups

Cairn description of social conflict processes (from conflict theory and interactionism) and pathways to resolution or escalation.

## CONTEXT

- **Groups or parties**: Competing for resources, status, or power.
- **Conflict**: Perceived incompatibility of actions, goals, or ideas.
- **Social structures**: Norms, power relations, institutions.

## REQUIREMENTS

```
R1. Conflict is a normal part of social interaction. [MUST]
R2. Unresolved conflict can lead to escalation or structural change. [MUST]
R3. Resolution often involves accommodation, negotiation, or power shifts. [MUST]
R4. Positive conflict can drive innovation and adaptation. [SHOULD]
```

## OUTCOMES

Either reinforced divisions, new alliances, or transformed social structures.

EMERGENT [SOCIAL: changed power balance or new norms]

---

## PROCESS — Formal

```
PROCESS GroupConflict (INPUT: competing interests; OUTPUT: resolution or new state)
  STATE
    conflict_level [scope: group; dir: read/write]
    power_relations [scope: group; dir: read/write]

  1. Identify incompatible goals or resources. [POWER, SOCIAL]
  2. Escalate through actions and rhetoric.
  3. DECISION [ON: path]
     accommodation: adjust positions
     negotiation: seek compromise
     domination: use power to impose
  4. Apply resolution strategy. [ITERATE]
  5. STATE UPDATE: new equilibrium or ongoing tension.
  6. EMERGENT [SOCIAL: structural change or reinforced status quo]

  AWAIT [EVENT: new conflict trigger; TIMEOUT: variable]
```

## PROCESS — Operator Profile

```
render-profile: group

HANDLE GROUP CONFLICT
  Purpose: Manage competing interests to reach workable outcome.
  Owner: Group leaders or mediators
  Assisted-by: [POWER] negotiation, [SOCIAL] norms
  1. Surface the real issues
  2. Explore options (compromise, collaboration, avoidance)
  3. Agree on resolution
  4. Implement and monitor
  Next: Institutionalize if successful
```