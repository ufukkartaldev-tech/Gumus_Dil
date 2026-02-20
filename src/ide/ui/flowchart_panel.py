# -*- coding: utf-8 -*-
import customtkinter as ctk
import tkinter as tk
from ..core.flowchart_generator import FlowchartGenerator
from ..core.tokenizer import GumusTokenizer
from ..core.parser import GumusParser

class FlowchartPanel(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.theme = config.THEMES[config.theme]
        
        self.generator = FlowchartGenerator()
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Üst Araç Çubuğu
        self.toolbar = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.toolbar.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(self.toolbar, text="🌿 Gümüş Akış", font=("Segoe UI", 14, "bold"), text_color=self.theme['accent']).pack(side="left")
        
        self.refresh_btn = ctk.CTkButton(
            self.toolbar, 
            text="Yenile", 
            width=60, 
            height=28,
            fg_color=self.theme['accent'],
            command=self.update_flowchart
        )
        self.refresh_btn.pack(side="right")

        # Çizim Alanı
        self.container = ctk.CTkFrame(self, fg_color=self.theme['bg'], corner_radius=12, border_width=1, border_color=self.theme['border'])
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(
            self.container, 
            bg=self.theme['bg'], 
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)
        
    def update_flowchart(self, code=None):
        if not code:
            # Editördeki kodu almayı denemek lazım ama şu an için boşsa işlem yapma
            return

        try:
            # Parse code
            tokenizer = GumusTokenizer(code)
            tokens = tokenizer.tokenize()
            parser = GumusParser(tokens)
            ast = parser.parse()
            
            # Generate flow
            nodes = self.generator.generate(ast)
            
            # Draw
            self._draw_nodes(nodes)
            
        except Exception as e:
            self.canvas.delete("all")
            self.canvas.create_text(100, 50, text=f"Hata: {str(e)}", fill="red", anchor="nw")

    def _draw_nodes(self, nodes):
        self.canvas.delete("all")
        
        y_offset = 40
        x_center = self.canvas.winfo_width() / 2
        if x_center < 100: x_center = 150 # Default if not rendered yet
        
        node_positions = {}
        
        for i, node in enumerate(nodes):
            x = x_center
            y = y_offset + (i * 80)
            node_positions[node.id] = (x, y)
            
            color = self.theme['accent']
            if node.type == 'start' or node.type == 'end':
                # Oval
                self.canvas.create_oval(x-50, y-20, x+50, y+20, fill=self.theme['sidebar_bg'], outline=color, width=2)
            elif node.type == 'decision':
                # Diamond
                points = [x, y-25, x+60, y, x, y+25, x-60, y]
                self.canvas.create_polygon(points, fill=self.theme['sidebar_bg'], outline=color, width=2)
            elif node.type == 'loop':
                # Hexagon-ish
                self.canvas.create_rectangle(x-55, y-20, x+55, y+20, fill=self.theme['sidebar_bg'], outline="#FFCC00", width=2)
            else:
                # Rectangle
                self.canvas.create_rectangle(x-50, y-20, x+50, y+20, fill=self.theme['sidebar_bg'], outline=color, width=2)
                
            self.canvas.create_text(x, y, text=node.label, fill=self.theme['fg'], font=("Segoe UI", 9))
            
        # Draw Arrows
        for node in nodes:
            if node.id in node_positions:
                start_pos = node_positions[node.id]
                for next_id in node.next:
                    if next_id in node_positions:
                        end_pos = node_positions[next_id]
                        self.canvas.create_line(
                            start_pos[0], start_pos[1]+20, 
                            end_pos[0], end_pos[1]-20, 
                            arrow=tk.LAST, 
                            fill=self.theme['comment'],
                            width=1.5
                        )
