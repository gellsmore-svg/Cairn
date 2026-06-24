# Tirzah in Cairn — agentic retrieval `ask` (representative slice)

A Cairn description of **Tirzah as it currently stands**, for one representative
slice: answering a user query in **agentic** retrieval mode (`retrieval_mode =
"agentic"`). This exercises STATE, a bounded iterative LLM loop, read-only tool
use, a DECISION, composition (`CALL`), tags, and requirements traceability.

Scope note: this is the *agentic* path. Tirzah also has a simpler `direct` mode.
The hybrid lexical+vector pre-rank inside `search_nodes` is opt-in
(`runtime.hybrid_search_enabled` + a real embedding adapter).

---

## CONTEXT

- **Tirzah** is a local graph-memory retrieval layer. Documents are ingested into
  provenance-aware trees of nodes in MongoDB; answers are produced by a local
  Ollama model reasoning over *retrieved* context, not whole documents.
- **operator** — the human asking a question in a session.
- **session** — a conversation; carries continuity state across turns.
- **memory-agent** — the local LLM acting as a retrieval planner: it chooses
  read-only tools to gather context before the answer is written.
- **tool menu (read-only)** — `search_nodes`, `compile_context`,
  `get_node_context`, `get_document`.

## REQUIREMENTS

```
R1. Answers SHALL be produced over local infrastructure (local Ollama).   [MUST]
    ACCEPTANCE: no mandatory cloud call in the default path.
R2. Retrieval tools SHALL be read-only; retrieval never writes the graph.  [MUST]
    ACCEPTANCE: the agent can call only the four read-only tools.
R3. The agent SHOULD choose tools dynamically across turns (not a fixed pipeline). [SHOULD]
R4. Each answer SHALL persist the exchange and a restart-state snapshot.    [MUST]
R5. Source text SHALL be returned as stored, never rewritten at retrieval.  [MUST]
R6. The agent loop SHALL be bounded.                                        [MUST]
    ACCEPTANCE: it stops at `memory_agent_max_iterations` regardless of model output.
```

## OUTCOMES

A saved answer plus a readable activity log / process trace; the session's
continuity snapshot is updated so the next turn can resume.

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
       CONSTRAINTS: bounded steps; no implicit tool or side-effect authority.
       STATE UPDATE: plan_revision ← revision 1
    2. CALL Ask(user_query, session_id) → answer, process_trace
    3. Evaluate retrieval and answer evidence as new plan information. [CODE, DETERMINISTIC]
    4. RECURSE [BASE: plan stable | complete | blocked; MAX_DEPTH: planning_max_revisions]
       STATE UPDATE: plan_revision ← complete replacement plan with parent lineage
    OUTPUT: answer, plan_revision, process_trace
```

## PROCESS — Formal

```
PROCESS Ask (INPUT: user_query, session_id; OUTPUT: answer, process_trace)
  STATE
    used_node_ids   [scope: process;  dir: write]        ref: T1
    identity_excl   [scope: process;  dir: read]         ref: T2
    continuity      [scope: session;  dir: write]        ref: T3

  1. Initialize the session; load the active agent identity (label/document
     exclusions).                                              [CODE, DETERMINISTIC]
     STATE UPDATE: identity_excl ← active identity exclusions
  2. CALL RetrieveAgentically(user_query, session_id) → gathered_context
                                                               [SATISFIES: R3]
  3. Generate the final answer from gathered_context.          [LLM, STOCHASTIC, SYNC] [SATISFIES: R1]
     CONSTRAINTS: answer only from retrieved/provided context; do not invent sources.
     STATE UPDATE: used_node_ids ← nodes present in gathered_context
  4. Persist the exchange and a restart-state snapshot.        [CODE, DETERMINISTIC, SIDE-EFFECT] [SATISFIES: R4]
     STATE UPDATE: continuity ← {query, used_node_ids, controller_decision,
                                 evidence_summary, skipped_chunks}
  OUTPUT: answer, process_trace
  RISKS: a small local model may answer thinly; the activity log + trace expose
         exactly what was retrieved and used.

