"""TIRAN v1.0 - readable, dependency-free transpiler."""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

TARGETS={"luau":".luau","lua":".lua","python":".py","javascript":".js","typescript":".ts","java":".java","csharp":".cs","html":".html"}
ALIASES={"js":"javascript","ts":"typescript","cs":"csharp"}

class TiranError(ValueError): pass

def target_name(value):
    value=ALIASES.get(value.strip().lower(),value.strip().lower())
    if value not in TARGETS: raise TiranError(f"Unsupported target '{value}'.")
    return value

def expr(value,target):
    value=value.strip()
    if not value: raise TiranError("An expression is required.")
    if target=="python":
        value=re.sub(r"\btrue\b","True",value,flags=re.I)
        value=re.sub(r"\bfalse\b","False",value,flags=re.I)
        value=re.sub(r"\b(?:nil|null|nothing)\b","None",value,flags=re.I)
    elif target in {"javascript","typescript","java","csharp"}:
        value=re.sub(r"\btrue\b","true",value,flags=re.I)
        value=re.sub(r"\bfalse\b","false",value,flags=re.I)
        value=re.sub(r"\b(?:nil|null|nothing)\b","null",value,flags=re.I)
        value=re.sub(r"\band\b","&&",value); value=re.sub(r"\bor\b","||",value)
    else:
        value=re.sub(r"\btrue\b","true",value,flags=re.I)
        value=re.sub(r"\bfalse\b","false",value,flags=re.I)
        value=re.sub(r"\b(?:null|nothing)\b","nil",value,flags=re.I)
    return value

def valid_name(name,line):
    if not re.fullmatch(r"[A-Za-z_]\w*",name):
        raise TiranError(f"Line {line}: invalid name '{name}'.")
    return name

class Compiler:
    def __init__(self,target):
        self.target=target_name(target); self.lines=[]; self.blocks=[]; self.declared=set()
    def emit(self,text,depth=None):
        d=len(self.blocks) if depth is None else depth
        self.lines.append("    "*d+text)
    def say(self,v):
        v=expr(v,self.target)
        if self.target=="html":
            if len(v)>=2 and v[0]==v[-1] and v[0] in {"\\\"","\\\'"}:
                text=v[1:-1].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                self.emit(f"<p>{text}</p>")
            else:
                raise TiranError("HTML target supports literal say statements only.")
        elif self.target in {"luau","lua","python","javascript","typescript"}: self.emit(f"print({v})")
        elif self.target=="java": self.emit(f"System.out.println({v});")
        else: self.emit(f"Console.WriteLine({v});")
    def assign(self,name,value,line):
        if self.target=="html": raise TiranError(f"Line {line}: variables are not supported by the HTML target.")
        valid_name(name,line); value=expr(value,self.target); new=name not in self.declared
        if self.target in {"luau","lua"}: self.emit(("local " if new else "")+f"{name} = {value}")
        elif self.target=="python": self.emit(f"{name} = {value}")
        elif self.target in {"javascript","typescript"}: self.emit(("let " if new else "")+f"{name} = {value};")
        else: self.emit(("var " if new else "")+f"{name} = {value};")
        self.declared.add(name)
    def begin(self,kind,head,line):
        if self.target=="html": raise TiranError(f"Line {line}: control flow is not supported by the HTML target.")
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
        if self.target=="html": raise TiranError(f"Line {line}: functions are not supported by the HTML target.")
        m=re.fullmatch(r"([A-Za-z_]\w*)\((.*)\)",text.strip())
        if not m: raise TiranError(f"Line {line}: use function name(args):")
        name=valid_name(m.group(1),line); args=[valid_name(x.strip(),line) for x in m.group(2).split(",") if x.strip()]
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
        if line.startswith("if ") and line.endswith(":"): return self.begin("if",line[3:-1],n)
        if line.startswith("repeat ") and line.endswith(":"): return self.begin("repeat",line[7:-1],n)
        if line.startswith("while ") and line.endswith(":"): return self.begin("while",line[6:-1],n)
        if line.startswith("function ") and line.endswith(":"): return self.function(line[9:-1],n)
        if line=="else:":
            if not self.blocks or self.blocks[-1]!="if": raise TiranError(f"Line {n}: else must follow if.")
            d=len(self.blocks)-1
            self.emit("else" if self.target in {"luau","lua"} else "else:" if self.target=="python" else "} else {",d); return
        if line=="end":
            if self.target=="html": raise TiranError(f"Line {n}: end is not valid for the HTML target.")
            if not self.blocks: raise TiranError(f"Line {n}: unexpected end.")
            self.blocks.pop()
            if self.target in {"luau","lua"}: self.emit("end",len(self.blocks))
            elif self.target!="python": self.emit("}",len(self.blocks))
            return
        if line=="break":
            if self.target=="html": raise TiranError(f"Line {n}: break is not supported by the HTML target.")
            return self.emit("break; " if self.target in {"java","csharp"} else "break")
        if line=="continue":
            if self.target=="html": raise TiranError(f"Line {n}: continue is not supported by the HTML target.")
            return self.emit("continue; " if self.target in {"java","csharp"} else "continue")
        if line.startswith("return"):
            if self.target=="html": raise TiranError(f"Line {n}: return is not supported by the HTML target.")
            v=line[6:].strip(); self.emit("return"+((" "+expr(v,self.target)) if v else "")+(";" if self.target in {"java","csharp"} else "")); return
        m=re.fullmatch(r"call\s+([A-Za-z_]\w*)\((.*)\)",line)
        if m: return self.emit(f"{m.group(1)}({m.group(2)})"+(";" if self.target in {"java","csharp"} else ""))
        m=re.fullmatch(r"create part\s+([A-Za-z_]\w*)",line)
        if m:
            if self.target!="luau": raise TiranError(f"Line {n}: create part requires convert luau.")
            self.emit(f'local {m.group(1)} = Instance.new("Part")'); self.declared.add(m.group(1)); return
        m=re.fullmatch(r"service\s+([A-Za-z_]\w*)\s*=\s*(.+)",line)
        if m:
            if self.target!="luau": raise TiranError(f"Line {n}: service requires convert luau.")
            self.emit(f'local {m.group(1)} = game:GetService("{m.group(2).strip()}")'); self.declared.add(m.group(1)); return
        m=re.fullmatch(r"set\s+([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s*=\s*(.+)",line[4:] if line.startswith("set ") else "")
        if m:
            if self.target not in {"luau","lua"}: raise TiranError(f"Line {n}: set requires Luau or Lua.")
            self.emit(f"{m.group(1)}.{m.group(2)[0].upper()+m.group(2)[1:]} = {expr(m.group(3),self.target)}"); return
        raise TiranError(f"Line {n}: unknown TIRAN command: {line}")
    def finish(self):
        if self.blocks: raise TiranError(f"Unclosed block: {self.blocks[-1]}.")
        return "\n".join(self.lines)+"\n"

