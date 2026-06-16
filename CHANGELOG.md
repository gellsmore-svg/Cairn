# Changelog

All notable changes to the Cairn specification are recorded here.

## [0.6] — 2026-06-16 (draft)

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

## [0.5] — prior

Initial prototype: PROCESS / numbered hierarchy / core verbs / tags / constructs
(ITERATE, RECURSE, QUEUE, PARALLEL, DECISION, RETRY, ERROR, STATE UPDATE, OUTPUT,
RISKS), CONSTRAINTS/BOUNDARIES and CONTEXT blocks, Formal + Narrative styles.
