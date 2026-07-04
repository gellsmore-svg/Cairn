# Cairn — a process meta-language

**Specification v0.9**

Cairn is a simple, textual, human-readable meta-language for describing complex
processes — especially agentic / LLM-centric ones — so that humans and LLMs can
read, write, compare, and reason about the same description.

This document is the specification. For the why, see
[README.md](README.md) (Purpose & Philosophy).

---

## 0. Reading guide

The **golden rule** comes first, because everything else serves it:

> When someone reads a Cairn description, they should think *"I get what's
> happening here,"* not *"I need to learn the notation first."*

So Cairn is **human-first**. Formality is **optional and progressive**: you add
precision only where it matters, and the readable flow stays clean. Where machine
precision is needed (for validation or AI execution), it lives in a **Formal**
layer that an AI keeps in sync with the **Narrative** human reading — both are
two views of one shared structure (§4).

---

## 1. Document structure — three modes

An Cairn document is built from three kinds of block. A document may use any
subset, in any combination.

| Mode | Answers | Shape |
|---|---|---|
| **CONTEXT** | "what world are we in?" | scene-setting, definitions, frames |
| **REQUIREMENTS / OUTCOMES** | "what must be true?" | declarative, testable assertions |
| **PROCESS** | "how does it flow?" | the numbered, imperative steps |

Keeping these three distinct is deliberate: requirements are *assertions* (with
acceptance criteria), not control flow, and scene-setting is *background*, not
steps. Mixing them is what makes most design docs hard to follow.

---

## 2. Design principles

1. **Human-first readability.** Concrete everyday words, short active sentences.
   Structure scaffolds; it never gets in the way.
2. **Least abstraction that works.** Don't invent a symbol where a plain word
   will do.
3. **Progressive formality.** The default is terse and readable. Precision
   (modifiers, state scopes, acceptance criteria) is added only where it earns
   its keep. Sensible defaults apply when a modifier is omitted.
4. **One structure, many profiles.** A single canonical backbone is *projected*
   into audience render profiles (precise `ai`, readable `operator`, and more);
   you author once and a tool/AI renders the rest (§3).
5. **Consistency through core verbs** (§5.3) — a recommended lexicon, never a
   rule. Clarity always wins over adherence.
6. **Practical and evolving.** Cairn is used "in anger" on real projects; the
   reserved vocabulary (verbs, tags) grows from real use, not theory.

---

## 3. The shared backbone and its render profiles

Every Cairn description has one **canonical backbone**:

- the **numbering** (`1.`, `2.1`, …) and indentation (sequence + hierarchy),
- the **construct** each step is (STEP, ITERATE, DECISION, …),
- the **tags** (§7) and **state references** (§6) on a step,
- any **formal modifiers** on a construct (e.g. `ITERATE [MAX: 5]`).

The backbone is the single source of truth. It is **projected** into one of
several **render profiles** for a given audience. You author the backbone once; a
tool or AI renders the profile. You do **not** hand-maintain multiple versions.

### 3.1 Render profiles

A profile projects the backbone with rules for what to **expose**, what to
**compress**, and how to phrase it. The standard profiles:

| Profile | For | Exposes | Compresses | Reads like |
|---|---|---|---|---|
| `ai` | machines / execution | everything: every step, modifier, tag, state | nothing | a precise, complete skeleton |
| `operator` | the person running it | intent, ownership, decisions, iteration, milestones, outputs | internal calls, mechanical sub-steps | a guided operational narrative |
| `executive` | sponsors / overview | milestones, owners, outcomes, key decisions | almost all mechanism | a one-glance status story |
| `audit` | review / compliance | everything significant + decisions, constraints, provenance, who-did-what | low-value mechanics only | a defensible record |

`ai` and `operator` are the **canonical pair** (the precise form and the readable
form); `executive` and `audit` are further projections of the *same* backbone.

Select a profile with a directive: `render-profile: operator`. Profiles other than
`ai` are lossy **by design**; when they seem to disagree, the `ai` projection wins
for machine semantics — the others are never authoritative.

