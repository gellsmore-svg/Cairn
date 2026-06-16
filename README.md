# Cairn

Cairn is a simple, textual, human-readable meta-language for describing complex
processes clearly and consistently — especially agentic / LLM-centric ones.

It lets humans and LLMs collaborate using the **same** description of a process,
independent of any programming language or platform. It bridges pseudocode-style
clarity with modern agentic realities: iteration, recursion, non-determinism,
sync/async, queuing, and error handling.

**The specification lives in [SPEC.md](SPEC.md) (v0.8).**

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

## What it's for

- Documenting **requirements** and technical specifications in design documents.
- **Reverse-engineering** hidden or unclear processes out of existing code, AI
  systems, or legacy implementations.
- Defining **AI-centric / agentic** processes — recursive calls, iterative
  refinement, dynamic LLM decisions, term invention, serialized agent
  discussions.
- Real-world use cases: recursive agentic workflows (chat interfaces, autonomous
  systems), low-resource queuing, semantic engines, multi-step reasoning.
- Describing **technical and business** processes at any level — from low-level
  code flows to high-level organisational, psychological, or sociological
  cause-effect analysis.

## Philosophy

### Human-first readability
The primary goal is **maximum human readability**. Anyone — technical or not —
should read a Cairn description and quickly understand the process without
wrestling with syntax, jargon, or abstraction. We remove cognitive barriers so
attention stays on **what the process actually does**, not on decoding notation.

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
- Tags (`[LLM, SYNC, DYNAMIC]`) add precision without cluttering prose.
- One canonical backbone is projected into audience **render profiles** (precise
  `ai`, readable `operator`, and more) — serving machines and humans alike.
- CONTEXT and CONSTRAINTS supply supporting knowledge on demand.

### Practical and evolving
Cairn is meant to be used "in anger" on real projects, evolving from actual needs
rather than theoretical perfection.

> The ultimate test: a reader thinks *"I get what's happening here,"* not
> *"I need to learn the notation first."*

## Status

**v0.8** — adds render profiles + ownership/assistance, on top of the
stress-tested v0.7. Refined by describing real systems in Cairn (Tirzah, Hoglah,
Mahalath — see [`examples/`](examples/)) and by modelling a human-led, AI-assisted
delivery process. Evolving from real use; a structural grammar is in
[GRAMMAR.md](GRAMMAR.md).

## Repository

- [SPEC.md](SPEC.md) — the specification (v0.7).
- [GRAMMAR.md](GRAMMAR.md) — structural EBNF for the skeleton.
- [examples/](examples/) — real systems described in Cairn (Tirzah, Hoglah, Mahalath).
- [CHANGELOG.md](CHANGELOG.md) — how the spec has evolved.

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
