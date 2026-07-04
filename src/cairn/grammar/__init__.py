"""Cairn structural grammar parser (GRAMMAR.md EBNF + SPEC §12 well-formedness)."""

from cairn.grammar.ast import CairnDocument
from cairn.grammar.extract import extract_cairn_source
from cairn.grammar.parser import parse_document
from cairn.grammar.plan_export import document_to_plan
from cairn.grammar.validate import validate_document

__all__ = [
    "CairnDocument",
    "document_to_plan",
    "extract_cairn_source",
    "parse_document",
    "validate_document",
]