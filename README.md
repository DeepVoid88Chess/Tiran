# TIRAN

**TIRAN - Designed to make coding easier.**

TIRAN is a small universal coding language and compiler. You write readable TIRAN source, choose a target, and TIRAN generates real source code for that target.

## v1.0

TIRAN v1.0 is the first complete, usable compiler release.

### Targets

- Luau
- Lua
- Python
- JavaScript
- TypeScript
- Java
- C#

Aliases: `js`, `ts`, and `cs`.

## Core syntax

### Target
```tiran
convert luau
```

### Output
```tiran
say "Hello from TIRAN!"
```

### Variables
```tiran
name = "TIRAN"
score = 100
say name
```

### If / else
```tiran
if score > 50:
    say "Great score!"
else:
    say "Keep going!"
end
```

### Loops
```tiran
repeat 5:
    say "Hello!"
end

while score > 0:
    score = score - 1
end
```

### Functions
```tiran
function greet(name):
    say name
end

call greet("TIRAN")
```

### Roblox / Luau
```tiran
convert luau

create part block
set block.name = "TiranBlock"
set block.anchored = true
set block.position = Vector3.new(0, 5, 0)
set block.parent = workspace
```

This generates real Luau such as:
```lua
local block = Instance.new("Part")
block.Name = "TiranBlock"
block.Anchored = true
block.Position = Vector3.new(0, 5, 0)
block.Parent = workspace
```

## CLI

Compile using the target in the source:
```text
python tiran.py examples/hello.tiran
```

Or select it from the command line:
```text
python tiran.py examples/hello.tiran --target luau
```

Write the result to a file:
```text
python tiran.py examples/hello.tiran --output hello.luau
```

## Tests

```text
python -m unittest discover
```

## Project layout

```text
Tiran/
  tiran.py
  README.md
  examples/
    hello.tiran
    features.tiran
    roblox.tiran
  tests/
    test_tiran.py
```

## What "complete" means here

TIRAN v1.0 is a complete first release of the compiler defined by this repository. It does not pretend that every programming-language feature can be translated perfectly between every language. Unsupported or target-specific operations produce clear compiler errors instead of silently generating fake code.

Future versions can expand the language, targets, Roblox APIs, editor, and tooling without changing the core idea.

**TIRAN - Designed to make coding easier.**
