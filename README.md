# Cairn

Cairn is a human-readable process language for **governed agentic work in human
systems**.

It gives humans and AI systems a shared way to describe, plan, interpret, and
review complex work across technical, psychological, organisational, and
sociological dimensions. It bridges pseudocode-style clarity with modern
agentic realities: iteration, recursion, non-determinism, sync/async, queuing,
outcome review, error handling, and human context.

**The specification lives in [SPEC.md](SPEC.md) (v0.9).**

Install: `pip install cairn-lang` — the distribution is named **cairn-lang**
(the PyPI name `cairn` belongs to an unrelated project) but the import is
unchanged: `import cairn`.

Optional extras:
- `pip install 'cairn-lang[render]'` — YAML stylesheets
- `pip install 'cairn-lang[web]'` — `cairn-serve` interactive composer
- `pip install 'cairn-lang[export]'` — HTML / DOCX / PDF export (python-docx + fpdf2)

## What it looks like

A small slice, in the readable **Narrative** style:

```
PROCESS — Answer a question from local memory.
  1. Gather context with read-only tools (search, then compile the surrounding nodes).
  2. The model writes the answer using only what was gathered — no invented sources.
  3. Save the exchange so the next turn can resume.
```

The same step in the precise **Formal** style (same backbone, with tags +
traceability):

```
2. Generate the answer from gathered_context.  [LLM, STOCHASTIC, SYNC] [SATISFIES: R1]
   CONSTRAINTS: answer only from retrieved context; do not invent sources.
```

Full worked descriptions of three real systems are in [`examples/`](examples/).

### Rendering & export
Cairn can be turned into audience-friendly views:

```bash
cairn-render my-process.cairn.md --profile narrative_steps
cairn-render my-process.cairn.md -f html -o view.html
cairn-render my-process.cairn.md -f pdf -o plan.pdf   # requires [export]
```

Or programmatically:

```python
from cairn.render import render_plan, export_view

view = render_plan(text, profile="operator")
pdf = export_view(view, "pdf")
```

Interactive composer: `cairn-serve`

## What it's for

- Documenting **requirements** and technical specifications in design documents.
- **Reverse-engineering** hidden or unclear processes out of existing code, AI
  systems, or legacy implementations.
- Defining **governed agentic** processes — recursive calls, iterative
  refinement, dynamic LLM decisions, tool boundaries, serialized agent
  discussions, trace, and outcome alignment.
- Real-world use cases: recursive agentic workflows (chat interfaces, autonomous
  systems), low-resource queuing, semantic engines, multi-step reasoning.
- Describing work as it actually happens: technical mechanisms embedded in
  human contexts, including cognitive, emotional, organisational, and social
  dynamics.
- New constructs for human dimensions: REGULATION, FEEDBACK (psych), COALITION, ALIGN, VISION (org), SOCIALIZE, SYMBOLIC_INTERACTION (socio), etc.

Put simply: Cairn treats software work, thinking work, and organisational work
as processes embedded in human systems, not as purely mechanical flows.

## Philosophy

### Human-first readability
The primary goal is **maximum human readability**. Anyone — technical or not —
should read a Cairn description and quickly understand the process without
wrestling with syntax, jargon, or abstraction. We remove cognitive barriers so
attention stays on **what the process actually does**, not on decoding notation.

This matters because agentic work is rarely just computation. It often includes
judgement, uncertainty, memory, motivation, trust, conflict, change, and review.
Cairn keeps those human dimensions describable without losing the governed
runtime spine that lets AI systems validate and interpret plans.

### Least abstract, simplest language possible
- Concrete, everyday words wherever they suffice.
- Short, direct sentences; active voice.
- Structure scaffolds without getting in the way.
- Details (constraints, context, edge cases) are optional layers consulted when
  needed — the main flow stays clean and punchy.

### Consistency through core verbs
A small recommended lexicon (Initialize, Propose, Evaluate, Decide, Update,
Execute, Iterate, Queue, Merge, Handle…) gives a consistent rhythm and "process
feel" that helps readers scan, compare, and mentally simulate flows — and helps
multiple people or LLMs write consistently. Verbs are **not rigid rules**;
clarity always wins.

### Balance of structure and flexibility
- Numbered steps + indentation give sequence and hierarchy.
- `PLAN` envelopes turn a `PROCESS` into a versioned live plan that can be revised when new information arrives.
- Tags (`[LLM, SYNC, DYNAMIC]`) add precision without cluttering prose.
- One canonical backbone is projected into audience **render profiles** (precise
  `ai`, readable `operator`, and more) — serving machines and humans alike.
