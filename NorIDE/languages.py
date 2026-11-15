import builtins
import keyword
import os
import re
import shutil
import sys


DQ = chr(34)
SQ = chr(39)
STR_PATTERN = f"({DQ * 3}.*?{DQ * 3}|{SQ * 3}.*?{SQ * 3}|{DQ}.*?{DQ}|{SQ}.*?{SQ})"

LANGUAGES = {
    "Python": {
        "ext": ".py",
        "filetypes": [("Python Files", "*.py"), ("All Files", "*.*")],
        "keywords": keyword.kwlist,
        "builtins": [w for w in dir(builtins) if not w.startswith("_")],
        "comment": r"#[^\n]*",
        "starter": (
            "# Press '▶ Run' to run Python!\n"
            'name = input("What is your name? ")\n'
            'print(f"Hello, {name}!")\n'
        ),
    },
    "JavaScript": {
        "ext": ".js",
        "filetypes": [("JavaScript Files", "*.js"), ("All Files", "*.*")],
        "keywords": [
            "const", "let", "var", "function", "return", "if", "else",
            "for", "while", "switch", "case", "break", "continue", "class",
            "new", "try", "catch", "throw", "async", "await", "import", "export",
            "true", "false", "null", "undefined",
        ],
        "builtins": ["console", "log", "Math", "JSON", "Array", "Object", "String", "Number"],
        "comment": r"//[^\n]*",
        "starter": (
            "// Requires Node.js installed\n"
            'console.log("Hello from JavaScript!");\n'
            "for (let i = 1; i <= 3; i++) {\n"
            "    console.log('Count:', i);\n"
            "}\n"
        ),
        },
        "C#": {
        "ext": ".cs",
        "filetypes": [("C# Files", "*.cs"), ("All Files", "*.*")],
        "keywords": [
            "abstract", "as", "base", "bool", "break", "byte", "case", "catch",
            "char", "checked", "class", "const", "continue", "decimal", "default",
            "delegate", "do", "double", "else", "enum", "event", "explicit",
            "extern", "false", "finally", "fixed", "float", "for", "foreach",
            "goto", "if", "implicit", "in", "int", "interface", "internal", "is",
            "lock", "long", "namespace", "new", "null", "object", "operator",
            "out", "override", "params", "private", "protected", "public",
            "readonly", "ref", "return", "sbyte", "sealed", "short", "sizeof",
            "stackalloc", "static", "string", "struct", "switch", "this", "throw",
            "true", "try", "typeof", "uint", "ulong", "unchecked", "unsafe",
            "ushort", "using", "var", "virtual", "void", "volatile", "while",
            "async", "await", "record",
        ],
        "builtins": [
            "Console", "WriteLine", "Write", "ReadLine", "Math", "Convert",
            "Int32", "Double", "Boolean", "String", "List", "Dictionary", "Main",
        ],
        "comment": r"//[^\n]*",
        "starter": (
            "// Requires .NET SDK installed\n"
            "using System;\n\n"
            "class Program {\n"
            "    static void Main() {\n"
            '        Console.WriteLine("Hello from C#!");\n'
            "    }\n"
            "}\n"
        ),
    },
    "C++": {
        "ext": ".cpp",
        "filetypes": [("C++ Files", "*.cpp"), ("All Files", "*.*")],
        "keywords": [
            "int", "float", "double", "char", "void", "bool", "return",
            "if", "else", "for", "while", "do", "switch", "case", "break",
            "continue", "class", "struct", "public", "private", "using",
            "namespace", "true", "false", "const", "auto", "include",
        ],
        "builtins": ["std", "cout", "cin", "endl", "string", "vector", "main"],
        "comment": r"//[^\n]*",
        "starter": (
            "// Requires g++ compiler installed\n"
            "#include <iostream>\n"
            "using namespace std;\n\n"
            "int main() {\n"
            '    cout << "Hello from C++!" << endl;\n'
            "    return 0;\n"
            "}\n"
        ),
    },
    "C": {
        "ext": ".c",
        "filetypes": [("C Files", "*.c"), ("All Files", "*.*")],
        "keywords": [
            "int", "float", "double", "char", "void", "return", "if",
            "else", "for", "while", "do", "switch", "case", "break",
            "continue", "struct", "typedef", "const", "sizeof", "include",
        ],
        "builtins": ["printf", "scanf", "malloc", "free", "main", "NULL"],
        "comment": r"//[^\n]*",
        "starter": (
            "// Requires gcc compiler installed\n"
            "#include <stdio.h>\n\n"
            "int main() {\n"
            '    printf("Hello from C!\\n");\n'
            "    return 0;\n"
            "}\n"
        ),
    },
        "Text": {
        "ext": ".txt",
        "filetypes": [("Text Files", "*.txt"), ("Markdown Files", "*.md"), ("All Files", "*.*")],
        "keywords": [],
        "builtins": [],
        "comment": r"(?!x)x",  # Matches nothing so plain text stays clean
        "starter": "Write your notes here...\n",
    },
        "Go": {
        "ext": ".go",
        "filetypes": [("Go Files", "*.go"), ("All Files", "*.*")],
        "keywords": [
            "break", "default", "func", "interface", "select", "case", "defer",
            "go", "map", "struct", "chan", "else", "goto", "package", "switch",
            "const", "fallthrough", "if", "range", "type", "continue", "for",
            "import", "return", "var", "true", "false", "nil", "iota",
        ],
        "builtins": [
            "fmt", "Println", "Printf", "Scanln", "main", "string", "int",
            "float64", "bool", "error", "len", "cap", "make", "new", "append",
        ],
        "comment": r"//[^\n]*",
        "starter": (
            "// Requires Go installed\n"
            "package main\n\n"
            'import "fmt"\n\n'
            "func main() {\n"
            '    fmt.Println("Hello from Go!")\n'
            "}\n"
        ),
    },
        "Rust": {
        "ext": ".rs",
        "filetypes": [("Rust Files", "*.rs"), ("All Files", "*.*")],
        "keywords": [
            "as", "break", "const", "continue", "crate", "else", "enum",
            "extern", "false", "fn", "for", "if", "impl", "in", "let", "loop",
            "match", "mod", "move", "mut", "pub", "ref", "return", "self",
            "Self", "static", "struct", "super", "trait", "true", "type",
            "unsafe", "use", "where", "while", "async", "await", "dyn",
        ],
        "builtins": [
            "println", "print", "format", "vec", "String", "Vec", "Option",
            "Result", "Some", "None", "Ok", "Err", "i32", "i64", "u32", "u64",
            "f32", "f64", "bool", "str", "usize", "main",
        ],
        "comment": r"//[^\n]*",
        "starter": (
            "// Requires rustc installed\n"
            "fn main() {\n"
            '    println!("Hello from Rust!");\n'
            "}\n"
        ),
    },
        "Java": {
        "ext": ".java",
        "filetypes": [("Java Files", "*.java"), ("All Files", "*.*")],
        "keywords": [
            "abstract", "assert", "boolean", "break", "byte", "case", "catch",
            "char", "class", "const", "continue", "default", "do", "double",
            "else", "enum", "extends", "final", "finally", "float", "for",
            "goto", "if", "implements", "import", "instanceof", "int",
            "interface", "long", "native", "new", "package", "private",
            "protected", "public", "return", "short", "static", "strictfp",
            "super", "switch", "synchronized", "this", "throw", "throws",
            "transient", "try", "void", "volatile", "while", "true", "false", "null",
        ],
        "builtins": [
            "System", "out", "in", "println", "print", "printf", "String",
            "Scanner", "Math", "Integer", "Double", "Boolean", "ArrayList", "main",
        ],
        "comment": r"//[^\n]*",
        "starter": (
            "// Requires Java JDK 11+ installed\n"
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            '        System.out.println("Hello from Java!");\n'
            "    }\n"
            "}\n"
        ),
    },
    "HTML": {
    "ext": ".html",
    "filetypes": [("HTML Files", "*.html;*.htm"), ("All Files", "*.*")],
    "keywords": [
        "html", "head", "body", "title", "style", "script", "div", "span",
        "h1", "h2", "h3", "p", "a", "img", "ul", "ol", "li", "button",
        "input", "form", "link", "meta", "section", "header", "footer",
    ],
    "builtins": [
        "class", "id", "href", "src", "rel", "type", "color", "background",
        "font-family", "margin", "padding", "display", "flex", "border",
    ],
    "comment": r"<!--[\s\S]*?-->",
    "starter": (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head>\n"
        "    <style>\n"
        "        body { font-family: sans-serif; background: #1e1e1e; color: white; padding: 40px; }\n"
        "        h1 { color: #569cd6; }\n"
        "    </style>\n"
        "</head>\n"
        "<body>\n"
        "    <h1>Hello from NorIDE!</h1>\n"
        "    <p>Edit this HTML/CSS and press '▶ Run' to preview in your browser.</p>\n"
        "</body>\n"
        "</html>\n"
        ),
    },
        "Lua": {
        "ext": ".lua",
        "filetypes": [("Lua Files", "*.lua"), ("All Files", "*.*")],
        "keywords": [
            "and", "break", "do", "else", "elseif", "end", "false", "for",
            "function", "goto", "if", "in", "local", "nil", "not", "or",
            "repeat", "return", "then", "true", "until", "while",
        ],
        "builtins": [
            "print", "io", "write", "read", "math", "string", "table", "os",
            "pairs", "ipairs", "next", "tonumber", "tostring", "type",
            "require", "pcall", "xpcall", "error", "assert",
        ],
        "comment": r"--[^\n]*",
        "starter": (
            "-- Requires Lua installed\n"
            'io.write("What is your name? ")\n'
            "io.flush()\n"
            "local name = io.read()\n"
            'print("Hello, " .. tostring(name) .. "!")\n'
        ),
    },
        "Assembly": {
        "ext": ".asm",
        "filetypes": [("Assembly Files", "*.asm;*.s"), ("All Files", "*.*")],
        "keywords": [
            "mov", "add", "sub", "mul", "imul", "div", "idiv", "inc", "dec",
            "push", "pop", "call", "ret", "jmp", "je", "jne", "jg", "jge",
            "jl", "jle", "cmp", "test", "and", "or", "xor", "not", "shl",
            "shr", "lea", "nop", "syscall", "int", "section", "global",
            "extern", "db", "dw", "dd", "dq", "resb", "resw", "resd", "resq",
        ],
        "builtins": [
            "rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rbp", "rsp",
            "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15",
            "eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp",
            "ax", "bx", "cx", "dx", "al", "bl", "cl", "dl",
            "main", "printf", "scanf", "exit", "rel", "default",
        ],
        "comment": r";[^\n]*",
        "starter": (
            "; Requires NASM + GCC (MinGW) installed\n"
            "default rel\n"
            "extern printf\n"
            "global main\n\n"
            "section .data\n"
            '    msg db "Hello from x86-64 Assembly!", 10, 0\n\n'
            "section .text\n"
            "main:\n"
            "    sub rsp, 40          ; Shadow space for Windows x64 calling convention\n"
            "    lea rcx, [msg]       ; 1st argument in RCX\n"
            "    call printf\n"
            "    xor eax, eax         ; Return 0\n"
            "    add rsp, 40\n"
            "    ret\n"
        ),
    },
        "PHP": {
        "ext": ".php",
        "filetypes": [("PHP Files", "*.php"), ("All Files", "*.*")],
        "keywords": [
            "abstract", "and", "array", "as", "break", "callable", "case",
            "catch", "class", "clone", "const", "continue", "declare", "default",
            "die", "do", "echo", "else", "elseif", "empty", "enddeclare",
            "endfor", "endforeach", "endif", "endswitch", "endwhile", "eval",
            "exit", "extends", "final", "finally", "fn", "for", "foreach",
            "function", "global", "goto", "if", "implements", "include",
            "include_once", "instanceof", "insteadof", "interface", "isset",
            "list", "match", "namespace", "new", "or", "print", "private",
            "protected", "public", "readonly", "require", "require_once",
            "return", "static", "switch", "throw", "trait", "try", "unset",
            "use", "var", "while", "xor", "yield", "true", "false", "null",
        ],
        "builtins": [
            "strlen", "strpos", "substr", "explode", "implode", "trim",
            "str_replace", "count", "array_push", "array_pop", "array_map",
            "array_filter", "in_array", "json_encode", "json_decode",
            "var_dump", "print_r", "readline", "fopen", "fread", "fwrite",
            "fclose", "file_get_contents", "file_put_contents", "date", "time",
        ],
        "comment": r"(//[^\n]*|#[^\n]*)",
        "starter": (
            "<?php\n"
            "// Requires PHP CLI installed\n"
            '$name = readline("What is your name? ");\n'
            'echo "Hello, " . $name . "!\\n";\n'
            "?>\n"
        ),
    },
        "Ruby": {
        "ext": ".rb",
        "filetypes": [("Ruby Files", "*.rb"), ("All Files", "*.*")],
        "keywords": [
            "BEGIN", "END", "alias", "and", "begin", "break", "case", "class",
            "def", "defined?", "do", "else", "elsif", "end", "ensure", "false",
            "for", "if", "in", "module", "next", "nil", "not", "or", "redo",
            "rescue", "retry", "return", "self", "super", "then", "true",
            "undef", "unless", "until", "when", "while", "yield",
        ],
        "builtins": [
            "puts", "print", "p", "gets", "chomp", "require", "require_relative",
            "attr_reader", "attr_writer", "attr_accessor", "initialize",
            "Array", "Hash", "String", "Integer", "Float", "File", "Dir", "Math",
        ],
        "comment": r"#[^\n]*",
        "starter": (
            "# Requires Ruby installed\n"
            'print "What is your name? "\n'
            "$stdout.flush\n"
            "name = gets.chomp\n"
            'puts "Hello, #{name}!"\n'
        ),
    },
        "Ruby on Rails": {
        "ext": ".rb",
        "filetypes": [("Ruby on Rails Files", "*.rb"), ("All Files", "*.*")],
        "keywords": [
            "BEGIN", "END", "alias", "and", "begin", "break", "case", "class",
            "def", "defined?", "do", "else", "elsif", "end", "ensure", "false",
            "for", "if", "in", "module", "next", "nil", "not", "or", "redo",
            "rescue", "retry", "return", "self", "super", "then", "true",
            "undef", "unless", "until", "when", "while", "yield", "require",
        ],
        "builtins": [
            "Rails", "Application", "ActionController", "Base", "API",
            "ActiveRecord", "ActiveSupport", "render", "params", "redirect_to",
            "routes", "draw", "root", "get", "post", "put", "patch", "delete",
            "resources", "before_action", "puts", "print", "gemfile", "Rackup",
        ],
        "comment": r"#[^\n]*",
        "starter": (
            "# Requires Ruby + 'gem install rails' installed\n"
            "# Starts a live Rails server at http://localhost:3000 (Press Esc to stop)\n"
            'require "bundler/inline"\n\n'
            "gemfile do\n"
            '  source "https://rubygems.org"\n'
            '  gem "rails"\n'
            '  gem "puma"\n'
            "end\n\n"
            'require "rails"\n'
            'require "action_controller/railtie"\n\n'
            "class MiniRailsApp < Rails::Application\n"
            "  config.root = __dir__\n"
            "  config.consider_all_requests_local = true\n"
            '  config.secret_key_base = "bolt_ide_secret_key_1234567890"\n'
            "  config.eager_load = false\n"
            "  Rails.logger = Logger.new($stdout)\n\n"
            "  routes.append do\n"
            '    root to: "hello#index"\n'
            "  end\n"
            "end\n\n"
            "class HelloController < ActionController::Base\n"
            "  def index\n"
            '    render html: "<h1>Hello from Ruby on Rails in NorIDE!</h1>".html_safe\n'
            "  end\n"
            "end\n\n"
            "MiniRailsApp.initialize!\n"
            'puts "Rails running on http://localhost:3000 — press Esc in IDE to stop."\n'
            "$stdout.flush\n"
            'Rack::Handler::Puma.run(MiniRailsApp, Port: 3000, Host: "127.0.0.1")\n'
        ),
    },
        "TypeScript": {
        "ext": ".ts",
        "filetypes": [("TypeScript Files", "*.ts;*.tsx"), ("All Files", "*.*")],
        "keywords": [
            "abstract", "any", "as", "async", "await", "boolean", "break",
            "case", "catch", "class", "const", "constructor", "continue",
            "declare", "default", "delete", "do", "else", "enum", "export",
            "extends", "false", "finally", "for", "from", "function", "get",
            "if", "implements", "import", "in", "infer", "instanceof",
            "interface", "is", "keyof", "let", "module", "namespace", "never",
            "new", "null", "number", "object", "of", "override", "private",
            "protected", "public", "readonly", "require", "return", "satisfies",
            "set", "static", "string", "super", "switch", "symbol", "this",
            "throw", "true", "try", "type", "typeof", "undefined", "unique",
            "unknown", "var", "void", "while", "yield",
        ],
        "builtins": [
            "console", "log", "warn", "error", "Math", "JSON", "Array",
            "Object", "String", "Number", "Boolean", "Promise", "Map", "Set",
            "Record", "Partial", "Required", "Pick", "Omit", "Readonly",
        ],
        "comment": r"//[^\n]*",
        "starter": (
            "// Requires Node.js + tsx ('npm install -g tsx')\n"
            "interface User {\n"
            "    name: string;\n"
            "    age: number;\n"
            "}\n\n"
            "const greet = (user: User): string => {\n"
            "    return `Hello, ${user.name} (age ${user.age})!`;\n"
            "};\n\n"
            'console.log(greet({ name: "Alex", age: 25 }));\n'
        ),
    },
        "SQL": {
        "ext": ".sql",
        "filetypes": [("SQL Files", "*.sql"), ("All Files", "*.*")],
        "keywords": [
            "SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES", "UPDATE",
            "SET", "DELETE", "CREATE", "TABLE", "DROP", "ALTER", "ADD", "INDEX",
            "VIEW", "JOIN", "INNER", "LEFT", "RIGHT", "FULL", "ON", "AS",
            "GROUP", "BY", "ORDER", "ASC", "DESC", "HAVING", "LIMIT", "OFFSET",
            "DISTINCT", "UNION", "ALL", "AND", "OR", "NOT", "IN", "IS", "NULL",
            "LIKE", "BETWEEN", "EXISTS", "CASE", "WHEN", "THEN", "ELSE", "END",
            "PRIMARY", "KEY", "FOREIGN", "REFERENCES", "UNIQUE", "DEFAULT",
            "select", "from", "where", "insert", "into", "values", "update",
            "set", "delete", "create", "table", "drop", "alter", "join",
            "inner", "left", "right", "on", "as", "group", "by", "order",
            "asc", "desc", "having", "limit", "and", "or", "not", "in", "null",
            "primary", "key", "default",
        ],
        "builtins": [
            "INT", "INTEGER", "TEXT", "VARCHAR", "CHAR", "REAL", "FLOAT",
            "DOUBLE", "BOOLEAN", "DATE", "DATETIME", "TIMESTAMP", "BLOB",
            "COUNT", "SUM", "AVG", "MIN", "MAX", "COALESCE", "ROUND", "UPPER",
            "LOWER", "LENGTH", "SUBSTR", "int", "integer", "text", "varchar",
            "real", "boolean", "count", "sum", "avg", "min", "max",
        ],
        "comment": r"--[^\n]*",
        "starter": (
            "-- Runs instantly using built-in SQLite!\n"
            "CREATE TABLE users (\n"
            "    id INTEGER PRIMARY KEY,\n"
            "    name TEXT NOT NULL,\n"
            "    role TEXT\n"
            ");\n\n"
            "INSERT INTO users (name, role) VALUES ('Alice', 'Developer');\n"
            "INSERT INTO users (name, role) VALUES ('Bob', 'Designer');\n\n"
            "SELECT * FROM users;\n"
        ),
    },
        "CSS": {
        "ext": ".css",
        "filetypes": [("CSS Files", "*.css"), ("All Files", "*.*")],
        "keywords": [
            "body", "html", "div", "span", "p", "a", "h1", "h2", "h3", "button",
            "input", "header", "footer", "main", "section", "nav", "ul", "li",
            "hover", "active", "focus", "before", "after", "root", "media",
            "keyframes", "import", "important",
        ],
        "builtins": [
            "color", "background", "background-color", "font-family", "font-size",
            "font-weight", "margin", "padding", "border", "border-radius",
            "display", "flex", "grid", "justify-content", "align-items",
            "gap", "width", "height", "max-width", "position", "top", "left",
            "right", "bottom", "z-index", "box-shadow", "opacity", "transition",
            "transform", "cursor", "text-align", "line-height", "overflow",
        ],
        "comment": r"/\*[\s\S]*?\*/",
        "starter": (
            "/* Press F5 to preview this CSS on a live sample card! */\n"
            "body {\n"
            "    font-family: 'Segoe UI', sans-serif;\n"
            "    background-color: #1e1e1e;\n"
            "    color: #ffffff;\n"
            "    display: flex;\n"
            "    justify-content: center;\n"
            "    align-items: center;\n"
            "    height: 100vh;\n"
            "    margin: 0;\n"
            "}\n\n"
            ".card {\n"
            "    background: #252526;\n"
            "    padding: 2rem;\n"
            "    border-radius: 12px;\n"
            "    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);\n"
            "    text-align: center;\n"
            "}\n\n"
            "button {\n"
            "    background: #007acc;\n"
            "    color: white;\n"
            "    border: none;\n"
            "    padding: 10px 20px;\n"
            "    border-radius: 6px;\n"
            "    cursor: pointer;\n"
            "}\n"
        ),
    },
        "R": {
        "ext": ".R",
        "filetypes": [("R Files", "*.R;*.r"), ("All Files", "*.*")],
        "keywords": [
            "if", "else", "repeat", "while", "function", "for", "in", "next",
            "break", "TRUE", "FALSE", "NULL", "Inf", "NaN", "NA",
            "NA_integer_", "NA_real_", "NA_complex_", "NA_character_",
        ],
        "builtins": [
            "print", "cat", "paste", "paste0", "c", "list", "vector", "matrix",
            "data.frame", "factor", "length", "dim", "nrow", "ncol", "names",
            "mean", "median", "sum", "min", "max", "sd", "var", "summary",
            "seq", "rep", "head", "tail", "str", "library", "require", "readLines",
        ],
        "comment": r"#[^\n]*",
        "starter": (
            "# Requires R (Rscript) installed\n"
            'numbers <- c(10, 20, 30, 40, 50)\n'
            'cat("Numbers:", numbers, "\\n")\n'
            'cat("Mean:", mean(numbers), "\\n")\n'
        ),
    },
        "Shell": {
        "ext": ".sh",
        "filetypes": [("Shell Scripts", "*.sh;*.bash"), ("All Files", "*.*")],
        "keywords": [
            "if", "then", "else", "elif", "fi", "case", "esac", "for", "select",
            "while", "until", "do", "done", "in", "function", "time", "coproc",
            "export", "local", "readonly", "declare", "typeset", "unset",
            "return", "exit", "break", "continue", "shift", "source", "true", "false",
        ],
        "builtins": [
            "echo", "printf", "read", "cd", "pwd", "ls", "cp", "mv", "rm",
            "mkdir", "rmdir", "touch", "cat", "grep", "sed", "awk", "find",
            "chmod", "chown", "ps", "kill", "sleep", "curl", "wget", "tar", "zip",
        ],
        "comment": r"#[^\n]*",
        "starter": (
            "#!/usr/bin/env bash\n"
            "# Requires bash (Git Bash / WSL on Windows, or built-in on macOS/Linux)\n"
            'read -p "What is your name? " name\n'
            'echo "Hello, $name!"\n'
        ),
    },
        "JSON": {
        "ext": ".json",
        "filetypes": [("JSON Files", "*.json"), ("All Files", "*.*")],
        "keywords": ["true", "false", "null"],
        "builtins": [],
        "comment": r"(?!x)x",  # Standard JSON does not support comments
        "starter": (
            '{\n'
            '    "ide": "NorIDE",\n'
            '    "version": 1.0,\n'
            '    "features": ["Syntax Highlighting", "Multi-Language", "JSON Validator"],\n'
            '    "active": true\n'
            '}\n'
        ),
    },
        "Swift": {
        "ext": ".swift",
        "filetypes": [("Swift Files", "*.swift"), ("All Files", "*.*")],
        "keywords": [
            "associatedtype", "class", "deinit", "enum", "extension",
            "fileprivate", "func", "import", "init", "inout", "internal",
            "let", "open", "operator", "private", "precedencegroup",
            "protocol", "public", "rethrows", "static", "struct", "subscript",
            "typealias", "var", "break", "case", "catch", "continue",
            "default", "defer", "do", "else", "fallthrough", "for", "guard",
            "if", "in", "repeat", "return", "throw", "switch", "where",
            "while", "as", "Any", "false", "is", "nil", "self", "Self",
            "super", "throws", "true", "try", "async", "await", "actor",
        ],
        "builtins": [
            "print", "readLine", "Int", "Double", "Float", "Bool", "String",
            "Array", "Dictionary", "Set", "Optional", "Result", "Error",
            "min", "max", "abs", "zip", "map", "filter", "reduce", "sorted",
        ],
        "comment": r"//[^\n]*",
        "starter": (
            "// Requires Swift toolchain installed\n"
            "import Foundation\n\n"
            'func greet(name: String) -> String {\n'
            '    return "Hello, \\(name) from Swift!"\n'
            "}\n\n"
            'print(greet(name: "Developer"))\n'
        ),
    },
        "YAML": {
        "ext": ".yaml",
        "filetypes": [("YAML Files", "*.yaml;*.yml"), ("All Files", "*.*")],
        "keywords": ["true", "false", "null", "yes", "no", "on", "off"],
        "builtins": [],
        "comment": r"#[^\n]*",
        "starter": (
            "# Press '▶ Run' to validate YAML syntax!\n"
            "ide:\n"
            "  name: NorIDE\n"
            "  version: 1.0\n"
            "  dark_mode: true\n"
            "  languages:\n"
            "    - Python\n"
            "    - Go\n"
            "    - Rust\n"
            "    - YAML\n"
        ),
    },
        "XML": {
        "ext": ".xml",
        "filetypes": [("XML Files", "*.xml;*.svg;*.xsd"), ("All Files", "*.*")],
        "keywords": [
            "xml", "version", "encoding", "standalone", "DOCTYPE", "ELEMENT",
            "ATTLIST", "ENTITY", "NOTATION", "CDATA", "true", "false",
        ],
        "builtins": [
            "id", "name", "type", "value", "href", "src", "xmlns", "xsi",
        ],
        "comment": r"<!--[\s\S]*?-->",
        "starter": (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<!-- Press F5 to validate and format XML! -->\n"
            "<ide>\n"
            "    <name>NorIDE</name>\n"
            "    <version>1.0</version>\n"
            "    <features>\n"
            "        <feature>Syntax Highlighting</feature>\n"
            "        <feature>XML Validator</feature>\n"
            "    </features>\n"
            "</ide>\n"
        ),
    },
        "Perl": {
        "ext": ".pl",
        "filetypes": [("Perl Files", "*.pl;*.pm"), ("All Files", "*.*")],
        "keywords": [
            "my", "our", "local", "state", "sub", "if", "elsif", "else",
            "unless", "while", "until", "for", "foreach", "do", "next",
            "last", "redo", "return", "use", "require", "package", "begin",
            "end", "given", "when", "default", "and", "or", "not", "xor",
            "eq", "ne", "lt", "gt", "le", "ge", "cmp", "strict", "warnings",
        ],
        "builtins": [
            "print", "say", "printf", "sprintf", "chomp", "chop", "split",
            "join", "push", "pop", "shift", "unshift", "splice", "sort",
            "reverse", "map", "grep", "keys", "values", "each", "exists",
            "delete", "defined", "undef", "scalar", "length", "substr",
            "index", "rindex", "open", "close", "read", "write", "die", "warn",
        ],
        "comment": r"#[^\n]*",
        "starter": (
            "#!/usr/bin/env perl\n"
            "# Requires Perl installed\n"
            "use strict;\n"
            "use warnings;\n\n"
            'STDOUT->autoflush(1);\n'
            'print "What is your name? ";\n'
            "my $name = <STDIN>;\n"
            "chomp($name);\n"
            'print "Hello, $name from Perl!\\n";\n'
        ),
    },
}

