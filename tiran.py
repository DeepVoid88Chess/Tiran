"""TIRAN - readable, dependency-free source transpiler with Roblox/Luau support."""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

TARGETS={"luau":".luau","lua":".lua","python":".py","javascript":".js","typescript":".ts","java":".java","csharp":".cs","html":".html"}
ALIASES={"js":"javascript","ts":"typescript","cs":"csharp"}
ROBLOX_CLASSES={
    "part":"Part","folder":"Folder","model":"Model","remoteevent":"RemoteEvent",
    "remote_function":"RemoteFunction","bindableevent":"BindableEvent","remote_function":"RemoteFunction",
    "screen_gui":"ScreenGui","screengui":"ScreenGui","frame":"Frame","textlabel":"TextLabel",
    "textbutton":"TextButton","imagelabel":"ImageLabel","imagebutton":"ImageButton",
    "uistroke":"UIStroke","uilistlayout":"UIListLayout","uipadding":"UIPadding",
    "stringvalue":"StringValue","intvalue":"IntValue","numbervalue":"NumberValue",
    "boolvalue":"BoolValue","objectvalue":"ObjectValue","configuration":"Configuration",
}

class TiranError(ValueError):
    pass

def target_name(value):
    value=ALIASES.get(value.strip().lower(),value.strip().lower())
    if value not in TARGETS:
        raise TiranError(f"Unsupported target '{value}'.")
    return value

def expr(value,target):
    value=value.strip()
    if not value:
        raise TiranError("An expression is required.")
    if target=="python":
        value=re.sub(r"\btrue\b","True",value,flags=re.I)
        value=re.sub(r"\bfalse\b","False",value,flags=re.I)
        value=re.sub(r"\b(?:nil|null|nothing)\b","None",value,flags=re.I)
        value=re.sub(r"\b(and|or|not)\b",lambda m:m.group(1),value)
        value=value.replace("~=","!=")
    elif target in {"javascript","typescript","java","csharp"}:
        value=re.sub(r"\btrue\b","true",value,flags=re.I)
        value=re.sub(r"\bfalse\b","false",value,flags=re.I)
        value=re.sub(r"\b(?:nil|null|nothing)\b","null",value,flags=re.I)
        value=re.sub(r"\band\b","&&",value,flags=re.I)
        value=re.sub(r"\bor\b","||",value,flags=re.I)
        value=re.sub(r"\bnot\b","!",value,flags=re.I)
        value=value.replace("~=","!=")
    else:
        value=re.sub(r"\btrue\b","true",value,flags=re.I)
        value=re.sub(r"\bfalse\b","false",value,flags=re.I)
        value=re.sub(r"\b(?:null|nothing)\b","nil",value,flags=re.I)
        value=re.sub(r"\band\b","and",value,flags=re.I)
        value=re.sub(r"\bor\b","or",value,flags=re.I)
        value=re.sub(r"\bnot\b","not",value,flags=re.I)
    return value

def valid_name(name,line):
    if not re.fullmatch(r"[A-Za-z_]\w*",name):
        raise TiranError(f"Line {line}: invalid name '{name}'.")
    return name

def roblox_prop(path):
    parts=path.split(".")
    return ".".join(parts[:-1]+[parts[-1][0].upper()+parts[-1][1:]])

