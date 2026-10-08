import unittest

from tiran import TiranError, compile_tiran, format_tiran
from tiran_stdlib import BUILTIN_COUNT, BUILTINS, get_builtin
from tiran_syntax import ParseError, parse_tiran


class TiranTests(unittest.TestCase):

    def test_syntax_tree(self):
        program = parse_tiran("""convert luau
if true:
    say "x"
end""")
        self.assertEqual(program.target, "luau")
        self.assertEqual(program.nodes[0].kind, "if")
        self.assertEqual(program.nodes[0].children[0].text, 'say "x"')

    def test_unexpected_end_is_parser_error(self):
        with self.assertRaises(ParseError):
            parse_tiran("convert luau\nend")


    def test_expression_ast(self):
        program = parse_tiran('convert luau\nlet values = [1, 2, 3]\nlet player = game.Players.LocalPlayer\n')
        first = program.nodes[0].expression
        self.assertEqual(first.kind, "list")
        self.assertEqual(len(first.children), 3)
        second = program.nodes[1].expression
        self.assertEqual(second.kind, "member")
        self.assertEqual(second.value, "LocalPlayer")

    def test_expression_parser_rejects_bad_syntax(self):
        with self.assertRaises(ParseError):
            parse_tiran("convert luau\nlet value = 1 + * 2")

    def test_target_mismatch(self):
        with self.assertRaises(TiranError):
            compile_tiran('convert luau\nsay "x"', target="python")

    def test_luau(self):
        self.assertIn('print("Hello")', compile_tiran('convert luau\nsay "Hello"'))

    def test_ast_expression_lowering(self):
        source = """convert luau
let values = [1, 2, 3]
let profile = {"name": "Jackson", "level": 5}
let score = values[0] + values[1] * 2
let player = game.Players.LocalPlayer
"""
        out = compile_tiran(source)
        self.assertIn("local values = {1, 2, 3}", out)
        self.assertIn('local profile = {["name"] = "Jackson", ["level"] = 5}', out)
        self.assertIn("local score = (values[0] + (values[1] * 2))", out)
        self.assertIn("local player = game.Players.LocalPlayer", out)

    def test_multi_argument_call_uses_ast(self):
        out = compile_tiran('convert luau\ncall math.max(1, 2, 3)')
        self.assertIn("math.max(1, 2, 3)", out)

    def test_expression_target_lowering(self):
        out = compile_tiran('convert python\nlet ok = true and not false\nlet power = 2 ^ 3')
        self.assertIn("ok = (True and (not False))", out)
        self.assertIn("power = (2 ** 3)", out)
    def test_python_loop(self):
        out=compile_tiran('convert python\nlet n = 2\nrepeat n:\n    say "x"\nend')
        self.assertIn('for _ in range(n):',out)

    def test_function(self):
        out=compile_tiran('convert javascript\nfunction greet(name):\n    say name\nend\ncall greet("A")')
        self.assertIn('function greet(name)',out)
        self.assertIn('greet("A")',out)

    def test_roblox(self):
        out=compile_tiran('convert luau\ncreate part block\nset block.name = "X"\nset block.anchored = true\nfunction onTouched(hit):\n    say hit\nend\nconnect block.Touched to onTouched\nwait 1\ndestroy block')
        self.assertIn('Instance.new("Part")',out)
        self.assertIn('block.Name = "X"',out)
        self.assertIn('block.Anchored = true',out)
        self.assertIn('block.Touched:Connect(onTouched)',out)
        self.assertIn('task.wait(1)',out)
        self.assertIn('block:Destroy()',out)

    def test_roblox_instance_types(self):
        out=compile_tiran('convert luau\ncreate folder folder1\ncreate model model1\ncreate remoteevent event1\ncreate remote_function fn1\ncreate bindableevent signal1\ncreate frame ui')
        self.assertIn('Instance.new("Folder")',out)
        self.assertIn('Instance.new("Model")',out)
        self.assertIn('Instance.new("RemoteEvent")',out)
        self.assertIn('Instance.new("RemoteFunction")',out)
        self.assertIn('Instance.new("BindableEvent")',out)
        self.assertIn('Instance.new("Frame")',out)

    def test_roblox_api_helpers(self):
        out=compile_tiran('convert luau\nservice Players = Players\ncreate remoteevent event\nvector3 spawn = 0, 5, 0\ncframe cf = 0, 0, 0\nset spawn = Vector3.new(0, 5, 0)\nparent event to workspace\nfire event "hello"\ninvoke event "request"')
        self.assertIn('game:GetService("Players")',out)
        self.assertIn('Vector3.new(0, 5, 0)',out)
        self.assertIn('CFrame.new(0, 0, 0)',out)
        self.assertIn('event.Parent = workspace',out)
        self.assertIn('event:FireServer("hello")',out)
        self.assertIn('event:InvokeServer("request")',out)

    def test_nested_properties(self):
        out=compile_tiran('convert luau\nset player.Character.Humanoid.WalkSpeed = 20')
        self.assertIn('player.Character.Humanoid.WalkSpeed = 20',out)

    def test_elseif(self):
        out=compile_tiran('convert luau\nif false:\n    say "a"\nelseif true:\n    say "b"\nelse:\n    say "c"\nend')
        self.assertIn('elseif true then',out)

    def test_modules(self):
        out=compile_tiran('convert luau\nimport Inventory as Inv')
        self.assertIn('local Inv = require(script.Parent.Inventory)',out)

    def test_error_handling(self):
        out=compile_tiran('convert python\ntry:\n    say "x"\ncatch error:\n    say error\nend')
        self.assertIn('try:',out)
        self.assertIn('except Exception as error:',out)

    def test_formatter(self):
        src='convert luau\nif true:\n say "x"\nend'
        self.assertEqual(format_tiran(src),'convert luau\nif true:\n    say "x"\nend\n')

    def test_unclosed_block(self):
        with self.assertRaises(TiranError):
            compile_tiran('convert luau\nif true:\n    say "x"')

    def test_unknown_command(self):
        with self.assertRaises(TiranError):
            compile_tiran('convert luau\nthis_is_not_tiran')

    def test_stdlib_exact_count(self):
        self.assertEqual(BUILTIN_COUNT,11000)
        self.assertEqual(len(BUILTINS),11000)

    def test_stdlib_has_no_constant_suffix_families(self):
        forbidden_prefixes={"number_add","number_subtract","number_multiply","number_divide","number_mod","text_repeat","text_prefix","text_suffix","list_take","list_drop","list_pad"}
        for name in BUILTINS:
            parts=name.rsplit("_",1)
            self.assertFalse(len(parts)==2 and parts[1].isdigit() and parts[0] in forbidden_prefixes,name)

    def test_stdlib_real_behavior(self):
        self.assertEqual(get_builtin("number_add")(10,5),15)
        self.assertEqual(get_builtin("number_subtract")(10,5),5)
        self.assertEqual(get_builtin("number_multiply")(10,5),50)
        self.assertEqual(get_builtin("number_divide")(10,5),2)
        self.assertEqual(get_builtin("number_mod")(10,3),1)
        self.assertEqual(get_builtin("text_repeat")("yo",3),"yoyoyo")
        self.assertEqual(get_builtin("text_prefix")("TIRAN",4),"TIRA")
        self.assertEqual(get_builtin("text_suffix")("TIRAN",4),"IRAN")
        self.assertEqual(get_builtin("list_take")([1,2,3],2),[1,2])
        self.assertEqual(get_builtin("list_drop")([1,2,3],2),[3])
        self.assertEqual(get_builtin("list_pad")([1],4,0),[1,0,0,0])
        self.assertEqual(get_builtin("number_absolute_then_square")(3),9)
        self.assertEqual(get_builtin("text_trim_then_upper")("  tiran  "),"TIRAN")
        self.assertEqual(get_builtin("list_reverse_then_length")([1,2,3]),3)

    def test_tiran_builtins_compile_to_python_runtime_calls(self):
        source = """convert python
let added = number_add(10, 5)
let cleaned = text_trim_then_upper("  tiran  ")
call list_take([1, 2, 3], 2)
"""
        out = compile_tiran(source)
        self.assertIn("from tiran_stdlib import get_builtin as __tiran_builtin", out)
        self.assertIn('__tiran_builtin("number_add")(10, 5)', out)
        self.assertIn('__tiran_builtin("text_trim_then_upper")("  tiran  ")', out)
        self.assertIn('__tiran_builtin("list_take")([1, 2, 3])', out)

    def test_compiled_python_executes_tiran_builtins(self):
        source = """convert python
let added = number_add(10, 5)
let cleaned = text_trim_then_upper("  tiran  ")
let picked = list_take([1, 2, 3], 2)
"""
        namespace = {}
        exec(compile_tiran(source), namespace)
        self.assertEqual(namespace["added"], 15)
        self.assertEqual(namespace["cleaned"], "TIRAN")
        self.assertEqual(namespace["picked"], [1, 2])

    def test_stdlib_missing_name(self):
        with self.assertRaises(KeyError):
            get_builtin("not_a_real_builtin")


if __name__=="__main__":
    unittest.main()
