## [Unreleased]

## [0.5.0] — 2026-07-05

- **`cairn.grammar`:** executable GRAMMAR.md EBNF parser — `parse_document`,
  `validate_document` (SPEC §12 well-formedness), `document_to_plan`,
  markdown `.cairn.md` extraction, AST bridge to `cairn.render`.
- **`cairn-validate` CLI** and Keturah manifest capabilities `parse_document` /
  `validate_document`.
- **`scripts/validate_examples.py`** now uses the grammar parser (zero syntax
  errors required across `examples/*.cairn.md`).

## [0.4.1] — 2026-07-05

- **`cairn.render` continued:** `audit` profile (SPEC §3.1), French (`fr`) phrasing,
  `max_depth` / `sections` filters, PLAN envelope header in views, operator phase
  parsing (unnumbered titles), `register_exporter` / `export_view` hooks for docx/PDF
  plugins, `cairn-render` CLI.

## [0.4.0] — 2026-07-05

- **`cairn.render` / `render_plan`:** simplified view generator — narrative_steps,
  simple_prose, operator, executive profiles; markdown/text/json/mermaid output;
  en/es phrasing; optional YAML stylesheets (`[render]` extra); Keturah manifest
  capability. See [docs/VIEW-GENERATOR.md](docs/VIEW-GENERATOR.md).

## [Unreleased] (spec / examples — prior)

- **SPEC §4.6** — PLAN interpretation: step state machine, handler dispatch, trace.
- Added **`STEP_STATUSES`** to conformance validation.
- Tirzah: `answer_query` unified via retrieve/synthesize phases; `plan_executions` resume store.
- Tirzah: split `retrieve_for_answer` / `synthesize_from_retrieval` for interpretive handlers.
- Added **`tirzah-plan-interpreter.cairn.md`** — interpretive execution target + Tirzah v1 handlers.
- Added **`tirzah-recursive-planning.cairn.md`** — live PLAN propose/execute/revise seam.
- Added **`hoglah-submit.cairn.md`** (pure submitter) and **`relational-substrate.cairn.md`**.
- Added **`tirzah-generated-output.cairn.md`** — queue → unreviewed nodes → endorse/reject.
- Added **`tirzah-web-research.cairn.md`** — `--web` promotion and bounded search/fetch.
- Added **`keturah.cairn.md`** (manifest + MCP) and **`galeed.cairn.md`** (trace spine).
- Updated **`tirzah-system.cairn.md`** composition map (TRUST milestone, web, Galeed).
- Added Cairn stress-test examples for **Mahlah** (three-channel conversational
  ask UI) and **Milcah** (recursive coherence-pressure rounds).
- Added **`tirzah-ingest.cairn.md`** — ingestion pipeline, dead-letter, profile backfill.
- Rewrote **`hoglah.cairn.md` v2** — `CONCURRENT`/`SERVICE`, `DURABLE-BEFORE`,
  `RECOVERY`, `IDEMPOTENT [KEY: …]`, `EMERGENT [SATISFIES: …]` illustration.
- Added **`mizpah.cairn.md`** (cross-session trace browser) and
  **`tirzah-system.cairn.md`** (ingest → ask → observe composition).
- Expanded **`tirzah.cairn.md`** — `DECISION` across direct/agentic/deep modes.
- Added **`tirzah-semantic-review.cairn.md`** — enqueue → human review → graph edge.
- Added **`scripts/validate_examples.py`** + pytest skeleton check for `*.cairn.md`.
- SPEC §9 — documented `EMERGENT [SATISFIES: …]` block form (equivalent to inline `via` form).
- Updated `examples/README.md` and OKF examples reference; fixed README SPEC
  version line (v0.9).

## [0.9] — 2026-06-24

- Added the `PLAN` revision envelope for live recursive process instances,
  including identity, parent revision, status, trigger information, and a complete
  bounded `PROCESS` backbone on every revision.

# Changelog

All notable changes to the Cairn specification are recorded here.

## [0.8] — 2026-06-16

From feedback after modelling an end-to-end human-led, AI-assisted delivery
process (customer idea → frame → build → verify → release → change management):

- **Render profiles (§3).** The "two styles" generalise to audience profiles —
  one canonical backbone *projected* into `ai` (precise), `operator` (guided
  operational narrative), `executive` (overview), and `audit` (defensible record).
  Profiles are rendered by tooling/AI, not hand-authored. `render-profile:` selects
  one. The **operator profile** is specified in full (Purpose / Owner / Assisted-by
  / Outputs / Iterate-until / Next, with compression rules + a "don't over-compress"
  guardrail).
