# Mahlah in Cairn — three-channel conversational ask (representative slice)

A Cairn description of **Mahlah as it currently stands**, for the slice that
exercises what Tirzah's backend example didn't surface on the **presentation**
side: a ChatGPT-style web UI that keeps **answer**, **process**, and **dev log**
strictly separated while consuming Tirzah's HTTP API.

Mahlah is the conversational front end split out of Tirzah (Vite + React +
TypeScript). Tirzah remains the memory engine; Mahlah owns layout, session UX,
and live trace display.

---

## CONTEXT

- **operator** — the human chatting in the browser.
- **session_id** — Tirzah's conversation key; Mahlah generates one per chat
  (client-side today) and passes it on every ask.
- **answer channel** — only the clean conversational reply in the chat bubble.
- **process channel** — live structured steps (retrieval, model, persistence) in a
  side panel via SSE; never mixed into the answer text.
- **dev-log channel** — full serial trace in a separate window (`?view=devlog`),
  suitable for a developer or another AI assistant to watch.
- **trace event** — a structured record (`type`, `status`, `summary`, `seq`, ids…)
  emitted by Tirzah and streamed over `/api/trace/stream`.

## REQUIREMENTS

```
R1. The answer shown in chat SHALL contain no process scaffolding.           [MUST]
    ACCEPTANCE: chat bubble text is only the conversational reply.
R2. Process events SHALL render separately from the answer, live per request.  [MUST]
    ACCEPTANCE: the process panel subscribes to SSE during the ask.
R3. The dev log SHALL be openable without disrupting the main chat.          [MUST]
    ACCEPTANCE: a popup window replays + tails the same session/trace.
R4. Each ask SHALL carry session_id and return trace/session/message ids.      [MUST]
R5. Feedback SHALL tie to the current session/trace without blocking chat.     [MUST]
R6. Model / adapter / retrieval-mode choices SHALL reflect the live backend.   [SHOULD]
    ACCEPTANCE: dropdowns populate from GET /api/runtime.
```

## OUTCOMES

The operator sees a clean answer, can watch what the system did in the process
panel, can open a deep dev log, and can submit feedback — all keyed to the same
session and trace.

---

## PROCESS — Formal

