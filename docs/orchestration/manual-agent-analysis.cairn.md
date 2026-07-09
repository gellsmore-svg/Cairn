# Manual Agent Analysis Orchestration Pattern

CONTEXT:
  purpose: Make manual GitHub-link analysis repeatable, evidence-grounded, and OKF-traceable.
  required_sources: SPEC.md; README.md; okf/concepts/index.md; docs/HCI-TOUCHPOINTS.md; docs/FUNCTIONAL-LAYOUT-LOAD.md.
  primary_outputs: findings, interface recommendations, report, open questions.

PROCESS — Analyze a repository, process, or interface using Cairn.

1. Load the target repository or process file. [LLM, READONLY, HUMAN]
   PURPOSE: Establish the actual scope before interpreting anything.
   CONSTRAINTS: Do not infer files that were not read. Record missing files as open questions.
   OUTPUT: source_inventory

2. Load Cairn semantic context. [LLM, READONLY]
   PURPOSE: Ground analysis in the OKF bundle and Cairn specification.
   CONTEXT: okf/concepts/human-factors.md; okf/concepts/augmentation-process.md; okf/concepts/hci-touchpoints.md; okf/concepts/functional-layout-load.md.
   TOOLING: If the harness can execute local code, import Cairn Python APIs or call Cairn CLI commands instead of relying on prompt-only reasoning for repeatable checks.
   OUTPUT: active_lenses

3. Identify the process type and human-facing surfaces. [LLM, DYNAMIC]
   PURPOSE: Decide whether this is operational workflow, agentic workflow, UI-mediated work, augmentation process, or mixed mode.
   HUMAN_DEMAND: ORIENT: understand where humans notice, decide, verify, recover, and hand off.
   OUTPUT: process_classification

4. Apply human-factors and augmentation lenses phase by phase. [LLM, STOCHASTIC]
   PURPOSE: Surface plausible cognitive, psychological, social, organisational, behavioural-economic, and augmentation forces.
   CONSTRAINTS: Separate observed evidence from inference. Use qualitative risk only with rationale.
   OUTPUT: HUMAN_FACTORS, HUMAN_RISK, AUGMENTATION_FINDINGS

5. Analyze HCI touchpoints and layout load when an interface is present. [LLM, TOOL]
   PURPOSE: Make UI-mediated human work explicit across awareness, orientation, execution, feedback, recovery, handoff, and adaptation.
   TOOLING: Use screenshots, Playwright evidence, layout JSON, visible UI descriptions, `cairn-ui-evidence`, `cairn-layout-load`, and the corresponding Python APIs where available.
   OUTPUT: HCI_TOUCHPOINTS, FUNCTIONAL_LAYOUT_LOAD

6. Generate interface recommendations with mandatory OKF traceability. [LLM, TOOL]
   PURPOSE: Convert findings into concrete changes.
   CONSTRAINTS: Every recommendation must cite exact OKF file and concept. No recommendation may appear without rationale and priority.
   TOOLING: Prefer `cairn-recommend-interface-changes` or `cairn.recommend_interface_changes` when structured UI evidence exists.
   OUTPUT: RECOMMENDATIONS

7. Produce a report. [LLM, TOOL]
   PURPOSE: Give the human a reviewable deliverable.
   TOOLING: Prefer `cairn-generate-report` or `cairn.build_analysis_report` when process text or UI evidence is available.
   OUTPUT: executive_summary, current_state_analysis, future_state_recommendations, risks, mitigations, references, open_questions.

8. Validate and self-check the output. [LLM, READONLY]
   PURPOSE: Prevent random or ungrounded analysis.
   CHECKS: All recommendations have traceability; uncertainty is marked; OKF files are cited; unresolved assumptions are listed.
   OUTPUT: final_answer

OUTPUT CONTRACT:
  required_sections: Executive summary; Evidence read; Human factors; Augmentation process; HCI/layout findings; Recommendations with OKF traceability; Report artifacts; Open questions.
  recommendation_fields: change; current state; future state; rationale; priority; effort; OKF file; OKF concept; research driver when available.
  refusal_condition: If no OKF/source evidence supports a recommendation, label it as a hypothesis or omit it.