EXT_TO_LANG = {cfg["ext"]: name for name, cfg in LANGUAGES.items()}
EXT_TO_LANG[".yml"] = "YAML"

def get_python_exe():
    if getattr(sys, "frozen", False):
        return shutil.which("python") or shutil.which("py") or "python"
    return sys.executable


def get_commands(lang, file_path):
    base, _ = os.path.splitext(file_path)
    exe_path = base + (".exe" if os.name == "nt" else ".out")
    if lang == "Python":
        return [[sys.executable, "-u", file_path]], None
    elif lang == "JavaScript":
        return [["node", file_path]], None
    elif lang == "C++":
        return [["g++", file_path, "-o", exe_path], [exe_path]], exe_path
    elif lang == "C":
        return [["gcc", file_path, "-o", exe_path], [exe_path]], exe_path
    elif lang == "Go":
        return [["go", "run", file_path]], None
    elif lang == "Rust":
        return [["rustc", file_path, "-o", exe_path], [exe_path]], exe_path
    elif lang == "Java":
        folder = os.path.dirname(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            src = f.read()
        match = re.search(r"\bclass\s+([A-Za-z_]\w*)", src)
        class_name = match.group(1) if match else "Main"

        target_java = os.path.join(folder, f"{class_name}.java")
        if os.path.abspath(file_path) != os.path.abspath(target_java):
            with open(target_java, "w", encoding="utf-8") as f:
                f.write(src)

        # Find the exact folder where javac lives and use its matching java binary
        javac_path = shutil.which("javac") or "javac"
        java_dir = os.path.dirname(javac_path)
        java_bin = os.path.join(java_dir, "java.exe" if os.name == "nt" else "java")
        if not os.path.exists(java_bin):
            java_bin = "java"

        class_file = os.path.join(folder, f"{class_name}.class")
        return [
            [javac_path, target_java],
            [java_bin, "-cp", folder, class_name],
        ], class_file
    elif lang == "C#":
        # Works out of the box with .NET 10+ (file-based apps)
        return [["dotnet", "run", file_path]], None
    elif lang == "Lua":
        return [["lua", file_path]], None
    elif lang == "Assembly":
        obj_path = base + ".obj"
        fmt = "win64" if os.name == "nt" else "elf64"
        return [
            ["nasm", "-f", fmt, file_path, "-o", obj_path],
            ["gcc", obj_path, "-o", exe_path],
            [exe_path],
        ], exe_path
    elif lang == "PHP":
        return [["php", file_path]], None
    elif lang == "Ruby":
        return [["ruby", file_path]], None
    elif lang == "Ruby on Rails":
        return [["ruby", file_path]], None
    elif lang == "TypeScript":
        npx_cmd = "npx.cmd" if os.name == "nt" else "npx"
        return [[npx_cmd, "tsx", file_path]], None
    elif lang == "SQL":
        sql_runner = (
            "import sqlite3, sys; "
            "conn = sqlite3.connect(':memory:'); "
            "cur = conn.cursor(); "
            "sql = open(sys.argv[1], encoding='utf-8').read(); "
            "[print(' | '.join(map(str, r))) for stmt in sql.split(';') if stmt.strip() "
            "for r in (cur.execute(stmt).fetchall() or [])]; "
            "conn.commit()"
        )
        return [[sys.executable, "-c", sql_runner, file_path]], None
    elif lang == "R":
        return [["Rscript", file_path]], None
    elif lang == "Shell":
        bash_cmd = shutil.which("bash")
        if not bash_cmd and os.name == "nt":
            git_bash = r"C:\Program Files\Git\bin\bash.exe"
            if os.path.exists(git_bash):
                bash_cmd = git_bash
        return [[bash_cmd or "bash", file_path]], None
    elif lang == "JSON":
        json_checker = (
            "import json, sys; "
            "data = json.load(open(sys.argv, encoding='utf-8')); "
            "print('Valid JSON! Formatted output:\\n' + json.dumps(data, indent=4))"
        )
        return [[sys.executable, "-c", json_checker, file_path]], None
    elif lang == "Swift":
        return [["swift", file_path]], None
    elif lang == "YAML":
        yaml_checker = (
            "import sys, json; "
            "text = open(sys.argv[1], encoding='utf-8').read(); "
            "try:\n"
            "    import yaml\n"
            "    data = yaml.safe_load(text)\n"
            "    print('Valid YAML! Parsed structure:\\n' + json.dumps(data, indent=2, default=str))\n"
            "except ImportError:\n"
            "    assert '\\t' not in text, 'Invalid YAML: Tab characters are not allowed for indentation!'\n"
            "    print('Basic YAML check passed! (Tip: run pip install pyyaml for full parsing)')"
        )
        return [[sys.executable, "-c", yaml_checker, file_path]], None
    elif lang == "XML":
        xml_checker = (
            "import sys, xml.etree.ElementTree as ET, xml.dom.minidom as minidom; "
            "raw = open(sys.argv[1], encoding='utf-8').read(); "
            "ET.fromstring(raw); "
            "pretty = '\\n'.join(l for l in minidom.parseString(raw).toprettyxml(indent='    ').splitlines() if l.strip()); "
            "print('Valid XML! Formatted output:\\n' + pretty)"
        )
        return [[sys.executable, "-c", xml_checker, file_path]], None
    elif lang == "Perl":
        return [["perl", file_path]], None

    




    return [], None