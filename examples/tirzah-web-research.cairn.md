# Tirzah in Cairn — web research override (representative slice)

A Cairn description of **Tirzah's bounded external evidence path** — how
`--web` (or runtime `web_research_enabled`) promotes non-agentic retrieval to
**agentic**, adds `web_search` / `web_fetch` to the memory-agent tool menu, and
treats fetched content as **untrusted evidence** separate from local graph memory.

This slice is a cross-cutting modifier on ask (`tirzah.cairn.md`): it does not
replace agentic retrieval; it extends the agentic loop when external facts are
needed.

---

## CONTEXT

- **web research** — optional bounded search + fetch against a configured search
  base URL (`web_search_base_url`); disabled by default.
- **memory-agent** — same planner as agentic ask; gains two extra tools when web
  is enabled.
- **web_search** — query a public search endpoint; returns snippets + URLs.
- **web_fetch** — fetch a public http/https URL *returned by web_search* when
  snippet is insufficient; private/loopback hosts blocked.
- **untrusted evidence** — web results are labelled as external in prompts and
  trace; they do not auto-ingest into the graph.

## REQUIREMENTS

```
R1. Web tools SHALL be unavailable unless web research is explicitly enabled.    [MUST]
    ACCEPTANCE: allowed_tool_specs(web_enabled=False) omits web_search/web_fetch.
R2. Enabling web on a non-agentic request SHALL promote retrieval to agentic.   [MUST]
    ACCEPTANCE: retrieval_mode_override = agentic_for_web_research in trace.
R3. web_fetch SHALL only target URLs from prior web_search results.             [MUST]
R4. Private and loopback hosts SHALL be rejected for fetch.                     [MUST]
R5. Web-sourced text SHALL be treated as untrusted in answer compilation.       [MUST]
R6. The agentic loop SHALL remain bounded when web is enabled.                [MUST]
```

## OUTCOMES

The operator can ask questions needing current external evidence while keeping
local memory authoritative and web content clearly secondary in prompts and trace.

---

## PROCESS — Formal

```
PROCESS AskWithWebResearch (INPUT: user_query, session_id, web_enabled; OUTPUT: answer, process_trace)
  STATE
    retrieval_mode  [scope: process; dir: read/write]  ref: W1
    web_enabled     [scope: process; dir: read]        ref: W2

  1. Initialize session; load runtime config.                               [CODE]
  2. MODE override [IF: web_enabled]
     STATE UPDATE: web_enabled ← true
     DECISION [ON: retrieval_mode]
       2a. direct | deep → promote retrieval_mode ← agentic                 [SATISFIES: R2]
           TRACE: retrieval_mode_override ← agentic_for_web_research
       2b. agentic → unchanged
  3. CALL RetrieveAgentically(user_query, session_id, web_enabled=true) → gathered
     CONSTRAINTS: allowed_tools include web_search, web_fetch when enabled  [SATISFIES: R1]
     CONSTRAINTS: max_iterations unchanged                                  [SATISFIES: R6]
  4. Generate answer; web context flagged as untrusted evidence.            [LLM] [SATISFIES: R5]
  5. Persist exchange + continuity (same as Ask).                             [CODE]
  OUTPUT: answer, process_trace

PROCESS ExecuteWebTool (INPUT: tool, arguments; OUTPUT: tool_result)
  CONSTRAINTS: web_enabled must be true; else return repair guidance with --web hint [SATISFIES: R1]
  1. DECISION [ON: tool]
     1a. web_search → CALL WebSearch(query, limit≤10) → snippets, urls       [EXTERNAL, SYNC]
     1b. web_fetch → validate url from prior search; block private hosts     [CODE] [SATISFIES: R3, R4]
         → CALL WebFetch(url) → content, content_type, provenance           [EXTERNAL, SYNC]
  2. Attach source metadata (url, fetched_at, untrusted=true) to result.     [CODE]
  OUTPUT: tool_result
```

## PROCESS — operator profile (rendered view)

```
render-profile: operator

ASK with external evidence
  Purpose:  Answer using local memory plus bounded web search/fetch when needed.
  Owner:    Operator
  Assisted by: memory-agent, WebResearchClient
  Preconditions: pass --web or enable runtime.web_research_enabled
  Next:     inspect process trace for research.started/completed events
```

## PROCESS — Narrative (same backbone)

```
PROCESS — AskWithWebResearch: agentic ask with an external evidence lane.
  Enable web → promote to agentic if needed → run the memory-agent loop with
  web_search/web_fetch available → compile answer treating web text as untrusted.

Web never writes the graph; endorsement of generated answers remains a separate
slice (tirzah-generated-output.cairn.md).
```

---

## Tool menu delta (agentic + web)

| Tool | When available | Notes |
|------|----------------|-------|
| `keyword_search`, `hybrid_search`, … | always (agentic) | read-only local memory |
| `web_search` | `web_enabled=true` | bounded result count |
| `web_fetch` | `web_enabled=true` | public URLs from search only |

---

## Stress-test notes

What worked: `MODE` override annotation for cross-cutting promotion; nested
`CALL RetrieveAgentically` reuse; `EXTERNAL` for search/fetch; explicit untrusted
policy in REQUIREMENTS.

Rough edges:

1. **Composition with low-intent override** — runtime may still downgrade agentic
   → direct after web promotion; order of overrides is implementation-defined.
2. **Deep mode + web** — promotion forces agentic; deep primitives are bypassed;
   document as intentional (web needs tool loop).
3. **Trace vocabulary** — `research.started/completed` events align with Galeed
   `EventType.RESEARCH_*`; link to galeed.cairn.md for cross-project correlation.