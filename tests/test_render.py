from pathlib import Path

import cairn
from cairn import CANONICAL_PLAN, render_plan, registered_profiles


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def test_registered_profiles_include_required_views():
    names = registered_profiles()
    for profile in ("narrative_steps", "simple_prose", "operator", "executive"):
        assert profile in names


def test_render_plan_from_canonical_dict_narrative():
    text = render_plan(CANONICAL_PLAN, profile="narrative_steps")
    assert "Retrieve relevant context" in text
    assert "Invoke" in text or "Synthesise" in text


def test_render_plan_spanish_prose():
    text = render_plan(CANONICAL_PLAN, profile="simple_prose", language="es")
    assert "El flujo consiste en" in text


def test_render_plan_executive_includes_objective():
    text = render_plan(CANONICAL_PLAN, profile="executive")
    assert "grounded answer" in text.lower() or "Objective" in text


def test_render_plan_json_output():
    payload = render_plan(CANONICAL_PLAN, profile="narrative_steps", output_format="json")
    assert payload["profile"] == "narrative_steps"
    assert "body" in payload


def test_render_plan_mermaid():
    diagram = render_plan(CANONICAL_PLAN, output_format="mermaid")
    assert diagram.startswith("flowchart TD")
    assert "s1" in diagram


def test_render_plan_from_keturah_example_markdown():
    md = (EXAMPLES / "keturah.cairn.md").read_text(encoding="utf-8")
    text = render_plan(md, profile="narrative_steps")
    assert "Load seam contracts" in text or "BuildCapabilitiesFromSeams" in text


def test_render_plan_operator_profile_from_example():
    md = (EXAMPLES / "tirzah-plan-interpreter.cairn.md").read_text(encoding="utf-8")
    text = render_plan(md, profile="operator", options={"boxed": True})
    assert "Purpose" in text or "WALK the plan" in text or "Execute each planned step" in text


def test_render_plan_warns_on_nonconformant_plan():
    payload = render_plan({"plan_id": "x", "steps": []}, output_format="json")
    assert payload["metadata"]["warnings"]


def test_render_plan_boxed_narrative():
    text = render_plan(CANONICAL_PLAN, profile="narrative_steps", options={"boxed": True})
    assert "> ### Step" in text


def test_public_api_exports_render_plan():
    assert hasattr(cairn, "render_plan")