class Compiler:
    def __init__(self,target):
        self.target=target_name(target)
        self.lines=[]
        self.blocks=[]
        self.declared=set()
        self.imports=[]

    def emit(self,text,depth=None):
        d=len(self.blocks) if depth is None else depth
        self.lines.append("    "*d+text)

    def require_luau(self,n,feature):
        if self.target!="luau":
            raise TiranError(f"Line {n}: {feature} requires convert luau.")

    def say(self,v):
        v=expr(v,self.target)
        if self.target=="html":
            if len(v)>=2 and v[0]==v[-1] and v[0] in {"\"","'"}:
                text=v[1:-1].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                self.emit(f"<p>{text}</p>")
            else:
                raise TiranError("HTML target supports literal say statements only.")
        elif self.target in {"luau","lua","python","javascript","typescript"}:
            self.emit(f"print({v})")
        elif self.target=="java":
            self.emit(f"System.out.println({v});")
        else:
            self.emit(f"Console.WriteLine({v});")

    def assign(self,name,value,line):
        if self.target=="html":
            raise TiranError(f"Line {line}: variables are not supported by the HTML target.")
        valid_name(name,line)
        value=expr(value,self.target)
        new=name not in self.declared
        if self.target in {"luau","lua"}:
            self.emit(("local " if new else "")+f"{name} = {value}")
        elif self.target=="python":
            self.emit(f"{name} = {value}")
        elif self.target in {"javascript","typescript"}:
            self.emit(("let " if new else "")+f"{name} = {value};")
        else:
            self.emit(("var " if new else "")+f"{name} = {value};")
        self.declared.add(name)

    def begin(self,kind,head,line):
        if self.target=="html":
            raise TiranError(f"Line {line}: control flow is not supported by the HTML target.")
        h=expr(head,self.target)
        if kind=="if":
            self.emit(f"if {h} then" if self.target in {"luau","lua"} else f"if {h}:" if self.target=="python" else f"if ({h}) {{")
        elif kind=="repeat":
            if self.target in {"luau","lua"}: self.emit(f"for _ = 1, {h} do")
            elif self.target=="python": self.emit(f"for _ in range({h}):")
            else: self.emit(f"for (let i = 0; i < {h}; i++) {{")
        elif kind=="while":
            self.emit(f"while {h} do" if self.target in {"luau","lua"} else f"while {h}:" if self.target=="python" else f"while ({h}) {{")
        self.blocks.append(kind)

    def function(self,text,line):
        if self.target=="html":
            raise TiranError(f"Line {line}: functions are not supported by the HTML target.")
        m=re.fullmatch(r"([A-Za-z_]\w*)\((.*)\)",text.strip())
        if not m:
            raise TiranError(f"Line {line}: use function name(args):")
        name=valid_name(m.group(1),line)
        args=[valid_name(x.strip(),line) for x in m.group(2).split(",") if x.strip()]
        a=", ".join(args)
        if self.target in {"luau","lua"}: self.emit(f"function {name}({a})")
        elif self.target=="python": self.emit(f"def {name}({a}):")
        elif self.target in {"javascript","typescript"}: self.emit(f"function {name}({a}) {{")
        elif self.target=="java": self.emit(f"static Object {name}({', '.join('Object '+x for x in args)}) {{")
        else: self.emit(f"static object {name}({', '.join('object '+x for x in args)}) {{")
        self.blocks.append("function")

    def statement(self,line,n):
        if line.startswith("say "): return self.say(line[4:])
        m=re.fullmatch(r"let\s+([A-Za-z_]\w*)\s*=\s*(.+)",line)
        if m: return self.assign(m.group(1),m.group(2),n)
        m=re.fullmatch(r"([A-Za-z_]\w*)\s*=\s*(.+)",line)
        if m: return self.assign(m.group(1),m.group(2),n)
        for kind,prefix in (("if","if "),("repeat","repeat "),("while","while ")):
            if line.startswith(prefix) and line.endswith(":"):
                return self.begin(kind,line[len(prefix):-1],n)
        if line.startswith("function ") and line.endswith(":"): return self.function(line[9:-1],n)
        if line.startswith("elseif ") and line.endswith(":"):
            if not self.blocks or self.blocks[-1]!="if": raise TiranError(f"Line {n}: elseif must follow if.")
            d=len(self.blocks)-1; h=expr(line[7:-1],self.target)
            self.emit(f"elseif {h} then" if self.target in {"luau","lua"} else f"elif {h}:" if self.target=="python" else f"}} else if ({h}) {{",d); return
        if line=="else:":
            if not self.blocks or self.blocks[-1]!="if": raise TiranError(f"Line {n}: else must follow if.")
            d=len(self.blocks)-1; self.emit("else" if self.target in {"luau","lua"} else "else:" if self.target=="python" else "} else {",d); return
        if line=="end":
            if not self.blocks: raise TiranError(f"Line {n}: unexpected end.")
            kind=self.blocks.pop()
            if self.target in {"luau","lua"}:
                if kind=="try" and self.target=="luau":
                    self.emit("end)",len(self.blocks))
                else:
                    self.emit("end",len(self.blocks))
            elif self.target!="python":
                self.emit("}",len(self.blocks))
            return
        if line in {"break","continue"}:
            if self.target=="html": raise TiranError(f"Line {n}: {line} is not supported by the HTML target.")
            self.emit(line+";" if self.target in {"java","csharp"} else line); return
        if line.startswith("return"):
            if self.target=="html": raise TiranError(f"Line {n}: return is not supported by the HTML target.")
            v=line[6:].strip()
            self.emit("return"+((" "+expr(v,self.target)) if v else "")+(";" if self.target in {"java","csharp"} else "")); return
        m=re.fullmatch(r"call\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\((.*)\)",line)
        if m:
            self.emit(f"{m.group(1)}({expr(m.group(2),self.target)})"+(";" if self.target in {"java","csharp"} else "")); return
        m=re.fullmatch(r"import\s+([A-Za-z_]\w*)(?:\s+as\s+([A-Za-z_]\w*))?",line)
        if m:
            module,alias=m.group(1),m.group(2) or m.group(1)
            if self.target=="luau": self.emit(f'local {alias} = require(script.Parent.{module})')
            elif self.target=="python": self.emit(f"import {module} as {alias}" if alias!=module else f"import {module}")
            elif self.target in {"javascript","typescript"}: self.emit(f'import {alias} from "./{module}"'+(";"))
            else: self.emit(f"// import {module}")
            self.imports.append(module); return
        if line=="try:":
            if self.target=="luau": self.emit("local __tiran_ok, __tiran_result = pcall(function()")
            elif self.target=="python": self.emit("try:")
            elif self.target in {"javascript","typescript"}: self.emit("try {")
            else: self.emit("try {")
            self.blocks.append("try"); return
        if line.startswith("catch") and line.endswith(":"):
            if not self.blocks or self.blocks[-1]!="try": raise TiranError(f"Line {n}: catch must follow try.")
            d=len(self.blocks)-1
            arg=line[5:-1].strip() or "error"
            if self.target=="luau":\n                self.emit("end",d)\n                self.emit(f"if not __tiran_ok then",d)
            elif self.target=="python": self.emit("except Exception as "+arg+":",d)
            else: self.emit("} catch (Exception "+arg+") {",d)
            return
        m=re.fullmatch(r"connect\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s+to\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)",line)
        if m:
            self.require_luau(n,"connect"); self.emit(f"{m.group(1)}:Connect({m.group(2)})"); return
        m=re.fullmatch(r"disconnect\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)",line)
        if m:
            self.require_luau(n,"disconnect"); self.emit(f"{m.group(1)}:Disconnect()"); return
        m=re.fullmatch(r"destroy\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)",line)
        if m:
            self.require_luau(n,"destroy"); self.emit(f"{m.group(1)}:Destroy()"); return
        m=re.fullmatch(r"wait(?:\s+(.+))?",line)
        if m:
            self.require_luau(n,"wait"); self.emit("task.wait("+ (expr(m.group(1),self.target) if m.group(1) else "") +")"); return
        m=re.fullmatch(r"fire\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*(.*)",line)
        if m:
            self.require_luau(n,"fire"); args=m.group(2).strip()
            self.emit(f"{m.group(1)}:FireServer({args})" if args else f"{m.group(1)}:FireServer()"); return
        m=re.fullmatch(r"invoke\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*(.*)",line)
        if m:
            self.require_luau(n,"invoke"); args=m.group(2).strip()
            self.emit(f"{m.group(1)}:InvokeServer({args})" if args else f"{m.group(1)}:InvokeServer()"); return
        m=re.fullmatch(r"service\s+([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)",line)
        if m:
            self.require_luau(n,"service"); self.emit(f'local {m.group(1)} = game:GetService("{m.group(2)}")'); self.declared.add(m.group(1)); return
        m=re.fullmatch(r"create\s+([A-Za-z_]\w*)\s+([A-Za-z_]\w*)",line,re.I)
        if m and m.group(1).lower() in ROBLOX_CLASSES:
            self.require_luau(n,"create"); cls=ROBLOX_CLASSES[m.group(1).lower()]
            self.emit(f'local {m.group(2)} = Instance.new("{cls}")'); self.declared.add(m.group(2)); return
        m=re.fullmatch(r"parent\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s+to\s+(.+)",line)
        if m:
            self.require_luau(n,"parent"); self.emit(f"{m.group(1)}.Parent = {expr(m.group(2),self.target)}"); return
        m=re.fullmatch(r"set\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*=\s*(.+)",line)
        if m:
            self.require_luau(n,"set"); self.emit(f"{roblox_prop(m.group(1))} = {expr(m.group(2),self.target)}"); return
        m=re.fullmatch(r"vector3\s+([A-Za-z_]\w*)\s*=\s*(.+)",line)
        if m:
            self.require_luau(n,"vector3"); self.emit(f"local {m.group(1)} = Vector3.new({m.group(2)})"); self.declared.add(m.group(1)); return
        m=re.fullmatch(r"cframe\s+([A-Za-z_]\w*)\s*=\s*(.+)",line)
        if m:
            self.require_luau(n,"cframe"); self.emit(f"local {m.group(1)} = CFrame.new({m.group(2)})"); self.declared.add(m.group(1)); return
        m=re.fullmatch(r"players\s+([A-Za-z_]\w*)\s*=\s*(.+)",line)
        if m:
            self.require_luau(n,"players"); self.emit(f"local {m.group(1)} = Players:{m.group(2)}"); self.declared.add(m.group(1)); return
        raise TiranError(f"Line {n}: unknown TIRAN command: {line}")

    def finish(self):
        if self.blocks: raise TiranError(f"Unclosed block: {self.blocks[-1]}.")
        return "\n".join(self.lines)+"\n"

