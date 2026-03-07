# -*- coding: utf-8 -*-
import customtkinter as ctk
import os
from pathlib import Path

class SearchPanel(ctk.CTkFrame):
    def __init__(self, parent, config, on_file_click):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_file_click = on_file_click
        self.all_results = []
        self.loaded_count = 0
        self.BATCH_SIZE = 50
        self.load_more_btn = None
        
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Tüm dosyalarda ara...", height=35)
        self.search_entry.pack(fill="x", padx=10, pady=10)
        self.search_entry.bind("<Return>", lambda e: self.perform_search())
        
        self.results_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True)

    def perform_search(self):
        query = self.search_entry.get().lower()
        if not query: return
        
        # Temizlik
        for widget in self.results_frame.winfo_children(): widget.destroy()
        self.all_results = []
        self.loaded_count = 0
        self.load_more_btn = None
        
        import threading
        
        def _search_thread():
            search_root = self.master.current_root if hasattr(self.master, 'current_root') else Path(os.getcwd())
            results = []
            for file_path in search_root.rglob("*.tr"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if query in line.lower():
                                results.append((file_path, i+1, line.strip()))
                except: continue
            
            self.after(0, lambda: self._show_results(results))
            
        threading.Thread(target=_search_thread, daemon=True).start()

    def _show_results(self, results):
        self.all_results = results
        if not self.all_results:
            self._add_result(Path("Bulunamadı"), 0, "Arama kriterine uygun sonuç yok.")
            return
        self._load_next_batch()

    def _load_next_batch(self):
        # Eğer daha önce "Daha Fazla" butonu varsa kaldır
        if self.load_more_btn:
            self.load_more_btn.destroy()
            self.load_more_btn = None

        end_idx = min(self.loaded_count + self.BATCH_SIZE, len(self.all_results))
        batch = self.all_results[self.loaded_count:end_idx]
        
        for res in batch:
            self._add_result(res[0], res[1], res[2])
            self.loaded_count += 1
            
        # Eğer hala gösterilecek sonuç varsa buton ekle
        if self.loaded_count < len(self.all_results):
            theme = self.config.THEMES[self.config.theme]
            remaining = len(self.all_results) - self.loaded_count
            self.load_more_btn = ctk.CTkButton(
                self.results_frame, 
                text=f"Daha fazla göster ({remaining} sonuç kaldı)",
                fg_color="transparent",
                border_width=1,
                border_color=theme['hover'],
                text_color=theme['fg'],
                hover_color=theme['hover'],
                command=self._load_next_batch
            )
            self.load_more_btn.pack(fill="x", padx=10, pady=10)

    def _add_result(self, path, line_no, content):
        theme = self.config.THEMES[self.config.theme]
        btn = ctk.CTkButton(self.results_frame, text=f"{path.name}:{line_no}\n{content[:40]}...",
                           anchor="w", fg_color="transparent", hover_color=theme['hover'],
                           text_color=theme['fg'], height=45, font=("Segoe UI", 10),
                           command=lambda p=path: self.on_file_click(str(p)))
        btn.pack(fill="x", padx=5, pady=2)