For these projections to work, the backbone carries the needed signal: **PURPOSE**
(intent, §5), **MILESTONE** (major transitions, §5), **Actor / ASSISTED-BY**
(ownership vs. contribution, §7), and the always-significant constructs (DECISION,
CONSTRAINTS, OUTPUT, AWAIT, GATED) that every profile but the most compressed
exposes.

### 3.2 The operator (human) profile

The headline human view. It answers, for each phase: *what is happening, why, who
owns it, what changed, what's next* — without implementation detail. For each
MILESTONE / PROCESS it renders **Purpose** (the `PURPOSE:` intent), **Owner** (the
Actor, a role if named), **Assisted by** (the `ASSISTED-BY` actors), **Outputs**
(key `OUTPUT`s / OUTCOMES), **Iterate until** (the `ITERATE [UNTIL: …]` condition,
when present), and **Next** (the following MILESTONE). It compresses internal
`CALL`s and mechanical `[CODE]` sub-steps, and always exposes decisions,
constraints, and outputs.

```
FRAME Opportunity
  Purpose:       Convert a customer need into executable context.
  Owner:         Product Lead
  Assisted by:   LLM
  Outputs:       specification, constraints, acceptance criteria
  Iterate until: confidence threshold satisfied
  Next:          BUILD Solution
```

**Success criterion:** a human grasps purpose, ownership, progress, and iteration
without reading mechanism. **Guardrail:** if removing a keyword or structure makes
understanding *harder*, the profile is over-compressed — restore it.

---

## 4. Core grammar

### 4.1 PROCESS

The top-level container. It has a **signature** (§11):

```
PROCESS <Name> (INPUT: <…>; OUTPUT: <…>)
```

### 4.2 Numbered hierarchy

Steps are numbered for sequence; indentation + dotted numbers show nesting:

```
1. …
2. …
   2.1 …
   2.2 …
3. …
```

### 4.3 Core verbs (recommended lexicon)

Start a step with one of these where it fits — it gives Cairn its scannable
"process feel." **Recommended, not required.**

`Initialize/Setup` · `Propose/Generate` · `Evaluate/Score` · `Decide/Choose` ·
`Update/Refine` · `Execute/Call` · `Iterate/Recurse` · `Queue/Negotiate` ·
`Merge/Output` · `Handle/Retry`

### 4.4 Steps and step-blocks

A step is a line; it may carry indented sub-blocks:

```
3. Evaluate each candidate for relevance. [LLM, STOCHASTIC]
   CONSTRAINTS: judge only against the original request.
   STATE UPDATE: useful_chunks += kept_ids
   OUTPUT: kept_ids, dropped_ids
   RISKS: a weak model may over-keep; the Python pre-rank bounds the set.
```

Sub-block keywords: `STATE UPDATE`, `OUTPUT`, `RISKS`, `CONSTRAINTS` /
`BOUNDARIES`, `CONTEXT`, `PURPOSE`, or nested numbered steps.


### 4.5 PLAN — a live, revisable process instance

`PROCESS` defines a reusable flow. `PLAN` identifies one live application of a
process to a request and records how that application changes as new information
arrives.

```text
PLAN <plan-id> REVISION <n> [STATUS: draft|active|stable|complete|blocked]
  PARENT: <revision number or none>
  REQUEST: <the request this plan serves>
  TRIGGER: <new information that caused this revision, or initial_request>

  PROCESS <Name> (INPUT: ...; OUTPUT: ...)
    ... normal Cairn process backbone ...
```

A plan revision:

- preserves the same `plan-id` and increments `REVISION`;
- names its parent revision, except revision 1;
- records the information that justified the change;
- contains a complete process backbone, not an ambiguous patch;
- must retain hard constraints and stopping bounds unless an authorised human or
  governing process explicitly changes them;
- may finish as `stable` when no change is warranted, `complete` when its outcome
  has been reached, or `blocked` when progress requires unavailable authority or
  information.

LLM-produced plans and revisions require bounded iteration. The runtime validates
the plan structure and remains responsible for tool permissions, side effects,
budgets, persistence, and termination. A `PLAN` is operational state, not trusted
knowledge; promoting its claims into memory is a separate governed action.

### 4.6 PLAN interpretation — live step execution

