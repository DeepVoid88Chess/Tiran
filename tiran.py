"""TIRAN v1.0
TIRAN - Designed to make coding easier.

A small, dependency-free compiler for a simple, readable source language.
TIRAN can generate complete source files for Luau, Lua, Python, JavaScript,
TypeScript, Java, and C#.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass


TARGETS = {
    "luau": ".luau",
    "lua": ".lua",
    "python": ".py",
    "javascript": ".js",
    "typescript": ".ts",
    "java": ".java",
    "csharp": ".cs",
}

ALIASES = {"js": "javascript", "ts": "typescript", "cs": "csharp"}


class TiranError(ValueError):
    """A user-friendly TIRAN compile error."""


@dataclass
class Block:
    kind: str


NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def validate_name(name: str, line: int) -> str:
    if not NAME.fullmatch(name):
        raise TiranError(f"Line {line}: invalid name '{name}'.")
    return name


def split_top_level(text: str, separator: str = ",") -> list[str]:
    result, start, depth, quote = [], 0, 0, None
    for i, char in enumerate(text):
        if quote:
            if char == quote and (i == 0 or text[i - 1] != "\\"):
                quote = None
        elif char in ""'":
            quote = char
        elif char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif char == separator and depth == 0:
            result.append(text[start:i].strip())
            start = i + 1
    tail = text[start:].strip()
    if tail:
        result.append(tail)
    return result


def expr(value: str, target: str) -> str:
    value = value.strip()
    if not value:
        raise TiranError("An expression is required.")

    replacements = [
        (r"\btrue\b", "True" if target == "python" else "true"),
        (r"\bfalse\b", "False" if target == "python" else "false"),
        (r"\bnothing\b|\bnull\b|\bnil\b",
         "None" if target == "python" else ("null" if target in {"javascript", "typescript"} else "nil")),
    ]
    for pattern, replacement in replacements:
        value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)

    if target in {"javascript", "typescript", "java", "csharp"}:
        value = re.sub(r"\band\b", "&&", value)
        value = re.sub(r"\bor\b", "||", value)
        value = re.sub(r"\bnot\b", "!", value)
    elif target in {"luau", "lua"}:
        value = value.replace(" and ", " and ").replace(" or ", " or ")
    return value


def quote(value: str) -> str:
    try:
        parsed = ast.literal_eval(value)
    except (ValueError, SyntaxError) as error:
        raise TiranError(f"Invalid string: {value}") from error
    if not isinstance(parsed, str):
        raise TiranError(f"Expected a string: {value}")
    return parsed


def parse_function_header(text: str, line: int) -> tuple[str, list[str]]:
    match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\((.*)\)", text.strip())
    if not match:
        raise TiranError(f"Line {line}: functions need name(arguments).")
    name = validate_name(match.group(1), line)
    args = []
    for item in split_top_level(match.group(2)):
        if item:
            args.append(validate_name(item, line))
    return name, args


class Compiler:
    def __init__(self, target: str):
        self.target = target
        self.lines: list[str] = []
        self.blocks: list[Block] = []
        self.function_names: set[str] = set()

    def emit(self, text: str, extra_indent: int = 0) -> None:
        self.lines.append("    " * (len(self.blocks) + extra_indent) + text)

    def close(self, expected: str, line: int) -> None:
        if not self.blocks or self.blocks[-1].kind != expected:
            actual = self.blocks[-1].kind if self.blocks else "nothing"
            raise TiranError(
                f"Line {line}: expected to close '{expected}', but '{actual}' is open."
            )
        self.blocks.pop()

    def say(self, value: str) -> None:
        value = expr(value, self.target)
        if self.target in {"luau", "lua", "python", "javascript", "typescript"}:
            self.emit(f"print({value})")
        elif self.target == "java":
            self.emit(f"System.out.println({value});")
        else:
            self.emit(f"Console.WriteLine({value});")

    def assign(self, name: str, value: str, line: int) -> None:
        validate_name(name, line)
        value = expr(value, self.target)
        if self.target in {"luau", "lua"}:
            self.emit(f"local {name} = {value}")
        elif self.target == "python":
            self.emit(f"{name} = {value}")
        elif self.target in {"javascript", "typescript"}:
            self.emit(f"let {name} = {value};")
        else:
            self.emit(f"var {name} = {value};")

    def create_part(self, name: str, line: int) -> None:
        validate_name(name, line)
        if self.target == "luau":
            self.emit(f'local {name} = Instance.new("Part")')
        elif self.target == "lua":
            self.emit(f'local {name} = Instance.new("Part")')
        else:
            raise TiranError(
                f"Line {line}: 'create part' is Roblox-specific and requires convert luau."
            )

    def set_property(self, statement: str, line: int) -> None:
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)", statement)
        if not match:
            raise TiranError(f"Line {line}: use 'set object.property = value'.")
        if self.target not in {"luau", "lua"}:
            raise TiranError(f"Line {line}: property setting currently requires convert luau.")
        obj, prop, value = match.groups()
        self.emit(f"{obj}.{prop[0].upper() + prop[1:]} = {expr(value, self.target)}")

    def finish(self) -> str:
        if self.blocks:
            raise TiranError(f"Unclosed block: {self.blocks[-1].kind}. Add 'end'.")
        return "\n".join(self.lines)

    def statement(self, line: str, number: int) -> None:
        if line.startswith("say "):
            self.say(line[4:].strip())
            return

        if line.startswith("create part "):
            self.create_part(line[12:].strip(), number)
            return

        if line.startswith("set "):
            self.set_property(line[4:].strip(), number)
            return

        if line.startswith("call "):
            call = line[5:].strip()
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*\(.*\)", call):
                raise TiranError(f"Line {number}: invalid function call.")
            if self.target in {"luau", "lua", "python", "javascript", "typescript"}:
                self.emit(call)
            else:
                self.emit(call + ";")
            return

        if line.startswith("return "):
            value = expr(line[7:], self.target)
            self.emit(f"return {value}" + (";" if self.target in {"java", "csharp"} else ""))
            return

        if line.startswith("repeat ") and line.endswith(":"):
            count = expr(line[7:-1], self.target)
            if self.target in {"luau", "lua"}:
                self.emit(f"for _ = 1, {count} do")
            elif self.target == "python":
                self.emit(f"for _ in range({count}):")
            elif self.target in {"javascript", "typescript"}:
                self.emit(f"for (let i = 0; i < {count}; i++) {{")
            else:
                self.emit(f"for (var i = 0; i < {count}; i++) {{")
            self.blocks.append(Block("repeat"))
            return

        if line.startswith("while ") and line.endswith(":"):
            condition = expr(line[6:-1], self.target)
            if self.target in {"luau", "lua"}:
                self.emit(f"while {condition} do")
            elif self.target == "python":
                self.emit(f"while {condition}:")
            else:
                self.emit(f"while ({condition}) {{")
            self.blocks.append(Block("while"))
            return

        if line.startswith("if ") and line.endswith(":"):
            condition = expr(line[3:-1], self.target)
            if self.target in {"luau", "lua"}:
                self.emit(f"if {condition} then")
            elif self.target == "python":
                self.emit(f"if {condition}:")
            else:
                self.emit(f"if ({condition}) {{")
            self.blocks.append(Block("if"))
            return

        if line == "else:":
            if not self.blocks or self.blocks[-1].kind != "if":
                raise TiranError(f"Line {number}: else must follow if.")
            if self.target in {"luau", "lua"}:
                self.lines.append("    " * (len(self.blocks) - 1) + "else")
            elif self.target == "python":
                self.lines.append("    " * (len(self.blocks) - 1) + "else:")
            else:
                self.lines.append("    " * (len(self.blocks) - 1) + "} else {")
            return

        if line == "end":
            if not self.blocks:
                raise TiranError(f"Line {number}: unexpected end.")
            block = self.blocks.pop()
            if self.target in {"luau", "lua"}:
                self.lines.append("    " * len(self.blocks) + "end")
            elif self.target in {"javascript", "typescript", "java", "csharp"}:
                self.lines.append("    " * len(self.blocks) + "}")
            return

        if line.startswith("function ") and line.endswith(":"):
            name, args = parse_function_header(line[9:-1], number)
            self.function_names.add(name)
            args_text = ", ".join(args)
            if self.target in {"luau", "lua"}:
                self.emit(f"function {name}({args_text})")
            elif self.target == "python":
                self.emit(f"def {name}({args_text}):")
            elif self.target in {"javascript", "typescript"}:
                self.emit(f"function {name}({args_text}) {{")
            elif self.target == "java":
                self.emit(f"static void {name}({', '.join('Object ' + a for a in args)}) {{")
            else:
                self.emit(f"static void {name}({', '.join('object ' + a for a in args)}) {{")
            self.blocks.append(Block("function"))
            return

        assignment = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)", line)
        if assignment:
            self.assign(assignment.group(1), assignment.group(2), number)
            return

        raise TiranError(f"Line {number}: unknown TIRAN command: {line}")


def compile_tiran(source: str, target: str) -> str:
    target = ALIASES.get(target.lower(), target.lower())
    if target not in TARGETS:
        raise TiranError(f"Unsupported target '{target}'.")
    compiler = Compiler(target)
    for number, raw in enumerate(source.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("convert "):
            requested = ALIASES.get(line[8:].strip().lower(), line[8:].strip().lower())
            if requested != target:
                raise TiranError(
                    f"Line {number}: source says convert {requested}, but compiler target is {target}."
                )
            continue
        compiler.statement(line, number)

    body = compiler.finish()
    return wrap_program(body, target)


def wrap_program(body: str, target: str) -> str:
    if target not in {"java", "csharp"}:
        return body + ("\n" if body else "")

    lines = body.splitlines()
    functions = []
    main_lines = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("static void "):
            function = [lines[i]]
            depth = lines[i].count("{") - lines[i].count("}")
            i += 1
            while i < len(lines) and depth > 0:
                function.append(lines[i])
                depth += lines[i].count("{") - lines[i].count("}")
                i += 1
            if depth != 0:
                raise TiranError("Internal error: unbalanced generated function.")
            functions.extend(function)
            functions.append("")
        else:
            main_lines.append(lines[i])
            i += 1

    if target == "java":
        parts = ["public class Main {"]
        if functions:
            parts.extend("    " + line if line else "" for line in functions)
        parts.extend([
            "    public static void main(String[] args) {",
            *("        " + line for line in main_lines),
            "    }",
            "}",
            "",
        ])
        return "\n".join(parts)

    parts = ["using System;", "", "public class Program {"]
    if functions:
        parts.extend("    " + line if line else "" for line in functions)
    parts.extend([
        "    public static void Main() {",
        *("        " + line for line in main_lines),
        "    }",
        "}",
        "",
    ])
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="tiran",
        description="Compile TIRAN source into real target-language code.",
    )
    parser.add_argument("source", help="Path to a .tiran file")
    parser.add_argument("-t", "--target", help="Target language; otherwise use convert in the source")
    parser.add_argument("-o", "--output", help="Write generated code to this file")
    args = parser.parse_args()

    try:
        with open(args.source, "r", encoding="utf-8") as file:
            source = file.read()

        target = args.target
        if not target:
            match = re.search(r"^\s*convert\s+([A-Za-z0-9_+-]+)\s*$", source, re.MULTILINE | re.IGNORECASE)
            if not match:
                raise TiranError("No target selected. Add 'convert <language>' or use --target.")
            target = match.group(1)

        result = compile_tiran(source, target)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as file:
                file.write(result)
            print(f"Compiled {args.source} -> {args.output}")
        else:
            sys.stdout.write(result)
        return 0
    except (OSError, TiranError) as error:
        print(f"TIRAN ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
