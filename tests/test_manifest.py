from keturah import validate_manifest

from cairn.conformance import PLAN_CONSTRUCTS
from cairn.manifest import build_manifest


def test_manifest_conforms_and_lists_grammar():
    m = build_manifest()
    assert validate_manifest(m) == []
    assert m.product == "cairn"
    vp = next(c for c in m.capabilities if c.name == "validate_plan")
    # constructs are listed from the contract, not duplicated
    for construct in PLAN_CONSTRUCTS:
        assert construct in vp.description
    assert "validate_plan" in [t["name"] for t in m.to_mcp()["tools"]]