A `PLAN` may be **interpreted** — walked step-by-step by a runtime that enforces
`depends_on`, `allowed_tools`, and per-step status transitions — rather than
executed only as narrative around a monolithic pipeline.

**Step state machine** (machine plans; prose plans may omit explicit status):

| Status | Meaning |
|--------|---------|
| `pending` | Not started; dependencies may be unsatisfied |
| `active` | Currently executing |
| `completed` | Succeeded; outputs available to dependents |
| `blocked` | Cannot proceed (missing handler, failed guard, unavailable tool) |
| `skipped` | Intentionally not run (deferred construct, duplicate effect, policy) |

**Interpretation order:** a step runs only when every `depends_on` id is
`completed`. Steps with no unresolved dependencies are **ready**; the runtime picks
from the ready set (typically ascending `id` / document order).

**Dispatch by construct:**

- `STEP` — acknowledge or execute. A pure framing step with no `allowed_tools`
  may complete as an acknowledged intent. A step tagged `[LLM, STOCHASTIC]` needs
  a stochastic handler or must delegate to a governed `CALL`.
- `CALL` — invoke a registered handler. The handler set **must** be a subset of
  `allowed_tools` on that step. Unknown tools → `blocked`, not silent fallback.
- `ITERATE` / `DECISION` / `RECURSE` — either expand into an inner interpreter
  loop with explicit bounds, or `skip` with trace when an outer revision loop
  already owns recursion (common for `RECURSE` on revision 1).

**Execution context** crosses steps through a bounded artifact map (step id →
output) and the `PROCESS` signature — not through callee-private `STATE` (§6.5).

**Trace:** each transition emits a process event (`plan.step.started`,
`plan.step.completed`, …) separate from the answer payload. Interpretation trace +
plan revision lineage together form the auditable record.

**Degenerate case:** a single `CALL` step whose handler runs the full legacy
pipeline is valid — interpretation collapses to today's monolithic executor. The
value of interpretation is **granular tool gating**, **resumability**, and
**honest step status** when plans grow beyond one blob.

**Planner vs interpreter:** the planner LLM proposes steps; the interpreter never
widens `allowed_tools` or skips `depends_on`. Revisions replace the backbone;
the interpreter may resume from the first `pending`/`blocked` step on the new
revision.

---

## 5. Constructs

Each construct below lists its **meaning**, optional **formal modifiers** (with
defaults), and how it reads in **Narrative**. Modifiers are the "progressive
formality" lever — omit them and the default applies.

### MILESTONE
A major transition / phase in a process (e.g. `FRAME`, `BUILD`, `VERIFY`,
`RELEASE`). Marks the points the `operator` / `executive` profiles surface.
- Formal: `MILESTONE <Name>` heading a step or group.
- Top-level steps may be treated as milestones implicitly; `MILESTONE` makes a
  significant transition explicit.

### PURPOSE
A one-line statement of **intent** on a PROCESS, MILESTONE, or step — *why* it
exists, not *how* it works. The `operator` profile renders it as "Purpose:".
- Formal: `PURPOSE: <intent>` (a sub-block, like OUTPUT/RISKS).

### STEP
A single action. The default construct; the verb carries the meaning.

A step may perform **many similar calls at once** (a fan-out / batch) and still be
*one* step — e.g. "run the requested tool calls." Tag it `[BATCH]` (optionally
`[BATCH: n]`) when the multiplicity matters. Use **PARALLEL** only for genuinely
*concurrent branches with independent control flow*, not for a loop or batch of
like calls.

### ITERATE
Repeat a block.
- Formal: `ITERATE [UNTIL: <condition>; MAX: <n>]`
  - `UNTIL` — termination condition (default: until the body signals done). The
    condition may reference state the body sets (e.g. `UNTIL: decision.status =
    done`).
  - `MAX` — hard cap on rounds (default: required for any LLM-driven loop).
- Loop control: a step inside the body may `BREAK` (exit the loop) or `CONTINUE`
  (skip to the next round) — see below. This is the explicit way to leave a loop
  early, rather than relying on a DECISION to "fall out."
- Narrative: *"Iterate, refining …, until <condition> or after at most <n>
  rounds."*

