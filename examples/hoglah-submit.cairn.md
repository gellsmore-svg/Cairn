# Hoglah in Cairn — pure submitter topology (representative slice)

A Cairn description of **Hoglah's decoupled submitter/worker pattern** — how
Tirzah, Milcah, and other clients **submit** model jobs without executing them,
while a separate worker daemon owns the queue, claims, and recovery.

This complements [`hoglah.cairn.md`](hoglah.cairn.md) (messaging **bridge** with
`SERVICE` loops). The pure submitter path is the common in-process integration
pattern on a shared SQLite/Mongo store.

---

## CONTEXT

- **submitter** — client with `start_worker=False`; enqueues via `submit()`, never
  runs the model locally.
- **worker daemon** — `hoglah run` (or `Hoglah(start_worker=True)`); claims
  `QUEUED` jobs, executes via adapter, writes terminal result.
- **Store** — shared durable queue (SQLite default, Mongo server-side).
- **correlation_id** — idempotency key; duplicate submits are no-ops.
- **ADR-016** — interrupted-job recovery runs **only** on worker instances.

## REQUIREMENTS

```
R1. A pure submitter SHALL NOT start a background worker.                       [MUST]
R2. A pure submitter SHALL NOT recover interrupted PROCESSING jobs.            [MUST]
    ACCEPTANCE: _recover_interrupted_jobs only when start_worker=True.
R3. submit() SHALL enqueue durably and return a job id / await result.          [MUST]
R4. Exactly one worker claim SHALL execute each job to terminal.                [MUST]
    ACCEPTANCE: atomic QUEUED → PROCESSING claim (same as hoglah.cairn.md R5).
R5. Multiple submitters MAY share one Store against one or more workers.        [SHOULD]
R6. Result delivery to a detached submitter SHALL use callback/poll/wait.        [SHOULD]
```

## OUTCOMES

Family products can fire-and-forget (or block-for) LLM work without embedding a
worker — safe alongside a long-lived daemon on the same queue.

---

## PROCESS — Formal

```
PROCESS SubmitAndCollect (INPUT: job_request; OUTPUT: terminal_result)
  STATE
    job_id          [scope: process; dir: write]  ref: J1
    client_mode     [scope: process; dir: read]   ref: J2  # submitter

  1. Construct Hoglah client with start_worker=False.                         [CODE]
     STATE UPDATE: client_mode ← submitter
     CONSTRAINTS: no background worker thread; no recovery on construct       [SATISFIES: R1, R2]
  2. CALL client.submit(kind, prompt, model, …) → job_id                       [CODE, SIDE-EFFECT]
     IDEMPOTENT [KEY: correlation_id]
     STATE UPDATE: Store += job (QUEUED)
  3. DECISION [ON: result delivery mode]
     3a. blocking wait → poll/wait until terminal                             [CODE, SYNC]
     3b. callback_url → return immediately; worker POSTs on completion        [CODE, ASYNC]
     3c. detached → return job_id; poll later                                 [CODE]
  OUTPUT: terminal_result (COMPLETED | FAILED + payload)

PROCESS WorkerDaemon (INPUT: Store; OUTPUT: —)
  CONSTRAINTS: start_worker=True; runs recovery on startup                     [SATISFIES: R2 inverse]
  1. On startup, CALL RecoverInterruptedJobs(Store).                            [CODE, RECOVERY]
  2. ITERATE [UNTIL: stop]
     CALL Work(Store)  # claim → execute adapter → terminal → callback          # hoglah.cairn.md
```

## PROCESS — operator profile (rendered view)

```
render-profile: operator

SUBMIT work
  Purpose:  Hand a model job to the shared queue without running Ollama in-process.
  Owner:    Submitter process (Tirzah, Milcah, script, …)
  Assisted by: Hoglah client API
  Next:     wait, poll, or rely on callback

RUN the worker
  Purpose:  Drain the queue, execute jobs once, survive restarts.
  Owner:    Worker daemon
  Iterate-until: operator stops the daemon
```

## PROCESS — Narrative (same backbone)

```
PROCESS — SubmitAndCollect: enqueue from a thin client.
  Open Hoglah(start_worker=False) → submit → collect result by wait/callback/poll.

PROCESS — WorkerDaemon: the executor that must be running somewhere else.
  Recover interrupted jobs → loop claim/execute until stopped.

Contrast with RunBridge: the bridge adds broker ingress/egress SERVICE loops;
the pure submitter talks to Store directly.
```

---

## Topology comparison

| Pattern | Submitter | Executor | Broker |
|---------|-----------|----------|--------|
| Pure submitter | `start_worker=False` | separate daemon | none |
| In-process | `start_worker=True` | same process | none |
| Messaging bridge | external publisher | worker + bridge SERVICEs | Kafka/Rabbit/Redis |

---

## Stress-test notes

What worked: `DECISION` on result delivery; explicit ADR-016 constraint as
`CONSTRAINTS` on client construct; `CALL Work` reuse from bridge example.

Rough edges:

1. **Agentic steps** — this slice has **no LLM planner steps**; the submitter is
   `[CODE]` throughout. Stochastic work happens inside the worker's model call
   (tagged `[EXTERNAL]` in `hoglah.cairn.md`), not in the submitter PROCESS.
2. **SQLite multi-worker** — two workers on one SQLite file still need a
   process-level lock; Mongo atomic claim is the safe server pattern.
3. **Messaging submitter** — `MessagingSubmitter` mirrors the bridge wire format
   over a broker; could be a sibling `hoglah-messaging-submit.cairn.md`.