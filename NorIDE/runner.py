import os
import subprocess
import tempfile
import threading
from languages import get_commands


class CodeRunner:
    def __init__(self, root, on_output):
        self.root = root
        self.on_output = on_output
        self.current_process = None
        self.current_run_id = 0

    def emit(self, text, run_id=None):
        if run_id is not None and run_id != self.current_run_id:
            return
        self.root.after(0, self.on_output, text)

    def stop(self):
        self.current_run_id += 1
        if self.current_process and self.current_process.poll() is None:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=1)
            except Exception:
                try:
                    self.current_process.kill()
                except Exception:
                    pass
            self.on_output("\n--- Process stopped ---\n")
        self.current_process = None

    def send_input(self, user_text):
        self.on_output(f"> {user_text}\n")
        if self.current_process and self.current_process.poll() is None:
            try:
                self.current_process.stdin.write(user_text + "\n")
                self.current_process.stdin.flush()
            except Exception as e:
                self.on_output(f"\n[Input Error: {e}]\n")

    def run_code(self, code, lang, ext, file_path=None):
        self.stop()
        self.current_run_id += 1
        run_id = self.current_run_id

        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            commands, exe_path = get_commands(lang, file_path)
            self.on_output(f"Running ({lang}): {file_path}\n" + "-" * 40 + "\n")
            threading.Thread(
                target=self._execute,
                args=(commands, file_path, exe_path, run_id, False),
                daemon=True,
            ).start()
        else:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=ext, mode="w", encoding="utf-8"
            ) as tmp:
                tmp.write(code)
                temp_path = tmp.name
            commands, exe_path = get_commands(lang, temp_path)
            self.on_output(f"Running unsaved {lang} code...\n" + "-" * 40 + "\n")
            threading.Thread(
                target=self._execute,
                args=(commands, temp_path, exe_path, run_id, True),
                daemon=True,
            ).start()

    def _execute(self, commands, file_path, exe_path, run_id, is_temp):
        try:
            for step_index, cmd in enumerate(commands):
                if run_id != self.current_run_id:
                    break

                proc = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                self.current_process = proc

                while True:
                    if run_id != self.current_run_id:
                        break
                    char = proc.stdout.read(1)
                    if not char and proc.poll() is not None:
                        break
                    if char:
                        self.emit(char, run_id)

                proc.wait()
                if proc.returncode != 0 and step_index < len(commands) - 1:
                    self.emit("\n--- Compilation failed ---\n", run_id)
                    return

            self.emit("\n--- Process finished ---\n", run_id)
        except FileNotFoundError as e:
            self.emit(
                f"\n[Compiler/Runtime not found: {e.filename}. Make sure it is installed and in PATH.]\n",
                run_id,
            )
        except Exception as e:
            self.emit(f"\n[Error: {e}]\n", run_id)
        finally:
            if is_temp and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass
            if is_temp and exe_path and os.path.exists(exe_path):
                try:
                    os.remove(exe_path)
                except Exception:
                    pass