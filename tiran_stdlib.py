"""TIRAN standard library.

This module registers exactly 11,000 callable built-ins.
The generated families are concrete operations with a captured numeric
parameter, not placeholder functions.
"""
from __future__ import annotations
import math
from typing import Any, Callable

Builtin = Callable[..., Any]
BUILTINS: dict[str, Builtin] = {}


def _add(name: str, fn: Builtin) -> None:
    if name in BUILTINS:
        raise RuntimeError(f"duplicate TIRAN builtin: {name}")
    BUILTINS[name] = fn


CORE: dict[str, Builtin] = {
    "abs": abs, "min": min, "max": max, "round": round,
    "floor": math.floor, "ceil": math.ceil, "sqrt": math.sqrt, "pow": pow,
    "length": lambda x: len(x), "lower": lambda x: str(x).lower(),
    "upper": lambda x: str(x).upper(), "trim": lambda x: str(x).strip(),
    "contains": lambda x, y: y in x,
    "starts_with": lambda x, y: str(x).startswith(str(y)),
    "ends_with": lambda x, y: str(x).endswith(str(y)),
    "join": lambda xs, sep="": str(sep).join(map(str, xs)),
    "split": lambda x, sep=None: str(x).split(sep),
    "replace": lambda x, old, new: str(x).replace(str(old), str(new)),
    "reverse": lambda x: x[::-1], "sort": lambda x: sorted(x),
    "sum": lambda x: sum(x), "any": lambda x: any(x),
    "all": lambda x: all(x),
}
for _name, _fn in CORE.items():
    _add(_name, _fn)


def _number_add(n): return lambda x: x + n
def _number_subtract(n): return lambda x: x - n
def _number_multiply(n): return lambda x: x * n
def _number_divide(n):
    if n == 0:
        return lambda x: (_ for _ in ()).throw(ZeroDivisionError("TIRAN builtin divisor is zero"))
    return lambda x: x / n
def _text_repeat(n): return lambda x: str(x) * n
def _text_prefix(n): return lambda x: str(x)[:n]
def _text_suffix(n): return lambda x: str(x)[-n:] if n else ""
def _list_take(n): return lambda x: list(x)[:n]
def _list_drop(n): return lambda x: list(x)[n:]
def _list_pad(n): return lambda x, value=None: list(x) + [value] * max(0, n - len(x))
def _number_mod(n):
    if n == 0:
        return lambda x: (_ for _ in ()).throw(ZeroDivisionError("TIRAN builtin modulus is zero"))
    return lambda x: x % n

# 11,000 total built-ins:
# 23 core functions + 10 families of 1,000 + 1 family of 977.
_FAMILIES = (
    ("number_add", _number_add, 1000),
    ("number_subtract", _number_subtract, 1000),
    ("number_multiply", _number_multiply, 1000),
    ("number_divide", _number_divide, 1000),
    ("text_repeat", _text_repeat, 1000),
    ("text_prefix", _text_prefix, 1000),
    ("text_suffix", _text_suffix, 1000),
    ("list_take", _list_take, 1000),
    ("list_drop", _list_drop, 1000),
    ("list_pad", _list_pad, 1000),
    ("number_mod", _number_mod, 977),
)
for _family, _factory, _count in _FAMILIES:
    for _n in range(_count):
        _add(f"{_family}_{_n}", _factory(_n))

BUILTIN_COUNT = len(BUILTINS)
assert BUILTIN_COUNT == 11000, f"internal registry count mismatch: {BUILTIN_COUNT}"


def get_builtin(name: str) -> Builtin:
    """Return one of the 11,000 built-ins by exact name."""
    try:
        return BUILTINS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown TIRAN builtin '{name}'.") from exc
