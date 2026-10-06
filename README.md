# TIRAN

**TIRAN - Designed to make coding easier.**

TIRAN is a universal coding and translation layer. You write TIRAN code once, choose a target language, and TIRAN generates real target-language code.

## TIRAN v0.2

TIRAN currently supports:

- Luau
- Lua
- Python
- JavaScript
- TypeScript
- Java
- C#

## Features

### Choose a language

```tiran
convert luau
```

### Say something

```tiran
say "Hello from TIRAN!"
```

Luau output:

```lua
print("Hello from TIRAN!")
```

### Variables

```tiran
name = "Jackson"
score = 100
say name
```

### Conditions

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
```

### Functions

```tiran
function greet(name):
    say name
end

call greet("TIRAN")
```

## Run TIRAN

Requires Python 3.

Compile and print:

```text
python tiran.py examples/hello.tiran
```

Compile and save:

```text
python tiran.py examples/hello.tiran hello.lua
```

Try the larger example:

```text
python tiran.py examples/features.tiran
```

## Roadmap

TIRAN is an evolving compiler. Future releases can add a stronger parser, richer expressions, Roblox-specific commands, more target languages, a test suite, and a dedicated editor.

**TIRAN - Designed to make coding easier.**
