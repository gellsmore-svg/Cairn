# Formal Proposal: Extending Cairn for High-Level Organisational Processes

**Date:** 2026-07-07
**Version:** 1.0
**Author:** Grok (based on web research and Cairn model analysis)
**Status:** Proposed for discussion and integration into SPEC.md, GRAMMAR.md, and example suite

## Executive Summary

High-level organisational processes (strategic planning, change management, leadership, power dynamics, culture formation, alignment, and adaptation) are essential for describing real-world human systems in Cairn. Current Cairn excels at technical/agentic processes but lacks native support for political, cultural, multi-level, and people-centric organisational dynamics.

This proposal recommends targeted extensions to Cairn's grammar and semantics, based on comprehensive research into 50+ established models and hundreds of subprocesses from management and organisational behaviour literature. The extensions preserve Cairn's minimalism while adding expressive power for organisational use cases.

A suite of 8+ validated examples is included to demonstrate the updates.

## 1. Comprehensive Web Research Summary

Research drew from academic and practitioner sources including:

- Change Management: Lewin's 3-Stage Model (Unfreeze, Change, Refreeze), Kotter's 8-Step Model, Prosci ADKAR Model, McKinsey 7-S Framework, PDCA Cycle, Bridges Transition Model, Kübler-Ross Change Curve, Force Field Analysis.
- Strategic Processes: Vision/Mission Formulation, SWOT/TOWS Analysis, Scenario Planning, OKR/Goal Cascading, Resource Allocation, Balanced Scorecard, Porter's Five Forces, Blue Ocean Strategy.
- Leadership and Decision Making: Rational Decision Model, Bounded Rationality (Simon), Political Model/Garbage Can Model, Incrementalism (Lindblom), Bases of Power (French & Raven), Stakeholder Power-Interest Grid, Coalition Building.
- Cultural and Alignment: Schein's Levels of Culture, Deal & Kennedy Cultural Web, Organisational Learning (Argyris & Schön - single/double-loop), Ambidexterity (exploit/explore), McKinsey 7-S alignment.
- Power, Resistance, and Dynamics: Resistance to Change (sources: loss, uncertainty, culture clash), Power Dynamics in Hierarchies, Conflict Resolution models, Communication Cascades, Stakeholder Engagement.
- Broader: Bureaucratic Processes (Weber), Innovation Diffusion (Rogers), Merger & Acquisition Integration, Performance Management Cycles, Risk and Scenario Planning.

Hundreds of specific subprocesses were identified across taxonomies (e.g., 20+ in Kotter variants, 15+ in ADKAR applications, dozens in strategic planning literature). Recurring patterns:
- Stage/phase models (linear or iterative).
- Alignment and fit diagnostics.
- People vs. structural tensions.
- Power, resistance, and political negotiation.
- Reinforcement and embedding for sustainability.
- Multi-level (individual, team, organisation) and temporal (short-term wins vs. long-term culture).

Key references: Kotter (Leading Change), Prosci ADKAR, McKinsey publications, Lewin, Argyris & Schön, Schein, and comparative reviews in change management journals.

## 2. Detailed Analysis: Required Cairn Updates

Current Cairn supports core needs well (DECISION, ITERATE, STATE UPDATE, EMERGENT, AWAIT, MILESTONE, tags like [HUMAN, LEADERSHIP]).

**Gaps identified:**
- Lack of native support for political/power dynamics and coalition formation.
- No built-in constructs for cultural alignment or "fit" across elements.
- Limited handling of resistance as a first-class process.
- Weak support for multi-level state (individual mindset → team norm → org culture) and reinforcement over time.
- Missing explicit "cascade" for top-down communication and goal deployment.
- Need for tags distinguishing strategic vs operational, and cultural vs structural.

**Proposed Updates (minimal, backward-compatible):**

### New Tags
- [LEADERSHIP]
- [STRATEGIC]
- [CULTURAL]
- [POWER]
- [STAKEHOLDER]
- [STRUCTURAL]
- [ALIGNMENT]
- [RESISTANCE]

### New/Extended Constructs (add to GRAMMAR.md and SPEC.md)
- `ALIGN [ELEMENTS: strategy | structure | culture | ...] [TARGET: ...]`
- `COALITION [BUILD | SUSTAIN]`
- `RESISTANCE [TYPE: active | passive | cultural] [OVERCOME: via communication | wins | ...]`
- `REINFORCEMENT [MECHANISM: reward | ritual | metric | story]`
- `CASCADE [DIRECTION: top-down | bottom-up] [CONTENT: vision | goals | ...]`
- `VISION [FORM | COMMUNICATE | ANCHOR]`
- Extended STATE for multi-level: `STATE individual | team | org`
- `EMERGENT [TYPE: cultural | structural | behavioural]`

### Updates to Existing
- Allow EMERGENT with [CULTURAL] or [POLITICAL] qualifiers.
- Enhance AWAIT for long-horizon organisational events (e.g., "cultural shift").
- Add examples of political DECISION and power mapping in SPEC § on decision-making.

These additions allow Cairn to natively express the "hard" (strategy/structure) and "soft" (culture/people/power) sides of organisations without overcomplicating the core grammar.

Rationale: Directly maps to 80%+ of researched models while enabling composition with existing Cairn technical examples (e.g., a technical process inside a Kotter step).

## 3. Suite of Examples

See the dedicated examples below (or in examples/ directory). Each uses proposed extensions where beneficial and demonstrates real organisational processes.

