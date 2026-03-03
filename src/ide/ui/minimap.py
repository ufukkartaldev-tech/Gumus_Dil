import tkinter as tk

class Minimap(tk.Canvas):
    def __init__(self, parent, text_widget, config, **kwargs):
        super().__init__(parent, **kwargs)
        self.text_widget = text_widget
        self.config = config
        self.configure(width=100, highlightthickness=0, relief='flat')
        self.apply_theme()
        
        # İnteraktif Minimap
        self.bind("<Button-1>", self.jump_to_click)
        self.bind("<B1-Motion>", self.jump_to_click)
        self.line_height = 3 # Varsayılan
        
    def apply_theme(self):
        theme = self.config.THEMES[self.config.theme]
        self.configure(bg=theme['sidebar_bg'])
        
    def redraw(self, *args):
        self.delete("all")
        content = self.text_widget.get("1.0", "end-1c")
        lines = content.split("\n")
        
        # Orijinal metin satır sayısı
        total_lines = len(lines)
        if total_lines == 0: return

        # Her satır 3 piksel temsil edilsin (daha net görünüm)
        line_height = 3
        
        theme = self.config.THEMES[self.config.theme]
        # Renk tonunu çeşitlendir (yorumlar silik, kodlar parlak)
        base_color = theme.get('comment', '#555')
        accent_color = theme.get('function', '#888')
        
        for i, line in enumerate(lines):
             if not line.strip(): continue
             
             # Satırın başındaki boşluğu al (girinti)
             indent = len(line) - len(line.lstrip())
             y = i * line_height + 5
             
             # Satır uzunluğu
             line_len = min(len(line.strip()), 50) 
             
             # Basit renk mantığı: eğer 'def' veya 'class' ise parlak yap
             is_def = line.strip().startswith(('fonksiyon', 'sınıf', 'temel'))
             color = accent_color if is_def else base_color
             
             self.create_line(
                 5 + (indent * 2), y, 
                 5 + (indent * 2) + (line_len * 2), y, 
                 fill=color, 
                 width=2 # Daha kalın
             )
             
        # Viewport göstergesi (kullanıcının şu an gördüğü alan)
        try:
             first_visible = self.text_widget.index("@0,0")
             last_visible = self.text_widget.index(f"@0,{self.text_widget.winfo_height()}")
             
             start_line = int(first_visible.split('.')[0])
             end_line = int(last_visible.split('.')[0])
             
             viewport_y1 = (start_line - 1) * line_height + 5
             viewport_y2 = (end_line - 1) * line_height + 5
             
             # Yarı saydam bir efekt verilemez (Canvas sınırlı), ama outline çizilebilir
             self.create_rectangle(
                 2, viewport_y1, 
                 98, viewport_y2, 
                 outline=theme['accent'],
                 width=1.5,
                 tags="viewport"
             )
             
        except:
             pass

    def jump_to_click(self, event):
        """Minimap'e tıklandığında oraya git"""
        y = event.y
        # Satır numarasını tahmin et
        target_line = int((y - 5) / self.line_height) + 1
        if target_line < 1: target_line = 1
        
        # Oraya kaydır
        try:
             self.text_widget.see(f"{target_line}.0")
             self.text_widget.mark_set("insert", f"{target_line}.0")
        except:
             pass
