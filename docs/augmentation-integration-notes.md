# Augmentation Integration Notes

This note records the first Cairn integration of the Augmentation Process lens.
It is intended as review context for maintainers and consuming LLMs.

## Files Changed

- `okf/concepts/augmentation-process.md` - new semantic lens.
- `okf/concepts/human-factors.md` - added Augmentation Process factor family.
- `okf/concepts/hci-touchpoints.md` and `docs/HCI-TOUCHPOINTS.md` - added
  augmentation-specific touchpoint and cognitive-aesthetic questions.
- `okf/concepts/functional-layout-load.md` and
  `docs/FUNCTIONAL-LAYOUT-LOAD.md` - added AI recommendation, uncertainty,
  evidence, and override geometry considerations.
- `src/cairn/human_factors.py` - added offline cue detection and LLM prompt
  language for augmentation.

## Research Mapping

- [DARPA Augmented Cognition TIE](https://www.semanticscholar.org/paper/Overview-of-the-DARPA-Augmented-Cognition-Technical-John-Kobus/98228d1f499802a2106d1e48716d4e810414f243)
  maps to cognitive-state visibility, workload gauges, adaptation triggers, and
  loop closure.
- [Nguyen and Elbanna's 2025 workplace review](https://link.springer.com/article/10.1007/s10796-025-10591-5)
  maps to enabling practices, role complementarity, outcomes, and the need to
  capture behavioural and longitudinal evidence.
- [Gomez et al.'s interaction-pattern taxonomy](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2024.1521066/full)
  maps to interaction richness: challenge, revise, ask why, compare, override,
  and maintain shared task state.
- [Irlenbusch et al.'s experimental-economics trust review](https://ideas.repec.org/p/ajk/ajkdps/417.html)
  maps to calibrated reliance under transparency, accountability, fairness,
  privacy, and efficiency constraints.
- [Romeo and Conti's automation-bias review](https://link.springer.com/article/10.1007/s00146-025-02422-7)
  maps to over-reliance, explanation over-trust, and the need for
  verification-oriented explanations.
- [Shared mental model work](https://hrilab.tufts.edu/publications/scheutzetal17smm.pdf)
  maps to explicit task, role, equipment, environment, workload, and progress
  models in human-agent teams.
- Recent "who thrives with AI" work maps to trait-aware onboarding and
  personalisation of augmentation level.

## Remaining Gaps

- Cairn still uses qualitative risk. Real deployments should validate the
  augmentation lens with user research, field observation, or controlled
  comparison where consequences justify it.
- The functional layout analyzer records geometry, but does not yet score
  `ai_output_to_evidence`, `uncertainty_to_action`, or
  `override_for_recommendation` as separate numeric metrics.
- A worked end-to-end augmentation example would help show the new lens in a
  complete Cairn process.
