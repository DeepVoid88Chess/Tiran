"""Small dependency-free syntax tree for TIRAN's core language."""
from dataclasses import dataclass, field
import re

@dataclass
class Node:
    kind: str
    line: int
    text: str
    children: list["Node"] = field(default_factory=list)

@dataclass
class Program:
    target: str | None
    nodes: list[Node]

class ParseError(ValueError):
    pass

def parse_tiran(source: str) -> Program:
    target = None
    roots = []
    stack = [(None, roots)]
    for number, raw in enumerate(source.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.fullmatch(r"convert\s+([\w+-]+)", line, re.I)
        if m:
            if target is not None:
                raise ParseError(f"Line {number}: multiple convert directives.")
            target = m.group(1).lower()
            continue
        if line == "end":
            if len(stack) == 1:
                raise ParseError(f"Line {number}: unexpected end.")
            stack.pop()
            continue
        if line in {"else:", "elseif"} or line.startswith("elseif ") or line.startswith("catch"):
            if len(stack) == 1:
                raise ParseError(f"Line {number}: branch has no open block.")
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
        node = Node(kind, number, line)
        stack[-1][1].append(node)
        if kind != "statement":
            stack.append((node, node.children))
    if len(stack) != 1:
        node = stack[-1][0]
        raise ParseError(f"Line {node.line}: unclosed {node.kind} block.")
    return Program(target, roots)

def ast_dict(program: Program):
    def pack(node):
        return {"kind": node.kind, "line": node.line, "text": node.text,
                "children": [pack(child) for child in node.children]}
    return {"target": program.target, "nodes": [pack(node) for node in program.nodes]}
