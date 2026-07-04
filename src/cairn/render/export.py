"""Export integration hooks for downstream docx/PDF tooling."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from cairn.render.model import RenderResult

Exporter = Callable[[RenderResult, dict[str, Any]], bytes]

_EXPORTERS: dict[str, Exporter] = {}


def register_exporter(format_name: str, exporter: Exporter) -> None:
    """Register a binary exporter (e.g. docx, pdf) for ``export_view``."""
    _EXPORTERS[format_name.lower()] = exporter


def registered_exporters() -> list[str]:
    return sorted(_EXPORTERS)


def export_view(result: RenderResult, format_name: str, options: dict[str, Any] | None = None) -> bytes:
    """Export a rendered view via a registered plugin exporter."""
    key = format_name.lower()
    if key not in _EXPORTERS:
        known = ", ".join(sorted(_EXPORTERS)) or "(none registered)"
        raise NotImplementedError(
            f"No exporter registered for {format_name!r}. "
            f"Register one with cairn.render.export.register_exporter, or use JSON/markdown output. "
            f"Registered: {known}"
        )
    return _EXPORTERS[key](result, options or {})