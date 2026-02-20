
import customtkinter as ctk
import tkinter as tk

class CanvasPanel(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        
        # Üst Bar
        self.top_bar = ctk.CTkFrame(self, height=30, fg_color="transparent")
        self.top_bar.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(self.top_bar, text="🎨 TUVAL", font=("Segoe UI", 12, "bold")).pack(side="left")
        
        self.clear_btn = ctk.CTkButton(self.top_bar, text="🧹", width=30, height=24, command=self.clear)
        self.clear_btn.pack(side="right")
        
        # Çizim Alanı
        theme = self.config.THEMES[self.config.theme]
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Komut Kuyruğu (External thread safe)
        self.command_queue = []
        
    def clear(self):
        self.canvas.delete("all")
        
    def process_command(self, cmd_str):
        """Basit çizim komutlarını işle (Örn: 'daire 50 #ff0000 100 100')"""
        try:
            parts = cmd_str.split()
            cmd = parts[0]
            
            if cmd == "daire":
                # daire r renk x y
                r = int(parts[1])
                color = parts[2]
                x = int(parts[3])
                y = int(parts[4])
                self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="")
                
            elif cmd == "dikdortgen":
                # dikdortgen w h renk x y
                w = int(parts[1])
                h = int(parts[2])
                color = parts[3]
                x = int(parts[4])
                y = int(parts[5])
                self.canvas.create_rectangle(x, y, x+w, y+h, fill=color, outline="")
                
            elif cmd == "cizgi":
                # cizgi x1 y1 x2 y2 renk kalinlik
                x1, y1, x2, y2 = map(int, parts[1:5])
                color = parts[5]
                width = int(parts[6])
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)
                
            elif cmd == "temizle":
                self.clear()
                
        except Exception as e:
            print(f"Canvas Hata: {e}")

    def apply_theme(self):
        # Canvas rengini temaya göre değil, hep beyaz/açık gri tutuyoruz ki çizim belli olsun
        # Ama çerçeve rengi güncellenebilir.
        pass

