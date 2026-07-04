# Tirzah in Cairn — ask with retrieval modes (direct · agentic · deep)

A Cairn description of **Tirzah as it currently stands**, for the **ask** slice
across all three retrieval modes. One `Ask` PROCESS branches on `retrieval_mode`;
each mode has its own retrieval sub-process before the shared answer + persist steps.

Related: [`tirzah-ingest.cairn.md`](tirzah-ingest.cairn.md) (corpus),
[`tirzah-semantic-review.cairn.md`](tirzah-semantic-review.cairn.md) (graph review),
[`tirzah-system.cairn.md`](tirzah-system.cairn.md) (composition).

---

## CONTEXT

- **Tirzah** — local graph-memory retrieval over MongoDB; answers use retrieved
  context, not whole documents.
- **operator** — human asking in a session (CLI or API).
- **retrieval_mode** — `direct` (single-focus compile), `agentic` (memory-agent
  tool loop), or `deep` (fixed primitive menu + sufficiency-gated rounds).
- **memory-agent** — LLM planner for agentic mode; read-only tool menu.
- **deep primitives** — validated read-only menu (`keyword_search`, `hybrid_search`,
  `semantic_search`, `node_context`, `expand_graph_paths`, …) per ADR-020.
- **hybrid search** — lexical + vector pre-rank when `hybrid_search_enabled` and a
  real embedding adapter are active.

## REQUIREMENTS

```
R1. Answers SHALL be produced over local infrastructure (local Ollama).        [MUST]
R2. Retrieval SHALL be read-only; ask never writes the graph.                  [MUST]
R3. Agentic mode SHOULD choose tools dynamically across turns.                  [SHOULD]
R4. Each answer SHALL persist the exchange and a continuity snapshot.            [MUST]
R5. Source text SHALL be returned as stored, never rewritten at retrieval.      [MUST]
R6. Agentic and deep loops SHALL be bounded.                                    [MUST]
R7. Direct mode SHALL select a focus node (corpus, active document, or given).  [MUST]
```

## OUTCOMES

A saved answer, readable activity log / process trace, and updated session
continuity — with retrieval diagnostics appropriate to the mode chosen.

---

## Recursive plan wrapper — Formal

```
PLAN request-plan REVISION 1 [STATUS: active]
  PARENT: none
  REQUEST: user_query
  TRIGGER: initial_request

  PROCESS PlanAndAsk (INPUT: user_query, session_id; OUTPUT: answer, plan_revision, process_trace)
    STATE
      plan_revision  [scope: process; dir: read/write] ref: T6
    1. Propose and validate a first-pass Cairn process for the request. [LLM, STOCHASTIC, SYNC]
    2. CALL Ask(user_query, session_id, retrieval_mode) → answer, process_trace
    3. Evaluate retrieval and answer evidence as new plan information. [CODE, DETERMINISTIC]
    4. RECURSE [BASE: plan stable | complete | blocked; MAX_DEPTH: planning_max_revisions]
    OUTPUT: answer, plan_revision, process_trace
```

## PROCESS — Formal

