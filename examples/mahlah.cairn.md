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
  2. Open a live trace stream for session_id (replay=false).    [CODE, ASYNC, SSE]
     PURPOSE: fill the process panel as Tirzah works, not only at the end.
     STATE UPDATE: process_events ← streamed events (deduped by event_id, ordered by seq)
  3. CALL Tirzah.Ask(user_text, session_id, model_opts) → answer, processEvents, traceId
     CONSTRAINTS: answer text only in the chat bubble; do not render processEvents there.
     [EXTERNAL, SYNC] [SATISFIES: R1, R4]
     STATE UPDATE: last_trace_id ← traceId; process_events ← final processEvents (if any)
  4. Append the assistant answer to chat; close the SSE subscription. [CODE, DETERMINISTIC]
     CONSTRAINTS: on failure, show a single error bubble; do not leak raw JSON.
  OUTPUT: chat_turn, process_events
```

```
PROCESS OpenDevLog (INPUT: session_id; OUTPUT: —)
  1. Open a new browser window at ?view=devlog&session=<session_id>. [CODE, DETERMINISTIC]
  2. Subscribe to GET /api/trace/stream with replay=true.             [CODE, ASYNC, SSE]
     PURPOSE: show history + live tail of the full request lifecycle. [SATISFIES: R3]
```

```
PROCESS SubmitFeedback (INPUT: text, session_id, trace_id; OUTPUT: feedback_id)
  1. POST /api/feedback with session_id, trace_id, and operator text. [EXTERNAL, SYNC]
     CONSTRAINTS: modal UI; chat layout unchanged after submit.       [SATISFIES: R5]
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