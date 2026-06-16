# Hoglah in Cairn — crash-safe bridge job lifecycle (representative slice)

A Cairn description of **Hoglah as it currently stands**, for the slice that best
exercises the constructs Tirzah didn't: the **crash-safe messaging-bridge job
lifecycle** — consume a job request from a broker, enqueue it durably, process it
on a serial worker, and publish the result via a transactional outbox, with
poison handling and restart recovery.

Hoglah is a local-first job queue for Ollama. A bridge (Kafka / RabbitMQ / Redis
Streams) optionally feeds the durable store; the design below is broker-neutral.

---

## CONTEXT

- **Store** — the durable job queue (SQLite default, or Mongo). The single source
  of truth: jobs, their status, a UNIQUE `correlation_id`, and a `published` flag.
- **broker** — an external message system the operator already runs; Hoglah
  bridges it without owning it.
- **correlation_id** — a unique key on each request; the idempotency key.
- **terminal** — a job in `COMPLETED` or `FAILED` (a result exists).
- **dead-letter** — where un-processable ("poison") messages go so they never
  block the queue.

## REQUIREMENTS

```
R1. No loss: a request the broker considers delivered SHALL eventually reach a
    terminal result.                                                       [MUST]
    ACCEPTANCE: the broker offset is committed only AFTER a durable enqueue.
R2. No duplicate execution: redelivery of an already-enqueued request SHALL be a
    no-op.                                                                  [MUST]
    ACCEPTANCE: enqueue is idempotent on correlation_id (UNIQUE).
R3. Exactly-once effect: each terminal result SHALL be published exactly once.   [MUST]
    ACCEPTANCE: published is set only after a confirmed broker ack (outbox).
R4. Poison messages SHALL NOT block the queue.                              [MUST]
    ACCEPTANCE: an unparseable message is dead-lettered, then acked.
R5. Each job SHALL execute once even with multiple workers.                 [MUST]
    ACCEPTANCE: claim is an atomic QUEUED → PROCESSING transition.
R6. The system SHALL survive restarts.                                      [MUST]
    ACCEPTANCE: interrupted jobs are re-queued; computed-but-unpublished
    results are re-emitted on startup.
```

## OUTCOMES

Every accepted request yields exactly one delivered result (or a dead-letter
entry). No loss, no duplicated effect, across crashes and restarts.

---

## PROCESS — Formal

```
PROCESS RunBridge (INPUT: broker, Store; OUTPUT: —)
  CONTEXT: three long-running services share the durable Store and run concurrently.
  STATE
    Store   [scope: global; dir: read/write]  ref: H1   # the durable queue (shared)

  1. On startup, CALL RecoverOnStartup(Store, broker).        [CODE, DETERMINISTIC] [SATISFIES: R6]
  2. PARALLEL [STATE: shared via Store; MERGE: none — runs until stop]
     2a. Ingest:  ITERATE [UNTIL: stop] → CALL Ingest(broker, Store)
     2b. Work:    ITERATE [UNTIL: stop] → CALL Work(Store)
     2c. Egress:  ITERATE [UNTIL: stop] → CALL Egress(Store, broker)

PROCESS Ingest (INPUT: broker, Store; OUTPUT: —)   # idempotent consumer
  1. Consume the next message from the broker.                [EXTERNAL, ASYNC, BLOCKING]
  2. Parse / validate it into a JobRequest.                   [CODE, DETERMINISTIC]
     ERROR [ON: unparseable; THEN: fallback → dead-letter the message, then ack it] [SATISFIES: R4]
  3. Enqueue durably, keyed on correlation_id.                [CODE, IDEMPOTENT, SIDE-EFFECT] [SATISFIES: R2]
     STATE UPDATE: Store += job (no-op if correlation_id already present)
  4. Ack / commit the broker offset — ONLY after step 3 is durable. [EXTERNAL] [SATISFIES: R1]
     CONSTRAINTS: ordering is safety-critical. A crash between 3 and 4 → the
     broker redelivers → step 3 is a no-op → it is acked. No loss, no dup.

PROCESS Work (INPUT: Store; OUTPUT: —)             # the serial worker
  QUEUE [ORDER: PRIORITY then FIFO; ONE_AT_A_TIME]
  1. Claim the next QUEUED job: atomic QUEUED → PROCESSING.   [CODE, DETERMINISTIC] [SATISFIES: R5]
     BREAK [IF: no job available]   # idle; the loop in RunBridge re-enters
  2. RETRY [MAX: max_attempts; BACKOFF: exponential]
     2.1 Execute the model call, within the timeout.          [EXTERNAL, ASYNC]
         ERROR [ON: timeout; THEN: fallback → mark FAILED (terminal), free the slot]
         ERROR [ON: transient; THEN: handle → retry per RETRY]
  3. Write the terminal result (COMPLETED / FAILED); leave it unpublished. [CODE, SIDE-EFFECT]
     STATE UPDATE: Store[job].result, status=terminal, published=false

PROCESS Egress (INPUT: Store, broker; OUTPUT: —)   # transactional outbox
  1. Take the next terminal-but-unpublished result.           [CODE, DETERMINISTIC]
     BREAK [IF: none]
  2. Produce the result to the broker (results stream, or the request's reply_to). [EXTERNAL, ASYNC]
     ERROR [ON: nack/unconfirmed; THEN: fallback → leave unpublished; retry next pass]
  3. Mark published — ONLY after a confirmed broker ack.      [CODE, SIDE-EFFECT] [SATISFIES: R3]
     CONSTRAINTS: a crash between 2 and 3 → on restart the result is still
     unpublished → it is re-emitted (R6). The consumer de-dups on correlation_id.

PROCESS RecoverOnStartup (INPUT: Store, broker; OUTPUT: —)
  1. Re-queue any job left PROCESSING by a crash (respecting max_attempts).  [CODE] [SATISFIES: R6]
  2. Re-emit every terminal-but-unpublished result (drain the outbox).       [CODE] [SATISFIES: R6]
```

