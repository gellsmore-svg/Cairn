"""Recursive-descent parser for Cairn structural grammar."""

from __future__ import annotations

import re
from typing import Any

from cairn.grammar.ast import (
    Annotation,
    CairnDocument,
    ConstraintsBlock,
    ConstructLine,
    ContextBlock,
    EmergentBlock,
    OutcomesBlock,
    Plan,
    Process,
    ProcessSignature,
    RenderProfileDirective,
    Requirement,
    RequirementsBlock,
    StateBlock,
    StateDecl,
    Step,
)
from cairn.grammar.extract import extract_cairn_source
from cairn.grammar.lexer import Line, is_render_profile, tokenize_lines
from cairn.grammar.tags import extract_bracket_tags, modifier_keys, split_tag_list

_STEP_ID = re.compile(r"^(\d+(?:\.\d+)*)([a-z])?\.\s*(.*)$", re.I)
_REQ_ID = re.compile(r"^(R\d+)\.\s*(.*)$", re.I)
_PRIORITY = re.compile(r"\[(MUST|SHOULD|MAY)\]\s*$", re.I)
_PROCESS_HDR = re.compile(
    r"^PROCESS\s+(?:(.+?)\s+\(INPUT:\s*(.+?)\s*;\s*OUTPUT:\s*(.+?)\)|(?:[—–-]\s*)?(.+?))\s*$",
    re.I,
)
_PROCESS_NARRATIVE = re.compile(r"^PROCESS\s+[—–-]\s*(.+?):\s*(.+)$", re.I)
_PLAN_HDR = re.compile(
    r"^PLAN\s+(\S+)\s+REVISION\s+(\d+)\s+\[STATUS:\s*(\w+)\]\s*$",
    re.I,
)
_SIGNATURE = re.compile(r"^\(INPUT:\s*(.+?)\s*;\s*OUTPUT:\s*(.+?)\)\s*$", re.I)
_STATE_DECL = re.compile(
    r"^(\S+)\s+\[scope:\s*(\w+)\s*;\s*dir:\s*([\w/]+)\](?:\s+ref:\s*(\S+))?(?:\s+#(.*))?$",
    re.I,
)
_ANNOTATION = re.compile(
    r"^(STATE UPDATE|OUTPUT|RISKS|PURPOSE|CONSTRAINTS|BOUNDARIES|CONTEXT):\s*(.*)$",
    re.I,
)
_EMERGENT = re.compile(r"^EMERGENT\s+(\[SATISFIES:\s*[^\]]+\])\s*$", re.I)
_CONSTRUCT_LINE = re.compile(
    r"^(MILESTONE|ITERATE|RECURSE|QUEUE|PARALLEL|SERVICE|CONCURRENT|DECISION|RETRY|ERROR|"
    r"AWAIT|CALL|MERGE|BREAK|CONTINUE|ATOMIC|STEP)\b(.*)$",
    re.I,
)
_CONSTRUCT_STEP = re.compile(
    r"^(STEP|MILESTONE|ITERATE|RECURSE|QUEUE|PARALLEL|SERVICE|DECISION|RETRY|ERROR|AWAIT|CALL)\b(.*)$",
    re.I,
)

_CONSTRUCT_NORMALIZE = {
    "DECIDE": "DECISION",
    "CONCURRENT": "PARALLEL",
}

def _is_section_header(text: str) -> bool:
    return text.upper() in {"CONTEXT", "OUTCOMES", "REQUIREMENTS"}


def _is_block_start(text: str) -> bool:
    if _is_section_header(text):
        return True
    if text.startswith("PLAN "):
        return True
    if text.startswith("PROCESS ") or text.startswith("PROCESS—") or text.startswith("PROCESS-"):
        return True
    if text.startswith("PROCESS —") or text.startswith("PROCESS –"):
        return True
    return False