- **Ownership vs. contribution (§7).** The `Actor` dimension is the *accountable
  owner*; `ASSISTED-BY: <actors>` names who materially contributes — e.g.
  `[HUMAN, ASSISTED-BY: LLM]`. Owners may carry a role (`[HUMAN: Product Lead]`).
  Hybrid human-led / AI-assisted work no longer disappears at the top level.
- **`MILESTONE` and `PURPOSE`** constructs — major transitions and per-phase intent,
  the signals the human-facing profiles render.

## [0.7] — 2026-06-16

First **stress-tested release**: the v0.6 draft plus everything learned from
describing three real systems (Tirzah, Hoglah, Mahalath) in Cairn. Adds a
structural grammar ([GRAMMAR.md](GRAMMAR.md)).

**Renamed** from the working title "APML" to **Cairn** — a cairn marks a route
with simple waypoints so anyone who follows can stay on the path, which is what a
Cairn description does for humans and AI.

Revision following design review. Adds:

- **Three document modes** — CONTEXT (scene), REQUIREMENTS/OUTCOMES (testable
  assertions), PROCESS (flow) — kept distinct.
- **Shared backbone + dual styles.** Formal and Narrative are two renderings of
  one canonical structure (numbering + constructs + tags + state); an AI keeps
  them in sync. Formal is canonical for machine semantics.
- **Scoped, referenced STATE.** Inline directional declarations
  (`scope`/`dir`/`ref`) linked by number to a definitive STATE REFERENCE.
- **Progressive-formality construct modifiers** with defaults (ITERATE
  `UNTIL/MAX`, RECURSE `BASE/MAX_DEPTH`, QUEUE `ORDER`, PARALLEL `STATE/MERGE`,
  RETRY `MAX/BACKOFF`, ERROR propagation).
- **Tags as orthogonal dimensions** (Actor / Determinism / Timing / Effects /
  Control) + namespaced extensions; vocabulary grows from real use.
- **Requirements & Outcomes mode** — `R#` SHALL/SHOULD assertions with
  `ACCEPTANCE`, `[MUST/SHOULD/MAY]`, and `[SATISFIES: R#]` traceability.
- **Composition** — PROCESS signatures (INPUT/OUTPUT) + `CALL`.
- **Structural conformance** rules + a worked example in both styles.

Refinements from the first stress test (Tirzah, `examples/tirzah.cairn.md`):

- **`BREAK` / `CONTINUE`** loop control + `ITERATE UNTIL` may read body-set state
  (explicit loop exit instead of a DECISION "falling out").
- **Fan-out clarified** — a step may make many like calls (`[BATCH]`) and still be
  one step; `PARALLEL` is reserved for concurrent independent branches.
- **`ERROR THEN: fallback → <target>`** names the concrete recovery.
- **STATE scope semantics** spelled out (§6.4); `iteration` scope resets each round.
- **STATE across `CALL`** is private by default (§6.5) — data crosses via
  INPUT/OUTPUT; shared mutable state must be declared at a shared scope.

Refinements from stress tests 2–3 (Hoglah, Mahalath):

- **`SERVICE` + `CONCURRENT`** — long-running concurrent activities that never
  join (worker loops, consumers, watched folders), distinct from `PARALLEL`
  (which joins at MERGE).
- **`AWAIT [EVENT/TIMEOUT/THEN]`** — suspend until a human/system event; real
  processes wait (the `[GATED, HUMAN]` and broker-ack cases).
- **`ATOMIC` / `DURABLE-BEFORE` / `RECOVERY:`** — express safety-critical ordering
  between steps and what happens if a crash lands between them (the crash-window
  analogue of `ERROR` fallback).
- **`RECURSE` is a self-`CALL`** — clarified, so recursion isn't double-notated.
- **`DECISION` branch bodies** — multi-step branches nest with letters (`2a.`/`2b.`),
  like PARALLEL.
- **`IDEMPOTENT [KEY: …]`** + parameterised tags (`BATCH [n]`).
- **Emergent guarantees** — `[SATISFIES]` may name several steps across processes;
  `[MAY]` = capability, so `[SATISFIES]` on it means "supports", not "guarantees".

## [0.5] — prior

Initial prototype: PROCESS / numbered hierarchy / core verbs / tags / constructs
(ITERATE, RECURSE, QUEUE, PARALLEL, DECISION, RETRY, ERROR, STATE UPDATE, OUTPUT,
RISKS), CONSTRAINTS/BOUNDARIES and CONTEXT blocks, Formal + Narrative styles.
