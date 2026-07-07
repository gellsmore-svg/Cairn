# Codex in Cairn - review-gated coding run

A Cairn description of the family coding workflow after the Keturah MCP bridge
is live: Codex performs the code-edit loop, while Cairn owns the process gate,
Milcah reviews risky changes through `tirzah.coherence_check`, and Galeed keeps
the run traceable.

This is a process contract, not a replacement coding agent. The runner can be a
thin wrapper around `codex exec --json --output-schema`.

---

## CONTEXT

- **Codex CLI** - coding execution engine: edits files, runs commands, and emits
  JSON event streams.
- **Cairn runner** - process owner: classifies risk, decides whether review is
  required, and accepts or blocks the run.
- **Keturah MCP** - exposes family tools to Codex, including Tirzah memory and
  Milcah review.
- **Milcah review** - pressure-tests the change through `tirzah.coherence_check`;
  slow but useful for higher-risk edits.
- **Galeed trace** - receives Codex hook events and records the run for later
  inspection.

## REQUIREMENTS

```
R1. Codex SHALL return a schema-constrained run summary, not only prose.       [MUST]
R2. A changed workspace SHALL expose a diff summary and verification evidence. [MUST]
R3. Milcah review SHALL run only when policy marks the change review_required. [SHOULD]
R4. A failed Codex run or failed verification SHALL block before review.       [MUST]
R5. A Milcah review with blocking objections SHALL stop acceptance unless a
    human override records a reason.                                          [MUST]
R6. Every run SHALL leave a Galeed trace id or an explicit trace-unavailable
    reason.                                                                  [MUST]
R7. The review step SHALL be bounded by timeout and budget policy.             [MUST]
```

## OUTCOMES

A coding run is either accepted, blocked with concrete objections/evidence, or
sent to a human override path. Routine low-risk edits can skip the expensive
Milcah review, while substantive changes get a recorded pressure test before
acceptance.

---

## PROCESS - Formal

```
PROCESS RunCodexWithReviewGate (INPUT: request, repo_path, policy; OUTPUT: gate_result)
  STATE
    codex_result     [scope: process; dir: read/write]  ref: C1
    change_set       [scope: process; dir: read/write]  ref: C2
    verification     [scope: process; dir: read/write]  ref: C3
    review_report    [scope: process; dir: read/write]  ref: C4
    gate_decision    [scope: process; dir: read/write]  ref: C5
    trace_ref        [scope: process; dir: read/write]  ref: C6

  1. MILESTONE FRAME - classify the request against policy.              [CODE, DETERMINISTIC]
     STATE UPDATE: gate_decision.review_required <- policy decision
     CONSTRAINTS: review_required for schema changes, security changes, release
                  changes, broad refactors, or explicit operator request. [SATISFIES: R3]

  2. MILESTONE EXECUTE - run Codex for the coding task.                  [EXTERNAL, SIDE-EFFECT]
     CALL RunCodexExec(request, repo_path, policy.output_schema) -> codex_result
     STATE UPDATE: codex_result <- structured summary
     CONSTRAINTS: use `codex exec --json --output-schema`; prompt may use
                  Keturah MCP memory but must not accept without verification.
                  [SATISFIES: R1]

  3. MILESTONE COLLECT - extract changed files, diff summary, tests, and trace.
     CALL CollectCodexEvidence(codex_result, repo_path) -> change_set, verification, trace_ref [CODE]
     STATE UPDATE: change_set <- diff and changed files
     STATE UPDATE: verification <- test commands and results
     STATE UPDATE: trace_ref <- Galeed trace id or unavailable reason       [SATISFIES: R2, R6]

  4. DECISION [ON: codex_result.status OR verification.status]
     4a. failed | blocked -> gate_decision.status <- blocked                [CODE] [SATISFIES: R4]
     4b. completed and verification passed -> continue

  5. DECISION [ON: gate_decision.review_required]
     5a. false -> gate_decision.status <- accepted_without_review           [CODE]
     5b. true -> CALL ReviewChangeWithMilcah(request, change_set, verification, policy) -> review_report
         STATE UPDATE: review_report <- specialist result                   [EXTERNAL, ASSISTED-BY: LLM]
         CONSTRAINTS: call Keturah MCP tool `tirzah.coherence_check` with
                      bounded timeout and the diff summary, not the whole repo.
                      [SATISFIES: R3, R7]

  6. DECISION [ON: review_report]
     6a. absent because review not required -> continue
     6b. terminal_reason in blocked | insufficient_evidence -> gate_decision.status <- blocked [CODE]
     6c. blocking objections present -> AWAIT [EVENT: human override; TIMEOUT: never] [HUMAN, GATED]
         STATE UPDATE: gate_decision.status <- accepted_by_override OR blocked
         CONSTRAINTS: override must record reviewer and reason.             [SATISFIES: R5]
     6d. no blocking objections -> gate_decision.status <- accepted          [CODE]

  7. MILESTONE RECORD - emit final gate result with evidence pointers.       [CODE, DETERMINISTIC]
     STATE UPDATE: gate_decision.trace_ref <- trace_ref
  OUTPUT: gate_result (status, changed_files, verification, review_report, trace_ref)

PROCESS RunCodexExec (INPUT: request, repo_path, output_schema; OUTPUT: codex_result)
  1. Build the Codex prompt from request, repo rules, and policy.             [CODE]
  2. Execute `codex exec --json --output-schema output_schema`.               [EXTERNAL, SIDE-EFFECT]
  3. Parse the final structured response and stream metadata.                 [CODE]
  4. Return failed when the CLI reports account limits, model errors, or schema drift. [CODE]
  OUTPUT: codex_result

PROCESS CollectCodexEvidence (INPUT: codex_result, repo_path; OUTPUT: change_set, verification, trace_ref)
  1. Read workspace status and changed file list.                             [CODE]
  2. Summarize the diff within the review budget.                             [CODE]
  3. Capture tests or checks reported by Codex.                               [CODE]
  4. Resolve the Galeed trace id from hook events when available.             [EXTERNAL]
  OUTPUT: change_set, verification, trace_ref

PROCESS ReviewChangeWithMilcah (INPUT: request, change_set, verification, policy; OUTPUT: review_report)
  1. Construct a bounded review context from request, diff summary, and test evidence. [CODE]
  2. CALL Keturah.Tool("tirzah.coherence_check", context) -> review_report    [EXTERNAL, ASSISTED-BY: LLM]
  3. Mark objections as blocking only when they identify a concrete correctness,
     safety, contract, or verification gap.                                  [CODE]
  OUTPUT: review_report
```

---

## Output schema sketch

The runner's first practical schema should be intentionally small:

```json
{
  "status": "completed|blocked|failed",
  "summary": "string",
  "changed_files": ["path"],
  "verification": [{"command": "string", "status": "passed|failed|not_run"}],
  "risk": "low|medium|high",
  "review_required": true,
  "diff_summary": "string"
}
```

## Stress-test notes

What worked: this keeps Codex as the executor and Cairn as the owner of
acceptance. It also makes Milcah review explicit instead of automatic, which
matters because the current live review path is useful but slow on a single
Hoglah worker.

Rough edge: the next implementation step needs a small runner that turns this
process into command execution, parses Codex event JSON, and calls the MCP review
tool outside Codex when the gate requires it.