def compile_tiran(source,target=None):
    if target is None:
        m=re.search(r"^\s*convert\s+([\w+-]+)\s*$",source,re.M|re.I)
        if not m: raise TiranError("No target selected. Add 'convert <language>' or use --target.")
        target=m.group(1)
    target=target_name(target)
    c=Compiler(target)
    for n,raw in enumerate(source.splitlines(),1):
        line=raw.strip()
        if not line or line.startswith("#") or line.lower().startswith("convert "): continue
        c.statement(line,n)
    return c.finish()

def format_tiran(source):
    out=[]
    depth=0
    for raw in source.splitlines():
        line=raw.strip()
        if not line: 
            if out and out[-1]!="": out.append("")
            continue
        if line in {"end","else:"} or line.startswith("elseif ") or line.startswith("catch"):
            depth=max(0,depth-1)
        out.append("    "*depth+line)
        if line.endswith(":") and not line.startswith("#") and not line.startswith("convert "):
            if line.startswith(("if ","elseif ","else","repeat ","while ","function ","try","catch")): depth+=1
    return "\n".join(out).rstrip()+"\n"

def main():
    p=argparse.ArgumentParser(prog="tiran",description="Compile and format TIRAN source.")
    p.add_argument("source",nargs="?")
    p.add_argument("-o","--output")
    p.add_argument("-t","--target")
    p.add_argument("--format",action="store_true")
    args=p.parse_args()
    if not args.source:
        p.error("source file is required")
    path=Path(args.source)
    try:
        source=path.read_text(encoding="utf-8")
        if args.format:
            result=format_tiran(source)
        else:
            result=compile_tiran(source,args.target)
        if args.output:
            Path(args.output).write_text(result,encoding="utf-8")
        else:
            print(result,end="")
        return 0
    except (OSError,TiranError) as e:
        print(f"TIRAN ERROR: {e}",file=sys.stderr)
        return 1

if __name__=="__main__":
    raise SystemExit(main())
