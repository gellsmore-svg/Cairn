# Tirzah in Cairn — source ingestion pipeline (representative slice)

A Cairn description of **Tirzah as it currently stands**, for the slice the
agentic `ask` example did not cover: **trusted text/Markdown ingestion** —
checksum, archive copy, duplicate rejection, bounded retries, dead-letter
routing, and resumable embedding/profile backfill.

Scope note: V1 uses deterministic heading/paragraph parsing via the mock ingestion
adapter by default; LLM-assisted chunking is post-V1. This describes the
**worker/queue path** (`enqueue-inbox` → `process-next`) and the **direct CLI
path** (`ingest-one`, `ingest-folder`).

---

## CONTEXT

- **source file** — a text/Markdown file staged under `data/ingest/` (inbox) or
  passed directly to `ingest-one`.
- **checksum** — SHA-256 of raw bytes; dedup key across the corpus.
- **archive** — immutable copy under `data/archive/<prefix>/<checksum>.<ext>`.
- **dead-letter** — `data/dead_letter/duplicate` or `…/failed` for rejected or
  exhausted sources.
- **ingestion queue** — MongoDB `queue` collection of pending jobs (`enqueue-inbox`).
- **ingestion adapter** — parses source into a provenance-aware document tree.
- **profile backfill** — batched, resumable job that embeds/profiles nodes after
  ingestion (does not block the hot ingest path).

## REQUIREMENTS

```
R1. Source bytes SHALL be preserved verbatim at archive time.              [MUST]
    ACCEPTANCE: archive copy equals staged file; graph stores checksum + archive_path.
R2. Duplicate content SHALL be rejected without mutating the graph.          [MUST]
    ACCEPTANCE: identical checksum → rejected + moved to dead_letter/duplicate.
R3. Transient ingest failures SHALL retry up to max_attempts.                [MUST]
R4. Exhausted failures SHALL land in dead_letter/failed and mark job failed. [MUST]
R5. Successful ingest SHALL produce inspectable documents, trees, and nodes. [MUST]
R6. Profile coverage SHALL be backfillable in bounded, resumable batches.    [SHOULD]
    ACCEPTANCE: queue-profile-backfill → process-profile-backfill advances a cursor.
```

## OUTCOMES

Trusted sources become searchable graph memory with provenance; duplicates and
failures land in predictable dead-letter locations; profile gaps can be closed
without re-ingesting.

---

## PROCESS — Formal

```
PROCESS IngestOne (INPUT: source_path, labels; OUTPUT: document_summary)
  1. Compute checksum_sha256 of source_path.                [CODE, DETERMINISTIC]
  2. DECISION [ON: checksum already in corpus]
     2a. reject — return duplicate summary (no graph write)  [CODE] [SATISFIES: R2]
     2b. continue
  3. Read text; run ingestion adapter → document tree.        [CODE, DETERMINISTIC]
  4. Copy source to archive (checksum-keyed path).            [CODE, SIDE-EFFECT] [SATISFIES: R1]
     STATE UPDATE: result.source.archive_path, checksum_sha256
  5. Commit document + nodes to MongoDB (embed on insert).    [CODE, SIDE-EFFECT] [SATISFIES: R5]
  OUTPUT: document_id, node_ids, archive_path

PROCESS IngestFolder (INPUT: folder_path, labels; OUTPUT: ingest_report)
  1. Discover supported files under folder_path.              [CODE, DETERMINISTIC]
  2. Annotate each file with origin_date (explicit content or file metadata).
  3. Sort sources chronologically (origin_date, then path).   [CODE] [SATISFIES: ordering policy]
  4. ITERATE [OVER: sorted sources]
     4.1 CALL IngestOne(source, labels) → per-file result
     4.2 ACCUMULATE inserted / rejected counts
  OUTPUT: ingest_report

PROCESS EnqueueInbox (INPUT: ingest_dir; OUTPUT: queue_summary)
  1. ITERATE [OVER: files in ingest_dir]
     1.1 Compute checksum; enqueue pending job in MongoDB queue.
     1.2 DECISION [ON: duplicate already queued or ingested]
         1.2a. reject job → move file to dead_letter/duplicate   [CODE] [SATISFIES: R2]
         1.2b. leave file in inbox for worker
  OUTPUT: queue_summary

PROCESS ProcessNext (INPUT: queue, config; OUTPUT: job_result)
  STATE
    job           [scope: iteration; dir: read/write]  ref: T-I1
  1. Atomically claim next pending queue job.                 [CODE, ATOMIC]
     BREAK [IF: queue idle]
  2. Start ingestion process_run for observability.          [CODE]
  3. Read source; run ingestion adapter.                      [CODE, DETERMINISTIC]
  4. Copy to archive; attach checksum + archive_path.         [CODE] [SATISFIES: R1]
  5. Commit ingestion to MongoDB (embed on insert).
     ERROR [ON: DuplicateSourceError; THEN: fallback → reject + dead_letter/duplicate] [SATISFIES: R2]
     ERROR [ON: transient; THEN: handle → retry if attempts < max_attempts] [SATISFIES: R3]
     ERROR [ON: exhausted; THEN: fallback → move to dead_letter/failed + fail job] [SATISFIES: R4]
  6. Move source to staging/processed.                        [CODE]
  7. Complete process_run; emit ingestion activity log.        [CODE] [SATISFIES: R5]
  OUTPUT: job_result (completed | rejected | retrying | failed)

PROCESS RunIngestionWorker (INPUT: config; OUTPUT: —)
  CONCURRENT [UNTIL: stop]
    SERVICE InboxWorker → ITERATE [UNTIL: stop] → CALL ProcessNext(queue, config)

PROCESS ProfileBackfill (INPUT: scope, batch_limit; OUTPUT: backfill_status)
  1. Queue a profile/embedding backfill job (label or document scope). [CODE]
  2. ITERATE [UNTIL: job complete OR operator max_batches]
     2.1 Select next batch of nodes missing profiles (cursor-based). [CODE]
     2.2 Generate local text-similarity profiles via non-HTTP worker. [CODE, SIDE-EFFECT]
     2.3 Advance job cursor; record batch counts.                     [CODE]
     RECOVERY: interrupted job resumes from last_node_id cursor       [SATISFIES: R6]
  OUTPUT: backfill_status (pending / running / complete / blocked)
```

