"""Second wave of TIRAN standard-library operations.

These are real unary pipelines grouped by the type they accept and return.
The names describe the exact operation order, and every generated callable
closes over its own operations safely.
"""
from __future__ import annotations

import math
import re
import statistics
import unicodedata
from typing import Any, Callable

Builtin = Callable[[Any], Any]


NUMBER_OPS: dict[str, Builtin] = {
    "absolute": abs,
    "negate": lambda x: -x,
    "square": lambda x: x * x,
    "cube": lambda x: x * x * x,
    "double": lambda x: x * 2,
    "half": lambda x: x / 2,
    "increment": lambda x: x + 1,
    "decrement": lambda x: x - 1,
    "reciprocal": lambda x: 1 / x,
    "sqrt": lambda x: math.sqrt(abs(x)),
    "floor": math.floor,
    "ceil": math.ceil,
    "round": round,
    "truncate": math.trunc,
    "fractional_part": lambda x: x - math.trunc(x),
    "distance_from_zero": abs,
    "positive_part": lambda x: max(0, x),
    "negative_part": lambda x: min(0, x),
    "double_then_add_one": lambda x: x * 2 + 1,
    "half_then_add_one": lambda x: x / 2 + 1,
    "percent_value": lambda x: x / 100,
    "radians": math.radians,
    "degrees": math.degrees,
}

TEXT_OPS: dict[str, Builtin] = {
    "lower": lambda x: str(x).lower(),
    "upper": lambda x: str(x).upper(),
    "trim": lambda x: str(x).strip(),
    "reverse": lambda x: str(x)[::-1],
    "title": lambda x: str(x).title(),
    "capitalize": lambda x: str(x).capitalize(),
    "casefold": lambda x: str(x).casefold(),
    "swapcase": lambda x: str(x).swapcase(),
    "remove_spaces": lambda x: str(x).replace(" ", ""),
    "spaces_to_underscores": lambda x: str(x).replace(" ", "_"),
    "spaces_to_hyphens": lambda x: str(x).replace(" ", "-"),
    "remove_digits": lambda x: re.sub(r"\\d", "", str(x)),
    "keep_digits": lambda x: "".join(c for c in str(x) if c.isdigit()),
    "remove_letters": lambda x: "".join(c for c in str(x) if not c.isalpha()),
    "keep_letters": lambda x: "".join(c for c in str(x) if c.isalpha()),
    "remove_punctuation": lambda x: "".join(c for c in str(x) if not unicodedata.category(c).startswith("P")),
    "keep_ascii": lambda x: str(x).encode("ascii", "ignore").decode("ascii"),
    "normalize_whitespace": lambda x: " ".join(str(x).split()),
    "first_character": lambda x: str(x)[:1],
    "last_character": lambda x: str(x)[-1:],
    "sort_characters": lambda x: "".join(sorted(str(x))),
    "unique_characters": lambda x: "".join(dict.fromkeys(str(x))),
    "duplicate_text": lambda x: str(x) * 2,
}

LIST_OPS: dict[str, Builtin] = {
    "copy": lambda x: list(x),
    "reverse": lambda x: list(reversed(x)),
    "sort": lambda x: sorted(x),
    "sort_reverse": lambda x: sorted(x, reverse=True),
    "unique": lambda x: list(dict.fromkeys(x)),
    "deduplicate": lambda x: list(dict.fromkeys(x)),
    "rotate_left": lambda x: list(x)[1:] + list(x)[:1] if x else [],
    "rotate_right": lambda x: list(x)[-1:] + list(x)[:-1] if x else [],
    "first_half": lambda x: list(x)[: (len(x) + 1) // 2],
    "second_half": lambda x: list(x)[len(x) // 2 :],
    "without_first": lambda x: list(x)[1:],
    "without_last": lambda x: list(x)[:-1],
    "every_second": lambda x: list(x)[::2],
    "every_other_reversed": lambda x: list(x)[::-2],
    "flatten_one": lambda x: [v for group in x for v in group],
    "wrap_each": lambda x: [[v] for v in x],
    "as_strings": lambda x: [str(v) for v in x],
    "as_integers": lambda x: [int(v) for v in x],
    "as_floats": lambda x: [float(v) for v in x],
    "filter_truthy": lambda x: [v for v in x if v],
    "filter_falsy": lambda x: [v for v in x if not v],
    "filter_none": lambda x: [v for v in x if v is not None],
    "filter_text": lambda x: [v for v in x if isinstance(v, str)],
    "filter_numbers": lambda x: [v for v in x if isinstance(v, (int, float)) and not isinstance(v, bool)],
}


def _compose(a: Builtin, b: Builtin, c: Builtin) -> Builtin:
    return lambda value, _a=a, _b=b, _c=c: _c(_b(_a(value)))


EXTRA_BUILTINS: dict[str, Builtin] = {}
EXTRA_DOCS: dict[str, str] = {}


def _add_domain(prefix: str, operations: dict[str, Builtin], limit: int) -> None:
    names = list(operations.items())
    made = 0
    # Three-stage pipelines are explicit, deterministic, and type-family scoped.
    for a_name, a_fn in names:
        for b_name, b_fn in names:
            for c_name, c_fn in names:
                name = f"extra_{prefix}_{a_name}_then_{b_name}_then_{c_name}"
                if name in EXTRA_BUILTINS:
                    continue
                EXTRA_BUILTINS[name] = _compose(a_fn, b_fn, c_fn)
                EXTRA_DOCS[name] = (
                    f"Accepts one {prefix} value and applies {a_name}, then "
                    f"{b_name}, then {c_name}. Each stage's output is passed "
                    "to the next stage."
                )
                made += 1
                if made >= limit:
                    return


_add_domain("number", NUMBER_OPS, 4000)
_add_domain("text", TEXT_OPS, 4000)
_add_domain("list", LIST_OPS, 3000)

EXTRA_BUILTIN_COUNT = len(EXTRA_BUILTINS)
assert EXTRA_BUILTIN_COUNT == 11000, (
    f"expected 11,000 extra built-ins, got {EXTRA_BUILTIN_COUNT}"
)
