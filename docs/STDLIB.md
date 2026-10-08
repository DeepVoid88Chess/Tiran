# TIRAN Standard Library

TIRAN ships exactly 11,000 callable built-ins in tiran_stdlib.py.

## Core functions

The 23 core functions are:

- abs
- min
- max
- round
- floor
- ceil
- sqrt
- pow
- length
- lower
- upper
- trim
- contains
- starts_with
- ends_with
- join
- split
- replace
- reverse
- sort
- sum
- any
- all

## Generated families

The remaining 10,977 functions are parameterized family members.

| Family | Entries | Example | Meaning |
|---|---:|---|---|
| number_add | 1000 | number_add_12(x) | x + 12 |
| number_subtract | 1000 | number_subtract_12(x) | x - 12 |
| number_multiply | 1000 | number_multiply_12(x) | x * 12 |
| number_divide | 1000 | number_divide_12(x) | x / 12 |
| text_repeat | 1000 | text_repeat_3(x) | repeat text 3 times |
| text_prefix | 1000 | text_prefix_4(x) | first 4 characters |
| text_suffix | 1000 | text_suffix_4(x) | last 4 characters |
| list_take | 1000 | list_take_4(x) | first 4 items |
| list_drop | 1000 | list_drop_4(x) | remove first 4 items |
| list_pad | 1000 | list_pad_4(x, v) | pad to at least 4 items |
| number_mod | 977 | number_mod_7(x) | x modulo 7 |

Every entry is created as a callable with its own captured parameter. Division and modulo by zero deliberately raise an error rather than silently returning a fake result.

## Using the library

    from tiran_stdlib import BUILTINS, get_builtin

    print(len(BUILTINS))
    print(get_builtin("number_add_5")(10))
    print(get_builtin("text_repeat_3")("TIRAN"))

The registry performs duplicate-name checks and asserts its final count at import time.
