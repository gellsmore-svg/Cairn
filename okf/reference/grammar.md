---
type: Reference
title: Grammar (GRAMMAR.md)
description: The formal (EBNF) grammar of Cairn's formal style — the precise syntax for processes, steps, constructs, tags, STATE, and sub-blocks that the SPEC describes prose-first.
resource: https://github.com/gellsmore-svg/Cairn/blob/main/GRAMMAR.md
tags: [cairn, grammar, ebnf, syntax]
timestamp: 2026-06-19T00:00:00Z
---

# Grammar — `GRAMMAR.md`

The formal (EBNF) grammar for Cairn's **formal style** — the precise, machine-
checkable syntax behind the prose-first [specification](spec.md). It pins down how
[constructs](../concepts/constructs.md), [tags](../concepts/tags.md),
[STATE](../concepts/state.md), and the OUTPUT/RISKS/PURPOSE/CONSTRAINTS sub-blocks
are written.

The grammar covers only the **`ai`/formal** projection; the narrative and other
[render profiles](../concepts/backbone-and-render-profiles.md) are lossy
projections of the same backbone and are not separately grammared. Validity is the
**structural conformance** of [SPEC §12](spec.md).
