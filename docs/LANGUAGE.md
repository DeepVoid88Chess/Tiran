# TIRAN Language Specification

## Target
Use `convert luau`, `convert lua`, `convert python`, `convert javascript`, `convert typescript`, `convert java`, or `convert csharp`.

## Statements
- `say expression`
- `let name = expression`
- `name = expression`
- `if expression:` / `else:` / `end`
- `repeat expression:` / `end`
- `while expression:` / `end`
- `function name(args):` / `end`
- `call name(args)`
- `return expression`
- `break`
- `continue`

## Roblox/Luau
- `create part name`
- `service variable = ServiceName`
- `set object.property = expression`

Expressions are intentionally close to the selected target language. TIRAN owns the program structure while allowing normal target expressions to pass through.

Errors are deterministic and include the source line whenever possible.
