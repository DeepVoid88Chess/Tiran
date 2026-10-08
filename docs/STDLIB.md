# TIRAN Standard Library

TIRAN has exactly **11,000 uniquely named built-ins**.

## The important rule

A parameter belongs in the function call, not in the function name.

Bad:

    number_add_5
    number_add_354
    list_drop_2
    list_drop_354

Good:

    number_add(10, 5)
    number_add(10, 354)
    list_drop(items, 2)
    list_drop(items, 354)

There is one number_add, one list_drop, and so on.

## Aglacitivity

**Aglacitive** is a TIRAN design warning for having many separate names for the same operation when the changing value could simply be an argument.

For example, this is aglacitive:

    fart_sniff_1
    fart_sniff_2
    fart_sniff_3
    ...
    fart_sniff_999

Those could be one function:

    fart_sniff(number)

The old TIRAN standard library had this problem with names such as number_add_5 and number_add_354. Those were replaced by parameterized functions such as number_add(number, amount).

Unique compositions are **not** considered aglacitive just because they share smaller operations. For example, number_absolute_then_square is a distinct named pipeline, so it is useful as its own built-in.

## Built-in categories

The registry contains:

- Core general-purpose operations such as abs, length, join, replace, sort, sum, any, and all.
- Parameterized number operations such as number_add, number_subtract, number_multiply, number_divide, and number_mod.
- Parameterized text operations such as text_repeat, text_prefix, and text_suffix.
- Parameterized list operations such as list_take, list_drop, and list_pad.
- Named number, text, and list transforms.
- Named two-step pipelines, such as number_absolute_then_square.
- Named three-step pipelines whose names describe the complete operation sequence.

The pipeline entries are real callables. They are not empty placeholders and they do not hide a numeric constant in their name.

## Examples

    from tiran_stdlib import get_builtin

    get_builtin("number_add")(10, 5)                # 15
    get_builtin("number_mod")(17, 4)                # 1
    get_builtin("text_prefix")("TIRAN", 3)          # "TIR"
    get_builtin("list_drop")([1, 2, 3, 4], 2)       # [3, 4]
    get_builtin("number_absolute_then_square")(-4)  # 16

The registry is verified by tests to contain exactly 11,000 names and to reject the old constant-suffix families.
