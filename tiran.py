"""TIRAN v0.2
TIRAN - Designed to make coding easier.
A small multi-target compiler with variables, expressions, conditions,
loops, functions, and Roblox-friendly Luau output.
"""

import ast
import sys


SUPPORTED_TARGETS = {
    "luau": "luau",
    "lua": "lua",
    "python": "python",
    "javascript": "javascript",
    "typescript": "typescript",
    "java": "java",
    "csharp": "csharp",
}


class CompilerError(ValueError):
    pass


def parse_value(value):
    value = value.strip()
    if not value:
        raise CompilerError("A value is required.")
    return value


def quote_string(value):
    try:
        parsed = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        raise CompilerError(f"Invalid string literal: {value}")
    if not isinstance(parsed, str):
        raise CompilerError(f"Expected a string: {value}")
    return parsed


def split_assignment(line):
    if "=" not in line:
        return None
    left, right = line.split("=", 1)
    left = left.strip()
    right = right.strip()
    if not left or not right:
        raise CompilerError("Assignments need a name and a value.")
    if not left.replace("_", "a").isalnum() or left[0].isdigit():
        raise CompilerError(f"Invalid variable name: {left}")
    return left, right


def translate_expr(expr, target):
    expr = expr.strip()
    if expr.lower() == "true":
        return "True" if target == "python" else "true"
    if expr.lower() == "false":
        return "False" if target == "python" else "false"
    if expr.lower() in {"nothing", "null", "nil"}:
        return "None" if target == "python" else ("null" if target in {"javascript", "typescript"} else "nil")
    if expr.startswith("string "):
        return expr[7:].strip()
    return expr


def indent(lines, level=1):
    prefix = "    " * level
    return [prefix + line if line else "" for line in lines]


def compile_say(target, value):
    if target in {"luau", "lua", "python", "javascript", "typescript"}:
        return f"print({translate_expr(value, target)})"
    if target == "java":
        return f"System.out.println({translate_expr(value, target)});"
    if target == "csharp":
        return f"Console.WriteLine({translate_expr(value, target)});"
    raise CompilerError(f"Unsupported target language: {target}")


def compile_assignment(target, name, value):
    value = translate_expr(value, target)
    if target in {"luau", "lua"}:
        return f"local {name} = {value}"
    if target == "python":
        return f"{name} = {value}"
    if target in {"javascript", "typescript"}:
        return f"let {name} = {value};"
    if target == "java":
        return f"var {name} = {value};"
    if target == "csharp":
        return f"var {name} = {value};"
    raise CompilerError(f"Unsupported target language: {target}")


def compile_condition(target, condition):
    condition = condition.strip()
    replacements = {
        " and ": " and ",
        " or ": " or ",
        " not ": " not ",
        "true": "true",
        "false": "false",
    }
    for old, new in replacements.items():
        condition = condition.replace(old, new)
    if target in {"luau", "lua", "javascript", "typescript"}:
        return condition.replace(" and ", " and ").replace(" or ", " or ")
    if target == "python":
        return condition
    if target in {"java", "csharp"}:
        return condition.replace(" and ", " && ").replace(" or ", " || ")
    return condition


