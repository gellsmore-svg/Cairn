# Family Human-Factors Analysis Notes

Generated while testing Cairn's offline human-factors analyzer against existing
family examples.

## Hoglah

Input: `examples/hoglah.cairn.md`

Result: the analyzer produced no substantive findings. That is expected for this
slice: it describes crash-safe queue mechanics and durable handoff rather than a
human-facing operator workflow.

Design implication: Hoglah itself is a strong fit as an execution substrate for
queued LLM interpretation, but the current Cairn example should not be treated as
a human-demand example until we model operator experiences such as:

- diagnosing queue failures,
- choosing when to retry or cancel jobs,
- interpreting status/debug output,
- configuring real vs stub model adapters,
- trusting a queued LLM result after delay or retry.

## Tirzah Semantic Review

Input: `examples/tirzah-semantic-review.cairn.md`

Initial result: the analyzer found human-gated steps but little structured
human-demand detail. We then annotated the semantic-review flow with
`HUMAN_DEMAND`, `HUMAN_LOAD`, `HUMAN_FACTORS`, `HUMAN_RISK`, `TRUST`, `SUPPORT`,
and `IMPROVEMENT` blocks.

Updated result: `docs/analysis/tirzah-semantic-review-human-factors.md` now
surfaces the main review burdens:

- reviewer attention and ambiguity load while inspecting candidate graph edges,
- trust calibration around label/vector similarity suggestions,
- accountability for promoted semantic edges,
- queue fatigue when many candidates are pending,
- closure clarity after accept/reject.

Recommended next modeling step: use this annotated example as the pattern for
other human-gated family workflows, especially generated-output endorsement and
Mahlah's conversational ask UI.

## Tirzah Generated Output Endorsement

Input: `examples/tirzah-generated-output.cairn.md`

Updated result: the generated-output trust gate is now annotated with human
demand and risk detail. The report in
`docs/analysis/tirzah-generated-output-human-factors.md` highlights:

- context burden while comparing query, answer, provenance, and source nodes,
- risk that fluent generated output is promoted into trusted memory too easily,
- one-click endorsement as the lowest-effort path,
- reviewer accountability for future retrieval behaviour,
- provenance/note capture as the difference between auditability and opaque
  trust changes.

Design implication: generated-output endorsement and semantic-edge review share
the same family pattern: a human-gated durable write whose quality depends on
context visibility, calibrated trust, and low-friction rejection/defer paths.
