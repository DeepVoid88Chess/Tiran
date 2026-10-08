"""Stable, user-facing diagnostic codes for TIRAN."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorInfo:
    code: str
    title: str
    explanation: str
    hint: str


# Codes are part of TIRAN's public interface. Do not reuse a retired code.
ERRORS: dict[str, ErrorInfo] = {}


def _group(prefix: str, entries: list[tuple[str, str, str, str]]) -> None:
    for suffix, title, explanation, hint in entries:
        code = f"{prefix}{suffix:03d}"
        ERRORS[code] = ErrorInfo(code, title, explanation, hint)


_group("E1", [
    (1, "Unexpected end", "An end statement has no open block.", "Remove the extra end or open the intended block."),
    (2, "Unclosed block", "A block was opened but never closed.", "Add end after the block's final statement."),
    (3, "Branch without block", "else, elseif, or catch has no matching open block.", "Place the branch inside its matching if or try block."),
    (4, "Invalid branch", "This branch is not valid at this position.", "Check branch order and matching block type."),
    (5, "Malformed expression", "The expression could not be parsed.", "Check operators, brackets, commas, and operand order."),
    (6, "Missing expression", "This statement requires an expression.", "Add a value or condition after the statement keyword."),
    (7, "Multiple targets", "More than one convert directive was found.", "Keep one convert directive at the top of the file."),
    (8, "Missing target", "No output language was selected.", "Add convert luau or pass --target."),
    (9, "Malformed function", "The function declaration is not valid TIRAN syntax.", "Use function name(arg1, arg2):"),
    (10, "Invalid identifier", "An identifier does not follow TIRAN naming rules.", "Start with a letter or underscore and use letters, digits, or underscores."),
    (11, "Unknown statement", "The compiler does not recognize this statement.", "Check spelling or consult the language specification."),
    (12, "Unexpected token", "A token appeared where it is not allowed.", "Remove the token or add the missing syntax before it."),
    (13, "Unterminated string", "A quoted string was not closed.", "Add the matching quote."),
    (14, "Unmatched delimiter", "A bracket or parenthesis is unmatched.", "Pair every opening delimiter with a closing delimiter."),
    (15, "Invalid call", "A call statement must contain a valid call expression.", "Use call function_name(arguments)."),
    (16, "Invalid assignment", "The assignment target or value is invalid.", "Use name = expression."),
    (17, "Duplicate directive", "A source directive was declared more than once.", "Keep only one directive of this kind."),
    (18, "Invalid import", "The import statement is malformed.", "Use import Module or import Module as Alias."),
    (19, "Invalid catch", "catch must directly follow an open try block.", "Use try:, then catch name:, then end."),
    (20, "Invalid block close", "The closing statement does not match an open block.", "Check the nesting of end statements."),
])
_group("E2", [
    (1, "Unsupported target", "The requested output language is not supported.", "Choose luau, lua, python, javascript, typescript, java, csharp, or html."),
    (2, "Target mismatch", "The source target differs from the requested target.", "Make convert and --target agree."),
    (3, "Feature unavailable for target", "This TIRAN feature requires a different output target.", "Compile with the target named in the diagnostic."),
    (4, "Unsupported expression", "This expression form cannot be emitted for the selected target.", "Rewrite the expression using supported target syntax."),
    (5, "Unsupported statement", "This statement cannot be emitted for the selected target.", "Use a supported statement or select another target."),
    (6, "Invalid target literal", "A literal cannot be represented with this target mapping.", "Use a target-supported value."),
    (7, "Invalid property path", "A property path is malformed.", "Use a dotted path such as player.Character.Name."),
    (8, "Invalid Roblox class", "The requested Roblox class is not in the compiler's class map.", "Use a supported class name or add it to the compiler map."),
    (9, "Invalid Roblox helper", "A Roblox helper statement is malformed.", "Check the helper's documented syntax."),
    (10, "Invalid module target", "This import form is not supported for the selected target.", "Use the target's native module system."),
])
_group("E3", [
    (1, "Unknown built-in", "The requested name is not in the TIRAN built-in registry.", "Check spelling or search the built-in catalog."),
    (2, "Built-in target limitation", "The registered Python runtime built-in cannot be emitted natively for this target.", "Use a target-native equivalent or compile to Python."),
    (3, "Built-in argument error", "A built-in received an invalid argument.", "Check the documented parameters and value types."),
    (4, "Built-in value error", "A built-in cannot process the supplied value.", "Check the input and the built-in's documented constraints."),
    (5, "Built-in division by zero", "A numeric operation attempted to divide by zero.", "Ensure the divisor is not zero."),
    (6, "Built-in index error", "A collection index is outside the available range.", "Check the collection length before indexing."),
    (7, "Built-in type error", "A value has the wrong type for this built-in.", "Pass the documented value type."),
    (8, "Built-in overflow", "A numeric operation exceeded supported limits.", "Use a smaller value or a safer numeric approach."),
    (9, "Built-in missing value", "A required value was not provided.", "Pass all required arguments."),
    (10, "Built-in unknown operation", "The requested built-in operation does not exist.", "Use a name from the current built-in catalog."),
])
_group("E4", [
    (1, "Internal compiler invariant", "The compiler encountered an unexpected internal state.", "Report the source and diagnostic code with a reproducible example."),
    (2, "Code generation failure", "The compiler could not emit valid target source.", "Simplify the construct and report the failing input."),
    (3, "Invalid AST node", "The syntax tree contains a node the compiler cannot handle.", "Check parser and compiler version compatibility."),
    (4, "Invalid compiler state", "The compiler state is inconsistent.", "Restart compilation and report a reproducible case."),
    (5, "Runtime support missing", "Generated code requires a runtime module that is unavailable.", "Keep the required TIRAN runtime beside the generated file."),
])
_group("E5", [
    (1, "Source file missing", "The source file could not be read.", "Check the file path and permissions."),
    (2, "Source encoding error", "The source file is not valid UTF-8.", "Save the file as UTF-8."),
    (3, "Output write error", "The compiler could not write the output file.", "Check the destination path and write permissions."),
    (4, "Invalid CLI arguments", "The command-line arguments are inconsistent.", "Run tiran --help and check the options."),
    (5, "Invalid AST request", "The source could not be converted to an AST report.", "Fix syntax errors before requesting --ast."),
    (6, "Invalid formatter input", "The formatter could not process the source.", "Fix malformed block structure and retry."),
    (7, "Check failed", "The source did not pass compiler validation.", "Read the earlier diagnostic and fix that issue."),
    (8, "Unknown command-line mode", "The selected command-line mode is not supported.", "Use --check, --format, --ast, or normal compilation."),
])
_group("E6", [
    (1, "Invalid numeric input", "A numeric operation received a value that is not a valid number.", "Pass an integer or floating-point value."),
    (2, "Invalid text input", "A text operation received a value that cannot be handled as text.", "Pass a string or convert the value first."),
    (3, "Invalid collection input", "A collection operation received an unsupported collection.", "Pass a list or another documented iterable."),
    (4, "Empty collection", "The operation requires at least one collection element.", "Check for an empty collection before calling it."),
    (5, "Invalid range", "The requested range has an invalid boundary or order.", "Ensure the lower boundary does not exceed the upper boundary."),
    (6, "Invalid encoding", "The requested text encoding is unsupported.", "Use a supported encoding such as UTF-8."),
    (7, "Invalid regular expression", "The regular expression is malformed.", "Escape special characters and check the pattern."),
    (8, "Invalid conversion", "A value cannot be converted to the requested type.", "Validate the input before converting it."),
])
_group("E7", [
    (1, "Reserved identifier", "The identifier conflicts with a reserved compiler name.", "Rename the variable or function."),
    (2, "Duplicate declaration", "The same declaration was added more than once.", "Use a distinct name or update the existing value."),
    (3, "Unknown symbol", "The compiler cannot resolve this symbol.", "Declare it, import it, or correct the spelling."),
    (4, "Invalid parameter list", "A function parameter list is malformed.", "Separate valid parameter names with commas."),
    (5, "Invalid return", "The return statement is not supported in this context.", "Move it into a function or choose a supported target."),
    (6, "Invalid loop control", "break or continue appears outside a loop.", "Move the statement into a loop."),
    (7, "Invalid control flow", "The requested control-flow transition is not valid.", "Check the enclosing block and branch order."),
    (8, "Potential name collision", "A generated helper name conflicts with a source name.", "Rename the source symbol to avoid the reserved helper prefix."),
])
_group("E8", [
    (1, "Configuration error", "The compiler configuration is invalid.", "Review the command-line options and project configuration."),
    (2, "Registry count mismatch", "The built-in registry has an unexpected number of entries.", "Regenerate the registry and run the standard-library tests."),
    (3, "Duplicate built-in", "Two built-ins use the same registered name.", "Give each built-in a unique name."),
    (4, "Documentation mismatch", "The documented built-in catalog does not match the registry.", "Regenerate built-in documentation from the registry."),
    (5, "Regression test failure", "A compiler behavior differs from its expected result.", "Reproduce the failing test and fix the underlying behavior."),
])

_group("E9", [
    (1, "Invalid argument count", "A function received the wrong number of arguments.", "Compare the call with the function's documented signature."),
    (2, "Invalid argument order", "Arguments were supplied in an unsupported order.", "Pass arguments in the order shown in the function reference."),
    (3, "Unsupported value", "The value is not supported by the requested operation.", "Use a value from the documented input domain."),
    (4, "Invalid boolean value", "A boolean operation received a non-boolean value.", "Use true or false, or explicitly convert the value."),
    (5, "Invalid collection key", "A collection key cannot be used for this operation.", "Use a supported, hashable key."),
    (6, "Duplicate key", "A map contains a duplicate key where unique keys are required.", "Keep one value for each key."),
    (7, "Invalid slice", "A slice boundary or step is invalid.", "Check start, stop, and step values."),
    (8, "Invalid Unicode operation", "A text operation cannot process the supplied Unicode value.", "Normalize the text or choose a Unicode-safe operation."),
    (9, "Invalid path", "A path is malformed or cannot be resolved.", "Check separators and ensure the referenced path exists."),
    (10, "Invalid service name", "The requested Roblox service name is invalid.", "Use an official Roblox service name."),
    (11, "Invalid event connection", "The event or callback cannot be connected as written.", "Check the event path and callback function."),
    (12, "Invalid remote call", "The remote-call statement is malformed.", "Check the remote object and its argument list."),
    (13, "Invalid instance creation", "The instance creation statement is invalid.", "Use create ClassName variable with a supported class."),
    (14, "Invalid property assignment", "The property assignment is malformed.", "Use set object.property = expression."),
    (15, "Invalid vector", "A Vector3 value does not have three valid components.", "Provide x, y, and z components."),
    (16, "Invalid CFrame", "A CFrame constructor has invalid components.", "Provide valid position components or a supported CFrame expression."),
    (17, "Invalid loop count", "The repeat count is not a valid loop count.", "Use a non-negative integer expression."),
    (18, "Invalid condition", "The condition cannot be represented for the selected target.", "Use a boolean expression supported by the target."),
    (19, "Invalid module name", "The module identifier is malformed.", "Use a valid module name."),
    (20, "Invalid output extension", "The output file extension does not match the selected target.", "Use the target's expected file extension."),
    (21, "Invalid source directive", "A source-level directive is malformed.", "Check the directive spelling and its required arguments."),
    (22, "Invalid compiler option", "A compiler option has an invalid value.", "Run tiran --help and use a supported option value."),
    (23, "Built-in registry unavailable", "The built-in registry could not be loaded.", "Ensure the TIRAN runtime files are installed together."),
    (24, "Built-in documentation unavailable", "The built-in documentation could not be found.", "Restore the docs directory or use the online reference."),
    (25, "Unsupported pipeline", "A built-in pipeline cannot process this type combination.", "Choose a pipeline whose stages accept each other's output."),
])


def classify_error(message: str) -> ErrorInfo:
    """Map a legacy human-readable error message to a stable public code."""
    text = message.lower()
    rules = (
        (("unsupported target",), "E2001"),
        (("target mismatch",), "E2002"),
        (("requires convert", "not supported by the html target", "control flow is not supported", "functions are not supported"), "E2003"),
        (("unexpected end",), "E1001"),
        (("unclosed block",), "E1002"),
        (("branch has no open block",), "E1003"),
        (("catch must follow try", "branch must follow if"), "E1019"),
        (("invalid name",), "E1010"),
        (("unknown tiran command",), "E1011"),
        (("expression is required",), "E1006"),
        (("invalid connect", "invalid import", "invalid roblox"), "E2009"),
        (("no target selected",), "E1008"),
        (("multiple convert",), "E1007"),
        (("unknown literal", "unsupported expression node"), "E2004"),
        (("invalid function", "use function"), "E1009"),
    )
    for needles, code in rules:
        if any(needle in text for needle in needles):
            return ERRORS[code]
    if text.startswith("line ") and ("parse" in text or "expression" in text):
        return ERRORS["E1005"]
    if "line " in text:
        return ERRORS["E1012"]
    return ERRORS["E4001"]


def error_catalog_markdown() -> str:
    """Render every stable diagnostic code for documentation."""
    lines = [
        "# TIRAN Error Codes",
        "",
        "Error codes are stable identifiers intended for tests, editors, logs, and support reports.",
        "Messages describe the source-level problem; hints suggest the next useful action.",
        "",
        "| Code | Title | Meaning | Suggested fix |",
        "|---|---|---|---|",
    ]
    for code in sorted(ERRORS):
        info = ERRORS[code]
        cells = [info.code, info.title, info.explanation, info.hint]
        lines.append("| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |")
    lines.append("")
    return "\n".join(lines)
