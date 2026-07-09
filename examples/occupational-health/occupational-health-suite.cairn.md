# Occupational Health And Safety Suite

Worked Cairn examples for occupational health, safety management, worker
well-being, and return-to-work processes. These examples are process-design
patterns, not legal or medical advice.

## PROCESS — Safety And Health Management System

```cairn
PROCESS SafetyHealthManagementSystem (INPUT: workplace_operations; OUTPUT: continuously_improved_safety_health_program)
  1. Establish management leadership, resources, and visible commitment. [HUMAN, MACRO]
     PURPOSE: make worker safety and health a core operational value rather than an afterthought.
     HUMAN_FACTORS:
       social_role: managers signal whether production pressure outranks safety.
       incentives_game_theory: if speed is rewarded and hazard reporting is punished, unsafe silence becomes rational.
     SUPPORT: publish commitments, resources, accountabilities, and stop-work authority.

  2. Enable worker participation and reporting without retaliation. [HUMAN, GATED]
     HUMAN_DEMAND:
       ORIENT: know what to report and where.
       ACT: report hazard, near miss, injury, fatigue, violence, or psychosocial risk.
       CLOSE: see response, owner, and next action.
       RECOVER: escalate if the concern is ignored or punished.
     HUMAN_RISK:
       probability: high
       impact: high
       confidence: medium
       rationale: weak participation hides hazards until harm occurs.
     SUPPORT: anonymous routes, union/worker representative involvement where relevant, and visible closure.

  3. Identify hazards and assess risk. [HUMAN, ASSISTED-BY: inspection_tools]
     HCI_TOUCHPOINT:
       phase: execution
       human_goal: capture hazard evidence without paperwork becoming the barrier.
     HUMAN_FACTORS:
       cognitive_load: inspections fail when workers must remember complex checklists under production pressure.
       behavioural_economics: familiarity normalizes hazards that have not yet caused visible harm.

  4. Prevent and control hazards using hierarchy of controls. [HUMAN, GATED]
     SUPPORT: prefer elimination, substitution, engineering controls, administrative controls, then PPE.
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: high
       rationale: PPE-only responses can shift system risk onto individual attention and compliance.

  5. Train, communicate, evaluate, and improve the program. [ITERATIVE]
     CHANGE_IMPACT:
       reinforcement: track hazard closure, near-miss learning, training effectiveness, and worker trust.
       adaptation: update controls when work, tools, staffing, contractors, or environment changes.
```

## PROCESS — Incident, Near-Miss, And Learning Review

```cairn
PROCESS IncidentNearMissLearningReview (INPUT: incident_or_near_miss; OUTPUT: corrective_actions_and_learning)
  1. Stabilize people, site, evidence, and immediate risk. [HUMAN, GATED]
     HUMAN_DEMAND:
       ORIENT: understand immediate danger and who needs help.
       ACT: make safe, treat injury, isolate hazard, preserve evidence.
       RECOVER: restore safe work only after controls are confirmed.
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: high
       rationale: early response affects injury severity and later learning quality.

  2. Collect accounts, conditions, equipment state, workload, and organizational factors. [HUMAN, READONLY]
     HUMAN_FACTORS:
       trauma_informed: avoid blame-first questioning after harm or fear.
       social_role: low-power workers may withhold evidence if retaliation is plausible.
     SUPPORT: separate factual learning from discipline unless intentional harm or reckless violation is established.

  3. Analyze root and contributing causes. [HUMAN, ASSISTED-BY: LLM]
     AUGMENTATION_PROCESS:
       role_complementarity: AI can organize evidence and propose cause trees; humans verify context and controls.
       automation_bias: do not accept a neat root cause that stops at worker error.

  4. Implement corrective and preventive actions. [SIDE-EFFECT]
     SUPPORT: assign owner, due date, control type, verification method, and worker communication.

  5. Verify effectiveness and share learning. [FEEDBACK, ITERATIVE]
     CHANGE_IMPACT:
       reinforcement: learning review must change equipment, work design, staffing, training, or controls.
```

