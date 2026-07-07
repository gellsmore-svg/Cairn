# Human Factors Analysis: HandleUserTurn

## 1. Append the user message to the rolling chat history.
**Purpose:** preserve the operator's conversational context before the system starts work.
- **cognitive_load: uncertainty load** - Matched cues in step 1: uncertainty, missing.
  Mitigation: show what is known, unknown, and disputed before asking for judgement.
**Risk:** moderate (probability: low; impact: medium; confidence: medium)
Rationale: duplicate or uncertain submission can confuse the conversation state, but the action is recoverable.
**Conversation starters:**
- What human-system forces are plausibly present in this step?
- Which context switches or memory burdens can be removed before the business decision?

## 2. Open a live trace stream for session_id (replay=false).
**Purpose:** fill the process panel as Tirzah works, not only at the end.
- **cognitive_load: context switching** - Matched cues in step 2: context_switches.
  Mitigation: co-locate evidence and reduce navigation before the decision point.
- **cognitive_load: uncertainty load** - Matched cues in step 2: uncertainty.
  Mitigation: show what is known, unknown, and disputed before asking for judgement.
- **behavioural_economics: effort avoidance** - Matched cues in step 2: trivial_actions.
  Mitigation: make the right action easier than the risky shortcut.
**Risk:** significant (probability: medium; impact: medium; confidence: medium)
Rationale: live trace visibility can either reduce uncertainty or create extra monitoring burden depending on clarity.
**Conversation starters:**
- What human-system forces are plausibly present in this step?
- Is the human accountable for a decision they can inspect, control, and recover from?
- Which context switches or memory burdens can be removed before the business decision?

## 3. Tirzah.Ask(user_text, session_id, model_opts) → answer, processEvents, traceId
**Purpose:** produce a clean conversational answer while preserving traceability to the underlying memory process.
- **cognitive_load: context switching** - Matched cues in step 3: context_switches.
  Mitigation: co-locate evidence and reduce navigation before the decision point.
- **cognitive_load: uncertainty load** - Matched cues in step 3: uncertainty.
  Mitigation: show what is known, unknown, and disputed before asking for judgement.
- **social_role: accountability without control** - Matched cues in step 3: accountable.
  Mitigation: align accountability with inspectable evidence, authority, and recovery paths.
**Risk:** significant (probability: medium; impact: high; confidence: medium)
Rationale: the clean answer is intentionally low-friction, so trust calibration depends on nearby but separate process evidence.
**Conversation starters:**
- What human-system forces are plausibly present in this step?
- Is the human accountable for a decision they can inspect, control, and recover from?
- Which context switches or memory burdens can be removed before the business decision?

## 4. Append the assistant answer to chat; close the SSE subscription.
**Purpose:** close the user turn cleanly without exposing implementation noise.
**Risk:** moderate (probability: medium; impact: medium; confidence: medium)
Rationale: failure presentation controls whether the user can recover calmly or is forced into technical interpretation.
**Conversation starters:**
- What human-system forces are plausibly present in this step?

## 1. Open a new browser window at ?view=devlog&session=<session_id>.
**Purpose:** let the operator or developer inspect detailed trace without disrupting chat.
- **cognitive_load: context switching** - Matched cues in step 1: context_switches.
  Mitigation: co-locate evidence and reduce navigation before the decision point.
**Risk:** significant (probability: medium; impact: medium; confidence: medium)
Rationale: dev log is valuable for trust and debugging, but it increases cognitive load and can overwhelm non-developer users.
**Conversation starters:**
- What human-system forces are plausibly present in this step?
- Is the human accountable for a decision they can inspect, control, and recover from?
- Which context switches or memory burdens can be removed before the business decision?

## 1. POST /api/feedback with session_id, trace_id, and operator text.
**Purpose:** let the operator correct, endorse, or contextualize the system's behaviour without breaking the conversation.
- **cognitive_load: context switching** - Matched cues in step 1: context_switches.
  Mitigation: co-locate evidence and reduce navigation before the decision point.
- **cognitive_load: uncertainty load** - Matched cues in step 1: missing.
  Mitigation: show what is known, unknown, and disputed before asking for judgement.
- **interface_friction: input burden** - Matched cues in step 1: input_burden, blank.
  Mitigation: provide structured inputs and editable templates for high-value feedback.
**Risk:** significant (probability: medium; impact: medium; confidence: medium)
Rationale: feedback is the main input pathway for improving human-AI interaction, but high input burden suppresses useful signal.
**Conversation starters:**
- What human-system forces are plausibly present in this step?
- Is the human accountable for a decision they can inspect, control, and recover from?
- Which context switches or memory burdens can be removed before the business decision?
