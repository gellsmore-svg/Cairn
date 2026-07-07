# Human Factors Analysis: ReviewGeneratedOutput

## 4.1. Present query, answer preview, provenance, used_node_ids.
**Purpose:** give the operator enough context to judge whether generated output deserves trusted memory status.
- **cognitive_load: context switching** - Matched cues in step 4.1: context_switches, co-locate.
  Mitigation: co-locate evidence and reduce navigation before the decision point.
- **cognitive_load: uncertainty load** - Matched cues in step 4.1: uncertainty.
  Mitigation: show what is known, unknown, and disputed before asking for judgement.
- **behavioural_economics: effort avoidance** - Matched cues in step 4.1: trivial_actions.
  Mitigation: make the right action easier than the risky shortcut.
**Risk:** significant (probability: medium; impact: high; confidence: medium)
Rationale: endorsement can promote generated text into trusted retrieval memory, so weak inspection context has downstream effects.
**Conversation starters:**
- What human-system forces are plausibly present in this step?
- Is the human accountable for a decision they can inspect, control, and recover from?
- Which context switches or memory burdens can be removed before the business decision?

## 4.2. operator endorsement decision.
**Purpose:** make trusted-memory promotion depend on explicit human endorsement or rejection.
- **cognitive_load: uncertainty load** - Matched cues in step 4.2: uncertainty.
  Mitigation: show what is known, unknown, and disputed before asking for judgement.
- **interface_friction: input burden** - Matched cues in step 4.2: input_burden.
  Mitigation: provide structured inputs and editable templates for high-value feedback.
- **social_role: accountability without control** - Matched cues in step 4.2: accountable.
  Mitigation: align accountability with inspectable evidence, authority, and recovery paths.
- **behavioural_economics: effort avoidance** - Matched cues in step 4.2: effort, one-click.
  Mitigation: make the right action easier than the risky shortcut.
**Risk:** significant (probability: medium; impact: high; confidence: medium)
Rationale: a single review action changes memory trust status and may influence later answers.
**Conversation starters:**
- What human-system forces are plausibly present in this step?
- Is the human accountable for a decision they can inspect, control, and recover from?
- Which context switches or memory burdens can be removed before the business decision?

## 4.3. EndorseGeneratedNode(node_id, endorsement_label, reviewer, note) → result
**Purpose:** record the endorsement decision with provenance for audit and future learning.
- **interface_friction: input burden** - Matched cues in step 4.3: input_burden, blank.
  Mitigation: provide structured inputs and editable templates for high-value feedback.
- **social_role: accountability without control** - Matched cues in step 4.3: audit.
  Mitigation: align accountability with inspectable evidence, authority, and recovery paths.
**Risk:** moderate (probability: low; impact: medium; confidence: medium)
Rationale: the trust decision already happened, but poor provenance weakens later audit and learning.
**Conversation starters:**
- What human-system forces are plausibly present in this step?

## 3. Update endorsement_label, provenance, metadata.review_history.
**Purpose:** make the final memory-trust state durable and attributable.
- **social_role: accountability without control** - Matched cues in step 3: accountable.
  Mitigation: align accountability with inspectable evidence, authority, and recovery paths.
**Risk:** significant (probability: medium; impact: high; confidence: medium)
Rationale: durable endorsement affects future retrieval behaviour and therefore future answers.
**Conversation starters:**
- What human-system forces are plausibly present in this step?
- Is the human accountable for a decision they can inspect, control, and recover from?
