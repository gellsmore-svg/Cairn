# Human Factors Analysis: ReviewSemanticEdges

## 3.1. Present source/target titles, relation, similarity context.
**Purpose:** give the operator enough local evidence to understand the proposed semantic link.
- **cognitive_load: context switching** - Matched cues in step 3.1: context_switches.
  Mitigation: co-locate evidence and reduce navigation before the decision point.
- **cognitive_load: uncertainty load** - Matched cues in step 3.1: missing.
  Mitigation: show what is known, unknown, and disputed before asking for judgement.
- **trust_automation: automation bias** - Matched cues in step 3.1: authoritative.
  Mitigation: expose evidence, uncertainty, and disagreement separately from the AI suggestion.
- **behavioural_economics: effort avoidance** - Matched cues in step 3.1: trivial_actions.
  Mitigation: make the right action easier than the risky shortcut.
**Risk:** significant (probability: medium; impact: medium; confidence: medium)
Rationale: the operator is asked to judge meaning from compressed evidence, so weak context can reduce review quality.
**Conversation starters:**
- What human-system forces are plausibly present in this step?
- Is the human accountable for a decision they can inspect, control, and recover from?
- Does the process calibrate trust before asking the human to approve or rely on AI output?
- Which context switches or memory burdens can be removed before the business decision?

## 3.2. operator decision.
**Purpose:** make graph promotion depend on an explicit human judgement.
- **cognitive_load: uncertainty load** - Matched cues in step 3.2: uncertainty.
  Mitigation: show what is known, unknown, and disputed before asking for judgement.
- **interface_friction: input burden** - Matched cues in step 3.2: input_burden.
  Mitigation: provide structured inputs and editable templates for high-value feedback.
- **social_role: accountability without control** - Matched cues in step 3.2: accountable.
  Mitigation: align accountability with inspectable evidence, authority, and recovery paths.
- **behavioural_economics: effort avoidance** - Matched cues in step 3.2: effort, one-click.
  Mitigation: make the right action easier than the risky shortcut.
**Risk:** significant (probability: medium; impact: high; confidence: medium)
Rationale: a single human decision controls durable graph writes, and review quality depends on calibrated trust in the suggestion.
**Conversation starters:**
- What human-system forces are plausibly present in this step?
- Is the human accountable for a decision they can inspect, control, and recover from?
- Which context switches or memory burdens can be removed before the business decision?

## 3.3. DecideCandidate(candidate_id, action, reviewer, note) → result
**Purpose:** record the decision with enough provenance for later audit and learning.
- **interface_friction: input burden** - Matched cues in step 3.3: input_burden, blank.
  Mitigation: provide structured inputs and editable templates for high-value feedback.
- **social_role: accountability without control** - Matched cues in step 3.3: audit.
  Mitigation: align accountability with inspectable evidence, authority, and recovery paths.
**Risk:** moderate (probability: low; impact: medium; confidence: medium)
Rationale: the main decision already happened, but poor feedback capture reduces future learning.
**Conversation starters:**
- What human-system forces are plausibly present in this step?

## 2b. accept → CALL PromoteToReviewedEdge(candidate, reviewer, note)
**Purpose:** turn an inspected candidate into a durable reviewed edge.
- **social_role: accountability without control** - Matched cues in step 2b: accountable.
  Mitigation: align accountability with inspectable evidence, authority, and recovery paths.
**Risk:** significant (probability: medium; impact: high; confidence: medium)
Rationale: promotion changes the graph and can affect later retrieval or reasoning paths.
**Conversation starters:**
- What human-system forces are plausibly present in this step?
- Is the human accountable for a decision they can inspect, control, and recover from?