def wrap(body,target):
    if target not in {"java","csharp"}: return body
    lines=body.rstrip().splitlines(); funcs=[]; main=[]; i=0
    while i<len(lines):
        if lines[i].lstrip().startswith(("static Object ","static object ")):
            f=[lines[i]]; depth=lines[i].count("{")-lines[i].count("}"); i+=1
            while i<len(lines) and depth: f.append(lines[i]); depth+=lines[i].count("{")-lines[i].count("}"); i+=1
            funcs+=f+[""]
        else: main.append(lines[i]); i+=1
    if target=="java": head=["public class Main {"]; tail=["    public static void main(String[] args) {","    }","}"]
    else: head=["using System;","","public class Program {"]; tail=["    public static void Main() {","    }","}"]
    return "\n".join(head+["    "+x if x else "" for x in funcs]+["        "+x for x in main[:0]]+["    public static void main(String[] args) {" if target=="java" else "    public static void Main() {"]+["        "+x for x in main]+["    }","}",""])

def compile_tiran(source,target=None):
    if target is None:
        m=re.search(r"^\s*convert\s+([\w+-]+)\s*$",source,re.M|re.I)
        if not m: raise TiranError("No target selected. Add 'convert <language>' or use --target.")
        target=m.group(1)
    target=target_name(target); c=Compiler(target)
    for n,raw in enumerate(source.splitlines(),1):
        line=raw.strip()
        if not line or line.startswith("#"): continue
        if line.lower().startswith("convert "):
            if target_name(line[8:])!=target: raise TiranError(f"Line {n}: target mismatch.")
            continue
        c.statement(line,n)
    return wrap(c.finish(),target)

def main():
    p=argparse.ArgumentParser(prog="tiran",description="Compile TIRAN into real source code.")
    p.add_argument("source"); p.add_argument("-t","--target"); p.add_argument("-o","--output")
    a=p.parse_args()
    try:
        result=compile_tiran(Path(a.source).read_text(encoding="utf-8"),a.target)
        if a.output: Path(a.output).write_text(result,encoding="utf-8"); print(f"Compiled {a.source} -> {a.output}")
        else: sys.stdout.write(result)
        return 0
    except (OSError,TiranError) as e:
        print(f"TIRAN ERROR: {e}",file=sys.stderr); return 1

if __name__=="__main__": raise SystemExit(main())
