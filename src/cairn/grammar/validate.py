"""SPEC §12 well-formedness validation for parsed Cairn documents."""

from __future__ import annotations

import re

from cairn.grammar.ast import (
    Annotation,
    CairnDocument,
    ConstructLine,
    Plan,
    Process,
    Step,
)
from cairn.grammar.tags import has_llm_actor, modifier_keys, tag_dimensions

_STATE_REF = re.compile(r"^(\w+)")
_LOOP_CONSTRUCTS = frozenset({"ITERATE", "RECURSE", "QUEUE"})
_BOUND_CONSTRUCTS = frozenset({"ITERATE", "RECURSE"})


def validate_document(doc: CairnDocument) -> list[str]:
    """Return well-formedness errors (empty list = well-formed per SPEC §12)."""
    errors: list[str] = list(doc.parse_errors)

    if not (
        doc.context_blocks
        or doc.requirements_blocks
        or doc.outcomes_blocks
        or doc.processes
        or doc.plans
    ):
        errors.append("document must contain at least one CONTEXT, REQUIREMENTS/OUTCOMES, or PROCESS block")

    for proc in doc.processes:
        errors.extend(_validate_process(proc))

    for plan in doc.plans:
        errors.extend(_validate_plan(plan))

    return errors


def _validate_process(proc: Process, *, plan_context: bool = False) -> list[str]:
    errors: list[str] = []
    if not proc.name or proc.name == "unnamed":
        errors.append(f"PROCESS at line {proc.lineno} must have a name")
    if proc.signature:
        if not proc.signature.inputs.strip():
            errors.append(f"PROCESS {proc.name!r} at line {proc.lineno}: INPUT must be declared")
        if not proc.signature.outputs.strip():
            errors.append(f"PROCESS {proc.name!r} at line {proc.lineno}: OUTPUT must be declared")

    declared_states = {d.name for d in proc.state.declarations} if proc.state else set()

    loop_depth = 0
    for element in proc.elements:
        if isinstance(element, ConstructLine) and element.construct in _LOOP_CONSTRUCTS:
            loop_depth = max(loop_depth, 1)
            errors.extend(_validate_construct_line(element, declared_states, loop_depth=0))

    for step in proc.steps:
        errors.extend(_validate_step_tree(step, declared_states, loop_depth=loop_depth))

    return errors


def _validate_plan(plan: Plan) -> list[str]:
    errors: list[str] = []
    if not plan.request.strip():
        errors.append(f"PLAN {plan.plan_id!r} at line {plan.lineno}: REQUEST is required")
    if not plan.trigger.strip():
        errors.append(f"PLAN {plan.plan_id!r} at line {plan.lineno}: TRIGGER is required")
    if plan.process:
        errors.extend(_validate_process(plan.process, plan_context=True))
    else:
        errors.append(f"PLAN {plan.plan_id!r} at line {plan.lineno}: must contain a PROCESS backbone")
    return errors


def _validate_step_tree(
    step: Step,
    declared_states: set[str],
    *,
    loop_depth: int,
    parent_number: str | None = None,
) -> list[str]:
    errors: list[str] = []

    if parent_number is not None:
        errors.extend(_check_nesting(parent_number, step.step_id, step.lineno))

    errors.extend(_validate_tags(step.tags, step.lineno))
    errors.extend(_validate_annotations(step.annotations, declared_states, step.lineno))

    construct = step.construct
    if construct in {"BREAK", "CONTINUE"} and loop_depth == 0:
        errors.append(
            f"line {step.lineno}: {construct} must appear inside ITERATE, RECURSE, or QUEUE"
        )
    if construct == "AWAIT":
        errors.extend(_check_await_timeout(step, step.lineno))

    new_loop_depth = loop_depth
    if construct in _LOOP_CONSTRUCTS:
        new_loop_depth = loop_depth + 1
        if construct in _BOUND_CONSTRUCTS or has_llm_actor(step.tags):
            errors.extend(_check_iteration_bound(step, step.lineno))

    for cline in step.construct_lines:
        errors.extend(_validate_construct_line(cline, declared_states, loop_depth=new_loop_depth))

    for child in step.children:
        errors.extend(
            _validate_step_tree(
                child,
                declared_states,
                loop_depth=new_loop_depth,
                parent_number=step.step_id if step.step_id != "0" else parent_number,
            )
        )

    return errors


