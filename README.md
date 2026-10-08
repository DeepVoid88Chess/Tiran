 # TIRAN

**TIRAN - a readable multi-target programming language.**

TIRAN is a readable, dependency-free programming language with a compiler that can generate source for multiple targets. The project is designed around a small, understandable language core, deterministic diagnostics, and a growing standard library.

## Using the standard library

The Python target can call any registered TIRAN built-in directly by name. For
example, `number_add(10, 5)` compiles to a call through
`tiran_stdlib.get_builtin`. Keep `tiran_stdlib.py` alongside generated Python
when the script uses TIRAN built-ins. The 22,000-entry registry is available
through `get_builtin(name)` in Python; the compiler currently wires these
calls into generated Python, not yet into standalone Luau output.

## Current release

TIRAN includes:

- A command-line compiler
- Luau, Lua, Python, JavaScript, TypeScript, Java, C#, and HTML targets
- Variables, assignment, expressions, conditionals, loops, functions, calls, returns, break, and continue
- Imports/modules and cross-target try/catch syntax
- A built-in formatter, syntax checker, and AST inspection mode
- Roblox/Luau helpers for Parts, folders, models, remotes, services, events, waiting, and destruction
- An exactly **11,000-function standard library**
- Stable compiler diagnostic codes with actionable hints in `docs/ERROR_CODES.md`
- Deterministic compiler errors with source line numbers and target validation
- Examples, tests, and GitHub Actions CI
- No third-party Python dependencies

## 22,000 built-ins

The file tiran_stdlib.py contains exactly 22,000 registered callable built-ins.

They are real Python callables, not empty placeholders. The library has core operations, parameterized operations, transforms, and named operation pipelines. Every registered name is documented in `docs/BUILTINS.md`.

Examples:

    from tiran_stdlib import get_builtin

    get_builtin("number_add")(10, 5)       # 15
    get_builtin("text_repeat")("yo", 3)    # yoyoyo
    get_builtin("text_prefix")("TIRAN", 4) # TIRA
    get_builtin("list_take")([1,2,3], 2)   # [1, 2]

The registry deliberately avoids baked-in numeric suffix names such as `number_add_5`; parameters belong in function arguments. The original 11,000 names are documented in `docs/BUILTINS.md`; the additional 11,000 are documented in `docs/BUILTINS_EXTRA_01.md` through `docs/BUILTINS_EXTRA_11.md`. The complete index is `docs/BUILTINS_V2.md`.

## Language

### Target

    convert luau

Supported targets:

- luau
- lua
- python
- javascript / js
- typescript / ts
- java
- csharp / cs
- html

### Output

    say "Hello from TIRAN!"

### Variables

    name = "TIRAN"
    score = 100
    say name

### If / else

    if score > 50:
        say "Great score!"
    else:
        say "Keep going!"
    end

### Loops

    repeat 5:
        say "Hello!"
    end

    while score > 0:
        score = score - 1
    end

### Functions

    function greet(name):
        say name
    end

    call greet("TIRAN")

### Roblox / Luau

    convert luau
    service RunService = RunService
    create part block
    set block.name = "TiranBlock"
    set block.anchored = true
    set block.position = Vector3.new(0, 5, 0)
    set block.parent = workspace

    function onTouched(hit):
        say hit
    end
    connect block.Touched to onTouched
    wait 1
    destroy block

This generates real Luau:

    local RunService = game:GetService("RunService")
    local block = Instance.new("Part")
    block.Name = "TiranBlock"
    block.Anchored = true
    block.Position = Vector3.new(0, 5, 0)
    block.Parent = workspace

## Modules and error handling\n\nTIRAN supports readable module imports such as `import Inventory as Inv`, which becomes `local Inv = require(script.Parent.Inventory)` for Luau. The `try` / `catch` form maps to the closest supported target mechanism. Luau uses protected calls (`pcall`).\n\n## CLI

Compile using the target in the source:

    python tiran.py examples/hello.tiran

Or select it from the command line:

    python tiran.py examples/hello.tiran --target luau

Format a TIRAN file with `--format`, or write compiled output to a file.\n\nWrite the result to a file:

    python tiran.py examples/hello.tiran --output hello.luau

Run the test suite:

    python -m unittest discover -s tests -v

## Project layout

    Tiran/
      tiran.py
      tiran_stdlib.py
      README.md
      docs/
        LANGUAGE.md
        API.md
        STDLIB.md
      examples/
        hello.tiran
        control_flow.tiran
        roblox.tiran
        roblox_game.tiran
      tests/
        test_tiran.py
      .github/
        workflows/
          test.yml

## Design rule

TIRAN only claims features that are implemented and tested. Target-specific operations produce clear compiler errors instead of silently generating fake code.

**TIRAN - readable code, explicit compilation, many targets.**
