from __future__ import annotations

from cairn.system_discovery import discover_system, format_system_discovery_report
from cairn.system_discovery_cli import main as system_discovery_main


def test_discover_system_finds_noa_galeed_ui_and_cairn_surfaces(tmp_path):
    (tmp_path / "Noa").mkdir()
    (tmp_path / "Noa" / "versions.lock").write_text("", encoding="utf-8")
    (tmp_path / "Noa" / "compose.yaml").write_text("services: {}\n", encoding="utf-8")
    (tmp_path / "Noa" / "health").mkdir()
    (tmp_path / "Noa" / "health" / "healthcheck.sh").write_text("#!/bin/sh\n", encoding="utf-8")

    (tmp_path / "Galeed").mkdir()
    (tmp_path / "Galeed" / "pyproject.toml").write_text('[project]\nname = "galeed"\n', encoding="utf-8")

    (tmp_path / "Mahlah").mkdir()
    (tmp_path / "Mahlah" / "package.json").write_text("{}", encoding="utf-8")
    (tmp_path / "Mahlah" / "e2e").mkdir()

    (tmp_path / "Cairn").mkdir()
    (tmp_path / "Cairn" / "docs").mkdir()
    (tmp_path / "Cairn" / "docs" / "scenarios").mkdir()

    report = discover_system(tmp_path)
    kinds = {surface.kind for surface in report.surfaces}

    assert "runtime_host" in kinds
    assert "trace_log_spine" in kinds
    assert "ui_surface" in kinds
    assert "process_language" in kinds
    assert any("Galeed" in item for item in report.observation_plan)
    assert any("Playwright" in item for item in report.observation_plan)


def test_format_system_discovery_report_and_cli(tmp_path):
    (tmp_path / "Hoglah").mkdir()
    (tmp_path / "Hoglah" / "pyproject.toml").write_text('[project]\nname = "hoglah"\n', encoding="utf-8")

    report = discover_system(tmp_path)
    markdown = format_system_discovery_report(report)
    assert "System Observation Discovery" in markdown
    assert "llm_queue" in markdown

    output = tmp_path / "discovery.md"
    rc = system_discovery_main([str(tmp_path), "-o", str(output)])
    assert rc == 0
    assert "Proposed Observation Plan" in output.read_text(encoding="utf-8")
