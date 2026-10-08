"""Dependency-free syntax and expression trees for TIRAN."""
from __future__ import annotations

from dataclasses import dataclass, field
import re

from tiran_expr import ExpressionError, expr_dict, parse_expression


@dataclass
class Node:
    kind: str
    line: int
    text: str
    children: list["Node"] = field(default_factory=list)
    expression: object | None = None


@dataclass
class Program:
    target: str | None
    nodes: list[Node]


class ParseError(ValueError):
    pass


def _parse_expr(source: str, line: int):
    try:
        return parse_expression(source)
    except ExpressionError as exc:
        raise ParseError(f"Line {line}: {exc}") from exc


def _expression_for(line: str, number: int):
    checks = (
        (r"^if\s+(.+):$", 1),
        (r"^elseif\s+(.+):$", 1),
        (r"^while\s+(.+):$", 1),
        (r"^repeat\s+(.+):$", 1),
        (r"^let\s+[A-Za-z_]\w*\s*=\s*(.+)$", 1),
        (r"^[A-Za-z_]\w*\s*=\s*(.+)$", 1),
        (r"^return(?:\s+(.+))?$", 1),
        (r"^say\s+(.+)$", 1),
        (r"^call\s+[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*\((.*)\)$", 1),
    )
    for pattern, group in checks:
        match = re.fullmatch(pattern, line)
        if match:
            value = match.group(group)
            if value:
                return _parse_expr(value, number)
    return None


def parse_tiran(source: str) -> Program:
    target = None
    roots = []
    stack = [(None, roots)]

    for number, raw in enumerate(source.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        match = re.fullmatch(r"convert\s+([\w+-]+)", line, re.I)
        if match:
            if target is not None:
                raise ParseError(f"Line {number}: multiple convert directives.")
            target = match.group(1).lower()
            continue

        if line == "end":
            if len(stack) == 1:
                raise ParseError(f"Line {number}: unexpected end.")
            stack.pop()
            continue

        if line == "else:" or line.startswith("elseif ") or line.startswith("catch"):
            if len(stack) == 1:
                raise ParseError(f"Line {number}: branch has no open block.")
            if line.startswith("elseif ") or line.startswith("else"):
                expression = _expression_for(line, number)
            else:
                expression = None
            node = Node("branch", number, line, expression=expression)
            stack[-1][1].append(node)
            continue

        kind = "statement"
        if line.startswith("if "):
            kind = "if"
        elif line.startswith("repeat "):
            kind = "repeat"
        elif line.startswith("while "):
            kind = "while"
        elif line.startswith("function "):
            kind = "function"
        elif line == "try:":
            kind = "try"

        expression = _expression_for(line, number)
        node = Node(kind, number, line, expression=expression)
        stack[-1][1].append(node)

        if kind != "statement":
            stack.append((node, node.children))

    if len(stack) != 1:
        node = stack[-1][0]
        raise ParseError(f"Line {node.line}: unclosed {node.kind} block.")

    return Program(target, roots)


def ast_dict(program: Program):
    def pack(node):
        result = {
            "kind": node.kind,
            "line": node.line,
            "text": node.text,
            "children": [pack(child) for child in node.children],
        }
        if node.expression is not None:
            result["expression"] = expr_dict(node.expression)
        return result

    return {
        "target": program.target,
        "nodes": [pack(node) for node in program.nodes],
    }
