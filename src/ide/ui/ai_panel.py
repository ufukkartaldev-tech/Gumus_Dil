# -*- coding: utf-8 -*-
import threading
import customtkinter as ctk
import random
import re
import json
import os
from datetime import datetime

from ..core.ai_engine import GumusIntelligenceEngine
from ..core.summarizer import GumusSummarizer
from .ai_logic import AIAssistantLogic

class AIPanel(ctk.CTkFrame):
    def __init__(self, parent, config, on_apply_code=None, on_get_code=None):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_apply_code = on_apply_code
        self.on_get_code = on_get_code
        self.knowledge_base = self._load_kb()
        
        self.is_processing = False
        self._setup_ui()
        self.ai_engine = GumusIntelligenceEngine(use_local_model=True)
        self.add_message("Merhaba aslanım! Gümüş Zeka emrine amade. Kodun dumanı mı tütüyor yoksa yeni bir mühür mü basacağız?", is_user=False)

    def _load_kb(self):
        try:
            kb_path = os.path.join(os.getcwd(), "src", "ide", "data", "gumus_bilgi.json")
            if os.path.exists(kb_path):
                with open(kb_path, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
        return []

    def _setup_ui(self):
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(self.title_frame, text="✨ GÜMÜŞ ZEKA", font=("Segoe UI", 12, "bold")).pack(side="left")
        
        self.chat_history = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.chat_history.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.input_wrapper = ctk.CTkFrame(self, fg_color=("gray90", "#1e1e1e"), corner_radius=20)
        self.input_wrapper.pack(fill="x", padx=10, pady=10)
        self.input_entry = ctk.CTkEntry(self.input_wrapper, placeholder_text="Daktiloya fısılda...", height=40, border_width=0, fg_color="transparent")
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(15, 5))
        self.input_entry.bind("<Return>", self.send_message)
        ctk.CTkButton(self.input_wrapper, text="🚀", width=36, height=36, corner_radius=18, command=self.send_message).pack(side="right", padx=2)

    def add_message(self, text, is_user=False, is_error=False, is_system=False):
        theme = self.config.THEMES[self.config.theme]
        if is_system:
            bg = "#2c3e50"
        else:
            bg = theme['accent'] if is_user else (theme['editor_bg'] if not is_error else "#441111")
        align = "right" if is_user else "left"
        
        container = ctk.CTkFrame(self.chat_history, fg_color="transparent")
        container.pack(fill="x", pady=4, padx=5)
        bubble = ctk.CTkFrame(container, fg_color=bg, corner_radius=15, border_width=1, border_color=theme['border'])
        bubble.pack(side=align, padx=5)
        
        # Split text and code
        parts = re.split(r'(```[\s\S]*?```)', text)
        for part in parts:
            if not part: continue
            if part.startswith("```"):
                code = part.strip("`").strip()
                lines = code.split('\n')
                if len(lines) > 0 and len(lines[0].split()) == 1 and not lines[0].strip().startswith(('yazdır', 'eğer')):
                     code = '\n'.join(lines[1:])
                box = ctk.CTkTextbox(bubble, height=min(200, 20 + len(code.split('\n')) * 18), font=("Consolas", 11), fg_color="#121212")
                box.insert("1.0", code); box.configure(state="disabled"); box.pack(padx=10, pady=5, fill="x")
            else:
                ctk.CTkLabel(bubble, text=part.strip(), font=("Segoe UI", 11), wraplength=220, justify="left").pack(padx=12, pady=5)
        
        self.chat_history._parent_canvas.update_idletasks()
        self.chat_history._parent_canvas.yview_moveto(1.0)

    def send_message(self, event=None):
        if self.is_processing:
            return # Zaten işlem yapılıyor
            
        msg = self.input_entry.get().strip()
        if msg:
            self.add_message(msg, is_user=True)
            self.input_entry.delete(0, "end")
            
            # Start worker thread
            self.is_processing = True
            current_code = self.on_get_code() if self.on_get_code else ""
            threading.Thread(target=self._ai_worker, args=(msg, current_code), daemon=True).start()

    def _ai_worker(self, query, code_context):
        """Bu fonksiyon arka planda (Worker Thread) çalışır, UI'ı dondurmaz."""
        self.after(0, lambda: self.add_message("Gümüş Zeka düşünüyor... 🧠", is_system=True))
        
        try:
            # 1. AI Engine
            local_resp = self.ai_engine.generate_response(query, code_context)
            if local_resp:
                self.after(0, lambda: self.add_message(local_resp))
                return

            # 2. Summarizer
            if any(w in query.lower() for w in ["özetle", "ne yapıyor"]):
                summary = GumusSummarizer.summarize(code_context)
                self.after(0, lambda: self.add_message(summary))
                return

            # 3. Fuzzy Logic
            fuzzy = AIAssistantLogic.get_fuzzy_response(query)
            if fuzzy:
                resp = AIAssistantLogic.apply_mood(fuzzy)
                self.after(0, lambda: self.add_message(resp))
                return

            # 4. Code Gen
            if any(w in query.lower() for w in ["kod", "yaz", "oluştur"]):
                code, analysis = AIAssistantLogic.generate_code_snippet(query)
                self.after(0, lambda: (
                    self.add_message(f"{analysis}\n\n```gümüşdil\n{code}\n```"),
                    self._show_fix_option(code)
                ))
                return

            self.after(0, lambda: self.add_message("Bunu henüz mühürlemedim yeğenim, ama üzerinde çalışıyorum! 🌱"))
            
        except Exception as e:
            self.after(0, lambda: self.add_message(f"Hata oluştu: {str(e)}", is_error=True))
        finally:
            self.is_processing = False

    def _show_fix_option(self, code):
        container = ctk.CTkFrame(self.chat_history, fg_color="transparent")
        container.pack(fill="x", pady=5, padx=15)
        ctk.CTkButton(container, text="✓ Uygula", fg_color="#4caf50", command=lambda: self.on_apply_code(code)).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(container, text="✗ Reddet", fg_color="#f44336", command=lambda: container.destroy()).pack(side="right", padx=5, expand=True, fill="x")

    def receive_external_query(self, query):
        if self.is_processing:
            return
            
        self.add_message(query, is_user=True)
        self.is_processing = True
        current_code = self.on_get_code() if self.on_get_code else ""
        threading.Thread(target=self._ai_worker, args=(query, current_code), daemon=True).start()
