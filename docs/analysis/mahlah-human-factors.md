# Human Factors Analysis: HandleUserTurn

## 1. Append the user message to the rolling chat history.
**Purpose:** preserve the operator's conversational context before the system starts work.
- **emotional_agency: recoverability and control** - Matched cues in step 1: emotional_agency.
  Mitigation: provide calm recovery paths and visible confirmation that the user's action was received.
**Risk:** moderate (probability: low; impact: medium; confidence: medium)
Rationale: duplicate or uncertain submission can confuse the conversation state, but the action is recoverable.
**Conversation starters:**
- What human-system forces are plausibly present in this step?

## 2. Open a live trace stream for session_id (replay=false).
**Purpose:** fill the process panel as Tirzah works, not only at the end.
- **cognitive_load: context switching** - Matched cues in step 2: context_switches.
  Mitigation: co-locate evidence and reduce navigation before the decision point.
- **cognitive_load: mode switching** - Matched cues in step 2: dev log.
  Mitigation: make cross-surface correlation visible and keep the main task resumable.
- **cognitive_load: vigilance load** - Matched cues in step 2: vigilance_load, waiting for live events, appears stalled.
  Mitigation: make running, stalled, completed, and failed states explicit.
- **interface_friction: closure ambiguity** - Matched cues in step 2: completed or failed.
  Mitigation: show explicit completion, failure, and next-action state.
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
- **cognitive_load: uncertainty load** - Matched cues in step 3: uncertainty_loops, not obviously grounded.
  Mitigation: show what is known, unknown, and disputed before asking for judgement.
- **cognitive_load: mode switching** - Matched cues in step 3: dev log.
  Mitigation: make cross-surface correlation visible and keep the main task resumable.
- **interface_friction: provenance burden** - Matched cues in step 3: provenance, trace/session.
  Mitigation: keep source, trace, reviewer, timestamp, and decision context inspectable together.
- **trust_automation: automation bias** - Matched cues in step 3: fluent answers.
  Mitigation: expose evidence, uncertainty, and disagreement separately from the AI suggestion.
- **social_role: accountability without control** - Matched cues in step 3: accountable.
  Mitigation: align accountability with inspectable evidence, authority, and recovery paths.
- **organisational_change: feedback suppression** - Matched cues in step 3: feedback.
  Mitigation: offer low-friction, structured feedback prompts tied to the trace or decision.
**Risk:** significant (probability: medium; impact: high; confidence: medium)
Rationale: the clean answer is intentionally low-friction, so trust calibration depends on nearby but separate process evidence.
**Conversation starters:**
- What human-system forces are plausibly present in this step?
- Is the human accountable for a decision they can inspect, control, and recover from?
- Does the process calibrate trust before asking the human to approve or rely on AI output?
- Which context switches or memory burdens can be removed before the business decision?

## 4. Append the assistant answer to chat; close the SSE subscription.
**Purpose:** close the user turn cleanly without exposing implementation noise.
- **interface_friction: closure ambiguity** - Matched cues in step 4: closure_clarity.
  Mitigation: show explicit completion, failure, and next-action state.
- **emotional_agency: recoverability and control** - Matched cues in step 4: emotional_agency, retry path.
  Mitigation: provide calm recovery paths and visible confirmation that the user's action was received.
**Risk:** moderate (probability: medium; impact: medium; confidence: medium)
Rationale: failure presentation controls whether the user can recover calmly or is forced into technical interpretation.
**Conversation starters:**
- What human-system forces are plausibly present in this step?

## 1. Open a new browser window at ?view=devlog&session=<session_id>.
**Purpose:** let the operator or developer inspect detailed trace without disrupting chat.
- **cognitive_load: context switching** - Matched cues in step 1: context_switches.
  Mitigation: co-locate evidence and reduce navigation before the decision point.
- **cognitive_load: mode switching** - Matched cues in step 1: second-window, second window, dev log, split attention.
  Mitigation: make cross-surface correlation visible and keep the main task resumable.
- **cognitive_load: vigilance load** - Matched cues in step 1: vigilance_load.
  Mitigation: make running, stalled, completed, and failed states explicit.
- **emotional_agency: recoverability and control** - Matched cues in step 1: without losing.
  Mitigation: provide calm recovery paths and visible confirmation that the user's action was received.
**Risk:** significant (probability: medium; impact: medium; confidence: medium)
Rationale: dev log is valuable for trust and debugging, but it increases cognitive load and can overwhelm non-developer users.
**Conversation starters:**
- What human-system forces are plausibly present in this step?
- Is the human accountable for a decision they can inspect, control, and recover from?
- Which context switches or memory burdens can be removed before the business decision?

## 2. Subscribe to GET /api/trace/stream with replay=true.
**Purpose:** show history + live tail of the full request lifecycle. [SATISFIES: R3]
- **cognitive_load: mode switching** - Matched cues in step 2: dev log.
  Mitigation: make cross-surface correlation visible and keep the main task resumable.
**Risk:** moderate (probability: medium; impact: medium; confidence: medium)
Rationale: Estimated from offline human-factor cues; confirm with domain users before treating as authoritative.
**Conversation starters:**
- What human-system forces are plausibly present in this step?
- Which context switches or memory burdens can be removed before the business decision?

## 1. POST /api/feedback with session_id, trace_id, and operator text.
**Purpose:** let the operator correct, endorse, or contextualize the system's behaviour without breaking the conversation.
- **cognitive_load: context switching** - Matched cues in step 1: context_switches.
  Mitigation: co-locate evidence and reduce navigation before the decision point.
- **cognitive_load: uncertainty load** - Matched cues in step 1: missing context.
  Mitigation: show what is known, unknown, and disputed before asking for judgement.
- **interface_friction: input burden** - Matched cues in step 1: input_burden, blank.
  Mitigation: provide structured inputs and editable templates for high-value feedback.
- **emotional_agency: recoverability and control** - Matched cues in step 1: emotional_agency, repair the interaction.
  Mitigation: provide calm recovery paths and visible confirmation that the user's action was received.
- **organisational_change: feedback suppression** - Matched cues in step 1: feedback, feedback prompts, text box is blank, high input burden suppresses useful signal.
  Mitigation: offer low-friction, structured feedback prompts tied to the trace or decision.
**Risk:** significant (probability: medium; impact: medium; confidence: medium)
Rationale: feedback is the main input pathway for improving human-AI interaction, but high input burden suppresses useful signal.
**Conversation starters:**
- What human-system forces are plausibly present in this step?
- Is the human accountable for a decision they can inspect, control, and recover from?
- Which context switches or memory burdens can be removed before the business decision?