def _validate_construct_line(
    cline: ConstructLine,
    declared_states: set[str],
    *,
    loop_depth: int,
) -> list[str]:
    errors: list[str] = []
    if cline.construct in {"BREAK", "CONTINUE"} and loop_depth == 0:
        errors.append(
            f"line {cline.lineno}: {cline.construct} must appear inside ITERATE, RECURSE, or QUEUE"
        )
    if cline.construct == "AWAIT":
        keys = modifier_keys(cline.modifiers)
        if "TIMEOUT" not in keys:
            errors.append(f"line {cline.lineno}: AWAIT must declare TIMEOUT")
    if cline.construct in _BOUND_CONSTRUCTS:
        keys = modifier_keys(cline.modifiers)
        key_name = "MAX_DEPTH" if cline.construct == "RECURSE" else "MAX"
        if key_name not in keys and "UNTIL" not in keys:
            errors.append(f"line {cline.lineno}: {cline.construct} should declare {key_name} or UNTIL")
    if cline.construct in _LOOP_CONSTRUCTS:
        inner_depth = loop_depth + 1
    else:
        inner_depth = loop_depth
    return errors


def _validate_annotations(annotations: list[Annotation], declared_states: set[str], lineno: int) -> list[str]:
    errors: list[str] = []
    for ann in annotations:
        if ann.keyword == "STATE_UPDATE":
            ref = _STATE_REF.match(ann.text.strip())
            if ref and ref.group(1) not in declared_states:
                errors.append(
                    f"line {ann.lineno}: STATE UPDATE references undeclared state {ref.group(1)!r}"
                )
    return errors


def _validate_tags(tags: list[str], lineno: int) -> list[str]:
    errors: list[str] = []
    dims = tag_dimensions(tags)
    for dim in ("actor", "determinism", "timing", "effect", "control"):
        values = dims.get(dim, [])
        if len(values) > 1:
            errors.append(f"line {lineno}: multiple {dim} tags: {values!r}")
    for custom in dims.get("custom", []):
        if not re.match(r"^[a-z][\w-]*:\S+", custom):
            errors.append(f"line {lineno}: custom tag must be namespaced (ns:word): {custom!r}")
    return errors


def _check_nesting(parent: str, child: str, lineno: int) -> list[str]:
    if child == "0":
        return []
    parent_parts = parent.split(".")
    child_parts = child.rstrip("abcdefghijklmnopqrstuvwxyz").split(".")
    child_letter = ""
    if child and child[-1].isalpha():
        child_letter = child[-1]
        child_parts = child[:-1].split(".")

    if len(child_parts) == len(parent_parts):
        if child_parts[:-1] != parent_parts[:-1]:
            return [f"line {lineno}: step {child} is not nested under {parent}"]
        try:
            if int(child_parts[-1]) != int(parent_parts[-1]):
                return [f"line {lineno}: step {child} sibling index mismatch under {parent}"]
        except ValueError:
            pass
    elif len(child_parts) == len(parent_parts) + 1:
        if child_parts[:-1] != parent_parts:
            return [f"line {lineno}: step {child} is not a child of {parent}"]
    elif len(child_parts) < len(parent_parts):
        return []
    return []


def _check_iteration_bound(step: Step, lineno: int) -> list[str]:
    errors: list[str] = []
    keys = set()
    for bracket in step.tags:
        for part in bracket.split(";"):
            if ":" in part:
                keys.add(part.split(":", 1)[0].strip().upper())
    body_keys = set()
    for token in re.findall(r"\b(MAX|MAX_DEPTH|UNTIL)\s*:", step.text, re.I):
        body_keys.add(token.upper())
    need = "MAX_DEPTH" if step.construct == "RECURSE" else "MAX"
    if need not in keys and need not in body_keys and "UNTIL" not in keys and "UNTIL" not in body_keys:
        if has_llm_actor(step.tags) or step.construct in _BOUND_CONSTRUCTS:
            errors.append(f"line {lineno}: {step.construct} with LLM involvement must declare {need} or UNTIL")
    return errors


def _check_await_timeout(step: Step, lineno: int) -> list[str]:
    if re.search(r"\bTIMEOUT\s*:", step.text, re.I):
        return []
    for bracket in step.tags:
        if "TIMEOUT" in bracket.upper():
            return []
    return [f"line {lineno}: AWAIT must declare TIMEOUT"]