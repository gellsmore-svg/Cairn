# Tirzah system in Cairn — ingest → memory → ask → observe (composition)

A **composition example** that stitches together the Tirzah slices documented
separately elsewhere in this folder. It does not replace the deep dives; it shows
how an operator-facing **end-to-end local memory workbench** flows across
processes and UIs.

Referenced slices:

- [`tirzah-ingest.cairn.md`](tirzah-ingest.cairn.md) — corpus build
- [`tirzah.cairn.md`](tirzah.cairn.md) — ask (direct · agentic · deep)
- [`tirzah-web-research.cairn.md`](tirzah-web-research.cairn.md) — optional `--web` override
- [`tirzah-generated-output.cairn.md`](tirzah-generated-output.cairn.md) — generated-output trust gate
- [`mahlah.cairn.md`](mahlah.cairn.md) — conversational UI (one session)
- [`mizpah.cairn.md`](mizpah.cairn.md) — trace watchtower (all sessions)
- [`galeed.cairn.md`](galeed.cairn.md) — trace spine emitters read/write

---

## CONTEXT

- **operator** — local user building and querying trusted memory on their machine.
- **corpus** — provenance-aware graph in MongoDB (documents, nodes, profiles).
- **session** — continuity container for asks and trace events.
- **workbench** — Tirzah CLI/API + optional Mahlah/Mizpah front ends.

## REQUIREMENTS

```
R1. Trusted sources SHALL enter the corpus with checksum + archive provenance. [MUST]
R2. The operator SHALL ask questions against ingested memory via a transparent
    retrieval pipeline.                                                     [MUST]
R3. Answers SHALL persist as exchanges keyed by session.                    [MUST]
R4. The operator SHALL observe process/trace without polluting the answer.    [MUST]
R5. Profile gaps SHALL be closable after ingest without re-parsing sources.   [SHOULD]
```

## OUTCOMES

A local operator can grow a corpus, query it with readable diagnostics, continue in
sessions, and audit past runs — the V1 product promise in one composed flow.

EMERGENT [SATISFIES: R4] — answer/process separation is guaranteed by Mahlah's
three-channel UI *and* by Tirzah's trace emission; neither slice alone is the
full UX guarantee.

---

## PROCESS — Formal

```
PROCESS TirzahWorkbench (INPUT: sources, questions; OUTPUT: operating_corpus)
  STATE
    corpus        [scope: global; dir: read/write]  ref: S1
    sessions      [scope: global; dir: read/write]  ref: S2

  1. MILESTONE BUILD — grow the trusted corpus.
     PURPOSE: turn staged files into searchable graph memory.
     DECISION [ON: entry path]
       1a. CALL IngestFolder(sources) → ingest_report          # batch CLI
       1b. CALL EnqueueInbox → CALL RunIngestionWorker        # inbox worker
     STATE UPDATE: corpus += new documents/nodes               [SATISFIES: R1]
  2. MILESTONE PROFILE — close embedding/profile gaps if needed.
     CALL ProfileBackfill(scope=corpus) → backfill_status      [SATISFIES: R5]
  2b. MILESTONE GRAPH (optional) — human-gated semantic edges.
      CALL ReviewSemanticEdges(scope=corpus) → review_summary  # tirzah-semantic-review.cairn.md
  3. MILESTONE ASK — query memory in a session.
     PURPOSE: answer from retrieved context; branch on retrieval_mode (direct/agentic/deep).
     ITERATE [OVER: operator questions]
       DECISION [ON: external evidence needed]
         3a. local only → CALL Ask(user_query, session_id, retrieval_mode) → answer, process_trace
         3b. --web      → CALL AskWithWebResearch(user_query, session_id, web_enabled=true)
       STATE UPDATE: sessions += exchange; process_trace persisted [SATISFIES: R2, R3]
  3b. MILESTONE TRUST (optional) — review generated answers before trusting memory.
      CALL ReviewGeneratedOutput(scope=session) → review_summary  # tirzah-generated-output.cairn.md
  4. MILESTONE OBSERVE — inspect what happened.
     DECISION [ON: observation surface]
       4a. CALL Mahlah.HandleUserTurn / OpenDevLog              # current session UX
       4b. CALL Mizpah.BrowseAndInspect                         # any session audit
     [SATISFIES: R4]
  OUTPUT: operating_corpus
```

## PROCESS — operator profile (rendered view)

```
render-profile: operator

BUILD memory
  Purpose:  Ingest trusted Markdown/text with provenance and dead-letter safety.
  Owner:    Operator
  Next:     backfill profiles if memory-health shows gaps

ASK questions
  Purpose:  Query the corpus; save exchanges per session.
  Owner:    Operator   Assisted by: LLM, retrieval agent
  Iterate-until: operator stops
  Next:     observe via Mahlah (chat) or Mizpah (audit)

OBSERVE runs
  Purpose:  Read process/trace without mixing it into answers.
  Owner:    Operator
  Assisted by: Mahlah process panel / Mizpah session browser
```

## PROCESS — Narrative (same backbone)

```
PROCESS — TirzahWorkbench: the local memory workbench, end to end.

  BUILD — ingest sources (folder or inbox worker), then backfill profiles if needed.
  ASK   — for each question, run the agentic ask path and persist the exchange.
  OBSERVE — use Mahlah for live chat + dev log, or Mizpah to browse any past session.
```

---

## Composition map

| Phase | Delegates to | File |
|-------|----------------|------|
| BUILD (folder) | `IngestFolder` | `tirzah-ingest.cairn.md` |
| BUILD (inbox) | `EnqueueInbox`, `RunIngestionWorker` | `tirzah-ingest.cairn.md` |
| PROFILE | `ProfileBackfill` | `tirzah-ingest.cairn.md` |
| GRAPH (optional) | `ReviewSemanticEdges` | `tirzah-semantic-review.cairn.md` |
| ASK | `Ask`, `RetrieveDirect` / `Agentically` / `Deep`, `PLAN` | `tirzah.cairn.md` |
| ASK (+web) | `AskWithWebResearch`, `ExecuteWebTool` | `tirzah-web-research.cairn.md` |
| TRUST (optional) | `ReviewGeneratedOutput`, `EndorseGeneratedNode` | `tirzah-generated-output.cairn.md` |
| OBSERVE (live) | `HandleUserTurn`, `OpenDevLog` | `mahlah.cairn.md` |
| OBSERVE (audit) | `BrowseAndInspect`, `QueryTrace` | `mizpah.cairn.md` + `galeed.cairn.md` |

---

## Stress-test notes

What worked: top-level **MILESTONE** phases; `DECISION` for ingest entry path and
observation surface; `CALL` composition without duplicating sub-process bodies;
`EMERGENT [SATISFIES]` for UX guarantees spanning backend + UI.

Rough edges:

1. **Direct / deep retrieval modes** — composition hard-codes agentic ask; a
   `DECISION [ON: retrieval_mode]` branch would bloat this doc (keep in `tirzah.cairn.md`).
2. **Generated-output endorsement** — now in `tirzah-generated-output.cairn.md`; optional
   TRUST milestone after ASK.
3. **Machine composition** — no validator checks that `CALL` targets exist across files.