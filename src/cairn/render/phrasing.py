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
    "fr": {
        "STEP": "",
        "CALL": "Appeler",
        "ITERATE": "Répéter ce qui suit",
        "DECISION": "Décider",
        "RECURSE": "Récursion",
        "QUEUE": "Mettre en file",
        "PARALLEL": "Exécuter en parallèle",
        "MERGE": "Fusionner",
        "SERVICE": "Exécuter le service",
        "RETRY": "Réessayer",
        "AWAIT": "Attendre",
        "BREAK": "Arrêter quand",
        "CONTINUE": "Continuer vers",
        "MILESTONE": "Jalon",
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
    "fr": {
        "CONSTRAINTS": "Contraintes",
        "OUTPUT": "Sortie",
        "PURPOSE": "Objectif",
        "RISKS": "Risques",
        "CONTEXT": "Contexte",
        "BOUNDARIES": "Limites",
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


# QUEUE parameters live in the step's bracket annotation, e.g.
# ``[ORDER: ROUND_ROBIN; ONE_AT_A_TIME; ROUNDS: 5; UNTIL: consensus]``. These
# patterns lift them back out so the turn-based / round-robin meaning can be
# phrased, instead of the view showing a bare "Queue:".
_Q_ORDER = re.compile(r"ORDER\s*:\s*([A-Za-z_]+)", re.I)
_Q_ROUNDS = re.compile(r"(?:ROUNDS|MAX)\s*:\s*(\d+)", re.I)
_Q_UNTIL = re.compile(r"UNTIL\s*:\s*([^;\]]+)", re.I)
_Q_SERIAL = re.compile(r"ONE[ _]AT[ _]A[ _]TIME|SERIAL", re.I)

# Localised fragments for composing the QUEUE description.
_QUEUE_PHRASING: dict[str, dict[str, str]] = {
    "en": {
        "subject": "Queue the participants",
        "ROUND_ROBIN": "round-robin", "PRIORITY": "by priority",
        "FIFO": "in turn", "_default": "in turn",
        "serial": ", one at a time",
        "rounds_1": ", for up to {n} round", "rounds_n": ", for up to {n} rounds",
        "until": ", until {u}",
    },
    "fr": {
        "subject": "Mettre les participants en file",
        "ROUND_ROBIN": "à tour de rôle", "PRIORITY": "par priorité",
        "FIFO": "dans l'ordre", "_default": "dans l'ordre",
        "serial": ", un à la fois",
        "rounds_1": ", pour un maximum de {n} tour", "rounds_n": ", pour un maximum de {n} tours",
        "until": ", jusqu'à {u}",
    },
    "es": {
        "subject": "Encolar a los participantes",
        "ROUND_ROBIN": "por turnos rotativos", "PRIORITY": "por prioridad",
        "FIFO": "en orden", "_default": "en orden",
        "serial": ", uno a la vez",
        "rounds_1": ", hasta {n} ronda", "rounds_n": ", hasta {n} rondas",
        "until": ", hasta {u}",
    },
}


def parse_queue_params(tags: list[str] | None) -> dict[str, str | bool]:
    """Pull ORDER / ROUNDS / UNTIL / one-at-a-time out of a QUEUE step's tags."""
    blob = "; ".join(tags or [])
    params: dict[str, str | bool] = {}
    if (m := _Q_ORDER.search(blob)):
        params["order"] = m.group(1).upper()
    if (m := _Q_ROUNDS.search(blob)):
        params["rounds"] = m.group(1)
    if (m := _Q_UNTIL.search(blob)):
        params["until"] = m.group(1).strip()
    if _Q_SERIAL.search(blob):
        params["serial"] = True
    return params


def describe_queue(tags: list[str] | None, language: str = "en") -> str:
    """A readable, localised description of a QUEUE step from its parameters."""
    words = _QUEUE_PHRASING.get(language, _QUEUE_PHRASING["en"])
    params = parse_queue_params(tags)
    order = str(params.get("order", "")) or "_default"
    parts = [words["subject"], " ", words.get(order, words["_default"])]
    if params.get("serial"):
        parts.append(words["serial"])
    if params.get("rounds"):
        n = str(params["rounds"])
        key = "rounds_1" if n == "1" else "rounds_n"
        parts.append(words[key].format(n=n))
    if params.get("until"):
        parts.append(words["until"].format(u=params["until"]))
    return "".join(parts)


def phrase_construct(
    construct: str | None, text: str, language: str = "en", tags: list[str] | None = None
) -> str:
    if not construct or construct == "STEP":
        return text
    if construct == "QUEUE":
        desc = describe_queue(tags, language)
        return f"{desc} — {text}" if text.strip() else desc
    glossary = CONSTRUCT_PHRASES.get(language, CONSTRUCT_PHRASES["en"])
    prefix = glossary.get(construct, construct)
    if construct == "ITERATE":
        return f"{prefix}: {text}"
    if construct == "DECISION":
        return f"{prefix} {text}"
    if construct == "CALL":
        return f"{prefix} {text}"
    return f"{prefix}: {text}" if prefix else text