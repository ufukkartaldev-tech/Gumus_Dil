# -*- coding: utf-8 -*-
import customtkinter as ctk

class GPIOPanel(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.pins = {} # {pin_number: (label, status_indicator)}
        
        theme = self.config.THEMES[self.config.theme]
        
        # Başlık
        ctk.CTkLabel(self, text="🔌 Sanal GPIO Çıkışları", font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        # Pin Grid
        self.grid_frame = ctk.CTkFrame(self, fg_color=theme['sidebar_bg'], corner_radius=10)
        self.grid_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 4x5 Grid (20 Pin)
        for i in range(20):
            row = i // 4
            col = i % 4
            
            pin_frame = ctk.CTkFrame(self.grid_frame, fg_color="transparent", width=60, height=80)
            pin_frame.grid(row=row, column=col, padx=5, pady=5)
            pin_frame.grid_propagate(False)
            
            # Pin No
            ctk.CTkLabel(pin_frame, text=f"P{i}", font=("Segoe UI", 10)).pack()
            
            # Status Indicator (Led)
            led = ctk.CTkFrame(pin_frame, width=20, height=20, corner_radius=10, fg_color="#333333")
            led.pack(pady=5)
            
            self.pins[i] = led

    def set_pin(self, pin, status):
        """Pin durumunu güncelle: 'HIGH', 'LOW'"""
        try:
            pin = int(pin)
            if pin in self.pins:
                color = "#00ff00" if status == "HIGH" else "#333333"
                self.pins[pin].configure(fg_color=color)
        except:
            pass

    def reset_all(self):
        for led in self.pins.values():
            led.configure(fg_color="#333333")

