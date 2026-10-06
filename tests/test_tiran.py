import unittest

from tiran import TiranError, compile_tiran


class TiranTests(unittest.TestCase):
    def test_luau(self):
        source = '''convert luau
say "Hello"
score = 10
if score > 5:
    say "Good"
else:
    say "Bad"
end
repeat 2:
    say "Loop"
end
'''
        output = compile_tiran(source, "luau")
        self.assertIn('print("Hello")', output)
        self.assertIn("local score = 10", output)
        self.assertIn("if score > 5 then", output)
        self.assertIn("for _ = 1, 2 do", output)

    def test_python(self):
        source = '''convert python
name = "TIRAN"
say name
'''
        output = compile_tiran(source, "python")
        self.assertEqual(output, 'name = "TIRAN"\nprint(name)\n')

    def test_roblox_part(self):
        source = '''convert luau
create part block
set block.name = "Test"
'''
        output = compile_tiran(source, "luau")
        self.assertIn('local block = Instance.new("Part")', output)
        self.assertIn('block.Name = "Test"', output)

    def test_java_is_a_complete_program(self):
        source = '''convert java
say "Hello"
'''
        output = compile_tiran(source, "java")
        self.assertIn("public class Main", output)
        self.assertIn("public static void main", output)
        self.assertIn('System.out.println("Hello");', output)

    def test_bad_target(self):
        with self.assertRaises(TiranError):
            compile_tiran("convert banana\nsay \"x\"", "banana")


if __name__ == "__main__":
    unittest.main()
