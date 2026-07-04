"""Construct rephrasing and multilingual glossaries."""

from __future__ import annotations

import re

CONSTRUCT_PHRASES: dict[str, dict[str, str]] = {
    "en": {
        "STEP": "",
        "CALL": "Invoke",
        "ITERATE": "Repeat the following",
        "DECISION": "Decide",
        "RECURSE": "Recurse",
        "QUEUE": "Queue",
        "PARALLEL": "Run in parallel",
        "MERGE": "Merge",
        "SERVICE": "Run service",
        "RETRY": "Retry",
        "AWAIT": "Wait for",
        "BREAK": "Stop when",
        "CONTINUE": "Continue to",
        "MILESTONE": "Milestone",
    },
    "es": {
        "STEP": "",
        "CALL": "Invocar",
        "ITERATE": "Repetir lo siguiente",
        "DECISION": "Decidir",
        "RECURSE": "Recursar",
        "QUEUE": "Encolar",
        "PARALLEL": "Ejecutar en paralelo",
        "MERGE": "Combinar",
        "SERVICE": "Ejecutar servicio",
        "RETRY": "Reintentar",
        "AWAIT": "Esperar",
        "BREAK": "Detener cuando",
        "CONTINUE": "Continuar a",
        "MILESTONE": "Hito",
    },
}

SUB_BLOCK_LABELS: dict[str, dict[str, str]] = {
    "en": {
        "CONSTRAINTS": "Constraints",
        "OUTPUT": "Output",
        "PURPOSE": "Purpose",
        "RISKS": "Risks",
        "CONTEXT": "Context",
        "BOUNDARIES": "Boundaries",
    },
    "es": {
        "CONSTRAINTS": "Restricciones",
        "OUTPUT": "Salida",
        "PURPOSE": "Propósito",
        "RISKS": "Riesgos",
        "CONTEXT": "Contexto",
        "BOUNDARIES": "Límites",
    },
}

_TAG_RE = re.compile(r"\[([^\]]+)\]")


def extract_tags(text: str) -> tuple[str, list[str]]:
    tags = _TAG_RE.findall(text)
    cleaned = _TAG_RE.sub("", text).strip()
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned, tags


def phrase_construct(construct: str | None, text: str, language: str = "en") -> str:
    if not construct or construct == "STEP":
        return text
    glossary = CONSTRUCT_PHRASES.get(language, CONSTRUCT_PHRASES["en"])
    prefix = glossary.get(construct, construct)
    if construct == "ITERATE":
        return f"{prefix}: {text}"
    if construct == "DECISION":
        return f"{prefix} {text}"
    if construct == "CALL":
        return f"{prefix} {text}"
    return f"{prefix}: {text}" if prefix else text