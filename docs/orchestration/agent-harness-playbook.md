# Agent Harness Playbook

Use this when Cairn is invoked through an interactive agentic harness such as
Codex CLI, Claude Code, Amazon Q, Cursor, Gemini CLI, or a similar local agent.
The agent should combine human-facing judgement with Cairn's deterministic
Python and CLI surface.

## Principle

Manual agent analysis is not prompt-only when the harness can execute code. The
agent should let Cairn libraries perform repeatable parsing, validation,
analysis, recommendation, and reporting steps, then use the LLM layer for
interpretation, prioritisation, synthesis, and careful explanation.

## Minimum Tool-Assisted Sequence

1. Read the target process, repository, UI evidence, screenshots, or Playwright
   artifacts. Record what was actually inspected.
2. Load Cairn semantic context:
   - `SPEC.md`
   - `docs/usage-modes.md`
   - `docs/orchestration/manual-agent-analysis.cairn.md`
   - `okf/concepts/index.md`
   - `docs/HCI-TOUCHPOINTS.md`
   - `docs/FUNCTIONAL-LAYOUT-LOAD.md`
3. Validate Cairn process files:

   ```bash
   cairn-validate process.cairn.md
   ```

   To generate this sequence from available artifacts, use:

   ```bash
   cairn-agent-harness-plan \
     --process process.cairn.md \
     --ui-evidence ui-sim-report.json \
     --layout layout.json \
     --repo . \
     --screenshot review-screen.png \
     --check-files \
     --fail-on-missing \
     --output-dir cairn-agent-output
   ```

   To emit a reviewable shell sequence:

   ```bash
   cairn-agent-harness-plan \
     --process process.cairn.md \
     --ui-evidence ui-sim-report.json \
     --check-files \
     --format shell \
     --output cairn-agent-plan.sh
   ```

   The shell format includes preflight checks for supplied local inputs. Remote
   repository URLs are recorded as provenance but are not treated as local files.

4. Run deterministic human-factors analysis:

   ```bash
   cairn-human-factors process.cairn.md --format json --output human-factors.json
   ```

5. If UI simulation evidence or layout JSON exists, run HCI/layout analysis:

   ```bash
   cairn-ui-evidence ui-sim-report.json --format json --output ui-evidence.json
   cairn-layout-load layout.json --format json --output layout-load.json
   ```

6. Generate OKF-traceable interface recommendations:

   ```bash
   cairn-recommend-interface-changes ui-sim-report.json \
     --output interface-recommendations.md \
     --future-svg-output future-state.svg
   ```

7. Generate a reviewable report:

   ```bash
   cairn-generate-report \
     --input process.cairn.md \
     --interface-evidence ui-sim-report.json \
     --format markdown \
     --output cairn-analysis-report.md
   ```

8. Use the agent to review the generated artifacts for:
   - missing evidence
   - unsupported certainty
   - recommendations without OKF traceability
   - human risks that are plausible but not yet evidenced
   - UI touchpoints that were skipped because no UI evidence was supplied

## Python Harness Example

```python
from pathlib import Path
import json

from cairn import (
    analyze_human_factors,
    build_agent_harness_plan,
    build_analysis_report,
    format_analysis_report,
    recommend_interface_changes,
)

plan = build_agent_harness_plan(
    process_path="process.cairn.md",
    ui_evidence_path="ui-sim-report.json",
    output_dir="cairn-agent-output",
)
process_text = Path("process.cairn.md").read_text(encoding="utf-8")
ui_evidence = json.loads(Path("ui-sim-report.json").read_text(encoding="utf-8"))

human_factors = analyze_human_factors(process_text)
recommendations = recommend_interface_changes(ui_evidence)
report = build_analysis_report(
    title="Tool-assisted Cairn analysis",
    process_text=process_text,
    interface_evidence=ui_evidence,
)

Path("human-factors.json").write_text(
    json.dumps(human_factors.to_dict(), indent=2),
    encoding="utf-8",
)
Path("interface-recommendations.json").write_text(
    json.dumps(recommendations.to_dict(), indent=2),
    encoding="utf-8",
)
Path("agent-harness-plan.json").write_text(
    json.dumps(plan.to_dict(), indent=2),
    encoding="utf-8",
)
Path("cairn-analysis-report.md").write_text(
    format_analysis_report(report),
    encoding="utf-8",
)
```

The agent may then explain the report in plain language, ask follow-up
questions, or perform additional repository/UI inspection. It should not replace
deterministic Cairn outputs with purely free-form reasoning when structured
evidence is available.

## When Evidence Is Missing

If the user supplies only a GitHub link or narrative process description, the
agent should still run whatever deterministic steps are possible, then label the
remaining analysis as inference. For UI claims, prefer to request or collect one
of the following before making firm recommendations:

- Playwright trace or simulation report
- layout JSON with element rectangles and relationships
- screenshot plus visible task sequence
- repository code for the relevant form or screen

## Boundary

The harness can orchestrate Cairn, Playwright, repository inspection, and LLM
interpretation. Cairn core should remain the portable semantic layer: process
language, OKF concepts, deterministic analyzers, traceable recommendations, and
reports.
