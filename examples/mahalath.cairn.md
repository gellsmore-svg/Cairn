# Mahalath in Cairn — ingest → debate → ontology (representative slice)

A Cairn description of **Mahalath as it currently stands**, for the slice that
exercises what Tirzah and Hoglah didn't: a **serialized multi-agent debate** that
defines a term, with **term invention (recursion)**, **confidence-gated**
acceptance, **human-review-gated** writes, and optional **frontier escalation**.

Mahalath is a self-sustaining, local-first ontology builder: drop Markdown into
`input/`, and it grows a provenance-rich *lexicon of meanings* — each an opaque,
immutable label (`MPL-004`), one or more debated definitions, a place in a
hierarchy, and an audit trail.

---

## CONTEXT

- **lexicon** — the append-only store of meanings. Each meaning: an opaque
  `MPL` label, definition(s), a frame, a place in the tree, provenance.
- **frame** — the sense a term is used in (a `field` means one thing to a
  physicist, another to a farmer). A human term may hold several meanings, one
  per frame (polysemy).
- **debate** — local LLM agents take turns proposing and critiquing a definition
  for a candidate term until a confidence threshold is met or they stall.
- **operator** — the human who reviews and approves proposed meanings.
- **frontier review** — an optional stronger model (Claude API) consulted for
  low-confidence items; off by default (local-first).

## REQUIREMENTS

```
R1. Source SHALL be preserved verbatim; ingestion never rewrites/summarises it.  [MUST]
    ACCEPTANCE: stored source bytes equal the ingested file (minus dup rejection).
R2. Ontology writes SHALL be review-gated; no autonomous agent write authority.  [MUST]
    ACCEPTANCE: a proposed meaning is committed only after operator approval.
R3. The lexicon SHALL be append-only; MPL labels are immutable.                  [MUST]
R4. A human term MAY hold multiple meanings, each keyed by frame (polysemy).     [SHOULD]
R5. A definition SHALL be accepted only at/above the confidence threshold;
    below it routes to review/escalation.                                        [MUST]
R6. Debate SHALL be bounded (≤ max_debate_iterations per term).                  [MUST]
```

## OUTCOMES

A growing, provenance-rich lexicon of precisely-defined meanings; low-confidence
candidates queued for human (or frontier) review; the source corpus untouched.

---

## PROCESS — Formal

```
PROCESS BuildOntology (INPUT: input_folder; OUTPUT: lexicon)
  CONTEXT: a long-running service watching `input/`.
  STATE
    lexicon   [scope: global; dir: read/write]  ref: M1

  1. ITERATE [UNTIL: stop]                                     # watched folder
     1.1 Ingest the next document; preserve source verbatim; reject duplicates
         by SHA-256 checksum.                                  [CODE, IDEMPOTENT, SIDE-EFFECT] [SATISFIES: R1]
     1.2 Extract candidate (term, frame) pairs from the document. [LLM, STOCHASTIC]
     1.3 Define each candidate.                                [BATCH]
         → CALL DefineTerm(term, frame, source_context)
  OUTPUT: lexicon  (grows; never shrinks)

PROCESS DefineTerm (INPUT: term, frame, source_context; OUTPUT: proposal | escalation)
  CONSTRAINTS: one meaning per (term, frame); cite source; never rewrite source. [SATISFIES: R1, R4]
  STATE
    candidates  [scope: process;    dir: read/write]  ref: M2   # proposed defs + scores
    best        [scope: iteration;  dir: write]        ref: M3   # current best {definition, confidence}

  1. ITERATE [UNTIL: best.confidence >= accept_threshold; MAX: max_debate_iterations]  [SATISFIES: R5, R6]
     1.1 QUEUE [ORDER: ROUND_ROBIN; ONE_AT_A_TIME]            # serialized agent discussion
         1.1.1 The next agent proposes or critiques a definition. [LLM, STOCHASTIC, SYNC]
               STATE UPDATE: candidates += {definition, critique}
     1.2 Score the strongest candidate → best.               [LLM, STOCHASTIC]
     1.3 BREAK [IF: best.confidence >= accept_threshold]      # accepted early
     1.4 CONTINUE [IF: progress made]                         # keep debating
     1.5 BREAK [IF: stalled]                                  # converged below threshold
  2. DECISION [ON: best.confidence]
     2a. >= threshold → Propose the meaning for the lexicon: opaque MPL label,
         frame, definition, provenance.                       [GATED, HUMAN] [SATISFIES: R2, R3]
         CONSTRAINTS: append-only; MPL immutable; committed only after operator approval.
     2b. < threshold → Escalate to the undecided queue, optionally to frontier review. [EXTERNAL, GATED]
  3. RECURSE [BASE: referenced term already in lexicon or atomic; MAX_DEPTH: n]
     IF a definition invents/references a new term, define it too (CALL DefineTerm).
  OUTPUT: a proposed meaning (pending approval) or an escalation entry
```