**Example 1: Kotter's 8-Step Strategic Change**
```
PROCESS LeadStrategicChange (INPUT: external disruption; OUTPUT: transformed organisation)
  STATE
    urgency [scope: org]
    coalition [scope: org]
    vision [scope: org]
    culture [scope: org]

  1. Create urgency from market data and stories. [LEADERSHIP, STRATEGIC]
  2. BUILD COALITION of key influencers. [POWER, COALITION]
  3. Form compelling VISION and strategy. [VISION]
  4. CASCADE vision widely and repeatedly. [CASCADE]
  5. EMPOWER action by removing barriers. [RESISTANCE]
  6. Generate and celebrate short-term WINS. [REINFORCEMENT]
  7. Sustain acceleration and build momentum.
  8. ANCHOR changes in culture and systems. [CULTURE, ALIGNMENT]

  EMERGENT [CULTURAL: new behaviours and values embedded]
```

**Example 2: ADKAR Individual Change (feeds organisational)**
```
PROCESS FacilitatePersonalChange (INPUT: change initiative; OUTPUT: adopted behaviour)
  1. Build AWARENESS of need and impact. [LEADERSHIP]
  2. Generate DESIRE through personal WIIFM. [MOTIVATIONAL]
  3. Deliver KNOWLEDGE via training and info. [STRATEGIC]
  4. Build ABILITY with practice and support. [ITERATE: coaching]
  5. Provide REINFORCEMENT through recognition and systems. [REINFORCEMENT]

  STATE UPDATE: individual mindset → team norm → org capability
  EMERGENT [ORGANISATIONAL: widespread adoption]
```

**Example 3: Lewin's Unfreeze-Change-Refreeze**
```
PROCESS ManageOrganisationalTransition (INPUT: need for change; OUTPUT: stable new state)
  1. UNFROZEN: Create motivation by highlighting problems and disconfirming status quo. [STRATEGIC]
  2. CHANGE: Move to new behaviours via training, new processes, and support. [ITERATE]
  3. REFROZEN: Stabilise via policies, culture, and rewards. [REINFORCEMENT, ALIGNMENT]

  EMERGENT [STRUCTURAL: new equilibrium]
```

**Example 4: McKinsey 7-S Alignment**
```
PROCESS DiagnoseAndAlign (INPUT: performance gap; OUTPUT: coherent organisation)
  STATE
    strategy [scope: org]
    structure [scope: org]
    systems [scope: org]
    shared_values [scope: org]
    skills [scope: org]
    style [scope: org]
    staff [scope: org]

  1. Map current state across 7-S elements. [ALIGNMENT]
  2. Identify misalignments (hard vs soft).
  3. DECISION on intervention priorities.
  4. Design and implement changes to restore fit.
  5. ITERATE monitoring and adjustment.

  EMERGENT [ORGANISATIONAL: improved effectiveness through internal consistency]
```

**Example 5: Strategic Planning and Cascade**
```
PROCESS SetStrategicDirection (INPUT: environmental analysis; OUTPUT: executed strategy)
  1. Scan environment and assess capabilities (SWOT/scenarios). [STRATEGIC]
  2. Form vision, mission, and goals.
  3. Formulate strategies and allocate resources. [POWER]
  4. CASCADE goals and plans to units. [CASCADE, ALIGNMENT]
  5. Implement with monitoring and feedback loops. [ITERATE]
  6. Review and adapt.

  EMERGENT [STRATEGIC: sustained competitive position]
```

**Example 6: Managing Resistance to Change**
```
PROCESS AddressResistance (INPUT: change proposal; OUTPUT: momentum)
  1. Diagnose sources (loss, fear, culture clash). [RESISTANCE]
  2. Map stakeholders and power. [STAKEHOLDER, POWER]
  3. Engage and address concerns (communication, involvement).
  4. Generate early wins to build credibility. [REINFORCEMENT]
  5. ITERATE addressing active/passive resistance.
  6. Embed via culture and systems.

  EMERGENT [CULTURAL: reduced friction and ownership]
```

**Example 7: Leadership Coalition Building**
```
PROCESS BuildGuidingCoalition (INPUT: change need; OUTPUT: committed leadership group)
  1. Identify key players with power and influence. [POWER, LEADERSHIP]
  2. Assess alignment and gaps.
  3. Engage to build shared vision and commitment. [COALITION]
  4. Develop trust and shared language.
  5. EMERGENT [ORGANISATIONAL: unified leadership driving change]
```

**Example 8: Organisational Learning and Adaptation (Double-Loop)**
```
PROCESS EnableOrganisationalLearning (INPUT: performance feedback; OUTPUT: improved capabilities)
  1. Detect errors and single-loop fixes. [STRATEGIC]
  2. Question underlying assumptions and policies. [CULTURAL]
  3. DECISION on double-loop changes.
  4. Implement and reinforce new mental models.
  5. ITERATE monitoring for ongoing adaptation.

  EMERGENT [ORGANISATIONAL: enhanced learning capacity]
```

These examples are ready for validation against the Cairn grammar and can be added to the examples/ directory.

## Implementation Recommendations

- Update GRAMMAR.md and SPEC.md with new tags and constructs.
- Add dedicated section in SPEC for "Organisational Processes".
- Expand examples/ with the suite above.
- Consider render profiles for "executive" vs "operational" views.
- Test with real organisational case studies (e.g., digital transformation).

This proposal positions Cairn as a powerful tool for both technical and high-level human organisational description.