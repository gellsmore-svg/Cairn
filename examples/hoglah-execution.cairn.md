# Hoglah Job Execution — low-level worker path (based on implementation)

Detailed Cairn description of **Hoglah's internal job execution** inside the client/worker (Hoglah class with start_worker=True). This captures the real code paths from submit through durable claim, retrying execution (with dispatch + adapter), result persistence, delivery, and recovery.

Focuses on the low-level PROCESS mechanics in client.py ( _worker_loop, _process_job, _execute_with_retries, _dispatch, _deliver, _recover... ), store.py (claim, enqueue, set_result), dispatch.py (BackendPool lease), and adapters.py (OllamaAdapter / StubAdapter).

Complements the higher-level bridge view in [`hoglah.cairn.md`](hoglah.cairn.md) and pure-submitter topology in [`hoglah-submit.cairn.md`](hoglah-submit.cairn.md).

---

## CONTEXT

- **Hoglah client** (start_worker=True) — owns the background asyncio worker thread + event loop. Provides submit(), wait(), cancel(), etc.
- **JobStore** (SQLite by default; also Mongo) — durable source of truth. enqueue is idempotent on correlation_id. claim_for_processing is the atomic gate.
- **BackendPool** — warm-affinity + least-loaded dispatch across one or more Ollama hosts (via OllamaAdapter). Tracks inflight + recent models per backend.
- **BaseAdapter** (OllamaAdapter real; StubAdapter for tests) — does the actual generate/chat/embed calls. Returns (output/embedding, usage, metadata including truncation).
- **JobRequest / JobResult** — persisted request (kind, prompt/messages, model, params, callback_key, callback_url, ...); terminal result with status, output/embedding, usage, truncated, error, metadata.
- **Witness / Galeed** (optional) — emits QUEUED/STARTED/COMPLETED/FAILED for tracing.
- **Delivery** — output_dir (atomic json), callback_url (POST with retries in daemon thread), optional message_bridge (Kafka etc.).
- **Recovery** — on init: re-queue PROCESSING jobs; attempt restart callback redelivery for named callbacks.
- **Semaphores / inflight tracking** — limits concurrency; per-job task tracking for cross-thread cancel.
- **correlation_id** — for idempotency (submitter + bridge ingest).

## REQUIREMENTS

```
R1. Enqueue SHALL be idempotent on correlation_id (no duplicate jobs from redeliveries). [MUST]
R2. Claim SHALL be atomic: only one worker owns QUEUED -> PROCESSING. [MUST]
R3. Execution SHALL respect max_retries + timeout_seconds (timeout is terminal, not retried). [MUST]
R4. Transient errors (connection/timeout/5xx/rate) SHALL retry with backoff; permanent/context errors SHALL not. [MUST]
R5. Result SHALL always be written (even on truncation) unless the job was CANCELLED. [MUST]  [ADR-009]
R6. On crash: PROCESSING jobs SHALL be re-queued on next worker start (respecting max_attempts). [MUST]
R7. Delivery (file/callback/bridge) SHALL be best-effort and never block the worker or change terminal status. [MUST]
R8. Cancel during execution SHALL interrupt the in-flight task (cross-thread via loop.call_soon_threadsafe) and record CANCELLED. [MUST]
R9. Direct callbacks (callables) are in-process only; named callback_key are durable (re-delivered on restart if registry supplied). [MUST]
R10. With multi-backend: lease SHALL prefer warm backend for the model, else least-loaded; track inflight + failures. [MUST]
```

## OUTCOMES

Every submitted job reaches exactly one terminal state (COMPLETED / FAILED / CANCELLED). Execution is serialized per concurrency slot, retried only for transients, recovered across restarts, and delivered exactly once where possible. No lost work, no silent duplicates, observable via traces + store.

EMERGENT [SATISFIES: R1,R2,R6]
  via idempotent enqueue + atomic claim + recovery of PROCESSING + best-effort but durable delivery

---

## PROCESS — Formal (low-level worker execution)