### BREAK / CONTINUE
Loop control inside ITERATE / QUEUE.
- `BREAK [IF: <condition>]` — leave the enclosing loop now (optionally only when
  the condition holds).
- `CONTINUE [IF: <condition>]` — skip the rest of this round and start the next.
- Prefer these over a DECISION whose only job is to exit a loop.

### RECURSE
A process that calls itself. **Recursion *is* a self-`CALL`** — `RECURSE` is the
same act as `CALL <ThisProcess>(…)` with the two guards below; don't write both
for the same recursion.
- Formal: `RECURSE [BASE: <condition>; MAX_DEPTH: <n>]`
  - `BASE` — base case (required). `MAX_DEPTH` — depth guard.

### QUEUE
Serialized / turn-based flow (e.g. agents taking turns).
- Formal: `QUEUE [ORDER: FIFO|PRIORITY|ROUND_ROBIN; ONE_AT_A_TIME]`
  - `ORDER` default `FIFO`. `ONE_AT_A_TIME` is the default for agent turns.

### PARALLEL … MERGE
Concurrent sub-branches that **join** at a MERGE.
- Formal: `PARALLEL [STATE: isolated|shared] … MERGE [<rule>]`
  - `STATE` default `isolated` (branches do **not** see each other's
    `STATE UPDATE`s until MERGE). `MERGE` states how outputs combine.
- Branches use letters: `3a.`, `3b.`, then a `MERGE` step.
- For concurrency that **never joins** (long-running services), use SERVICE.

### SERVICE
A long-running, concurrent activity that does **not** join — e.g. a worker loop,
a watched-folder ingester, a broker consumer. Several SERVICEs typically run at
once over **shared** state and continue until stopped.
- Formal: `SERVICE <Name> [UNTIL: stop]` — usually an `ITERATE [UNTIL: stop]` body.
- Run a set concurrently with `CONCURRENT { SERVICE a; SERVICE b; … }`
  (the non-joining counterpart of PARALLEL); name the shared state they operate on.

### DECISION
A branch point.
- Inline (one-liners): `DECISION [ON: <value>] → <branch-A> | <branch-B> | …`
- With **branch bodies** (multi-step): name branches with letters and nest their
  steps, like PARALLEL — `2a.` … / `2b.` … under the DECISION.
- Narrative: *"If <…>, then …; otherwise …."*

### RETRY
Re-attempt on transient failure.
- Formal: `RETRY [MAX: <n>; BACKOFF: none|linear|exponential]` (defaults `MAX: 3`,
  `BACKOFF: exponential`).

### ERROR
Handle / propagate a failure.
- Formal: `ERROR [ON: <type>; THEN: handle|fallback|propagate]`
  (default `propagate` to the parent PROCESS).
- When `THEN` is `fallback` (or `handle`), **name the target**:
  `ERROR [ON: malformed; THEN: fallback → stop with current context]`. The arrow
  gives the concrete recovery, not just the mode.

### AWAIT
Suspend until an external event — a human approval, a system signal, a timeout.
Real processes *wait*: a `[GATED, HUMAN]` write waits for an operator; a crash-safe
egress waits for a broker ack. The process resumes (or times out) when the event
arrives.
- Formal: `AWAIT [EVENT: <what>; TIMEOUT: <duration|never>; THEN: <on-timeout>]`
- Example: `AWAIT [EVENT: operator approves the proposed meaning; TIMEOUT: never]`.
- State held across an AWAIT is whatever its scope keeps (§6); the wait may
  outlive a restart, so durable scope is what survives.

### ATOMIC / DURABLE-BEFORE  (ordering & recovery)
Crash-safe systems hinge on *ordering between steps* and *what happens if a crash
lands between them*. Make that explicit instead of burying it in prose:
- `DURABLE-BEFORE: <step>` on a step — this step's effect must be durable **before**
  `<step>` runs (e.g. "enqueue is durable before the broker offset is committed").
- `ATOMIC { … }` — a group whose effect is all-or-nothing.
- `RECOVERY: <action>` — a step/process annotation stating what happens if a crash
  interrupts here on restart (e.g. `RECOVERY: redelivery re-runs the enqueue, which
  is a no-op`). This is the crash-window analogue of `ERROR`’s fallback.

