# Cairn examples

Worked Cairn descriptions of real systems, used to stress-test the spec.

| Example | System | Slice |
|---------|--------|-------|
| [`tirzah-system.cairn.md`](tirzah-system.cairn.md) | Tirzah | **Composition:** ingest → ask → observe |
| [`tirzah.cairn.md`](tirzah.cairn.md) | Tirzah | Ask — direct · agentic · deep retrieval |
| [`tirzah-recursive-planning.cairn.md`](tirzah-recursive-planning.cairn.md) | Tirzah | Live PLAN propose → execute → revise |
| [`tirzah-ingest.cairn.md`](tirzah-ingest.cairn.md) | Tirzah | Source ingestion, dead-letter, profile backfill |
| [`tirzah-semantic-review.cairn.md`](tirzah-semantic-review.cairn.md) | Tirzah | Human-gated semantic-edge review queue |
| [`tirzah-generated-output.cairn.md`](tirzah-generated-output.cairn.md) | Tirzah | Generated-output queue → endorse/reject |
| [`tirzah-web-research.cairn.md`](tirzah-web-research.cairn.md) | Tirzah | `--web` search/fetch override on agentic ask |
| [`galeed.cairn.md`](galeed.cairn.md) | Galeed | Cross-project trace spine (emit + query) |
| [`keturah.cairn.md`](keturah.cairn.md) | Keturah | LLM interface manifest + MCP projection |
| [`mizpah.cairn.md`](mizpah.cairn.md) | Mizpah | Cross-session trace browser |
| [`hoglah.cairn.md`](hoglah.cairn.md) | Hoglah | Crash-safe bridge (v2: SERVICE, DURABLE-BEFORE) |
| [`hoglah-submit.cairn.md`](hoglah-submit.cairn.md) | Hoglah | Pure submitter / worker daemon topology |
| [`mahalath.cairn.md`](mahalath.cairn.md) | Mahalath | Ingest → debate → ontology |
| [`mahlah.cairn.md`](mahlah.cairn.md) | Mahlah | Three-channel conversational UI |
| [`milcah.cairn.md`](milcah.cairn.md) | Milcah | Recursive coherence-pressure rounds |
| [`relational-substrate.cairn.md`](relational-substrate.cairn.md) | Relational Substrate | Grammar sandbox, sequence traces, sweep |

Each describes the system **as it currently stands**, exercising CONTEXT,
REQUIREMENTS/OUTCOMES, and PROCESS modes — and is expected to surface gaps that
feed back into [../SPEC.md](../SPEC.md).