```
PROCESS HandleUserTurn (INPUT: user_text, session_id, model_opts; OUTPUT: chat_turn, process_events)
  STATE
    process_events  [scope: request; dir: write]  ref: M1   # live panel for THIS ask
    last_trace_id   [scope: session; dir: write]  ref: M2

  1. Append the user message to the rolling chat history.       [CODE, DETERMINISTIC]
     PURPOSE: preserve the operator's conversational context before the system starts work.
     HUMAN_DEMAND:
       ORIENT: see that the submitted message is now part of the visible conversation.
       ACT: wait for the answer or decide to monitor the process panel.
       CLOSE: understand that the request has been accepted and is in progress.
       RECOVER: allow the operator to retry or edit if the wrong text was sent.
     HUMAN_LOAD:
       focus_actions: 1
       business_actions: 1
       trivial_actions: 0
       closure_clarity: high
     HUMAN_FACTORS:
       emotional_agency: immediate message echo supports confidence that the system heard the request.
       interface_friction: missing or delayed echo can create uncertainty about whether to resubmit.
     HUMAN_RISK:
       probability: low
       impact: medium
       confidence: medium
       score: moderate
       rationale: duplicate or uncertain submission can confuse the conversation state, but the action is recoverable.
  2. Open a live trace stream for session_id (replay=false).    [CODE, ASYNC, SSE]
     PURPOSE: fill the process panel as Tirzah works, not only at the end.
     HUMAN_DEMAND:
       ORIENT: notice that the side panel is process context, not the answer.
       ACT: optionally monitor retrieval/model/persistence steps while waiting.
       CLOSE: see that the process stream has completed or failed for this ask.
       RECOVER: switch to dev log if the panel is too compressed or appears stalled.
     HUMAN_LOAD:
       focus_actions: 3
       business_actions: 1
       trivial_actions: 2
       context_switches: 2
       vigilance_load: medium while waiting for live events.
     HUMAN_FACTORS:
       cognitive_load: answer and process channels compete for attention if they update together.
       trust_automation: visible process can calibrate trust, but too much detail can look like authority theatre.
       interface_friction: unclear stream state can make the operator wonder whether the ask is stuck.
     HUMAN_RISK:
       probability: medium
       impact: medium
       confidence: medium
       score: significant
       rationale: live trace visibility can either reduce uncertainty or create extra monitoring burden depending on clarity.
     SUPPORT: label process state clearly as running, complete, failed, or disconnected.
     STATE UPDATE: process_events ← streamed events (deduped by event_id, ordered by seq)
  3. CALL Tirzah.Ask(user_text, session_id, model_opts) → answer, processEvents, traceId
     PURPOSE: produce a clean conversational answer while preserving traceability to the underlying memory process.
     CONSTRAINTS: answer text only in the chat bubble; do not render processEvents there.
     HUMAN_DEMAND:
       ORIENT: understand that the answer is AI-assisted and grounded in Tirzah's memory process.
       ACT: read the answer, compare it to intent, and decide whether to ask again, inspect process, or give feedback.
       CLOSE: see the final answer and know which trace/session it belongs to.
       RECOVER: ask a clarifying follow-up, inspect the dev log, or submit feedback when the answer feels wrong.
     HUMAN_LOAD:
       focus_actions: 5
       business_actions: 2
       context_switches: 2
       uncertainty_loops: 1
       ambiguity_load: medium when the answer is plausible but not obviously grounded.
     HUMAN_FACTORS:
       trust_automation: fluent answers can invite over-reliance unless grounding and trace access are nearby.
       cognitive_load: the operator may need to reconcile answer content with process evidence.
       social_role: if used in work, the operator may become accountable for acting on the answer.
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: medium
       score: significant
       rationale: the clean answer is intentionally low-friction, so trust calibration depends on nearby but separate process evidence.
     TRUST: keep the answer clean while making trace/session provenance easy to inspect.
     [EXTERNAL, SYNC] [SATISFIES: R1, R4]
     STATE UPDATE: last_trace_id ← traceId; process_events ← final processEvents (if any)
  4. Append the assistant answer to chat; close the SSE subscription. [CODE, DETERMINISTIC]
     CONSTRAINTS: on failure, show a single error bubble; do not leak raw JSON.
     PURPOSE: close the user turn cleanly without exposing implementation noise.
     HUMAN_DEMAND:
       ORIENT: know whether the turn completed successfully or failed.
       ACT: continue the conversation, inspect process details, or retry after an error.
       CLOSE: see final answer state and no longer expect live process updates for that ask.
       RECOVER: receive a clear retry path if the ask failed.
     HUMAN_LOAD:
       focus_actions: 2
       business_actions: 1
       closure_clarity: high when answer and process panel both show completion.
       input_burden: low
     HUMAN_FACTORS:
       emotional_agency: clear closure reduces anxious rechecking.
       interface_friction: raw JSON errors push technical debugging onto the operator.
     HUMAN_RISK:
       probability: medium
       impact: medium
       confidence: medium
       score: moderate
       rationale: failure presentation controls whether the user can recover calmly or is forced into technical interpretation.
     SUPPORT: show one human-readable failure message plus an optional dev-log link.
  OUTPUT: chat_turn, process_events
```

