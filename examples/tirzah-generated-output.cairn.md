# Tirzah in Cairn — generated-output endorsement (representative slice)

A Cairn description of **Tirzah's trust gate for model-generated memory** — how
LLM answers are queued after an exchange, ingested as **unreviewed** graph nodes,
and only promoted to trusted memory through explicit operator endorsement or
rejection.

This slice complements ask (`tirzah.cairn.md`) and semantic-edge review
(`tirzah-semantic-review.cairn.md`): ask produces answers; output ingestion
materializes them as reviewable nodes; endorsement decides what retrieval may
treat as human-trusted.

---

## CONTEXT

- **exchange** — persisted ask result (query, answer, used nodes, process trace).
- **output-ingestion job** — pending row in `output_ingestion_queue`, keyed by
  `exchange_id` with content-hash dedup.
- **generated-output node** — graph node labelled `generated_output` +
  `llm_answer`, default `endorsement_label=unreviewed`.
- **endorsement label** — `unreviewed` | `implicit_endorsed` | `explicit_endorsed`
  | `rejected`; only `generated_output` nodes may be updated via review controls.
- **operator** — human reviewer in CLI (`review-generated-output`, `endorse-node`)
  or web developer mode (`/api/review/...`).

## REQUIREMENTS

```
R1. Every non-empty answer SHALL be queued for output ingestion after persist.  [MUST]
    ACCEPTANCE: save_exchange calls queue_exchange_output; exchange links job_id.
R2. Ingested generated output SHALL enter the graph as unreviewed only.         [MUST]
    ACCEPTANCE: output_job_to_ingestion_result sets DEFAULT_ENDORSEMENT_LABEL.
R3. Endorsement or rejection SHALL require explicit operator action.            [MUST]
    ACCEPTANCE: update_node_endorsement rejects non-generated_output nodes.
R4. Duplicate answer content SHALL NOT create duplicate graph documents.        [MUST]
    ACCEPTANCE: content_hash_sha256 dedup; DuplicateSourceError → rejected job.
R5. Review surfaces SHALL list nodes filterable by endorsement label.           [SHOULD]
R6. Retrieval ranking MAY demote unreviewed generated output until endorsed.    [SHOULD]
```

## OUTCOMES

Model answers become inspectable memory candidates — never silently trusted —
with a clear audit trail of who endorsed or rejected what.

---

## PROCESS — Formal

```
PROCESS ReviewGeneratedOutput (INPUT: scope; OUTPUT: review_summary)
  1. MILESTONE QUEUE — ensure exchanges have pending output jobs.
     NOTE: queueing happens inside save_exchange after Ask; this milestone is
     for operator-driven replay or backlog drain.
     CALL ListOutputJobs(status=pending, scope) → pending_jobs              [CODE]
  2. MILESTONE INGEST — materialize queued answers as unreviewed nodes.
     ITERATE [OVER: pending_jobs | UNTIL: idle]
       CALL ProcessNextOutputJob(job_id) → ingest_result                    [CODE, SIDE-EFFECT]
       CONSTRAINTS: commit via guarded commit_ingestion; no auto-endorsement [SATISFIES: R2]
       ERROR [ON: duplicate_output_checksum; THEN: mark job rejected]        [SATISFIES: R4]
     STATE UPDATE: exchange.output_node_ids ← result.node_ids
  3. MILESTONE INSPECT — list generated-output nodes for review.            [CODE] [SATISFIES: R5]
     CALL ListGeneratedOutputNodes(endorsement_label=unreviewed, limit) → nodes
  4. ITERATE [OVER: nodes the operator chooses to act on]
     4.1 Present query, answer preview, provenance, used_node_ids.
     4.2 AWAIT [EVENT: operator endorse or reject; TIMEOUT: never]          [HUMAN, GATED]
     4.3 CALL EndorseGeneratedNode(node_id, endorsement_label, reviewer, note) → result
  OUTPUT: review_summary (ingested_count, endorsed_count, rejected_count)

PROCESS ProcessNextOutputJob (INPUT: job_id?; OUTPUT: ingest_result)
  1. Claim next pending job (status pending → processing).                    [CODE]
  2. CALL output_job_to_ingestion_result(job) → IngestionResult              [CODE]
     CONSTRAINTS: labels include generated_output, llm_answer; endorsement unreviewed [SATISFIES: R2]
  3. CALL commit_ingestion(result) → document_id, tree_id, node_ids         [CODE, SIDE-EFFECT]
  4. Link exchange.output_document_id / output_node_ids; record active docs. [CODE]
  5. Mark job completed (or rejected/failed on error).                        [CODE]
  OUTPUT: ingest_result

PROCESS EndorseGeneratedNode (INPUT: node_id, endorsement_label; OUTPUT: node_state)
  1. Validate endorsement_label ∈ allowed set.                                [CODE]
  2. Load node; reject if labels lack generated_output.                       [CODE] [SATISFIES: R3]
  3. Update endorsement_label, provenance, metadata.review_history.           [CODE, SIDE-EFFECT, GATED, HUMAN]
  OUTPUT: node_state
```

## PROCESS — operator profile (rendered view)

```
render-profile: operator

DRAIN output queue
  Purpose:  Turn saved answers into inspectable unreviewed memory nodes.
  Owner:    Operator (or background worker)
  Assisted by: output_ingestion worker / CLI process command
  Next:     inspect unreviewed nodes

REVIEW generated answers
  Purpose:  Explicitly endorse trustworthy output or reject noise.
  Owner:    Operator
  Iterate-until: queue drained or operator stops
  Outputs:  explicit_endorsed / rejected nodes with review_history
```

## PROCESS — Narrative (same backbone)

```
PROCESS — ReviewGeneratedOutput: trust gate for model memory.
  List pending jobs → process each into unreviewed generated_output nodes → list
  unreviewed → for each one the operator cares about, endorse or reject explicitly.

No step upgrades endorsement without human action.
```

---

## Endorsement labels

| Label | Meaning | Retrieval hint |
|-------|---------|----------------|
| `unreviewed` | Default after ingest; not human-trusted | demoted in search scoring |
| `implicit_endorsed` | Soft trust (rare; policy-driven) | neutral/boost per policy |
| `explicit_endorsed` | Operator affirmed | boosted in search scoring |
| `rejected` | Operator discarded | penalized / excluded |

---

## Stress-test notes

What worked: `MILESTONE` QUEUE/INGEST/INSPECT/REVIEW phases; parallel shape to
semantic-edge review; `AWAIT` human gate; clear split between automatic queue
(R1) and gated endorsement (R3).

Rough edges:

1. **Automatic queue vs manual drain** — queue is side-effect of `save_exchange`;
   modelling as nested CALL from `Ask` step 4 would couple ask + trust slices.
2. **Two nodes per job** — root + answer chunk; endorsement targets the chunk the
   operator sees; Cairn has no `PRIMARY` node annotation yet.
3. **Relation to semantic review** — sibling PROCESS; both are human-gated writes
   with different promotion targets (edge vs endorsement_label).