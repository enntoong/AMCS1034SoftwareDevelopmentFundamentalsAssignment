# notes_organizer_app.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import datetime
import webbrowser
import platform
import subprocess

# ----------------- Configuration -----------------
DATA_DIR = "data"

# Field separators and tokens (kept simple & human-readable)
FIELD_SEP = "||"        # separates fields in a single note line
ATT_SEP = ";;"          # separates multiple attachments inside attachments field
NL_TOKEN = "<NL>"       # replaces newline in content for single-line storage
PIPE_TOKEN = "<PIPE>"   # escape for FIELD_SEP if user types it
SEMI_TOKEN = "<SEMI>"   # escape for ATT_SEP if user types it

# Default suggestions
DEFAULT_CATEGORIES = ["General","School","Work","Personal","Study"]
DEFAULT_TAGS = ["Urgent","Todo","Important","Exam"]

# ----------------- Helpers -----------------
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def encode_field(s: str) -> str:
    if s is None:
        return ""
    return s.replace(FIELD_SEP, PIPE_TOKEN).replace(ATT_SEP, SEMI_TOKEN).replace("\n", NL_TOKEN)

def decode_field(s: str) -> str:
    if s is None:
        return ""
    return s.replace(PIPE_TOKEN, FIELD_SEP).replace(SEMI_TOKEN, ATT_SEP).replace(NL_TOKEN, "\n")

def open_path(path: str):
    """Open a file path or URL cross-platform."""
    if path.startswith("http://") or path.startswith("https://"):
        webbrowser.open(path)
        return
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("Open failed", f"Couldn't open '{path}': {e}")

