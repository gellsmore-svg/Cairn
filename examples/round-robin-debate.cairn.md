# Round-robin multi-LLM debate in Cairn — turn-based discussion

A Cairn description of **several different LLMs debating a claim in turns**,
each turn seeing the discussion so far, bounded by a round cap and stopping
early on consensus. This is the canonical use of the **`QUEUE`** construct with
`ORDER: ROUND_ROBIN` and `ONE_AT_A_TIME`, executed by Tirzah's interpretive
planner (`execute_queue_step`).

The point of `QUEUE` over `PARALLEL`: turns are **serial** and state is
**shared**, so each agent reads the accumulating transcript — a discussion, not
parallel monologues.

---

## CONTEXT

Three agents (each a distinct model) pressure-test a claim. Turns alternate;
the shared `debate` state carries the running transcript; the loop is bounded
by `ROUNDS` and ends early when the agents converge.

## OUTCOMES

A `verdict`: the agreed (or best-supported) position, a confidence, and the
recorded dissent — plus the full turn-by-turn transcript as an audit trail.

## PROCESS — Formal

```
PROCESS RoundRobinDebate (INPUT: claim; OUTPUT: verdict)
  STATE
    transcript  [scope: process; dir: read/write]  ref: T1

  1. STEP — Frame the claim and the debate rules.        [CODE, DETERMINISTIC]
  2. QUEUE [ORDER: ROUND_ROBIN; ONE_AT_A_TIME; ROUNDS: 5; UNTIL: consensus; MAX: 10]
     2a. CALL Proposer(claim, transcript) → argument     [LLM, STOCHASTIC]
         STATE UPDATE: transcript ← argument
     2b. CALL Challenger(claim, transcript) → rebuttal   [LLM, STOCHASTIC]
         STATE UPDATE: transcript ← rebuttal
     2c. CALL Synthesist(transcript) → assessment        [LLM, STOCHASTIC]
         STATE UPDATE: transcript ← assessment
         CONSTRAINTS: signal converged when positions stop moving
  3. CALL Summarise(transcript) → verdict                [LLM, STOCHASTIC]
     OUTPUT: verdict (position, confidence, dissent)
```

---

## Narrative (same backbone)

> Frame the claim, then **queue the three agents to take turns, round-robin,
> for up to five rounds** — the proposer argues, the challenger rebuts, the
> synthesist assesses, each reading the transcript so far — **stopping early
> once they reach consensus**. Then summarise the debate into a verdict.

## How it runs

- Each `2a/2b/2c` is one CALL — a turn by one model. `ONE_AT_A_TIME` runs them
  serially so `debate.transcript` accumulates and every later turn sees it.
- `ROUND_ROBIN; ROUNDS: 5` cycles all three participants for up to five rounds.
- `UNTIL: consensus` lets the discussion end early: when a turn signals
  `converged` (or its output says "consensus reached"), the queue stops before
  the cap. Absent a signal, it runs the full five rounds — never unbounded.
- The interpreter records every turn in the queue artifact (an auditable
  transcript), and each turn's model call is captured in the family LLM
  debugging view.

`PARALLEL … MERGE` would instead run the three agents **at once** on isolated
state and reconcile — use that for independent fan-out, `QUEUE` for a
turn-taking discussion.
