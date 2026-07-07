# Hoglah in Cairn — crash-safe bridge job lifecycle (v2)

A Cairn description of **Hoglah as it currently stands**, for the slice that best
exercises **v0.9 durable-system constructs**: `SERVICE` / `CONCURRENT`,
`DURABLE-BEFORE`, `RECOVERY`, and idempotency keyed on `correlation_id`.

This revision replaces the v1 `PARALLEL … MERGE: none` pattern with the spec's
intended long-running-service model (see stress-test notes at the end).

Hoglah is a local-first job queue for Ollama. A bridge (Kafka / RabbitMQ / Redis
Streams) optionally feeds the durable store; the design below is broker-neutral.

For the **pure submitter** path see [`hoglah-submit.cairn.md`](hoglah-submit.cairn.md).

For the **detailed internal execution** (worker loop, claim, retries, dispatch, adapter calls, recovery) see the low-level implementation walk-through in [`hoglah-execution.cairn.md`](hoglah-execution.cairn.md).

---

## CONTEXT

- **Store** — the durable job queue (SQLite default, or Mongo). Single source of
  truth: jobs, status, UNIQUE `correlation_id`, `published` flag.
- **broker** — external message system Hoglah bridges without owning.
- **correlation_id** — idempotency key for ingress and consumer-side dedup.
- **terminal** — `COMPLETED` or `FAILED` with a stored result.
- **dead-letter** — poison or unprocessable messages routed out of the hot path.

## REQUIREMENTS

```
R1. No loss: a broker-delivered request SHALL eventually reach a terminal result. [MUST]
    ACCEPTANCE: broker offset acked only AFTER durable enqueue.
R2. No duplicate execution: redelivery of an already-enqueued request SHALL be a no-op. [MUST]
    ACCEPTANCE: enqueue idempotent on correlation_id (UNIQUE).
R3. Exactly-once effect: each terminal result SHALL be published exactly once. [MUST]
    ACCEPTANCE: published set only after confirmed broker ack; consumer dedups on correlation_id.
R4. Poison messages SHALL NOT block the queue. [MUST]
R5. Each job SHALL execute once even with multiple workers. [MUST]
    ACCEPTANCE: atomic QUEUED → PROCESSING claim.
R6. The system SHALL survive restarts. [MUST]
    ACCEPTANCE: interrupted jobs re-queued; unpublished terminal results re-emitted.
```

## OUTCOMES

Every accepted request yields exactly one delivered result (or a dead-letter entry).
No loss, no duplicated effect, across crashes and restarts.

EMERGENT [SATISFIES: R3]
  via Ingest.3–4 (durable-before-ack), Egress.2–3 (outbox), consumer dedup on correlation_id

---

## PROCESS — Formal