## PROCESS — Narrative (same backbone)

```
PROCESS — IngestOne: ingest a single trusted file now.
  Hash it → reject if duplicate → parse → archive an exact copy → commit nodes.

PROCESS — IngestFolder: ingest a folder in chronological order.
  Discover files → sort by origin date → ingest each with IngestOne.

PROCESS — EnqueueInbox + ProcessNext: restart-safe inbox worker.
  Stage files in data/ingest → enqueue jobs → worker claims one at a time,
  archives, commits or dead-letters, then moves successes to staging/processed.

PROCESS — ProfileBackfill: close profile gaps after ingest.
  Queue a resumable job → process bounded batches until scope is covered or blocked.
```

## PROCESS — operator profile (rendered view)

```
render-profile: operator

STAGE sources
  Purpose:  Add trusted Markdown/text to local memory with provenance.
  Owner:    Operator
  Next:     run worker or ingest-one

RUN the inbox worker
  Purpose:  Drain the ingestion queue one job at a time.
  Owner:    Operator (or daemon)
  Iterate-until: queue idle or stop
  Next:     inspect documents; queue profile backfill if coverage is partial

BACKFILL profiles
  Purpose:  Embed/profile nodes that ingested before the adapter was ready.
  Owner:    Operator
  Assisted by: local_command worker
  Next:     memory-health shows improved profile coverage
```

---

## STATE REFERENCE (stub)

- **T-I1 job** — queue record: `{path, checksum_sha256, attempts, status, details}`.

---

## Stress-test notes

What worked: `DECISION` branches for duplicate vs continue; `ERROR THEN: fallback`
for duplicate/transient/exhausted; separate **queue worker** PROCESS vs **direct
IngestOne**; `SERVICE` for long-running inbox drain; profile backfill as a
**second PROCESS** with cursor `RECOVERY`.

Rough edges to feed back:

1. **Best-effort multi-collection commit** — ingestion writes several Mongo
   collections without a transaction; Cairn has no "best-effort rollback" construct
   (noted in Tirzah v1-known-limitations).
2. **IngestFolder vs EnqueueInbox** — two entry paths to the same outcome; Cairn
   could use `VARIANT` or `MODE:` to show alternate entry without duplicating
   ProcessNext internals.
3. **Web upload path** — FastAPI staging uses the same queue but a different
   entry PROCESS (not expanded here).
4. **Relationship to agentic ask** — ingest builds the corpus that
   `tirzah.cairn.md` later retrieves; a top-level `TirzahSystem` composition
   PROCESS could `CALL` both slices for end-to-end documentation.