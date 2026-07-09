# Sociological Work Interface Suite

Examples for group dynamics, informal systems, and domestic/work interfaces.

## PROCESS — Meeting Power And Status Dynamics

```cairn
PROCESS MeetingPowerStatusDynamics (INPUT: decision_meeting; OUTPUT: legitimate_or_captured_decision)
  1. Establish agenda, roles, and decision rule. [HUMAN, SOCIAL]
     HUMAN_FACTORS:
       power_distance: high-status speakers can set frames before evidence is reviewed.
       social_proof: early agreement can suppress dissent.

  2. Surface evidence and minority views. [HUMAN, GATED]
     SUPPORT: use pre-reads, round-robin input, anonymous concerns, and explicit dissent capture.

  3. Decide and record rationale. [DECISION, SIDE-EFFECT]
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: medium
       rationale: captured decisions appear aligned while hiding unspoken risk.

  4. Review whether dissent was heard and acted on. [FEEDBACK]
```

## PROCESS — Informal Reputation And Gossip Flow

```cairn
PROCESS InformalReputationFlow (INPUT: ambiguous_event; OUTPUT: corrected_or_distorted_reputation)
  1. Ambiguous event is interpreted by witnesses. [SOCIAL, SYMBOLIC]
     HUMAN_FACTORS:
       attribution_bias: people infer character from limited behaviour.
       status: reputation effects differ by role power and group membership.

  2. Story spreads through informal channels. [ASYNC, SOCIAL]
     GAME_THEORY:
       pattern: sharing inside information can create status rewards.
       mitigation: provide official, fair, privacy-respecting clarification routes.

  3. Individual or manager responds. [HUMAN, GATED]
     SUPPORT: separate facts, impact, privacy, and repair path.

  4. Norms either reinforce gossip or shift toward accountable feedback. [EMERGENT]
```

## PROCESS — Inclusion And Belonging In Hybrid Work

```cairn
PROCESS HybridBelongingProcess (INPUT: hybrid_team_interactions; OUTPUT: inclusion_or_exclusion_pattern)
  1. Work interactions occur across office, video, chat, and asynchronous tools. [SOCIAL, UI]
     HCI_TOUCHPOINT:
       phase: awareness
       human_goal: know where decisions and relationship signals happen.
     HUMAN_FACTORS:
       social_presence: remote members may miss informal context and status cues.

  2. Norms form around who gets attention and information. [SOCIALIZE, EMERGENT]
     HUMAN_RISK:
       probability: medium
       impact: medium
       confidence: medium
       rationale: belonging affects retention, voice, and decision quality.

  3. Design inclusive rituals and information defaults. [HUMAN, SUPPORT]
     SUPPORT: decision logs, rotating facilitation, async-first updates, and explicit informal onboarding.

  4. Review participation patterns without reducing people to metrics. [FEEDBACK]
```

## PROCESS — Domestic Stress And Work Boundary Negotiation

```cairn
PROCESS DomesticStressWorkBoundary (INPUT: domestic_stress_and_work_expectations; OUTPUT: negotiated_or_failed_boundary)
  1. Domestic demands collide with work schedule or cognitive load. [HUMAN, CONTEXT]
     HUMAN_FACTORS:
       spillover: strain can move across home and work systems.
       social_norm: employees may hide domestic strain to preserve professional identity.

  2. Employee chooses disclose, compensate, withdraw, or request support. [HUMAN, DECISION]
     GAME_THEORY:
       pattern: if support requests are punished, concealment becomes rational.
       mitigation: make support routes predictable and non-stigmatizing.

  3. Manager negotiates boundary and coverage. [HUMAN, SUPPORT]
     SUPPORT: clarify priority, deadline, coverage, and confidentiality.

  4. Team adjusts work design and norms. [SOCIALIZE, FEEDBACK]
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: medium
       rationale: unmanaged boundary conflict can become burnout, quality loss, or attrition.
```
