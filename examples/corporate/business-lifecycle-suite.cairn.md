# Corporate Business Lifecycle Suite

Worked Cairn examples for core corporate flows from idea intake through support.
These examples emphasize human decision load, augmentation, HCI touchpoints, and
behavioural-economic risks.

## PROCESS — Idea Intake And Evaluation

```cairn
PROCESS CorporateIdeaIntake (INPUT: idea_submission; OUTPUT: funded_or_rejected_concept)
  1. Capture the idea with customer, problem, evidence, and strategic fit. [UI, HUMAN]
     PURPOSE: make the idea legible without forcing a business case too early.
     HUMAN_DEMAND:
       ORIENT: understand why the idea matters and who is affected.
       ACT: provide evidence, assumptions, and uncertainty.
       CLOSE: know whether the idea is queued, rejected, or needs discovery.
     HUMAN_FACTORS:
       behavioural_economics: status quo bias and seniority halo can suppress weak-signal innovation.
       cognitive_load: submitters may overfit to template language rather than customer evidence.
     SUPPORT: separate required evidence from optional polish; allow low-fidelity submissions.

  2. Cluster similar ideas and detect duplicates. [CODE, ASSISTED-BY: LLM]
     AUGMENTATION_PROCESS:
       role_complementarity: AI clusters semantic similarity; humans judge strategic meaning.
       trust_calibration: show candidate duplicates with evidence, not a single verdict.
     HUMAN_RISK:
       probability: medium
       impact: medium
       confidence: medium
       rationale: over-trusting clustering can bury novel variations.

  3. Review value, risk, learning potential, and reversibility. [HUMAN, GATED]
     HUMAN_DEMAND:
       ORIENT: compare value evidence, uncertainty, cost, and opportunity cost.
       ACT: select fund, discover, defer, merge, or reject.
       CLOSE: publish a reason that is useful to the submitter.
     HUMAN_FACTORS:
       social_role: politics can turn evaluation into reputation protection.
       incentives_game_theory: departments may inflate benefits to win scarce capacity.
     SUPPORT: require explicit uncertainty and reversible next experiment before funding.

  4. Notify submitter and route funded concepts into discovery. [CODE, UI, ASYNC]
     HCI_TOUCHPOINT:
       phase: feedback
       human_goal: understand the decision and next opportunity for action.
     SUPPORT: include decision, rationale, evidence gaps, owner, and next review date.
```

## PROCESS — Concept To MVP

```cairn
PROCESS ConceptToMVP (INPUT: funded_concept; OUTPUT: tested_mvp_decision)
  1. Define the smallest customer-learning outcome. [HUMAN, COLLABORATIVE]
     HUMAN_FACTORS:
       cognitive_load: teams confuse deliverables with learning goals.
       behavioural_economics: sunk-cost pressure begins once a named project exists.
     SUPPORT: write one falsifiable learning question before scope is estimated.

  2. Build experiment plan, risk guardrails, and user touchpoints. [HUMAN, ASSISTED-BY: LLM]
     AUGMENTATION_PROCESS:
       interaction_richness: AI helps draft variants; product owner selects what is ethically testable.
       bias_mitigation: check whether proposed users exclude low-power or high-friction groups.
     HCI_TOUCHPOINT:
       phase: orientation
       human_goal: understand the experiment without confusing it with a committed product.

  3. Deliver MVP slice and collect evidence. [CODE, ITERATIVE, ASSISTED-BY: product team]
     HUMAN_DEMAND:
       ACT: build, test, observe, and repair.
       RECOVER: stop the experiment if harm, confusion, or unusable evidence appears.
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: medium
       rationale: MVP pressure can turn uncertainty into premature commitment.

  4. Decide persevere, pivot, pause, or stop. [HUMAN, GATED]
     HUMAN_FACTORS:
       behavioural_economics: loss aversion can keep weak MVPs alive.
       social_role: public sponsorship can make stopping feel like failure.
     SUPPORT: separate learning success from product success in the decision record.
```

## PROCESS — Lead To Opportunity

```cairn
PROCESS LeadToOpportunity (INPUT: inbound_lead; OUTPUT: qualified_opportunity)
  1. Capture lead source, need, consent, and urgency. [UI, CODE]
     HCI_TOUCHPOINT:
       phase: awareness
       ui_surface: CRM lead intake
       human_goal: see whether the lead needs fast action or nurture.

  2. Score fit and buying intent. [ASSISTED-BY: LLM, STOCHASTIC]
     AUGMENTATION_PROCESS:
       trust_calibration: AI score must expose evidence and missing information.
       automation_bias: do not hide low-scoring strategic accounts.
     HUMAN_FACTORS:
       behavioural_economics: salience bias may overweight recent campaigns.

  3. Sales development representative qualifies or rejects. [HUMAN, GATED]
     HUMAN_DEMAND:
       ORIENT: understand account, contact, need, consent, and score rationale.
       ACT: call, email, research, qualify, reject, or route.
       CLOSE: see CRM state and next owner.
     SUPPORT: keep evidence, script, objection notes, and next action in one decision region.

  4. Convert to opportunity with next step and forecast category. [SIDE-EFFECT, UI]
     HUMAN_RISK:
       probability: medium
       impact: medium
       confidence: medium
       rationale: optimistic qualification pollutes pipeline and forecasts.
```

