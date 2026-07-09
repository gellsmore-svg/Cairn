from __future__ import annotations

from pathlib import Path
import sys
import types

from cairn import analyze_human_factors, build_human_factors_prompt, format_human_factors_report, interpret_human_factors
from cairn.human_factors_cli import main as human_factors_main
from cairn.llm_adapters import HoglahLLMProvider, LLMRequest, LLMResponse


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def test_analyze_human_factors_finds_risk_and_factors():
    md = (EXAMPLES / "accounts-payable-exception.cairn.md").read_text(encoding="utf-8")
    report = analyze_human_factors(md)
    assert report.steps
    review = next(step for step in report.steps if step.step == "3")
    families = {finding.family for finding in review.factors}
    assert "trust_automation" in families
    assert "cognitive_load" in families
    assert review.risk is not None
    assert review.risk.score == "critical"
    assert "HUMAN_FACTORS" in review.suggested_blocks


def test_format_human_factors_report_markdown_and_json():
    md = (EXAMPLES / "accounts-payable-exception.cairn.md").read_text(encoding="utf-8")
    report = analyze_human_factors(md)
    markdown = format_human_factors_report(report)
    assert "Human Factors Analysis" in markdown
    assert "automation bias" in markdown

    payload = format_human_factors_report(report, output_format="json")
    assert isinstance(payload, dict)
    assert payload["steps"]


class FakeProvider:
    name = "fake"

    def complete(self, request: LLMRequest) -> LLMResponse:
        assert request.task == "cairn.human_factors.interpret"
        assert "offline_report" in request.context
        return LLMResponse(text="## Highest-risk steps\n\nStep 3 needs review.", provider=self.name)


def test_interpret_human_factors_uses_provider():
    md = (EXAMPLES / "accounts-payable-exception.cairn.md").read_text(encoding="utf-8")
    report = analyze_human_factors(md)
    prompt = build_human_factors_prompt(md, report)
    assert "Highest-risk steps" in prompt
    assert "HCI touchpoints" in prompt
    assert "cognitive aesthetic" in prompt
    assert "visual hierarchy" in prompt
    assert "Separate observed evidence from inference" in prompt
    assert "Augmentation process findings" in prompt
    assert "challenge, revision, override" in prompt
    interpretation = interpret_human_factors(md, FakeProvider(), report=report)
    assert interpretation.provider == "fake"
    assert "Step 3" in interpretation.text
    assert interpretation.report is report


def test_human_factors_cli_command_provider(tmp_path, capsys):
    script = tmp_path / "fake_llm.py"
    script.write_text(
        "import json, sys\n"
        "payload = json.load(sys.stdin)\n"
        "print(json.dumps({'text': 'Adapter OK: ' + payload['task']}))\n",
        encoding="utf-8",
    )
    example = EXAMPLES / "accounts-payable-exception.cairn.md"
    rc = human_factors_main([str(example), "--llm-command", f"{sys.executable} {script}"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "Adapter OK: cairn.human_factors.interpret" in captured.out


def test_hoglah_provider_is_optional_and_uses_hoglah_api(monkeypatch):
    class FakeResult:
        output = "queued interpretation"
        error = None

    class FakeHoglah:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def submit(self, **kwargs):
            assert kwargs["model"] == "stub:1"
            assert kwargs["metadata"]["task"] == "task"
            return "job-1"

        def wait(self, job_id, timeout=None):
            assert job_id == "job-1"
            assert timeout == 5
            return FakeResult()

    monkeypatch.setitem(sys.modules, "hoglah", types.SimpleNamespace(Hoglah=FakeHoglah))
    provider = HoglahLLMProvider(model="stub:1", timeout=5)
    response = provider.complete(LLMRequest(task="task", prompt="hello", context={}))
    assert response.provider == "hoglah"
    assert response.text == "queued interpretation"


def test_analyzer_detects_mahlah_patterns_without_broad_missing_noise():
    md = (EXAMPLES / "mahlah.cairn.md").read_text(encoding="utf-8")
    report = analyze_human_factors(md)
    first = next(step for step in report.steps if step.step == "1" and "rolling chat" in step.text)
    first_factors = {(finding.family, finding.factor) for finding in first.factors}
    assert ("cognitive_load", "uncertainty load") not in first_factors
    assert ("emotional_agency", "recoverability and control") in first_factors

    devlog = next(step for step in report.steps if "devlog" in step.text)
    devlog_factors = {(finding.family, finding.factor) for finding in devlog.factors}
    assert ("cognitive_load", "mode switching") in devlog_factors

    feedback = next(step for step in report.steps if "feedback" in step.text.lower())
    feedback_factors = {(finding.family, finding.factor) for finding in feedback.factors}
    assert ("organisational_change", "feedback suppression") in feedback_factors


def test_analyzer_detects_augmentation_process_cues():
    md = """
PROCESS — Review AI-assisted decision.
  1. Review AI recommendation with uncertainty display and source evidence. [HUMAN, ASSISTED-BY: LLM]
     HUMAN_LOAD:
       cognitive state: reviewer may be overloaded during queue pressure
       adaptation trigger: system reduces secondary detail when workload rises
     HUMAN_FACTORS:
       shared mental model: human and AI must keep the same task state
       challenge path: reviewer can ask why, revise, or override
"""
    report = analyze_human_factors(md)

    factors = {(finding.family, finding.factor) for step in report.steps for finding in step.factors}
    assert ("augmentation_process", "cognitive-state adaptation") in factors
    assert ("augmentation_process", "role complementarity") in factors
    assert ("augmentation_process", "shared mental model") in factors
    assert ("augmentation_process", "trust calibration") in factors
