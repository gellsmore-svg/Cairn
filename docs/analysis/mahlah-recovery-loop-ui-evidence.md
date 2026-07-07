# UI Human-Load Evidence: mahlah-recovery-loop

## Metrics
- assertions: 2
- clicks: 1
- contextSwitches: 1
- fills: 2
- popups: 0
- screenshots: 0
- waits: 2

## Phases
- **awareness**
  - The user must find the input surface before they can repair an unclear request.
- **execution**
  - The tester chooses a deterministic adapter so the recovery loop can be inspected repeatably.
  - The user expresses intent but omits the object, authority, and source context required for safe completion.
- **notification**
  - The user must judge whether the answer resolves the missing context or requires a repair turn.
  - The user must decide whether the repaired answer has enough authority and evidence to close the loop.
- **recovery**
  - The user must reconstruct missing details, name uncertainty, and avoid accepting accountability they cannot verify.
- **inspection**
  - The user switches into audit mode to check whether the repair turn changed the process state.

## Human Systems
accountability, attention, attention switching, audit reasoning, comprehension, configuration, decision, language, orientation, recall, trust calibration, uncertainty management, working memory

## Findings
- **cognitive_load: context switching** - The simulation observed 1 explicit context switch(es).
  Mitigation: Keep the primary task resumable and make cross-surface state correlation visible.
- **cognitive_load: uncertainty load** - The scenario declares uncertainty management as part of the user's task.
  Mitigation: Surface missing context, assumptions, and confidence before asking the user to trust or act on the answer.
- **interface_friction: system-use overhead** - The task included controls or inputs that support the system rather than the business question itself.
  Mitigation: Separate expert configuration from ordinary execution, or preserve safe defaults.
- **scenario_finding: Recovery recursion finding** - Repair turns can shift hidden work onto the human: remembering context, clarifying authority, and checking whether the AI incorporated the correction.
  Mitigation: Make missing fields, authority gaps, and incorporated corrections explicit before the user is asked to close the loop.

## Risk
significant (probability: medium; impact: high; confidence: medium)
Estimated from observed UI actions, context switches, and scenario annotations; validate with real users.

## Suggested Cairn Blocks
### HUMAN_DEMAND
```cairn
AWARENESS: The user must find the input surface before they can repair an unclear request.
EXECUTION: The tester chooses a deterministic adapter so the recovery loop can be inspected repeatably. The user expresses intent but omits the object, authority, and source context required for safe completion.
NOTIFICATION: The user must judge whether the answer resolves the missing context or requires a repair turn. The user must decide whether the repaired answer has enough authority and evidence to close the loop.
RECOVERY: The user must reconstruct missing details, name uncertainty, and avoid accepting accountability they cannot verify.
INSPECTION: The user switches into audit mode to check whether the repair turn changed the process state.
```

### HUMAN_LOAD
```cairn
focus_actions: 5
trivial_actions: 1
context_switches: 1
input_burden: 2 fill action(s)
closure_clarity: uncertain
human_systems: accountability, attention, attention switching, audit reasoning, comprehension, configuration, decision, language, orientation, recall, trust calibration, uncertainty management, working memory
```

### HUMAN_FACTORS
```cairn
cognitive_load: context switching - The simulation observed 1 explicit context switch(es).
cognitive_load: uncertainty load - The scenario declares uncertainty management as part of the user's task.
interface_friction: system-use overhead - The task included controls or inputs that support the system rather than the business question itself.
scenario_finding: Recovery recursion finding - Repair turns can shift hidden work onto the human: remembering context, clarifying authority, and checking whether the AI incorporated the correction.
```

### HUMAN_RISK
```cairn
probability: medium
impact: high
confidence: medium
score: significant
rationale: Estimated from observed UI actions, context switches, and scenario annotations; validate with real users.
```