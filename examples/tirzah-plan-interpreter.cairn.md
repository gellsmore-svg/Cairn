# Tirzah in Cairn — interpretive PLAN execution (target slice)

A Cairn description of **step-by-step PLAN interpretation** — how a runtime walks
a versioned machine plan in `depends_on` order, dispatches `CALL` steps through a
handler registry constrained by `allowed_tools`, and emits per-step status +
trace.

This is the evolution beyond [`tirzah-recursive-planning.cairn.md`](tirzah-recursive-planning.cairn.md)
(descriptive plan around a monolithic executor). Cairn SPEC §4.6 normatively
defines the step state machine.

---

## CONTEXT

- **interpreter** — Python runtime that owns status transitions and handler dispatch.
- **planner** — LLM that proposes/revises plans; never widens `allowed_tools`.
- **handler registry** — `tool_name → callable(step, context)`; subset of runtime whitelist.
- **execution context** — `query`, `session_id`, `artifacts` (step id → output), `trace`.
- **ready set** — steps whose `depends_on` are all `completed`.
- **degenerate mode** — one `CALL` + `tirzah_retrieval` handler runs the legacy full pipeline.

## REQUIREMENTS

```
R1. A step SHALL run only when every depends_on step is completed.              [MUST]
R2. CALL dispatch SHALL use only handlers named in step.allowed_tools.           [MUST]
R3. Unknown tools or constructs without handlers SHALL mark the step blocked.     [MUST]
    ACCEPTANCE: no silent fallback to full pipeline unless that handler is registered.
R4. Step status SHALL transition pending → active → completed|blocked|skipped.  [MUST]
R5. Each transition SHALL append to an interpretation trace.                      [MUST]
R6. tirzah_retrieval SHALL execute at most once per plan interpretation.           [SHOULD]
    ACCEPTANCE: duplicate CALL steps skip with reason duplicate_effect.
R7. Planner revisions SHALL replace the backbone; interpreter resumes on pending. [SHOULD]
R8. Interpretation trace SHALL remain separate from the conversational answer.    [MUST]
```

## OUTCOMES

Operators and orchestrators see **honest per-step progress** — which planned actions
ran, which were blocked, and what artifacts each step produced — not only a
post-hoc narrative after a monolithic ask.

---

## PROCESS — Formal

```
PROCESS InterpretPlan (INPUT: plan, query, session_id; OUTPUT: execution_result, updated_plan)
  STATE
    artifacts     [scope: process; dir: read/write]  ref: X1
    completed     [scope: process; dir: write]       ref: X2  # set of step ids
    trace         [scope: process; dir: write]       ref: X3

  1. Validate plan via cairn.validate_plan.                                   [CODE] [SATISFIES: R1 precursor]
  2. ITERATE [UNTIL: no ready steps remain; MAX: step_count + 1]
     2.1 Compute ready = steps where status=pending and depends_on ⊆ completed. [CODE]
     2.2 BREAK [IF: ready is empty]
     2.3 For each step in ready (document order):
         2.3.1 STATE UPDATE: step.status ← active
               EMIT plan.step.started                                               [SATISFIES: R5]
         2.3.2 DECISION [ON: step.construct]
           a. STEP → CALL AcknowledgeStep OR stochastic handler if tagged LLM
           b. CALL → CALL DispatchCall(step, handler_registry) → artifact
               CONSTRAINTS: pick first allowed_tool with registered handler         [SATISFIES: R2]
               ERROR [ON: no handler; THEN: status ← blocked]                       [SATISFIES: R3]
           c. RECURSE → status ← skipped (outer revision loop owns recursion)
           d. ITERATE → run direct body steps up to MAX with until: criteria
           e. DECISION → evaluate ON: signal, skip unselected branch steps
         2.3.3 STATE UPDATE: artifacts[step.id] ← artifact; completed += step.id
               step.status ← completed | blocked | skipped                           [SATISFIES: R4]
               EMIT plan.step.completed | plan.step.blocked | plan.step.skipped
  3. Merge interpretation trace into process_trace (not answer text).           [CODE] [SATISFIES: R8]
  OUTPUT: execution_result (primary artifact e.g. retrieval_result), updated_plan

PROCESS DispatchCall (INPUT: step, registry; OUTPUT: artifact)
  1. DECISION [ON: allowed_tools ∩ registry.keys()]
     1a. tirzah_retrieval → CALL RunRetrievalPipeline(query, session_id)       [CODE, SIDE-EFFECT]
         CONSTRAINTS: skip if retrieval already ran (duplicate_effect)           [SATISFIES: R6]
     1b. answer_adapter → return artifacts[retrieval_step] or synthesize only   [CODE]
     1c. coherence_check | specialist → CALL MilcahSpecialist(step, query)      [EXTERNAL]
     1d. web_search | web_fetch → CALL ExecuteWebTool (web slice)               [EXTERNAL]
  2. Validate artifact against step.success_criteria (best-effort).             [CODE]
  OUTPUT: artifact
```