```
PROCESS SubmitJob (INPUT: request, Store, client; OUTPUT: job_id)
  1. Normalize request (kind, prompt/messages, model, options, tags, priority, timeout, max_retries, callback_key/url, metadata, ...).  [CODE]
  2. job_id = Store.enqueue(request, correlation_id?, callback_key?)
     IDEMPOTENT [KEY: correlation_id]   [SATISFIES: R1]
     STATE UPDATE: Store += {id: job_id, status: QUEUED, request: ..., created_at, ...}
     (no-op / return existing id if correlation_id seen)
  3. Emit QUEUED witness.
  4. If direct callable callback: remember in _direct_callbacks[job_id] (process lifetime only).
  OUTPUT: job_id

PROCESS WorkerLoop (INPUT: Store, config.concurrency, adapters; OUTPUT: —)
  STATE
    _worker_running   [scope: worker; dir: read/write]
    sem               [scope: worker; dir: read/write]
    _inflight         [scope: worker; dir: read/write]
    _worker_loop_ref  [scope: worker; dir: write]
  1. On start (if start_worker): spawn daemon thread running the worker loop.
  2. ITERATE [UNTIL: not _worker_running]
     a. queued = Store.list(status=QUEUED, limit=10)
     b. FOR each row in queued:
        job_id = row["id"]
        IF job_id already in _inflight: SKIP
        acquire semaphore slot
        create task for _ProcessJob(job_id)
        track task in _inflight
     c. sleep poll interval
  3. On shutdown: drain in-flight tasks (bounded wait), cancel stragglers.
     (PROCESSING jobs left as-is for startup recovery.)

PROCESS _ProcessJob (INPUT: job_id, sem, Store, pool, adapter, witness; OUTPUT: —)
  1. claimed = Store.claim_for_processing(job_id)
     IF not claimed: RETURN
     [ATOMIC: QUEUED → PROCESSING]
  2. row = Store.get(job_id)
     request = JobRequest from row
  3. witness.emit(JOB_STARTED)
  4. result = _ExecuteWithRetries(job_id, request)
  5. latest = Store.get(job_id)
     IF latest.status == CANCELLED: RETURN
     [RACE GUARD]
  6. Store.set_result(job_id, result)
  7. witness.emit( COMPLETED or FAILED )
  8. witness.record_io(...)
  9. CALL _Deliver(result, request)
  10. CALL _FireCallback(job_id, result, callback_key)
     (semaphore released on exit)

PROCESS _ExecuteWithRetries (INPUT: job_id, request; OUTPUT: JobResult)
  1. ITERATE [MAX: request.max_retries + 1]
     TRY:
        payload = _Dispatch(request) [TIMEOUT: request.timeout_seconds]
        build result (handle embed vs text, record truncated if present)
        RETURN result
     ERROR [ON: timeout]:
        record timed_out
        BREAK
     ERROR [ON: transient error]:
        IF more attempts:
           sleep backoff
           CONTINUE
        BREAK
  2. RETURN FAILED result

PROCESS _Dispatch (INPUT: request; OUTPUT: payload)
  1. DECISION [multi backend?]
     yes: lease backend (warm for model preferred, else least loaded); delegate to it
     no: delegate to the single configured adapter

PROCESS AdapterRun (OllamaAdapter; INPUT: request; OUTPUT: (output, usage, meta))
  1. ensure model pulled
  2. compute effective context from model info
  3. DECISION [kind]
     embed: client.embed → vector + usage
     generate/chat: client call → text + usage + done_reason
  4. map done_reason length to truncated metadata
  5. RETURN (errors propagate to retry logic)

PROCESS _Deliver (INPUT: result, request; OUTPUT: —)
  1. IF output dir: atomic file write
  2. IF callback url: background POST with retries
  3. IF bridge: publish result

PROCESS RecoverOnStartup (INPUT: Store; OUTPUT: —)
  1. ITERATE PROCESSING jobs:
     update to QUEUED (recovery note)
     [worker instances only]

PROCESS RedeliverRestartCallbacks (INPUT: Store, registry; OUTPUT: —)
  1. On init:
     for recent terminal jobs with named key present in registry:
        re-attempt delivery and fire
     [note: direct callables are lost when the process exits]

PROCESS Cancel (INPUT: job_id; OUTPUT: bool)
  1. IF terminal: return false
  2. mark CANCELLED, persist result, deliver
  3. interrupt in-flight task if owned by this worker
     [CANCELLED result is authoritative]
```

## PROCESS — operator profile (rendered view)

```
render-profile: operator

SUBMIT job (client.submit)
  Purpose: Persist a model request for later execution by a worker (this process or daemon).
  Owner:   Caller (Tirzah, script, ...)
  Assisted-by: Hoglah client + Store
  Next:    worker claims it

WORKER POLL + CLAIM
  Purpose: Find QUEUED work and atomically take ownership.
  Owner:   Background worker loop
  1. List QUEUED (priority/FIFO)
  2. claim_for_processing (QUEUED → PROCESSING)
     [ATOMIC]

EXECUTE WITH RETRIES + DISPATCH
  Purpose: Run the model (respecting timeout, retries, warm backends).
  Owner:   _process_job + _execute + pool.lease + adapter
  1. lease backend (warm for model or least-loaded)
  2. adapter.run / embed (ollama or stub)
  3. on transient: backoff + retry (up to max_retries)
  4. on timeout or permanent: FAILED
  5. on success (even truncated): COMPLETED + metadata

PERSIST + DELIVER + CALLBACK
  Purpose: Make the terminal result durable and visible to submitter.
  1. set_result (status + full JobResult)
  2. deliver (atomic file, POST callback_url, bridge)
  3. fire callback (direct or registry key)

RECOVERY (on worker start)
  Purpose: Survive crashes without loss or duplication.
  - Re-queue any left in PROCESSING
  - Re-attempt named callback delivery for recent terminals
```

## STRESS NOTES (from actual implementation)

- Atomic claim + inflight tracking prevents double execution even under polling.
- Timeout is hard terminal (cancels the generation task).
- Context truncation is always reported, never silent (ADR-009).
- Delivery is best-effort and fire-and-forget (never blocks worker or alters status).
- Direct callbacks are ephemeral; only callback_key + registry survive restarts.
- Multi-backend: warm-affinity first (to avoid reloads), then least-loaded; short failure cooldowns.
- Idempotency at enqueue (correlation_id) + best-effort at egress.
- The priority_queue.py is a separate in-process primitive (not the main durable worker path).

This description is derived directly from the implementation in client.py, store.py, dispatch.py, adapters.py, and models.py (as of the current codebase).
