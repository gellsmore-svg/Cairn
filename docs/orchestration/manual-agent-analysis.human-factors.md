# Manual Agent Analysis Human-Factors View

## Human Demand

- `awareness`: the agent must discover what repo, process, or interface is in scope.
- `orientation`: the agent must load Cairn OKF context before judging the target.
- `execution`: the agent applies human-factors, augmentation, HCI, and layout lenses.
- `feedback`: the agent reports what evidence was read and what remains missing.
- `handoff`: the final report must be usable by a developer, designer, or process owner.

## Human Risk

- `probability: medium`
- `impact: high`
- `confidence: medium`
- `score: significant`
- `rationale`: manual agent analysis is useful but prone to drift unless every
  finding and recommendation is tied back to source evidence and OKF concepts.

## Guardrails

- Cite exact OKF files and concept names for each recommendation.
- Mark UI/user-experience claims as inference unless backed by evidence.
- Do not invent repository structure, implementation details, or research claims.
- Prefer open questions over confident guesses.
- Keep Cairn core focused; propose separate modules/repos for logging,
  dashboards, provider orchestration, or product-specific telemetry.
