import unittest
from tiran import TiranError, compile_tiran

class TiranTests(unittest.TestCase):
    def test_luau(self):
        self.assertIn('print("Hello")', compile_tiran('convert luau\nsay "Hello"'))
    def test_python_loop(self):
        out=compile_tiran('convert python\nlet n = 2\nrepeat n:\n    say "x"\nend')
        self.assertIn('for _ in range(n):',out)
    def test_function(self):
        out=compile_tiran('convert javascript\nfunction greet(name):\n    say name\nend\ncall greet("A")')
        self.assertIn('function greet(name)',out)
        self.assertIn('greet("A")',out)
    def test_roblox(self):
        out=compile_tiran('convert luau\ncreate part block\nset block.name = "X"\nset block.anchored = true')
        self.assertIn('Instance.new("Part")',out)
        self.assertIn('block.Name = "X"',out)
        self.assertIn('block.Anchored = true',out)
    def test_unclosed_block(self):
        with self.assertRaises(TiranError):
            compile_tiran('convert luau\nif true:\n    say "x"')
    def test_unknown_command(self):
        with self.assertRaises(TiranError):
            compile_tiran('convert luau\nthis_is_not_tiran')

if __name__ == "__main__":
    unittest.main()