```
PROCESS RunBridge (INPUT: broker, Store; OUTPUT: —)
  STATE
    Store   [scope: global; dir: read/write]  ref: H1

  1. On startup, CALL RecoverOnStartup(Store, broker).     [CODE, DETERMINISTIC] [SATISFIES: R6]
  2. CONCURRENT [STATE: shared via Store; UNTIL: stop]
       SERVICE IngestLoop  → ITERATE [UNTIL: stop] → CALL Ingest(broker, Store)
       SERVICE WorkLoop    → ITERATE [UNTIL: stop] → CALL Work(Store)
       SERVICE EgressLoop  → ITERATE [UNTIL: stop] → CALL Egress(Store, broker)

PROCESS Ingest (INPUT: broker, Store; OUTPUT: —)
  1. Consume the next message from the broker.              [EXTERNAL, ASYNC, BLOCKING]
  2. Parse / validate into a JobRequest.                  [CODE, DETERMINISTIC]
     ERROR [ON: unparseable; THEN: fallback → dead-letter, then ack] [SATISFIES: R4]
  3. Enqueue durably in Store.                              [CODE, IDEMPOTENT, SIDE-EFFECT] [SATISFIES: R2]
     IDEMPOTENT [KEY: correlation_id]
     STATE UPDATE: Store += job (no-op if correlation_id already present)
     RECOVERY: broker redelivery → step 3 is a no-op → proceed to ack
  4. Ack / commit the broker offset.                        [EXTERNAL]
     DURABLE-BEFORE: step 3
     [SATISFIES: R1]

PROCESS Work (INPUT: Store; OUTPUT: —)
  QUEUE [ORDER: PRIORITY then FIFO; ONE_AT_A_TIME]
  1. Claim next QUEUED job: atomic QUEUED → PROCESSING.     [CODE, ATOMIC] [SATISFIES: R5]
     BREAK [IF: no job available]
  2. RETRY [MAX: max_attempts; BACKOFF: exponential]
     2.1 Execute the model call within timeout.             [EXTERNAL, ASYNC]
         ERROR [ON: timeout; THEN: fallback → mark FAILED (terminal)]
         ERROR [ON: transient; THEN: handle → retry per RETRY]
  3. Write terminal result; leave published=false.          [CODE, SIDE-EFFECT]
     STATE UPDATE: Store[job].result, status=terminal, published=false

PROCESS Egress (INPUT: Store, broker; OUTPUT: —)
  1. Take next terminal-but-unpublished result.            [CODE, DETERMINISTIC]
     BREAK [IF: none]
  2. Produce result to broker (results stream or reply_to). [EXTERNAL, ASYNC]
     ERROR [ON: nack/unconfirmed; THEN: fallback → leave unpublished; retry next pass]
  3. Mark published=true in Store.                        [CODE, SIDE-EFFECT]
     DURABLE-BEFORE: step 2 broker ack confirmed
     RECOVERY: crash before step 3 → job stays unpublished → RecoverOnStartup re-emits
     [contributes to EMERGENT R3]

PROCESS RecoverOnStartup (INPUT: Store, broker; OUTPUT: —)
  1. Re-queue jobs left PROCESSING by a crash (respect max_attempts). [CODE] [SATISFIES: R6]
  2. CALL Egress for each unpublished terminal result (drain outbox). [CODE] [SATISFIES: R6]
```

## PROCESS — Narrative (same backbone)

```
PROCESS — RunBridge: bridge a broker to the durable queue.

  1. Recover anything a crash left half-done.
  2. Run three long-lived services concurrently over the shared Store until stopped:
     — Ingest pulls broker messages into the queue.
     — Work runs jobs one at a time.
     — Egress publishes finished results via the transactional outbox.

PROCESS — Ingest: one safe message into the queue.
  Read → parse (or dead-letter poison) → enqueue keyed by correlation_id (idempotent)
  → only then ack the broker. If we crash between enqueue and ack, redelivery is harmless.

PROCESS — Work: one job, serially.
  Atomically claim → retry model call on transient errors → save terminal result unpublished.

PROCESS — Egress: publish one result, exactly once.
  Take unpublished terminal → produce to broker → mark published only after ack.
  Crash between produce and mark → restart re-emits; consumer dedups.
```

---

## STATE REFERENCE (stub)

- **H1 Store** — `{correlation_id (UNIQUE), request, status, result, published}`.
  Shared by all SERVICEs and recovery. Claim is conditional `QUEUED → PROCESSING`.

---

## Stress-test notes

**v2 changes (exercises SPEC v0.9):**

| v1 gap | v2 treatment |
|--------|----------------|
| `PARALLEL … MERGE: none` for perpetual loops | `CONCURRENT { SERVICE … }` |
| Crash windows in CONSTRAINTS prose | `DURABLE-BEFORE` + `RECOVERY` on Ingest/Egress |
| `[IDEMPOTENT]` without key | `IDEMPOTENT [KEY: correlation_id]` |
| R3 spans Ingest+Egress+consumer | `EMERGENT [SATISFIES: R3]` block (SPEC §9) |

**Still open for the spec:**

1. **SERVICE stop/join** — `UNTIL: stop` is named but graceful shutdown semantics
   (drain in-flight, final outbox pass) remain operator prose.
3. **Transport-specific poison paths** — Rabbit DLX vs Kafka manual DLT vs Redis
   PEL recovery differ; this example stays broker-neutral at the PROCESS level.