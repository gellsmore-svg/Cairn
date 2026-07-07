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

Result: the analyzer found human-gated steps but little structured human-demand
detail. The current report therefore starts a conversation rather than producing
rich risk estimates.

Design implication: this is a good next candidate for manual annotation. The
likely human-system forces are:

- reviewer attention and ambiguity load while inspecting candidate graph edges,
- trust calibration around label/vector similarity suggestions,
- accountability for promoted semantic edges,
- queue fatigue when many candidates are pending,
- closure clarity after accept/reject.

Recommended next modeling step: add `HUMAN_DEMAND`, `HUMAN_FACTORS`, and
`HUMAN_RISK` blocks to the Tirzah semantic-review example, then rerun
`cairn-human-factors`.
