#!/usr/bin/env python3
import tkinter as tk
from tkinter import tk, filedialog, messagebox
import os
import time
import zipfile
import shutil
import ast
import operator as op

# -------------------- Utilities --------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
NOTES_DIR = os.path.join(BASE_DIR, 'notes')
if not os.path.exists(NOTES_DIR):
    os.makedirs(NOTES_DIR, exist_ok=True)

# Safe eval for calculator using ast
# Supported binary: + - * / ** %
# Supported unary: + - (UAdd, USub)
allowed_binops = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    # floor division intentionally omitted, but you can add ast.FloorDiv: op.floordiv
}  
allowed_unaryops = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}

def safe_eval(expr: str):
    """Evaluate arithmetic expression safely using AST."""
    try:
        node = ast.parse(expr, mode='eval')
        return _eval(node.body)
    except Exception as e:
        raise ValueError("Invalid expression") from e

def _eval(node):
    # numbers (compat for different Python versions)
    if isinstance(node, ast.Constant):  # Python 3.8+
        if isinstance(node.value, (int, float)):
            return node.value
        else:
            raise ValueError("Only numbers allowed")
    if isinstance(node, ast.Num):  # older ast
        return node.n

    if isinstance(node, ast.BinOp):
        if type(node.op) not in allowed_binops:
            raise ValueError("Operator not allowed")
        left = _eval(node.left)
        right = _eval(node.right)
        return allowed_binops[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp):
        if type(node.op) not in allowed_unaryops:
            raise ValueError("Unary operator not allowed")
        val = _eval(node.operand)
        return allowed_unaryops[type(node.op)](val)

    # allow grouping parentheses etc because ast handles them via subnodes
    raise ValueError("Unsupported expression")

