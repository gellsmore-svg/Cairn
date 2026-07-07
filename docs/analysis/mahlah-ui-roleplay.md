# UI Role-Play Review: mahlah-human-load

## Role-play snapshots

- Novice user: likely completes the chat task, but may not understand why adapter choice matters.
- Experienced operator under pressure: likely treats the process panel and dev log as optional unless something fails.
- Developer or analyst: benefits from the dev log, but pays a context-switch cost moving out of the main flow.

## Likely load amplifiers

The observed context switches, popup inspection, and feedback form create useful audit surfaces while adding work outside the business question.

## Failure or recursion loops

If the process trace is empty, the user may re-open logs, retry the prompt, or question whether hidden work happened.

## Suggested Cairn annotations

Add `HUMAN_LOAD` for `context_switches` and `input_burden`, and `HUMAN_RISK` for uncertainty around empty trace states.

## Questions for the developer or process owner

- Should adapter selection be hidden for ordinary users?
- Should an empty process trace explain why no events are present?
