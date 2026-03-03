# -*- coding: utf-8 -*-
import customtkinter as ctk
import json
import shutil

class TrainingPanel(ctk.CTkFrame):
    def __init__(self, parent, config, on_load_task):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_load_task = on_load_task # callback(task_code, instructions)
        
        # Görev Veritabanı
        self.tasks = []
        self._load_tasks_from_json()
        
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        self._load_tasks_ui()
        
    def _load_tasks_from_json(self):
        try:
            from ..config import DATA_DIR
            tasks_file = DATA_DIR / "tasks.json"
            
            # Eğer userdata dizininde yoksa proje içinden al
            if not tasks_file.exists():
                from ..config import IDE_DIR
                fallback_file = IDE_DIR / "data" / "tasks.json"
                if fallback_file.exists():
                    shutil.copy(fallback_file, tasks_file)
                else:
                    tasks_file = fallback_file
            
            if tasks_file.exists():
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
            else:
                self.master.master.master.terminal.write_text(f">>> [Uyarı] GYM Görevleri bulunamadı: {tasks_file}\n")
                self.tasks = []
        except Exception as e:
            try:
                self.master.master.master.terminal.write_text(f">>> [Hata] GYM Yükleme hatası: {e}\n")
            except:
                print("GYM Yükleme hatası:", e)
            self.tasks = []
        
    def _load_tasks_ui(self):
        theme = self.config.THEMES[self.config.theme]
        
        title = ctk.CTkLabel(self.scroll, text="🏋️ GÜMÜŞ GYM", font=("Segoe UI", 14, "bold"), text_color=theme['accent'])
        title.pack(pady=(10, 20))
        
        for task in self.tasks:
            card = ctk.CTkFrame(self.scroll, fg_color=theme['sidebar_bg'], corner_radius=10, border_width=1, border_color=theme['border'])
            card.pack(fill="x", pady=5, padx=5)
            
            # Başlık
            ctk.CTkLabel(card, text=task['title'], font=("Segoe UI", 12, "bold"), text_color=theme['fg']).pack(anchor="w", padx=10, pady=(10, 0))
            
            # Açıklama
            desc = ctk.CTkLabel(card, text=task['desc'], font=("Segoe UI", 10), text_color=theme['comment'], wraplength=200, justify="left")
            desc.pack(anchor="w", padx=10, pady=(2, 10))
            
            # Başla Butonu
            btn = ctk.CTkButton(card, text="Başla", height=24, width=60, fg_color=theme['accent'], hover_color=theme['select_bg'],
                              command=lambda t=task: self.start_task(t))
            btn.pack(anchor="e", padx=10, pady=(0, 10))
            
    def start_task(self, task):
        # Kullanıcının editörüne kodu yükle
        self.on_load_task(task['code'])
        # Yönlendirme mesajı (Opsiyonel)
        print(f"Görev Başladı: {task['title']}")
