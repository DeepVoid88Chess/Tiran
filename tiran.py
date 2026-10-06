"""TIRAN v0.1
TIRAN - Designed to make coding easier.
A tiny first compiler that translates TIRAN into real target-language code.
"""

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


def compile_say(target, value):
    if target in {"luau", "lua", "python", "javascript", "typescript"}:
        return f"print({value})"
    if target == "java":
        return f"System.out.println({value});"
    if target == "csharp":
        return f"Console.WriteLine({value});"
    raise ValueError(f"Unsupported target language: {target}")


def compile_tiran(source):
    target = None
    output = []

    for line_number, raw_line in enumerate(source.splitlines(), start=1):
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if line.lower().startswith("convert "):
            target_name = line[8:].strip().lower()
            if target_name not in SUPPORTED_TARGETS:
                raise ValueError(
                    f"Line {line_number}: unsupported target '{target_name}'."
                )
            target = SUPPORTED_TARGETS[target_name]
            continue

        if target is None:
            raise ValueError(
                f"Line {line_number}: choose a target first with 'convert <language>'."
            )

        if line.startswith("say "):
            value = line[4:].strip()
            if not value:
                raise ValueError(f"Line {line_number}: say needs a value.")
            output.append(compile_say(target, value))
            continue

        raise ValueError(f"Line {line_number}: unknown TIRAN command: {line}")

    if target is None:
        raise ValueError("No target language selected.")

    return "\n".join(output)


def main():
    if len(sys.argv) not in {2, 3}:
        print("Usage: python tiran.py <file.tiran> [output-file]")
        raise SystemExit(1)

    input_file = sys.argv[1]

    try:
        with open(input_file, "r", encoding="utf-8") as file:
            source = file.read()

        result = compile_tiran(source)

        if len(sys.argv) == 3:
            with open(sys.argv[2], "w", encoding="utf-8") as file:
                file.write(result + "\n")
            print(f"Compiled {input_file} -> {sys.argv[2]}")
        else:
            print(result)

    except (OSError, ValueError) as error:
        print(f"TIRAN ERROR: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
