## Recovery loop UI human load

PURPOSE:
  Record human-load evidence observed during UI simulation `mahlah-recovery-loop`.

EVIDENCE:
  ui_simulation: mahlah-recovery-loop
  clicks: 1
  fills: 2
  waits: 2
  context_switches: 1
  popups: 0

HUMAN_DEMAND:
  AWARENESS: The user must find the input surface before they can repair an unclear request.
  EXECUTION: The tester chooses a deterministic adapter so the recovery loop can be inspected repeatably. The user expresses intent but omits the object, authority, and source context required for safe completion.
  NOTIFICATION: The user must judge whether the answer resolves the missing context or requires a repair turn. The user must decide whether the repaired answer has enough authority and evidence to close the loop.
  RECOVERY: The user must reconstruct missing details, name uncertainty, and avoid accepting accountability they cannot verify.
  INSPECTION: The user switches into audit mode to check whether the repair turn changed the process state.

HUMAN_LOAD:
  focus_actions: 5
  trivial_actions: 1
  context_switches: 1
  input_burden: 2 fill action(s)
  closure_clarity: uncertain
  human_systems: accountability, attention, attention switching, audit reasoning, comprehension, configuration, decision, language, orientation, recall, trust calibration, uncertainty management, working memory

HUMAN_FACTORS:
  cognitive_load: context switching - The simulation observed 1 explicit context switch(es).
  cognitive_load: uncertainty load - The scenario declares uncertainty management as part of the user's task.
  interface_friction: system-use overhead - The task included controls or inputs that support the system rather than the business question itself.
  scenario_finding: Recovery recursion finding - Repair turns can shift hidden work onto the human: remembering context, clarifying authority, and checking whether the AI incorporated the correction.

HUMAN_RISK:
  probability: medium
  impact: high
  confidence: medium
  score: significant
  rationale: Estimated from observed UI actions, context switches, and scenario annotations; validate with real users.

REVIEW:
  Treat this as design evidence, not measurement of a person.
  Confirm the annotations with the process owner and representative users before adopting.