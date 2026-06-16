# APML — Agentic Process Meta-Language

**Specification v0.6 (draft)**

APML is a simple, textual, human-readable meta-language for describing complex
processes — especially agentic / LLM-centric ones — so that humans and LLMs can
read, write, compare, and reason about the same description.

This document is the specification. For the why, see
[README.md](README.md) (Purpose & Philosophy).

---

## 0. Reading guide

The **golden rule** comes first, because everything else serves it:

> When someone reads an APML description, they should think *"I get what's
> happening here,"* not *"I need to learn the notation first."*

So APML is **human-first**. Formality is **optional and progressive**: you add
precision only where it matters, and the readable flow stays clean. Where machine
precision is needed (for validation or AI execution), it lives in a **Formal**
layer that an AI keeps in sync with the **Narrative** human reading — both are
two views of one shared structure (§4).

---

## 1. Document structure — three modes

An APML document is built from three kinds of block. A document may use any
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
4. **One structure, two styles.** Formal (machine-precise) and Narrative
   (human-readable) are two renderings of the *same* backbone; an AI translates
   and keeps them aligned (§4).
5. **Consistency through core verbs** (§5.3) — a recommended lexicon, never a
   rule. Clarity always wins over adherence.
6. **Practical and evolving.** APML is used "in anger" on real projects; the
   reserved vocabulary (verbs, tags) grows from real use, not theory.

---

## 3. The shared backbone and the two styles

Every APML description has one **canonical backbone**:

- the **numbering** (`1.`, `2.1`, …) and indentation (sequence + hierarchy),
- the **construct** each step is (STEP, ITERATE, DECISION, …),
- the **tags** (§8) and **state references** (§7) on a step,
- any **formal modifiers** on a construct (e.g. `ITERATE [MAX: 5]`).

Two styles render that backbone:

- **Formal** — terse, verb-led, carries the precise modifiers. This is the
  **canonical** form for anything machine-checkable or AI-executable.
- **Narrative** — the same steps written as plain prose for a human reader.

They share the numbering **1:1**, so a reader can move between them and an AI can
translate either way and keep them consistent. When the two disagree, **Formal
wins** for machine semantics; Narrative wins for human intent (and the
disagreement is a bug to fix).

> Authoring guidance: write whichever style is natural, and let tooling/AI
> generate and sync the other. You do **not** maintain both by hand.

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

Start a step with one of these where it fits — it gives APML its scannable
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
`BOUNDARIES`, `CONTEXT`, or nested numbered steps.

---

## 5. Constructs

Each construct below lists its **meaning**, optional **formal modifiers** (with
defaults), and how it reads in **Narrative**. Modifiers are the "progressive
formality" lever — omit them and the default applies.

### STEP
A single action. The default construct; the verb carries the meaning.

### ITERATE
Repeat a block.
- Formal: `ITERATE [UNTIL: <condition>; MAX: <n>]`
  - `UNTIL` — termination condition (default: until the body signals done).
  - `MAX` — hard cap on rounds (default: required for any LLM-driven loop).
- Narrative: *"Iterate, refining …, until <condition> or after at most <n>
  rounds."*

### RECURSE
A process (or step) that calls itself.
- Formal: `RECURSE [BASE: <condition>; MAX_DEPTH: <n>]`
  - `BASE` — base case (required). `MAX_DEPTH` — depth guard.

### QUEUE
Serialized / turn-based flow (e.g. agents taking turns).
- Formal: `QUEUE [ORDER: FIFO|PRIORITY|ROUND_ROBIN; ONE_AT_A_TIME]`
  - `ORDER` default `FIFO`. `ONE_AT_A_TIME` is the default for agent turns.

### PARALLEL … MERGE
Concurrent sub-branches, lettered, then a join.
- Formal: `PARALLEL [STATE: isolated|shared] … MERGE [<rule>]`
  - `STATE` default `isolated` (branches do **not** see each other's
    `STATE UPDATE`s until MERGE). `MERGE` states how outputs combine.
- Branches use letters: `3a.`, `3b.`, then a `MERGE` step.

### DECISION
A branch point.
- Formal: `DECISION [ON: <value>] → <branch-A> | <branch-B> | …`
- Narrative: *"If <…>, then …; otherwise …."*

### RETRY
Re-attempt on transient failure.
- Formal: `RETRY [MAX: <n>; BACKOFF: none|linear|exponential]` (defaults `MAX: 3`,
  `BACKOFF: exponential`).

### ERROR
Handle / propagate a failure.
- Formal: `ERROR [ON: <type>; THEN: handle|fallback|propagate]`
  (default `propagate` to the parent PROCESS).

### CALL
Invoke another PROCESS (composition, §11).
- Formal: `CALL <ProcessName>(<args>) → <result>`

### STATE UPDATE / OUTPUT / RISKS
Annotations on a step: a write to declared state (§7), what the step yields, and
known hazards. `OUTPUT` at PROCESS level is its return.

---

## 6. STATE

State is the substance of agentic processes (notes, exclusion lists,
accumulators, session memory). APML declares it at a **simple, directional level
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

---

## 7. Tags

Tags add precision without prose. The reserved set is organised as **orthogonal
dimensions** — at most one value per dimension on a step — plus **namespaced
extensions** for anything custom.

| Dimension | Reserved values |
|---|---|
| **Actor** | `LLM` · `HUMAN` · `CODE` · `EXTERNAL` |
| **Determinism** | `DETERMINISTIC` · `STOCHASTIC` |
| **Timing** | `SYNC` · `ASYNC` |
| **Effects** | `PURE` · `SIDE-EFFECT` · `IDEMPOTENT` |
| **Control** (optional) | `BLOCKING` · `GATED` (human review) · `CACHED` |

Example: `[LLM, STOCHASTIC, SYNC, SIDE-EFFECT]`.

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

APML expresses requirements **directly**, as testable assertions — distinct from
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
- Process steps may reference requirements for traceability:
  `4. … [SATISFIES: R2]`.
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

APML descriptions are free-text inside a light structural skeleton. A description
is **well-formed** if:

1. it contains at least one of CONTEXT, REQUIREMENTS/OUTCOMES, or PROCESS;
2. every PROCESS has a name (and a signature when it takes input / returns
   output);
3. steps are consistently numbered and nested;
4. reserved tags use at most one value per dimension (§7); custom tags are
   namespaced;
5. every `STATE UPDATE` names a piece declared in a `STATE` block;
6. LLM-driven `ITERATE` / `RECURSE` carry a bound (`MAX` / `MAX_DEPTH`).

Descriptions (the prose in each step) are intentionally **not** constrained —
that is where human readability lives. Tooling validates the skeleton, not the
words.

A minimal structural grammar (EBNF) for the skeleton will accompany this spec
once the constructs settle.

---

## 13. Versioning & evolution

- This is **v0.6**, a draft that supersedes v0.5 (adds: shared-backbone dual
  style, scoped+referenced STATE, progressive-formality construct modifiers,
  tag dimensions + extensions, requirements/outcomes mode, composition,
  conformance).
- APML evolves from real use. The reserved verbs and tags grow as the language is
  applied to actual projects; changes are recorded in
  [CHANGELOG.md](CHANGELOG.md).
- The first stress test is describing three real systems (Tirzah, Hoglah,
  Mahalath) in APML — see `examples/`.