## PROCESS — Quote To Order

```cairn
PROCESS QuoteToOrder (INPUT: approved_quote; OUTPUT: accepted_order_or_exception)
  1. Present quote, customer terms, margin, and approval history. [UI, HUMAN]
     FUNCTIONAL_LAYOUT_LOAD:
       evidence_action_distance: high if price exceptions are far from submit/approve actions.
       label_field_distance: medium when quote fields use dense tables with weak labels.
     SUPPORT: put price, margin, exception, and approval action in one visual decision panel.

  2. Detect commercial and fulfilment exceptions. [CODE, ASSISTED-BY: LLM]
     AUGMENTATION_PROCESS:
       role_complementarity: rules detect hard exceptions; AI summarizes ambiguous customer language.
       trust_calibration: mark suggestions as evidence summaries, not approvals.

  3. Human approves, repairs, or escalates. [HUMAN, GATED]
     HUMAN_FACTORS:
       incentives_game_theory: sales pressure may compete with margin and delivery risk.
       social_role: approver carries accountability across sales, finance, and operations.
     HUMAN_RISK:
       probability: high
       impact: high
       confidence: medium
       rationale: quote decisions bind price, delivery promises, and customer expectations.

  4. Convert accepted quote to order and notify downstream teams. [CODE, ASYNC]
     HCI_TOUCHPOINT:
       phase: handoff
       human_goal: know which team owns fulfilment, finance, and customer confirmation.
```

## PROCESS — Order To Cash Exception

```cairn
PROCESS OrderToCashException (INPUT: invoice_or_payment_exception; OUTPUT: resolved_cash_state)
  1. Detect mismatch between order, invoice, payment, and customer remittance. [CODE, DETERMINISTIC]
     OUTPUT: cash_exception_case

  2. Show exception queue with value, age, customer, and cause. [UI, HUMAN]
     HUMAN_DEMAND:
       ORIENT: prioritize by materiality, due date, customer risk, and evidence completeness.
       ACT: open, assign, defer, or escalate.
       CLOSE: know whether action is taken or safely queued.
     HUMAN_FACTORS:
       cognitive_load: financial exception queues combine vigilance, comparison, and time pressure.

  3. Reconcile evidence and choose resolution path. [HUMAN, ASSISTED-BY: LLM, GATED]
     AUGMENTATION_PROCESS:
       role_complementarity: AI summarizes remittance and likely cause; human decides accounting action.
       automation_bias: require human verification of customer-specific terms before write-off or credit.
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: medium
       rationale: errors affect revenue, customer trust, and audit trail.

  4. Post correction, collect payment, dispute, or escalate. [SIDE-EFFECT]
     SUPPORT: show downstream accounting entry, customer message, owner, and audit reason.
```

## PROCESS — Support Escalation And Retention

```cairn
PROCESS SupportEscalationRetention (INPUT: high_risk_support_ticket; OUTPUT: retained_or_escalated_customer)
  1. Classify ticket severity, sentiment, product area, and customer value. [ASSISTED-BY: LLM]
     AUGMENTATION_PROCESS:
       bias_mitigation: sentiment and customer value must not hide safety, accessibility, or fairness issues.
       trust_calibration: show excerpts behind sentiment and escalation recommendations.

  2. Route to support, engineering, customer success, or incident command. [CODE, ASSISTED-BY: support lead]
     HUMAN_FACTORS:
       social_role: handoffs can create ownership diffusion.
       cognitive_load: agent must integrate emotion, technical detail, SLA, and relationship risk.
     SUPPORT: make owner, next action, customer promise, and escalation path explicit.

  3. Resolve issue and communicate evidence-backed response. [HUMAN, ASSISTED-BY: LLM]
     HCI_TOUCHPOINT:
       phase: execution
       human_goal: craft a response that is accurate, empathic, and auditable.
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: medium
       rationale: poor response quality can turn a technical issue into churn or reputation loss.

  4. Review retention signal and feed product learning. [HUMAN, ASYNC]
     CHANGE_IMPACT:
       role_shift: support becomes a learning sensor, not only a ticket closer.
       reinforcement: show reduced repeat tickets and better customer outcomes.
```
