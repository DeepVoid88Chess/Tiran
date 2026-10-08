"""TIRAN compiler: parse source into an AST, then lower that AST to a target."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from tiran_expr import Expr
from tiran_syntax import Node, ParseError, ast_dict, parse_tiran

TARGETS = {
    "luau": ".luau",
    "lua": ".lua",
    "python": ".py",
    "javascript": ".js",
    "typescript": ".ts",
    "java": ".java",
    "csharp": ".cs",
    "html": ".html",
}
ALIASES = {"js": "javascript", "ts": "typescript", "cs": "csharp"}

ROBLOX_CLASSES = {
    "part": "Part",
    "folder": "Folder",
    "model": "Model",
    "remoteevent": "RemoteEvent",
    "remote_function": "RemoteFunction",
    "bindableevent": "BindableEvent",
    "screen_gui": "ScreenGui",
    "screengui": "ScreenGui",
    "frame": "Frame",
    "textlabel": "TextLabel",
    "textbutton": "TextButton",
    "imagelabel": "ImageLabel",
    "imagebutton": "ImageButton",
    "uistroke": "UIStroke",
    "uilistlayout": "UIListLayout",
    "uipadding": "UIPadding",
    "stringvalue": "StringValue",
    "intvalue": "IntValue",
    "numbervalue": "NumberValue",
    "boolvalue": "BoolValue",
    "objectvalue": "ObjectValue",
    "configuration": "Configuration",
}


class TiranError(ValueError):
    pass


def target_name(value: str) -> str:
    value = ALIASES.get(value.strip().lower(), value.strip().lower())
    if value not in TARGETS:
        raise TiranError(f"Unsupported target '{value}'.")
    return value


def valid_name(name: str, line: int) -> str:
    if not re.fullmatch(r"[A-Za-z_]\w*", name):
        raise TiranError(f"Line {line}: invalid name '{name}'.")
    return name


def roblox_prop(path: str) -> str:
    parts = path.split(".")
    return ".".join(parts[:-1] + [parts[-1][0].upper() + parts[-1][1:]])


def _literal(node: Expr, target: str) -> str:
    value = (node.value or "").lower()
    if value == "true":
        return "True" if target == "python" else "true"
    if value == "false":
        return "False" if target == "python" else "false"
    if value in {"nil", "null", "nothing"}:
        return "None" if target == "python" else "nil" if target in {"luau", "lua"} else "null"
    raise TiranError(f"Unknown literal '{node.value}'.")


def lower_expr(node: Expr, target: str) -> str:
    """Lower the target-neutral expression AST instead of rewriting raw text."""
    kind = node.kind

    if kind == "number" or kind == "string":
        return node.value or ""
    if kind == "name":
        return node.value or ""
    if kind == "literal":
        return _literal(node, target)

    if kind == "unary":
        value = lower_expr(node.children[0], target)
        op = node.value or ""
        if op == "not":
            op = "not " if target in {"luau", "lua", "python"} else "!"
        return f"({op}{value})"

    if kind == "binary":
        left = lower_expr(node.children[0], target)
        right = lower_expr(node.children[1], target)
        op = node.value or ""
        if op == "and":
            op = "and" if target in {"luau", "lua", "python"} else "&&"
        elif op == "or":
            op = "or" if target in {"luau", "lua", "python"} else "||"
        elif op == "~=":
            op = "!="
        elif op == "^" and target in {"python", "javascript", "typescript"}:
            op = "**"
        elif op == "^" and target in {"java", "csharp"}:
            return f"Math.pow({left}, {right})"
        elif op == "//" and target in {"javascript", "typescript", "java", "csharp"}:
            op = "/"
        return f"({left} {op} {right})"

    if kind == "call":
        callee = lower_expr(node.children[0], target)
        args = ", ".join(lower_expr(child, target) for child in node.children[1:])
        return f"{callee}({args})"

    if kind == "member":
        return f"{lower_expr(node.children[0], target)}.{node.value}"

    if kind == "index":
        return f"{lower_expr(node.children[0], target)}[{lower_expr(node.children[1], target)}]"

    if kind == "list":
        items = ", ".join(lower_expr(child, target) for child in node.children)
        if target in {"luau", "lua"}:
            return "{" + items + "}"
        if target == "python" or target in {"javascript", "typescript"}:
            return "[" + items + "]"
        if target == "java":
            return "new Object[]{" + items + "}"
        return "new object[]{" + items + "}"

    if kind == "dict":
        pairs = list(zip(node.children[::2], node.children[1::2]))
        if target == "python":
            return "{" + ", ".join(
                f"{lower_expr(k, target)}: {lower_expr(v, target)}" for k, v in pairs
            ) + "}"
        if target in {"luau", "lua"}:
            return "{" + ", ".join(
                f"[{lower_expr(k, target)}] = {lower_expr(v, target)}" for k, v in pairs
            ) + "}"
        if target in {"javascript", "typescript"}:
            return "{" + ", ".join(
                f"[{lower_expr(k, target)}]: {lower_expr(v, target)}" for k, v in pairs
            ) + "}"
        if target == "java":
            args = ", ".join(
                f"{lower_expr(k, target)}, {lower_expr(v, target)}" for k, v in pairs
            )
            return f"java.util.Map.of({args})"
        entries = ", ".join(
            f"{{ {lower_expr(k, target)}, {lower_expr(v, target)} }}" for k, v in pairs
        )
        return f"new System.Collections.Generic.Dictionary<object, object> {{ {entries} }}"

    raise TiranError(f"Unsupported expression node '{kind}'.")


def _parse_expression_text(source: str, line: int) -> Expr:
    # Core expressions have already been parsed by tiran_syntax.
    from tiran_expr import ExpressionError, parse_expression

    try:
        return parse_expression(source)
    except ExpressionError as exc:
        raise TiranError(f"Line {line}: {exc}") from exc


class Compiler:
    def __init__(self, target: str):
        self.target = target_name(target)
        self.lines: list[str] = []
        self.blocks: list[str] = []
        self.declared: set[str] = set()
        self.imports: list[str] = []

    def emit(self, text: str, depth: int | None = None) -> None:
        d = len(self.blocks) if depth is None else depth
        self.lines.append("    " * d + text)

    def require_luau(self, n: int, feature: str) -> None:
        if self.target != "luau":
            raise TiranError(f"Line {n}: {feature} requires convert luau.")

    def expression(self, node: Node, fallback: str | None = None) -> str:
        if isinstance(node.expression, Expr):
            return lower_expr(node.expression, self.target)
        if fallback is None:
            raise TiranError(f"Line {node.line}: expression is required.")
        return lower_expr(_parse_expression_text(fallback, node.line), self.target)

    def assign(self, node: Node, name: str, value: str) -> None:
        line = node.line
        if self.target == "html":
            raise TiranError(f"Line {line}: variables are not supported by the HTML target.")
        valid_name(name, line)
        rendered = self.expression(node, value)
        new = name not in self.declared
        if self.target in {"luau", "lua"}:
            self.emit(("local " if new else "") + f"{name} = {rendered}")
        elif self.target == "python":
            self.emit(f"{name} = {rendered}")
        elif self.target in {"javascript", "typescript"}:
            self.emit(("let " if new else "") + f"{name} = {rendered};")
        else:
            self.emit(("var " if new else "") + f"{name} = {rendered};")
        self.declared.add(name)

    def compile_core(self, node: Node) -> bool:
        line = node.text
        n = node.line

        if line.startswith("say "):
            value = self.expression(node, line[4:])
            if self.target == "html":
                raw = line[4:].strip()
                if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {"'", '"'}:
                    text = raw[1:-1].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    self.emit(f"<p>{text}</p>")
                else:
                    raise TiranError("HTML target supports literal say statements only.")
            elif self.target in {"luau", "lua", "python", "javascript", "typescript"}:
                self.emit(f"print({value})")
            elif self.target == "java":
                self.emit(f"System.out.println({value});")
            else:
                self.emit(f"Console.WriteLine({value});")
            return True

        match = re.fullmatch(r"let\s+([A-Za-z_]\w*)\s*=\s*(.+)", line)
        if match:
            self.assign(node, match.group(1), match.group(2))
            return True

        match = re.fullmatch(r"([A-Za-z_]\w*)\s*=\s*(.+)", line)
        if match:
            self.assign(node, match.group(1), match.group(2))
            return True

        if line.startswith("return"):
            if self.target == "html":
                raise TiranError(f"Line {n}: return is not supported by the HTML target.")
            value = line[6:].strip()
            rendered = self.expression(node, value) if value else ""
            suffix = ";" if self.target in {"java", "csharp"} else ""
            self.emit("return" + ((" " + rendered) if rendered else "") + suffix)
            return True

        match = re.fullmatch(r"call\s+(.+)", line)
        if match:
            if not isinstance(node.expression, Expr):
                raise TiranError(f"Line {n}: call requires an expression.")
            rendered = lower_expr(node.expression, self.target)
            suffix = ";" if self.target in {"java", "csharp"} else ""
            self.emit(f"{rendered}{suffix}")
            return True

        return False

    def begin(self, node: Node, kind: str, head: str) -> None:
        if self.target == "html":
            raise TiranError(f"Line {node.line}: control flow is not supported by the HTML target.")
        h = self.expression(node, head)
        if kind == "if":
            if self.target in {"luau", "lua"}:
                self.emit(f"if {h} then")
            elif self.target == "python":
                self.emit(f"if {h}:")
            else:
                self.emit(f"if ({h}) {{")
        elif kind == "repeat":
            if self.target in {"luau", "lua"}:
                self.emit(f"for _ = 1, {h} do")
            elif self.target == "python":
                self.emit(f"for _ in range({h}):")
            else:
                self.emit(f"for (let i = 0; i < {h}; i++) {{")
        elif kind == "while":
            if self.target in {"luau", "lua"}:
                self.emit(f"while {h} do")
            elif self.target == "python":
                self.emit(f"while {h}:")
            else:
                self.emit(f"while ({h}) {{")
        self.blocks.append(kind)

    def function(self, text: str, line: int) -> None:
        if self.target == "html":
            raise TiranError(f"Line {line}: functions are not supported by the HTML target.")
        match = re.fullmatch(r"([A-Za-z_]\w*)\((.*)\)", text.strip())
        if not match:
            raise TiranError(f"Line {line}: use function name(args):")
        name = valid_name(match.group(1), line)
        args = [valid_name(x.strip(), line) for x in match.group(2).split(",") if x.strip()]
        joined = ", ".join(args)
        if self.target in {"luau", "lua"}:
            self.emit(f"function {name}({joined})")
        elif self.target == "python":
            self.emit(f"def {name}({joined}):")
        elif self.target in {"javascript", "typescript"}:
            self.emit(f"function {name}({joined}) {{")
        elif self.target == "java":
            self.emit(f"static Object {name}({', '.join('Object ' + x for x in args)}) {{")
        else:
            self.emit(f"static object {name}({', '.join('object ' + x for x in args)}) {{")
        self.blocks.append("function")

    def branch(self, node: Node) -> None:
        if not self.blocks or self.blocks[-1] != "if":
            raise TiranError(f"Line {node.line}: branch must follow if.")
        depth = len(self.blocks) - 1
        if node.text.startswith("elseif "):
            condition = self.expression(node, node.text[7:-1])
            if self.target in {"luau", "lua"}:
                self.emit(f"elseif {condition} then", depth)
            elif self.target == "python":
                self.emit(f"elif {condition}:", depth)
            else:
                self.emit(f"}} else if ({condition}) {{", depth)
        elif node.text == "else:":
            if self.target in {"luau", "lua"}:
                self.emit("else", depth)
            elif self.target == "python":
                self.emit("else:", depth)
            else:
                self.emit("} else {", depth)
        elif node.text.startswith("catch"):
            arg = node.text[5:-1].strip() or "error"
            if self.target == "luau":
                self.emit("end", depth)
                self.emit("if not __tiran_ok then", depth)
            elif self.target == "python":
                self.emit(f"except Exception as {arg}:", depth)
            else:
                self.emit(f"}} catch (Exception {arg}) {{", depth)

    def special(self, node: Node) -> bool:
        line, n = node.text, node.line

        match = re.fullmatch(r"import\s+([A-Za-z_]\w*)(?:\s+as\s+([A-Za-z_]\w*))?", line)
        if match:
            module, alias = match.group(1), match.group(2) or match.group(1)
            if self.target == "luau":
                self.emit(f"local {alias} = require(script.Parent.{module})")
            elif self.target == "python":
                self.emit(f"import {module} as {alias}" if alias != module else f"import {module}")
            elif self.target in {"javascript", "typescript"}:
                self.emit(f'import {alias} from "./{module}";')
            else:
                self.emit(f"// import {module}")
            self.imports.append(module)
            return True

        if line == "try:":
            if self.target == "luau":
                self.emit("local __tiran_ok, __tiran_result = pcall(function()")
            elif self.target == "python":
                self.emit("try:")
            else:
                self.emit("try {")
            self.blocks.append("try")
            return True

        if line.startswith("connect "):
            match = re.fullmatch(r"connect\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s+to\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)", line)
            if not match:
                raise TiranError(f"Line {n}: invalid connect statement.")
            self.require_luau(n, "connect")
            self.emit(f"{match.group(1)}:Connect({match.group(2)})")
            return True

        match = re.fullmatch(r"disconnect\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)", line)
        if match:
            self.require_luau(n, "disconnect")
            self.emit(f"{match.group(1)}:Disconnect()")
            return True

        match = re.fullmatch(r"destroy\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)", line)
        if match:
            self.require_luau(n, "destroy")
            self.emit(f"{match.group(1)}:Destroy()")
            return True

        match = re.fullmatch(r"wait(?:\s+(.+))?", line)
        if match:
            self.require_luau(n, "wait")
            if match.group(1):
                value = lower_expr(_parse_expression_text(match.group(1), n), self.target)
                self.emit(f"task.wait({value})")
            else:
                self.emit("task.wait()")
            return True

        match = re.fullmatch(r"fire\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*(.*)", line)
        if match:
            self.require_luau(n, "fire")
            args = match.group(2).strip()
            self.emit(f"{match.group(1)}:FireServer({args})" if args else f"{match.group(1)}:FireServer()")
            return True

        match = re.fullmatch(r"invoke\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*(.*)", line)
        if match:
            self.require_luau(n, "invoke")
            args = match.group(2).strip()
            self.emit(f"{match.group(1)}:InvokeServer({args})" if args else f"{match.group(1)}:InvokeServer()")
            return True

        match = re.fullmatch(r"service\s+([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)", line)
        if match:
            self.require_luau(n, "service")
            self.emit(f'local {match.group(1)} = game:GetService("{match.group(2)}")')
            self.declared.add(match.group(1))
            return True

        match = re.fullmatch(r"create\s+([A-Za-z_]\w*)\s+([A-Za-z_]\w*)", line, re.I)
        if match and match.group(1).lower() in ROBLOX_CLASSES:
            self.require_luau(n, "create")
            cls = ROBLOX_CLASSES[match.group(1).lower()]
            self.emit(f'local {match.group(2)} = Instance.new("{cls}")')
            self.declared.add(match.group(2))
            return True

        match = re.fullmatch(r"parent\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s+to\s+(.+)", line)
        if match:
            self.require_luau(n, "parent")
            value = lower_expr(_parse_expression_text(match.group(2), n), self.target)
            self.emit(f"{match.group(1)}.Parent = {value}")
            return True

        match = re.fullmatch(r"set\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*=\s*(.+)", line)
        if match:
            self.require_luau(n, "set")
            value = lower_expr(_parse_expression_text(match.group(2), n), self.target)
            self.emit(f"{roblox_prop(match.group(1))} = {value}")
            return True

        match = re.fullmatch(r"vector3\s+([A-Za-z_]\w*)\s*=\s*(.+)", line)
        if match:
            self.require_luau(n, "vector3")
            value = match.group(2)
            self.emit(f"local {match.group(1)} = Vector3.new({value})")
            self.declared.add(match.group(1))
            return True

        match = re.fullmatch(r"cframe\s+([A-Za-z_]\w*)\s*=\s*(.+)", line)
        if match:
            self.require_luau(n, "cframe")
            value = match.group(2)
            self.emit(f"local {match.group(1)} = CFrame.new({value})")
            self.declared.add(match.group(1))
            return True

        match = re.fullmatch(r"players\s+([A-Za-z_]\w*)\s*=\s*(.+)", line)
        if match:
            self.require_luau(n, "players")
            self.emit(f"local {match.group(1)} = Players:{match.group(2)}")
            self.declared.add(match.group(1))
            return True

        return False

    def node(self, node: Node) -> None:
        if node.kind in {"if", "repeat", "while"}:
            self.begin(node, node.kind, node.text[len(node.kind):].strip()[:-1])
            for child in node.children:
                self.node(child)
            self.close(node.line)
            return

        if node.kind == "function":
            self.function(node.text[9:-1], node.line)
            for child in node.children:
                self.node(child)
            self.close(node.line)
            return

        if node.kind == "try":
            self.special(node)
            for child in node.children:
                self.node(child)
            self.close(node.line)
            return

        if node.kind == "branch":
            self.branch(node)
            for child in node.children:
                self.node(child)
            return

        if self.compile_core(node):
            return
        if self.special(node):
            return
        raise TiranError(f"Line {node.line}: unknown TIRAN command: {node.text}")

    def close(self, line: int) -> None:
        if not self.blocks:
            raise TiranError(f"Line {line}: unexpected end.")
        kind = self.blocks.pop()
        if self.target in {"luau", "lua"}:
            if kind == "try" and self.target == "luau":
                self.emit("end)")
            else:
                self.emit("end")
        elif self.target != "python":
            self.emit("}")
    
    def finish(self) -> str:
        if self.blocks:
            raise TiranError(f"Unclosed block: {self.blocks[-1]}.")
        return "\n".join(self.lines) + "\n"


def compile_tiran(source: str, target: str | None = None) -> str:
    program = parse_tiran(source)
    if target is None:
        target = program.target
    if target is None:
        raise TiranError("No target selected. Add 'convert <language>' or use --target.")
    target = target_name(target)
    if program.target is not None and target_name(program.target) != target:
        raise TiranError(
            f"Target mismatch: source selects {program.target!r} but compiler requested {target!r}."
        )

    compiler = Compiler(target)
    for node in program.nodes:
        compiler.node(node)
    return compiler.finish()


def format_tiran(source: str) -> str:
    out = []
    depth = 0
    for raw in source.splitlines():
        line = raw.strip()
        if not line:
            if out and out[-1] != "":
                out.append("")
            continue
        if line in {"end", "else:"} or line.startswith("elseif ") or line.startswith("catch"):
            depth = max(0, depth - 1)
        out.append("    " * depth + line)
        if line.endswith(":") and not line.startswith("#") and not line.startswith("convert "):
            if line.startswith(("if ", "elseif ", "else", "repeat ", "while ", "function ", "try", "catch")):
                depth += 1
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(prog="tiran", description="Compile and format TIRAN source.")
    parser.add_argument("source", nargs="?")
    parser.add_argument("-o", "--output")
    parser.add_argument("-t", "--target")
    parser.add_argument("--format", action="store_true")
    parser.add_argument("--check", action="store_true", help="validate and compile without emitting source")
    parser.add_argument("--ast", action="store_true", help="print the parsed syntax tree as JSON")
    args = parser.parse_args()

    if not args.source:
        parser.error("source file is required")

    path = Path(args.source)
    try:
        source = path.read_text(encoding="utf-8")
        if args.ast:
            result = json.dumps(ast_dict(parse_tiran(source)), indent=2) + "\n"
        elif args.check:
            compile_tiran(source, args.target)
            result = "TIRAN OK\n"
        elif args.format:
            result = format_tiran(source)
        else:
            result = compile_tiran(source, args.target)

        if args.output:
            Path(args.output).write_text(result, encoding="utf-8")
        else:
            print(result, end="")
        return 0
    except (OSError, TiranError, ParseError) as exc:
        print(f"TIRAN ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