class Parser:
    def __init__(self, lines: list[Line]):
        self.lines = lines
        self.pos = 0
        self.errors: list[str] = []

    def _error(self, message: str, line: Line | None = None) -> None:
        if line:
            self.errors.append(f"line {line.lineno}: {message}")
        else:
            self.errors.append(message)

    def _peek(self) -> Line | None:
        if self.pos >= len(self.lines):
            return None
        return self.lines[self.pos]

    def _advance(self) -> Line | None:
        line = self._peek()
        if line:
            self.pos += 1
        return line

    def _at_indent(self, minimum: int) -> bool:
        line = self._peek()
        return line is not None and line.indent >= minimum

    def parse_document(self, source_kind: str = "cairn") -> CairnDocument:
        doc = CairnDocument(source_kind=source_kind)
        operator_mode = False
        while self._peek():
            line = self._peek()
            assert line is not None
            profile = is_render_profile(line)
            if profile:
                self._advance()
                doc.directives.append(RenderProfileDirective(profile=profile, lineno=line.lineno))
                operator_mode = profile.lower() == "operator"
                continue
            upper = line.text.upper()
            if upper == "CONTEXT":
                operator_mode = False
                doc.context_blocks.append(self._parse_context_block())
            elif upper == "OUTCOMES":
                operator_mode = False
                doc.outcomes_blocks.append(self._parse_outcomes_block())
            elif upper == "REQUIREMENTS":
                operator_mode = False
                doc.requirements_blocks.append(self._parse_requirements_block())
            elif upper.startswith("PLAN ") and _PLAN_HDR.match(line.text):
                operator_mode = False
                doc.plans.append(self._parse_plan())
            elif upper.startswith("PLAN "):
                if operator_mode:
                    self._advance()
                else:
                    self._error(f"invalid PLAN header: {line.text!r}", line)
                    self._advance()
            elif upper.startswith("PROCESS"):
                operator_mode = False
                doc.processes.append(self._parse_process())
            elif operator_mode:
                self._advance()
            elif not _is_block_start(line.text):
                self._advance()
            else:
                self._error(f"unexpected top-level line: {line.text!r}", line)
                self._advance()
        doc.parse_errors = list(self.errors)
        return doc

    def _parse_context_block(self) -> ContextBlock:
        line = self._advance()
        assert line is not None
        block = ContextBlock(lineno=line.lineno)
        base = line.indent
        while self._peek() and self._peek().indent == base:
            cur = self._peek()
            assert cur is not None
            if _is_section_header(cur.text):
                break
            block.lines.append(self._advance().text)  # type: ignore[union-attr]
        return block

    def _parse_outcomes_block(self) -> OutcomesBlock:
        line = self._advance()
        assert line is not None
        block = OutcomesBlock(lineno=line.lineno)
        base = line.indent
        while self._peek() and self._peek().indent == base:
            cur = self._peek()
            assert cur is not None
            if _is_section_header(cur.text) or cur.text.startswith("PROCESS "):
                break
            emergent = _EMERGENT.match(cur.text)
            if emergent:
                self._advance()
                eb = EmergentBlock(satisfies=emergent.group(1), lineno=cur.lineno)
                while self._peek() and self._peek().indent > base:
                    eb.lines.append(self._advance().text)  # type: ignore[union-attr]
                block.emergent_blocks.append(eb)
            else:
                block.lines.append(self._advance().text)  # type: ignore[union-attr]
        return block

    def _parse_requirements_block(self) -> RequirementsBlock:
        line = self._advance()
        assert line is not None
        block = RequirementsBlock(lineno=line.lineno)
        base = line.indent
        while self._peek() and self._peek().indent == base:
            cur = self._peek()
            assert cur is not None
            if _is_block_start(cur.text):
                break
            cur = self._advance()
            assert cur is not None
            req_match = _REQ_ID.match(cur.text)
            if not req_match:
                self._error(f"expected requirement id R<n>. …, got {cur.text!r}", cur)
                continue
            body = req_match.group(2).strip()
            priority = None
            pri = _PRIORITY.search(body)
            if pri:
                priority = pri.group(1).upper()
                body = _PRIORITY.sub("", body).strip()
            req = Requirement(req_id=req_match.group(1).upper(), text=body, priority=priority, lineno=cur.lineno)
            req_indent = cur.indent
            while self._peek() and self._peek().indent > req_indent:
                sub = self._advance()
                assert sub is not None
                if sub.text.upper().startswith("ACCEPTANCE:"):
                    req.acceptance = sub.text.split(":", 1)[1].strip()
                else:
                    req.text = f"{req.text} {sub.text}".strip()
            block.requirements.append(req)
        return block

    def _parse_plan(self) -> Plan:
        line = self._advance()
        assert line is not None
        match = _PLAN_HDR.match(line.text)
        if not match:
            self._error(f"invalid PLAN header: {line.text!r}", line)
            return Plan(plan_id="unknown", revision=0, status="draft", lineno=line.lineno)
        plan = Plan(
            plan_id=match.group(1),
            revision=int(match.group(2)),
            status=match.group(3).lower(),
            lineno=line.lineno,
        )
        body_indent = line.indent + 2
        while self._peek() and self._peek().indent >= body_indent:
            cur = self._peek()
            assert cur is not None
            if cur.text.upper().startswith("PARENT:"):
                self._advance()
                val = cur.text.split(":", 1)[1].strip()
                plan.parent = None if val.lower() == "none" else val
            elif cur.text.upper().startswith("REQUEST:"):
                self._advance()
                plan.request = cur.text.split(":", 1)[1].strip()
            elif cur.text.upper().startswith("TRIGGER:"):
                self._advance()
                plan.trigger = cur.text.split(":", 1)[1].strip()
            elif cur.text.upper().startswith("PROCESS"):
                plan.process = self._parse_process()
            else:
                self._error(f"unexpected PLAN body line: {cur.text!r}", cur)
                self._advance()
        return plan

    def _parse_process(self) -> Process:
        line = self._advance()
        assert line is not None
        proc = Process(name="", lineno=line.lineno)

        narrative = _PROCESS_NARRATIVE.match(line.text)
        if narrative:
            proc.name = narrative.group(1).strip()
            proc.description = narrative.group(2).strip()
        else:
            match = _PROCESS_HDR.match(line.text)
            if not match:
                self._error(f"invalid PROCESS header: {line.text!r}", line)
                proc.name = line.text
            elif match.group(1):
                proc.name = match.group(1).strip()
                proc.signature = ProcessSignature(inputs=match.group(2).strip(), outputs=match.group(3).strip())
            else:
                tail = (match.group(4) or "").strip()
                if ":" in tail:
                    proc.name, proc.description = [p.strip() for p in tail.split(":", 1)]
                else:
                    proc.name = tail or "unnamed"

        body_indent = line.indent + 2
        while self._peek() and self._peek().indent >= body_indent:
            cur = self._peek()
            assert cur is not None
            if cur.indent < body_indent:
                break
            upper = cur.text.upper()
            if upper == "STATE":
                proc.state = self._parse_state_block()
            elif upper in {"CONSTRAINTS", "BOUNDARIES"}:
                proc.constraints = self._parse_constraints_block()
            elif upper == "CONTEXT":
                proc.context = self._parse_context_block()
            elif _ANNOTATION.match(cur.text):
                ann = _ANNOTATION.match(cur.text)
                assert ann is not None
                annotation = Annotation(
                    keyword=ann.group(1).upper().replace(" ", "_"),
                    text=ann.group(2).strip(),
                    lineno=cur.lineno,
                )
                self._advance()
                while self._peek() and self._peek().indent > cur.indent:
                    sub = self._advance()
                    assert sub is not None
                    if _ANNOTATION.match(sub.text) or _is_block_start(sub.text) or _STEP_ID.match(sub.text):
                        self.pos -= 1
                        break
                    annotation.text = f"{annotation.text} {sub.text}".strip()
                proc.elements.append(annotation)
            elif _STEP_ID.match(cur.text):
                proc.steps.append(self._parse_step(body_indent))
            elif _CONSTRUCT_LINE.match(cur.text):
                proc.elements.append(self._parse_construct_line())
            elif proc.signature is None or proc.description:
                self._advance()
            else:
                self._error(f"unexpected PROCESS element: {cur.text!r}", cur)
                self._advance()
        return proc

    def _parse_state_block(self) -> StateBlock:
        line = self._advance()
        assert line is not None
        block = StateBlock(lineno=line.lineno)
        decl_indent = line.indent + 2
        while self._peek() and self._peek().indent >= decl_indent:
            cur = self._advance()
            assert cur is not None
            match = _STATE_DECL.match(cur.text)
            if match:
                block.declarations.append(
                    StateDecl(
                        name=match.group(1),
                        scope=match.group(2).lower(),
                        direction=match.group(3).lower(),
                        ref=match.group(4),
                        comment=match.group(5).strip() if match.group(5) else None,
                        lineno=cur.lineno,
                    )
                )
            else:
                self._error(f"invalid STATE declaration: {cur.text!r}", cur)
        return block

    def _parse_constraints_block(self) -> ConstraintsBlock:
        line = self._advance()
        assert line is not None
        keyword = line.text.split(":", 1)[0].strip().upper()
        block = ConstraintsBlock(keyword=keyword, lineno=line.lineno)
        if ":" in line.text:
            block.inline_text = line.text.split(":", 1)[1].strip()
            return block
        inner = line.indent + 2
        while self._peek() and self._peek().indent >= inner:
            block.lines.append(self._advance().text)  # type: ignore[union-attr]
        return block

    def _parse_step(self, parent_indent: int) -> Step:
        line = self._advance()
        assert line is not None
        step_match = _STEP_ID.match(line.text)
        construct = None
        body = line.text
        step_id = ""

        if step_match:
            step_id = step_match.group(1) + (step_match.group(2) or "")
            body = step_match.group(3).strip()
        else:
            cl = _CONSTRUCT_LINE.match(line.text)
            if cl:
                step_id = "0"
                construct = _CONSTRUCT_NORMALIZE.get(cl.group(1).upper(), cl.group(1).upper())
                body = cl.group(2).strip()
            else:
                self._error(f"invalid step line: {line.text!r}", line)
                step_id = "0"
                body = line.text

        cstep = _CONSTRUCT_STEP.match(body)
        if cstep:
            construct = _CONSTRUCT_NORMALIZE.get(cstep.group(1).upper(), cstep.group(1).upper())
            body = cstep.group(2).strip()

        cleaned, tags = extract_bracket_tags(body)
        if cleaned.startswith("→"):
            cleaned = cleaned.lstrip("→").strip()

        step = Step(step_id=step_id, construct=construct, text=cleaned, tags=tags, lineno=line.lineno)
        child_indent = line.indent + 2
        while self._peek() and self._peek().indent >= child_indent:
            cur = self._peek()
            assert cur is not None
            ann = _ANNOTATION.match(cur.text)
            if ann:
                self._advance()
                step.annotations.append(
                    Annotation(keyword=ann.group(1).upper().replace(" ", "_"), text=ann.group(2).strip(), lineno=cur.lineno)
                )
                continue
            cline = _CONSTRUCT_LINE.match(cur.text)
            if cline and not _STEP_ID.match(cur.text):
                step.construct_lines.append(self._parse_construct_line())
                continue
            if _STEP_ID.match(cur.text):
                step.children.append(self._parse_step(line.indent))
                continue
            self._advance()
        return step

    def _parse_construct_line(self) -> ConstructLine:
        line = self._advance()
        assert line is not None
        match = _CONSTRUCT_LINE.match(line.text)
        if not match:
            return ConstructLine(construct="STEP", text=line.text, lineno=line.lineno)
        construct = _CONSTRUCT_NORMALIZE.get(match.group(1).upper(), match.group(1).upper())
        rest = match.group(2).strip()
        arrow_target = None
        if "→" in rest:
            before, after = rest.split("→", 1)
            rest = before.strip()
            arrow_target = after.strip()
        mods: list[str] = []
        mod_match = re.match(r"^(\[[^\]]+\])\s*(.*)$", rest)
        if mod_match:
            mods = split_tag_list(mod_match.group(1).strip("[]"))
            rest = mod_match.group(2).strip()
        cleaned, tags = extract_bracket_tags(rest)
        if tags:
            mods.extend(tags)
        return ConstructLine(
            construct=construct,
            modifiers=mods,
            arrow_target=arrow_target,
            text=cleaned,
            lineno=line.lineno,
        )


def parse_document(text: str) -> CairnDocument:
    """Parse Cairn skeleton text or markdown-wrapped ``.cairn.md`` content."""
    source, kind = extract_cairn_source(text)
    lines = tokenize_lines(source)
    parser = Parser(lines)
    return parser.parse_document(source_kind=kind)