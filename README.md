# Cairn

Cairn is a simple, textual, human-readable meta-language for describing complex
processes clearly and consistently — especially agentic / LLM-centric ones.

It lets humans and LLMs collaborate using the **same** description of a process,
independent of any programming language or platform. It bridges pseudocode-style
clarity with modern agentic realities: iteration, recursion, non-determinism,
sync/async, queuing, and error handling.

**The specification lives in [SPEC.md](SPEC.md) (v0.6, draft).**

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
- Two styles — a Formal skeleton and a Narrative reading — render the **same**
  underlying structure, serving machines and humans alike.
- CONTEXT and CONSTRAINTS supply supporting knowledge on demand.

### Practical and evolving
Cairn is meant to be used "in anger" on real projects, evolving from actual needs
rather than theoretical perfection.

> The ultimate test: a reader thinks *"I get what's happening here,"* not
> *"I need to learn the notation first."*

## Status

Draft, **v0.6**. Evolving from real use; the first stress test is describing
Tirzah, Hoglah, and Mahalath in Cairn (see [`examples/`](examples/)).

## License

[Apache License 2.0](LICENSE).
