# Galeed in Cairn — cross-project trace spine (representative slice)

A Cairn description of **Galeed as it currently stands**: the family's shared
**heap of witness** — structured process telemetry separated from final answers,
emitted by any project and viewed by **Mizpah** (the watchtower).

Galeed records; Mizpah inspects. See [`mizpah.cairn.md`](mizpah.cairn.md) for the
browser UX over what Galeed persists.

---

## CONTEXT

- **trace event** — structured record: `event_id`, `type`, `status`, `summary`,
  `seq`, `timestamp`, `metadata`, correlation ids (`session_id`, `trace_id`,
  `request_id`, …).
- **Tracer** — per-request recorder: emit events, persist, query helpers.
- **TraceBus** — in-process pub/sub for live SSE tails (Mahlah process panel,
  Mizpah live tail).
- **schema_version** — `galeed.SCHEMA_VERSION`; bump only on incompatible shape
  changes; new event *types* are additive.
- **emitter** — any family project (Tirzah ask, Hoglah job, Mahalath ingest, …).

## REQUIREMENTS

```
R1. Process telemetry SHALL be separable from the final answer payload.        [MUST]
    ACCEPTANCE: events carry summaries/metadata; answer text lives elsewhere.
R2. Emitters SHALL populate standard correlation keys when applicable.          [MUST]
    ACCEPTANCE: CORRELATION_KEYS = request_id, session_id, trace_id, plan_id, job_id.
R3. Event vocabulary SHALL be extensible without schema_version bump.           [MUST]
    ACCEPTANCE: Tracer.emit accepts any type string; EventType documents family set.
R4. Live subscribers SHALL receive events without blocking the emitter.         [SHOULD]
    ACCEPTANCE: TraceBus publish is in-process, non-blocking.
R5. Persisted events SHALL be queryable by session for cross-session audit.     [MUST]
R6. Viewers (Mizpah, Mahlah dev log) SHALL remain read-only on the trace store. [MUST]
```

## OUTCOMES

Operators and integrators can stitch a request lifecycle across projects, stream
it live, and audit it later — without mixing diagnostics into conversational answers.

EMERGENT [SATISFIES: R1, R6] — answer/process separation in Mahlah's three-channel
UI is guaranteed only when emitters use Galeed's event contract consistently.

---

## PROCESS — Formal

```
PROCESS RecordRequestLifecycle (INPUT: request_context; OUTPUT: trace_id)
  STATE
    trace_id    [scope: request; dir: write]  ref: G1
    seq         [scope: request; dir: write]  ref: G2

  1. Create Tracer with correlation ids from request_context.                 [CODE]
     STATE UPDATE: trace_id ← new_trace_id; populate session_id, request_id
  2. EMIT process.started                                                     [CODE, SIDE-EFFECT] [SATISFIES: R1]
     CALL Tracer.emit(type=process.started, summary, metadata)
     CALL TraceBus.publish(event)                                              [SATISFIES: R4]
  3. ITERATE [OVER: substantive steps in the host process]
     3.1 EMIT typed step events (retrieval.*, model.*, research.*, job.*, …)  [CODE, SIDE-EFFECT]
         CONSTRAINTS: metadata includes correlation keys where applicable      [SATISFIES: R2]
         STATE UPDATE: seq += 1
     3.2 Persist each event to trace store.                                   [CODE] [SATISFIES: R5]
  4. EMIT answer.finalized (answer reference only, not full answer dump).     [CODE]
  5. EMIT process.completed | process.failed                                  [CODE]
  OUTPUT: trace_id

PROCESS QueryTrace (INPUT: session_id; OUTPUT: event_timeline)
  CONSTRAINTS: read-only; no writes to trace store                            [SATISFIES: R6]
  1. CALL list_trace_sessions() or list_trace_events(session_id)              [CODE]
  2. Order by seq; attach correlation_ids via galeed.correlation_ids(event)   [CODE]
  OUTPUT: event_timeline
```

## PROCESS — operator profile (rendered view)

```
render-profile: operator

WATCH a run live
  Purpose:  See process steps stream without polluting the chat answer.
  Owner:    Operator (via Mahlah process panel or Mizpah tail)
  Assisted by: TraceBus SSE subscriber
  Next:     open Mizpah for cross-session audit

AUDIT later
  Purpose:  Reconstruct what happened in any past session.
  Owner:    Operator
  Assisted by: Mizpah BrowseAndInspect (mizpah.cairn.md)
```

## PROCESS — Narrative (same backbone)

```
PROCESS — RecordRequestLifecycle: emitters write the witness heap.
  Open a Tracer → emit started → for each real step emit a typed event (persist +
  bus publish) → finalize → complete or fail.

PROCESS — QueryTrace: viewers read without writing.
  List sessions or events for a session; correlation helpers stitch cross-repo ids.
```

---

## Documented event families (extensible)

| Family | Example types | Typical emitter |
|--------|---------------|-----------------|
| Session | `session.created`, `message.user.submitted` | Tirzah, Mahlah |
| Process | `process.started`, `process.step`, `process.completed` | all |
| Retrieval | `retrieval.mongo.*`, `context.selected` | Tirzah |
| Research | `research.started`, `research.completed` | Tirzah web path |
| Jobs | `job.queued`, `job.completed` | Hoglah |
| Ontology | `document.ingested`, `debate.completed` | Mahalath |

---

## Stress-test notes

What worked: infrastructure-shaped PROCESS (emit vs query); `EMERGENT` link to
Mahlah UX guarantee; correlation keys as STATE refs; read-only query path pairs
with Mizpah.

Rough edges:

1. **Physical store location** — events persist in Tirzah Mongo today; Galeed is
   library-only; extraction to shared service not modelled.
2. **Feedback collection** — `record_feedback` is adjacent but separate;
   could be `CALL RecordFeedback` sibling PROCESS.
3. **No endorsement / graph events** — memory trust gates live in Tirzah slices;
   Galeed documents telemetry only.