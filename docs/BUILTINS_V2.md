# TIRAN Built-in Function Reference

TIRAN now defines **22,000 uniquely named callable built-ins** in its Python registry.

## Original 11,000 built-ins

The original catalog and its operation descriptions are in [BUILTINS.md](BUILTINS.md).

## Additional 11,000 built-ins

Each additional function is a three-stage, type-family-scoped pipeline. Its name describes the exact order of operations. Every entry below documents the function name and its behavior.

- [Additional built-ins 01 (entries 1-1000)](BUILTINS_EXTRA_01.md)
- [Additional built-ins 02 (entries 1001-2000)](BUILTINS_EXTRA_02.md)
- [Additional built-ins 03 (entries 2001-3000)](BUILTINS_EXTRA_03.md)
- [Additional built-ins 04 (entries 3001-4000)](BUILTINS_EXTRA_04.md)
- [Additional built-ins 05 (entries 4001-5000)](BUILTINS_EXTRA_05.md)
- [Additional built-ins 06 (entries 5001-6000)](BUILTINS_EXTRA_06.md)
- [Additional built-ins 07 (entries 6001-7000)](BUILTINS_EXTRA_07.md)
- [Additional built-ins 08 (entries 7001-8000)](BUILTINS_EXTRA_08.md)
- [Additional built-ins 09 (entries 8001-9000)](BUILTINS_EXTRA_09.md)
- [Additional built-ins 10 (entries 9001-10000)](BUILTINS_EXTRA_10.md)
- [Additional built-ins 11 (entries 10001-11000)](BUILTINS_EXTRA_11.md)

## Important runtime note

The built-in registry is implemented in Python. Generated Python can call these functions through `tiran_stdlib.get_builtin`. Other targets, including Luau, still need target-native equivalents or a dedicated runtime implementation before these Python callables can run there.
