# Accounts Payable Exception Review

```cairn
CONTEXT
Invoice exception - an invoice whose amount, supplier, receipt, approval, or purchase order record does not match payment policy.
AP clerk - the finance operator who owns first-line review and records the decision.
AI summary - an LLM-assisted explanation of the mismatch, with links to source evidence.

REQUIREMENTS
R1. A clerk must see the source invoice, purchase order, receipt status, and policy reason before approving payment. [MUST]
R2. AI-generated recommendations must expose uncertainty and source disagreement. [MUST]
R3. The case must leave a clear audit trail: decision, reason, evidence viewed, and escalation if any. [MUST]

OUTCOMES
The clerk can resolve routine exceptions without hidden cognitive overload.
High-risk or under-evidenced cases are escalated rather than rubber-stamped.
Repeated exceptions produce learning for finance operations and supplier management.

PROCESS ResolveInvoiceException (INPUT: invoice_case; OUTPUT: exception_outcome)
  1. Detect that an invoice does not match purchase order records. [CODE, DETERMINISTIC, SYNC]
     PURPOSE: create a review case only when payment cannot safely proceed automatically.
     OUTPUT: exception_case

  2. Notify the AP clerk that the exception needs review. [CODE, ASYNC]
     PURPOSE: bring one specific unresolved payment issue into awareness.
     HUMAN_DEMAND:
       ORIENT: notice the queue item and understand why this invoice needs attention.
       ACT: decide whether to open it now or leave it in the queue.
       CLOSE: see that the item has moved into active review.
       RECOVER: defer low-urgency items without losing the reason they matter.
     HUMAN_LOAD:
       focus_actions: 2
       business_actions: 1
       trivial_actions: 1
       context_switches: 1
       urgency_load: medium when due date is close
     SUPPORT: show supplier, amount, due date, mismatch reason, risk marker, and SLA.
     FAILURE_MODE: vague alerts create queue fatigue and encourage later rubber-stamping.

  3. Review the AI-generated exception summary and source evidence. [HUMAN: AP clerk, ASSISTED-BY: LLM, GATED]
     PURPOSE: decide whether the invoice is valid, invalid, correctable, or escalated.
     HUMAN_DEMAND:
       ORIENT: understand the AI claim, the mismatch type, and the evidence set.
       ACT: compare invoice, purchase order, receipt, supplier history, and policy.
       CLOSE: reach a defensible judgement or identify the missing information.
       RECOVER: request missing evidence, correct the AI summary, or escalate to a manager.
     HUMAN_SIMULATION:
       role: competent AP clerk, not a procurement policy expert.
       visible_context: queue item, AI summary, invoice, purchase order, receipt status, policy excerpt.
       task_goal: resolve the case correctly without manager escalation unless evidence is missing or risk is high.
       test_cases: normal evidence complete; missing receipt; wrong AI summary; policy threshold conflict.
     HUMAN_LOAD:
       focus_actions: 8
       business_actions: 3
       trivial_actions: 5
       explicit_decisions: 3
       context_switches: 5
       uncertainty_loops: 2
       input_burden: medium
       closure_clarity: medium
     TRUST: require calibrated trust; show source evidence, uncertainty, and disagreement before approval.
     HUMAN_FACTORS:
       cognitive_load: working memory burden, attention fragmentation, ambiguity load.
       trust_automation: automation bias, authority effect, poor trust calibration.
       social_role: accountability without full control if AI summary shapes the decision.
       behavioural_economics: effort avoidance may favour accepting the easiest visible option.
       incentive_risk: pressure to close the queue can compete with careful review.
     HUMAN_RISK:
       probability: high
       impact: high
       confidence: medium
       score: critical
       rationale: high workload, visible AI recommendation, incomplete evidence risk, and human accountability combine to reduce effective review capacity.
     SUPPORT: co-locate invoice, purchase order, receipt, policy, and AI rationale on one review surface.
     SIMULATION_FINDINGS:
       User cannot approve confidently when receipt status is hidden.
       AI summary looks authoritative even when one source is uncertain.
       Five context switches occur before the first business decision.
     IMPROVEMENT:
       Reduce context switches by showing all evidence in one pane.
       Add a first-class "request missing receipt" action.
       Require an uncertainty acknowledgement before approval when sources disagree.

  4. Confirm the decision and record the reason. [HUMAN: AP clerk, SIDE-EFFECT]
     PURPOSE: make the outcome accountable, reusable, and auditable.
     HUMAN_DEMAND:
       ORIENT: see the available outcomes and the consequence of each.
       ACT: choose approve, reject, correct, or escalate, then record a reason.
       CLOSE: know the decision has been saved and will be visible to audit and downstream finance.
       RECOVER: edit the reason before final submission or cancel without changing the case.
     HUMAN_LOAD:
       focus_actions: 4
       business_actions: 2
       trivial_actions: 2
       explicit_decisions: 2
       input_burden: high if reason text is blank free-form
     SUPPORT: provide editable reason templates grounded in the evidence and policy.
     TRUST: distinguish "AI suggested reason" from "human final reason".
     HUMAN_FACTORS:
       interface_friction: blank free-text reasons create avoidable input burden.
       behavioural_economics: default wording can anchor the human decision.
       social_role: audit visibility may increase blame avoidance.
     HUMAN_RISK:
       probability: medium
       impact: medium
       confidence: medium
       score: significant
       rationale: the decision is consequential and the reason field can either support clear judgement or push the clerk into defensive wording.
     CHANGE_IMPACT:
       role_shift: clerk moves from data entry toward exception judgement.
       new_skill: evidence-based review of AI-assisted recommendations.
       accountability: decision remains human-owned, with AI assistance visible.

  5. Notify the clerk and finance queue of the completed outcome. [CODE, ASYNC]
     PURPOSE: close the loop so the case is no longer mentally open.
     HUMAN_DEMAND:
       ORIENT: notice final status, timestamp, and whether any follow-up remains.
       ACT: move on, monitor escalation, or reopen if the displayed status is wrong.
       CLOSE: queue count decreases and the invoice moves to approved, rejected, corrected, or escalated.
       RECOVER: reopen with reason if the confirmation contradicts the decision.
     HUMAN_LOAD:
       focus_actions: 1
       business_actions: 0
       trivial_actions: 0
       context_switches: 0
       closure_clarity: high
     SUPPORT: show final status in the queue and on the case timeline.
     FAILURE_MODE: unclear closure causes duplicate work or anxious rechecking.

  6. Review recurring exception patterns. [HUMAN: Finance lead, ASSISTED-BY: LLM, x:periodic]
     PURPOSE: reduce avoidable future exceptions and improve the operating system.
     HUMAN_DEMAND:
       ORIENT: understand which exception types are repeated and which teams or suppliers are involved.
       ACT: decide whether to update supplier data, procurement practice, policy wording, or training.
       CLOSE: assign an improvement action and see whether exception rate changes.
       ADAPT: finance learns from repeated exceptions rather than absorbing them as normal workload.
     CHANGE_IMPACT:
       adoption_support: training, reversible rollout, audit trail, and manager escalation.
       resistance: concern that clerks are accountable for AI-shaped decisions.
       reinforcement: show corrected summaries and reduced repeat exceptions in team review.
```