def compile_tiran(source):
    target = None
    output = []
    stack = []

    lines = source.splitlines()

    def current_output():
        return output

    def emit(line):
        level = len(stack)
        current_output().extend(indent([line], level))

    def close_block(kind, line_number):
        if not stack or stack[-1] != kind:
            expected = stack[-1] if stack else "nothing"
            raise CompilerError(
                f"Line {line_number}: cannot close '{kind}' here; open block is '{expected}'."
            )
        stack.pop()

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if line.lower().startswith("convert "):
            if stack:
                raise CompilerError(f"Line {line_number}: convert cannot be inside a block.")
            target_name = line[8:].strip().lower()
            if target_name not in SUPPORTED_TARGETS:
                raise CompilerError(
                    f"Line {line_number}: unsupported target '{target_name}'."
                )
            target = SUPPORTED_TARGETS[target_name]
            continue

        if target is None:
            raise CompilerError(
                f"Line {line_number}: choose a target first with 'convert <language>'."
            )

        if line.startswith("say "):
            emit(compile_say(target, parse_value(line[4:])))
            continue

        assignment = split_assignment(line)
        if assignment:
            name, value = assignment
            emit(compile_assignment(target, name, value))
            continue

        if line.startswith("if ") and line.endswith(":"):
            condition = compile_condition(target, line[3:-1])
            if target in {"luau", "lua", "python", "javascript", "typescript"}:
                emit(f"if {condition} then" if target in {"luau", "lua"} else f"if {condition}:")
            else:
                emit(f"if ({condition}) {{")
            stack.append("if")
            continue

        if line == "else:":
            if not stack or stack[-1] != "if":
                raise CompilerError(f"Line {line_number}: else must follow if.")
            if target in {"luau", "lua", "python", "javascript", "typescript"}:
                if target in {"luau", "lua"}:
                    output.append("    " * (len(stack) - 1) + "else")
                else:
                    output.append("    " * (len(stack) - 1) + "else:")
            else:
                output.append("    " * (len(stack) - 1) + "} else {")
            continue

        if line == "end":
            if not stack:
                raise CompilerError(f"Line {line_number}: unexpected end.")
            kind = stack.pop()
            if target in {"luau", "lua"}:
                output.append("    " * len(stack) + "end")
            elif target in {"python"}:
                pass
            elif target in {"javascript", "typescript", "java", "csharp"}:
                output.append("    " * len(stack) + "}")
            continue

        if line.startswith("repeat ") and line.endswith(":"):
            count = line[7:-1].strip()
            if target in {"luau", "lua"}:
                emit(f"for _ = 1, {count} do")
            elif target == "python":
                emit(f"for _ in range({count}):")
            elif target in {"javascript", "typescript"}:
                emit(f"for (let i = 0; i < {count}; i++) {{")
            else:
                emit(f"for (var i = 0; i < {count}; i++) {{")
            stack.append("repeat")
            continue

        if line.startswith("function ") and line.endswith(":"):
            signature = line[9:-1].strip()
            if "(" not in signature or not signature.endswith(")"):
                raise CompilerError(f"Line {line_number}: functions need name(arguments).")
            if target in {"luau", "lua"}:
                emit(f"function {signature}")
            elif target == "python":
                emit(f"def {signature}:")
            elif target in {"javascript", "typescript"}:
                emit(f"function {signature} {{")
            elif target == "java":
                emit(f"static void {signature} {{")
            elif target == "csharp":
                emit(f"static void {signature} {{")
            stack.append("function")
            continue

        if line.startswith("return "):
            value = translate_expr(line[7:], target)
            if target in {"luau", "lua", "python", "javascript", "typescript"}:
                emit(f"return {value}")
            else:
                emit(f"return {value};")
            continue

        if line.startswith("call "):
            call = line[5:].strip()
            if target in {"luau", "lua", "python"}:
                emit(call)
            else:
                emit(call + ("" if call.endswith(";") else ";"))
            continue

        raise CompilerError(f"Line {line_number}: unknown TIRAN command: {line}")

    if target is None:
        raise CompilerError("No target language selected.")
    if stack:
        raise CompilerError(f"Unclosed block: {stack[-1]}. Add 'end'.")
    return "\n".join(output)


def main():
    if len(sys.argv) not in {2, 3}:
        print("Usage: python tiran.py <file.tiran> [output-file]")
        raise SystemExit(1)

    try:
        with open(sys.argv[1], "r", encoding="utf-8") as file:
            source = file.read()
        result = compile_tiran(source)

        if len(sys.argv) == 3:
            with open(sys.argv[2], "w", encoding="utf-8") as file:
                file.write(result + "\n")
            print(f"Compiled {sys.argv[1]} -> {sys.argv[2]}")
        else:
            print(result)
    except (OSError, CompilerError) as error:
        print(f"TIRAN ERROR: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
