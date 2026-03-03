import customtkinter as ctk
import tkinter as tk

class FindReplacePanel(ctk.CTkFrame):
    def __init__(self, parent, textbox, config, **kwargs):
        theme = config.THEMES[config.theme]
        super().__init__(parent, fg_color=theme['sidebar_bg'], corner_radius=5, border_width=1, border_color=theme['border'], **kwargs)
        self.textbox = textbox
        self.config = config
        self.replace_mode = False
        
        # Üst satır: Bul
        row1 = ctk.CTkFrame(self, fg_color="transparent")
        row1.pack(fill="x", padx=5, pady=5)
        
        self.find_entry = ctk.CTkEntry(row1, placeholder_text="Bul...", width=150, height=28, font=("Segoe UI", 12))
        self.find_entry.pack(side="left", padx=(0, 5))
        self.find_entry.bind("<Return>", self.find_next)
        self.find_entry.bind("<KeyRelease>", self._live_search)
        
        ctk.CTkButton(row1, text="↓", width=24, height=24, command=self.find_next).pack(side="left", padx=1)
        ctk.CTkButton(row1, text="↑", width=24, height=24, command=self.find_prev).pack(side="left", padx=1)
        ctk.CTkButton(row1, text="×", width=24, height=24, fg_color="transparent", hover_color="#c62828", command=self.hide).pack(side="left", padx=(5, 0))
        
        # Alt satır: Değiştir (Opsiyonel)
        self.replace_row = ctk.CTkFrame(self, fg_color="transparent")
        
        self.replace_entry = ctk.CTkEntry(self.replace_row, placeholder_text="Değiştir...", width=150, height=28, font=("Segoe UI", 12))
        self.replace_entry.pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(self.replace_row, text="Değiştir", width=60, height=24, font=("Segoe UI", 11), command=self.replace_one).pack(side="left", padx=1)
        ctk.CTkButton(self.replace_row, text="Tümü", width=50, height=24, font=("Segoe UI", 11), command=self.replace_all).pack(side="left", padx=1)

    def toggle(self, replace_mode=False):
        if self.winfo_ismapped():
            if replace_mode != self.replace_mode:
                self.set_mode(replace_mode)
            else:
                self.hide()
        else:
            self.set_mode(replace_mode)
            self.show()

    def set_mode(self, replace_mode):
        self.replace_mode = replace_mode
        if replace_mode:
            self.replace_row.pack(fill="x", padx=5, pady=(0, 5))
        else:
            self.replace_row.pack_forget()

    def show(self):
        self.place(relx=1.0, rely=0.0, anchor="ne", x=-25, y=5)
        self.lift()
        self.find_entry.focus_set()

    def hide(self):
        self.place_forget()
        self.textbox.tag_remove("search_highlight", "1.0", tk.END)
        self.textbox.focus_set()

    def _live_search(self, event=None):
        query = self.find_entry.get()
        self.textbox.tag_remove("search_highlight", "1.0", tk.END)
        if not query: return
        
        count = 0
        start_pos = "1.0"
        while True:
            pos = self.textbox.search(query, start_pos, stopindex=tk.END)
            if not pos: break
            
            end_pos = f"{pos}+{len(query)}c"
            self.textbox.tag_add("search_highlight", pos, end_pos)
            start_pos = end_pos
            count += 1
            if count > 1000: break # Performans koruması

    def find_next(self, event=None):
        query = self.find_entry.get()
        if not query: return
        
        start_pos = self.textbox.index(tk.INSERT) + "+1c"
        pos = self.textbox.search(query, start_pos, stopindex=tk.END)
        if not pos:
             pos = self.textbox.search(query, "1.0", stopindex=tk.END)
        
        if pos:
            self._highlight_match(pos, len(query))

    def find_prev(self, event=None):
        query = self.find_entry.get()
        if not query: return
        
        start_pos = self.textbox.index(tk.INSERT)
        pos = self.textbox.search(query, start_pos, stopindex="1.0", backwards=True)
        if not pos:
             pos = self.textbox.search(query, tk.END, stopindex="1.0", backwards=True)
             
        if pos:
            self._highlight_match(pos, len(query))

    def _highlight_match(self, pos, length):
        end_pos = f"{pos}+{length}c"
        self.textbox.tag_remove("sel", "1.0", tk.END)
        self.textbox.tag_add("sel", pos, end_pos)
        self.textbox.mark_set(tk.INSERT, end_pos)
        self.textbox.see(pos)

    def replace_one(self):
        query = self.find_entry.get()
        replacement = self.replace_entry.get()
        if not query: return
        
        try:
            sel_start = self.textbox.index("sel.first")
            sel_end = self.textbox.index("sel.last")
            if self.textbox.get(sel_start, sel_end) == query:
                self.textbox.delete(sel_start, sel_end)
                self.textbox.insert(sel_start, replacement)
                self.find_next()
            else:
                self.find_next()
        except:
            self.find_next()

    def replace_all(self):
        query = self.find_entry.get()
        replacement = self.replace_entry.get()
        if not query: return
        
        text = self.textbox.get("1.0", 'end-1c')
        new_text = text.replace(query, replacement)
        
        self.textbox.delete("1.0", tk.END)
        self.textbox.insert("1.0", new_text)
        self._live_search()
