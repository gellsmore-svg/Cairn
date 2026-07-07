# Tirzah in Cairn — semantic-edge review (representative slice)

A Cairn description of **Tirzah's human-gated semantic graph review** — how
candidate edges are proposed, queued, and either promoted to reviewed graph edges
or rejected. No autonomous graph writes: acceptance is always operator action.

This slice complements ingestion (`tirzah-ingest.cairn.md`) and ask
(`tirzah.cairn.md`): ingestion builds nodes; profile/embedding coverage enables
vector candidates; review turns inspected suggestions into durable graph edges.

---

## CONTEXT

- **semantic-edge candidate** — a proposed link between two nodes (`source` →
  `target`, `relation_type`, similarity metadata), status `pending`.
- **reviewed graph edge** — a promoted edge written only after operator accept.
- **candidate sources** — `label_overlap` (deterministic), vector/embedding
  similarity (requires profile coverage), profile-batch scans.
- **operator** — human reviewer in CLI or web developer mode.

## REQUIREMENTS

```
R1. Candidate generation SHALL be read-only on the graph until review.         [MUST]
    ACCEPTANCE: enqueue inserts pending rows only; no edge promotion without accept.
R2. Accept SHALL create a reviewed semantic edge with reviewer attribution.     [MUST]
R3. Reject SHALL mark the candidate rejected without creating an edge.          [MUST]
R4. Duplicate candidate pairs SHALL NOT be re-enqueued.                         [MUST]
R5. Review actions SHALL be available from CLI and web surfaces.                [SHOULD]
```

## OUTCOMES

The operator inspects a bounded queue of semantic suggestions, accepts the good
ones into the graph, and rejects the rest — with provenance on who reviewed what.

---

## PROCESS — Formal

