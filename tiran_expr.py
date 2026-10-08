"""Expression lexer and Pratt parser for TIRAN.

The parser is dependency-free and intentionally target-neutral. It gives the
compiler a real expression tree while leaving target-specific lowering to the
backend.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import re


class ExpressionError(ValueError):
    pass


@dataclass
class Expr:
    kind: str
    value: str | None = None
    children: list["Expr"] = field(default_factory=list)


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    position: int


_TOKEN = re.compile(
    r"""(?P<ws>\s+)|(?P<number>(?:\d+\.\d*|\.\d+|\d+))|"""
    r"""(?P<string>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|"""
    r"""(?P<name>[A-Za-z_]\w*)|(?P<op>==|~=|!=|<=|>=|//|&&|\|\||=>|[+\-*/%^<>=!.,()[\]{}:])"""
)


def tokenize(source: str) -> list[Token]:
    tokens: list[Token] = []
    pos = 0
    while pos < len(source):
        match = _TOKEN.match(source, pos)
        if not match:
            raise ExpressionError(f"Unexpected character at column {pos + 1}: {source[pos]!r}.")
        kind = match.lastgroup
        value = match.group()
        if kind != "ws":
            tokens.append(Token(kind, value, pos))
        pos = match.end()
    tokens.append(Token("eof", "", len(source)))
    return tokens


class Parser:
    PRECEDENCE = {
        "or": 1, "||": 1,
        "and": 2, "&&": 2,
        "==": 3, "~=": 3, "!=": 3, "<": 3, "<=": 3, ">": 3, ">=": 3,
        "+": 4, "-": 4,
        "*": 5, "/": 5, "//": 5, "%": 5,
        "^": 6,
    }

    def __init__(self, source: str):
        self.source = source
        self.tokens = tokenize(source)
        self.index = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.index]

    def advance(self) -> Token:
        token = self.current
        self.index += 1
        return token

    def accept(self, value: str) -> bool:
        if self.current.value == value:
            self.advance()
            return True
        return False

    def expect(self, value: str) -> Token:
        if self.current.value != value:
            raise ExpressionError(
                f"Expected {value!r} at column {self.current.position + 1}, "
                f"got {self.current.value or 'end of expression'!r}."
            )
        return self.advance()

    def parse(self) -> Expr:
        if self.current.kind == "eof":
            raise ExpressionError("Expression is empty.")
        result = self.expression(0)
        if self.current.kind != "eof":
            raise ExpressionError(
                f"Unexpected {self.current.value!r} at column {self.current.position + 1}."
            )
        return result

    def expression(self, minimum: int) -> Expr:
        left = self.prefix()
        while True:
            op = self.current.value.lower() if self.current.kind == "name" else self.current.value
            precedence = self.PRECEDENCE.get(op)
            if precedence is None or precedence < minimum:
                break
            self.advance()
            right = self.expression(precedence + (0 if op == "^" else 1))
            left = Expr("binary", op, [left, right])
        return left

    def prefix(self) -> Expr:
        token = self.current
        if token.value in {"-", "+", "!"} or (
            token.kind == "name" and token.value.lower() == "not"
        ):
            self.advance()
            return Expr("unary", token.value, [self.expression(7)])
        if token.value == "(":
            self.advance()
            value = self.expression(0)
            self.expect(")")
            return self.postfix(value)
        if token.kind == "number":
            self.advance()
            return self.postfix(Expr("number", token.value))
        if token.kind == "string":
            self.advance()
            return self.postfix(Expr("string", token.value))
        if token.kind == "name":
            self.advance()
            lowered = token.value.lower()
            if lowered in {"true", "false", "nil", "null", "nothing"}:
                return self.postfix(Expr("literal", lowered))
            return self.postfix(Expr("name", token.value))
        if token.value == "[":
            return self.list_literal()
        if token.value == "{":
            return self.dict_literal()
        raise ExpressionError(
            f"Expected an expression at column {token.position + 1}, got {token.value!r}."
        )

    def postfix(self, value: Expr) -> Expr:
        while True:
            if self.accept("("):
                args = []
                if self.current.value != ")":
                    while True:
                        args.append(self.expression(0))
                        if not self.accept(","):
                            break
                self.expect(")")
                value = Expr("call", None, [value, *args])
            elif self.accept("["):
                index = self.expression(0)
                self.expect("]")
                value = Expr("index", None, [value, index])
            elif self.accept("."):
                name = self.current
                if name.kind != "name":
                    raise ExpressionError(
                        f"Expected a member name at column {name.position + 1}."
                    )
                self.advance()
                value = Expr("member", name.value, [value])
            else:
                break
        return value

    def list_literal(self) -> Expr:
        self.expect("[")
        items = []
        if self.current.value != "]":
            while True:
                items.append(self.expression(0))
                if not self.accept(","):
                    break
        self.expect("]")
        return Expr("list", None, items)

    def dict_literal(self) -> Expr:
        self.expect("{")
        pairs = []
        if self.current.value != "}":
            while True:
                key = self.expression(0)
                self.expect(":")
                value = self.expression(0)
                pairs.extend((key, value))
                if not self.accept(","):
                    break
        self.expect("}")
        return Expr("dict", None, pairs)


def parse_expression(source: str) -> Expr:
    return Parser(source).parse()


def expr_dict(node: Expr):
    return {
        "kind": node.kind,
        **({"value": node.value} if node.value is not None else {}),
        "children": [expr_dict(child) for child in node.children],
    }
