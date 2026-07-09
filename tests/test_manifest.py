from importlib.metadata import PackageNotFoundError

import cairn.manifest as manifest_module
from cairn.conformance import PLAN_CONSTRUCTS
from cairn.manifest import build_manifest


def test_manifest_conforms_and_lists_grammar():
    m = build_manifest()
    assert m.product == "cairn"
    vp = next(c for c in m.capabilities if c.name == "validate_plan")
    # constructs are listed from the contract, not duplicated
    for construct in PLAN_CONSTRUCTS:
        assert construct in vp.description
    tool_names = [t["name"] for t in m.to_mcp()["tools"]]
    assert "validate_plan" in tool_names
    assert "parse_document" in tool_names
    assert "validate_document" in tool_names
    assert "analyze_human_factors" in tool_names
    assert "analyze_ui_simulation_report" in tool_names
    assert "analyze_functional_layout" in tool_names


def test_manifest_version_prefers_distribution_name(monkeypatch):
    calls = []

    def fake_version(distribution: str) -> str:
        calls.append(distribution)
        if distribution == "cairn-lang":
            return "9.9.9"
        raise PackageNotFoundError

    monkeypatch.setattr(manifest_module, "_pkg_version", fake_version)

    assert manifest_module._version() == "9.9.9"
    assert calls == ["cairn-lang"]