PROCESS RetrieveAgentically (INPUT: query, session_id; OUTPUT: gathered_context)
  CONSTRAINTS: tools are READ-ONLY (search_nodes, compile_context,
               get_node_context, get_document); no graph writes. [SATISFIES: R2, R5]
  STATE
    history     [scope: process;    dir: read/write]  ref: T4
    decision    [scope: iteration;  dir: write]       ref: T5

  1. ITERATE [UNTIL: decision.status = done; MAX: memory_agent_max_iterations]  [SATISFIES: R6]
     1.1 Propose the next decision — which read-only tools to call, or stop.    [LLM, STOCHASTIC, SYNC]
         CONSTRAINTS: choose only from the tool menu; emit a structured plan.
     1.2 Validate and parse the proposed decision.                              [CODE, DETERMINISTIC]
         ERROR [ON: malformed; THEN: fallback] → stop with the context gathered so far.
     1.3 DECISION [ON: decision.status] → done: exit loop | continue: run tools
     1.4 Execute the requested tool calls.                                      [CODE, DETERMINISTIC]
         CONTEXT: search_nodes may blend lexical + query-vector when hybrid
                  search is enabled with a real embedder.
     1.5 Summarize tool results; append to history.                            [CODE, DETERMINISTIC]
         STATE UPDATE: history += {decision, tool_results_summary}
  2. Compile role-tagged context (focus, ancestors, siblings, descendants)
     under the character budget.                                              [CODE, DETERMINISTIC] [SATISFIES: R5]
  OUTPUT: gathered_context  (compiled context + the nodes used and the
          considered-but-skipped chunks)
```

## PROCESS — Narrative (same backbone)

```
PROCESS — Ask: answer a user's query in a session.

  1. Set up the session and load the agent's identity, which says what labels and
     documents this agent isn't allowed to see.
  2. Gather context by running the agentic retrieval process below.
  3. The model writes the final answer using only the gathered context — it must
     not invent sources. Record which nodes it used.
  4. Save the exchange and a restart snapshot (the query, the nodes used, the
     controller's decision, an evidence summary, and what was considered but
     left out), so the next turn can resume.

  Risk: a small local model can answer thinly, so the readable activity log and
  trace always show exactly what was retrieved and used.

PROCESS — RetrieveAgentically: let the model gather context with read-only tools.

  1. Loop — at most `memory_agent_max_iterations` rounds:
     1.1 The model proposes what to do next: call some read-only tools, or stop.
     1.2 Check and parse that proposal. If it's malformed, stop and use whatever
         context has been gathered so far.
     1.3 If the model says it's done, leave the loop; otherwise run its tools.
     1.4 Run the requested tools (search, compile context, fetch a node or
         document). Search can mix keyword and vector relevance when hybrid
         search is switched on with a real embedding model.
     1.5 Summarize what came back and add it to the running history.
  2. Compile the surrounding context (the focus node plus its ancestors, nearby
     siblings, and descendants) up to the character budget.

  Result: the compiled context, the nodes it used, and the chunks it considered
  but dropped.
```

---

## STATE REFERENCE (stub)

The definitive definitions these `ref:` numbers point to (format TBD per spec
§6). Sketched here for the slice:

- **T1 used_node_ids** — IDs of nodes whose text fed the answer (deduped).
- **T2 identity_excl** — label + document exclusions from the active agent identity.
- **T3 continuity** — the `session_continuity` snapshot for the session (latest
  prompt iteration; supersedes the prior one).
- **T4 history** — per-Ask list of `{decision, tool_results_summary}` driving the loop prompt.
- **T5 decision** — the parsed memory-agent decision this round: `{status,
  tool_calls, controller_decision, confidence}`.

---

## Stress-test notes (gaps surfaced for the spec)

What worked: the three modes, `CALL` composition, `ITERATE [UNTIL/MAX]`,
read-only constraint as a PROCESS-level `CONSTRAINTS`, tag dimensions, and
`[SATISFIES: R#]` traceability all mapped cleanly onto real code.

Rough edges to feed back into v0.6:
1. **DECISION-to-exit-a-loop is awkward.** Step 1.3 both branches *and* breaks the
   enclosing ITERATE. Cairn needs a clear way to express "exit/continue the
   current loop" (a `BREAK`/`CONTINUE`, or letting `ITERATE UNTIL` reference a
   value the body sets). Right now it's implicit.
2. **A step that is itself an LLM tool-batch** (1.4) hides real fan-out (it runs N
   tool calls). Is that a `PARALLEL`, or just one step? Spec should say how to
   show "one step, many calls" without forcing PARALLEL.
3. **STATE direction at the call boundary.** `CALL` passes/returns values, but the
   relationship between a sub-process's STATE and the caller's isn't expressed.
   Either declare shared state at the boundary, or treat sub-process STATE as
   private (recommended) — the spec is silent.
4. **`ERROR ... THEN: fallback`** needs to name *what* the fallback is (here:
   "stop with current context"). Modifier should allow a short target, not just a
   mode.
5. **Iteration-scoped STATE** (`decision`, T5) reads well, but the spec should
   confirm it resets each round (it does here) vs. persists.
