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

    def test_stdlib_real_behavior(self):
        self.assertEqual(get_builtin("number_add_5")(10), 15)
        self.assertEqual(get_builtin("number_subtract_5")(10), 5)
        self.assertEqual(get_builtin("number_multiply_5")(10), 50)
        self.assertEqual(get_builtin("number_divide_5")(10), 2)
        self.assertEqual(get_builtin("text_repeat_3")("yo"), "yoyoyo")
        self.assertEqual(get_builtin("text_prefix_4")("TIRAN"), "TIRA")
        self.assertEqual(get_builtin("text_suffix_4")("TIRAN"), "IRAN")
        self.assertEqual(get_builtin("list_take_2")([1, 2, 3]), [1, 2])
        self.assertEqual(get_builtin("list_drop_2")([1, 2, 3]), [3])
        self.assertEqual(get_builtin("list_pad_4")([1], 0), [1, 0, 0, 0])

    def test_stdlib_missing_name(self):
        with self.assertRaises(KeyError):
            get_builtin("not_a_real_builtin")


if __name__ == "__main__":
    unittest.main()
