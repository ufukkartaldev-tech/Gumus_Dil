# -*- coding: utf-8 -*-
import customtkinter as ctk

class OutlinePanel(ctk.CTkFrame):
    def __init__(self, parent, config, on_jump):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_jump = on_jump
        self.tree_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.tree_frame.pack(fill="both", expand=True)

    def update_outline(self, symbols):
        for widget in self.tree_frame.winfo_children(): widget.destroy()
        theme = self.config.THEMES[self.config.theme]
        for s in symbols:
            color = theme.get(s['type'], theme.get('fg', 'white'))
            btn = ctk.CTkButton(self.tree_frame, text=f"{s['icon']} {s['name']}", anchor="w",
                               fg_color="transparent", hover_color=theme['hover'], text_color=color,
                               height=28, font=("Segoe UI", 11), command=lambda line=s['line']: self.on_jump(line))
            btn.pack(fill="x", padx=5, pady=1)
