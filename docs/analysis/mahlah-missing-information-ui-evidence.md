# UI Human-Load Evidence: mahlah-missing-information

## Metrics
- assertions: 2
- clicks: 1
- contextSwitches: 1
- fills: 1
- popups: 0
- screenshots: 0
- waits: 1

## Phases
- **awareness**
  - The user must locate where to ask for help before they can express uncertainty.
- **execution**
  - The user or tester must choose a model path before testing the missing-information case.
  - The user asks a natural question while leaving out the object, source, and authority needed for a reliable answer.
- **notification**
  - The user must decide whether the response correctly asks for missing context or over-answers the request.
- **inspection**
  - The user switches from task completion to checking whether the system recognised missing context.

## Human Systems
attention, attention switching, audit reasoning, comprehension, configuration, decision, language, orientation, trust calibration, uncertainty management, working memory

## Findings
- **cognitive_load: context switching** - The simulation observed 1 explicit context switch(es).
  Mitigation: Keep the primary task resumable and make cross-surface state correlation visible.
- **cognitive_load: uncertainty load** - The scenario declares uncertainty management as part of the user's task.
  Mitigation: Surface missing context, assumptions, and confidence before asking the user to trust or act on the answer.
- **interface_friction: system-use overhead** - The task included controls or inputs that support the system rather than the business question itself.
  Mitigation: Separate expert configuration from ordinary execution, or preserve safe defaults.
- **scenario_finding: Missing-information recursion finding** - If an AI system answers incomplete requests without surfacing uncertainty, the human may need extra recursion to discover what was assumed.
  Mitigation: Design answer paths that ask for missing object, authority, source, and date context before proceeding.

## Risk
significant (probability: medium; impact: high; confidence: medium)
Estimated from observed UI actions, context switches, and scenario annotations; validate with real users.

## Suggested Cairn Blocks
### HUMAN_DEMAND
```cairn
AWARENESS: The user must locate where to ask for help before they can express uncertainty.
EXECUTION: The user or tester must choose a model path before testing the missing-information case. The user asks a natural question while leaving out the object, source, and authority needed for a reliable answer.
NOTIFICATION: The user must decide whether the response correctly asks for missing context or over-answers the request.
INSPECTION: The user switches from task completion to checking whether the system recognised missing context.
```

### HUMAN_LOAD
```cairn
focus_actions: 3
trivial_actions: 1
context_switches: 1
input_burden: 1 fill action(s)
closure_clarity: uncertain
human_systems: attention, attention switching, audit reasoning, comprehension, configuration, decision, language, orientation, trust calibration, uncertainty management, working memory
```

### HUMAN_FACTORS
```cairn
cognitive_load: context switching - The simulation observed 1 explicit context switch(es).
cognitive_load: uncertainty load - The scenario declares uncertainty management as part of the user's task.
interface_friction: system-use overhead - The task included controls or inputs that support the system rather than the business question itself.
scenario_finding: Missing-information recursion finding - If an AI system answers incomplete requests without surfacing uncertainty, the human may need extra recursion to discover what was assumed.
```

### HUMAN_RISK
```cairn
probability: medium
impact: high
confidence: medium
score: significant
rationale: Estimated from observed UI actions, context switches, and scenario annotations; validate with real users.
```