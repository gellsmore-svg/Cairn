# Tirzah in Cairn — recursive PLAN execution (representative slice)

A Cairn description of **Tirzah's live, revisable execution plans** — how an LLM
proposes a versioned `PLAN`, Python validates it against Cairn conformance,
executes the existing ask pipeline, then revises the plan from new evidence.

This is the operational answer to "how does Cairn become a live execution plan
for recursive LLM work?" — see also the PLAN wrapper in
[`tirzah.cairn.md`](tirzah.cairn.md) and Cairn SPEC §4.5.

---

## CONTEXT

- **PROCESS** — reusable flow template (e.g. `Ask`, `FulfilRequest`).
- **PLAN** — one live instance: `plan_id`, `REVISION n`, `STATUS`, `TRIGGER`,
  complete backbone for this request.
- **machine plan** — JSON dict (`objective`, `steps[]`, `stopping_conditions`,
  `revision_decision`) validated by `cairn.validate_plan`.
- **cairn_text** — rendered Cairn prose (`PLAN … PROCESS FulfilRequest …`) stored
  alongside the machine plan for humans.
- **planner** — LLM that proposes/revises plans only; does not execute tools.
- **executor** — Python-owned ask pipeline (`answer_query`); owns side effects.

## REQUIREMENTS

```
R1. The planner SHALL propose plans, not execute them.                          [MUST]
R2. Every plan revision SHALL pass Cairn machine conformance validation.        [MUST]
    ACCEPTANCE: cairn.validate_plan(plan.to_dict()) == [].
R3. Revisions SHALL be complete replacements, not ambiguous patches.            [MUST]
R4. LLM-driven revision SHALL be bounded (planning_max_revisions, max_steps).   [MUST]
R5. Plan state SHALL persist separately from trusted graph memory.              [MUST]
    ACCEPTANCE: recursive_plans collection; not auto-endorsed.
R6. Step allowed_tools SHALL be filtered to a runtime whitelist.                [MUST]
R7. Execution SHALL proceed even if the planner returns malformed JSON.         [MUST]
    ACCEPTANCE: fallback_plan with bounded RECURSE step.
```

## OUTCOMES

Each user request gets a versioned, inspectable process plan that evolves as
retrieval/answer evidence arrives — without treating the plan itself as memory.

---

## PROCESS — Formal

```
PLAN request-plan REVISION 1 [STATUS: active]
  PARENT: none
  REQUEST: user_query
  TRIGGER: initial_request

  PROCESS PlanAndExecute (INPUT: user_query, session_id; OUTPUT: answer, request_plan, plan_revisions)
    STATE
      plan          [scope: request; dir: read/write]  ref: P1
      revisions     [scope: request; dir: write]       ref: P2

    1. Propose first-pass plan from request + planning context.  [LLM, STOCHASTIC, SYNC] [SATISFIES: R1]
       CALL create_initial_plan(user_query, context) → plan
       CALL cairn.validate_plan(plan) → errors
       ERROR [ON: errors nonempty OR malformed JSON; THEN: fallback_plan]       [SATISFIES: R7]
       CONSTRAINTS: filter step.allowed_tools to ALLOWED_PLAN_TOOLS whitelist   [SATISFIES: R6]
       STATE UPDATE: plan ← validated plan; save_plan_revision(plan)            [SATISFIES: R5]
    2. Execute the governed ask pipeline (unchanged product path).              [CODE, SIDE-EFFECT]
       CALL executor(db, config, query=user_query, session_id) → result
       CONSTRAINTS: executor owns retrieval, model calls, persistence — not the planner
    3. Extract new_information from result (retrieval_status, used_nodes, preview). [CODE]
    4. RECURSE [BASE: revision_decision ∈ {stable, complete, blocked} OR revision ≥ max; MAX_DEPTH: planning_max_revisions]
       4.1 Revise plan from new_information.                    [LLM, STOCHASTIC, SYNC]
           CALL revise_plan(plan, new_information) → next_revision
           CONSTRAINTS: complete replacement backbone; preserve bounds            [SATISFIES: R3, R4]
           CALL cairn.validate_plan(next_revision) → errors                        [SATISFIES: R2]
       4.2 STATE UPDATE: revisions += next_revision; save_plan_revision
       4.3 BREAK [IF: revision_decision ∈ {stable, complete, blocked}]
    5. Attach request_plan + plan_revisions + plan_trace to result.             [CODE]
    OUTPUT: answer, request_plan, plan_revisions, process_trace
```