## PROCESS — operator profile (rendered view)

```
render-profile: operator

WALK the plan
  Purpose:  Execute each planned step in order, gated by dependencies and tools.
  Owner:    Python interpreter
  Assisted by: handler registry (retrieval, answer, specialist, web)
  Iterate-until: no ready steps remain
  Outputs:  per-step status + interpretation trace
  Next:     revise plan from execution evidence (recursive-planning slice)
```

## PROCESS — Narrative (same backbone)

```
PROCESS — InterpretPlan: the plan becomes the conductor.
  Validate → repeat: find ready pending steps → activate → dispatch by construct →
  record artifact → mark completed/blocked/skipped → emit trace.

Contrast with deep retrieval (tirzah.cairn.md RetrieveDeep): that loop interprets
*primitives* inside one PROCESS; InterpretPlan interprets *plan steps* across a
whole request PLAN.
```

---

## Handler registry (Tirzah v1)

| Tool | Handler behaviour |
|------|-------------------|
| `tirzah_retrieval` | `retrieve_for_answer` — context only, no LLM answer / persist |
| `answer_adapter` | `synthesize_from_retrieval` or `synthesize_from_context_bundle` |
| `search_nodes` | `execute_search_nodes_tool` → append to `context_bundle.tool_results` |
| `compile_context` | `compile_context` on focus node or latest search hit → append to bundle |
| `get_node_context` | Parent/child slice for resolved focus node |
| `get_graph_edges` | Typed edges for resolved focus node |
| `expand_proximity` | One-hop related nodes + optional compiled contexts |
| `expand_graph_paths` | Bounded multi-hop path expansion |
| `semantic_candidates` | Label-overlap candidate nodes (read-only) |
| `list_documents` / `list_active_documents` | Corpus / session document indexes |
| `get_document` / `get_document_tree` | Document metadata from compile step or kwargs |
| `coherence_check`, `milcah`, … | `run_planned_specialist` for matching step |
| `web_search`, `web_fetch` | Bounded web research when enabled; fetch uses latest search URL |

Granular tools accumulate into `context_bundle`; synthesis builds an agentic
envelope from the bundle when no monolithic `retrieval_package` exists.
Ask responses may include `context_bundle_summary` and `plan_execution` (compact
execution row) when interpretive mode persists state.

Steps without a matching handler → `blocked` with `reason: no_handler`.

---

## Agentic steps under interpretation

| Step kind | Agentic? | How |
|-----------|----------|-----|
| Planner-proposed `STEP` "Interpret request" | Potential | Acknowledged without LLM in v1; could add `[LLM, STOCHASTIC]` micro-call later |
| `CALL tirzah_retrieval` | **Yes** (inside handler) | Full ask pipeline may run agentic retrieval |
| `CALL coherence_check` | **Yes** | Milcah stochastic rounds |
| `RECURSE` on revision 1 | Deferred | `skipped` — revision loop handles recursion |
| Interpreter loop itself | No | `[CODE, DETERMINISTIC]` ready-set walk |

---

## Stress-test notes

What worked: SPEC §4.6 state machine maps to JSON `step.status`; `depends_on` DAG;
`DispatchCall` reuses existing Tirzah seams; deep-mode primitive loop as analogy.

Rough edges:

1. **Deep mode** — `tirzah_retrieval` runs `run_deep_retrieval` (chunks only);
   `answer_adapter` runs `synthesize_answer` over `useful_chunks` and persists.
   Legacy `pre_built_answer` packages still persist without a second adapter call.
2. **Construct subset** — v1 expands direct-body `ITERATE`/`DECISION` only; nested
   branch trees and BREAK/CONTINUE are not modelled yet.
3. **Resume after restart** — `plan_executions` collection persists running state;
   interpreter reloads completed steps + artifacts and continues from `pending`.
4. **PLAN revision mid-flight** — concurrent revision + interpretation ordering
   is implementation-defined; safest rule: finish current step, then apply revision.