## PROCESS — Narrative (same backbone)

```
PROCESS — RunBridge: bridge a broker to the durable queue.

  1. On startup, recover: re-queue jobs a crash left half-done, and re-send any
     results that were computed but never published.
  2. Then run three services at once over the shared queue, until stopped:
     2a. Ingest — pull requests off the broker into the queue.
     2b. Work — process queued jobs, one at a time.
     2c. Egress — publish finished results back to the broker.

PROCESS — Ingest: take one message safely into the queue.
  1. Read the next message from the broker.
  2. Parse it into a job. If it can't be parsed, send it to the dead-letter
     destination and acknowledge it — never let a bad message block the queue.
  3. Add the job to the durable queue, keyed by its correlation id; if that id is
     already present, this does nothing.
  4. Only now acknowledge the broker. (Ordering matters: if we crash between 3
     and 4, the broker resends, step 3 no-ops, and we acknowledge — nothing is
     lost or duplicated.)

PROCESS — Work: process one job, serially.
  1. Atomically claim the next queued job (so two workers can't take the same
     one). If none is waiting, stop this pass.
  2. Run the model call within the timeout, retrying on transient errors up to the
     limit; on timeout, fail the job cleanly and free the slot.
  3. Save the final result and leave it marked "not yet published."

PROCESS — Egress: publish one finished result, exactly once.
  1. Take the next finished, unpublished result (stop if there are none).
  2. Send it to the broker (the results stream, or the reply address on the
     request). If the broker doesn't confirm, leave it unpublished and try again
     next pass.
  3. Mark it published only after a confirmed acknowledgement. (If we crash
     between sending and marking, it stays "unpublished" and is re-sent on
     restart; the consumer removes the duplicate by correlation id.)
```

---

## STATE REFERENCE (stub)

- **H1 Store** — the durable job queue: each job `{correlation_id (UNIQUE),
  request, status, result, published}`. The single source of truth, shared by
  Ingest / Work / Egress / recovery. Backed by SQLite (default) or Mongo; the
  atomic claim (R5) is a conditional `QUEUED → PROCESSING` update.

---

## Stress-test notes (gaps surfaced for the spec)

What worked: `QUEUE`, `RETRY`, the new `ERROR THEN: fallback → <target>`,
`BREAK [IF: …]`, `[IDEMPOTENT]`/`[ASYNC]` tags, shared-Store `STATE`, and the
crash-safety guarantees as `REQUIREMENTS` with `ACCEPTANCE` mapped very cleanly —
this domain fit Cairn better than Tirzah did.

New gaps to feed back:
1. **Long-running concurrent services with no join.** `PARALLEL … MERGE` assumes a
   join, but Ingest/Work/Egress are perpetual loops over shared state. I used
   `MERGE: none — runs until stop`; the spec should bless a **SERVICE / DAEMON**
   notion (concurrent, non-joining, shared-state) rather than overloading
   PARALLEL.
2. **Crash-window / recovery semantics are first-class here but unsupported.** The
   whole design is about "if a crash happens *between step 3 and step 4*, then …".
   Cairn can only put this in `CONSTRAINTS` prose. A crash-safe spec language
   wants a way to mark a **safety-critical ordering / atomic boundary** between
   two steps and state the **recovery** if interrupted there (e.g. `ATOMIC`/
   `DURABLE-BEFORE`, or a `RECOVERY:` annotation).
3. **Idempotency is a property of a step's *effect*, not just a tag.** `[IDEMPOTENT]`
   flags it, but "keyed on correlation_id" (the *what*) lives in prose. Consider an
   `IDEMPOTENT [KEY: correlation_id]` form.
4. **"Exactly-once effect"** is an end-to-end property spanning Ingest + Egress +
   consumer de-dup — it satisfies R3 across *three* processes. Cairn ties one step
   to a requirement via `[SATISFIES]`, but has no clean way to say "this guarantee
   emerges from steps X, Y, Z together."
