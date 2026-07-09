# Manual Agent Analysis Orchestration Pattern

Use this scaffold when a human gives an agent a GitHub link, process file, UI
evidence bundle, or screenshot and asks for Cairn analysis.

1. Load the target repository or process file. Record what was actually read and
   list missing files as open questions.
2. Load Cairn semantic context: SPEC, README, OKF concept index, human factors,
   augmentation process, HCI touchpoints, and functional layout load.
3. Classify the process type and identify all human-facing surfaces.
4. Apply human-factors and augmentation lenses phase by phase. Separate observed
   evidence from inference.
5. Analyze HCI touchpoints and layout load whenever an interface is present.
6. Generate interface recommendations. Every recommendation must cite the exact
   OKF file and concept that drove it.
7. Produce a report with executive summary, current-state analysis,
   recommendations, risks, mitigations, references, and open questions.
8. Validate the output: no uncited recommendations, no hidden assumptions, no
   unsupported certainty.

Required recommendation fields: change, current state, future state, rationale,
priority, effort, OKF file, OKF concept, and research driver where available.