```
PROCESS OpenDevLog (INPUT: session_id; OUTPUT: —)
  1. Open a new browser window at ?view=devlog&session=<session_id>. [CODE, DETERMINISTIC]
     PURPOSE: let the operator or developer inspect detailed trace without disrupting chat.
     HUMAN_DEMAND:
       ORIENT: understand that the dev log is a deeper diagnostic surface for the same session.
       ACT: choose whether to split attention into a second window.
       CLOSE: return to the main chat with the same session context intact.
       RECOVER: close the window without losing the chat state.
     HUMAN_LOAD:
       context_switches: 2
       focus_actions: 3
       business_actions: 1
       vigilance_load: medium for non-developer operators.
     HUMAN_FACTORS:
       cognitive_load: second-window inspection creates a mode and attention shift.
       interface_friction: unclear correlation between chat and dev log can break trust in the trace.
     HUMAN_RISK:
       probability: medium
       impact: medium
       confidence: medium
       score: significant
       rationale: dev log is valuable for trust and debugging, but it increases cognitive load and can overwhelm non-developer users.
  2. Subscribe to GET /api/trace/stream with replay=true.             [CODE, ASYNC, SSE]
     PURPOSE: show history + live tail of the full request lifecycle. [SATISFIES: R3]
     SUPPORT: preserve visible session id, trace id, and request summary so the dev log remains anchored to the chat.
```

```
PROCESS SubmitFeedback (INPUT: text, session_id, trace_id; OUTPUT: feedback_id)
  1. POST /api/feedback with session_id, trace_id, and operator text. [EXTERNAL, SYNC]
     CONSTRAINTS: modal UI; chat layout unchanged after submit.       [SATISFIES: R5]
     PURPOSE: let the operator correct, endorse, or contextualize the system's behaviour without breaking the conversation.
     HUMAN_DEMAND:
       ORIENT: know which answer/trace the feedback will attach to.
       ACT: describe what was useful, wrong, missing, confusing, or risky.
       CLOSE: see confirmation that feedback was saved and linked to the current trace.
       RECOVER: cancel or edit feedback without changing the chat.
       ADAPT: repeated feedback can improve future retrieval, UI wording, and trust calibration.
     HUMAN_LOAD:
       input_burden: medium if the text box is blank and unstructured.
       focus_actions: 3
       business_actions: 1
       context_switches: 1
     HUMAN_FACTORS:
       interface_friction: blank feedback asks the operator to invent useful structure.
       emotional_agency: feedback gives the operator a way to repair the interaction rather than silently tolerate failure.
       organisational_change: trace-linked feedback turns individual frustration into process learning.
     HUMAN_RISK:
       probability: medium
       impact: medium
       confidence: medium
       score: significant
       rationale: feedback is the main input pathway for improving human-AI interaction, but high input burden suppresses useful signal.
     IMPROVEMENT: offer feedback prompts such as "wrong source", "missing context", "unclear answer", "good answer", or "unsafe confidence".
  OUTPUT: feedback_id
```

## PROCESS — operator profile (rendered view)

```
render-profile: operator

CHAT with Tirzah
  Purpose:  Ask questions; see only the conversational answer in the main pane.
  Owner:    Operator   Assisted by: Mahlah UI
  Next:     (process panel shows live work on the right)

WATCH the process
  Purpose:  See retrieval and model steps without cluttering the answer.
  Owner:    Operator
  Iterate-until: the current ask completes
  Next:     open dev log for full detail, or submit feedback

CONFIGURE runtime
  Purpose:  Pick model, adapter, and retrieval mode the backend actually offers.
  Owner:    Operator
  Assisted by: GET /api/runtime
```

---

## STATE REFERENCE (stub)

- **M1 process_events** — trace events for the in-flight ask (panel state).
- **M2 last_trace_id** — most recent trace id in the active conversation (feedback + dev log).

---

## Stress-test notes (gaps surfaced for the spec)

What worked: three **channels** as separate processes sharing `session_id` /
`trace_id`; `CALL` into Tirzah; SSE as an async side subscription alongside a
sync HTTP ask; operator render profile maps cleanly onto the UI layout.

Rough edges to feed back:

1. **Cross-channel correlation** — answer, process, and dev log all need the
   same ids; Cairn could recommend a standard "correlation envelope" for
   multi-surface UIs.
2. **Client-owned vs server-owned session state** — Mahlah still persists
   conversations in `localStorage` while Tirzah already exposes
   `/api/sessions` and `/api/history`; the gap is an integration concern worth
   documenting as a follow-on PROCESS (server sync not yet implemented).
3. **SSE lifecycle** — opening/closing streams per ask vs per session is an
   implementation detail the spec doesn't yet guide.