```
PROCESS Ask (INPUT: user_query, session_id, retrieval_mode; OUTPUT: answer, process_trace)
  STATE
    used_node_ids   [scope: process;  dir: write]        ref: T1
    identity_excl   [scope: process;  dir: read]         ref: T2
    continuity      [scope: session;  dir: write]        ref: T3
    gathered        [scope: process;  dir: write]        ref: T7

  1. Initialize session; load active agent identity exclusions. [CODE, DETERMINISTIC]
     STATE UPDATE: identity_excl ← exclusions
  2. DECISION [ON: retrieval_mode]
     2a. direct  → CALL RetrieveDirect(user_query, session_id) → gathered      [SATISFIES: R7]
     2b. agentic → CALL RetrieveAgentically(user_query, session_id) → gathered  [SATISFIES: R3]
     2c. deep    → CALL RetrieveDeep(user_query, session_id) → gathered
     STATE UPDATE: gathered ← retrieval result; used_node_ids ← gathered.used_nodes
  3. Generate answer from gathered context only.               [LLM, STOCHASTIC, SYNC] [SATISFIES: R1]
     CONSTRAINTS: do not invent sources; verbatim source policy               [SATISFIES: R5]
  4. Persist exchange + continuity snapshot.                 [CODE, SIDE-EFFECT] [SATISFIES: R4]
     STATE UPDATE: continuity ← {query, used_node_ids, diagnostics, skipped_chunks}
  OUTPUT: answer, process_trace

PROCESS RetrieveDirect (INPUT: query, session_id; OUTPUT: gathered)
  CONSTRAINTS: read-only retrieval; no graph writes. [SATISFIES: R2, R5]
  1. Classify query (corpus search vs active-document reference vs low-intent). [CODE]
  2. DECISION [ON: focus selection]
     2a. use provided focus_node_id
     2b. resolve active-document focus from session                      [SATISFIES: R7]
     2c. search corpus (lexical; hybrid+vector if enabled) → focus node   [SATISFIES: R7]
  3. Compile role-tagged context around focus under char/token budget.    [CODE, DETERMINISTIC]
  4. Build prompt envelope (optional semantic resolver strictness).       [CODE]
  OUTPUT: gathered (prompt envelope, used_nodes, retrieval_status, skipped)

PROCESS RetrieveAgentically (INPUT: query, session_id; OUTPUT: gathered)
  CONSTRAINTS: read-only tool menu only. [SATISFIES: R2, R5]
  STATE
    history     [scope: process;    dir: read/write]  ref: T4
    decision    [scope: iteration;  dir: write]       ref: T5
  1. ITERATE [UNTIL: decision.status = done; MAX: memory_agent_max_iterations] [SATISFIES: R6]
     1.1 Propose next tool batch or stop.                    [LLM, STOCHASTIC, SYNC]
     1.2 Validate parsed decision.                           [CODE]
         ERROR [ON: malformed; THEN: fallback → stop with context gathered so far]
     1.3 DECISION [ON: decision.status] → done: BREAK | continue
     1.4 Execute requested read-only tool calls.            [CODE, BATCH] [SATISFIES: R3]
     1.5 Summarize results; append to history.              [CODE]
  2. Compile context under budget from gathered tool results. [CODE]
  OUTPUT: gathered

PROCESS RetrieveDeep (INPUT: query, session_id; OUTPUT: gathered)
  CONSTRAINTS: fixed validated primitive menu only; read-only. [SATISFIES: R2]
  STATE
    shortlist   [scope: process;    dir: read/write]  ref: T8
    sufficiency [scope: iteration;  dir: write]       ref: T9
  1. ITERATE [UNTIL: sufficiency stop | plateau | max_iterations; MAX: deep_max_iterations] [SATISFIES: R6]
     1.1 Plan next primitive calls from the fixed menu.       [LLM, STOCHASTIC, SYNC]
     1.2 Validate each primitive call (hostile-input guard). [CODE, DETERMINISTIC]
     1.3 Execute primitives (keyword / hybrid / semantic search, paths, …). [CODE, BATCH, READ-ONLY]
     1.4 Gate and shortlist candidates; score sufficiency.   [CODE, DETERMINISTIC]
         STATE UPDATE: sufficiency ← novelty/plateau score (surfaced in process trace)
     1.5 BREAK [IF: sufficiency ≥ stop threshold OR plateau passes exceeded]
  2. Synthesize final answer from shortlist.                [LLM, STOCHASTIC, SYNC]
  OUTPUT: gathered (answer text may be produced inside deep flow; used_nodes from shortlist)
```

## PROCESS — Narrative (same backbone)

```
PROCESS — Ask: one question, three retrieval strategies.

  Set up the session, then branch:
  — **direct:** pick one focus node (from the query, an active document, or corpus
    search), compile its surrounding context, answer once.
  — **agentic:** let the memory-agent loop over read-only tools until done or max
    iterations, then compile and answer.
  — **deep:** run bounded rounds over a fixed primitive menu with sufficiency
    scoring until stop/plateau, then synthesize.

  Always persist the exchange and continuity snapshot. Small local models may answer
  thinly — the activity log and trace show what was retrieved.

PROCESS — RetrieveDirect / RetrieveAgentically / RetrieveDeep: see Formal above.
```

## PROCESS — operator profile (rendered view)

```
render-profile: operator

ASK with chosen retrieval mode
  Purpose:  Get an answer grounded in local memory with mode-appropriate diagnostics.
  Owner:    Operator
  Assisted by: LLM, retrieval controller
  Next:     inspect process trace; optional semantic-edge review on used nodes
```

---

## STATE REFERENCE (stub)

- **T1 used_node_ids** — nodes whose text fed the answer.
- **T2 identity_excl** — label/document exclusions from active agent identity.
- **T3 continuity** — latest `session_continuity` snapshot.
- **T4 history** — agentic planner rounds `{decision, tool_results_summary}`.
- **T5 decision** — parsed agentic decision this iteration.
- **T6 plan_revision** — Cairn PLAN envelope for recursive planning wrapper.
- **T7 gathered** — compiled context package passed to answer step.
- **T8 shortlist** — deep-mode candidate node set.
- **T9 sufficiency** — deep-mode per-round stop signal.

---

## Mode comparison

| Mode | Control | Best for | Bounded by |
|------|---------|----------|------------|
| `direct` | Deterministic focus + compile | Fast, narrow queries | token/char budget |
| `agentic` | LLM picks read-only tools | Exploratory questions | `memory_agent_max_iterations` |
| `deep` | LLM picks from fixed primitives | Broad corpus questions | sufficiency + `deep_max_iterations` |

---

## Stress-test notes

What worked: single `Ask` with `DECISION [ON: retrieval_mode]`; shared persist
step; mode-specific sub-processes; `[BATCH]` on tool/primitive execution.

Addressed since v0.6 notes: `BREAK` for loop exit; `BATCH` for multi-call steps.

Still open:

1. **Low-intent override** — runtime may downgrade agentic → direct; express as
   `MODE:` override annotation on step 2.
2. **Web research promotion** — `--web` forces agentic; cross-cutting modifier.
3. **STATE at CALL boundary** — `gathered` return contract is explicit; sub-process
   STATE remains private (recommended pattern).
4. **Deep answer double-invocation** — deep flow may call the model inside
   `RetrieveDeep` *and* step 3 is skipped/empty prompt; document as mode exception.