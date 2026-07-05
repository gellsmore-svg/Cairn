---
type: Reference
title: Specification (SPEC.md)
description: The normative Cairn specification, v0.9 — covering versioned PLAN envelopes, the three document modes, the shared backbone and render profiles, the core grammar and constructs, STATE, tags, CONTEXT/CONSTRAINTS, requirements/outcomes, composition, conformance, and versioning.
resource: https://github.com/gellsmore-svg/Cairn/blob/main/SPEC.md
tags: [cairn, spec, normative]
timestamp: 2026-07-05T00:00:00Z
---

# Specification — `SPEC.md` (v0.9)

The normative definition of Cairn. Section map:

- §0 Reading guide · §1 [Document structure — three modes](../concepts/document-modes.md)
- §2 Design principles · §3 [The shared backbone and its render profiles](../concepts/backbone-and-render-profiles.md)
- §4 Core grammar · §5 [Constructs](../concepts/constructs.md)
- §6 [STATE](../concepts/state.md) · §7 [Tags](../concepts/tags.md) · §8 CONTEXT and CONSTRAINTS
- §9 [Requirements & Outcomes](../concepts/composition.md) · §10 [Composition (signatures + CALL)](../concepts/composition.md)
- §11 Worked example · §12 Conformance (structural) · §13 Versioning & evolution

It is deliberately small — the language is meant to fit in one document and be
read by both humans and LLMs. The formal style's syntax is given precisely in the
[grammar](grammar.md).

## §4.6 — PLAN interpretation (added in spec 0.9 / conformance 0.2+)

A `PLAN` may be **interpreted**: walked step-by-step by a runtime that enforces
`depends_on`, `allowed_tools`, and the per-step status machine
(`pending / active / completed / blocked / skipped` — `STEP_STATUSES` in the
conformance surface). Dispatch is by construct; execution context crosses steps
through a bounded artifact map; each transition emits a `plan.step.*` process
event. The degenerate single-CALL plan collapses to a monolithic executor —
interpretation buys granular tool gating, resumability, and live visibility.
Tirzah's `planning/executor.py` is the reference interpreter.