## PROCESS — Occupational Health Surveillance And Privacy

```cairn
PROCESS OccupationalHealthSurveillancePrivacy (INPUT: exposure_or_health_monitoring_need; OUTPUT: protected_worker_health_and_privacy)
  1. Define monitoring purpose, population, exposure, consent/legal basis, and privacy boundary. [HUMAN, GATED]
     HUMAN_FACTORS:
       trust: workers may fear health data will become performance or employability data.
       social_role: occupational health must protect health without becoming covert discipline.
     CONSTRAINTS: collect only what is necessary; separate clinical/confidential data from management reporting.

  2. Collect exposure and health data through appropriate clinical or technical process. [HUMAN, ASSISTED-BY: occupational_health_provider]
     HUMAN_DEMAND:
       ORIENT: understand what is being measured and why.
       ACT: participate, ask questions, or decline where applicable.
       CLOSE: know what happens with results and who can see them.

  3. Interpret aggregate patterns and individual fitness-for-work implications. [HUMAN, GATED]
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: medium
       rationale: misuse of health data can harm trust, employment, and legal compliance.
     SUPPORT: use aggregate reporting for prevention and confidential clinical communication for individuals.

  4. Improve controls and communicate population-level learning. [FEEDBACK]
     CHANGE_IMPACT:
       reinforcement: surveillance should drive hazard reduction, not normalize harmful exposure.
```

## PROCESS — Psychosocial Risk And Burnout Prevention

```cairn
PROCESS PsychosocialRiskBurnoutPrevention (INPUT: work_design_and_wellbeing_signals; OUTPUT: healthier_work_system)
  1. Identify workload, control, support, justice, role clarity, violence, and moral-injury risks. [HUMAN, READONLY]
     HUMAN_FACTORS:
       cognitive_load: chronic overload reduces attention, learning, and error recovery.
       trauma_informed: distress signals may reflect system strain, not individual weakness.
     SUPPORT: use confidential listening, workload data, and worker participation.

  2. Prioritize hazards in the work system. [HUMAN, GATED]
     HUMAN_RISK:
       probability: high
       impact: high
       confidence: medium
       rationale: burnout and psychosocial hazards affect health, safety, quality, and retention.
     CONSTRAINTS: do not reduce psychosocial risk management to resilience training alone.

  3. Redesign work controls and support. [MACRO, HUMAN]
     SUPPORT: adjust staffing, schedule, autonomy, conflict routes, recovery time, manager behaviour, and demand clarity.
     CHANGE_IMPACT:
       role_shift: managers become work-system designers, not only performance monitors.

  4. Evaluate outcomes and adapt. [FEEDBACK, ITERATIVE]
     HUMAN_DEMAND:
       CLOSE: workers see what changed because they participated.
```

## PROCESS — Return To Work And Reasonable Adjustment

```cairn
PROCESS ReturnToWorkReasonableAdjustment (INPUT: worker_health_limitation_or_absence; OUTPUT: safe_sustainable_work_participation)
  1. Receive absence, restriction, or adjustment request. [HUMAN, GATED]
     HUMAN_FACTORS:
       dignity: worker needs support without intrusive disclosure.
       psychological_safety: fear of stigma can delay help-seeking.
     CONSTRAINTS: separate functional work capacity from unnecessary medical detail.

  2. Assess job demands, restrictions, accommodations, and risk. [HUMAN, ASSISTED-BY: occupational_health_provider]
     HUMAN_DEMAND:
       ORIENT: understand essential duties, hazards, recovery needs, and worker preferences.
       ACT: design modified duties, schedule, equipment, or phased return.
       RECOVER: revise if symptoms, risk, or work demands change.

  3. Agree plan with worker, manager, HR, and clinical/OH input where appropriate. [HUMAN, GATED]
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: medium
       rationale: poor return-to-work design can worsen health or create unsafe work.
     SUPPORT: document duties, limits, review date, confidentiality, and escalation.

  4. Monitor fit and adjust plan. [FEEDBACK, ITERATIVE]
     CHANGE_IMPACT:
       reinforcement: successful return-to-work depends on real work design, not only individual resilience.
```

