import os
import sys
import traceback
from tkinter import messagebox
import re
import tempfile
import webbrowser
import json



sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import re
    from tkinter import *
    from tkinter.filedialog import askopenfilename, asksaveasfilename
    from tkinter.scrolledtext import ScrolledText
    from tkinter.ttk import *
    from tkinter.colorchooser import askcolor

    from languages import EXT_TO_LANG, LANGUAGES, STR_PATTERN
    from runner import CodeRunner

    def ev(name):
        return chr(60) + name + chr(62)

    root = Tk()
    root.geometry("780x620")
    root.title("NorIDE")

    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "NorIDE_Logo.ico")
    if os.path.exists(icon_path):
        logo_img = PhotoImage(file=icon_path)
    else:
        logo_img = PhotoImage(width=32, height=32)
        logo_img.put("#00cccc", to=(0, 0, 32, 32))
        logo_img.put("#ffffff", to=(8, 8, 24, 24))
        logo_img.put("#00cccc", to=(12, 12, 20, 20))
    root.iconphoto(True, logo_img)

    current_file_path = None
    console_visible = False
    find_visible = False
    current_theme = "Dark"
    current_font_size = 11

    THEMES = {
        "Dark": {
            "editor_bg": "#1e1e1e",
            "editor_fg": "#d4d4d4",
            "cursor": "#ffffff",
            "gutter_bg": "#181818",
            "gutter_fg": "#858585",
            "console_bg": "#141414",
            "console_fg": "#ffffff",
            "keyword": "#569cd6",
            "builtin": "#dcdcaa",
            "string": "#ce9178",
            "number": "#b5cea8",
            "comment": "#6a9955",
            "search_bg": "#515c6a",
            "search_fg": "#ffffff",
        },
        "Light": {
            "editor_bg": "#ffffff",
            "editor_fg": "#1e1e1e",
            "cursor": "#000000",
            "gutter_bg": "#f0f0f0",
            "gutter_fg": "#6e6e6e",
            "console_bg": "#f7f7f7",
            "console_fg": "#1e1e1e",
            "keyword": "#0000ff",
            "builtin": "#795e26",
            "string": "#a31515",
            "number": "#098658",
            "comment": "#008000",
            "search_bg": "#ffdf5d",
            "search_fg": "#000000",
        },
    }
    SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

    def load_settings():
        global current_theme, current_font_size
        if not os.path.exists(SETTINGS_PATH):
            return
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            current_theme = data.get("theme", current_theme)
            current_font_size = int(data.get("font_size", current_font_size))
            if "dark_fg" in data:
                THEMES["Dark"]["editor_fg"] = data["dark_fg"]
            if "light_fg" in data:
                THEMES["Light"]["editor_fg"] = data["light_fg"]
        except Exception:
            pass

    def save_settings():
        data = {
            "theme": current_theme,
            "font_size": current_font_size,
            "dark_fg": THEMES["Dark"]["editor_fg"],
            "light_fg": THEMES["Light"]["editor_fg"],
        }
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass

    load_settings()

    def apply_theme(theme_name=None):
        global current_theme
        if theme_name:
            current_theme = theme_name
        if "theme_var" in globals() or "theme_var" in locals():
            theme_var.set(current_theme)
        t = THEMES[current_theme]


        code_editor.config(
            bg=t["editor_bg"],
            fg=t["editor_fg"],
            insertbackground=t["cursor"],
        )
        line_numbers.config(bg=t["gutter_bg"])
        console_box.config(bg=t["console_bg"], fg=t["console_fg"])

        code_editor.tag_configure("keyword", foreground=t["keyword"])
        code_editor.tag_configure("builtin", foreground=t["builtin"])
        code_editor.tag_configure("string", foreground=t["string"])
        code_editor.tag_configure("number", foreground=t["number"])
        code_editor.tag_configure("comment", foreground=t["comment"])
        code_editor.tag_configure(
            "search_match", background=t["search_bg"], foreground=t["search_fg"]
        )
        update_line_numbers()
        save_settings()

    def toggle_theme(event=None):
        # Theme Dropdown on Toolbar
        Label(toolbar, text="Theme:").pack(side=LEFT, padx=(10, 4), pady=2)
        theme_var = StringVar(value=current_theme)  # <-- Changed from "Dark"
        theme_combo = Combobox(
              toolbar,
              textvariable=theme_var,
              values=list(THEMES.keys()),
              state="readonly",
              width=7,
          )
        theme_combo.pack(side=LEFT, padx=2, pady=2)
        theme_combo.bind(ev(ev("ComboboxSelected")), lambda e: apply_theme(theme_var.get()))
        return "break"

    def change_font_size(delta):
        global current_font_size
        new_size = max(8, min(28, current_font_size + delta))
        current_font_size = new_size
        font_var.set(str(current_font_size))
        code_editor.config(font=("Consolas", current_font_size))
        console_box.config(font=("Consolas", max(8, current_font_size - 1)))
        update_line_numbers()
        save_settings()
        code_editor.focus_set()
        return "break"

    def on_font_select(event=None):
        global current_font_size
        current_font_size = int(font_var.get())
        change_font_size(0)

    
    def on_font_select(event=None):
        global current_font_size
        current_font_size = int(font_var.get())
        change_font_size(0)

    def pick_font_color(event=None):
        """Opens a color picker and updates the editor's main text color."""
        current_fg = code_editor.cget("fg")
        chosen = askcolor(color=current_fg, title="Choose Font Color")
        hex_color = chosen[1]  # chosen is ((r, g, b), '#hexcode')
        if hex_color:
          THEMES[current_theme]["editor_fg"] = hex_color
          code_editor.config(fg=hex_color, insertbackground=hex_color)
          save_settings()


    html_preview_path = None


    PAIRS = {
        "(": ")",
        "[": "]",
        "{": "}",
        chr(34): chr(34),
        chr(39): chr(39),
    }

    def append_output(text):
        console_box.config(state="normal")
        console_box.insert(END, text)
        console_box.see(END)
        console_box.config(state="disabled")

    runner = CodeRunner(root, append_output)

    def show_console():
        global console_visible
        if not console_visible:
            paned.add(console_box, weight=2)
            input_frame.pack(side=BOTTOM, fill=X, padx=5, pady=(0, 5))
            console_visible = True
            toggle_console_btn.config(text="Hide Console")

    def hide_console():
        global console_visible
        if console_visible:
            paned.forget(console_box)
            input_frame.pack_forget()
            console_visible = False
            toggle_console_btn.config(text="Show Console")

    def toggle_console(event=None):
        if console_visible:
            hide_console()
        else:
            show_console()
        return "break"

    def update_line_numbers(event=None):
        line_numbers.delete("all")
        t = THEMES[current_theme]

    def update_line_numbers(event=None):
        line_numbers.delete("all")
        t = THEMES[current_theme]

        line_str, _ = code_editor.index("end-1c").split(".")
        total_lines = int(line_str)
        digits = max(4, len(str(total_lines)))
        char_width = int(current_font_size * 0.85)
        gutter_width = digits * char_width + 14
        line_numbers.config(width=gutter_width)

        i = code_editor.index("@0,0")
        while True:
            dline = code_editor.dlineinfo(i)
            if dline is None:
                break
            _, y, _, _, _ = dline
            linenum, _ = str(i).split(".")
            line_numbers.create_text(
                gutter_width - 7,
                y,
                anchor="ne",
                text=linenum,
                fill=t["gutter_fg"],
                font=("Consolas", current_font_size),
            )
            i = code_editor.index(f"{i}+1line")

    def highlight_syntax(event=None):
        lang = lang_var.get()
        cfg = LANGUAGES.get(lang, LANGUAGES["Python"])

        code = code_editor.get("1.0", "end-1c")
        for tag in ("keyword", "builtin", "number", "string", "comment"):
            code_editor.tag_remove(tag, "1.0", END)

        def apply_pattern(pattern, tag, flags=0):
            for match in re.finditer(pattern, code, flags):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                code_editor.tag_add(tag, start, end)

        kw_pat = r"\b(" + "|".join(re.escape(w) for w in cfg["keywords"]) + r")\b"
        bi_pat = r"\b(" + "|".join(re.escape(w) for w in cfg["builtins"]) + r")\b"
        num_pat = r"\b\d+(\.\d+)?\b"

        apply_pattern(num_pat, "number")
        apply_pattern(bi_pat, "builtin")
        apply_pattern(kw_pat, "keyword")
        apply_pattern(STR_PATTERN, "string", re.DOTALL)
        apply_pattern(cfg["comment"], "comment")
        update_line_numbers()
        if lang == "Text":
            words = len(code.split())
            root.title(f"NorIDE - {words} words | {len(code)} chars")

    # --- Ctrl+F Find & Replace Functions ---
    def open_find_bar(event=None):
        global find_visible
        if not find_visible:
            find_frame.pack(side=TOP, fill=X, padx=5, pady=(4, 0), before=paned)
            find_visible = True
        selected = code_editor.tag_ranges(SEL)
        if selected:
            find_entry.delete(0, END)
            find_entry.insert(0, code_editor.get(selected[0], selected[1]))
        find_entry.focus_set()
        find_entry.select_range(0, END)
        find_next()
        return "break"

    def close_find_bar(event=None):
        global find_visible
        if find_visible:
            find_frame.pack_forget()
            code_editor.tag_remove("search_match", "1.0", END)
            find_visible = False
            code_editor.focus_set()
        return "break"

    def find_next(event=None):
        query = find_entry.get()
        code_editor.tag_remove("search_match", "1.0", END)
        if not query:
            find_status.config(text="")
            return "break"

        # Highlight all matches
        start = "1.0"
        count = 0
        while True:
            pos = code_editor.search(query, start, stopindex=END, nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(query)}c"
            code_editor.tag_add("search_match", pos, end)
            start = end
            count += 1

        # Jump to next match from cursor
        next_pos = code_editor.search(query, INSERT, stopindex=END, nocase=True)
        if not next_pos:
            next_pos = code_editor.search(query, "1.0", stopindex=END, nocase=True)

        if next_pos:
            next_end = f"{next_pos}+{len(query)}c"
            code_editor.tag_remove(SEL, "1.0", END)
            code_editor.tag_add(SEL, next_pos, next_end)
            code_editor.mark_set(INSERT, next_end)
            code_editor.see(next_pos)
            find_status.config(text=f"{count} found")
        else:
            find_status.config(text="0 found")
        return "break"

    def replace_one(event=None):
        query = find_entry.get()
        replacement = replace_entry.get()
        if not query:
            return
        selected = code_editor.tag_ranges(SEL)
        if selected and code_editor.get(selected[0], selected[1]).lower() == query.lower():
            code_editor.delete(selected[0], selected[1])
            code_editor.insert(selected[0], replacement)
            highlight_syntax()
        find_next()

    def replace_all(event=None):
        query = find_entry.get()
        replacement = replace_entry.get()
        if not query:
            return
        pos = "1.0"
        while True:
            pos = code_editor.search(query, pos, stopindex=END, nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(query)}c"
            code_editor.delete(pos, end)
            code_editor.insert(pos, replacement)
            pos = f"{pos}+{len(replacement)}c"
        highlight_syntax()
        find_next()

    def on_language_change(event=None):
        lang = lang_var.get()
        code_editor.config(wrap=WORD if lang == "Text" else NONE)
        highlight_syntax()
        if not current_file_path:
            code_editor.delete("1.0", END)
            code_editor.insert("1.0", LANGUAGES[lang]["starter"])
            highlight_syntax()
            update_line_numbers()

    def insert_spaces(event):
        code_editor.insert(INSERT, "    ")
        highlight_syntax()
        return "break"

    def auto_indent(event):
        line_text = code_editor.get("insert linestart", "insert")
        stripped = line_text.rstrip()
        leading_spaces = len(line_text) - len(line_text.lstrip(" "))
        indent = " " * leading_spaces

        if stripped.endswith(":") or stripped.endswith("{"):
            indent += "    "

        code_editor.insert(INSERT, "\n" + indent)
        code_editor.see(INSERT)
        highlight_syntax()
        return "break"

    def auto_close_pair(event):
        ch = event.char
        if event.state & 0x4 or event.state & 0x8 or event.state & 0x20000:
            return
        ch = event.char
        if not ch or ord(ch) < 32:
            return

        next_char = code_editor.get("insert", "insert + 1 chars")

        if ch in PAIRS.values() and next_char == ch:
            code_editor.mark_set(INSERT, "insert + 1 chars")
            return "break"

        if ch in PAIRS:
            code_editor.insert(INSERT, ch + PAIRS[ch])
            code_editor.mark_set(INSERT, "insert - 1 chars")
            highlight_syntax()
            return "break"

    def smart_backspace(event):
        prev_char = code_editor.get("insert - 1 chars", "insert")
        next_char = code_editor.get("insert", "insert + 1 chars")

        if prev_char in PAIRS and PAIRS[prev_char] == next_char:
            code_editor.delete("insert - 1 chars", "insert + 1 chars")
            highlight_syntax()
            return "break"

    def send_input(event=None):
        user_text = input_entry.get()
        input_entry.delete(0, END)
        runner.send_input(user_text)

    def run_editor_code(event=None):
        lang = lang_var.get()
        ext = LANGUAGES[lang]["ext"]
        code = code_editor.get("1.0", "end-1c")

        if lang == "Text":
            show_console()
            append_output("\n[Plain Text mode — nothing to execute.]\n")
            return "break"

        if lang == "HTML":
            if current_file_path:
                with open(current_file_path, "w", encoding="utf-8") as f:
                    f.write(code)
                target_url = "file://" + os.path.abspath(current_file_path)
            else:
                preview_path = os.path.join(tempfile.gettempdir(), "boltide_preview.html")
                with open(preview_path, "w", encoding="utf-8") as f:
                    f.write(code)
                target_url = "file://" + os.path.abspath(preview_path)

            webbrowser.open(target_url)
            show_console()
            append_output(f"\n[Opened HTML preview in default browser: {target_url}]\n")
            return "break"

        elif lang == "CSS":
            if current_file_path:
                with open(current_file_path, "w", encoding="utf-8") as f:
                    f.write(code)

            preview_path = os.path.join(tempfile.gettempdir(), "boltide_css_preview.html")
            sample_html = (
                "<!DOCTYPE html><html><head><meta charset='utf-8'>"
                "<title>CSS Live Preview</title>"
                f"<style>{code}</style></head><body>"
                "<div class='card'>"
                "<h1>CSS Live Preview</h1>"
                "<p>This sample card uses your <code>body</code>, <code>.card</code>, "
                "<code>h1</code>, <code>p</code>, and <code>button</code> styles.</p>"
                "<input type='text' placeholder='Sample input'><br><br>"
                "<button>Sample Button</button>"
                "</div></body></html>"
            )
            with open(preview_path, "w", encoding="utf-8") as f:
                f.write(sample_html)

            target_url = "file://" + os.path.abspath(preview_path)
            webbrowser.open(target_url)
            show_console()
            append_output(f"\n[Opened CSS preview in default browser: {target_url}]\n")
            return "break"

        # --- All other languages (Python, JS, C++, Go, etc.) run here in the console ---
        show_console()
        console_box.config(state="normal")
        console_box.delete("1.0", END)
        console_box.config(state="disabled")

        runner.run_code(code, lang, ext, current_file_path)
        return "break"

    def stop_running_process(event=None):
        if find_visible:
            return close_find_bar()
        runner.stop()
        return "break"

    def new_file(event=None):
        global current_file_path
        runner.stop()
        current_file_path = None
        lang = lang_var.get()
        code_editor.delete("1.0", END)
        code_editor.insert("1.0", LANGUAGES[lang]["starter"])
        highlight_syntax()
        update_line_numbers()
        hide_console()
        root.title("NorIDE - Unsaved")
        return "break"

    def open_file(event=None):
        global current_file_path
        file_path = askopenfilename(
            filetypes=[
                ("Supported Code", "*.py *.js *.ts *.cpp *.c *.cs *.go *.rs *.java *.lua *.asm *.php *.rb *.sql *.R *.sh *.json *.swift *.yaml *.yml *.xml *.pl *.html *.css *.txt"),
                ("Perl Files", "*.pl;*.pm"),
                ("XML Files", "*.xml;*.svg;*.xsd"),
                ("YAML Files", "*.yaml;*.yml"),
                ("Swift Files", "*.swift"),
                ("JSON Files", "*.json"),
                ("Shell Scripts", "*.sh;*.bash"),
                ("R Files", "*.R;*.r"),
                ("CSS Files", "*.css"),
                ("SQL Files", "*.sql"),
                ("TypeScript Files", "*.ts;*.tsx"),
                ("Ruby Files", "*.rb"),
                ("PHP Files", "*.php"),
                ("Assembly Files", "*.asm;*.s"),
                ("Lua Files", "*.lua"),
                ("HTML Files", "*.html;*.htm"),
                ("Java Files", "*.java"),
                ("Rust Files", "*.rs"),
                ("Go Files", "*.go"),
                ("Python Files", "*.py"),
                ("JavaScript Files", "*.js"),
                ("C++ Files", "*.cpp"),
                ("C Files", "*.c"),
                ("C# Files", "*.cs"),
                ("All Files", "*.*"),
            ]
        )
        if file_path:
            runner.stop()
            current_file_path = file_path

            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            if ext in EXT_TO_LANG:
                lang_var.set(EXT_TO_LANG[ext])
                code_editor.config(wrap=WORD if EXT_TO_LANG[ext] == "Text" else NONE)

            with open(file_path, "r", encoding="utf-8") as f:
                code_editor.delete("1.0", END)
                code_editor.insert("1.0", f.read())
            highlight_syntax()
            update_line_numbers()
            root.title(f"NorIDE - {os.path.basename(file_path)}")
        return "break"

    def save_file(event=None):
        global current_file_path
        lang = lang_var.get()
        cfg = LANGUAGES[lang]

        if not current_file_path:
            file_path = asksaveasfilename(
                defaultextension=cfg["ext"], filetypes=cfg["filetypes"]
            )
            if not file_path:
                return "break"
            current_file_path = file_path

        with open(current_file_path, "w", encoding="utf-8") as f:
            f.write(code_editor.get("1.0", "end-1c"))
        root.title(f"NorIDE - {os.path.basename(current_file_path)}")
        return "break"

    # --- Menu Bar & Toolbar ---
    menubar = Menu(root)
    root.config(menu=menubar)


    toolbar = Frame(root, relief=RAISED, borderwidth=1)
    toolbar.pack(side=TOP, fill=X)
    Button(toolbar, text="New", command=new_file).pack(side=LEFT, padx=2, pady=2)
    Button(toolbar, text="Open", command=open_file).pack(side=LEFT, padx=2, pady=2)
    Button(toolbar, text="Save", command=save_file).pack(side=LEFT, padx=2, pady=2)

    Label(toolbar, text="Language:").pack(side=LEFT, padx=(10, 4), pady=2)
    lang_var = StringVar(value="Python")
    lang_combo = Combobox(
        toolbar,
        textvariable=lang_var,
        values=list(LANGUAGES.keys()),
        state="readonly",
        width=12,
    )
    lang_combo.pack(side=LEFT, padx=2, pady=2)
    lang_combo.bind(ev(ev("ComboboxSelected")), on_language_change)

    Button(toolbar, text="▶ Run", command=run_editor_code).pack(side=LEFT, padx=(10, 2), pady=2)
    Button(toolbar, text="■ Stop", command=stop_running_process).pack(side=LEFT, padx=2, pady=2)
    Label(toolbar, text="Theme:").pack(side=LEFT, padx=(10, 4), pady=2)
    theme_var = StringVar(value="Dark")
    theme_combo = Combobox(
        toolbar,
        textvariable=theme_var,
        values=list(THEMES.keys()),
        state="readonly",
        width=7,
    )
    theme_combo.pack(side=LEFT, padx=2, pady=2)
    theme_combo.bind(ev(ev("ComboboxSelected")), lambda e: apply_theme(theme_var.get()))

    Label(toolbar, text="Size:").pack(side=LEFT, padx=(8, 4), pady=2)
    font_var = StringVar(value="11")
    font_combo = Combobox(
        toolbar,
        textvariable=font_var,
        values=["9", "10", "11", "12", "14", "16", "18", "20", "24"],
        state="readonly",
        width=4,
    )
    font_combo.pack(side=LEFT, padx=2, pady=2)
    font_combo.bind(ev(ev("ComboboxSelected")), on_font_select)

    Button(toolbar, text="Color", command=pick_font_color).pack(side=LEFT, padx=4, pady=2)

    # ---------------------------------------------------

    toggle_console_btn = Button(toolbar, text="Show Console", command=toggle_console)
    toggle_console_btn.pack(side=RIGHT, padx=4, pady=2)
    Button(toolbar, text="Find", command=open_find_bar).pack(side=RIGHT, padx=2, pady=2)

    # --- Hidden Find & Replace Bar (Opens on Ctrl+F) ---
    find_frame = Frame(root, relief=GROOVE, borderwidth=1)
    Label(find_frame, text="Find:").pack(side=LEFT, padx=(4, 2), pady=2)
    find_entry = Entry(find_frame, width=18)
    find_entry.pack(side=LEFT, padx=2, pady=2)
    find_entry.bind(ev("Return"), find_next)

    Button(find_frame, text="Next", command=find_next).pack(side=LEFT, padx=2, pady=2)

    Label(find_frame, text="Replace:").pack(side=LEFT, padx=(8, 2), pady=2)
    replace_entry = Entry(find_frame, width=18)
    replace_entry.pack(side=LEFT, padx=2, pady=2)
    replace_entry.bind(ev("Return"), replace_one)

    Button(find_frame, text="Replace", command=replace_one).pack(side=LEFT, padx=2, pady=2)
    Button(find_frame, text="All", command=replace_all).pack(side=LEFT, padx=2, pady=2)

    find_status = Label(find_frame, text="", width=9)
    find_status.pack(side=LEFT, padx=4)
    Button(find_frame, text="✕", width=3, command=close_find_bar).pack(side=RIGHT, padx=2, pady=2)

    # --- Split Screen (Single PanedWindow) ---
    paned = PanedWindow(root, orient=VERTICAL)
    paned.pack(expand=True, fill=BOTH, padx=5, pady=5)

    editor_frame = Frame(paned)
    paned.add(editor_frame, weight=3)

    line_numbers = Canvas(editor_frame, width=42, bg="#181818", highlightthickness=0)
    line_numbers.pack(side=LEFT, fill=Y)

    code_editor = ScrolledText(
        editor_frame,
        font=("Consolas", 11),
        undo=True,
        wrap=NONE,
        bg="#1e1e1e",
        fg="#d4d4d4",
        insertbackground="white",
    )
    code_editor.pack(side=RIGHT, expand=True, fill=BOTH)

    code_editor.config(
        yscrollcommand=lambda *args: (code_editor.vbar.set(*args), update_line_numbers())
    )
    code_editor.bind(ev("Configure"), update_line_numbers)
    code_editor.bind(ev("MouseWheel"), lambda e: root.after(1, update_line_numbers))

    code_editor.tag_configure("keyword", foreground="#569cd6")
    code_editor.tag_configure("builtin", foreground="#dcdcaa")
    code_editor.tag_configure("string", foreground="#ce9178")
    code_editor.tag_configure("number", foreground="#b5cea8")
    code_editor.tag_configure("comment", foreground="#6a9955")
    code_editor.tag_configure("search_match", background="#515c6a", foreground="#ffffff")
    code_editor.tag_raise("string")
    code_editor.tag_raise("comment")
    code_editor.tag_raise("search_match")

    code_editor.bind(ev("KeyRelease"), highlight_syntax)
    code_editor.bind(ev("Tab"), insert_spaces)
    code_editor.bind(ev("Return"), auto_indent)
    code_editor.bind(ev("Key"), auto_close_pair)
    code_editor.bind(ev("BackSpace"), smart_backspace)

    console_box = ScrolledText(
        paned,
        state="disabled",
        bg="#141414",
        fg="#ffffff",
        font=("Consolas", 10),
        height=8,
    )

    input_frame = Frame(root)
    Label(input_frame, text="Input:").pack(side=LEFT, padx=(0, 5))
    input_entry = Entry(input_frame)
    input_entry.pack(side=LEFT, expand=True, fill=X)
    input_entry.bind(ev("Return"), send_input)
    Button(input_frame, text="Send", command=send_input).pack(side=RIGHT, padx=(5, 0))

    code_editor.insert("1.0", LANGUAGES["Python"]["starter"])
    highlight_syntax()
    root.after(50, update_line_numbers)

    def duplicate_line(event=None):
        """Duplicates the current line directly below."""
        line_text = code_editor.get("insert linestart", "insert lineend")
        code_editor.insert("insert lineend", "\n" + line_text)
        highlight_syntax()
        update_line_numbers()
        return "break"

    def toggle_comment(event=None):
        """Adds or removes the current language's comment symbol on the current line."""
        lang = lang_var.get()
        # Pick the single-line comment symbol for the active language
        if lang in ("Python", "R", "Shell", "Ruby", "Ruby on Rails", "YAML", "Perl"):
            prefix = "# "
        elif lang == "Lua" or lang == "SQL":
            prefix = "-- "
        elif lang == "Assembly":
            prefix = "; "
        else:
            prefix = "// "

        line_start = code_editor.index("insert linestart")
        line_text = code_editor.get(line_start, "insert lineend")
        stripped = line_text.lstrip(" ")
        indent = " " * (len(line_text) - len(stripped))

        if stripped.startswith(prefix.strip()):
            # Remove comment
            uncommented = stripped[len(prefix):] if stripped.startswith(prefix) else stripped[len(prefix.strip()):]
            code_editor.delete(line_start, "insert lineend")
            code_editor.insert(line_start, indent + uncommented)
        else:
            # Add comment
            code_editor.delete(line_start, "insert lineend")
            code_editor.insert(line_start, indent + prefix + stripped)

        highlight_syntax()
        return "break"


    def handle_shortcuts(event):
        ctrl = (event.state & 0x4) != 0 or (event.state & 0x40000) != 0
        shift = (event.state & 0x1) != 0
        key = event.keysym.lower()
        ch = event.char

        # Function & Escape keys
        if key == "f5" and not shift:
            return run_editor_code()
        elif key == "escape" or (key == "f5" and shift):
            return stop_running_process()

        # Existing Ctrl shortcuts
        elif (ctrl and key == "r") or ch == "\x12":
            return run_editor_code()
        elif (ctrl and key == "s") or ch == "\x13":
            return save_file()
        elif (ctrl and key == "o") or ch == "\x0f":
            return open_file()
        elif (ctrl and key == "n") or ch == "\x0e":
            return new_file()
        elif (ctrl and key == "f") or ch == "\x06":
            return open_find_bar()
        elif (ctrl and key == "j") or ch == "\x0a":
            return toggle_console()
        elif (ctrl and key == "t") or ch == "\x14":
            return toggle_theme()
        elif (ctrl and key in ("plus", "equal", "kp_add")) or ch == "\x1d":
            return change_font_size(1)
        elif (ctrl and key in ("minus", "kp_subtract")) or ch == "\x1f":
            return change_font_size(-1)
        elif (ctrl and key == "q") or ch == "\x11":
            on_close()
            return "break"
        elif (ctrl and key == "d") or ch == "\x04":
            return duplicate_line()
        elif ctrl and key in ("slash", "kp_divide", "7"):
            return toggle_comment()

        
    def on_close():
        save_settings()
        runner.stop()
        try:
          root.destroy()
        except Exception:
          pass


    root.protocol("WM_DELETE_WINDOW", on_close)
    root.title("NorIDE")

    apply_theme(current_theme)
    change_font_size(0)
    code_editor.focus_set()
    root.mainloop()



except Exception:
    messagebox.showerror("main.py Startup Error", traceback.format_exc())