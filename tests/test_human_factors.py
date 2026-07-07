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