## PROCESS — Contractor And Host Employer Safety Coordination

```cairn
PROCESS ContractorHostSafetyCoordination (INPUT: contractor_work_package; OUTPUT: coordinated_safe_work)
  1. Define scope, hazards, permits, roles, and site controls before work begins. [HUMAN, GATED]
     HUMAN_FACTORS:
       boundary: host and contractor may each assume the other owns a hazard.
       social_role: temporary or contract workers may hesitate to challenge unsafe instructions.

  2. Exchange training, procedures, emergency contacts, and stop-work authority. [HUMAN, SUPPORT]
     HCI_TOUCHPOINT:
       phase: orientation
       human_goal: know site-specific hazards and who can stop or change work.

  3. Monitor work, changes, and simultaneous operations. [SERVICE, ITERATIVE]
     HUMAN_RISK:
       probability: medium
       impact: high
       confidence: medium
       rationale: contractor incidents often arise at coordination boundaries.
     SUPPORT: daily briefings, change-of-scope triggers, shared hazard log, and joint escalation.

  4. Close work package and capture learning. [FEEDBACK]
     CHANGE_IMPACT:
       reinforcement: update prequalification, permits, and coordination practices.
```

## PROCESS — Ergonomic And Human-Factors Workstation Review

```cairn
PROCESS ErgonomicHumanFactorsReview (INPUT: task_discomfort_or_design_change; OUTPUT: improved_work_design)
  1. Observe task, posture, repetition, force, reach, visual demand, and cognitive demand. [HUMAN, READONLY]
     HUMAN_FACTORS:
       cognitive_load: mental demand and physical demand interact in error and fatigue risk.
       behavioural_economics: workers may tolerate discomfort when reporting seems costly or futile.

  2. Identify ergonomic and interface contributors. [HUMAN, ASSISTED-BY: assessment_tool]
     FUNCTIONAL_LAYOUT_LOAD:
       evidence_action_distance: relevant controls, warnings, and task materials should be close to the work sequence.
       cumulative_pointer_travel: excessive UI movement can compound physical strain.

  3. Redesign equipment, layout, pacing, task rotation, or UI. [HUMAN, GATED]
     SUPPORT: prioritize design controls over reminders to "be careful."

  4. Verify comfort, safety, quality, and productivity outcomes. [FEEDBACK]
```

## PROCESS — Workplace Violence And Threat Response

```cairn
PROCESS WorkplaceViolenceThreatResponse (INPUT: threat_signal_or_incident; OUTPUT: protected_people_and_learning)
  1. Detect threat signal, harassment, aggression, or violence. [HUMAN, EMOTIONAL]
     REGULATION [STRATEGY: immediate_safety_orientation]
     HUMAN_DEMAND:
       ORIENT: identify danger, location, people at risk, and safe exit/escalation route.
       ACT: get safe, alert, de-escalate only if trained and safe, or call emergency support.
       RECOVER: access support after the event.

  2. Activate response protocol. [SERVICE, GATED]
     HUMAN_FACTORS:
       trauma_informed: response should protect affected people from blame, disbelief, or forced retelling.
       social_role: bystanders and managers need clear authority and duties.

  3. Support affected workers and preserve evidence. [HUMAN, SUPPORT]
     HUMAN_RISK:
       probability: low
       impact: high
       confidence: medium
       rationale: threat response affects immediate safety and long-term psychological harm.

  4. Review controls and prevention. [FEEDBACK, ITERATIVE]
     SUPPORT: adjust staffing, environment, reporting, training, customer policies, and escalation routes.
```