# ----------------- Main App -----------------
class NotesOrganizerApp:
    """
    Notes organizer with per-user storage.

    Signature kept so homepage/login can call: NotesOrganizerApp(root, current_user)
    If current_user is None, 'default_user' is used (useful for standalone testing).
    """
    def __init__(self, root, current_user=None):
        # determine user
        if not current_user:
            current_user = "default_user"
        self.user = current_user

        # prepare per-user paths
        self.user_dir = os.path.join(DATA_DIR, self.user)
        ensure_dir(self.user_dir)
        self.notes_file = os.path.join(self.user_dir, "notes.txt")
        self.categories_file = os.path.join(self.user_dir, "categories.txt")
        self.tags_file = os.path.join(self.user_dir, "tags.txt")

        # ensure files exist
        for p in (self.notes_file, self.categories_file, self.tags_file):
            if not os.path.exists(p):
                open(p, "a", encoding="utf-8").close()

        # UI root
        self.root = root
        self.root.title(f"Notes Organizer - {self.user}")
        self.root.geometry("980x640")
        self.root.config(bg="#f8f9fb")

        # ---------------- UI ----------------
        toolbar = tk.Frame(self.root, bg="#2f3b52", height=58)
        toolbar.pack(side="top", fill="x")

        tk.Label(toolbar, text="📝 Notes Organizer", bg="#2f3b52", fg="white",
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=12)

        tk.Button(toolbar, text="➕ New", command=self.new_note,
                  bg="#28a745", fg="white", relief="flat", padx=10).pack(side="left", padx=8, pady=8)
        tk.Button(toolbar, text="💾 Save", command=self.save_note,
                  bg="#007bff", fg="white", relief="flat", padx=10).pack(side="left", padx=8, pady=8)
        tk.Button(toolbar, text="❌ Delete", command=self.delete_note,
                  bg="#dc3545", fg="white", relief="flat", padx=10).pack(side="left", padx=8, pady=8)

        # Search on toolbar
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(toolbar, textvariable=self.search_var, width=36, font=("Segoe UI", 10))
        search_entry.pack(side="right", padx=8)
        search_entry.bind("<Return>", lambda e: self.search_notes())

        tk.Button(toolbar, text="🔍", command=self.search_notes,
                  bg="#ffc107", fg="black", relief="flat", padx=8).pack(side="right", padx=8, pady=8)

        # Search placeholder
        self._placeholder_text = "Search notes..."
        self.search_var.set(self._placeholder_text)
        search_entry.config(fg="gray")
        def clear_placeholder(event=None):
            if self.search_var.get() == self._placeholder_text:
                self.search_var.set("")
                search_entry.config(fg="black")
        def set_placeholder(event=None):
            if not self.search_var.get():
                self.search_var.set(self._placeholder_text)
                search_entry.config(fg="gray")
        search_entry.bind("<FocusIn>", clear_placeholder)
        search_entry.bind("<FocusOut>", set_placeholder)
        def on_type(*args):
            if search_entry.cget("fg") == "gray":
                search_entry.config(fg="black")
                if self.search_var.get() == self._placeholder_text:
                    self.search_var.set("")
        self.search_var.trace_add("write", on_type)
        set_placeholder()

        # Layout: left list, right editor
        paned = ttk.PanedWindow(self.root, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=12, pady=12)

        # Left
        left_frame = ttk.Frame(paned, width=300)
        paned.add(left_frame, weight=1)

        tk.Label(left_frame, text="Notes", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=(6,2))
        self.notes_listbox = tk.Listbox(left_frame, font=("Segoe UI", 10), activestyle="none", selectmode="extended")
        self.notes_listbox.pack(fill="both", expand=True, padx=8, pady=6)
        self.notes_listbox.bind("<<ListboxSelect>>", lambda e: self.load_selected_note())

        left_buttons = tk.Frame(left_frame)
        left_buttons.pack(fill="x", padx=8, pady=(0,8))
        tk.Button(left_buttons, text="Refresh", command=self.reload_notes, padx=6).pack(side="left")
        tk.Button(left_buttons, text="All", command=self.show_all, padx=6).pack(side="left", padx=6)

        # Right
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)

        # Title
        tk.Label(right_frame, text="Title", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=6, pady=(6,2))
        self.title_entry = tk.Entry(right_frame, font=("Segoe UI", 11))
        self.title_entry.grid(row=0, column=1, columnspan=3, sticky="ew", padx=6, pady=(6,2))
        self.title_entry.bind("<Return>", lambda e: self.category_combo.focus_set())

        # Category
        tk.Label(right_frame, text="Category", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", padx=6, pady=2)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            right_frame,
            textvariable=self.category_var,
            values=self.load_suggestions(self.categories_file, DEFAULT_CATEGORIES),
            state="normal"
        )
        self.category_combo.grid(row=1, column=1, sticky="ew", padx=6, pady=2)
        tk.Button(right_frame, text="➕", width=3, command=lambda: self.add_suggestion_popup(self.categories_file, "Category")).grid(row=1, column=2, padx=4, sticky="w")
        tk.Button(right_frame, text="⚙", width=3, command=lambda: self.manage_suggestions(self.categories_file, "Category", self.category_combo)).grid(row=1, column=3, padx=4, sticky="w")
        self.category_combo.bind("<Return>", lambda e: self.tags_combo.focus_set())

        # Tags
        tk.Label(right_frame, text="Tags (comma separated)", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", padx=6, pady=2)
        self.tags_var = tk.StringVar()
        self.tags_combo = ttk.Combobox(
            right_frame,
            textvariable=self.tags_var,
            values=self.load_suggestions(self.tags_file, DEFAULT_TAGS),
            state="normal"
        )
        self.tags_combo.grid(row=2, column=1, sticky="ew", padx=6, pady=2)
        tk.Button(right_frame, text="➕", width=3, command=lambda: self.add_suggestion_popup(self.tags_file, "Tag")).grid(row=2, column=2, padx=4, sticky="w")
        tk.Button(right_frame, text="⚙", width=3, command=lambda: self.manage_suggestions(self.tags_file, "Tag", self.tags_combo)).grid(row=2, column=3, padx=4, sticky="w")
        self.tags_combo.bind("<Return>", lambda e: self.content_text.focus_set())

        # Attachments list + buttons
        tk.Label(right_frame, text="Attachments", font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="nw", padx=6, pady=(6,2))
        attach_frame = tk.Frame(right_frame)
        attach_frame.grid(row=3, column=1, columnspan=3, sticky="ew", padx=6, pady=(6,2))
        self.attach_listbox = tk.Listbox(attach_frame, height=4, selectmode="extended")
        self.attach_listbox.pack(side="left", fill="x", expand=True)
        self.attach_listbox.bind("<Double-1>", self.open_selected_attachment)
        att_btns = tk.Frame(attach_frame)
        att_btns.pack(side="right", padx=6)
        tk.Button(att_btns, text="Attach File", command=self.attach_file).pack(pady=2)
        tk.Button(att_btns, text="Attach Link", command=self.attach_link).pack(pady=2)
        tk.Button(att_btns, text="Open", command=self.open_attachment).pack(pady=2)
        tk.Button(att_btns, text="Remove", command=self.remove_attachment).pack(pady=2)

        # Content text
        tk.Label(right_frame, text="Content", font=("Segoe UI", 10, "bold")).grid(row=4, column=0, sticky="nw", padx=6, pady=(6,2))
        self.content_text = tk.Text(right_frame, wrap="word", font=("Segoe UI", 11), height=14)
        self.content_text.grid(row=4, column=1, columnspan=3, sticky="nsew", padx=6, pady=(6,8))

        # Delete key bindings (notes and attachments)
        self.notes_listbox.bind("<Delete>", lambda e: self.delete_note())
        self.attach_listbox.bind("<Delete>", lambda e: self.remove_attachment())

        # Enter in content -> save unless Shift+Enter
        def handle_content_enter(event):
            if event.state & 0x0001:  # Shift is pressed
                self.content_text.insert(tk.INSERT, "\n")
                return "break"
            else:
                self.save_note()
                return "break"
        self.content_text.bind("<Return>", handle_content_enter)

        # Configure grid weights
        right_frame.grid_rowconfigure(4, weight=1)
        right_frame.grid_columnconfigure(1, weight=1)

        # Internal state
        self.notes = []            # list of note dicts
        self.filtered_indices = [] # maps listbox index -> notes index
        self.currently_loaded_idx = None  # real index of note loaded into editor, or None

        # Load notes
        self.reload_notes()

    # ----------------- Manage Suggestions -----------------
    def manage_suggestions(self, path, label, combo_widget):
        popup = tk.Toplevel(self.root)
        popup.title(f"Manage {label} Suggestions")
        popup.geometry("300x300")
        popup.grab_set()

        tk.Label(popup, text=f"{label} Suggestions", font=("Segoe UI", 10, "bold")).pack(pady=5)

        listbox = tk.Listbox(popup, font=("Segoe UI", 10), selectmode="extended")
        listbox.pack(fill="both", expand=True, padx=10, pady=5)

        # Load current suggestions
        items = self.load_suggestions(path, DEFAULT_CATEGORIES if "Category" in label else DEFAULT_TAGS)
        for it in items:
            listbox.insert(tk.END, it)

        # Protected defaults
        category_defaults = DEFAULT_CATEGORIES
        tag_defaults = DEFAULT_TAGS
        def get_defaults():
            return category_defaults if "Category" in label else tag_defaults

        def delete_selected():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("No selection", f"Please select at least one {label} to delete.", parent=popup)
                return
            to_delete = [listbox.get(i) for i in sel]
            protected = get_defaults()
            removed = 0
            for d in to_delete:
                if d not in protected and d in items:
                    items.remove(d)
                    removed += 1
            if removed == 0:
                messagebox.showinfo("Protected", "Default suggestions cannot be deleted.", parent=popup)
                return
            # Save updated
            with open(path, "w", encoding="utf-8") as f:
                for it in sorted(items):
                    f.write(it + "\n")
            # Refresh
            combo_widget["values"] = self.load_suggestions(path, [])
            listbox.delete(0, tk.END)
            for it in items:
                listbox.insert(tk.END, it)

        def delete_all():
            protected = get_defaults()
            if messagebox.askyesno("Confirm", f"Delete all {label} suggestions (defaults will stay)?", parent=popup):
                with open(path, "w", encoding="utf-8") as f:
                    for it in protected:
                        f.write(it + "\n")
                combo_widget["values"] = protected
                listbox.delete(0, tk.END)
                for it in protected:
                    listbox.insert(tk.END, it)
                messagebox.showinfo("Deleted", f"All {label} suggestions cleared (defaults kept).", parent=popup)

        # Bind Delete key AFTER delete_selected is defined
        listbox.bind("<Delete>", lambda e: delete_selected())

        tk.Button(popup, text="Delete Selected", command=delete_selected).pack(pady=5)
        tk.Button(popup, text="Delete All", command=delete_all).pack(pady=5)

    # ----------------- Suggestions helpers -----------------
    def load_suggestions(self, path, defaults):
        ensure_dir(self.user_dir)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(defaults))
        with open(path, "r", encoding="utf-8") as f:
            items = [line.strip() for line in f if line.strip()]
        if not items:
            items = defaults
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(defaults))
        return items

    def save_suggestion_line(self, path, new_item):
        items = set(self.load_suggestions(path, []))
        items.add(new_item.strip())
        with open(path, "w", encoding="utf-8") as f:
            for it in sorted(items):
                f.write(it + "\n")
        # refresh combobox values
        if path == self.categories_file:
            self.category_combo["values"] = self.load_suggestions(self.categories_file, DEFAULT_CATEGORIES)
        elif path == self.tags_file:
            self.tags_combo["values"] = self.load_suggestions(self.tags_file, DEFAULT_TAGS)

    def add_suggestion_popup(self, path, label):
        ans = simpledialog.askstring(f"Add {label}", f"Enter new {label}:", parent=self.root)
        if ans and ans.strip():
            self.save_suggestion_line(path, ans.strip())
            messagebox.showinfo("Saved", f"New {label} suggestion saved.", parent=self.root)

    # ----------------- Attachments -----------------
    def attach_file(self):
        p = filedialog.askopenfilename(title="Select file")
        if p:
            self.attach_listbox.insert(tk.END, p)

    def attach_link(self):
        url = simpledialog.askstring("Attach Link", "Paste the URL (http/https):", parent=self.root)
        if url and url.strip():
            self.attach_listbox.insert(tk.END, url.strip())

    def remove_attachment(self):
        sel = list(self.attach_listbox.curselection())
        if not sel:
            messagebox.showwarning("No selection", "Please select one or more attachments to remove.", parent=self.root)
            return
        # delete from listbox highest->lowest to avoid index shift
        for i in reversed(sel):
            self.attach_listbox.delete(i)
        # If a note is currently loaded in the editor and user wants changes applied immediately:
        # we will update the in-memory note attachments (they will be saved on next Save).
        if self.currently_loaded_idx is not None and 0 <= self.currently_loaded_idx < len(self.notes):
            # Rebuild attachments from listbox into the in-memory note
            new_attachments = [self.attach_listbox.get(i) for i in range(self.attach_listbox.size())]
            self.notes[self.currently_loaded_idx]["attachments"] = new_attachments
            # persist to file immediately
            self.save_all_notes()

    def open_selected_attachment(self, event=None):
        sel = self.attach_listbox.curselection()
        if not sel:
            return
        p = self.attach_listbox.get(sel[0])
        open_path(p)

    # ----------------- Notes file format helpers -----------------
    def build_note_line(self, note: dict) -> str:
        title = encode_field(note.get("title",""))
        category = encode_field(note.get("category",""))
        tags = encode_field(note.get("tags",""))
        content = encode_field(note.get("content",""))
        attachments = encode_field(ATT_SEP.join(note.get("attachments",[])))
        date = encode_field(note.get("date",""))
        return FIELD_SEP.join([title, category, tags, content, attachments, date]) + "\n"

    def parse_note_line(self, line: str) -> dict:
        parts = line.rstrip("\n").split(FIELD_SEP)
        while len(parts) < 6:
            parts.append("")
        title = decode_field(parts[0])
        category = decode_field(parts[1])
        tags = decode_field(parts[2])
        content = decode_field(parts[3])
        attachments_str = decode_field(parts[4])
        date = decode_field(parts[5])
        attachments = attachments_str.split(ATT_SEP) if attachments_str else []
        return {"title": title, "category": category, "tags": tags, "content": content, "attachments": attachments, "date": date}

    # ----------------- Load / Save -----------------
    def reload_notes(self):
        """Reload from user's notes file and refresh listbox (clears search/filter)."""
        self.notes.clear()
        ensure_dir(self.user_dir)
        with open(self.notes_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        note = self.parse_note_line(line)
                        self.notes.append(note)
                    except Exception:
                        continue
        # refresh suggestions combobox values
        self.category_combo["values"] = self.load_suggestions(self.categories_file, DEFAULT_CATEGORIES)
        self.tags_combo["values"] = self.load_suggestions(self.tags_file, DEFAULT_TAGS)
        self.show_all()

    def save_all_notes(self):
        ensure_dir(self.user_dir)
        with open(self.notes_file, "w", encoding="utf-8") as f:
            for note in self.notes:
                f.write(self.build_note_line(note))

    # ----------------- UI Actions -----------------
    def show_all(self):
        self.filtered_indices = list(range(len(self.notes)))
        self.refresh_listbox()

    def refresh_listbox(self):
        self.notes_listbox.delete(0, tk.END)
        for idx in self.filtered_indices:
            n = self.notes[idx]
            display = f"{n['title']}  [{n['category']}] - {n.get('date','')}"
            self.notes_listbox.insert(tk.END, display)

    def new_note(self):
        self.title_entry.delete(0, tk.END)
        self.category_combo.set("")
        self.tags_combo.set("")
        self.content_text.delete("1.0", tk.END)
        self.attach_listbox.delete(0, tk.END)
        self.notes_listbox.selection_clear(0, tk.END)
        self.currently_loaded_idx = None

    def save_note(self):
        title = self.title_entry.get().strip()
        category = self.category_var.get().strip() if self.category_var.get().strip() else "General"
        tags = self.tags_var.get().strip()
        content = self.content_text.get("1.0", tk.END).rstrip("\n")
        attachments = [self.attach_listbox.get(i) for i in range(self.attach_listbox.size())]
        if not title:
            messagebox.showwarning("Validation", "Please enter a title.", parent=self.root)
            return
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        note = {"title": title, "category": category, "tags": tags, "content": content, "attachments": attachments, "date": date}

        # If a note is selected -> update original note (we need to map index)
        sel = self.notes_listbox.curselection()
        if sel:
            listbox_i = sel[0]
            if listbox_i < len(self.filtered_indices):
                real_idx = self.filtered_indices[listbox_i]
                self.notes[real_idx] = note
                self.currently_loaded_idx = real_idx
        else:
            self.notes.append(note)
            # set currently_loaded_idx to last appended
            self.currently_loaded_idx = len(self.notes) - 1

        # persist new category/tag suggestions if they are new
        if category:
            self.save_suggestion_line(self.categories_file, category)
        if tags:
            for t in [tt.strip() for tt in tags.split(",") if tt.strip()]:
                self.save_suggestion_line(self.tags_file, t)

        self.save_all_notes()
        self.reload_notes()
        messagebox.showinfo("Saved", "Note saved successfully.", parent=self.root)
        self.new_note()

    def delete_note(self):
        sel = self.notes_listbox.curselection()
        if not sel:
            messagebox.showwarning("Select", "Please select at least one note to delete.", parent=self.root)
            return
        confirm = messagebox.askyesno("Confirm", f"Delete {len(sel)} selected note(s)?", parent=self.root)
        if not confirm:
            return
        for listbox_i in reversed(sel):
            real_idx = self.filtered_indices[listbox_i]
            # protect index range
            if 0 <= real_idx < len(self.notes):
                del self.notes[real_idx]
        self.save_all_notes()
        self.reload_notes()
        self.new_note()

    def load_selected_note(self):
        sel = self.notes_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        real_idx = self.filtered_indices[idx]
        if not (0 <= real_idx < len(self.notes)):
            return
        note = self.notes[real_idx]
        # populate editor
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, note["title"])
        self.category_combo.set(note["category"])
        self.tags_combo.set(note["tags"])
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert("1.0", note["content"])
        self.attach_listbox.delete(0, tk.END)
        for a in note.get("attachments", []):
            self.attach_listbox.insert(tk.END, a)
        self.currently_loaded_idx = real_idx

    def open_attachment(self):
        sel = self.attach_listbox.curselection()
        if not sel:
            messagebox.showwarning("Open", "Select an attachment.", parent=self.root)
            return
        p = self.attach_listbox.get(sel[0])
        open_path(p)

    def search_notes(self, event=None):
        q = self.search_var.get().strip().lower()
        # Ignore placeholder
        if q == self._placeholder_text:
            q = ""
        self.filtered_indices = []
        if not q:
            self.filtered_indices = list(range(len(self.notes)))
        else:
            for i, n in enumerate(self.notes):
                combined = " ".join([
                    n.get("title", ""),
                    n.get("tags", ""),
                    n.get("category", ""),
                    n.get("content", "")
                ]).lower()
                if q in combined:
                    self.filtered_indices.append(i)
            if not self.filtered_indices:
                messagebox.showerror("Not Found", f"No notes found for '{q}'", parent=self.root)
        self.refresh_listbox()

# ----------------- Run standalone -----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = NotesOrganizerApp(root, "testuser")
    root.mainloop()