# -------------------- GUI --------------------
class ProductivitySuite(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Colorful Productivity Suite")
        self.geometry("900x600")
        self.minsize(800, 500)
        self.style = tk.Style(self)
        self.configure(bg="#f7f3ff")
        self.create_header()
        self.create_tabs()

    def create_header(self):
        header = tk.Frame(self, bg="#6C5CE7", height=70)
        header.pack(fill='x')
        title = tk.Label(header, text="✨ Productivity Suite", bg="#6C5CE7", fg="white",
                         font=("Segoe UI", 18, "bold"))
        title.pack(side='left', padx=20, pady=12)
        subtitle = tk.Label(header, text="Calculator • Notes • File Organizer • Timer", bg="#6C5CE7", fg="#EDE7FF",
                            font=("Segoe UI", 10))
        subtitle.pack(side='left', padx=10, pady=16)

    def create_tabs(self):
        notebook = tk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=12, pady=12)

        # Calculator Tab
        calc_frame = tk.Frame(notebook)
        self.build_calculator(calc_frame)
        notebook.add(calc_frame, text="Calculator")

        # Notes Tab
        notes_frame = tk.Frame(notebook)
        self.build_notes(notes_frame)
        notebook.add(notes_frame, text="Notes")

        # File Organizer Tab
        files_frame = tk.Frame(notebook)
        self.build_file_organizer(files_frame)
        notebook.add(files_frame, text="File Organizer")

        # Timer Tab
        timer_frame = tk.Frame(notebook)
        self.build_timer(timer_frame)
        notebook.add(timer_frame, text="Timer")

    # ---------------- Calculator ----------------
    def build_calculator(self, parent):
        # ttk.Frame uses 'padding' option; parent is a ttk.Frame
        parent.configure(padding=12)
        frame = tk.Frame(parent, bg="#F0EEFF")
        frame.pack(fill='both', expand=True, padx=8, pady=8)

        self.expr_var = tk.StringVar()
        self.result_var = tk.StringVar()

        expr_entry = tk.Entry(frame, textvariable=self.expr_var, font=("Segoe UI", 16))
        expr_entry.pack(fill='x', padx=12, pady=12)
        expr_entry.focus_set()

        result_label = tk.Label(frame, textvariable=self.result_var, font=("Segoe UI", 16, "bold"), bg="#F0EEFF")
        result_label.pack(anchor='e', padx=12)

        btn_frame = tk.Frame(frame, bg="#F0EEFF")
        btn_frame.pack(pady=10)

        buttons = [
            ('7','8','9','/'),
            ('4','5','6','*'),
            ('1','2','3','-'),
            ('0','.','=','+'),
        ]
        def click(val):
            if val == '=':
                try:
                    res = safe_eval(self.expr_var.get())
                    self.result_var.set(str(res))
                except Exception:
                    self.result_var.set("Error")
            else:
                self.expr_var.set(self.expr_var.get() + val) 

        for r, row in enumerate(buttons):
            for c, ch in enumerate(row):
                b = tk.Button(btn_frame, text=ch, command=lambda v=ch: click(v), width=6)
                b.grid(row=r, column=c, padx=6, pady=6)

        clear_btn = tk.Button(frame, text="Clear", command=lambda: (self.expr_var.set(''), self.result_var.set('')))
        clear_btn.pack(pady=6)

        # Bind Enter to evaluate and Backspace to remove last char if focus not in entry
        self.bind('<Return>', lambda e: click('='))
        self.bind('<BackSpace>', lambda e: self.expr_var.set(self.expr_var.get()[:-1]) if self.focus_get() not in (expr_entry,) else None)

    # ---------------- Notes ----------------
    def build_notes(self, parent):
        parent.configure(padding=12)
        left = tk.Frame(parent, width=260, bg="#FFF6E5")
        left.pack(side='left', fill='y', padx=(0,8), pady=8)

        right = tk.Frame(parent, bg="#FFFFFF")
        right.pack(side='left', fill='both', expand=True, padx=8, pady=8)

        # Left: list of notes
        lbl = tk.Label(left, text="Your Notes", bg="#FFF6E5", font=("Segoe UI", 12, "bold"))
        lbl.pack(pady=8)
        self.notes_listbox = tk.Listbox(left)
        self.notes_listbox.pack(fill='y', expand=True, padx=8, pady=8)
        self.refresh_notes_list()

        btn_frame = tk.Frame(left, bg="#FFF6E5")
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="New", command=self.new_note).grid(row=0, column=0, padx=4)
        tk.Button(btn_frame, text="Load", command=self.load_selected_note).grid(row=0, column=1, padx=4)
        tk.Button(btn_frame, text="Delete", command=self.delete_selected_note).grid(row=0, column=2, padx=4)

        # Right: editor
        title_frame = tk.Frame(right, bg="#FFFFFF")
        title_frame.pack(fill='x')
        tk.Label(title_frame, text="Title:", bg="#FFFFFF").pack(side='left', padx=6, pady=6)
        self.note_title_var = tk.StringVar()
        tk.Entry(title_frame, textvariable=self.note_title_var).pack(side='left', fill='x', expand=True, padx=6)

        self.note_text = tk.Text(right, wrap='word', font=("Segoe UI", 11))
        self.note_text.pack(fill='both', expand=True, padx=6, pady=8)

        save_frame = tk.Frame(right, bg="#FFFFFF")
        save_frame.pack(fill='x')
        tk.Button(save_frame, text="Save Note", command=self.save_note).pack(side='left', padx=6, pady=8)
        tk.Button(save_frame, text="Save As...", command=self.save_note_as).pack(side='left', padx=6, pady=8)

    def refresh_notes_list(self):
        self.notes_listbox.delete(0, tk.END)
        try:
            for fname in sorted(os.listdir(NOTES_DIR)):
                if fname.endswith('.txt'):
                    self.notes_listbox.insert(tk.END, fname)
        except FileNotFoundError:
            os.makedirs(NOTES_DIR, exist_ok=True)

    def new_note(self):
        self.note_title_var.set("New Note")
        self.note_text.delete('1.0', tk.END)

    def save_note(self):
        title = self.note_title_var.get().strip() or "untitled"
        safe_name = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not safe_name: 
            safe_name = "untitled"
        fname = safe_name + ".txt"
        path = os.path.join(NOTES_DIR, fname)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.note_text.get('1.0', tk.END))
        messagebox.showinfo("Saved", f"Saved note as {fname}")
        self.refresh_notes_list()

    def save_note_as(self):
        fpath = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text files', '*.txt')])
        if fpath:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(self.note_text.get('1.0', tk.END))
            messagebox.showinfo("Saved", f"Saved note to {fpath}")
            self.refresh_notes_list()

    def load_selected_note(self):
        sel = self.notes_listbox.curselection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a note to load")
            return
        fname = self.notes_listbox.get(sel[0])
        path = os.path.join(NOTES_DIR, fname)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")
            return
        self.note_title_var.set(os.path.splitext(fname)[0])
        self.note_text.delete('1.0', tk.END)
        self.note_text.insert(tk.END, data)

    def delete_selected_note(self):
        sel = self.notes_listbox.curselection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a note to delete")
            return
        fname = self.notes_listbox.get(sel[0])
        path = os.path.join(NOTES_DIR, fname)
        if messagebox.askyesno("Delete", f"Delete {fname}?"):
            try:
                os.remove(path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {e}")
            self.refresh_notes_list()

    # ---------------- File Organizer ----------------
    def build_file_organizer(self, parent):
        parent.configure(padding=12)
        frame = tk.Frame(parent, bg="#F0FFF6")
        frame.pack(fill='both', expand=True, padx=8, pady=8)

        label = tk.Label(frame, text="Choose a folder to organize (files will be moved into subfolders by extension)", bg="#F0FFF6")
        label.pack(padx=12, pady=12)

        self.org_path_var = tk.StringVar()
        path_entry = tk.Entry(frame, textvariable=self.org_path_var)
        path_entry.pack(fill='x', padx=12, pady=6)

        browse_btn = tk.Button(frame, text="Browse", command=self.browse_folder)
        browse_btn.pack(padx=12, pady=6)

        tk.Button(frame, text="Organize", command=self.organize_folder).pack(pady=8)

        self.org_log = tk.Text(frame, height=10, state='disabled')
        self.org_log.pack(fill='both', expand=True, padx=12, pady=8)

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.org_path_var.set(path)

    def append_log(self, text):
        self.org_log.configure(state='normal')
        self.org_log.insert(tk.END, text + "\n")
        self.org_log.see(tk.END)
        self.org_log.configure(state='disabled')

    def organize_folder(self):
        path = self.org_path_var.get().strip()
        if not path or not os.path.isdir(path):
            messagebox.showwarning("Invalid", "Please select a valid folder to organize")
            return
        self.append_log(f"Organizing: {path}") 
        for fname in os.listdir(path):
            full = os.path.join(path, fname)
            if os.path.isfile(full):
                ext = os.path.splitext(fname)[1].lower().lstrip('.') or 'no_ext'
                target_dir = os.path.join(path, ext + "_files")
                os.makedirs(target_dir, exist_ok=True)
                dest = os.path.join(target_dir, fname)
                try:
                    shutil.move(full, dest)
                    self.append_log(f"Moved: {fname} -> {os.path.basename(target_dir)}/")
                except Exception as e:
                    self.append_log(f"Failed: {fname} ({e})")
        self.append_log("Done.")

    # ---------------- Timer ----------------
    def build_timer(self, parent):
        parent.configure(padding=12)

        frame = tk.Frame(parent, bg="#FFF0F6")
        frame.pack(fill='both', expand=True, padx=8, pady=8)

        # Countdown
        cd_frame = tk.LabelFrame(frame, text="Countdown Timer", bg="#FFF0F6")
        cd_frame.pack(fill='x', padx=8, pady=8)

        self.cd_minutes = tk.IntVar(value=0)
        self.cd_seconds = tk.IntVar(value=30)
        tk.Spinbox(cd_frame, from_=0, to=999, textvariable=self.cd_minutes, width=6).pack(side='left', padx=6, pady=6)
        tk.Label(cd_frame, text="min", bg="#FFF0F6").pack(side='left')
        tk.Spinbox(cd_frame, from_=0, to=59, textvariable=self.cd_seconds, width=6).pack(side='left', padx=6)
        tk.Label(cd_frame, text="sec", bg="#FFF0F6").pack(side='left')

        self.cd_status_var = tk.StringVar(value="Stopped")
        self.cd_display_var = tk.StringVar(value="00:30")
        tk.Label(cd_frame, textvariable=self.cd_display_var, font=("Segoe UI", 16)).pack(side='right', padx=12)

        cd_btn_frame = tk.Frame(cd_frame, bg="#FFF0F6")
        cd_btn_frame.pack(fill='x', pady=6)
        tk.Button(cd_btn_frame, text="Start", command=self.start_countdown).pack(side='left', padx=6)
        tk.Button(cd_btn_frame, text="Stop", command=self.stop_countdown).pack(side='left', padx=6)
        tk.Button(cd_btn_frame, text="Reset", command=self.reset_countdown).pack(side='left', padx=6)
        tk.Label(cd_btn_frame, textvariable=self.cd_status_var, bg="#FFF0F6").pack(side='left', padx=8)

        # Stopwatch
        sw_frame = tk.LabelFrame(frame, text="Stopwatch", bg="#FFF0F6")
        sw_frame.pack(fill='x', padx=8, pady=8)
        self.sw_display_var = tk.StringVar(value="00:00:00")
        tk.Label(sw_frame, textvariable=self.sw_display_var, font=("Segoe UI", 16)).pack(side='left', padx=12)
        sw_btn_frame = tk.Frame(sw_frame, bg="#FFF0F6")
        sw_btn_frame.pack(side='left', padx=8)
        tk.Button(sw_btn_frame, text="Start", command=self.start_stopwatch).pack(side='left', padx=6)
        tk.Button(sw_btn_frame, text="Stop", command=self.stop_stopwatch).pack(side='left', padx=6)
        tk.Button(sw_btn_frame, text="Reset", command=self.reset_stopwatch).pack(side='left', padx=6)

        # countdown internal
        self._cd_running = False
        self._cd_total = 30
        self._cd_remaining = 30
        self._cd_after_id = None

        # stopwatch internal
        self._sw_running = False
        self._sw_start_time = None
        self._sw_elapsed = 0.0
        self._sw_after_id = None

    # Countdown methods (use after-based loop)
    def start_countdown(self):
        if self._cd_running:
            return
        mins = int(self.cd_minutes.get())
        secs = int(self.cd_seconds.get())
        total = mins*60 + secs
        if total <= 0:
            messagebox.showwarning("Invalid", "Set a time greater than 0")
            return
        self._cd_total = total
        self._cd_remaining = total
        self._cd_running = True
        self.cd_status_var.set("Running")
        self._cd_tick()

    def _cd_tick(self):
        if not self._cd_running:
            return
        t = self._cd_remaining
        mins, secs = divmod(t, 60)
        self.cd_display_var.set(f"{mins:02d}:{secs:02d}")
        if t <= 0:
            self._cd_running = False
            self.cd_status_var.set("Finished")
            # schedule messagebox on main loop
            self.after(100, lambda: messagebox.showinfo("Timer", "Countdown finished!"))
            return
        self._cd_remaining -= 1
        self._cd_after_id = self.after(1000, self._cd_tick) 

    def stop_countdown(self):
        self._cd_running = False
        if self._cd_after_id:
            self.after_cancel(self._cd_after_id)
            self._cd_after_id = None
        self.cd_status_var.set("Stopped")

    def reset_countdown(self):
        self.stop_countdown()
        mins = int(self.cd_minutes.get())
        secs = int(self.cd_seconds.get())
        total = mins*60 + secs
        self._cd_total = total
        self._cd_remaining = total
        self.cd_display_var.set(f"{mins:02d}:{secs:02d}")

    # Stopwatch methods (use after-based loop)
    def start_stopwatch(self):
        if self._sw_running:
            return
        self._sw_running = True
        self._sw_start_time = time.time() - self._sw_elapsed
        self._sw_tick()

    def _sw_tick(self):
        if not self._sw_running:
            return
        self._sw_elapsed = time.time() - self._sw_start_time
        hrs, rem = divmod(self._sw_elapsed, 3600)
        mins, secs = divmod(rem, 60)
        self.sw_display_var.set(f"{int(hrs):02d}:{int(mins):02d}:{int(secs):02d}")
        self._sw_after_id = self.after(200, self._sw_tick)

    def stop_stopwatch(self):
        if not self._sw_running:
            return
        self._sw_running = False
        if self._sw_after_id:
            self.after_cancel(self._sw_after_id)
            self._sw_after_id = None

    def reset_stopwatch(self):
        self.stop_stopwatch()
        self._sw_elapsed = 0.0
        self.sw_display_var.set("00:00:00")

# -------------------- Run --------------------
def main():
    app = ProductivitySuite()
    app.mainloop()


if __name__ == '__main__':
    main()