## PROCESS — operator profile (rendered view)

```
render-profile: operator

PLAN the work
  Purpose:  Sketch how the request will be fulfilled before and after evidence arrives.
  Owner:    Planner LLM (proposes only)
  Assisted by: Python validator, planning context from prior sessions
  Outputs:  versioned PLAN with objective + steps + stopping conditions
  Next:     run the normal ask pipeline

EXECUTE then REVISE
  Purpose:  Do the real retrieval/answer work, then update the plan if evidence changed it.
  Owner:    Python executor (Tirzah ask pipeline)
  Iterate-until: plan stable, complete, blocked, or revision limit
  Next:     inspect activity log "Request Plan" section and plan_revisions API
```

## PROCESS — Narrative (same backbone)

```
PROCESS — PlanAndExecute: plan first, execute for real, revise from facts.
  LLM drafts revision 1 → Python validates and saves → executor runs ask →
  evidence bundle feeds a bounded RECURSE of plan revisions → final plan returned
  alongside the answer.

The plan is operational telemetry. Promoting its claims into trusted memory is a
separate governed action (tirzah-generated-output.cairn.md).
```

---

## Machine plan step shape

Each step in the JSON plan carries execution hints the runtime may enforce:

| Field | Role |
|-------|------|
| `id` | Stable step identity + `depends_on` graph |
| `action` | Human/LLM-readable intent (becomes Cairn step prose) |
| `construct` | `STEP` · `CALL` · `ITERATE` · `DECISION` · `RECURSE` |
| `status` | `pending` · `active` · `completed` · `blocked` · `skipped` |
| `allowed_tools` | Whitelisted tool names (e.g. `tirzah_retrieval`, `web_search`) |
| `success_criteria` | What "done" means for this step |

Rendered Cairn text is derived automatically (`render_cairn_plan`); humans read
`cairn_text`, machines read the JSON dict.

---

## Agentic steps in this slice

Cairn has no single `AGENTIC` tag. Agentic *potential* shows up as:

| Signal | Where | Meaning |
|--------|-------|---------|
| `[LLM, STOCHASTIC]` | steps 1, 4.1 | Model proposes plan content; non-deterministic |
| `RECURSE` + `MAX_DEPTH` | step 4 | Bounded self-revision loop |
| `allowed_tools` on `CALL` steps | machine plan | Which tools the executor *may* use when it reaches that step |
| `revision_decision` | plan envelope | `revise` continues recursion; `stable`/`complete`/`blocked` stop |

Steps tagged `[CODE, DETERMINISTIC]` (validate, save, execute wrapper) are
**not** agentic — Python owns them regardless of what the plan says.

**Important seam today:** Tirzah's executor still runs the full ask pipeline as
one unit; the plan is **descriptive + revisable state** ahead of/after execution,
not yet a step-by-step interpreter that walks `depends_on` and flips step
`status` live. That gap is the next evolution toward true plan-driven execution.

---

## Stress-test notes

What worked: SPEC §4.5 `PLAN` maps cleanly to persisted `recursive_plans`;
`RECURSE` for revision loop; `cairn.validate_plan` as cross-repo contract;
explicit planner/executor split; fallback on malformed planner output.

Rough edges:

1. **Plan vs execution coupling** — plan describes work; executor runs a fixed
   pipeline. Full interpretive execution (walk steps, enforce `allowed_tools` per
   step) is not modelled here yet.
2. **Construct subset** — planner allows `STEP|CALL|ITERATE|DECISION|RECURSE`;
   Cairn conformance allows more (`MILESTONE`, `AWAIT`, …) than the planner emits.
3. **Specialist hook** — `run_planned_specialist` may fire Milcah after planning;
   cross-PROCESS `CALL` not drawn inside the PLAN backbone.