import unittest

from tiran import TiranError, compile_tiran
from tiran_stdlib import BUILTIN_COUNT, BUILTINS, get_builtin


class TiranTests(unittest.TestCase):
    def test_luau(self):
        self.assertIn('print("Hello")', compile_tiran('convert luau\nsay "Hello"'))

    def test_python_loop(self):
        out = compile_tiran(
            'convert python\nlet n = 2\nrepeat n:\n    say "x"\nend'
        )
        self.assertIn('for _ in range(n):', out)

    def test_function(self):
        out = compile_tiran(
            'convert javascript\nfunction greet(name):\n    say name\nend\ncall greet("A")'
        )
        self.assertIn('function greet(name)', out)
        self.assertIn('greet("A")', out)

    def test_roblox(self):
        out = compile_tiran(
            'convert luau\ncreate part block\n'
            'set block.name = "X"\nset block.anchored = true'
        )
        self.assertIn('Instance.new("Part")', out)
        self.assertIn('block.Name = "X"', out)
        self.assertIn('block.Anchored = true', out)

    def test_unclosed_block(self):
        with self.assertRaises(TiranError):
            compile_tiran('convert luau\nif true:\n    say "x"')

    def test_unknown_command(self):
        with self.assertRaises(TiranError):
            compile_tiran('convert luau\nthis_is_not_tiran')

    def test_stdlib_exact_count(self):
        self.assertEqual(BUILTIN_COUNT, 11000)
        self.assertEqual(len(BUILTINS), 11000)

    def test_stdlib_has_no_constant_suffix_families(self):
        forbidden_prefixes = {
            "number_add", "number_subtract", "number_multiply", "number_divide",
            "number_mod", "text_repeat", "text_prefix", "text_suffix",
            "list_take", "list_drop", "list_pad",
        }
        for name in BUILTINS:
            parts = name.rsplit("_", 1)
            self.assertFalse(
                len(parts) == 2
                and parts[1].isdigit()
                and parts[0] in forbidden_prefixes,
                name,
            )

    def test_stdlib_real_behavior(self):
        self.assertEqual(get_builtin("number_add")(10, 5), 15)
        self.assertEqual(get_builtin("number_subtract")(10, 5), 5)
        self.assertEqual(get_builtin("number_multiply")(10, 5), 50)
        self.assertEqual(get_builtin("number_divide")(10, 5), 2)
        self.assertEqual(get_builtin("number_mod")(10, 3), 1)
        self.assertEqual(get_builtin("text_repeat")("yo", 3), "yoyoyo")
        self.assertEqual(get_builtin("text_prefix")("TIRAN", 4), "TIRA")
        self.assertEqual(get_builtin("text_suffix")("TIRAN", 4), "IRAN")
        self.assertEqual(get_builtin("list_take")([1, 2, 3], 2), [1, 2])
        self.assertEqual(get_builtin("list_drop")([1, 2, 3], 2), [3])
        self.assertEqual(get_builtin("list_pad")([1], 4, 0), [1, 0, 0, 0])
        self.assertEqual(get_builtin("number_absolute_then_square")(3), 9)
        self.assertEqual(get_builtin("text_trim_then_upper")("  tiran  "), "TIRAN")
        self.assertEqual(get_builtin("list_reverse_then_length")([1, 2, 3]), 3)

    def test_stdlib_missing_name(self):
        with self.assertRaises(KeyError):
            get_builtin("not_a_real_builtin")


if __name__ == "__main__":
    unittest.main()
