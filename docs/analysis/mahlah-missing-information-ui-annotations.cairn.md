## Missing information UI human load

PURPOSE:
  Record human-load evidence observed during UI simulation `mahlah-missing-information`.

EVIDENCE:
  ui_simulation: mahlah-missing-information
  clicks: 1
  fills: 1
  waits: 1
  context_switches: 1
  popups: 0

HUMAN_DEMAND:
  AWARENESS: The user must locate where to ask for help before they can express uncertainty.
  EXECUTION: The user or tester must choose a model path before testing the missing-information case. The user asks a natural question while leaving out the object, source, and authority needed for a reliable answer.
  NOTIFICATION: The user must decide whether the response correctly asks for missing context or over-answers the request.
  INSPECTION: The user switches from task completion to checking whether the system recognised missing context.

HUMAN_LOAD:
  focus_actions: 3
  trivial_actions: 1
  context_switches: 1
  input_burden: 1 fill action(s)
  closure_clarity: uncertain
  human_systems: attention, attention switching, audit reasoning, comprehension, configuration, decision, language, orientation, trust calibration, uncertainty management, working memory

HUMAN_FACTORS:
  cognitive_load: context switching - The simulation observed 1 explicit context switch(es).
  cognitive_load: uncertainty load - The scenario declares uncertainty management as part of the user's task.
  interface_friction: system-use overhead - The task included controls or inputs that support the system rather than the business question itself.
  scenario_finding: Missing-information recursion finding - If an AI system answers incomplete requests without surfacing uncertainty, the human may need extra recursion to discover what was assumed.

HUMAN_RISK:
  probability: medium
  impact: high
  confidence: medium
  score: significant
  rationale: Estimated from observed UI actions, context switches, and scenario annotations; validate with real users.

REVIEW:
  Treat this as design evidence, not measurement of a person.
  Confirm the annotations with the process owner and representative users before adopting.