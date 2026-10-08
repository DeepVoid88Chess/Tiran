# TIRAN Error Codes

Stable codes identify compiler diagnostics in tests, terminal output, editors, and bug reports. Each entry explains the problem and gives a suggested next step.

| Code | Error | Meaning | Suggested fix |
|---|---|---|---|
| E1001 | Unexpected end | An end statement has no open block. | Remove the extra end or open the intended block. |
| E1002 | Unclosed block | A block was opened but never closed. | Add end after the block's final statement. |
| E1003 | Branch without block | else, elseif, or catch has no matching open block. | Place the branch inside its matching if or try block. |
| E1004 | Invalid branch | This branch is not valid at this position. | Check branch order and matching block type. |
| E1005 | Malformed expression | The expression could not be parsed. | Check operators, brackets, commas, and operand order. |
| E1006 | Missing expression | This statement requires an expression. | Add a value or condition after the statement keyword. |
| E1007 | Multiple targets | More than one convert directive was found. | Keep one convert directive at the top of the file. |
| E1008 | Missing target | No output language was selected. | Add convert luau or pass --target. |
| E1009 | Malformed function | The function declaration is not valid TIRAN syntax. | Use function name(arg1, arg2): |
| E1010 | Invalid identifier | An identifier does not follow TIRAN naming rules. | Start with a letter or underscore and use letters, digits, or underscores. |
| E1011 | Unknown statement | The compiler does not recognize this statement. | Check spelling or consult the language specification. |
| E1012 | Unexpected token | A token appeared where it is not allowed. | Remove the token or add the missing syntax before it. |
| E1013 | Unterminated string | A quoted string was not closed. | Add the matching quote. |
| E1014 | Unmatched delimiter | A bracket or parenthesis is unmatched. | Pair every opening delimiter with a closing delimiter. |
| E1015 | Invalid call | A call statement must contain a valid call expression. | Use call function_name(arguments). |
| E1016 | Invalid assignment | The assignment target or value is invalid. | Use name = expression. |
| E1017 | Duplicate directive | A source directive was declared more than once. | Keep only one directive of this kind. |
| E1018 | Invalid import | The import statement is malformed. | Use import Module or import Module as Alias. |
| E1019 | Invalid catch | catch must directly follow an open try block. | Use try:, then catch name:, then end. |
| E1020 | Invalid block close | The closing statement does not match an open block. | Check the nesting of end statements. |
| E2001 | Unsupported target | The requested output language is not supported. | Choose luau, lua, python, javascript, typescript, java, csharp, or html. |
| E2002 | Target mismatch | The source target differs from the requested target. | Make convert and --target agree. |
| E2003 | Feature unavailable for target | This TIRAN feature requires a different output target. | Compile with the target named in the diagnostic. |
| E2004 | Unsupported expression | This expression form cannot be emitted for the selected target. | Rewrite the expression using supported target syntax. |
| E2005 | Unsupported statement | This statement cannot be emitted for the selected target. | Use a supported statement or select another target. |
| E2006 | Invalid target literal | A literal cannot be represented with this target mapping. | Use a target-supported value. |
| E2007 | Invalid property path | A property path is malformed. | Use a dotted path such as player.Character.Name. |
| E2008 | Invalid Roblox class | The requested Roblox class is not in the compiler's class map. | Use a supported class name or add it to the compiler map. |
| E2009 | Invalid Roblox helper | A Roblox helper statement is malformed. | Check the helper's documented syntax. |
| E2010 | Invalid module target | This import form is not supported for the selected target. | Use the target's native module system. |
| E3001 | Unknown built-in | The requested name is not in the TIRAN built-in registry. | Check spelling or search the built-in catalog. |
| E3002 | Built-in target limitation | The registered Python runtime built-in cannot be emitted natively for this target. | Use a target-native equivalent or compile to Python. |
| E3003 | Built-in argument error | A built-in received an invalid argument. | Check the documented parameters and value types. |
| E3004 | Built-in value error | A built-in cannot process the supplied value. | Check the input and the built-in's documented constraints. |
| E3005 | Built-in division by zero | A numeric operation attempted to divide by zero. | Ensure the divisor is not zero. |
| E3006 | Built-in index error | A collection index is outside the available range. | Check the collection length before indexing. |
| E3007 | Built-in type error | A value has the wrong type for this built-in. | Pass the documented value type. |
| E3008 | Built-in overflow | A numeric operation exceeded supported limits. | Use a smaller value or a safer numeric approach. |
| E3009 | Built-in missing value | A required value was not provided. | Pass all required arguments. |
| E3010 | Built-in unknown operation | The requested built-in operation does not exist. | Use a name from the current built-in catalog. |
| E4001 | Internal compiler invariant | The compiler encountered an unexpected internal state. | Report the source and diagnostic code with a reproducible example. |
| E4002 | Code generation failure | The compiler could not emit valid target source. | Simplify the construct and report the failing input. |
| E4003 | Invalid AST node | The syntax tree contains a node the compiler cannot handle. | Check parser and compiler version compatibility. |
| E4004 | Invalid compiler state | The compiler state is inconsistent. | Restart compilation and report a reproducible case. |
| E4005 | Runtime support missing | Generated code requires a runtime module that is unavailable. | Keep the required TIRAN runtime beside the generated file. |
| E5001 | Source file missing | The source file could not be read. | Check the file path and permissions. |
| E5002 | Source encoding error | The source file is not valid UTF-8. | Save the file as UTF-8. |
| E5003 | Output write error | The compiler could not write the output file. | Check the destination path and write permissions. |
| E5004 | Invalid CLI arguments | The command-line arguments are inconsistent. | Run tiran --help and check the options. |
| E5005 | Invalid AST request | The source could not be converted to an AST report. | Fix syntax errors before requesting --ast. |
| E5006 | Invalid formatter input | The formatter could not process the source. | Fix malformed block structure and retry. |
| E5007 | Check failed | The source did not pass compiler validation. | Read the earlier diagnostic and fix that issue. |
| E5008 | Unknown command-line mode | The selected command-line mode is not supported. | Use --check, --format, --ast, or normal compilation. |
| E6001 | Invalid numeric input | A numeric operation received a value that is not a valid number. | Pass an integer or floating-point value. |
| E6002 | Invalid text input | A text operation received a value that cannot be handled as text. | Pass a string or convert the value first. |
| E6003 | Invalid collection input | A collection operation received an unsupported collection. | Pass a list or another documented iterable. |
| E6004 | Empty collection | The operation requires at least one collection element. | Check for an empty collection before calling it. |
| E6005 | Invalid range | The requested range has an invalid boundary or order. | Ensure the lower boundary does not exceed the upper boundary. |
| E6006 | Invalid encoding | The requested text encoding is unsupported. | Use a supported encoding such as UTF-8. |
| E6007 | Invalid regular expression | The regular expression is malformed. | Escape special characters and check the pattern. |
| E6008 | Invalid conversion | A value cannot be converted to the requested type. | Validate the input before converting it. |
| E7001 | Reserved identifier | The identifier conflicts with a reserved compiler name. | Rename the variable or function. |
| E7002 | Duplicate declaration | The same declaration was added more than once. | Use a distinct name or update the existing value. |
| E7003 | Unknown symbol | The compiler cannot resolve this symbol. | Declare it, import it, or correct the spelling. |
| E7004 | Invalid parameter list | A function parameter list is malformed. | Separate valid parameter names with commas. |
| E7005 | Invalid return | The return statement is not supported in this context. | Move it into a function or choose a supported target. |
| E7006 | Invalid loop control | break or continue appears outside a loop. | Move the statement into a loop. |
| E7007 | Invalid control flow | The requested control-flow transition is not valid. | Check the enclosing block and branch order. |
| E7008 | Potential name collision | A generated helper name conflicts with a source name. | Rename the source symbol to avoid the reserved helper prefix. |
| E8001 | Configuration error | The compiler configuration is invalid. | Review the command-line options and project configuration. |
| E8002 | Registry count mismatch | The built-in registry has an unexpected number of entries. | Regenerate the registry and run the standard-library tests. |
| E8003 | Duplicate built-in | Two built-ins use the same registered name. | Give each built-in a unique name. |
| E8004 | Documentation mismatch | The documented built-in catalog does not match the registry. | Regenerate built-in documentation from the registry. |
| E8005 | Regression test failure | A compiler behavior differs from its expected result. | Reproduce the failing test and fix the underlying behavior. |

**Catalog size:** 74 stable diagnostic codes.