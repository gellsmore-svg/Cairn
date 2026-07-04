# Keturah in Cairn — LLM interface manifest (representative slice)

A Cairn description of **Keturah as it currently stands**: the family's uniform
catalogue of what an LLM or orchestrator **can call** in each product — built
from seam contracts already enforced in code, projected to MCP via `to_mcp()`.

Keturah answers: *what interfaces does this product offer, and with what JSON
schemas?* It does not replace MCP; it is the source manifest MCP servers adapt.

---

## CONTEXT

- **capability** — one LLM-consumable interface: name, description, input/output
  JSON Schema, kind (`tool` | `resource` | `prompt`).
- **manifest** — product name, version, description, and the capability list.
- **MCP projection** — `Manifest.to_mcp()` → `tools/list` shape for thin adapters.
- **registry** — optional aggregate of sibling manifests (e.g. Tirzah federates
  Milcah, Mahalath, Cairn, Hoglah when installed).
- **seam contract** — the enforced shape a product already validates (Cairn plan
  schema, Milcah specialist result, Tirzah coherence call).

## REQUIREMENTS

```
R1. Each capability SHALL declare machine-readable input (and output) schema.   [MUST]
R2. Manifests SHALL be buildable from existing seam contracts, not hand drift.  [MUST]
    ACCEPTANCE: e.g. Cairn validate_plan uses PLAN_CONSTRUCTS from conformance.py.
R3. MCP projection SHALL include only kind=tool capabilities as callable tools. [MUST]
R4. Manifest schema version SHALL gate incompatible shape changes.              [MUST]
R5. Services SHOULD expose GET /api/capabilities (?format=mcp optional).        [SHOULD]
R6. Federated registry SHOULD discover sibling manifests when packages install. [SHOULD]
```

## OUTCOMES

Any family product can publish a single manifest that matches its real contracts;
orchestrators and MCP bridges consume one stable catalogue per product.

---

## PROCESS — Formal

```
PROCESS PublishManifest (INPUT: product; OUTPUT: manifest_dict)
  1. Load seam contracts the product enforces at runtime.                   [CODE]
     EXAMPLES: Cairn PLAN_CONSTRUCTS; Milcah RESULT_FIELDS; Tirzah specialist schema
  2. CALL BuildCapabilitiesFromSeams(contracts) → capabilities               [CODE] [SATISFIES: R2]
     CONSTRAINTS: descriptions + schemas derived from the same constants as validators
  3. CALL manifest(product, version, capabilities) → Manifest                 [CODE]
  4. Validate manifest shape (capabilities list, kinds, schemas).             [CODE] [SATISFIES: R1, R4]
  5. DECISION [ON: consumer format]
     5a. dict → CALL Manifest.to_dict() → manifest_dict
     5b. MCP  → CALL Manifest.to_mcp() → tools_list                          [SATISFIES: R3]
     5c. HTTP → serve at /api/capabilities                                   [SATISFIES: R5]
  OUTPUT: manifest_dict

PROCESS FederateRegistry (INPUT: host_product; OUTPUT: registry)
  1. CALL host_product.build_manifest() → primary                            [CODE]
  2. ITERATE [OVER: installed sibling packages]
     TRY CALL sibling.build_manifest() → append if present                     [CODE] [SATISFIES: R6]
     ERROR [ON: import failure; THEN: skip sibling, continue]
  3. CALL Registry(primary + siblings) → registry
  OUTPUT: registry (union of callable + resource capabilities)
```

## PROCESS — operator profile (rendered view)

```
render-profile: operator

DISCOVER interfaces
  Purpose:  See what an LLM may call in a product before wiring an agent.
  Owner:    Integrator / operator
  Assisted by: manifest builder, optional MCP adapter
  Outputs:  manifest JSON or MCP tools/list
  Next:     bind tools in planner or IDE MCP client
```

## PROCESS — Narrative (same backbone)

```
PROCESS — PublishManifest: one catalogue per product.
  Read the contracts code already enforces → declare capabilities with matching
  schemas → bundle manifest → expose as dict, MCP, or HTTP.

PROCESS — FederateRegistry: optional family-wide view.
  Host product loads its manifest plus siblings when installed (fail-soft).
```

---

## Family examples (manifest sources)

| Product | Representative capabilities | Seam source |
|---------|----------------------------|-------------|
| Cairn | `validate_plan`, `plan_schema` | `conformance.py` |
| Tirzah | `ask`, `coherence_check`, `semantic_annotate` | interaction + coherence + semantic |
| Milcah | `coherence_check` | specialist request/result |
| Galeed | (trace types as resources, not tools) | `events.py` vocabulary |

---

## Stress-test notes

What worked: meta-process describing *interface publication* rather than a user
workflow; `DECISION` on output format; federated registry as optional composition.

Rough edges:

1. **Resources vs tools** — `plan_schema` is `kind=resource`; Cairn needs a
   consistent pattern for non-callable manifest entries in operator docs.
2. **Version drift** — manifest `version` must track package release; no Cairn
   construct for "manifest built at build time vs runtime introspection."
3. **No PROCESS for MCP server itself** — adapter is thin; could be a one-step
   `CALL ServeMcp(registry)` sibling example later.