### CALL
Invoke another PROCESS (composition, §11).
- Formal: `CALL <ProcessName>(<args>) → <result>`

### STATE UPDATE / OUTPUT / RISKS
Annotations on a step: a write to declared state (§7), what the step yields, and
known hazards. `OUTPUT` at PROCESS level is its return.

---

## 6. STATE

State is the substance of agentic processes (notes, exclusion lists,
accumulators, session memory). Cairn declares it at a **simple, directional level
inline**, and links to a **definitive definition by number** in a reference
document (the reference-doc format is part of the spec and TBD in detail).

### 6.1 Inline declaration

A `STATE` block names each piece with a **scope**, a **direction**, and a
reference number:

```
STATE
  useful_chunks   [scope: session;  dir: write]      ref: S1
  exclusion_ids   [scope: session;  dir: read/write] ref: S2
  rolling_summary [scope: session;  dir: read/write] ref: S3
```

- **scope** — one of `global | process | session | iteration`.
- **dir** — data-flow direction at this level: `read | write | read/write`
  (think "in / out / in-out").
- **ref** — a number (`S1`, …) pointing to the definitive definition (type,
  invariants, semantics) held in a linked **STATE REFERENCE** document.

### 6.2 Use in steps

Steps reference declared state by name:

```
3. Keep the relevant chunks.
   STATE UPDATE: useful_chunks += kept_ids
```

### 6.3 Why directional + referenced

Inline you see *enough* to read the flow (what state exists, its scope, whether a
step reads or writes it) without clutter; the *definitive* meaning lives once, by
number, in the reference doc. This keeps the main flow human-readable while giving
an AI a precise, executable contract. Scope makes PARALLEL/RECURSE access
explicit (a `session`-scoped value is shared across a session; an `iteration`-
scoped value resets each loop).

### 6.4 Scope semantics

- `global` — lives for the whole description.
- `process` — lives for one run of the PROCESS that declares it.
- `session` — shared across the turns of a session.
- `iteration` — **reset at the start of each ITERATE/QUEUE round.** A value the
  body recomputes each pass is `iteration`-scoped; a value that accumulates
  across passes (e.g. `history`) is `process`-scoped.

### 6.5 STATE and the CALL boundary

A sub-process's STATE is **private by default**. Data crosses a `CALL` only
through its **INPUT / OUTPUT** signature — a caller cannot see or write a callee's
internal state, and vice versa. To share mutable state across a `CALL`, declare it
at a shared scope (`process`/`global`) visible to both, and say so explicitly.
This keeps composition (§10) safe to reason about: a PROCESS is understood from
its signature, not its callees' internals.

---

## 7. Tags

Tags add precision without prose. The reserved set is organised as **orthogonal
dimensions** — at most one value per dimension on a step — plus **namespaced
extensions** for anything custom.

| Dimension | Reserved values |
|---|---|
| **Actor** (owner) | `LLM` · `HUMAN` · `CODE` · `EXTERNAL` |
| **Determinism** | `DETERMINISTIC` · `STOCHASTIC` |
| **Timing** | `SYNC` · `ASYNC` |
| **Effects** | `PURE` · `SIDE-EFFECT` · `IDEMPOTENT` |
| **Control** (optional) | `BLOCKING` · `GATED` (human review) · `CACHED` |

Example: `[LLM, STOCHASTIC, SYNC, SIDE-EFFECT]`.

**Ownership vs. contribution.** The **Actor** dimension names the *accountable
owner* — who decides, approves, and owns the outcome — **not** necessarily who does
the work. To name who *materially contributes* (executes, generates, analyses) use
`ASSISTED-BY`:

- `[HUMAN, ASSISTED-BY: LLM]` — a human owns the decision; an LLM did the framing /
  generation / analysis.
- `ASSISTED-BY` takes one or more actors: `[LLM, ASSISTED-BY: CODE]`,
  `[HUMAN, ASSISTED-BY: LLM, EXTERNAL]`.
