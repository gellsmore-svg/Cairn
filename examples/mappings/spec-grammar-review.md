# SPEC / GRAMMAR Review From Expanded Examples

The expanded example suite exercised corporate, organisational-change,
psychological, sociological, technical/agentic, HCI, and augmentation cases.

## Result

No immediate SPEC or GRAMMAR extension was required to represent the new
examples. Existing constructs and annotations were sufficient:

- `HUMAN_DEMAND`
- `HUMAN_FACTORS`
- `HUMAN_RISK`
- `AUGMENTATION_PROCESS`
- `HCI_TOUCHPOINT`
- `FUNCTIONAL_LAYOUT_LOAD`
- `CHANGE_IMPACT`
- `SUPPORT`
- existing tags such as `HUMAN`, `CODE`, `LLM`, `UI`, `GATED`, `ASYNC`,
  `ITERATIVE`, `ASSISTED-BY`

## Small Future Candidates

These are not required now, but could become useful if the human-systems corpus
continues to grow:

- `BOUNDARY`: explicit construct for work/home, role, consent, and authority
  boundaries.
- `CONTEST`: explicit construct for challenging AI output, power claims, or
  contested social meaning.
- `CAPACITY`: explicit construct for current human or team cognitive/emotional
  capacity, especially in trauma-informed and caregiver-load examples.
- `NORM`: explicit construct for group expectations, sanctions, and informal
  enforcement.

## Recommendation

Keep the core language stable for now. Use examples and OKF mappings to test
whether these candidate constructs recur often enough to justify promotion into
SPEC/GRAMMAR. The current annotation style is expressive enough and avoids
prematurely expanding the formal grammar.
