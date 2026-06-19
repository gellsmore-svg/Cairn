---
type: Project
title: Cairn
description: A simple, textual, human-readable meta-language for describing complex processes clearly and consistently — especially agentic / LLM-centric ones — so humans and LLMs collaborate on the same process description, independent of any language or platform.
resource: https://github.com/gellsmore-svg/Cairn
tags: [cairn, meta-language, process, agentic, specification]
timestamp: 2026-06-19T00:00:00Z
---

# Cairn

Cairn is a simple, textual, human-readable **meta-language for describing complex
processes** — especially agentic / LLM-centric ones. It lets humans and LLMs
collaborate using the **same** description of a process, independent of any
programming language or platform, bridging pseudocode-style clarity with modern
agentic realities: iteration, recursion, non-determinism, sync/async, queuing, and
error handling.

The specification is [SPEC.md](https://github.com/gellsmore-svg/Cairn/blob/main/SPEC.md)
(v0.8); this bundle is an [Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
description of its concepts and reference material.

## Map

- **[Concepts](concepts/index.md)** — the language ideas: the three document
  modes, the shared backbone + render profiles, the process constructs, STATE,
  tags, and composition.
- **[Reference](reference/index.md)** — the concrete artifacts: the spec, the
  grammar, and the worked examples.

## At a glance

- One **canonical backbone**, rendered to audience [profiles](concepts/backbone-and-render-profiles.md)
  (`ai` / `operator` / `executive` / `audit`) — authored once, not maintained in
  parallel.
- Three [document modes](concepts/document-modes.md): CONTEXT, REQUIREMENTS/OUTCOMES,
  PROCESS.
- A small set of [constructs](concepts/constructs.md) for real control flow.
- License: Apache-2.0. Used across the family — see the
  [examples](reference/examples.md) (Tirzah, Hoglah, Mahalath).