```
PROCESS ReviewSemanticEdges (INPUT: focus_node_or_scope; OUTPUT: review_summary)
  1. MILESTONE PROPOSE — generate candidates into the pending queue.
     DECISION [ON: candidate_source]
       1a. CALL EnqueueLabelOverlapCandidates(node_id) → enqueue_report   [CODE] [SATISFIES: R1, R4]
       1b. CALL EnqueueVectorCandidates(node_id | document | batch) → enqueue_report
  2. MILESTONE INSPECT — list pending candidates for operator review.       [CODE] [SATISFIES: R5]
     CALL ListPendingCandidates(limit, status=pending) → candidates
  3. ITERATE [OVER: candidates the operator chooses to act on]
     3.1. Present source/target titles, relation, similarity context.
         PURPOSE: give the operator enough local evidence to understand the proposed semantic link.
         HUMAN_DEMAND:
           ORIENT: notice what source, target, relation, and similarity signal are being proposed.
           ACT: inspect whether the candidate meaning is plausible before choosing accept or reject.
           CLOSE: know whether the candidate is ready for a decision or needs more context.
           RECOVER: open surrounding node context or defer the candidate if the evidence is insufficient.
         HUMAN_LOAD:
           focus_actions: 4
           business_actions: 2
           trivial_actions: 2
           context_switches: 3
           ambiguity_load: medium to high when labels and vector similarity disagree.
         HUMAN_FACTORS:
           cognitive_load: semantic comparison requires working memory across source, target, and relation.
           trust_automation: similarity signals can look more authoritative than they are.
           interface_friction: missing surrounding context can force navigation before judgement.
         HUMAN_RISK:
           probability: medium
           impact: medium
           confidence: medium
           score: significant
           rationale: the operator is asked to judge meaning from compressed evidence, so weak context can reduce review quality.
         SUPPORT: show source excerpt, target excerpt, relation rationale, similarity method, and nearby graph context together.
     3.2. AWAIT [EVENT: operator accept or reject; TIMEOUT: never] operator decision. [HUMAN, GATED]
         PURPOSE: make graph promotion depend on an explicit human judgement.
         HUMAN_DEMAND:
           ORIENT: understand that no graph edge is written until this decision is made.
           ACT: choose accept, reject, defer, or inspect more context.
           CLOSE: see the candidate leave the active decision state after action.
           RECOVER: allow defer/skip without forcing a low-confidence accept or reject.
         HUMAN_LOAD:
           explicit_decisions: 1
           uncertainty_loops: 1
           input_burden: low if accept/reject is enough; medium when a note is required.
           closure_clarity: medium
         HUMAN_FACTORS:
           trust_automation: human gate can become a rubber stamp if the suggestion appears too confident.
           behavioural_economics: one-click accept can become the lowest-effort path.
           social_role: reviewer is accountable for graph quality after promotion.
         HUMAN_RISK:
           probability: medium
           impact: high
           confidence: medium
           score: significant
           rationale: a single human decision controls durable graph writes, and review quality depends on calibrated trust in the suggestion.
         TRUST: show why the candidate was proposed before presenting accept as an easy action.
         SUPPORT: provide accept, reject, defer, and inspect-more-context paths with clear consequences.
     3.3. CALL DecideCandidate(candidate_id, action, reviewer, note) → result
         PURPOSE: record the decision with enough provenance for later audit and learning.
         HUMAN_DEMAND:
           ORIENT: confirm which candidate and action are being recorded.
           ACT: provide a note when the decision is non-obvious or useful for future learning.
           CLOSE: see accepted/rejected status and reviewer attribution on the candidate.
           ADAPT: repeated notes can improve future candidate generation and reviewer calibration.
         HUMAN_LOAD:
           input_burden: medium if notes are blank free text.
           closure_clarity: high when status and attribution are visible immediately.
         HUMAN_FACTORS:
           interface_friction: blank notes can discourage useful feedback.
           organisational_change: review notes turn operator judgement into training material for future graph quality.
         HUMAN_RISK:
           probability: low
           impact: medium
           confidence: medium
           score: moderate
           rationale: the main decision already happened, but poor feedback capture reduces future learning.
         IMPROVEMENT: offer editable note templates such as "good semantic relation", "too weak", "wrong relation", or "needs more context".
  OUTPUT: review_summary (accepted_count, rejected_count)

PROCESS EnqueueLabelOverlapCandidates (INPUT: node_id; OUTPUT: enqueue_report)
  1. Find peer nodes sharing labels with the source node.                   [CODE, READ-ONLY]
  2. For each pair not already pending/reviewed, insert pending candidate.  [CODE, SIDE-EFFECT]
     CONSTRAINTS: status=pending only; no graph edge write                  [SATISFIES: R1, R4]
  OUTPUT: enqueue_report

PROCESS DecideCandidate (INPUT: candidate_id, action; OUTPUT: candidate_state)
  1. Load pending candidate; reject if not pending.                         [CODE]
  2. DECISION [ON: action]
     2a. reject → mark candidate rejected                                  [CODE] [SATISFIES: R3]
     2b. accept → CALL PromoteToReviewedEdge(candidate, reviewer, note)    [CODE, GATED, HUMAN] [SATISFIES: R2]
         PURPOSE: turn an inspected candidate into a durable reviewed edge.
         HUMAN_FACTORS:
           social_role: reviewer attribution makes the human accountable for promoted meaning.
           trust_automation: accepted edges may later influence retrieval, so over-trusting weak candidates has downstream effects.
         HUMAN_RISK:
           probability: medium
           impact: high
           confidence: medium
           score: significant
           rationale: promotion changes the graph and can affect later retrieval or reasoning paths.
         SUPPORT: preserve source evidence and review note with the promoted edge.
  OUTPUT: candidate_state

PROCESS PromoteToReviewedEdge (INPUT: candidate, reviewer; OUTPUT: edge_id)
  1. Create reviewed semantic graph edge (source, target, relation, weight). [CODE, SIDE-EFFECT]
  2. Mark candidate accepted with reviewer + timestamp.                     [CODE]
  OUTPUT: edge_id
```

## PROCESS — operator profile (rendered view)

```
render-profile: operator

PROPOSE candidates
  Purpose:  Surface plausible semantic links without auto-writing the graph.
  Owner:    Operator
  Assisted by: label/vector similarity scans
  Next:     inspect the pending queue

REVIEW each suggestion
  Purpose:  Accept good edges; reject noise.
  Owner:    Operator
  Iterate-until: queue drained or operator stops
  Outputs:  reviewed graph edges + rejected candidates
```

## PROCESS — Narrative (same backbone)

```
PROCESS — ReviewSemanticEdges: grow the graph deliberately.
  Enqueue candidates (label overlap or vector similarity) → list pending → for each
  one the operator cares about, accept (promote to edge) or reject.

No step writes a graph edge without explicit human accept.
```

---

## Stress-test notes

What worked: `MILESTONE` PROPOSE/INSPECT/REVIEW phases; `AWAIT` for human gate;
`DECISION` accept/reject; clear read-only enqueue vs write-on-accept split.

Rough edges:

1. **Batch vector enqueue** — web/CLI batch endpoints are a fan-out enqueue; model
   as `[BATCH]` step per SPEC §5 STEP.
2. **Relation to ask** — accepted edges influence later retrieval paths; emergent
   link to `RetrieveAgentically` not drawn here (cross-PROCESS SATISFIES).
3. **Endorsement of generated outputs** — sibling PROCESS in
   `tirzah-generated-output.cairn.md`.
