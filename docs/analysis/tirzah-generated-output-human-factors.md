# Human Factors Analysis: ReviewGeneratedOutput

## 4.1. Present query, answer preview, provenance, used_node_ids.
**Purpose:** give the operator enough context to judge whether generated output deserves trusted memory status.
- **cognitive_load: context switching** - Matched cues in step 4.1: context_switches, co-locate.
  Mitigation: co-locate evidence and reduce navigation before the decision point.
- **interface_friction: provenance burden** - Matched cues in step 4.1: provenance, source evidence, used nodes, process trace.
  Mitigation: keep source, trace, reviewer, timestamp, and decision context inspectable together.
- **trust_automation: automation bias** - Matched cues in step 4.1: fluent generated.
  Mitigation: expose evidence, uncertainty, and disagreement separately from the AI suggestion.
- **behavioural_economics: effort avoidance** - Matched cues in step 4.1: trivial_actions.
  Mitigation: make the right action easier than the risky shortcut.
**Risk:** significant (probability: medium; impact: high; confidence: medium)
Rationale: endorsement can promote generated text into trusted retrieval memory, so weak inspection context has downstream effects.
**Conversation starters:**
- What human-system forces are plausibly present in this step?
- Is the human accountable for a decision they can inspect, control, and recover from?
- Does the process calibrate trust before asking the human to approve or rely on AI output?
- Which context switches or memory burdens can be removed before the business decision?

## 4.2. operator endorsement decision.
**Purpose:** make trusted-memory promotion depend on explicit human endorsement or rejection.
- **cognitive_load: uncertainty load** - Matched cues in step 4.2: uncertainty_loops.
  Mitigation: show what is known, unknown, and disputed before asking for judgement.
- **interface_friction: input burden** - Matched cues in step 4.2: input_burden.
  Mitigation: provide structured inputs and editable templates for high-value feedback.
- **interface_friction: closure ambiguity** - Matched cues in step 4.2: closure_clarity.
  Mitigation: show explicit completion, failure, and next-action state.
- **trust_automation: rubber-stamp risk** - Matched cues in step 4.2: rubber stamp, one-click endorsement, lowest-effort path.
  Mitigation: make reject, defer, and inspect-more-context paths as easy and legitimate as approval.
- **social_role: accountability without control** - Matched cues in step 4.2: accountable.
  Mitigation: align accountability with inspectable evidence, authority, and recovery paths.
- **behavioural_economics: effort avoidance** - Matched cues in step 4.2: effort, one-click.
  Mitigation: make the right action easier than the risky shortcut.
**Risk:** significant (probability: medium; impact: high; confidence: medium)
Rationale: a single review action changes memory trust status and may influence later answers.
**Conversation starters:**
- What human-system forces are plausibly present in this step?
- Is the human accountable for a decision they can inspect, control, and recover from?
- Does the process calibrate trust before asking the human to approve or rely on AI output?
- Which context switches or memory burdens can be removed before the business decision?

## 4.3. EndorseGeneratedNode(node_id, endorsement_label, reviewer, note) → result
**Purpose:** record the endorsement decision with provenance for audit and future learning.
- **interface_friction: input burden** - Matched cues in step 4.3: input_burden, blank.
  Mitigation: provide structured inputs and editable templates for high-value feedback.
- **interface_friction: closure ambiguity** - Matched cues in step 4.3: closure_clarity.
  Mitigation: show explicit completion, failure, and next-action state.
- **interface_friction: provenance burden** - Matched cues in step 4.3: provenance.
  Mitigation: keep source, trace, reviewer, timestamp, and decision context inspectable together.
- **social_role: accountability without control** - Matched cues in step 4.3: audit.
  Mitigation: align accountability with inspectable evidence, authority, and recovery paths.
- **organisational_change: feedback suppression** - Matched cues in step 4.3: feedback.
  Mitigation: offer low-friction, structured feedback prompts tied to the trace or decision.
**Risk:** moderate (probability: low; impact: medium; confidence: medium)
Rationale: the trust decision already happened, but poor provenance weakens later audit and learning.
**Conversation starters:**
- What human-system forces are plausibly present in this step?

## 3. Update endorsement_label, provenance, metadata.review_history.
**Purpose:** make the final memory-trust state durable and attributable.
- **interface_friction: provenance burden** - Matched cues in step 3: provenance, source evidence, review_history.
  Mitigation: keep source, trace, reviewer, timestamp, and decision context inspectable together.
- **social_role: accountability without control** - Matched cues in step 3: accountable.
  Mitigation: align accountability with inspectable evidence, authority, and recovery paths.
**Risk:** significant (probability: medium; impact: high; confidence: medium)
Rationale: durable endorsement affects future retrieval behaviour and therefore future answers.
**Conversation starters:**
- What human-system forces are plausibly present in this step?
- Is the human accountable for a decision they can inspect, control, and recover from?
