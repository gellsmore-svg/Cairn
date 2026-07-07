from __future__ import annotations

from pathlib import Path

from cairn.live_observer import analyze_live_observations, format_live_observation_report
from cairn.live_observer_cli import _load_observations, main as live_observer_main


ROOT = Path(__file__).resolve().parents[1]


def test_analyze_live_observations_finds_human_and_agent_risks():
    raw = (ROOT / "docs" / "observations" / "noah-live-observer-sample.jsonl").read_text(encoding="utf-8")
    report = analyze_live_observations(_load_observations(raw), title="Noah sample")

    factors = {(finding.family, finding.factor) for finding in report.findings}
    assert ("system_reliability", "runtime errors") in factors
    assert ("agent_effectiveness", "unsupported or overconfident output") in factors
    assert ("human_systems", "accountability or uncertainty load") in factors
    assert report.risk is not None
    assert report.risk.score == "critical"
    assert "HUMAN_LOAD" in report.suggested_blocks
    assert "IMPROVEMENT" in report.suggested_blocks


def test_format_live_observation_report_markdown_and_json():
    raw = (ROOT / "docs" / "observations" / "noah-live-observer-sample.jsonl").read_text(encoding="utf-8")
    report = analyze_live_observations(_load_observations(raw), title="Noah sample")

    markdown = format_live_observation_report(report)
    assert "Live Observation Evidence" in markdown
    assert "unsupported or overconfident output" in markdown

    payload = format_live_observation_report(report, output_format="json")
    assert isinstance(payload, dict)
    assert payload["event_count"] == 7


def test_live_observer_cli_reads_jsonl(tmp_path):
    source = ROOT / "docs" / "observations" / "noah-live-observer-sample.jsonl"
    output = tmp_path / "live-observer.md"

    rc = live_observer_main([str(source), "--title", "Noah sample", "-o", str(output)])

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    assert "Noah sample" in text
    assert "HUMAN_RISK" in text
