# TIRAN Language Specification

TIRAN is designed as a small readable core language with target-specific extensions. Source is validated before code generation so malformed block structure is reported consistently.

## Target
Use `convert luau`, `convert lua`, `convert python`, `convert javascript`, `convert typescript`, `convert java`, `convert csharp`, or `convert html`.

## Statements
- `say expression`
- `let name = expression`
- `name = expression`
- `if expression:` / `elseif expression:` / `else:` / `end`
- `repeat expression:` / `end`
- `while expression:` / `end`
- `function name(args):` / `end`
- `call name(args)`
- `return expression`
- `break`
- `continue`
- `import Module [as Alias]`
- `try:` / `catch name:` / `end`

## Expressions
TIRAN expressions are deliberately close to target syntax. Arithmetic, comparisons, boolean operators, function calls, table/collection literals, indexing, and constructors can be passed through to the selected target.

Example:

    let total = 10 + 5 * 2
    let items = {"apple", "cake"}
    let player = {name = "TIRAN", score = total}

The compiler normalizes common TIRAN literals such as `true`, `false`, `nil`, and `nothing` for the selected target.

## Roblox/Luau
- `create part name`
- `create folder name`
- `create model name`
- `create remoteevent name`
- `create remote_function name`
- `create bindableevent name`
- `create screengui name`
- `create frame name`
- `create textlabel name`
- `create textbutton name`
- `create imagelabel name`
- `create imagebutton name`
- `service variable = ServiceName`
- `set object.property = expression`
- `parent object to expression`
- `connect object.Event to function`
- `disconnect connection`
- `destroy object`
- `wait [seconds]`
- `fire remote arguments`
- `invoke remote arguments`
- `vector3 name = x, y, z`
- `cframe name = x, y, z`

Property paths can be nested, for example:

    set player.Character.Humanoid.WalkSpeed = 20

## Modules
For Luau, `import Inventory as Inv` becomes:

    local Inv = require(script.Parent.Inventory)

## Error handling
TIRAN's `try/catch` construct maps to each target's closest supported mechanism. Luau uses `pcall` because Luau does not have native try/catch syntax.

## Tooling

Validate a program without emitting generated code:

    python tiran.py program.tiran --check

Inspect the parsed syntax tree:

    python tiran.py program.tiran --ast

The AST is intentionally small and dependency-free so future editor tooling can build on it.

## Formatting
Run:

    python tiran.py file.tiran --format --output formatted.tiran

The formatter normalizes indentation without changing the program's statements.

## Errors
Errors are deterministic and include the source line whenever possible. Target-specific operations fail clearly rather than emitting fake code.