- The owner may carry a **role**: `[HUMAN: Product Lead, ASSISTED-BY: LLM]`.

This keeps hybrid human-led / AI-assisted work visible at the top level instead of
hiding it as pure `[HUMAN]` (loses the AI's contribution) or pure `[LLM]` (loses
ownership). The `operator`/`audit` profiles render owner and assistance distinctly
(§3).

A tag may carry a parameter where it sharpens meaning — most usefully the
idempotency key: `IDEMPOTENT [KEY: correlation_id]` (the *what* that makes a repeat
a no-op), and `BATCH [n]` for fan-out size (§5 STEP).

**Extensions:** custom tags are namespaced and visibly non-standard, e.g.
`[x:rerank]`, `[team:billing]`. The reserved vocabulary is expected to **grow
from real use** (describing actual projects), not be fixed up front.

---

## 8. CONTEXT and CONSTRAINTS

- **CONTEXT** — a top-level or per-PROCESS list of definitions / frames /
  background. Provides the bigger picture without cluttering the flow. Referenced
  from steps when helpful.
- **CONSTRAINTS / BOUNDARIES** — limits on a PROCESS or STEP. Inline when short;
  referenced ("See Coherence Rules") when shared or long.

---

## 9. Requirements & Outcomes mode

Cairn expresses requirements **directly**, as testable assertions — distinct from
process steps — so a single document can set the scene, state what must be true,
and describe the flow.

```
REQUIREMENTS
  R1. Retrieval SHALL run entirely on local infrastructure.   [MUST]
      ACCEPTANCE: no network call occurs in the default path.
  R2. The agent SHALL exclude already-returned chunks within a session. [MUST]
  R3. The system SHOULD surface key sources with the answer.  [SHOULD]

OUTCOMES
  A synthesised answer, plus optional transparency (key sources, path,
  confidence).
```

- Each requirement: an id (`R1`), a `SHALL/SHOULD/MAY` assertion, a priority tag
  (`[MUST] | [SHOULD] | [MAY]`), and an optional `ACCEPTANCE` criterion.
- `[MUST]`/`[SHOULD]` are obligations; **`[MAY]` is a capability** — on a step,
  `[SATISFIES: R#]` then means *"supports"*, not *"guarantees"*.
- Process steps reference requirements for traceability: `4. … [SATISFIES: R2]`.
- **A guarantee may be emergent** — satisfied by several steps together, possibly
  across processes or even across separate UI/backend slices. Use either form:
  - **Inline (on a step or OUTCOMES block):**
    `[SATISFIES: R3 — via Ingest.3–4 + Egress.2–3 + consumer dedup on correlation_id]`
  - **Block (at OUTCOMES or parent PROCESS level):**
    ```
    EMERGENT [SATISFIES: R3]
      via Ingest.3–4, Egress.2–3, consumer correlation_id dedup
    ```
  The two forms are equivalent; the block form is easier to read for guarantees
  that no single step owns. Per-step `[SATISFIES]` remains the common case.
- **OUTCOMES** are the expected end-states (what "done" looks like), separate
  from the moment-to-moment OUTPUT of steps.

---

## 10. Composition (signatures + CALL)

Processes are reusable. A PROCESS declares a signature and can be invoked from a
step:

```
PROCESS Ask (INPUT: user_query; OUTPUT: answer)
  1. CALL Retrieve(user_query) → useful_chunks
  2. Generate the answer from useful_chunks. [LLM]
  OUTPUT: answer

PROCESS Retrieve (INPUT: query; OUTPUT: useful_chunks)
  …
```

`CALL` makes nesting explicit and keeps large systems decomposed into named,
referenceable processes.

---

## 11. Worked example

The same small agentic-retrieval loop, in both styles. They share the backbone
(numbering, constructs, tags, state).

### 11.1 Formal

