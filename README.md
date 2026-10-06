# TIRAN

**TIRAN - Designed to make coding easier.**

TIRAN is a universal coding and translation layer. You write TIRAN code once, choose a target language, and TIRAN generates real code for that language.

## TIRAN v0.1

The first version supports:

- Luau
- Lua
- Python
- JavaScript
- TypeScript
- Java
- C#

### Example

TIRAN:

```tiran
convert luau

say "Hello from TIRAN!"
```

Output:

```lua
print("Hello from TIRAN!")
```

## Run it

Requires Python 3.

```text
python tiran.py examples/hello.tiran
```

To save the generated code:

```text
python tiran.py examples/hello.tiran hello.lua
```

## Roadmap

TIRAN will grow from this tiny compiler into a real language and translation system, with variables, functions, conditions, loops, and richer target-language generation.