## PROCESS — Narrative (same backbone)

```
PROCESS — BuildOntology: grow the lexicon from a watched folder.
  1. Keep watching `input/`. For each new document:
     1.1 Ingest it, storing the source exactly as-is and rejecting duplicates by
         checksum.
     1.2 Pull out the candidate terms and the sense (frame) each is used in.
     1.3 Define every candidate (below).

PROCESS — DefineTerm: agree a definition for one term-in-a-frame.
  1. Debate — at most `max_debate_iterations` rounds:
     1.1 Agents take turns, one at a time, proposing or critiquing a definition,
         always citing the source and never rewriting it.
     1.2 Score the best definition so far for confidence.
     1.3 If it clears the acceptance threshold, stop — we have a definition.
     1.4 If the round made progress, keep debating.
     1.5 If it has stalled below the threshold, stop and escalate.
  2. Then:
     2a. If confident enough, propose the meaning for the lexicon — an opaque
         label, its frame, definition, and provenance — to be committed only
         after the operator approves it (append-only; labels never change).
     2b. If not, send it to the undecided queue, and optionally to a stronger
         frontier model for review.
  3. If defining this term surfaced a brand-new term, define that one too — the
     same way — stopping when it bottoms out at terms already known or atomic.
```

---

## STATE REFERENCE (stub)

- **M1 lexicon** — append-only store of meanings: `{MPL (immutable), frame,
  definitions[], parent, provenance}`. Shared/global; grows only.
- **M2 candidates** — per-term debate working set: proposed definitions + critiques + scores.
- **M3 best** — the leading `{definition, confidence}` this round (recomputed each pass).

---

## Stress-test notes (gaps surfaced for the spec)

What worked well: `QUEUE [ROUND_ROBIN]` captured the serialized agent debate
naturally; `BREAK`/`CONTINUE [IF]` made the multi-exit loop (accept early /
keep going / stall) readable (a direct payoff of the Tirzah fix); `[GATED, HUMAN]`
expressed review-gated writes; `RECURSE [BASE/MAX_DEPTH]` fit term invention; and
the principles mapped onto `REQUIREMENTS`.

New gaps (added to the running list from Hoglah):
1. **Pausing for a human, possibly indefinitely.** Step 2a is `[GATED, HUMAN]` —
   the process *suspends* until the operator approves, which may be much later or
   never. Cairn has no notion of **await / suspend-and-resume** on an external
   (human or system) event. This is the human-in-the-loop analogue of Hoglah's
   crash-recovery gap: real processes *wait*.
2. **RECURSE vs CALL overlap.** I expressed term invention as both a `RECURSE`
   block *and* a `CALL DefineTerm` — they're the same act (recurse = call self).
   The spec should say recursion *is* a self-`CALL` with `BASE`/`MAX_DEPTH`, so
   authors don't double-notate.
3. **DECISION as a step with branch-bodies.** Step 2's branches (2a/2b) are
   substantial sub-flows, not one-liners. Cairn's `DECISION → A | B` reads fine
   inline but the spec should show how a branch *body* nests (lettered sub-steps,
   like PARALLEL's 3a/3b — reuse that convention).
4. **"MAY" requirements (R4 polysemy)** are capabilities, not obligations — the
   spec lists `[MAY]` but should note that `[SATISFIES: R4]` on a step means
   "supports", not "guarantees".

Recurring from Hoglah and reconfirmed here:
- **Long-running SERVICE with no join** (BuildOntology's watched folder, like
  Hoglah's three services) — strongest signal yet that Cairn needs a `SERVICE`
  construct.
