# Organisational: Stakeholder Power Mapping and Engagement

Cairn description of stakeholder analysis and engagement processes in organisational strategy and change (power-interest grid, influence strategies).

## CONTEXT

- **Organisation**: Pursuing initiative or strategy.
- **Stakeholders**: Individuals or groups with interest or power.
- **Power and interest**: Key dimensions for mapping.

## REQUIREMENTS

```
R1. Identify all relevant stakeholders and their power/interest. [MUST]
R2. Prioritize engagement based on influence and impact. [MUST]
R3. Tailor strategies to different stakeholder types. [MUST]
R4. Monitor and adapt engagement over time. [MUST]
```

## OUTCOMES

Support secured, resistance minimized, and successful implementation.

EMERGENT [ORGANISATIONAL: aligned stakeholder coalition]

---

## PROCESS — Formal

```
PROCESS EngageStakeholders (INPUT: proposed initiative; OUTPUT: stakeholder support)
  STATE
    stakeholder_map [scope: org; dir: read/write]
    engagement_level [scope: org; dir: read/write]

  1. Identify stakeholders and assess power and interest. [POWER, STAKEHOLDER]
  2. Map on power-interest grid.
  3. DECISION [ON: engagement strategy per quadrant]
     high power/high interest: manage closely
     high power/low interest: keep satisfied
     low power/high interest: keep informed
     low power/low interest: monitor
  4. Execute tailored actions (communication, involvement, etc.).
  5. ITERATE monitoring and adjustment.
  6. EMERGENT [ORGANISATIONAL: sustained support and reduced opposition]
```

## PROCESS — Operator Profile

```
render-profile: executive

ENGAGE STAKEHOLDERS
  Purpose: Build necessary support for initiatives.
  Owner: Project/strategy leaders
  Assisted-by: [POWER] analysis, [STAKEHOLDER] communication
  1. Map who has power and interest
  2. Decide how to handle each group
  3. Communicate and involve appropriately
  4. Track and adapt
  Next: Maintain relationships
```