```
CONTEXT
  A local LLM retrieves over a graph store under a small context window.

PROCESS Retrieve (INPUT: query; OUTPUT: useful_chunks)
  STATE
    useful_chunks  [scope: session; dir: write]      ref: S1
    exclusion_ids  [scope: session; dir: read/write] ref: S2
    novelty        [scope: iteration; dir: write]     ref: S3

  1. Initialize empty useful_chunks and exclusion_ids.            [CODE, DETERMINISTIC]
  2. ITERATE [UNTIL: novelty < 0.1; MAX: 5]
     2.1 Propose a query plan.                                    [LLM, STOCHASTIC, SYNC]
         CONSTRAINTS: choose one of the fixed query primitives.
     2.2 Execute the plan and gate candidates.                    [CODE, DETERMINISTIC]
         STATE UPDATE: exclusion_ids += returned_ids
     2.3 Evaluate the shortlist for relevance.                    [LLM, STOCHASTIC]
         STATE UPDATE: useful_chunks += kept_ids
     2.4 Update novelty from new-vs-excluded ratio.               [CODE, DETERMINISTIC]
  3. CALL Synthesize(useful_chunks) → answer.                     [LLM] [SATISFIES: R1]
  OUTPUT: answer
  RISKS: a weak local model may mis-judge relevance; the Python gate (2.2) bounds it.
```

### 11.2 Narrative (same backbone)

```
PROCESS — Retrieve an answer for a user query.

  1. Start with an empty "useful" set and an empty "already-seen" set.
  2. Loop — at most five rounds, stopping early when little new turns up:
     2.1 The model proposes a query plan, choosing one of the allowed search
         primitives.
     2.2 Run the plan; record everything returned so it isn't fetched again.
     2.3 The model judges the shortlist and keeps what's genuinely relevant.
     2.4 Measure how much of this round was new; that drives the stop decision.
  3. Hand the kept chunks to the Synthesize process to write the answer.

  Risk: a small model can mis-judge relevance, so a deterministic filter in 2.2
  bounds what it ever sees.
```

---

## 12. Conformance (structural)

Cairn descriptions are free-text inside a light structural skeleton. A description
is **well-formed** if:

1. it contains at least one of CONTEXT, REQUIREMENTS/OUTCOMES, or PROCESS;
2. every PROCESS has a name (and a signature when it takes input / returns
   output);
3. steps are consistently numbered and nested;
4. reserved tags use at most one value per dimension (§7); custom tags are
   namespaced;
5. every `STATE UPDATE` names a piece declared in a `STATE` block;
6. LLM-driven `ITERATE` / `RECURSE` carry a bound (`MAX` / `MAX_DEPTH`);
7. `BREAK` / `CONTINUE` appear only inside a loop (`ITERATE` / `QUEUE`);
8. every `AWAIT` states a `TIMEOUT` (a value or `never`).

Descriptions (the prose in each step) are intentionally **not** constrained —
that is where human readability lives. Tooling validates the skeleton, not the
words.

A minimal structural grammar (EBNF) for the skeleton is in
[GRAMMAR.md](GRAMMAR.md). It defines the structure; step descriptions stay free
text.

---

## 13. Versioning & evolution

- **v0.9** adds versioned live `PLAN` envelopes for bounded recursive revision of a complete `PROCESS` backbone.
- **v0.8** adds **render profiles** (the `ai`/`operator`/`executive`/`audit`
  projections of one backbone, §3), **ownership vs. contribution**
  (`Actor` = owner + `ASSISTED-BY`, §7), and `MILESTONE` / `PURPOSE` to feed the
  human-facing profiles — from feedback after modelling an end-to-end
  human-led, AI-assisted delivery process.
- v0.7 was the first stress-tested release. It supersedes the v0.6 draft
  (shared-backbone dual style, scoped+referenced STATE, progressive-formality
  modifiers, tag dimensions + extensions, requirements/outcomes mode, composition,
  conformance) and folds in everything learned from describing three real systems:
  `SERVICE`/`CONCURRENT`, `AWAIT`, `ATOMIC`/`DURABLE-BEFORE`/`RECOVERY`,
  `BREAK`/`CONTINUE`, parameterised tags, and emergent `[SATISFIES]`.
- Cairn evolves from real use. The reserved verbs and tags grow as the language is
  applied to actual projects; changes are recorded in
  [CHANGELOG.md](CHANGELOG.md).
- The first stress test is describing three real systems (Tirzah, Hoglah,
  Mahalath) in Cairn — see `examples/`.
