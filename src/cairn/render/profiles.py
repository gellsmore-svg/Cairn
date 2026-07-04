"""Pluggable render profiles for simplified Cairn views."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from cairn.render.model import ProcessDocument, RenderResult, StepNode
from cairn.render.phrasing import SUB_BLOCK_LABELS, phrase_construct


class RenderProfile(ABC):
    name: str

    @abstractmethod
    def render(self, doc: ProcessDocument, language: str, options: dict[str, Any]) -> RenderResult:
        ...


def _indent(depth: int) -> str:
    return "  " * depth


def _render_step_line(node: StepNode, language: str, depth: int, options: dict[str, Any]) -> list[str]:
    include_tags = options.get("include_tags", False)
    text = phrase_construct(node.construct, node.text, language)
    line = f"{_indent(depth)}{node.number}. {text}"
    lines = [line]
    if include_tags and node.tags:
        lines.append(f"{_indent(depth)}   _(tags: {', '.join(node.tags)})_")
    return lines


def _walk_steps(nodes: list[StepNode], language: str, depth: int, options: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    footnotes: list[str] = []
    include_sub = options.get("include_sub_blocks", True)

    for node in nodes:
        lines.extend(_render_step_line(node, language, depth, options))
        if include_sub and node.sub_blocks:
            labels = SUB_BLOCK_LABELS.get(language, SUB_BLOCK_LABELS["en"])
            for key, value in node.sub_blocks.items():
                label = labels.get(key, key.replace("_", " ").title())
                lines.append(f"{_indent(depth + 1)}**{label}:** {value}")
                footnotes.append(f"{node.number} {label}: {value}")
        lines.extend(_walk_steps(node.children, language, depth + 1, options))

    return lines


def _boxed(title: str, body_lines: list[str]) -> list[str]:
    out = [f"> ### {title}", ">"]
    for line in body_lines:
        out.append(f"> {line}" if line else ">")
    out.append(">")
    return out


class NarrativeStepsProfile(RenderProfile):
    name = "narrative_steps"

    def render(self, doc: ProcessDocument, language: str, options: dict[str, Any]) -> RenderResult:
        lines: list[str] = []
        if doc.title:
            lines.append(f"## {doc.title}")
            lines.append("")

        step_lines = _walk_steps(doc.steps, language, 0, options)
        if options.get("boxed"):
            for node in doc.steps:
                block = _render_step_line(node, language, 0, options)
                block.extend(_walk_steps(node.children, language, 1, options))
                lines.extend(_boxed(f"Step {node.number}", block))
                lines.append("")
        else:
            lines.extend(step_lines)

        footnotes = []
        if options.get("include_footnotes") and doc.requirements:
            footnotes.extend(f"Requirement: {r}" for r in doc.requirements[:10])

        return RenderResult(
            profile=self.name,
            language=language,
            format=options.get("output_format", "markdown"),
            body="\n".join(lines).strip(),
            footnotes=footnotes,
            metadata={"warnings": doc.warnings},
        )


class SimpleProseProfile(RenderProfile):
    name = "simple_prose"

    def render(self, doc: ProcessDocument, language: str, options: dict[str, Any]) -> RenderResult:
        parts: list[str] = []
        if doc.title:
            parts.append(doc.title)
        elif doc.plan:
            parts.append(doc.plan.get("objective", "This process"))

        actions = []
        for node in doc.steps:
            actions.append(phrase_construct(node.construct, node.text, language).rstrip("."))

        if actions:
            if language == "es":
                parts.append("El flujo consiste en: " + "; luego, ".join(actions) + ".")
            else:
                parts.append("The flow proceeds by: " + "; then, ".join(actions) + ".")

        if doc.outcomes:
            label = "Resultados esperados" if language == "es" else "Expected outcomes"
            parts.append(f"{label}: {', '.join(doc.outcomes)}.")

        return RenderResult(
            profile=self.name,
            language=language,
            format=options.get("output_format", "markdown"),
            body="\n\n".join(parts),
            metadata={"warnings": doc.warnings},
        )


class OperatorProfile(RenderProfile):
    name = "operator"

    def render(self, doc: ProcessDocument, language: str, options: dict[str, Any]) -> RenderResult:
        lines: list[str] = []
        if doc.title:
            lines.append(f"# {doc.title}")
            lines.append("")

        for node in doc.steps:
            title = node.text.split(".")[0][:60] if node.text else f"Step {node.number}"
            block: list[str] = []
            purpose = node.purpose or node.text
            if language == "es":
                block.append(f"**Propósito:** {purpose}")
                if node.owner:
                    block.append(f"**Responsable:** {node.owner}")
                if node.assisted_by:
                    block.append(f"**Asistido por:** {node.assisted_by}")
                if node.outputs:
                    block.append(f"**Salidas:** {', '.join(node.outputs)}")
                if node.iterate_until:
                    block.append(f"**Repetir hasta:** {node.iterate_until}")
                if node.next_phase:
                    block.append(f"**Siguiente:** {node.next_phase}")
            else:
                block.append(f"**Purpose:** {purpose}")
                if node.owner:
                    block.append(f"**Owner:** {node.owner}")
                if node.assisted_by:
                    block.append(f"**Assisted by:** {node.assisted_by}")
                if node.outputs:
                    block.append(f"**Outputs:** {', '.join(node.outputs)}")
                if node.iterate_until:
                    block.append(f"**Iterate until:** {node.iterate_until}")
                if node.next_phase:
                    block.append(f"**Next:** {node.next_phase}")

            if options.get("boxed", True):
                lines.extend(_boxed(title, block))
            else:
                lines.extend(block)
            lines.append("")

        return RenderResult(
            profile=self.name,
            language=language,
            format=options.get("output_format", "markdown"),
            body="\n".join(lines).strip(),
            metadata={"warnings": doc.warnings},
        )


class ExecutiveProfile(RenderProfile):
    name = "executive"

    def render(self, doc: ProcessDocument, language: str, options: dict[str, Any]) -> RenderResult:
        lines: list[str] = []
        heading = "Resumen ejecutivo" if language == "es" else "Executive overview"
        lines.append(f"## {heading}")
        lines.append("")

        objective = doc.plan.get("objective") if doc.plan else doc.title
        if objective:
            label = "Objetivo" if language == "es" else "Objective"
            lines.append(f"**{label}:** {objective}")
            lines.append("")

        milestone_label = "Hitos" if language == "es" else "Milestones"
        lines.append(f"### {milestone_label}")
        for node in doc.steps:
            if node.construct == "MILESTONE" or not node.children:
                summary = node.purpose or phrase_construct(node.construct, node.text, language)
                owner = f" ({node.owner})" if node.owner else ""
                lines.append(f"- **{node.number}** {summary}{owner}")

        if doc.outcomes:
            label = "Resultados" if language == "es" else "Outcomes"
            lines.append("")
            lines.append(f"### {label}")
            for outcome in doc.outcomes:
                lines.append(f"- {outcome}")

        return RenderResult(
            profile=self.name,
            language=language,
            format=options.get("output_format", "markdown"),
            body="\n".join(lines).strip(),
            metadata={"warnings": doc.warnings},
        )


_PROFILES: dict[str, RenderProfile] = {
    "narrative_steps": NarrativeStepsProfile(),
    "simple_prose": SimpleProseProfile(),
    "operator": OperatorProfile(),
    "executive": ExecutiveProfile(),
    # SPEC v0.9 aliases
    "narrative": NarrativeStepsProfile(),
}


def get_profile(name: str) -> RenderProfile:
    if name not in _PROFILES:
        raise ValueError(f"Unknown render profile: {name!r}. Known: {sorted(_PROFILES)}")
    return _PROFILES[name]


def registered_profiles() -> list[str]:
    return sorted(_PROFILES)