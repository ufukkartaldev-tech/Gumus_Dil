
import customtkinter as ctk
import tkinter as tk

class CommandPalette(ctk.CTkToplevel):
    def __init__(self, parent, commands):
        super().__init__(parent)
        self.commands = commands # List of {"label": "...", "command": func}
        
        self.title("Komut Paleti")
        self.geometry("500x350")
        self.overrideredirect(True) # Çerçevesiz
        self.configure(fg_color="transparent")
        
        # Merkezde aç
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 250
        y = parent.winfo_rooty() + 100
        self.geometry(f"+{x}+{y}")
        
        # Ana Kap (Shadow Effect Style)
        self.frame = ctk.CTkFrame(self, corner_radius=10, border_width=2, border_color="#5eccf3") # Neon border
        self.frame.pack(fill="both", expand=True)
        
        # Arama Kutusu
        self.search_entry = ctk.CTkEntry(
            self.frame, 
            placeholder_text="Komut yazın... (Örn: Tema, Kaydet, Çalıştır)",
            height=40,
            font=("Segoe UI", 14),
            border_width=0,
            fg_color="transparent"
        )
        self.search_entry.pack(fill="x", padx=10, pady=(10, 5))
        self.search_entry.focus_set()
        
        # Ayırıcı
        ctk.CTkFrame(self.frame, height=2, fg_color="gray30").pack(fill="x", padx=10, pady=5)
        
        # Sonuç Listesi
        self.results_frame = ctk.CTkScrollableFrame(self.frame, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Eventler
        self.search_entry.bind("<KeyRelease>", self.update_results)
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<FocusOut>", lambda e: self.destroy())
        
        self.update_results()

    def update_results(self, event=None):
        query = self.search_entry.get().lower()
        
        # Temizle
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        # Filtrele ve Göster
        count = 0
        for cmd in self.commands:
            if query in cmd['label'].lower():
                self._add_result(cmd)
                count += 1
                if count >= 8: break # Max 8 sonuç

    def _add_result(self, cmd):
        btn = ctk.CTkButton(
            self.results_frame,
            text=cmd['label'],
            anchor="w",
            fg_color="transparent",
            hover_color=("gray75", "gray25"),
            text_color=("black", "white"),
            height=35,
            command=lambda: self._execute(cmd['command'])
        )
        btn.pack(fill="x", pady=2)

    def _execute(self, func):
        self.destroy()
        func()