- CONTEXT and CONSTRAINTS supply supporting knowledge on demand.

### Human-system awareness
Cairn can describe psychological, organisational, and sociological processes
alongside technical ones because governed agentic work happens inside human
systems. These dimensions are not a separate ambition from the agentic use case;
they are part of the operating environment that a useful agentic process must be
able to notice, express, and review.

### Practical and evolving
Cairn is meant to be used "in anger" on real projects, evolving from actual needs
rather than theoretical perfection.

> The ultimate test: a reader thinks *"I get what's happening here,"* not
> *"I need to learn the notation first."*

## Status

**v0.8** (current on PyPI as `cairn-lang`) — complete export support (`html`/`docx`/`pdf`), interactive `cairn-serve`, executable grammar + conformance, multiple render profiles, and real usage examples across the family stack.

The specification is at v0.9 (PLAN envelopes etc.). A structural grammar is in
[GRAMMAR.md](GRAMMAR.md). Refined by describing real systems (Tirzah, Hoglah, Mahalath, etc.).

## Repository

- [SPEC.md](SPEC.md) — the specification (v0.9).
- [GRAMMAR.md](GRAMMAR.md) — structural EBNF for the skeleton.
- [examples/](examples/) — real systems described in Cairn (Tirzah, Hoglah, Mahalath, Mahlah, Milcah, Mizpah); see `tirzah-system.cairn.md` for end-to-end composition.
- [CHANGELOG.md](CHANGELOG.md) — how the spec has evolved.
- [okf/](okf/index.md) — an [Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
  knowledge bundle: Cairn's concepts and reference, as linked markdown.

## Feedback & contributing

Cairn evolves from real use, so **feedback is the point** — especially from
describing your own processes in it. That is exactly how v0.7 was shaped.

- **Ambiguity, gap, or rough edge?** Open a
  [feedback issue](../../issues/new/choose).
- **A new construct, tag, or change?** Open a proposal (same chooser) — say what
  real process motivated it; concrete beats theoretical.
- **Questions, ideas, show-and-tell?** Use the
  [Discussions](../../discussions) tab.
- See [CONTRIBUTING.md](CONTRIBUTING.md) for how proposals are handled.

## License

[Apache License 2.0](LICENSE).

## Conformance (`cairn` package)

Cairn is primarily a spec, but it also ships a tiny, dependency-free
**conformance surface** so a runtime can validate the plans it produces instead of
embedding a private dialect:

```python
import cairn

# Runtime PLAN dict conformance (SPEC §4.5)
errors = cairn.validate_plan(plan_dict)   # [] when conformant

# Structural grammar (GRAMMAR.md EBNF + SPEC §12 well-formedness)
doc = cairn.parse_document(cairn_text_or_markdown)
errors = cairn.validate_document(doc)   # [] when well-formed
plan = cairn.document_to_plan(doc)        # first PLAN or PROCESS → plan dict

# Simplified human-readable views
view = cairn.render_plan(cairn_text_or_markdown, profile="narrative_steps")
cairn.CANONICAL_PLAN                       # an executable known-good fixture
cairn.PLAN_CONSTRUCTS                      # the allowed step constructs (SPEC §5)
```

CLI: `cairn-validate examples/hoglah.cairn.md` · `cairn-render examples/hoglah.cairn.md`

### View composer (`cairn-serve`)

An interactive, local composer for building a transformation view of a process
and **saving the recipe as a named template**:

```bash
pip install 'cairn-lang[web]'
cairn-serve            # http://127.0.0.1:8795
```

Paste a Cairn process, pick a profile and options (language, format, depth,
sections, layout), watch the view update live, then **Save as template**. A
template is persisted as a stylesheet under `~/.cairn/templates/<name>.json`,
so it is directly reusable on the CLI:
`cairn-render --stylesheet ~/.cairn/templates/<name>.json input.cairn.md`.

Grammar parser: [docs/GRAMMAR-PARSER.md](docs/GRAMMAR-PARSER.md). Simplified views:
[docs/VIEW-GENERATOR.md](docs/VIEW-GENERATOR.md).

Tirzah's recursive planner is tested against `cairn.validate_plan` so its output
cannot drift from the grammar.

Works the same on native Linux and WSL. Requires `keturah` in the same environment
(local editable install or PyPI once published).

```bash
pip install -e ".[dev]" && pytest
```
