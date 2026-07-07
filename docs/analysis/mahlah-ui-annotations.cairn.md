## Review Mahlah UI human load

PURPOSE:
  Record human-load evidence observed during UI simulation `mahlah-human-load`.

EVIDENCE:
  ui_simulation: mahlah-human-load
  clicks: 4
  fills: 2
  waits: 2
  context_switches: 3
  popups: 1

HUMAN_DEMAND:
  AWARENESS: The user needs a stable signpost that confirms they are in the expected workspace. The next action should be visually obvious without reading process instrumentation. The process trace should be discoverable without competing with the primary answer.
  EXECUTION: Adapter selection is a system-use decision, not part of the user's business task. The user translates intent into a prompt and must preserve the question while operating the UI.
  NOTIFICATION: The response should arrive as a readable answer, with process detail available separately.
  INSPECTION: Inspecting the process trace deliberately moves the user from answer consumption into audit mode. A separate log window is powerful for developers but increases task switching cost.
  FEEDBACK: The user must convert an experience into actionable feedback without losing the original work context.

HUMAN_LOAD:
  focus_actions: 8
  trivial_actions: 4
  context_switches: 3
  input_burden: 2 fill action(s)
  closure_clarity: uncertain
  human_systems: attention, attention switching, audit reasoning, comprehension, configuration, context switching, debug reasoning, decision, language, metacognition, motor planning, orientation, recall, social risk, trust calibration, working memory

HUMAN_FACTORS:
  cognitive_load: context switching - The simulation observed 3 explicit context switch(es).
  interface_friction: mode switching - The simulation opened a separate popup/window during task inspection.
  interface_friction: system-use overhead - The task included controls or inputs that support the system rather than the business question itself.
  organisational_change: feedback capture burden - The user is asked to translate an experience into feedback after completing the main task.
  scenario_finding: Human-load finding - System configuration and developer inspection controls create useful power, but they can pull attention away from the user's primary task.
  scenario_finding: Trace completeness finding - An inspectable but empty process trace can create uncertainty about whether the system did hidden work or simply has no available instrumentation for this path.

HUMAN_RISK:
  probability: high
  impact: medium
  confidence: medium
  score: significant
  rationale: Estimated from observed UI actions, context switches, and scenario annotations; validate with real users.

REVIEW:
  Treat this as design evidence, not measurement of a person.
  Confirm the annotations with the process owner and representative users before adopting.