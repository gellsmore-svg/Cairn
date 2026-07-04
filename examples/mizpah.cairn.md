# Mizpah in Cairn — cross-session trace browser (representative slice)

A Cairn description of **Mizpah as it currently stands**: the family **watchtower**
over structured trace events — browse *any* session after the fact, not only the
conversation you are in.

Mizpah pairs with [Mahlah](mahlah.cairn.md): Mahlah's dev-log popup shows the
**current** session inline; Mizpah lists **all** sessions and inspects any one's
full lifecycle. Both read Tirzah's trace API today, which persists
[Galeed](galeed.cairn.md) events (`tirzah/trace/` is still single-sourced in
Tirzah; extraction to Mizpah is deferred until a second emitter needs it).

---

## CONTEXT

- **operator** — someone auditing, debugging, or reviewing what the system did.
- **session** — a keyed conversation/run in the trace store (`session_id`).
- **trace event** — structured record: `type`, `status`, `summary`, `seq`,
  `timestamp`, `metadata`, ids (same contract as Mahlah's process/dev channels).
- **live tail** — optional SSE subscription with `replay=true` to append new
  events while a session is selected.

## REQUIREMENTS

```
R1. The operator SHALL list sessions without knowing session_id in advance.   [MUST]
    ACCEPTANCE: GET /api/trace/sessions returns summaries (counts, first query, last activity).
R2. Sessions SHALL be filterable by id, query text, or source.                [SHOULD]
R3. Selecting a session SHALL show its full event timeline.                   [MUST]
    ACCEPTANCE: GET /api/trace/events?session_id=… returns ordered events.
R4. Live tail SHALL be optional and non-disruptive to the timeline view.      [SHOULD]
    ACCEPTANCE: GET /api/trace/stream?session_id=…&replay=true (SSE).
R5. Event detail SHALL be inspectable and exportable.                         [SHOULD]
    ACCEPTANCE: copy-all-as-JSON in the UI.
R6. The viewer SHALL remain read-only — no writes to the trace store.        [MUST]
```

## OUTCOMES

The operator can find a past session, read its complete request lifecycle, optionally
watch it live, and export events — without opening Mahlah or reading MongoDB.

---

## PROCESS — Formal

```
PROCESS BrowseAndInspect (INPUT: filters; OUTPUT: selected_session_view)
  STATE
    sessions      [scope: process; dir: read/write]  ref: Z1
    selection     [scope: process; dir: read/write]  ref: Z2
    events        [scope: process; dir: read/write]  ref: Z3
    live_tail     [scope: process; dir: read/write]  ref: Z4

  1. Load session summaries from the trace API.               [EXTERNAL, SYNC] [SATISFIES: R1]
     CALL TraceAPI.ListSessions(limit) → sessions
     STATE UPDATE: sessions ← summaries
  2. Apply operator filters (id / query / source).          [CODE, DETERMINISTIC] [SATISFIES: R2]
     STATE UPDATE: sessions ← filtered view
  3. DECISION [ON: operator selects a session]
     3a. CALL InspectSession(session_id) → event_timeline
         STATE UPDATE: selection ← session_id; events ← timeline
     3b. BREAK [IF: no selection yet]
  OUTPUT: selected_session_view

PROCESS InspectSession (INPUT: session_id, live_tail?; OUTPUT: event_timeline)
  1. Fetch persisted events for the session.                  [EXTERNAL, SYNC] [SATISFIES: R3]
     CALL TraceAPI.GetEvents(session_id) → events
  2. DECISION [ON: live_tail enabled]
     2a. Subscribe SSE with replay=true.                      [EXTERNAL, ASYNC, SSE] [SATISFIES: R4]
         ITERATE [UNTIL: operator disables tail or leaves session]
           append incoming events (dedupe by event_id, order by seq)
         STATE UPDATE: events += tailed events
     2b. static timeline only
  3. Render timestamp, status, type, source, summary, metadata per event. [CODE]
  4. On export request, serialize events as JSON.             [CODE] [SATISFIES: R5]
     CONSTRAINTS: read-only; no POST to trace store           [SATISFIES: R6]
  OUTPUT: event_timeline
```

## PROCESS — operator profile (rendered view)

```
render-profile: operator

FIND a session
  Purpose:  Locate a past conversation or run among all sessions in the store.
  Owner:    Operator
  Assisted by: Mizpah UI
  Outputs:  filtered session list
  Next:     select one to inspect

READ the lifecycle
  Purpose:  See every trace event for that session in order.
  Owner:    Operator
  Iterate-until: operator leaves the session or enables live tail
  Next:     copy JSON for audit, or switch to Mahlah for a new ask
```

## PROCESS — Narrative (same backbone)

```
PROCESS — BrowseAndInspect: the watchtower workflow.
  Load all session summaries → filter → when the operator picks one, load its
  full event timeline; optionally tail new events over SSE.

PROCESS — InspectSession: one session's story.
  Pull persisted events → optionally subscribe live → render and export.
  Read-only throughout.
```

---

## STATE REFERENCE (stub)

- **Z1 sessions** — list rows from `/api/trace/sessions`.
- **Z2 selection** — active `session_id`.
- **Z3 events** — ordered timeline for the selection.
- **Z4 live_tail** — whether SSE replay tail is active.

---

## Stress-test notes

What worked: read-only **EXTERNAL** calls; `DECISION` for select-vs-idle; nested
`ITERATE` for SSE tail; clear complement to Mahlah (cross-session vs in-session).

Rough edges:

1. **Shared trace contract across UIs** — Mahlah, Mizpah, and Tirzah CLI should
   share a documented correlation envelope (`session_id`, `trace_id`, `event_id`);
   Cairn could add a `CHANNEL` or `SURFACE` annotation for multi-view systems.
2. **Collector service** — future central ingest of events from Mahalath/Hoglah
   is not modelled; today Mizpah assumes Tirzah's API is the trace source of truth.
3. **No PLAN / agentic loop** — purely observational; exercises a different shape
   than Tirzah ask or Hoglah bridge.